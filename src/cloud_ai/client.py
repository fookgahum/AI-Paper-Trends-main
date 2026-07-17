"""Single, replaceable boundary for paid cloud-model requests."""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Protocol, Tuple

import httpx
import yaml


@dataclass(frozen=True)
class CloudAIConfig:
    provider: str
    model: str
    base_url: str
    api_key_env: str
    timeout_seconds: float
    temperature: float
    prompt_version: str


class CloudAIClient(Protocol):
    provider: str
    model: str

    def generate_learning_plan(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]: ...

    def analyze_direction_updates(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]: ...


def load_cloud_config(path: Path) -> CloudAIConfig:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return CloudAIConfig(
        provider=str(payload.get("provider", "mock")),
        model=str(payload.get("model", "mock-frontier-tutor-v1")),
        base_url=str(payload.get("base_url", "https://api.openai.com/v1")).rstrip("/"),
        api_key_env=str(payload.get("api_key_env", "CLOUD_AI_API_KEY")),
        timeout_seconds=float(payload.get("timeout_seconds", 90)),
        temperature=float(payload.get("temperature", 0.2)),
        prompt_version=str(payload.get("prompt_version", "learning-plan-v1")),
    )


def create_cloud_client(config: CloudAIConfig) -> CloudAIClient:
    if config.provider == "mock":
        return MockCloudAIClient(config.model)
    if config.provider in {"openai_compatible", "openai"}:
        return OpenAICompatibleCloudAIClient(config)
    raise ValueError(f"Unsupported cloud AI provider: {config.provider}")


class OpenAICompatibleCloudAIClient:
    """Call an OpenAI-compatible Chat Completions endpoint for strict JSON."""

    provider = "openai_compatible"

    def __init__(self, config: CloudAIConfig) -> None:
        self.config = config
        self.model = config.model

    def generate_learning_plan(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        return self._request_json(
            context,
            "Create a grounded learning and reproduction plan. Every task needs a "
            "measurable deliverable and acceptance rule. Every anchor-paper id must "
            "come from the supplied evidence.",
        )

    def analyze_direction_updates(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        return self._request_json(
            context,
            "Map every supplied paper to an existing direction when evidence is strong. "
            "Otherwise set direction_id to null and create a grounded new-direction "
            "candidate. Do not invent paper or direction ids.",
        )

    def _request_json(
        self, context: Dict[str, Any], task_instruction: str
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        api_key = os.getenv(self.config.api_key_env)
        if not api_key:
            raise RuntimeError(
                f"Missing API key. Set environment variable {self.config.api_key_env}."
            )
        system_prompt = (
            "You are a senior computer-science research mentor. Return only one valid JSON "
            f"object matching the supplied schema. {task_instruction}"
        )
        user_prompt = json.dumps(context, ensure_ascii=False)
        with httpx.Client(timeout=self.config.timeout_seconds) as client:
            response = client.post(
                f"{self.config.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": self.model,
                    "temperature": self.config.temperature,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            response.raise_for_status()
        payload = response.json()
        content = payload["choices"][0]["message"]["content"]
        usage = payload.get("usage", {})
        return json.loads(content), {
            "input_tokens": int(usage.get("prompt_tokens", 0)),
            "output_tokens": int(usage.get("completion_tokens", 0)),
        }


class MockCloudAIClient:
    """Deterministic, free generator used by tests and first-run evaluation."""

    provider = "mock"

    def __init__(self, model: str = "mock-frontier-tutor-v1") -> None:
        self.model = model

    def generate_learning_plan(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        direction = context["direction"]
        language = context["request"]["language"]
        duration = int(context["request"]["duration_days"])
        title = _localized(direction["title"], language)
        summary = _localized(direction["summary"], language)
        entry_points = _localized(direction.get("entry_points", {}), language) or []
        representatives = direction["representative_papers"][:3]
        cut1 = max(1, round(duration * 0.2))
        cut2 = max(cut1 + 1, round(duration * 0.5))
        cut3 = max(cut2 + 1, round(duration * 0.8))
        cut3 = min(cut3, duration - 1) if duration > 3 else duration
        ranges = [(1, cut1), (cut1 + 1, cut2), (cut2 + 1, cut3)]
        if cut3 < duration:
            ranges.append((cut3 + 1, duration))
        ranges = [(start, end) for start, end in ranges if start <= end]
        stage_names = (
            ["建立地图", "读懂锚点论文", "完成复现", "形成可投稿假设"]
            if language == "zh-CN"
            else ["Map the field", "Read anchor papers", "Reproduce", "Form a publishable hypothesis"]
        )
        anchors = [
            {
                "paper_id": paper["id"],
                "title": paper["title"],
                "source_url": paper["source_url"],
                "reason": (
                    f"作为第 {index} 篇锚点，提取问题定义、关键假设、实验协议和失败边界。"
                    if language == "zh-CN"
                    else f"Anchor {index}: extract the problem, assumptions, protocol, and failure boundary."
                ),
                "reading_order": index,
                "reproduction_level": f"L{min(index, 3)}",
            }
            for index, paper in enumerate(representatives, 1)
        ]
        anchor_ids = [paper["paper_id"] for paper in anchors]
        stages = []
        for index, (start, end) in enumerate(ranges):
            name = stage_names[min(index, len(stage_names) - 1)]
            deliverable = (
                f"一份关于“{title}”的阶段产物：包含可运行材料、结果表和误差记录。"
                if language == "zh-CN"
                else f"A {title} stage artifact with runnable material, results, and an error log."
            )
            stages.append(
                {
                    "id": f"stage_{index + 1}",
                    "title": name,
                    "day_start": start,
                    "day_end": end,
                    "goal": deliverable,
                    "tasks": [
                        {
                            "id": f"task_{index + 1}",
                            "day_start": start,
                            "day_end": end,
                            "title": name,
                            "objectives": [
                                ("从论文证据建立能力，而不是只看二手总结。" if language == "zh-CN" else "Build capability from paper evidence, not summaries alone.")
                            ],
                            "actions": [
                                ("阅读指定锚点并填写问题—方法—实验—局限四格笔记。" if language == "zh-CN" else "Read anchors and complete problem-method-experiment-limit notes."),
                                ("运行一个最小实验并保存配置、日志和随机种子。" if language == "zh-CN" else "Run one minimum experiment and save config, logs, and seeds."),
                            ],
                            "deliverable": deliverable,
                            "acceptance": ("第三方按 README 能复现，且结果表包含至少一个失败样例。" if language == "zh-CN" else "A third party can reproduce from README and the results include one failure case."),
                            "anchor_paper_ids": anchor_ids[: min(index + 1, len(anchor_ids))],
                        }
                    ],
                }
            )
        focus = entry_points[0] if entry_points else title
        artifact = {
            "direction_id": direction["id"],
            "direction_title": title,
            "executive_summary": (
                f"目标不是泛读，而是在 {duration} 天内从“理解 {title}”走到“可复现并能提出最小研究假设”。{summary}"
                if language == "zh-CN"
                else f"In {duration} days, move from understanding {title} to reproducibility and a minimum research hypothesis. {summary}"
            ),
            "duration_days": duration,
            "knowledge_tree": _mock_knowledge_tree(title, language),
            "stages": stages,
            "anchor_papers": anchors,
            "reproduction_ladder": _mock_reproduction_ladder(language),
            "research_hypotheses": [
                {
                    "id": "hypothesis_1",
                    "question": (f"能否围绕“{focus}”用更低算力得到稳定、可解释的改进？" if language == "zh-CN" else f"Can '{focus}' yield a stable, interpretable gain at lower compute?"),
                    "novelty": ("把前沿问题缩成单变量、可证伪的最小贡献。" if language == "zh-CN" else "Reduce the frontier problem to one falsifiable variable."),
                    "minimum_experiment": ("复用一篇锚点的公开数据与评测，只替换一个变量，报告均值、方差和失败类型。" if language == "zh-CN" else "Reuse one anchor's data and evaluation, change one variable, and report mean, variance, and failure types."),
                    "risks": (["提升来自数据泄漏", "基线复现误差大于方法收益"] if language == "zh-CN" else ["Gain comes from leakage", "Baseline variance exceeds method gain"]),
                }
            ],
        }
        return artifact, {"input_tokens": 0, "output_tokens": 0}

    def analyze_direction_updates(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        language = context["request"]["language"]
        directions = context["directions"]
        assignments = []
        candidate_papers = []
        for paper in context["papers"]:
            paper_tokens = _word_tokens(f"{paper['title']} {paper['abstract']}")
            scored = []
            for direction in directions:
                direction_text = " ".join(
                    str(_localized(direction.get(field, ""), language))
                    for field in ("title", "summary")
                )
                overlap = len(paper_tokens & _word_tokens(direction_text))
                scored.append((overlap, direction["id"]))
            best_overlap, best_id = max(scored, default=(0, ""))
            matched = best_id if best_overlap >= 2 else None
            assignments.append(
                {
                    "paper_id": paper["id"],
                    "direction_id": matched,
                    "confidence": min(0.95, 0.5 + best_overlap * 0.1) if matched else 0.35,
                    "rationale": (
                        "标题和摘要与现有方向存在可核查的术语重合。"
                        if matched and language == "zh-CN"
                        else "The title and abstract have inspectable overlap with an existing direction."
                        if matched
                        else "与现有方向的证据重合不足，保留为候选而不强行归类。"
                        if language == "zh-CN"
                        else "Evidence overlap is too weak for a forced assignment; keep it as a candidate."
                    ),
                }
            )
            if not matched:
                candidate_papers.append(paper)
        candidates = []
        if candidate_papers:
            candidate_title = (
                "待核查的新兴方向候选" if language == "zh-CN" else "Emerging direction candidate for review"
            )
            candidates.append(
                {
                    "id": "candidate_" + hashlib.sha256(
                        "|".join(paper["id"] for paper in candidate_papers).encode("utf-8")
                    ).hexdigest()[:12],
                    "title": candidate_title,
                    "summary": (
                        "这些新论文暂时无法可靠映射到现有方向，需要结合更多论文和正文证据人工复核。"
                        if language == "zh-CN"
                        else "These papers cannot yet be reliably mapped and need more evidence plus human review."
                    ),
                    "evidence_paper_ids": [paper["id"] for paper in candidate_papers],
                    "difference_from_existing": (
                        "当前样本与 13 个正式方向的标题和摘要证据重合较弱。"
                        if language == "zh-CN"
                        else "The current sample has weak title/abstract evidence overlap with the 13 published directions."
                    ),
                    "recommended_action": (
                        "补充同类论文，阅读正文后再决定合并或建立新方向。"
                        if language == "zh-CN"
                        else "Add related papers and inspect full text before merging or publishing a new direction."
                    ),
                }
            )
        artifact = {
            "run_id": context["request"]["run_id"],
            "assignments": assignments,
            "candidates": candidates,
            "synthesis": (
                f"已检查 {len(assignments)} 篇未分析论文；正式方向未被自动修改。"
                if language == "zh-CN"
                else f"Reviewed {len(assignments)} unanalysed papers; published directions were not modified."
            ),
        }
        return artifact, {"input_tokens": 0, "output_tokens": 0}


def _localized(value: Any, language: str) -> Any:
    if isinstance(value, dict):
        return value.get(language) or value.get("en-US") or value.get("zh-CN")
    return value


def _word_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}|[\u4e00-\u9fff]{2,}", value.casefold())
        if token not in {"the", "and", "with", "from", "this", "that"}
    }


def _mock_knowledge_tree(title: str, language: str) -> list[dict[str, Any]]:
    if language == "zh-CN":
        values = [
            ("foundation", "问题与基础", "掌握任务定义、数据和核心指标。", [], "一页术语与指标表"),
            ("evidence", "论文证据链", "能拆解锚点论文的假设与证据。", ["foundation"], "三篇四格论文卡"),
            ("reproduction", "可复现实验", "把论文描述变成可运行且可追踪的实验。", ["evidence"], "带配置和日志的基线仓库"),
            ("research", "研究假设", f"围绕{title}形成可证伪贡献。", ["reproduction"], "一页实验提案"),
        ]
    else:
        values = [
            ("foundation", "Problem foundations", "Master task definitions, data, and metrics.", [], "One-page glossary and metric map"),
            ("evidence", "Paper evidence", "Decompose anchor assumptions and evidence.", ["foundation"], "Three structured paper cards"),
            ("reproduction", "Reproducible experiment", "Turn descriptions into traceable experiments.", ["evidence"], "Baseline repository with config and logs"),
            ("research", "Research hypothesis", f"Form a falsifiable {title} contribution.", ["reproduction"], "One-page experiment proposal"),
        ]
    return [
        {"id": node_id, "title": node_title, "reason": reason, "prerequisites": prereqs, "deliverable": deliverable, "estimated_hours": 4 + index * 2}
        for index, (node_id, node_title, reason, prereqs, deliverable) in enumerate(values)
    ]


def _mock_reproduction_ladder(language: str) -> list[dict[str, str]]:
    if language == "zh-CN":
        rows = [
            ("L0", "读懂", "能口述问题、方法和证据", "完成四格论文卡"),
            ("L1", "跑通", "运行作者或官方基线", "保存环境、配置与原始日志"),
            ("L2", "对齐", "复现主要指标", "误差在预先声明阈值内"),
            ("L3", "扩展", "完成一个受控变量实验", "含消融、方差和失败分析"),
            ("L4", "研究", "验证自己的可证伪假设", "形成可审稿的证据包"),
        ]
    else:
        rows = [
            ("L0", "Understand", "Explain the problem, method, and evidence", "Complete structured paper cards"),
            ("L1", "Run", "Run the author or official baseline", "Save environment, config, and raw logs"),
            ("L2", "Match", "Reproduce the primary metric", "Stay within a declared error tolerance"),
            ("L3", "Extend", "Run one controlled-variable experiment", "Include ablation, variance, and failures"),
            ("L4", "Research", "Test a falsifiable original hypothesis", "Produce a reviewable evidence package"),
        ]
    return [
        {"level": level, "title": title, "goal": goal, "acceptance": acceptance}
        for level, title, goal, acceptance in rows
    ]
