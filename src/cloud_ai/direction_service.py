"""Analyse newly pulled papers without silently changing published directions."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from src.cloud_ai.client import CloudAIClient, CloudAIConfig
from src.cloud_ai.job_runtime import run_with_heartbeat
from src.cloud_ai.schemas import DirectionUpdateArtifact
from src.storage import LocalDatabase
from web.result_store import ResultStore


class DirectionUpdateService:
    """Map new papers to existing directions or save reviewable candidates."""

    def __init__(
        self,
        database: LocalDatabase,
        result_store: ResultStore,
        client: CloudAIClient,
        config: CloudAIConfig,
    ) -> None:
        self.database = database
        self.result_store = result_store
        self.client = client
        self.config = config

    def create_job(self, payload: Dict[str, Any]) -> str:
        return self.database.create_job("direction_update", payload)

    def run_job(self, job_id: str, payload: Dict[str, Any]) -> None:
        try:
            self.database.update_job(
                job_id, status="running", stage="collecting_unanalysed_papers", progress_total=4
            )
            papers = self.database.list_unanalysed_papers(int(payload["paper_limit"]))
            if not papers:
                self.database.update_job(
                    job_id,
                    status="completed",
                    stage="completed",
                    progress_current=4,
                    progress_total=4,
                    result={
                        "update_id": None,
                        "analysed": 0,
                        "assignments": [],
                        "candidates": [],
                        "message": "No unanalysed papers are waiting.",
                    },
                )
                return
            context = self._build_context(payload, papers)
            self.database.update_job(
                job_id, stage="analysing_directions", progress_current=1, progress_total=4
            )
            raw_artifact, usage = run_with_heartbeat(
                self.database,
                job_id,
                "analysing_directions",
                lambda: self.client.analyze_direction_updates(context),
            )
            self.database.update_job(
                job_id, stage="validating_direction_evidence", progress_current=2
            )
            artifact = DirectionUpdateArtifact.model_validate(raw_artifact)
            self._validate_artifact(artifact, context)
            artifact_payload = artifact.model_dump(mode="json")
            update_id = self.database.save_direction_update(
                job_id=job_id,
                run_id=payload["run_id"],
                provider=self.client.provider,
                model=self.client.model,
                prompt_version=self.config.prompt_version,
                artifact=artifact_payload,
            )
            self.database.mark_papers_analysed(
                assignment.paper_id for assignment in artifact.assignments
            )
            request_key = hashlib.sha256(
                json.dumps(context, ensure_ascii=False, sort_keys=True).encode("utf-8")
            ).hexdigest()
            self.database.record_usage(
                job_id,
                {
                    "provider": self.client.provider,
                    "model": self.client.model,
                    "request_key": request_key,
                    **usage,
                    "cached": False,
                },
            )
            self.database.update_job(
                job_id,
                status="completed",
                stage="completed",
                progress_current=4,
                progress_total=4,
                result={
                    "update_id": update_id,
                    "analysed": len(artifact.assignments),
                    "assignments": artifact_payload["assignments"],
                    "candidates": artifact_payload["candidates"],
                    "synthesis": artifact.synthesis,
                },
            )
        except Exception as error:
            self.database.update_job(
                job_id,
                status="failed",
                stage="failed",
                error={"type": type(error).__name__, "message": str(error)},
            )

    def _build_context(
        self, payload: Dict[str, Any], papers: list[Dict[str, Any]]
    ) -> Dict[str, Any]:
        snapshot = self.result_store.get_snapshot(payload["run_id"])
        directions = [
            {
                "id": direction["id"],
                "title": direction["title"],
                "summary": direction["summary"],
                "entry_points": direction.get("entry_points", {}),
            }
            for direction in snapshot.opportunities.get("directions", [])
        ]
        return {
            "output_contract": DirectionUpdateArtifact.model_json_schema(),
            "directions": directions,
            "papers": [
                {
                    "id": paper["id"],
                    "conference": paper["conference"],
                    "year": paper["year"],
                    "title": paper["title"],
                    "abstract": paper["abstract"],
                    "keywords": paper["keywords"],
                    "source_url": paper["source_url"],
                }
                for paper in papers
            ],
            "request": {
                "run_id": payload["run_id"],
                "language": payload["language"],
                "rule": "Return a draft only; never modify published directions.",
            },
        }

    @staticmethod
    def _validate_artifact(
        artifact: DirectionUpdateArtifact, context: Dict[str, Any]
    ) -> None:
        if artifact.run_id != context["request"]["run_id"]:
            raise ValueError("AI output changed the requested run id")
        paper_ids = {paper["id"] for paper in context["papers"]}
        assigned_ids = {assignment.paper_id for assignment in artifact.assignments}
        if assigned_ids != paper_ids:
            raise ValueError("AI output must assign every requested paper exactly once")
        direction_ids = {direction["id"] for direction in context["directions"]}
        if any(
            assignment.direction_id not in direction_ids
            for assignment in artifact.assignments
            if assignment.direction_id is not None
        ):
            raise ValueError("AI output invented an existing direction id")
        evidence_ids = {
            paper_id
            for candidate in artifact.candidates
            for paper_id in candidate.evidence_paper_ids
        }
        if evidence_ids - paper_ids:
            raise ValueError("AI output invented candidate evidence paper ids")
        unassigned = {
            assignment.paper_id
            for assignment in artifact.assignments
            if assignment.direction_id is None
        }
        if unassigned - evidence_ids:
            raise ValueError("Every unassigned paper must support a direction candidate")
