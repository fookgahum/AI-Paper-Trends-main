"""Build evidence-backed frontier direction briefs from the web paper snapshot."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterable, List

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_DIR = PROJECT_ROOT / "data" / "web" / "ccfa_2026"
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "frontier" / "directions.yaml"
CONFERENCES = ("ICLR", "ICML", "ACL")
EVALUATION_PATTERN = re.compile(
    r"\b(benchmark|benchmarking|evaluation|evaluate|evaluating|dataset|"
    r"diagnostic|analysis|taxonomy|empirical study|systematic study)\b",
    re.IGNORECASE,
)
def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
        file.write("\n")


def _normalise_text(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def _signal_rate(papers: Iterable[Dict[str, Any]], pattern: re.Pattern[str]) -> int:
    rows = list(papers)
    if not rows:
        return 0
    matches = sum(
        bool(pattern.search(f"{paper['title']} {paper['abstract']}"))
        for paper in rows
    )
    return round(matches / len(rows) * 100)


def _breadth_score(conference_counts: Counter[str]) -> int:
    total = sum(conference_counts.values())
    if not total:
        return 0
    entropy = -sum(
        (count / total) * math.log(count / total)
        for count in conference_counts.values()
        if count
    )
    return round(entropy / math.log(len(CONFERENCES)) * 100)


def _competition_pressure(paper_count: int) -> str:
    if paper_count >= 65:
        return "high"
    if paper_count >= 45:
        return "medium_high"
    if paper_count >= 30:
        return "medium"
    return "lower"


def _profile_score(
    barriers: Dict[str, int],
    capabilities: Dict[str, int],
    *,
    paper_count: int,
    breadth: int,
    evaluation_rate: int,
) -> Dict[str, int]:
    dimensions = ("compute", "data", "engineering", "theory")
    deficit = sum(
        max(0, int(barriers[name]) - int(capabilities[name]))
        for name in dimensions
    )
    worst_deficit = max(
        max(0, int(barriers[name]) - int(capabilities[name]))
        for name in dimensions
    )
    average_fit = max(0, 100 - deficit / 16 * 100)
    bottleneck_fit = max(0, 100 - worst_deficit / 4 * 100)
    capability_fit = round(average_fit * 0.5 + bottleneck_fit * 0.5)
    evidence_strength = round(min(100, paper_count / 50 * 100))
    competition_headroom = round(
        max(0, min(100, 100 - (paper_count - 20) / 60 * 100))
    )
    score = round(
        capability_fit * 0.55
        + breadth * 0.15
        + evaluation_rate * 0.12
        + evidence_strength * 0.10
        + competition_headroom * 0.08
    )
    return {
        "score": score,
        "capability_fit": capability_fit,
        "evidence_strength": evidence_strength,
        "breadth": breadth,
        "evaluation_access": evaluation_rate,
        "competition_headroom": competition_headroom,
    }


def _representative_papers(
    papers: List[Dict[str, Any]], queries: List[str]
) -> List[Dict[str, str]]:
    representatives: List[Dict[str, str]] = []
    used_ids = set()
    for query in queries:
        needle = _normalise_text(query)
        match = next(
            (
                paper
                for paper in papers
                if paper["id"] not in used_ids
                and needle in _normalise_text(paper["title"])
            ),
            None,
        )
        if match is None:
            raise ValueError(f"Representative paper not found for query: {query}")
        used_ids.add(match["id"])
        representatives.append(
            {
                "id": match["id"],
                "title": match["title"],
                "conference": match["conference"],
                "source_url": match["source_url"],
            }
        )
    return representatives


def build_opportunity_payload(
    papers: List[Dict[str, Any]], config: Dict[str, Any]
) -> Dict[str, Any]:
    """Validate the curated taxonomy and compute its evidence metrics."""
    directions = config.get("directions", [])
    profiles = config.get("profiles", [])
    if not directions or not profiles:
        raise ValueError("Frontier config must define directions and profiles.")

    profile_ids = [profile.get("id") for profile in profiles]
    if any(not profile_id for profile_id in profile_ids) or len(
        set(profile_ids)
    ) != len(profile_ids):
        raise ValueError("Frontier profiles must have unique non-empty ids.")
    dimensions = {"compute", "data", "engineering", "theory"}
    for profile in profiles:
        capabilities = profile.get("capabilities", {})
        if set(capabilities) != dimensions or any(
            not 1 <= int(value) <= 5 for value in capabilities.values()
        ):
            raise ValueError(f"Invalid profile capabilities: {profile.get('id')}")

    paper_topics = {int(paper["topic_id"]) for paper in papers}
    configured_topics: List[int] = []
    for direction in directions:
        direction_id = direction.get("id")
        for field in ("title", "summary", "why_now", "best_for", "avoid"):
            bilingual = direction.get(field)
            if not isinstance(bilingual, dict) or any(
                not isinstance(bilingual.get(language), str)
                or not bilingual[language].strip()
                for language in ("zh-CN", "en-US")
            ):
                raise ValueError(
                    f"Direction {direction_id} has invalid bilingual {field}."
                )
        for field in ("entry_points", "paper_shapes"):
            bilingual = direction.get(field)
            if not isinstance(bilingual, dict) or any(
                not isinstance(bilingual.get(language), list)
                or not bilingual[language]
                or any(not isinstance(item, str) for item in bilingual[language])
                for language in ("zh-CN", "en-US")
            ):
                raise ValueError(
                    f"Direction {direction_id} has invalid bilingual {field}."
                )
        if any(
            len(direction["entry_points"][language]) != 3
            for language in ("zh-CN", "en-US")
        ):
            raise ValueError(
                f"Direction {direction_id} must define exactly three entry points per language."
            )
        barriers = direction.get("barriers", {})
        if set(barriers) != dimensions or any(
            not 1 <= int(value) <= 5 for value in barriers.values()
        ):
            raise ValueError(f"Invalid direction barriers: {direction_id}")
        if len(direction.get("representative_queries", [])) != 3:
            raise ValueError(
                f"Direction {direction_id} must define three representative papers."
            )
        configured_topics.extend(int(topic) for topic in direction["topic_ids"])
    duplicates = [
        topic for topic, count in Counter(configured_topics).items() if count > 1
    ]
    if duplicates:
        raise ValueError(f"Topic ids assigned to multiple directions: {duplicates}")
    if set(configured_topics) != paper_topics:
        raise ValueError(
            "Direction taxonomy must cover every modeled topic exactly once: "
            f"configured={sorted(set(configured_topics))}, papers={sorted(paper_topics)}"
        )

    built_directions = []
    direction_by_topic: Dict[int, Dict[str, Any]] = {}
    for source in directions:
        direction = deepcopy(source)
        topic_ids = {int(topic) for topic in direction.pop("topic_ids")}
        direction_papers = [
            paper for paper in papers if int(paper["topic_id"]) in topic_ids
        ]
        conference_counts = Counter(
            paper["conference"] for paper in direction_papers
        )
        breadth = _breadth_score(conference_counts)
        evaluation_rate = _signal_rate(direction_papers, EVALUATION_PATTERN)
        barriers = {
            name: int(value) for name, value in direction["barriers"].items()
        }
        scores = {
            profile["id"]: _profile_score(
                barriers,
                profile["capabilities"],
                paper_count=len(direction_papers),
                breadth=breadth,
                evaluation_rate=evaluation_rate,
            )
            for profile in profiles
        }
        direction["topic_ids"] = sorted(topic_ids)
        direction["paper_count"] = len(direction_papers)
        direction["conference_counts"] = {
            conference: conference_counts.get(conference, 0)
            for conference in CONFERENCES
        }
        direction["breadth_score"] = breadth
        direction["evaluation_signal_rate"] = evaluation_rate
        direction["competition_pressure"] = _competition_pressure(
            len(direction_papers)
        )
        direction["evidence_confidence"] = (
            "high" if len(direction_papers) >= 35 and breadth >= 75 else "medium"
        )
        direction["scores"] = scores
        direction["representative_papers"] = _representative_papers(
            direction_papers, direction.pop("representative_queries")
        )
        built_directions.append(direction)
        for topic_id in topic_ids:
            direction_by_topic[topic_id] = direction

    for paper in papers:
        direction = direction_by_topic[int(paper["topic_id"])]
        paper["direction_id"] = direction["id"]
        paper["direction_title"] = direction["title"]

    return {
        "schema_version": 1,
        "analysis_scope": {
            "paper_count": len(papers),
            "year": 2026,
            "conferences": list(CONFERENCES),
            "population": "fixed accepted/published paper sample",
        },
        "decision_question": {
            "zh-CN": "在不同研究资源条件下，哪些 2026 前沿方向更适合作为论文切入点？",
            "en-US": "Which 2026 frontier directions are more practical paper entry points under different research-resource profiles?",
        },
        "methodology": {
            "zh-CN": (
                "切入友好度是启发式决策指标，不是录用概率。它综合资源匹配 55%、"
                "跨会议覆盖 15%、评测型切入信号 12%、样本证据量 10% 和竞争余量 8%。"
                "资源匹配同时考虑平均差距和单项短板。方向总结由 600 篇摘要与代表论文归纳，"
                "资源门槛为 1（低）到 5（高）的人工审阅标注；竞争余量仅由本样本中的"
                "相对论文密度近似。"
            ),
            "en-US": (
                "Entry friendliness is a decision heuristic, not an acceptance probability. "
                "It combines resource fit (55%), cross-venue breadth (15%), evaluation-oriented "
                "entry signals (12%), evidence volume (10%), and competition headroom (8%). "
                "Resource fit penalizes both average gaps and a single bottleneck. Summaries are "
                "synthesized from 600 abstracts and representative papers; resource barriers are "
                "reviewed labels from 1 (low) to 5 (high), while competition headroom is only "
                "approximated from relative paper density in this sample."
            ),
        },
        "limitations": {
            "zh-CN": [
                "样本只包含 2026 年已录用或已发表论文，不能推断真实录用概率。",
                "没有投稿总量和拒稿数据，因此“样本拥挤度”不等于真实竞争强度。",
                "没有跨年序列，因此不能判断一个方向正在增长还是降温。",
                "方向总结和资源门槛经过人工归纳，适合筛选候选题，不替代具体文献综述。",
            ],
            "en-US": [
                "The sample contains only accepted or published 2026 papers, so it cannot estimate acceptance probability.",
                "Submission totals and rejected work are unavailable; sample density is not real competitive intensity.",
                "There is no multi-year series, so the analysis cannot establish growth or cooling momentum.",
                "Direction synthesis and resource barriers are reviewed judgments for screening candidates, not a substitute for a focused literature review.",
            ],
        },
        "score_formula": {
            "resource_fit": 0.55,
            "cross_venue_breadth": 0.15,
            "evaluation_signal": 0.12,
            "evidence_strength": 0.10,
            "competition_headroom": 0.08,
        },
        "profiles": profiles,
        "directions": built_directions,
    }


def build_opportunity_snapshot(run_dir: Path, config_path: Path) -> Path:
    papers_path = run_dir / "papers.json"
    manifest_path = run_dir / "manifest.json"
    papers = _load_json(papers_path)
    manifest = _load_json(manifest_path)
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    payload = build_opportunity_payload(papers, config)
    output_path = run_dir / "opportunities.json"
    manifest["frontier_analysis"] = {
        "file": output_path.name,
        "direction_count": len(payload["directions"]),
        "default_profile": "individual",
        "score_is_acceptance_probability": False,
        "method": "curated direction synthesis with reproducible evidence metrics",
    }
    _write_json(papers_path, papers)
    _write_json(manifest_path, manifest)
    _write_json(output_path, payload)
    print(
        f"[frontier-analysis] Saved {len(payload['directions'])} directions to "
        f"{output_path}",
        flush=True,
    )
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build frontier opportunity briefs from an exported web run."
    )
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    build_opportunity_snapshot(args.run_dir, args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
