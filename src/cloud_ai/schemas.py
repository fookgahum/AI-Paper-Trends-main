"""Strict output contract shared by mock and cloud learning-plan generators."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class KnowledgeNode(StrictModel):
    id: str = Field(min_length=1)
    category: str = Field(min_length=1)
    depth: str = Field(pattern=r"^(awareness|working|implementation|research)$")
    title: str = Field(min_length=1)
    why_required: str = Field(min_length=1)
    what_to_learn: List[str] = Field(min_length=1)
    not_required: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    mastery_checks: List[str] = Field(min_length=1)
    resource_queries: List[str] = Field(min_length=1)
    evidence_paper_ids: List[str] = Field(default_factory=list)
    estimated_hours: float = Field(gt=0)


class KnowledgeGap(StrictModel):
    area: str = Field(min_length=1)
    current_assumption: str = Field(min_length=1)
    target_level: str = Field(min_length=1)
    diagnostic_questions: List[str] = Field(min_length=1)
    bridge_node_ids: List[str] = Field(min_length=1)


class LearningResource(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    resource_type: str = Field(min_length=1)
    url: str = Field(pattern=r"^https://")
    language: str = Field(min_length=1)
    node_ids: List[str] = Field(min_length=1)
    recommended_sections: List[str] = Field(min_length=1)
    purpose: str = Field(min_length=1)
    stop_rule: str = Field(min_length=1)


class MasteryMilestone(StrictModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    node_ids: List[str] = Field(min_length=1)
    capability: str = Field(min_length=1)
    gate_checks: List[str] = Field(min_length=1)
    common_failures: List[str] = Field(min_length=1)
    estimated_hours: float = Field(gt=0)


class KnowledgeScope(StrictModel):
    starting_point: str = Field(min_length=1)
    target_capability: str = Field(min_length=1)
    must_learn_node_ids: List[str] = Field(min_length=1)
    optional_node_ids: List[str] = Field(default_factory=list)
    minimum_viable_node_ids: List[str] = Field(min_length=1)
    research_ready_node_ids: List[str] = Field(min_length=1)
    defer_topics: List[str] = Field(min_length=1)
    exit_criteria: List[str] = Field(min_length=1)
    minimum_viable_hours: float = Field(gt=0)
    estimated_total_hours: float = Field(gt=0)
    available_hours: float = Field(gt=0)
    feasibility: str = Field(pattern=r"^(unrealistic|tight|feasible)$")
    projection_note: str = Field(min_length=1)


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
    knowledge_scope: KnowledgeScope
    gap_diagnosis: List[KnowledgeGap] = Field(min_length=1)
    knowledge_tree: List[KnowledgeNode] = Field(min_length=6)
    mastery_milestones: List[MasteryMilestone] = Field(min_length=3)
    starter_resources: List[LearningResource] = Field(min_length=4)
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
        must_learn = set(self.knowledge_scope.must_learn_node_ids)
        optional = set(self.knowledge_scope.optional_node_ids)
        if must_learn - known or optional - known:
            raise ValueError("knowledge scope references an unknown node")
        if must_learn & optional:
            raise ValueError("a knowledge node cannot be both required and optional")
        minimum_viable = set(self.knowledge_scope.minimum_viable_node_ids)
        research_ready = set(self.knowledge_scope.research_ready_node_ids)
        if minimum_viable - must_learn:
            raise ValueError("minimum viable path must contain only required nodes")
        if research_ready != must_learn:
            raise ValueError("research-ready path must match the required knowledge boundary")
        if self.knowledge_scope.minimum_viable_hours > self.knowledge_scope.estimated_total_hours:
            raise ValueError("minimum viable path cannot take longer than the research-ready path")
        for node in self.knowledge_tree:
            if node.id in minimum_viable and set(node.prerequisites) - minimum_viable:
                raise ValueError("minimum viable path must include every node prerequisite")
        for gap in self.gap_diagnosis:
            if set(gap.bridge_node_ids) - known:
                raise ValueError("knowledge gap references an unknown bridge node")
        milestone_ids: set[str] = set()
        milestone_node_ids: list[str] = []
        for milestone in self.mastery_milestones:
            if milestone.id in milestone_ids:
                raise ValueError("mastery milestone ids must be unique")
            milestone_ids.add(milestone.id)
            if set(milestone.node_ids) - known:
                raise ValueError("mastery milestone references an unknown node")
            milestone_node_ids.extend(milestone.node_ids)
        if len(milestone_node_ids) != len(set(milestone_node_ids)):
            raise ValueError("a knowledge node cannot appear in multiple mastery milestones")
        if must_learn - set(milestone_node_ids):
            raise ValueError("mastery milestones must cover every required node")
        resource_ids: set[str] = set()
        resource_urls: set[str] = set()
        for resource in self.starter_resources:
            if resource.id in resource_ids:
                raise ValueError("starter resource ids must be unique")
            resource_ids.add(resource.id)
            if resource.url in resource_urls:
                raise ValueError("starter resource URLs must be unique")
            resource_urls.add(resource.url)
            if set(resource.node_ids) - known:
                raise ValueError("starter resource references an unknown node")

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
