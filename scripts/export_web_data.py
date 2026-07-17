"""Export topic-model CSV output as a validated web dashboard snapshot."""

from __future__ import annotations

import argparse
import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_METADATA = {
    "ICLR": {
        "label": "ICLR 2026 official virtual program",
        "url": "https://iclr.cc/virtual/2026/papers.html",
        "scope": "Accepted program papers · fixed random sample",
    },
    "ICML": {
        "label": "ICML 2026 official virtual program",
        "url": "https://icml.cc/virtual/2026/papers.html",
        "scope": "Accepted program papers · fixed random sample",
    },
    "ACL": {
        "label": "ACL 2026 official ACL Anthology proceedings",
        "url": "https://aclanthology.org/events/acl-2026/",
        "scope": "Published long papers · fixed random sample",
    },
}


def _parse_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        try:
            parsed = ast.literal_eval(stripped)
        except (ValueError, SyntaxError):
            return [stripped]
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    return []


def _nullable_float(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def load_topic_labels(path: Path) -> Dict[int, str]:
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    return {int(topic_id): str(label) for topic_id, label in raw.items()}


def build_papers(dataframe: pd.DataFrame, labels: Dict[int, str]) -> List[Dict[str, Any]]:
    required = {
        "id",
        "conference",
        "year",
        "title",
        "abstract",
        "authors",
        "decision",
        "source_url",
        "Topic",
    }
    missing = required - set(dataframe.columns)
    if missing:
        raise ValueError(f"Processed CSV is missing columns: {sorted(missing)}")

    papers: List[Dict[str, Any]] = []
    for row in dataframe.to_dict(orient="records"):
        topic_id = int(row["Topic"])
        topic_name = labels.get(topic_id, "Other / Outlier")
        papers.append(
            {
                "id": str(row["id"]),
                "conference": str(row["conference"]),
                "year": int(row["year"]),
                "title": str(row["title"]),
                "abstract": str(row["abstract"]),
                "authors": _parse_list(row["authors"]),
                "keywords": _parse_list(row.get("keywords")),
                "decision": str(row.get("decision") or "Published"),
                "avg_rating": _nullable_float(row.get("avg_rating")),
                "topic_id": topic_id,
                "topic_name": topic_name,
                "source_topic": str(row.get("source_topic") or ""),
                "source_url": str(row["source_url"]),
                "source_name": str(row.get("source_name") or "Official source"),
            }
        )
    return sorted(papers, key=lambda paper: (paper["conference"], paper["title"]))


def build_manifest(
    papers: List[Dict[str, Any]],
    run_id: str,
    seed: int,
    sample_size: int,
    topic_model: str = "BERTopic with a locally cached sentence-transformer",
) -> Dict[str, Any]:
    sources = []
    for conference in ("ICLR", "ICML", "ACL"):
        metadata = SOURCE_METADATA[conference]
        sources.append(
            {
                "conference": conference,
                **metadata,
                "paper_count": sum(
                    paper["conference"] == conference for paper in papers
                ),
            }
        )
    return {
        "run_id": run_id,
        "title": "CCF-A 2026 · 600-paper frontier sample",
        "year": 2026,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_seed": seed,
        "sample_size_per_conference": sample_size,
        "sample_scope": "accepted_or_published",
        "scope_note": {
            "zh-CN": (
                "截至 2026-07-17，NeurIPS 2026 官方投稿页尚无公开论文，因此第三个真实来源采用 "
                "ACL 2026。ICLR、ICML、ACL 各从官方已录用/已发表论文中固定随机抽取 200 篇，"
                "共 600 篇；它不是全部投稿样本，不能用于计算真实录用率。"
            ),
            "en-US": (
                "As of 2026-07-17, the official NeurIPS 2026 submission page exposes no "
                "papers, so ACL 2026 is the third real source. This fixed sample contains "
                "200 accepted or published papers from each official ICLR, ICML, and ACL "
                "source (600 total); it cannot support a true acceptance-rate estimate."
            ),
        },
        "source_checked_at": "2026-07-17",
        "metrics_availability": {
            "public_review_rating": False,
            "acceptance_rate": False,
        },
        "topic_model": topic_model,
        "paper_count": len(papers),
        "sources": sources,
    }


def export_snapshot(
    input_path: Path,
    labels_path: Path,
    output_dir: Path,
    run_id: str,
    seed: int,
    sample_size: int,
    topic_model: str = "BERTopic with a locally cached sentence-transformer",
) -> None:
    dataframe = pd.read_csv(input_path, encoding="utf-8-sig")
    papers = build_papers(dataframe, load_topic_labels(labels_path))
    expected_total = sample_size * len(SOURCE_METADATA)
    if len(papers) != expected_total:
        raise ValueError(f"Expected {expected_total} papers, found {len(papers)}")
    manifest = build_manifest(papers, run_id, seed, sample_size, topic_model)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in (("manifest.json", manifest), ("papers.json", papers)):
        with (output_dir / name).open("w", encoding="utf-8", newline="\n") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
            file.write("\n")
    print(f"[web-export] Saved {len(papers)} papers to {output_dir}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export topic data for the web UI.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--labels", type=Path, required=True)
    parser.add_argument("--run-id", default="ccfa_2026")
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "web" / "ccfa_2026",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_snapshot(
        args.input,
        args.labels,
        args.output,
        args.run_id,
        args.seed,
        args.sample_size,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
