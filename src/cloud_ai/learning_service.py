"""Build validated learning artifacts from frontier-analysis evidence."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from src.cloud_ai.client import (
    CloudAIClient,
    CloudAIConfig,
    verified_resource_catalog,
)
from src.cloud_ai.job_runtime import run_with_heartbeat
from src.cloud_ai.schemas import LearningPlanArtifact
from src.storage import LocalDatabase
from web.result_store import ResultStore, ResultStoreError


class LearningPlanService:
    """Coordinate a learning-plan job without coupling web code to an AI vendor."""

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
        return self.database.create_job("learning_plan", payload)

    def run_job(self, job_id: str, payload: Dict[str, Any]) -> None:
        try:
            self.database.update_job(
                job_id, status="running", stage="collecting_evidence", progress_total=4
            )
            context = self._build_context(payload)
            self.database.update_job(
                job_id, stage="generating", progress_current=1, progress_total=4
            )
            raw_artifact, usage = run_with_heartbeat(
                self.database,
                job_id,
                "generating",
                lambda: self.client.generate_learning_plan(context),
            )
            self.database.update_job(
                job_id, stage="validating", progress_current=2, progress_total=4
            )
            artifact = LearningPlanArtifact.model_validate(raw_artifact)
            self._validate_evidence(artifact, context)
            artifact_payload = artifact.model_dump(mode="json")
            plan_id = self.database.save_learning_plan(
                job_id=job_id,
                direction_id=artifact.direction_id,
                direction_version=context["direction_version"],
                duration_days=artifact.duration_days,
                language=payload["language"],
                provider=self.client.provider,
                model=self.client.model,
                prompt_version=self.config.prompt_version,
                paper_cutoff=context["paper_cutoff"],
                artifact=artifact_payload,
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
                result={"plan_id": plan_id, "artifact": artifact_payload},
            )
        except Exception as error:
            self.database.update_job(
                job_id,
                status="failed",
                stage="failed",
                error={"type": type(error).__name__, "message": str(error)},
            )

    def _build_context(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = self.result_store.get_snapshot(payload["run_id"])
        direction = next(
            (
                item
                for item in snapshot.opportunities.get("directions", [])
                if item["id"] == payload["direction_id"]
            ),
            None,
        )
        if direction is None:
            raise ResultStoreError(f"Unknown frontier direction: {payload['direction_id']}")
        paper_by_id = {paper["id"]: paper for paper in snapshot.papers}
        representatives = [
            {**paper_by_id[paper["id"]], **paper}
            for paper in direction["representative_papers"]
            if paper["id"] in paper_by_id
        ]
        if not representatives:
            raise ValueError("Direction has no representative papers in this snapshot")
        grounded_direction = {**direction, "representative_papers": representatives}
        generated_at = snapshot.manifest.get("generated_at")
        return {
            "output_contract": LearningPlanArtifact.model_json_schema(),
            "verified_resource_catalog": verified_resource_catalog(
                direction["id"], payload["language"]
            ),
            "direction": grounded_direction,
            "direction_version": f"{payload['run_id']}:{generated_at or 'unknown'}",
            "paper_cutoff": generated_at or datetime.now(timezone.utc).isoformat(),
            "request": {
                "duration_days": int(payload["duration_days"]),
                "language": payload["language"],
                "experience_level": payload.get("experience_level", "intermediate"),
                "weekly_hours": int(payload.get("weekly_hours", 10)),
                "compute_profile": payload.get("compute_profile", "single_gpu_or_cpu"),
            },
        }

    @staticmethod
    def _validate_evidence(
        artifact: LearningPlanArtifact, context: Dict[str, Any]
    ) -> None:
        if artifact.direction_id != context["direction"]["id"]:
            raise ValueError("AI output changed the requested direction id")
        allowed = {
            paper["id"] for paper in context["direction"]["representative_papers"]
        }
        generated = {paper.paper_id for paper in artifact.anchor_papers}
        if generated - allowed:
            raise ValueError("AI output invented an anchor paper id")
        knowledge_evidence = {
            paper_id
            for node in artifact.knowledge_tree
            for paper_id in node.evidence_paper_ids
        }
        if knowledge_evidence - allowed:
            raise ValueError("AI output invented knowledge-node evidence paper ids")
        allowed_resource_urls = {
            resource["url"] for resource in context["verified_resource_catalog"]
        }
        generated_resource_urls = {
            resource.url for resource in artifact.starter_resources
        }
        if generated_resource_urls - allowed_resource_urls:
            raise ValueError("AI output invented an unverified starter-resource URL")
