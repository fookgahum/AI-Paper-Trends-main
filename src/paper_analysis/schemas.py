"""Strict contracts for evidence-grounded single-paper analysis."""

from __future__ import annotations

from typing import List, Literal

from pydantic import Field, model_validator

from src.cloud_ai.schemas import StrictModel


PAPER_ANALYSIS_ARTIFACT_VERSION = 1


class PaperEvidence(StrictModel):
    id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    page: int = Field(ge=0)
    section: str = Field(min_length=1)
    excerpt: str = Field(min_length=1, max_length=900)
    evidence_type: Literal["author_statement", "ai_synthesis", "needs_verification"]


class GroundedInsight(StrictModel):
    title: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class QuickBrief(StrictModel):
    one_sentence: str = Field(min_length=1)
    research_question: GroundedInsight
    motivation: GroundedInsight
    prior_gap: GroundedInsight
    approach: GroundedInsight
    main_result: GroundedInsight
    limitation: GroundedInsight


class ReadingStep(StrictModel):
    order: int = Field(ge=1)
    title: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    page_numbers: List[int]
    evidence_ids: List[str] = Field(min_length=1)


class LogicStep(StrictModel):
    stage: Literal[
        "problem", "prior_work", "gap", "hypothesis", "method", "evidence", "conclusion"
    ]
    content: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class MethodModule(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    purpose: str = Field(min_length=1)
    input: str = Field(min_length=1)
    process: str = Field(min_length=1)
    output: str = Field(min_length=1)
    why_it_matters: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class EquationInsight(StrictModel):
    label: str = Field(min_length=1)
    intuition: str = Field(min_length=1)
    symbols: List[str] = Field(min_length=1)
    tiny_example: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class ExperimentFinding(StrictModel):
    question: str = Field(min_length=1)
    finding: str = Field(min_length=1)
    strength: Literal["supported", "partial", "not_shown"]
    caution: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class KnowledgeItem(StrictModel):
    id: str = Field(min_length=1)
    priority: Literal["must", "just_in_time", "defer"]
    title: str = Field(min_length=1)
    why_needed: str = Field(min_length=1)
    learn: List[str] = Field(min_length=1)
    stop_rule: str = Field(min_length=1)
    self_check: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class ReproductionStep(StrictModel):
    level: Literal["L0", "L1", "L2", "L3"]
    title: str = Field(min_length=1)
    actions: List[str] = Field(min_length=1)
    expected_output: str = Field(min_length=1)
    success_criteria: str = Field(min_length=1)
    estimated_hours: float = Field(gt=0)
    evidence_ids: List[str] = Field(min_length=1)


class MasteryCheck(StrictModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    expected_points: List[str] = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class ResearchExtension(StrictModel):
    id: str = Field(min_length=1)
    idea: str = Field(min_length=1)
    difference: str = Field(min_length=1)
    minimum_experiment: str = Field(min_length=1)
    novelty_risk: str = Field(min_length=1)
    resource_need: str = Field(min_length=1)
    evidence_ids: List[str] = Field(min_length=1)


class PaperAnalysisArtifact(StrictModel):
    artifact_version: int = Field(default=PAPER_ANALYSIS_ARTIFACT_VERSION)
    paper_id: str = Field(min_length=1)
    paper_title: str = Field(min_length=1)
    document_status: Literal["full_text", "abstract_only"]
    scope_note: str = Field(min_length=1)
    warnings: List[str]
    evidence: List[PaperEvidence] = Field(min_length=1)
    quick_brief: QuickBrief
    reading_route: List[ReadingStep] = Field(min_length=1)
    logic_chain: List[LogicStep] = Field(min_length=5)
    method_modules: List[MethodModule] = Field(min_length=1)
    equations: List[EquationInsight]
    experiment_review: List[ExperimentFinding] = Field(min_length=1)
    knowledge_map: List[KnowledgeItem] = Field(min_length=3)
    reproduction_plan: List[ReproductionStep] = Field(min_length=4, max_length=4)
    mastery_checks: List[MasteryCheck] = Field(min_length=3)
    research_extensions: List[ResearchExtension] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_grounding(self) -> "PaperAnalysisArtifact":
        evidence_ids = [item.id for item in self.evidence]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("paper evidence ids must be unique")
        known = set(evidence_ids)
        referenced: list[str] = []
        brief = self.quick_brief
        for insight in (
            brief.research_question,
            brief.motivation,
            brief.prior_gap,
            brief.approach,
            brief.main_result,
            brief.limitation,
        ):
            referenced.extend(insight.evidence_ids)
        for collection in (
            self.reading_route,
            self.logic_chain,
            self.method_modules,
            self.equations,
            self.experiment_review,
            self.knowledge_map,
            self.reproduction_plan,
            self.mastery_checks,
            self.research_extensions,
        ):
            for item in collection:
                referenced.extend(item.evidence_ids)
        unknown = set(referenced) - known
        if unknown:
            raise ValueError(f"analysis references unknown evidence ids: {sorted(unknown)}")
        check_ids = [item.id for item in self.mastery_checks]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("mastery check ids must be unique")
        levels = [step.level for step in self.reproduction_plan]
        if levels != ["L0", "L1", "L2", "L3"]:
            raise ValueError("reproduction plan must be ordered from L0 through L3")
        if self.document_status == "abstract_only" and any(
            item.strength == "supported" for item in self.experiment_review
        ):
            raise ValueError("abstract-only analysis cannot claim fully supported experiments")
        return self
