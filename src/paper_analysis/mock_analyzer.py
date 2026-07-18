"""Deterministic paper-analysis generator for free local evaluation."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


def build_mock_paper_analysis(
    context: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    paper = context["paper"]
    document = context["document"]
    request = context["request"]
    zh = request["language"] == "zh-CN"
    chunks = document["chunks"]

    def tr(zh_text: str, en_text: str) -> str:
        return zh_text if zh else en_text

    def choose(terms: List[str], fallback: int = 0) -> Dict[str, Any]:
        lowered = [term.casefold() for term in terms]
        return next(
            (
                chunk
                for chunk in chunks
                if any(term in chunk["text"].casefold() for term in lowered)
            ),
            chunks[min(fallback, len(chunks) - 1)],
        )

    evidence_specs = [
        ("problem", ["challenge", "problem", "however", "问题", "挑战"], 0),
        ("method", ["we propose", "we introduce", "method", "framework", "提出"], 0),
        ("result", ["experiment", "results", "outperform", "实验", "结果"], 0),
        ("evaluation", ["dataset", "benchmark", "metric", "baseline", "数据集"], 1),
        ("limitation", ["limitation", "future work", "fails", "局限", "限制"], 2),
        ("detail", ["architecture", "training", "objective", "loss", "algorithm"], 1),
    ]
    evidence = []
    for name, terms, fallback in evidence_specs:
        chunk = choose(terms, fallback)
        evidence.append(
            {
                "id": f"evidence_{name}",
                "chunk_id": chunk["id"],
                "page": int(chunk["page"]),
                "section": chunk["section"],
                "excerpt": chunk["text"][:700],
                "evidence_type": (
                    "author_statement"
                    if name not in {"limitation", "detail"}
                    else "needs_verification"
                ),
            }
        )

    abstract = str(paper.get("abstract") or "").strip()
    sentences = [
        value.strip()
        for value in re.split(r"(?<=[.!?。！？])\s+", abstract)
        if value.strip()
    ]
    first = sentences[0] if sentences else paper["title"]
    method_sentence = next(
        (
            value
            for value in sentences
            if re.search(r"\b(?:we propose|we introduce|we present|our approach)\b", value, re.I)
        ),
        sentences[min(1, len(sentences) - 1)] if sentences else first,
    )
    result_sentence = next(
        (
            value
            for value in reversed(sentences)
            if re.search(r"\b(?:results?|experiments?|outperform|show|demonstrate)\b", value, re.I)
        ),
        sentences[-1] if sentences else first,
    )
    status = document["status"]
    full_text = status == "full_text"
    scope_note = tr(
        f"已解析公开 PDF 的 {document['page_count']} 页正文；结论仍应通过页码证据复核。"
        if full_text
        else "公开 PDF 未能取得或解析，本次只基于题目和摘要；方法细节、实验与复现均为待核查路线。",
        f"Parsed {document['page_count']} PDF pages; verify conclusions against the cited pages."
        if full_text
        else "The public PDF was unavailable or unparseable. This analysis uses title and abstract only; method, experiment, and reproduction details remain provisional.",
    )
    warnings = []
    if not full_text:
        warnings.append(
            tr(
                "当前是摘要级分析，不能证明具体实验设置、消融结果或公式细节。",
                "This is abstract-level analysis and cannot establish detailed experiments, ablations, or equations.",
            )
        )
    if document.get("error"):
        warnings.append(
            tr("PDF 获取信息：", "PDF acquisition note: ")
            + document["error"].get("message", "")
        )

    problem = tr(
        f"论文围绕“{paper['title']}”所代表的问题展开。摘要首先指出：{first}",
        f"The paper studies the problem represented by “{paper['title']}”. Its opening claim is: {first}",
    )
    approach = tr(
        f"作者的核心方案可先压缩为：{method_sentence}",
        f"The core approach can first be compressed to: {method_sentence}",
    )
    result = tr(
        f"当前可直接核查的结果陈述是：{result_sentence}",
        f"The directly inspectable result claim is: {result_sentence}",
    )
    limitation = tr(
        "需要重点核查论文是否报告失败案例、方差、数据泄漏、额外算力和跨数据集泛化；摘要本身不足以排除这些风险。",
        "Check whether the paper reports failures, variance, leakage, extra compute, and cross-dataset generalization; the abstract alone cannot rule these risks out.",
    )
    insight = lambda title, explanation, evidence_id: {
        "title": title,
        "explanation": explanation,
        "evidence_ids": [evidence_id],
    }
    pages = sorted({int(item["page"]) for item in evidence if int(item["page"]) > 0})
    first_page = pages[:1]
    result_pages = sorted(
        {
            item["page"]
            for item in evidence
            if item["id"] in {"evidence_result", "evidence_evaluation"} and item["page"] > 0
        }
    )
    concepts = _concepts_from_paper(paper)
    code_urls = re.findall(r"https://github\.com/[\w.-]+/[\w.-]+", abstract)
    code_note = code_urls[0] if code_urls else tr(
        "当前元数据未提供已核验的官方代码仓库。",
        "The current metadata contains no verified official code repository.",
    )

    artifact = {
        "artifact_version": 1,
        "paper_id": paper["id"],
        "paper_title": paper["title"],
        "document_status": status,
        "scope_note": scope_note,
        "warnings": warnings,
        "evidence": evidence,
        "quick_brief": {
            "one_sentence": tr(
                f"这篇论文针对一个已有方法仍未充分解决的问题，提出了特定框架，并报告了改进；快速阅读时必须把“作者声称有效”和“实验真正证明有效”分开。",
                "The paper targets a gap in prior methods, proposes a specific framework, and reports an improvement; read it by separating the authors' claim from what the experiments actually establish.",
            ),
            "research_question": insight(tr("研究问题", "Research question"), problem, "evidence_problem"),
            "motivation": insight(
                tr("为什么值得研究", "Why it matters"),
                tr("这个问题会影响方法能否在目标场景中可靠、可扩展地工作。", "The problem affects whether the method works reliably and at scale in its target setting."),
                "evidence_problem",
            ),
            "prior_gap": insight(
                tr("以前缺什么", "Prior gap"),
                tr("现有方案仍有摘要中指出的能力、验证或可用性缺口；精读时应把缺口对应到具体基线。", "Prior work retains a capability, validation, or usability gap named in the source; map that gap to concrete baselines during close reading."),
                "evidence_problem",
            ),
            "approach": insight(tr("作者怎么做", "Approach"), approach, "evidence_method"),
            "main_result": insight(tr("主要结果", "Main result"), result, "evidence_result"),
            "limitation": insight(tr("最大风险", "Main risk"), limitation, "evidence_limitation"),
        },
        "reading_route": [
            {
                "order": 1,
                "title": tr("先抓住问题与结论", "Capture problem and conclusion"),
                "instruction": tr("读摘要、引言开头和主要结果陈述，写出问题—方法—结果三句话。", "Read the abstract, opening motivation, and main result; write problem–method–result in three sentences."),
                "purpose": tr("先建立论文骨架，避免一开始陷入公式。", "Build the paper skeleton before entering details."),
                "page_numbers": first_page,
                "evidence_ids": ["evidence_problem", "evidence_result"],
            },
            {
                "order": 2,
                "title": tr("拆解方法数据流", "Trace the method data flow"),
                "instruction": tr("按输入、核心变换、输出画一张流程图，并标记真正新增的模块。", "Draw input, core transformations, and output; mark the genuinely new module."),
                "purpose": tr("确认贡献是新机制、组合方式还是评测设计。", "Determine whether the contribution is a mechanism, composition, or evaluation design."),
                "page_numbers": pages[:3],
                "evidence_ids": ["evidence_method", "evidence_detail"],
            },
            {
                "order": 3,
                "title": tr("审查实验证据", "Audit experimental evidence"),
                "instruction": tr("逐项记录数据集、基线、指标、主结果、消融和失败案例；缺失项标为未证明。", "Record datasets, baselines, metrics, main results, ablations, and failures; mark missing items as unproven."),
                "purpose": tr("判断实验是否真的支撑作者结论。", "Judge whether the experiments support the claim."),
                "page_numbers": result_pages,
                "evidence_ids": ["evidence_evaluation", "evidence_result", "evidence_limitation"],
            },
        ],
        "logic_chain": [
            {"stage": "problem", "content": problem, "evidence_ids": ["evidence_problem"]},
            {"stage": "prior_work", "content": tr("现有方法构成作者比较和改进的起点。", "Prior methods form the comparison and improvement baseline."), "evidence_ids": ["evidence_problem"]},
            {"stage": "gap", "content": tr("作者认为现有方法在目标条件下仍存在关键缺口。", "The authors argue that prior methods retain a key gap under the target conditions."), "evidence_ids": ["evidence_problem"]},
            {"stage": "hypothesis", "content": tr("核心假设是新设计能够缓解该缺口，同时保持目标能力。", "The central hypothesis is that the new design reduces the gap while preserving the target capability."), "evidence_ids": ["evidence_method"]},
            {"stage": "method", "content": approach, "evidence_ids": ["evidence_method", "evidence_detail"]},
            {"stage": "evidence", "content": result, "evidence_ids": ["evidence_result", "evidence_evaluation"]},
            {"stage": "conclusion", "content": tr("结论是否成立取决于基线公平性、评测覆盖和失败分析。", "The conclusion depends on baseline fairness, evaluation coverage, and failure analysis."), "evidence_ids": ["evidence_result", "evidence_limitation"]},
        ],
        "method_modules": [
            {
                "id": "module_problem_representation",
                "title": tr("问题表示", "Problem representation"),
                "purpose": tr("把原始任务转成模型可以处理的输入和约束。", "Turn the raw task into model-ready inputs and constraints."),
                "input": tr("论文定义的原始数据或任务实例", "Raw data or task instances defined by the paper"),
                "process": tr("预处理、表示或上下文构造", "Preprocessing, representation, or context construction"),
                "output": tr("核心方法的标准化输入", "Normalized input for the core method"),
                "why_it_matters": tr("输入定义决定了比较是否公平以及方法能处理什么。", "Input definition controls comparison fairness and applicability."),
                "evidence_ids": ["evidence_problem", "evidence_detail"],
            },
            {
                "id": "module_core_method",
                "title": tr("核心机制", "Core mechanism"),
                "purpose": tr("实现作者声称的主要改进。", "Implement the paper's claimed improvement."),
                "input": tr("标准化输入和模型状态", "Normalized inputs and model state"),
                "process": approach,
                "output": tr("预测、生成结果或中间表示", "Prediction, generation, or intermediate representation"),
                "why_it_matters": tr("这是复现时最需要与基线隔离比较的变量。", "This is the variable that reproduction should isolate against the baseline."),
                "evidence_ids": ["evidence_method"],
            },
            {
                "id": "module_evaluation",
                "title": tr("输出与评测", "Output and evaluation"),
                "purpose": tr("把方法输出转成可与基线比较的证据。", "Turn outputs into evidence comparable with baselines."),
                "input": tr("方法输出和参考答案或评测规则", "Method outputs and references or evaluation rules"),
                "process": tr("计算指标、运行消融并整理失败案例", "Compute metrics, run ablations, and organize failures"),
                "output": result,
                "why_it_matters": tr("指标和协议比单个最好分数更能决定结论可信度。", "Metrics and protocol matter more than one best score."),
                "evidence_ids": ["evidence_evaluation", "evidence_result"],
            },
        ],
        "equations": [],
        "experiment_review": [
            {
                "question": tr("主实验是否支持核心主张？", "Does the main experiment support the core claim?"),
                "finding": result,
                "strength": "partial",
                "caution": tr("需要核对完整表格、方差、基线配置和统计显著性。", "Verify full tables, variance, baseline settings, and statistical significance."),
                "evidence_ids": ["evidence_result", "evidence_evaluation"],
            },
            {
                "question": tr("论文是否证明各模块不可替代？", "Does the paper establish that each module is necessary?"),
                "finding": tr("必须通过消融实验逐模块核查；当前分析不把摘要中的整体提升当成模块证明。", "Audit each module through ablation; an aggregate abstract claim is not module-level proof."),
                "strength": "partial" if full_text else "not_shown",
                "caution": tr("没有消融或对照时，只能证明整个系统相关，不能证明因果贡献。", "Without ablation or controls, the system may correlate with gains without establishing causal contribution."),
                "evidence_ids": ["evidence_evaluation", "evidence_limitation"],
            },
            {
                "question": tr("失败边界是否清楚？", "Are failure boundaries clear?"),
                "finding": tr("把未报告的分布、长尾案例和资源条件列为待验证项。", "Treat unreported distributions, tail cases, and resource conditions as open checks."),
                "strength": "not_shown",
                "caution": limitation,
                "evidence_ids": ["evidence_limitation"],
            },
        ],
        "knowledge_map": _knowledge_map(concepts, zh),
        "reproduction_plan": _reproduction_plan(code_note, paper, zh),
        "mastery_checks": _mastery_checks(zh),
        "research_extensions": [
            {
                "id": "extension_failure_boundary",
                "idea": tr("系统化构造原论文覆盖不足的失败场景。", "Systematically construct failure cases under-covered by the paper."),
                "difference": tr("贡献重点从继续刷平均分转为定义并解释可靠性边界。", "Shift the contribution from average-score gains to defining and explaining reliability boundaries."),
                "minimum_experiment": tr("复现一个基线和作者方法，在一个受控变量上分桶报告性能与失败类型。", "Reproduce one baseline and the method, then bucket performance and failure types along one controlled variable."),
                "novelty_risk": tr("如果只是换数据集而没有新发现，新颖性不足。", "A dataset swap without a new finding is not novel enough."),
                "resource_need": tr("沿用原论文最小配置；优先单卡或 CPU 可运行的子集。", "Reuse the smallest original setup; prefer a single-GPU or CPU-compatible subset."),
                "evidence_ids": ["evidence_result", "evidence_limitation"],
            },
            {
                "id": "extension_efficiency",
                "idea": tr("隔离核心模块，研究更低数据或算力下是否仍有效。", "Isolate the core module and test whether it survives lower data or compute."),
                "difference": tr("把原方法转化为资源受限、可解释的最小版本。", "Turn the method into a resource-bounded, interpretable minimum version."),
                "minimum_experiment": tr("固定数据和评测，仅改变一个资源变量，报告均值、方差和退化曲线。", "Fix data and evaluation, vary one resource variable, and report mean, variance, and degradation curves."),
                "novelty_risk": tr("单纯压缩模型属于工程优化，必须解释何时有效和为何有效。", "Plain compression is engineering unless it explains when and why it works."),
                "resource_need": tr("从论文最小公开配置开始，先做一条曲线。", "Start from the smallest public setup and produce one controlled curve."),
                "evidence_ids": ["evidence_method", "evidence_evaluation"],
            },
        ],
    }
    all_evidence = [item["id"] for item in evidence]
    for item in artifact["knowledge_map"]:
        item["evidence_ids"] = ["evidence_detail"]
    for item in artifact["reproduction_plan"]:
        item["evidence_ids"] = ["evidence_method", "evidence_evaluation"]
    for item in artifact["mastery_checks"]:
        item["evidence_ids"] = all_evidence[:2]
    return artifact, {"input_tokens": 0, "output_tokens": 0}


def _concepts_from_paper(paper: Dict[str, Any]) -> List[str]:
    text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9-]{3,}", text)
    stop = {"this", "that", "with", "from", "their", "using", "paper", "method", "model", "results", "based"}
    result = []
    for token in tokens:
        value = token.casefold()
        if value not in stop and value not in result:
            result.append(value)
    return result[:4] or ["problem formulation", "evaluation"]


def _knowledge_map(concepts: List[str], zh: bool) -> List[Dict[str, Any]]:
    tr = lambda a, b: a if zh else b
    core = "、".join(concepts[:3]) if zh else ", ".join(concepts[:3])
    return [
        {
            "id": "knowledge_problem",
            "priority": "must",
            "title": tr("任务定义与数据流", "Task definition and data flow"),
            "why_needed": tr("不先明确输入、输出和约束，就无法判断方法解决了什么。", "Without inputs, outputs, and constraints, the method's claim is impossible to judge."),
            "learn": [tr("写出一个具体输入输出例子", "Write one concrete input/output example"), tr("区分训练、推理和评测阶段", "Separate training, inference, and evaluation")],
            "stop_rule": tr("能够不看论文画出任务数据流即可。", "Stop when you can draw the task data flow without the paper."),
            "self_check": tr("给定一个样本，方法最终要预测或生成什么？", "For one sample, what must the method predict or generate?"),
        },
        {
            "id": "knowledge_core",
            "priority": "must",
            "title": tr(f"方向核心概念：{core}", f"Core concepts: {core}"),
            "why_needed": tr("这些词决定论文的新机制和基线差异。", "These concepts determine the new mechanism and its baseline difference."),
            "learn": [tr("用自己的话解释每个概念", "Explain each concept in your own words"), tr("指出概念在方法哪个模块出现", "Locate each concept in the method")],
            "stop_rule": tr("能用一个小例子解释核心机制，不需要先掌握所有变体。", "Stop once a tiny example explains the core mechanism; defer variants."),
            "self_check": tr("如果移除核心机制，系统会退化成哪个基线？", "Which baseline remains if the core mechanism is removed?"),
        },
        {
            "id": "knowledge_evaluation",
            "priority": "just_in_time",
            "title": tr("实验设计与统计判断", "Experimental design and statistical judgment"),
            "why_needed": tr("最好分数不能单独证明方法有效。", "A best score alone cannot establish effectiveness."),
            "learn": [tr("基线公平性、消融、方差和失败案例", "Baseline fairness, ablation, variance, and failures"), tr("指标与真实目标是否一致", "Whether metrics match the real objective")],
            "stop_rule": tr("能指出一个结果表不能证明的结论即可。", "Stop when you can name one claim a result table cannot prove."),
            "self_check": tr("提升小于随机波动时应该如何报告？", "How should a gain below random variation be reported?"),
        },
        {
            "id": "knowledge_defer",
            "priority": "defer",
            "title": tr("暂缓：全部相关变体与完整理论", "Defer: every variant and complete theory"),
            "why_needed": tr("它们会扩大阅读面，但不是理解论文主线的前置。", "They broaden context but are not prerequisites for the paper's main line."),
            "learn": [tr("只有遇到正文阻塞时再补具体变体", "Learn a variant only when the paper blocks on it")],
            "stop_rule": tr("当前不要展开。", "Do not expand this now."),
            "self_check": tr("这个知识是否直接阻塞方法或实验理解？", "Does this knowledge directly block method or experiment understanding?"),
        },
    ]


def _reproduction_plan(code_note: str, paper: Dict[str, Any], zh: bool) -> List[Dict[str, Any]]:
    tr = lambda a, b: a if zh else b
    return [
        {"level": "L0", "title": tr("确认可复现入口", "Verify reproduction entry"), "actions": [tr(f"核对官方页面和代码：{code_note}", f"Verify official source and code: {code_note}"), tr("记录数据、权重、许可证和环境版本", "Record data, weights, licenses, and environment versions")], "expected_output": tr("一份无失效链接的复现清单", "A reproduction checklist with no dead links"), "success_criteria": tr("每个依赖都有公开来源或明确缺失标记", "Every dependency has a public source or an explicit missing marker"), "estimated_hours": 1.5},
        {"level": "L1", "title": tr("跑通最小样例", "Run the smallest example"), "actions": [tr("缩小数据和模型，固定随机种子", "Shrink data and model; fix random seeds"), tr("保存命令、配置、日志和一个输出", "Save command, config, log, and one output")], "expected_output": tr("可重复执行的最小运行记录", "A repeatable minimum run"), "success_criteria": tr("清空输出后按记录能再次得到同类结果", "A clean rerun reproduces the same kind of output"), "estimated_hours": 4},
        {"level": "L2", "title": tr("复现一个关键结果", "Reproduce one key result"), "actions": [tr("选择一条主基线和一个主要指标", "Choose one main baseline and metric"), tr("至少运行三个种子并报告均值与方差", "Run at least three seeds and report mean and variance")], "expected_output": tr("原论文值、复现值和偏差解释表", "A table of paper value, reproduced value, and discrepancy"), "success_criteria": tr("差异处在预设容差内，或有可核查原因", "Difference is within tolerance or has an inspectable cause"), "estimated_hours": 12},
        {"level": "L3", "title": tr("改变一个变量", "Change one variable"), "actions": [tr("只替换一个模块、资源条件或数据切片", "Replace only one module, resource condition, or data slice"), tr("保留基线、协议和失败案例", "Keep baselines, protocol, and failure cases")], "expected_output": tr("一张受控对照表和失败类型分析", "One controlled comparison and failure taxonomy"), "success_criteria": tr("能够说明变化来自哪个变量，而不是环境漂移", "Attribute the change to the variable, not environment drift"), "estimated_hours": 16},
    ]


def _mastery_checks(zh: bool) -> List[Dict[str, Any]]:
    tr = lambda a, b: a if zh else b
    return [
        {"id": "check_problem", "question": tr("不用看论文，用三句话说明问题、方法和结果。", "Without the paper, state problem, method, and result in three sentences."), "expected_points": [tr("具体问题和目标", "Concrete problem and objective"), tr("核心机制而不是论文标题", "Core mechanism, not the title"), tr("结果及证据边界", "Result and evidence boundary")]},
        {"id": "check_flow", "question": tr("按输入—处理—输出画出方法，并指出真正新增的模块。", "Draw input–process–output and identify the genuinely new module."), "expected_points": [tr("输入与约束", "Inputs and constraints"), tr("核心变换", "Core transformation"), tr("输出与评测", "Output and evaluation")]},
        {"id": "check_evidence", "question": tr("主实验和消融实验分别能证明什么、不能证明什么？", "What can and cannot the main experiment and ablation establish?"), "expected_points": [tr("主实验比较整体效果", "Main experiment compares overall effect"), tr("消融隔离模块贡献", "Ablation isolates module contribution"), tr("都不能自动证明泛化或因果", "Neither automatically proves generalization or causality")]},
        {"id": "check_failure", "question": tr("指出一个最可能失败的场景，并设计最小验证。", "Name one likely failure case and design a minimum test."), "expected_points": [tr("可证伪的失败条件", "Falsifiable failure condition"), tr("只改变一个变量", "Change one variable"), tr("包含指标和失败记录", "Include metrics and failure records")]},
    ]
