"""Orchestrate evidence-grounded single-paper analysis jobs."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict

from src.cloud_ai.client import CloudAIClient, CloudAIConfig
from src.cloud_ai.job_runtime import run_with_heartbeat
from src.paper_analysis.document_service import PaperDocumentService
from src.paper_analysis.schemas import PaperAnalysisArtifact
from src.storage import LocalDatabase
from web.result_store import ResultStore


class PaperAnalysisService:
    """Build, validate, persist, and assess one progressive paper reading."""

    def __init__(
        self,
        database: LocalDatabase,
        result_store: ResultStore,
        document_service: PaperDocumentService,
        client: CloudAIClient,
        config: CloudAIConfig,
    ) -> None:
        self.database = database
        self.result_store = result_store
        self.document_service = document_service
        self.client = client
        self.config = config

    def create_job(self, payload: Dict[str, Any]) -> str:
        return self.database.create_job("paper_analysis", payload)

    def run_job(self, job_id: str, payload: Dict[str, Any]) -> None:
        try:
            self.database.update_job(
                job_id,
                status="running",
                stage="collecting_paper",
                progress_total=5,
            )
            paper = self.result_store.get_paper(payload["run_id"], payload["paper_id"])
            self.database.update_job(
                job_id,
                stage="preparing_document",
                progress_current=1,
                progress_total=5,
            )
            document = self.document_service.prepare(
                payload["run_id"],
                paper,
                prefer_full_text=bool(payload.get("prefer_full_text", True)),
                force_refresh=bool(payload.get("force_refresh", False)),
            )
            context = self._build_context(payload, paper, document)
            self.database.update_job(
                job_id,
                stage="analysing_paper",
                progress_current=2,
                progress_total=5,
            )
            raw_artifact, usage = run_with_heartbeat(
                self.database,
                job_id,
                "analysing_paper",
                lambda: self.client.analyze_paper(context),
                progress_current=2,
                progress_total=5,
            )
            self.database.update_job(
                job_id,
                stage="validating_evidence",
                progress_current=3,
                progress_total=5,
            )
            artifact = PaperAnalysisArtifact.model_validate(raw_artifact)
            self._validate_evidence(artifact, document)
            artifact_payload = artifact.model_dump(mode="json")
            analysis_id = self.database.save_paper_analysis(
                job_id=job_id,
                document_id=document["id"],
                run_id=payload["run_id"],
                paper_id=payload["paper_id"],
                language=payload["language"],
                experience_level=payload["experience_level"],
                reading_goal=payload["reading_goal"],
                math_depth=payload["math_depth"],
                compute_profile=payload["compute_profile"],
                provider=self.client.provider,
                model=self.client.model,
                prompt_version=self.config.prompt_version,
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
                progress_current=5,
                progress_total=5,
                result={
                    "analysis_id": analysis_id,
                    "document_status": document["status"],
                    "page_count": document["page_count"],
                    "artifact": artifact_payload,
                },
            )
        except Exception as error:
            self.database.update_job(
                job_id,
                status="failed",
                stage="failed",
                error={"type": type(error).__name__, "message": str(error)},
            )

    def evaluate_mastery(
        self, analysis_id: str, check_id: str, answer: str
    ) -> Dict[str, Any]:
        analysis = self.database.get_paper_analysis(analysis_id)
        artifact = PaperAnalysisArtifact.model_validate(analysis["artifact"])
        check = next(
            (item for item in artifact.mastery_checks if item.id == check_id), None
        )
        if check is None:
            raise KeyError(f"Unknown paper mastery check: {check_id}")
        normalized = answer.strip()
        if not normalized:
            raise ValueError("Mastery answer cannot be empty")
        answer_tokens = _mastery_tokens(normalized)
        direct_hits = sum(
            point.casefold() in normalized.casefold() for point in check.expected_points
        )
        matched_points = sum(
            bool(_mastery_tokens(point) & answer_tokens)
            for point in check.expected_points
        )
        passed = len(normalized) >= 40 and (direct_hits >= 1 or matched_points >= 2)
        zh = analysis["language"] == "zh-CN"
        if passed:
            feedback = (
                "回答已经包含可核查的关键点。下一步请对照证据页码，确认不是只复述 AI 总结。"
                if zh
                else "The answer contains inspectable key points. Now verify them against the cited pages instead of repeating the AI summary."
            )
        else:
            missing = "；".join(check.expected_points) if zh else "; ".join(check.expected_points)
            feedback = (
                f"回答还不够具体。请补充：{missing}"
                if zh
                else f"The answer is not specific enough. Add: {missing}"
            )
        self.database.save_paper_mastery_progress(
            analysis_id,
            check_id,
            status="passed" if passed else "needs_review",
            answer=normalized,
            feedback=feedback,
        )
        return self.database.get_paper_analysis(analysis_id)

    @staticmethod
    def _build_context(
        payload: Dict[str, Any], paper: Dict[str, Any], document: Dict[str, Any]
    ) -> Dict[str, Any]:
        chunks = [
            {
                "id": chunk["id"],
                "page": chunk["page"],
                "section": chunk["section"],
                "text": chunk["text"][:2400],
            }
            for chunk in _select_document_chunks(document["chunks"])
        ]
        return {
            "output_contract": PaperAnalysisArtifact.model_json_schema(),
            "paper": {
                key: paper.get(key)
                for key in (
                    "id",
                    "title",
                    "abstract",
                    "authors",
                    "conference",
                    "year",
                    "source_url",
                    "direction_id",
                    "direction_title",
                )
            },
            "document": {
                "status": document["status"],
                "page_count": document["page_count"],
                "pdf_url": document.get("pdf_url"),
                "chunks": chunks,
            },
            "request": {
                "language": payload["language"],
                "experience_level": payload["experience_level"],
                "reading_goal": payload["reading_goal"],
                "math_depth": payload["math_depth"],
                "compute_profile": payload["compute_profile"],
            },
        }

    @staticmethod
    def _validate_evidence(
        artifact: PaperAnalysisArtifact, document: Dict[str, Any]
    ) -> None:
        if artifact.paper_id != document["paper_id"]:
            raise ValueError("AI output changed the requested paper id")
        if artifact.document_status != document["status"]:
            raise ValueError("AI output changed the document evidence scope")
        chunks = {item["id"]: item for item in document["chunks"]}
        for evidence in artifact.evidence:
            chunk = chunks.get(evidence.chunk_id)
            if chunk is None:
                raise ValueError("AI output invented a paper chunk id")
            if evidence.page != int(chunk["page"]):
                raise ValueError("AI output changed an evidence page number")
            if evidence.section != chunk["section"]:
                raise ValueError("AI output changed an evidence section")
            if evidence.excerpt not in chunk["text"]:
                raise ValueError("AI evidence excerpt is not present in the source chunk")


def _select_document_chunks(
    chunks: list[Dict[str, Any]], limit: int = 80
) -> list[Dict[str, Any]]:
    """Cover the paper arc instead of truncating long PDFs at the introduction."""
    if len(chunks) <= limit:
        return chunks
    selected = set(range(min(12, len(chunks))))
    selected.update(range(max(0, len(chunks) - 12), len(chunks)))
    keyword_groups = (
        ("method", "approach", "framework", "algorithm", "architecture"),
        ("experiment", "evaluation", "dataset", "baseline", "metric"),
        ("result", "outperform", "ablation", "analysis", "finding"),
        ("limitation", "failure", "future work", "conclusion", "discussion"),
    )
    for terms in keyword_groups:
        matches = [
            index
            for index, chunk in enumerate(chunks)
            if any(term in chunk["text"].casefold() for term in terms)
        ]
        if matches:
            stride = max(1, len(matches) // 12)
            selected.update(matches[::stride][:12])
    remaining = max(0, limit - len(selected))
    if remaining:
        stride = max(1, len(chunks) // remaining)
        for index in range(0, len(chunks), stride):
            if len(selected) >= limit:
                break
            selected.add(index)
    return [chunks[index] for index in sorted(selected)]


def _mastery_tokens(value: str) -> set[str]:
    """Extract lightweight concept tokens for Chinese and English paraphrases."""

    normalized = value.casefold()
    tokens = set(re.findall(r"[a-z][\w-]{2,}", normalized))
    for sequence in re.findall(r"[\u4e00-\u9fff]+", normalized):
        tokens.update(sequence[index : index + 2] for index in range(len(sequence) - 1))
    return tokens
