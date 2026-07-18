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

    def analyze_paper(
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
        prompt_version=str(payload.get("prompt_version", "knowledge-curriculum-v3")),
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
            "Create a grounded research curriculum, not merely a calendar. First bound "
            "the knowledge the learner must master: diagnose prerequisite gaps, build a "
            "dependency-ordered knowledge map, say what is in and out of scope, attach "
            "mastery checks and resource search queries, and define exit capabilities. "
            "Split the map into small capability gates, name the shortest path to paper "
            "literacy separately from the full research-ready path, and choose starter "
            "resources only from the supplied verified resource catalog, copying its "
            "URLs exactly. Keep every selected catalog node_id unchanged and create a "
            "matching knowledge node with that id. For every resource, prescribe only "
            "the needed sections and a stop rule. "
            "Only then project that curriculum onto a 7/30/90-day schedule. Every task "
            "needs a measurable deliverable and acceptance rule. Every paper id must "
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

    def analyze_paper(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        return self._request_json(
            context,
            "Create a progressive, evidence-grounded close reading of one paper. Every "
            "substantive item must cite supplied chunk ids. Copy evidence excerpts exactly "
            "from those chunks and preserve their page and section. Separate author claims, "
            "AI synthesis, and items needing verification. If document_status is "
            "abstract_only, do not claim detailed experiments, equations, ablations, or "
            "reproduction facts. Produce a three-minute brief, reading route, logic chain, "
            "method data flow, evidence audit, bounded prerequisites, L0-L3 reproduction "
            "route, active-recall checks, and cautious research extensions.",
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
        experience = context["request"]["experience_level"]
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
            ["补齐必备知识", "建立方向核心地图", "读懂并复现锚点论文", "形成可投稿假设"]
            if language == "zh-CN"
            else ["Close prerequisite gaps", "Build the core map", "Read and reproduce anchors", "Form a publishable hypothesis"]
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
        curriculum = _mock_knowledge_curriculum(
            direction,
            language,
            experience,
            anchor_ids,
            duration,
            int(context["request"].get("weekly_hours", 10)),
        )
        stages = []
        for index, (start, end) in enumerate(ranges):
            name = stage_names[min(index, len(stage_names) - 1)]
            relevant_nodes = curriculum["knowledge_scope"]["must_learn_node_ids"]
            chunk_size = max(1, len(relevant_nodes) // len(ranges))
            stage_node_ids = relevant_nodes[
                index * chunk_size : (index + 1) * chunk_size
            ]
            if index == len(ranges) - 1:
                stage_node_ids = relevant_nodes[index * chunk_size :]
            node_titles = [
                node["title"]
                for node in curriculum["knowledge_tree"]
                if node["id"] in stage_node_ids
            ]
            deliverable = (
                f"完成本阶段知识验收：{'、'.join(node_titles) or title}，并保存笔记、代码或结果证据。"
                if language == "zh-CN"
                else f"Pass the mastery checks for {', '.join(node_titles) or title} and retain notes, code, or result evidence."
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
                                (
                                    f"掌握知识节点：{'、'.join(node_titles)}。"
                                    if language == "zh-CN"
                                    else f"Master these knowledge nodes: {', '.join(node_titles)}."
                                )
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
                f"先圈定学习边界，再安排时间：本路线把“{title}”拆成 {len(curriculum['knowledge_tree'])} 个有依赖关系的知识节点，先补前置，再掌握方向核心、实验与研究能力；{duration} 天只是这张知识地图的一种时间投影。{summary}"
                if language == "zh-CN"
                else f"Bound the curriculum before scheduling it: {title} is decomposed into {len(curriculum['knowledge_tree'])} dependency-linked nodes spanning prerequisites, core concepts, experiments, and research. The {duration}-day calendar is only one projection of that map. {summary}"
            ),
            "duration_days": duration,
            **curriculum,
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

    def analyze_paper(
        self, context: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, int]]:
        from src.paper_analysis.mock_analyzer import build_mock_paper_analysis

        return build_mock_paper_analysis(context)


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


DIRECTION_KNOWLEDGE_AREAS: dict[str, list[tuple[str, str]]] = {
    "retrieval_truthfulness": [
        ("经典信息检索：倒排索引、BM25 与召回率", "Classical IR: inverted indexes, BM25, and recall"),
        ("稠密检索、向量表示与重排", "Dense retrieval, vector representations, and reranking"),
        ("RAG 上下文构造、路由与检索—生成协同", "RAG context construction, routing, and retrieval-generation coordination"),
        ("事实性、幻觉检测与可归因评测", "Factuality, hallucination detection, and attribution evaluation"),
        ("GraphRAG、数据污染与检索系统攻防", "GraphRAG, data poisoning, and retrieval-system security"),
    ],
    "agent_evaluation": [
        ("智能体循环、状态、记忆与工具调用协议", "Agent loops, state, memory, and tool-use protocols"),
        ("任务环境、工具沙箱与可控模拟器", "Task environments, tool sandboxes, and controlled simulators"),
        ("轨迹记录、长程信用分配与失败分类", "Trajectory logging, long-horizon credit, and failure taxonomies"),
        ("智能体能力、可靠性与风险评测指标", "Agent capability, reliability, and risk metrics"),
        ("多智能体协作、通信与系统性失效", "Multi-agent coordination, communication, and systemic failures"),
    ],
    "time_series_foundation": [
        ("时间序列统计：平稳性、趋势、季节性与自相关", "Time-series statistics: stationarity, trend, seasonality, and autocorrelation"),
        ("预测、分类、异常检测与缺失值任务定义", "Forecasting, classification, anomaly detection, and missing-value tasks"),
        ("时序 Transformer、状态空间模型与频域方法", "Time-series Transformers, state-space models, and frequency methods"),
        ("自监督时序表征与基础模型预训练", "Self-supervised temporal representations and foundation pretraining"),
        ("跨域适配、分布漂移与真实场景评测", "Domain adaptation, distribution shift, and real-world evaluation"),
    ],
    "llm_safety": [
        ("安全威胁建模、攻击面与风险分级", "Safety threat modeling, attack surfaces, and risk classification"),
        ("偏好对齐、拒答行为与安全训练数据", "Preference alignment, refusal behavior, and safety training data"),
        ("越狱、提示注入与自适应攻击", "Jailbreaks, prompt injection, and adaptive attacks"),
        ("偏见、公平性与价值冲突评测", "Bias, fairness, and value-conflict evaluation"),
        ("安全基准、红队协议与防御有效性", "Safety benchmarks, red-teaming protocols, and defense validity"),
    ],
    "efficient_llm": [
        ("推理时延、吞吐、显存与计算复杂度", "Inference latency, throughput, memory, and compute complexity"),
        ("注意力、KV Cache 与长上下文瓶颈", "Attention, KV cache, and long-context bottlenecks"),
        ("量化、剪枝、蒸馏与低秩适配", "Quantization, pruning, distillation, and low-rank adaptation"),
        ("Token 压缩、动态计算与推理路由", "Token compression, dynamic compute, and inference routing"),
        ("质量—效率权衡、硬件感知与端到端评测", "Quality-efficiency tradeoffs, hardware awareness, and end-to-end evaluation"),
    ],
    "multimodal_reasoning": [
        ("视觉、文本与音频编码器及表示空间", "Vision, text, and audio encoders and representation spaces"),
        ("跨模态对齐、融合与对比学习", "Cross-modal alignment, fusion, and contrastive learning"),
        ("视觉语言模型、视觉提示与多步推理", "Vision-language models, visual prompting, and multi-step reasoning"),
        ("细粒度 grounding、知识融合与幻觉", "Fine-grained grounding, knowledge fusion, and hallucination"),
        ("多模态数据构造、评测协议与污染检查", "Multimodal data construction, evaluation protocols, and contamination checks"),
    ],
    "causal_foundation": [
        ("概率图模型、结构因果模型与 do-演算", "Probabilistic graphs, structural causal models, and do-calculus"),
        ("混杂、可识别性、反事实与因果效应估计", "Confounding, identifiability, counterfactuals, and effect estimation"),
        ("因果发现的约束、评分与函数方法", "Constraint, score, and functional methods for causal discovery"),
        ("基础模型表征、干预与因果知识注入", "Foundation-model representations, interventions, and causal knowledge"),
        ("合成/真实数据验证与因果结论边界", "Synthetic/real validation and boundaries of causal claims"),
    ],
    "reasoning_rl": [
        ("MDP、价值函数、策略梯度与离线/在线 RL", "MDPs, value functions, policy gradients, and offline/online RL"),
        ("PPO、策略优化稳定性与采样效率", "PPO, policy-optimization stability, and sample efficiency"),
        ("奖励建模、过程监督与可验证奖励", "Reward modeling, process supervision, and verifiable rewards"),
        ("推理轨迹、搜索与测试时计算", "Reasoning traces, search, and test-time compute"),
        ("奖励投机、泛化与推理评测可靠性", "Reward hacking, generalization, and reasoning-evaluation reliability"),
    ],
    "embodied_memory": [
        ("机器人坐标系、感知、控制与运动规划", "Robot frames, perception, control, and motion planning"),
        ("POMDP、世界模型与长程记忆", "POMDPs, world models, and long-horizon memory"),
        ("视觉—语言—动作模型与动作 Token", "Vision-language-action models and action tokens"),
        ("长程具身任务、数据采集与仿真基准", "Long-horizon embodied tasks, data collection, and simulation benchmarks"),
        ("Sim2Real、错误恢复与真实机器人评测", "Sim2Real, error recovery, and real-robot evaluation"),
    ],
    "generative_vision_3d": [
        ("生成建模、扩散过程与条件控制", "Generative modeling, diffusion processes, and conditional control"),
        ("视频时序一致性、运动表示与长视频建模", "Video temporal consistency, motion representations, and long-video modeling"),
        ("相机模型、多视图几何与三维重建", "Camera models, multiview geometry, and 3D reconstruction"),
        ("NeRF、3D Gaussian 与可微渲染", "NeRF, 3D Gaussian splatting, and differentiable rendering"),
        ("生成质量、几何一致性与人类偏好评测", "Generation quality, geometric consistency, and human-preference evaluation"),
    ],
    "theory_optimization": [
        ("概率论、线性代数、凸分析与浓缩不等式", "Probability, linear algebra, convex analysis, and concentration inequalities"),
        ("泛化界、稳定性与复杂度度量", "Generalization bounds, stability, and complexity measures"),
        ("在线学习、多臂老虎机与后悔界", "Online learning, bandits, and regret bounds"),
        ("非凸优化、随机优化与收敛分析", "Non-convex, stochastic optimization, and convergence analysis"),
        ("理论假设、可证结论与经验验证的对应", "Connecting theoretical assumptions, guarantees, and empirical validation"),
    ],
    "pretraining_interpretability": [
        ("Transformer 内部计算、残差流与注意力机制", "Transformer computation, residual streams, and attention"),
        ("表征几何、特征形成与训练动力学", "Representation geometry, feature formation, and training dynamics"),
        ("探针、稀疏自编码器与机制解释", "Probing, sparse autoencoders, and mechanistic interpretation"),
        ("因果干预、消融与跨检查点比较", "Causal interventions, ablations, and checkpoint comparisons"),
        ("解释忠实性、可重复性与伪相关控制", "Interpretation faithfulness, reproducibility, and spurious-correlation controls"),
    ],
    "human_ai_creation": [
        ("HCI 研究方法、需求分析与交互设计", "HCI research methods, needs analysis, and interaction design"),
        ("用户研究、实验设计与定性/定量分析", "User studies, experimental design, and qualitative/quantitative analysis"),
        ("人机共创、混合主动交互与控制权", "Human-AI co-creation, mixed initiative, and user control"),
        ("叙事、可视化与创作过程建模", "Narrative, visualization, and modeling creative processes"),
        ("主观质量、行为指标、伦理与可复现评测", "Subjective quality, behavioral metrics, ethics, and reproducible evaluation"),
    ],
}


def _mock_knowledge_curriculum(
    direction: Dict[str, Any],
    language: str,
    experience: str,
    anchor_ids: list[str],
    duration_days: int,
    weekly_hours: int,
) -> dict[str, Any]:
    zh = language == "zh-CN"
    direction_title = str(_localized(direction["title"], language))
    category_foundation = "基础前置" if zh else "Prerequisites"
    category_core = "方向核心" if zh else "Direction core"
    category_practice = "论文与研究实践" if zh else "Paper and research practice"
    nodes = [
        _knowledge_node(
            "python_engineering",
            category_foundation,
            "implementation",
            "Python 与实验工程" if zh else "Python and experiment engineering",
            "所有后续复现都依赖可运行、可追踪的实验环境。" if zh else "Every later reproduction step depends on runnable, traceable experiments.",
            ["Python 数据结构、函数、类与包管理", "NumPy/Pandas/PyTorch 基本操作", "Git、虚拟环境、配置、日志和随机种子"] if zh else ["Python data structures, functions, classes, and packages", "Basic NumPy, Pandas, and PyTorch", "Git, environments, configuration, logging, and random seeds"],
            ["不要求先掌握大型系统开发", "不要求从零实现深度学习框架"] if zh else ["No need for large-system engineering first", "No need to implement a deep-learning framework"],
            [],
            ["能独立运行一个 PyTorch 训练脚本", "能保存环境、配置、日志并复跑同一结果"] if zh else ["Run a PyTorch training script independently", "Save environment, config, and logs and rerun the same result"],
            ["Python PyTorch 入门 实验复现", "Git virtual environment experiment reproducibility"],
            12,
        ),
        _knowledge_node(
            "math_probability",
            category_foundation,
            "working",
            "线性代数、概率与统计直觉" if zh else "Linear algebra, probability, and statistical intuition",
            "需要读懂张量、概率目标、指标波动和实验显著性。" if zh else "Needed to read tensors, probabilistic objectives, metric variance, and significance.",
            ["向量、矩阵、范数、相似度与特征分解", "条件概率、期望、方差与常见分布", "抽样、置信区间、假设检验与效应量"] if zh else ["Vectors, matrices, norms, similarity, and eigendecomposition", "Conditional probability, expectation, variance, and common distributions", "Sampling, confidence intervals, hypothesis tests, and effect size"],
            ["暂不要求完整测度论", "暂不要求所有公式的严格证明"] if zh else ["No measure theory yet", "No rigorous proof of every formula yet"],
            [],
            ["能解释余弦相似度、交叉熵和置信区间", "能判断一次小幅提升是否可能只是随机波动"] if zh else ["Explain cosine similarity, cross entropy, and confidence intervals", "Judge whether a small gain may be random variation"],
            ["线性代数 机器学习 直觉", "probability statistics for machine learning"],
            12,
        ),
        _knowledge_node(
            "ml_foundations",
            category_foundation,
            "working",
            "机器学习与优化基础" if zh else "Machine-learning and optimization foundations",
            "需要区分训练目标、泛化、过拟合、数据泄漏和优化问题。" if zh else "Needed to separate objectives, generalization, overfitting, leakage, and optimization issues.",
            ["监督/自监督学习与训练—验证—测试划分", "损失函数、梯度下降、正则化和超参数", "基线、消融、数据泄漏与分布外泛化"] if zh else ["Supervised/self-supervised learning and train/validation/test splits", "Losses, gradient descent, regularization, and hyperparameters", "Baselines, ablations, leakage, and out-of-distribution generalization"],
            ["暂不需要覆盖所有传统算法", "暂不追求优化理论证明"] if zh else ["No need to cover every classical algorithm", "No optimization proofs required yet"],
            ["python_engineering", "math_probability"],
            ["能解释训练损失下降但测试变差的原因", "能设计一个只改变单变量的消融实验"] if zh else ["Explain falling train loss with worse test results", "Design a one-variable ablation"],
            ["machine learning fundamentals generalization", "机器学习 基线 消融 数据泄漏"],
            12,
        ),
        _knowledge_node(
            "deep_learning_transformer",
            category_foundation,
            "working",
            "深度学习与 Transformer 基础" if zh else "Deep learning and Transformer foundations",
            "多数当前前沿论文默认读者理解神经网络、注意力和预训练范式。" if zh else "Most frontier papers assume neural networks, attention, and pretraining paradigms.",
            ["前向/反向传播、表示学习与优化稳定性", "注意力、位置编码、残差连接和归一化", "预训练、微调、提示学习与推理"] if zh else ["Forward/backpropagation, representation learning, and stability", "Attention, positional encoding, residuals, and normalization", "Pretraining, fine-tuning, prompting, and inference"],
            ["不要求从零训练大模型", "不要求记住每个模型架构变体"] if zh else ["No need to train a foundation model from scratch", "No need to memorize every architecture variant"],
            ["ml_foundations"],
            ["能画出 Transformer 数据流并解释张量形状", "能说清预训练、微调和推理的差别"] if zh else ["Draw Transformer data flow and explain tensor shapes", "Distinguish pretraining, fine-tuning, and inference"],
            ["Transformer illustrated tutorial", "PyTorch Transformer from scratch basics"],
            14,
        ),
    ]

    areas = DIRECTION_KNOWLEDGE_AREAS.get(direction["id"])
    if not areas:
        areas = [
            (f"{direction_title}的问题定义与术语", f"Problem definitions and terminology for {direction_title}"),
            (f"{direction_title}的数据集与基准", f"Datasets and benchmarks for {direction_title}"),
            (f"{direction_title}的主要方法族", f"Main method families for {direction_title}"),
            (f"{direction_title}的指标与失败模式", f"Metrics and failure modes for {direction_title}"),
            (f"{direction_title}的前沿分支与争议", f"Frontier branches and open debates in {direction_title}"),
        ]
    previous = "ml_foundations"
    for index, pair in enumerate(areas, 1):
        area = pair[0] if zh else pair[1]
        node_id = f"direction_core_{index}"
        nodes.append(
            _knowledge_node(
                node_id,
                category_core,
                "working" if index < 4 else "research",
                area,
                f"它是理解“{direction_title}”论文问题、方法或证据链不可跳过的一层。" if zh else f"This is a non-skippable layer for understanding the problems, methods, or evidence in {direction_title} papers.",
                [f"{area}的核心概念、常用符号和问题定义", f"{area}的主要方法族、假设与适用条件", f"{area}的典型数据、指标和失败模式"] if zh else [f"Core concepts, notation, and problem definitions of {area}", f"Main method families, assumptions, and operating conditions of {area}", f"Typical data, metrics, and failure modes of {area}"],
                [f"暂不遍历{area}的所有论文", "暂不学习与当前方向无关的工程变体"] if zh else [f"Do not survey every paper on {area} yet", "Defer engineering variants unrelated to the current direction"],
                [previous],
                [f"能用自己的话解释{area}并画出方法关系", f"能指出一篇锚点论文在{area}上的假设和弱点"] if zh else [f"Explain {area} and draw its method relationships", f"Identify an anchor paper's assumptions and weakness in {area}"],
                [f"{area} tutorial survey", f"{area} benchmark baseline"],
                6 + index * 2,
                anchor_ids,
            )
        )
        previous = node_id

    nodes.extend(
        [
            _knowledge_node(
                "paper_evidence",
                category_practice,
                "implementation",
                "论文证据拆解与阅读" if zh else "Paper evidence decomposition",
                "会读论文不等于读完论文；需要提取问题、假设、方法、实验与局限。" if zh else "Reading is not finishing pages; it is extracting the problem, assumptions, method, experiments, and limitations.",
                ["问题—方法—证据—局限四格笔记", "主张与实验表格/消融之间的对应", "锚点论文之间的共同假设和冲突"] if zh else ["Problem-method-evidence-limit notes", "Links between claims, result tables, and ablations", "Shared assumptions and conflicts across anchors"],
                ["不要求逐句翻译", "不要求从引言开始线性阅读"] if zh else ["No sentence-by-sentence translation", "No need to read linearly from the introduction"],
                ["direction_core_3"],
                ["能在十分钟内讲清一篇论文的证据链", "能指出作者没有证明的主张"] if zh else ["Explain a paper's evidence chain in ten minutes", "Identify a claim the paper did not establish"],
                [f"{direction_title} survey", "how to read machine learning papers critically"],
                8,
                anchor_ids,
            ),
            _knowledge_node(
                "reproducible_baseline",
                category_practice,
                "implementation",
                "基线复现与实验诊断" if zh else "Baseline reproduction and experiment diagnosis",
                "只有跑通、对齐并解释误差，才真正掌握论文方法。" if zh else "Real mastery requires running, matching, and explaining experimental error.",
                ["环境、数据、配置和随机种子固定", "指标实现与论文协议对齐", "误差来源、方差、失败样例和资源消耗"] if zh else ["Fix environment, data, config, and seeds", "Align metrics with the paper protocol", "Track error sources, variance, failures, and resource use"],
                ["不要求第一步复现全部实验", "不需要购买论文未依赖的昂贵算力"] if zh else ["Do not reproduce every experiment first", "Do not buy compute the paper does not require"],
                ["paper_evidence", "python_engineering"],
                ["第三方按 README 能跑出同一结果", "主要指标误差在预先声明范围内且能解释偏差"] if zh else ["A third party can rerun from the README", "Primary metric is within a declared tolerance and deviations are explained"],
                [f"{direction_title} GitHub baseline reproduction", "ML experiment reproducibility checklist"],
                18,
                anchor_ids,
            ),
            _knowledge_node(
                "research_design",
                category_practice,
                "research",
                "研究问题、对照实验与可证伪假设" if zh else "Research questions, controls, and falsifiable hypotheses",
                "复现之后必须能把失败或边界转成单变量、可验证的研究问题。" if zh else "After reproduction, failures or boundaries must become one-variable, testable research questions.",
                ["从失败分类提炼研究缺口", "形成单变量假设、强基线和公平对照", "报告均值、方差、消融、负结果和适用边界"] if zh else ["Turn failure taxonomies into research gaps", "Form one-variable hypotheses with strong baselines and fair controls", "Report means, variance, ablations, negative results, and scope"],
                ["暂不追求一次解决整个方向", "暂不把换模型或换数据当作创新"] if zh else ["Do not solve the whole field at once", "Do not treat a model or dataset swap as novelty"],
                ["reproducible_baseline"],
                ["能写出一句可被实验否定的假设", "能设计最小实验区分方法收益与数据/算力收益"] if zh else ["Write a hypothesis that an experiment can disprove", "Design a minimum experiment separating method gain from data/compute gain"],
                [f"{direction_title} open problems", "machine learning experimental design ablation"],
                12,
                anchor_ids,
            ),
        ]
    )

    optional_ids = (
        ["deep_learning_transformer"]
        if direction["id"] in {"time_series_foundation", "causal_foundation", "theory_optimization"}
        else []
    )
    must_ids = [node["id"] for node in nodes if node["id"] not in optional_ids]
    minimum_viable_ids = [
        node_id
        for node_id in [
            "python_engineering",
            "math_probability",
            "ml_foundations",
            "deep_learning_transformer",
            "direction_core_1",
            "direction_core_2",
            "direction_core_3",
            "paper_evidence",
        ]
        if node_id in must_ids
    ]
    full_hours = sum(node["estimated_hours"] for node in nodes if node["id"] in must_ids)
    remaining_factor = {"zero": 1.0, "beginner": 0.78, "intermediate": 0.52, "advanced": 0.32}.get(experience, 0.52)
    total_hours = round(full_hours * remaining_factor, 1)
    minimum_viable_hours = round(
        sum(
            node["estimated_hours"]
            for node in nodes
            if node["id"] in minimum_viable_ids
        )
        * remaining_factor,
        1,
    )
    available_hours = round(duration_days / 7 * weekly_hours, 1)
    feasibility = (
        "feasible"
        if available_hours >= total_hours
        else "tight"
        if available_hours >= total_hours * 0.7
        else "unrealistic"
    )
    start_labels = {
        "zero": ("零基础：默认不具备编程、数学和机器学习前置" if zh else "Zero foundation: no programming, mathematics, or ML prerequisites assumed"),
        "beginner": ("入门：能运行示例，但核心概念和实验方法不稳定" if zh else "Beginner: can run examples but lacks stable concepts and experiment practice"),
        "intermediate": ("中等：具备机器学习基础，需要补方向核心和研究实践" if zh else "Intermediate: has ML basics and needs direction core plus research practice"),
        "advanced": ("进阶：前置知识作为快速诊断，重点定位前沿边界和研究缺口" if zh else "Advanced: prerequisites are diagnostic; focus on frontier boundaries and gaps"),
    }
    gaps = _mock_gap_diagnosis(experience, language)
    return {
        "knowledge_scope": {
            "starting_point": start_labels.get(experience, start_labels["intermediate"]),
            "target_capability": (
                f"能独立读懂“{direction_title}”前沿论文，复现一篇锚点工作，并设计一个公平、可证伪的最小改进实验。"
                if zh
                else f"Independently understand frontier {direction_title} papers, reproduce one anchor, and design a fair, falsifiable minimum extension."
            ),
            "must_learn_node_ids": must_ids,
            "optional_node_ids": optional_ids,
            "minimum_viable_node_ids": minimum_viable_ids,
            "research_ready_node_ids": must_ids,
            "defer_topics": (
                ["完整数学证明与所有理论分支", "从零预训练大模型或搭建大规模分布式系统", "与当前研究问题无关的相邻方向", "一次性复现论文全部附录实验"]
                if zh
                else ["Full proofs and every theoretical branch", "Training a foundation model or building a distributed stack from scratch", "Adjacent fields unrelated to the chosen question", "Reproducing every appendix experiment at once"]
            ),
            "exit_criteria": (
                ["能画出知识依赖图并解释每个核心节点", "能用证据卡比较至少三篇锚点论文", "能复现一个强基线并解释误差", "能提出一个带强基线、控制变量和失败条件的研究假设"]
                if zh
                else ["Draw the dependency map and explain each core node", "Compare at least three anchors with evidence cards", "Reproduce a strong baseline and explain error", "Propose a hypothesis with a strong baseline, controlled variable, and failure condition"]
            ),
            "minimum_viable_hours": minimum_viable_hours,
            "estimated_total_hours": total_hours,
            "available_hours": available_hours,
            "feasibility": feasibility,
            "projection_note": (
                f"按每周 {weekly_hours} 小时，{duration_days} 天约有 {available_hours} 小时；先达到结构化读论文约需 {minimum_viable_hours} 小时，达到独立复现和研究设计约需 {total_hours} 小时。时间不足时先停在最近的能力关卡并延长周期，不伪装成已经掌握。"
                if zh
                else f"At {weekly_hours} hours/week, {duration_days} days provides about {available_hours} hours. Structured paper literacy needs about {minimum_viable_hours} hours; independent reproduction and research design need about {total_hours}. Stop at the nearest capability gate and extend the timeline instead of pretending mastery."
            ),
        },
        "gap_diagnosis": gaps,
        "knowledge_tree": nodes,
        "mastery_milestones": _mock_mastery_milestones(
            nodes, must_ids, language, remaining_factor
        ),
        "starter_resources": _mock_starter_resources(
            direction["id"], language, must_ids
        ),
    }


def _mock_mastery_milestones(
    nodes: list[dict[str, Any]],
    must_ids: list[str],
    language: str,
    remaining_factor: float,
) -> list[dict[str, Any]]:
    zh = language == "zh-CN"
    definitions = [
        (
            "gate_1_tools_math",
            "关卡 1：能运行，也能看懂数字" if zh else "Gate 1: Run code and read the numbers",
            ["python_engineering", "math_probability"],
            "独立运行小实验，并解释张量、相似度和结果波动。" if zh else "Run a small experiment and explain tensors, similarity, and result variance.",
            ["从空目录建立环境并运行训练脚本", "用自己的话解释一个指标和置信区间"] if zh else ["Create an environment and run a training script from an empty folder", "Explain one metric and its confidence interval in your own words"],
            ["只看视频而没有亲手运行", "会套公式但不知道数值代表什么"] if zh else ["Watching without running anything", "Applying formulas without interpreting the values"],
        ),
        (
            "gate_2_ml",
            "关卡 2：能判断模型是否真的学会" if zh else "Gate 2: Judge whether a model really learned",
            ["ml_foundations", "deep_learning_transformer"],
            "解释训练、泛化与注意力，并设计一个无泄漏的单变量实验。" if zh else "Explain training, generalization, and attention, then design a leakage-free one-variable experiment.",
            ["定位一次过拟合或泄漏", "画出模型数据流并标注输入输出"] if zh else ["Diagnose one overfitting or leakage case", "Draw model data flow with inputs and outputs"],
            ["把训练损失下降当成研究结论", "同时改多个变量后归因"] if zh else ["Treating lower train loss as a research conclusion", "Changing several variables and claiming causality"],
        ),
        (
            "gate_3_paper_literacy",
            "关卡 3：能结构化读懂方向论文" if zh else "Gate 3: Read direction papers structurally",
            ["direction_core_1", "direction_core_2", "direction_core_3", "paper_evidence"],
            "不用逐句翻译，也能讲清一篇论文的问题、方法、证据和局限。" if zh else "Explain a paper's problem, method, evidence, and limits without translating every sentence.",
            ["十分钟口述一篇锚点论文的证据链", "比较三篇论文的方法假设和失败模式"] if zh else ["Give a ten-minute evidence-chain account of one anchor", "Compare assumptions and failures across three papers"],
            ["收藏很多论文但没有证据卡", "只复述摘要和作者结论"] if zh else ["Collecting papers without evidence cards", "Repeating only abstracts and author conclusions"],
        ),
        (
            "gate_4_frontier",
            "关卡 4：能定位前沿争议和空白" if zh else "Gate 4: Locate frontier disputes and gaps",
            ["direction_core_4", "direction_core_5"],
            "指出现有结论依赖的边界、冲突证据和仍未验证的假设。" if zh else "Identify boundaries, conflicting evidence, and assumptions that remain untested.",
            ["列出至少两个跨论文冲突", "把一个开放问题改写成可验证条件"] if zh else ["List at least two cross-paper conflicts", "Rewrite one open question as a testable condition"],
            ["把论文数量少误认为研究空白", "把换模型名称当成新问题"] if zh else ["Mistaking few papers for a research gap", "Treating a model-name swap as a new problem"],
        ),
        (
            "gate_5_research",
            "关卡 5：能复现并形成最小研究闭环" if zh else "Gate 5: Reproduce and close a minimum research loop",
            ["reproducible_baseline", "research_design"],
            "复现一个强基线，并用公平对照检验一句可被否定的假设。" if zh else "Reproduce a strong baseline and test one falsifiable hypothesis with fair controls.",
            ["第三方可按 README 复跑", "负结果能够明确否定或收缩假设"] if zh else ["A third party can rerun from the README", "A negative result can reject or narrow the hypothesis"],
            ["只展示最好一次结果", "没有强基线、方差或失败样例"] if zh else ["Reporting only the best run", "Missing a strong baseline, variance, or failure cases"],
        ),
    ]
    hours = {node["id"]: node["estimated_hours"] for node in nodes}
    milestones = []
    for milestone_id, title, node_ids, capability, checks, failures in definitions:
        scoped_ids = [node_id for node_id in node_ids if node_id in must_ids]
        if not scoped_ids:
            continue
        milestones.append(
            {
                "id": milestone_id,
                "title": title,
                "node_ids": scoped_ids,
                "capability": capability,
                "gate_checks": checks,
                "common_failures": failures,
                "estimated_hours": round(
                    sum(hours[node_id] for node_id in scoped_ids) * remaining_factor,
                    1,
                ),
            }
        )
    return milestones


def _mock_starter_resources(
    direction_id: str, language: str, must_ids: list[str]
) -> list[dict[str, Any]]:
    zh = language == "zh-CN"
    resources = [
        {
            "id": "cs50p",
            "title": "CS50's Introduction to Programming with Python",
            "provider": "Harvard CS50",
            "resource_type": "course",
            "url": "https://cs50.harvard.edu/python/",
            "language": "English",
            "node_ids": ["python_engineering"],
            "recommended_sections": ["Weeks 0-4: functions, conditionals, loops, exceptions, libraries", "Week 5: unit tests", "Week 6: file I/O"],
            "purpose": "为没有编程经历的学生建立能读、改、调试研究脚本的最低能力。" if zh else "Build the minimum ability to read, edit, and debug research scripts without prior programming experience.",
            "stop_rule": "完成一个读取 CSV、计算指标并带测试的小程序后停止；暂不学正则与完整面向对象。" if zh else "Stop after a tested program reads a CSV and computes a metric; defer regex and full object-oriented coverage.",
        },
        {
            "id": "mit_linear_algebra",
            "title": "MIT OpenCourseWare 18.06SC Linear Algebra",
            "provider": "MIT OpenCourseWare",
            "resource_type": "course",
            "url": "https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/",
            "language": "English",
            "node_ids": ["math_probability"],
            "recommended_sections": ["Unit I: geometry of linear equations", "Unit II: least squares and eigenvalues"],
            "purpose": "补齐读张量、相似度、投影和特征分解所需的线性代数直觉。" if zh else "Build intuition for tensors, similarity, projections, and eigendecomposition.",
            "stop_rule": "能手算小矩阵乘法、解释投影和特征向量后停止；暂不追求全部证明与习题。" if zh else "Stop once you can multiply small matrices and explain projection and eigenvectors; defer full proofs and problem sets.",
        },
        {
            "id": "d2l",
            "title": "Dive into Deep Learning",
            "provider": "D2L.ai",
            "resource_type": "interactive_book",
            "url": "https://d2l.ai/",
            "language": "English / Chinese editions",
            "node_ids": ["math_probability", "ml_foundations", "deep_learning_transformer"],
            "recommended_sections": ["2. Preliminaries", "3-5. Linear models and MLPs", "11. Attention mechanisms and Transformers"],
            "purpose": "把数学、代码和神经网络放在同一个可运行叙事中。" if zh else "Connect mathematics, code, and neural networks in one runnable narrative.",
            "stop_rule": "每章只做一个可运行练习并通过对应能力关卡；不要顺序读完整本书。" if zh else "Do one runnable exercise per selected chapter and stop when its gate passes; do not read the whole book sequentially.",
        },
        {
            "id": "pytorch_basics",
            "title": "Learn the Basics — PyTorch Tutorials",
            "provider": "PyTorch",
            "resource_type": "tutorial",
            "url": "https://docs.pytorch.org/tutorials/beginner/basics/index.html",
            "language": "English",
            "node_ids": ["python_engineering", "ml_foundations", "deep_learning_transformer"],
            "recommended_sections": ["Tensors and datasets", "Build model", "Autograd", "Optimization loop", "Save and load"],
            "purpose": "用官方最小样例跑通数据—模型—训练—保存的完整闭环。" if zh else "Run the official minimal data-model-training-save loop.",
            "stop_rule": "能从空文件重写一个小训练循环并保存模型后停止；不刷完所有教程。" if zh else "Stop after rewriting a small training loop from an empty file and saving the model; do not complete every tutorial.",
        },
    ]
    if "deep_learning_transformer" in must_ids:
        resources.append(
            {
                "id": "hf_llm_course",
                "title": "Hugging Face LLM Course",
                "provider": "Hugging Face",
                "resource_type": "course",
                "url": "https://huggingface.co/learn/llm-course/chapter1/1",
                "language": "English",
                "node_ids": ["deep_learning_transformer"],
                "recommended_sections": ["Chapter 1: Transformer models", "Chapter 2: Using Transformers"],
                "purpose": "建立现代 Transformer 模型的使用和组件直觉。" if zh else "Build working intuition for modern Transformer use and components.",
                "stop_rule": "能解释 tokenizer—model—logits 流程并修改一个推理样例后停止；暂不学部署和分布式训练。" if zh else "Stop after explaining tokenizer-model-logits flow and modifying an inference example; defer deployment and distributed training.",
            }
        )
    if direction_id == "retrieval_truthfulness":
        resources.append(
            {
                "id": "stanford_ir",
                "title": "Introduction to Information Retrieval",
                "provider": "Stanford NLP Group",
                "resource_type": "book",
                "url": "https://nlp.stanford.edu/IR-book/html/htmledition/irbook.html",
                "language": "English",
                "node_ids": ["direction_core_1", "direction_core_2"],
                "recommended_sections": ["Chapter 1: Boolean retrieval", "Chapter 6: scoring and vector space", "Chapter 8: evaluation"],
                "purpose": "先掌握检索、排序和评测，再进入 RAG 与事实性前沿。" if zh else "Master retrieval, ranking, and evaluation before entering RAG and factuality research.",
                "stop_rule": "能手算一次 TF-IDF 排序并解释 precision/recall 后停止；暂不读完整索引工程。" if zh else "Stop after manually ranking with TF-IDF and explaining precision/recall; defer full indexing engineering.",
            }
        )
    known = set(must_ids) | {"deep_learning_transformer"}
    for resource in resources:
        resource["node_ids"] = [node_id for node_id in resource["node_ids"] if node_id in known]
    return [resource for resource in resources if resource["node_ids"]]


def verified_resource_catalog(
    direction_id: str, language: str
) -> list[dict[str, Any]]:
    """Return the small, reviewed URL allowlist exposed to paid model calls."""

    all_curriculum_nodes = [
        "python_engineering",
        "math_probability",
        "ml_foundations",
        "deep_learning_transformer",
        "direction_core_1",
        "direction_core_2",
    ]
    return _mock_starter_resources(direction_id, language, all_curriculum_nodes)


def _knowledge_node(
    node_id: str,
    category: str,
    depth: str,
    title: str,
    why_required: str,
    what_to_learn: list[str],
    not_required: list[str],
    prerequisites: list[str],
    mastery_checks: list[str],
    resource_queries: list[str],
    estimated_hours: float,
    evidence_paper_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "category": category,
        "depth": depth,
        "title": title,
        "why_required": why_required,
        "what_to_learn": what_to_learn,
        "not_required": not_required,
        "prerequisites": prerequisites,
        "mastery_checks": mastery_checks,
        "resource_queries": resource_queries,
        "evidence_paper_ids": evidence_paper_ids or [],
        "estimated_hours": estimated_hours,
    }


def _mock_gap_diagnosis(experience: str, language: str) -> list[dict[str, Any]]:
    zh = language == "zh-CN"
    rows = {
        "zero": [
            ("编程与实验环境", "默认尚不能独立运行研究代码", "可独立管理并复跑 PyTorch 实验", ["能否解释虚拟环境、依赖和随机种子的作用？", "能否修改配置并定位一次报错？"], ["python_engineering"]),
            ("数学与统计", "默认缺少读公式和判断实验波动的基础", "能理解论文常见公式、指标和不确定性", ["能否解释向量相似度、期望和方差？", "能否判断 0.3% 提升是否可信？"], ["math_probability"]),
            ("机器学习", "默认不了解训练、泛化和实验对照", "能识别过拟合、泄漏并设计消融", ["训练集、验证集和测试集为何要分开？", "什么叫只改变一个变量？"], ["ml_foundations", "deep_learning_transformer"]),
            ("研究实践", "默认只会阅读结论，尚不能建立证据链", "能读懂、复现并形成可证伪假设", ["能否说出论文主张由哪张表支持？", "能否定义一次失败如何否定假设？"], ["paper_evidence", "reproducible_baseline", "research_design"]),
        ],
        "beginner": [
            ("机器学习概念", "能运行示例但知识点可能彼此孤立", "形成训练、评测与泛化的完整框架", ["能否解释损失与最终指标的区别？", "能否识别数据泄漏？"], ["ml_foundations", "deep_learning_transformer"]),
            ("研究实践", "缺少从论文到复现实验的闭环", "能复现并诊断基线", ["能否保存全部配置和原始日志？", "能否解释复现偏差？"], ["paper_evidence", "reproducible_baseline", "research_design"]),
        ],
        "intermediate": [
            ("方向知识", "已有通用基础，但方向概念和方法关系未成体系", "建立可解释的方向核心地图", ["能否比较该方向三类方法的假设？", "能否说清主流基准的盲点？"], ["direction_core_1", "direction_core_2", "direction_core_3", "direction_core_4", "direction_core_5"]),
            ("研究出口", "能读论文但不一定能把失败转成研究问题", "形成公平且可证伪的最小实验", ["假设能否被一个负结果否定？", "是否包含强基线与控制变量？"], ["reproducible_baseline", "research_design"]),
        ],
        "advanced": [
            ("前沿边界", "通用能力已具备，需要快速定位证据冲突和空白", "用复现失败形成研究缺口", ["哪些结论只在单一数据集成立？", "现有方法共享什么未验证假设？"], ["direction_core_4", "direction_core_5", "paper_evidence", "research_design"]),
        ],
    }
    selected = rows.get(experience, rows["intermediate"])
    if zh:
        return [
            {
                "area": area,
                "current_assumption": current,
                "target_level": target,
                "diagnostic_questions": questions,
                "bridge_node_ids": node_ids,
            }
            for area, current, target, questions, node_ids in selected
        ]
    return [
        {
            "area": {
                "编程与实验环境": "Programming and experiment environment",
                "数学与统计": "Mathematics and statistics",
                "机器学习": "Machine learning",
                "研究实践": "Research practice",
                "机器学习概念": "Machine-learning concepts",
                "方向知识": "Direction knowledge",
                "研究出口": "Research path",
                "前沿边界": "Frontier boundary",
            }.get(area, area),
            "current_assumption": {
                "zero": "No prerequisite mastery is assumed.",
                "beginner": "Can run examples, but knowledge and research practice are fragmented.",
                "intermediate": "General ML foundations exist, but direction knowledge needs structure.",
                "advanced": "General capability exists; frontier evidence and gaps need diagnosis.",
            }.get(experience, "Current capability needs diagnosis."),
            "target_level": "Pass the linked knowledge-node mastery checks.",
            "diagnostic_questions": [
                "Can you explain this area without notes?",
                "Can you produce evidence by code, calculation, or a paper result?",
            ],
            "bridge_node_ids": node_ids,
        }
        for area, _current, _target, _questions, node_ids in selected
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
