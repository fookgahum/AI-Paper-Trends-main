"""Strict output contract shared by mock and cloud learning-plan generators."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KnowledgeNode(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    prerequisites: List[str] = Field(default_factory=list)
    deliverable: str = Field(min_length=1)
    estimated_hours: float = Field(gt=0)


class LearningTask(StrictModel):
    id: str = Field(min_length=1)
    day_start: int = Field(ge=1)
    day_end: int = Field(ge=1)
    title: str = Field(min_length=1)
    objectives: List[str] = Field(min_length=1)
    actions: List[str] = Field(min_length=1)
    deliverable: str = Field(min_length=1)
    acceptance: str = Field(min_length=1)
    anchor_paper_ids: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_day_range(self) -> "LearningTask":
        if self.day_end < self.day_start:
            raise ValueError("task day_end must not precede day_start")
        return self


class PlanStage(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    day_start: int = Field(ge=1)
    day_end: int = Field(ge=1)
    goal: str = Field(min_length=1)
    tasks: List[LearningTask] = Field(min_length=1)


class AnchorPaper(StrictModel):
    paper_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    reading_order: int = Field(ge=1)
    reproduction_level: str = Field(pattern=r"^L[0-4]$")


class ReproductionLevel(StrictModel):
    level: str = Field(pattern=r"^L[0-4]$")
    title: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    acceptance: str = Field(min_length=1)


class ResearchHypothesis(StrictModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    novelty: str = Field(min_length=1)
    minimum_experiment: str = Field(min_length=1)
    risks: List[str] = Field(min_length=1)


class DirectionAssignment(StrictModel):
    paper_id: str = Field(min_length=1)
    direction_id: str | None = None
    confidence: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=1)


class DirectionCandidate(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    evidence_paper_ids: List[str] = Field(min_length=1)
    difference_from_existing: str = Field(min_length=1)
    recommended_action: str = Field(min_length=1)


class DirectionUpdateArtifact(StrictModel):
    run_id: str = Field(min_length=1)
    assignments: List[DirectionAssignment]
    candidates: List[DirectionCandidate]
    synthesis: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_update(self) -> "DirectionUpdateArtifact":
        paper_ids = [assignment.paper_id for assignment in self.assignments]
        if len(paper_ids) != len(set(paper_ids)):
            raise ValueError("direction assignments must contain unique paper ids")
        candidate_ids = [candidate.id for candidate in self.candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("direction candidate ids must be unique")
        return self


class LearningPlanArtifact(StrictModel):
    direction_id: str = Field(min_length=1)
    direction_title: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    duration_days: int = Field(gt=0)
    knowledge_tree: List[KnowledgeNode] = Field(min_length=1)
    stages: List[PlanStage] = Field(min_length=1)
    anchor_papers: List[AnchorPaper] = Field(min_length=1)
    reproduction_ladder: List[ReproductionLevel] = Field(min_length=5, max_length=5)
    research_hypotheses: List[ResearchHypothesis] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_plan(self) -> "LearningPlanArtifact":
        node_ids = [node.id for node in self.knowledge_tree]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("knowledge node ids must be unique")
        known = set(node_ids)
        for node in self.knowledge_tree:
            unknown = set(node.prerequisites) - known
            if unknown:
                raise ValueError(f"unknown knowledge prerequisites: {sorted(unknown)}")
        self._validate_acyclic({node.id: node.prerequisites for node in self.knowledge_tree})

        ordered_stages = sorted(self.stages, key=lambda stage: stage.day_start)
        expected_start = 1
        task_ids: set[str] = set()
        anchor_ids = {paper.paper_id for paper in self.anchor_papers}
        for stage in ordered_stages:
            if stage.day_start != expected_start or stage.day_end < stage.day_start:
                raise ValueError("plan stages must cover a contiguous day range")
            expected_start = stage.day_end + 1
            for task in stage.tasks:
                if task.id in task_ids:
                    raise ValueError("learning task ids must be unique")
                task_ids.add(task.id)
                if task.day_start < stage.day_start or task.day_end > stage.day_end:
                    raise ValueError("learning task must stay inside its stage")
                if set(task.anchor_paper_ids) - anchor_ids:
                    raise ValueError("learning task references an unknown anchor paper")
        if expected_start - 1 != self.duration_days:
            raise ValueError("plan stages must cover the requested duration")

        levels = [level.level for level in self.reproduction_ladder]
        if levels != ["L0", "L1", "L2", "L3", "L4"]:
            raise ValueError("reproduction ladder must be ordered from L0 through L4")
        return self

    @staticmethod
    def _validate_acyclic(graph: dict[str, List[str]]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ValueError("knowledge tree must be acyclic")
            if node in visited:
                return
            visiting.add(node)
            for parent in graph[node]:
                visit(parent)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)
