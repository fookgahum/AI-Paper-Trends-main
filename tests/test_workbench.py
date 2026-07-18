"""End-to-end tests for URL ingestion and mock AI learning plans."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import httpx

from src.cloud_ai.client import (
    CloudAIConfig,
    MockCloudAIClient,
    OpenAICompatibleCloudAIClient,
)
from src.cloud_ai.learning_service import LearningPlanService
from src.cloud_ai.schemas import LearningPlanArtifact
from src.paper_analysis.document_service import chunk_pages, resolve_pdf_url
from src.paper_analysis.schemas import PaperAnalysisArtifact
from src.paper_analysis.service import _select_document_chunks
from src.paper_sources import FetchedDocument
from src.paper_sources.service import parse_document
from tests.test_web import _write_snapshot
from web.app import create_app
from web.result_store import ResultStore


def _fake_fetch(url: str) -> FetchedDocument:
    payload = {
        "papers": [
            {
                "id": "demo-001",
                "title": "A Small Reproducible Frontier Study",
                "abstract": "We evaluate a compact and reproducible research method.",
                "authors": ["A. Researcher"],
                "keywords": ["evaluation", "reproducibility"],
                "url": "https://papers.example.test/demo-001",
                "pdf_url": "https://papers.example.test/demo-001.pdf",
            },
            {"id": "missing-abstract", "title": "Rejected incomplete paper"},
        ]
    }
    return FetchedDocument(
        url=url,
        content=json.dumps(payload).encode("utf-8"),
        content_type="application/json",
    )


def _minimal_pdf() -> bytes:
    objects = [
        "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>\nendobj\n",
        "4 0 obj\n<< /Length 178 >>\nstream\nBT /F1 11 Tf 72 720 Td (1 Introduction) Tj 0 -20 Td (We propose a graph method for reliable evaluation.) Tj 0 -20 Td (Experiments show improvements over a strong baseline.) Tj ET\nendstream\nendobj\n",
        "5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    content = b"%PDF-1.4\n"
    offsets = []
    for item in objects:
        offsets.append(len(content))
        content += item.encode("ascii")
    xref = len(content)
    content += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        content += f"{offset:010d} 00000 n \n".encode()
    return content + (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n"
    ).encode()


def _fake_pdf_fetch(url: str) -> FetchedDocument:
    return FetchedDocument(url=url, content=_minimal_pdf(), content_type="application/pdf")


class WorkbenchApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        _write_snapshot(self.root)
        app = create_app(
            self.root,
            local_root=self.root / "local",
            paper_fetch=_fake_fetch,
        )
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        )

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        self.temp.cleanup()

    async def test_pull_is_observable_and_deduplicates(self) -> None:
        request = {
            "url": "https://proceedings.example.test/papers.json",
            "conference": "DEMO",
            "year": 2026,
            "parser": "json",
            "download_pdf": False,
            "remember_source": True,
        }
        first = await self.client.post("/api/paper-pulls", json=request)
        self.assertEqual(first.status_code, 202)
        first_job = await self.client.get(f"/api/jobs/{first.json()['job_id']}")
        self.assertEqual(first_job.json()["status"], "completed")
        self.assertEqual(first_job.json()["result"]["new"], 1)
        self.assertEqual(first_job.json()["result"]["rejected"], 1)

        again = await self.client.post(
            f"/api/paper-sources/{first.json()['source_id']}/pull"
        )
        again_job = await self.client.get(f"/api/jobs/{again.json()['job_id']}")
        self.assertEqual(again_job.json()["result"]["duplicate"], 1)
        local = await self.client.get("/api/local/papers?limit=10")
        self.assertEqual(local.json()["count"], 3)  # two seeded + one pulled

    async def test_mock_learning_plan_and_progress(self) -> None:
        created = await self.client.post(
            "/api/learning/plans",
            json={
                "run_id": "demo",
                "direction_id": "graph_systems",
                "duration_days": 30,
                "language": "zh-CN",
                "experience_level": "intermediate",
                "weekly_hours": 10,
                "compute_profile": "cpu_only",
            },
        )
        self.assertEqual(created.status_code, 202)
        job = await self.client.get(f"/api/jobs/{created.json()['job_id']}")
        self.assertEqual(job.json()["status"], "completed", job.json())
        plan_id = job.json()["result"]["plan_id"]
        plan = await self.client.get(f"/api/learning/plans/{plan_id}")
        artifact = LearningPlanArtifact.model_validate(plan.json()["artifact"])
        self.assertEqual(artifact.duration_days, 30)
        self.assertEqual(artifact.anchor_papers[0].paper_id, "paper-a")
        self.assertEqual(
            [item.level for item in artifact.reproduction_ladder],
            ["L0", "L1", "L2", "L3", "L4"],
        )
        self.assertGreaterEqual(len(artifact.knowledge_tree), 10)
        self.assertTrue(artifact.knowledge_scope.must_learn_node_ids)
        self.assertTrue(artifact.knowledge_scope.defer_topics)
        self.assertTrue(artifact.gap_diagnosis)

        task_id = artifact.stages[0].tasks[0].id
        progress = await self.client.patch(
            f"/api/learning/plans/{plan_id}/tasks/{task_id}",
            json={"status": "done", "notes": "verified", "actual_hours": 2.5},
        )
        self.assertEqual(progress.status_code, 200)
        self.assertEqual(progress.json()["progress"][0]["status"], "done")

    async def test_direction_update_creates_draft_without_mutating_snapshot(self) -> None:
        pulled = await self.client.post(
            "/api/paper-pulls",
            json={
                "url": "https://proceedings.example.test/papers.json",
                "conference": "DEMO",
                "year": 2026,
                "parser": "json",
                "download_pdf": False,
                "remember_source": True,
            },
        )
        pull_job = await self.client.get(f"/api/jobs/{pulled.json()['job_id']}")
        self.assertEqual(pull_job.json()["status"], "completed")

        created = await self.client.post(
            "/api/direction-updates",
            json={"run_id": "demo", "paper_limit": 20, "language": "zh-CN"},
        )
        update_job = await self.client.get(f"/api/jobs/{created.json()['job_id']}")
        self.assertEqual(update_job.json()["status"], "completed", update_job.json())
        self.assertEqual(update_job.json()["result"]["analysed"], 1)
        self.assertTrue(update_job.json()["result"]["candidates"])

        drafts = await self.client.get("/api/direction-updates")
        self.assertEqual(len(drafts.json()["items"]), 1)
        self.assertEqual(drafts.json()["items"][0]["status"], "draft")
        dashboard = await self.client.get("/api/runs/demo/dashboard")
        self.assertEqual(len(dashboard.json()["opportunities"]["directions"]), 2)

    async def test_cloud_status_reports_free_mock_mode(self) -> None:
        response = await self.client.get("/api/cloud/status")
        self.assertEqual(response.json()["provider"], "mock")
        self.assertTrue(response.json()["configured"])
        self.assertEqual(response.json()["learning_artifact_version"], 3)
        self.assertEqual(response.json()["paper_analysis_artifact_version"], 1)

    async def test_mock_paper_analysis_is_grounded_and_assesses_mastery(self) -> None:
        created = await self.client.post(
            "/api/paper-analyses",
            json={
                "run_id": "demo",
                "paper_id": "paper-a",
                "language": "zh-CN",
                "experience_level": "zero",
                "reading_goal": "deep",
                "math_depth": "intuition",
                "compute_profile": "cpu_only",
                "prefer_full_text": False,
            },
        )
        self.assertEqual(created.status_code, 202)
        job = await self.client.get(f"/api/jobs/{created.json()['job_id']}")
        self.assertEqual(job.json()["status"], "completed", job.json())
        analysis_id = job.json()["result"]["analysis_id"]
        response = await self.client.get(f"/api/paper-analyses/{analysis_id}")
        artifact = PaperAnalysisArtifact.model_validate(response.json()["artifact"])
        self.assertEqual(artifact.paper_id, "paper-a")
        self.assertEqual(artifact.document_status, "abstract_only")
        self.assertTrue(artifact.warnings)
        self.assertTrue(
            all(item.strength != "supported" for item in artifact.experiment_review)
        )
        source_chunks = {item.chunk_id for item in artifact.evidence}
        self.assertEqual(source_chunks, {"abstract-1"})

        check_id = artifact.mastery_checks[0].id
        incomplete = await self.client.post(
            f"/api/paper-analyses/{analysis_id}/checks/{check_id}",
            json={"answer": "这篇论文看起来不错，但我还没有说清楚。"},
        )
        self.assertEqual(incomplete.status_code, 200, incomplete.text)
        self.assertEqual(incomplete.json()["progress"][0]["status"], "needs_review")

        assessed = await self.client.post(
            f"/api/paper-analyses/{analysis_id}/checks/{check_id}",
            json={
                "answer": "具体问题是语言模型治理；方法是按语言自由度调整水印强度；结果是在多种语言上报告更强的检测鲁棒性，但仍需回到原文核查实验边界。"
            },
        )
        self.assertEqual(assessed.status_code, 200, assessed.text)
        self.assertEqual(assessed.json()["progress"][0]["status"], "passed")

        history = await self.client.get(
            "/api/papers/paper-a/analyses", params={"run_id": "demo"}
        )
        self.assertEqual(history.json()["items"][0]["id"], analysis_id)

    async def test_full_text_paper_analysis_serves_grounded_pdf(self) -> None:
        app = create_app(
            self.root,
            local_root=self.root / "pdf-local",
            paper_document_fetch=_fake_pdf_fetch,
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            created = await client.post(
                "/api/paper-analyses",
                json={
                    "run_id": "demo",
                    "paper_id": "paper-a",
                    "language": "en-US",
                    "experience_level": "beginner",
                    "reading_goal": "reproduce",
                    "math_depth": "formula",
                    "compute_profile": "cpu_only",
                    "prefer_full_text": True,
                },
            )
            job = await client.get(f"/api/jobs/{created.json()['job_id']}")
            self.assertEqual(job.json()["status"], "completed", job.json())
            self.assertEqual(job.json()["result"]["document_status"], "full_text")
            self.assertEqual(job.json()["result"]["page_count"], 1)
            analysis_id = job.json()["result"]["analysis_id"]
            analysis = await client.get(f"/api/paper-analyses/{analysis_id}")
            artifact = PaperAnalysisArtifact.model_validate(
                analysis.json()["artifact"]
            )
            self.assertTrue(all(item.page == 1 for item in artifact.evidence))
            pdf = await client.get(f"/api/paper-analyses/{analysis_id}/pdf")
            self.assertEqual(pdf.status_code, 200)
            self.assertTrue(pdf.content.startswith(b"%PDF"))


class PaperDocumentTests(unittest.TestCase):
    def test_resolves_supported_official_pdf_urls(self) -> None:
        self.assertEqual(
            resolve_pdf_url(
                {"source_url": "https://aclanthology.org/2026.acl-long.12/"}
            ),
            "https://aclanthology.org/2026.acl-long.12.pdf",
        )
        self.assertEqual(
            resolve_pdf_url(
                {"source_url": "https://openreview.net/forum?id=paper123"}
            ),
            "https://openreview.net/pdf?id=paper123",
        )

    def test_chunks_keep_page_and_section_grounding(self) -> None:
        chunks = chunk_pages(
            [
                "1 Introduction\nThis paper studies a problem. We propose a method.",
                "2 Experiments\nResults improve the baseline. Limitations remain.",
            ],
            target_chars=40,
        )
        self.assertEqual(chunks[0]["page"], 1)
        self.assertTrue(all(item["id"].startswith("p") for item in chunks))
        self.assertTrue(any(item["page"] == 2 for item in chunks))

    def test_long_paper_selection_covers_results_and_conclusion(self) -> None:
        chunks = [
            {"id": f"c{index}", "page": index + 1, "section": "Body", "text": "body"}
            for index in range(160)
        ]
        chunks[120]["text"] = "Experiments and ablation results"
        chunks[150]["text"] = "Limitations and conclusion"
        selected = _select_document_chunks(chunks, limit=40)
        ids = {item["id"] for item in selected}
        self.assertIn("c0", ids)
        self.assertIn("c120", ids)
        self.assertIn("c150", ids)
        self.assertIn("c159", ids)


class CloudBoundaryTests(unittest.TestCase):
    def test_real_client_fails_before_network_without_key(self) -> None:
        config = CloudAIConfig(
            provider="openai_compatible",
            model="test-model",
            base_url="https://api.example.test/v1",
            api_key_env="AI_PAPER_TEST_MISSING_KEY",
            timeout_seconds=1,
            temperature=0,
            prompt_version="test",
        )
        os.environ.pop(config.api_key_env, None)
        with self.assertRaisesRegex(RuntimeError, config.api_key_env):
            OpenAICompatibleCloudAIClient(config).generate_learning_plan({})


class PaperParserTests(unittest.TestCase):
    def test_openreview_notes_payload_uses_nested_content(self) -> None:
        payload = {
            "notes": [
                {
                    "id": "forum-1",
                    "content": {
                        "title": {"value": "Nested OpenReview paper"},
                        "abstract": {"value": "A public abstract."},
                        "authors": {"value": ["Ada"]},
                    },
                }
            ]
        }
        papers = parse_document(
            FetchedDocument(
                "https://api2.openreview.net/notes",
                json.dumps(payload).encode("utf-8"),
                "application/json",
            )
        )
        self.assertEqual(papers[0]["title"], "Nested OpenReview paper")
        self.assertEqual(
            papers[0]["source_url"], "https://openreview.net/forum?id=forum-1"
        )

    def test_acl_event_page_resolves_separate_abstract_panel(self) -> None:
        html = """
        <div class="d-sm-flex"><p><a href="/2026.acl-long.12/">Grounded Paper</a>
        <a href="/people/a/">A. Author</a></p></div>
        <div id="abstract-2026--acl-long--12"><div class="card-body">Full abstract.</div></div>
        """
        papers = parse_document(
            FetchedDocument(
                "https://aclanthology.org/events/acl-2026/",
                html.encode("utf-8"),
                "text/html",
            ),
            "acl",
        )
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["abstract"], "Full abstract.")
        self.assertEqual(papers[0]["authors"], ["A. Author"])


class LearningCurriculumTests(unittest.TestCase):
    def test_zero_foundation_curriculum_covers_all_published_directions(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        snapshot = ResultStore(project_root / "data" / "web").get_snapshot(
            "ccfa_2026"
        )
        paper_by_id = {paper["id"]: paper for paper in snapshot.papers}
        client = MockCloudAIClient()
        for direction in snapshot.opportunities["directions"]:
            grounded = {
                **direction,
                "representative_papers": [
                    {**paper_by_id[paper["id"]], **paper}
                    for paper in direction["representative_papers"]
                ],
            }
            raw, _usage = client.generate_learning_plan(
                {
                    "direction": grounded,
                    "request": {
                        "language": "zh-CN",
                        "duration_days": 30,
                        "experience_level": "zero",
                    },
                }
            )
            artifact = LearningPlanArtifact.model_validate(raw)
            self.assertIn("零基础", artifact.knowledge_scope.starting_point)
            self.assertGreaterEqual(len(artifact.knowledge_tree), 12)
            self.assertGreaterEqual(len(artifact.gap_diagnosis), 4)
            self.assertEqual(len(artifact.mastery_milestones), 5)
            self.assertGreaterEqual(len(artifact.starter_resources), 4)
            self.assertLess(
                artifact.knowledge_scope.minimum_viable_hours,
                artifact.knowledge_scope.estimated_total_hours,
            )
            self.assertLess(
                artifact.knowledge_scope.available_hours,
                artifact.knowledge_scope.minimum_viable_hours,
            )
            self.assertEqual(artifact.knowledge_scope.feasibility, "unrealistic")
            categories = {node.category for node in artifact.knowledge_tree}
            self.assertEqual(
                categories, {"基础前置", "方向核心", "论文与研究实践"}
            )
            for node in artifact.knowledge_tree:
                self.assertTrue(node.what_to_learn)
                self.assertTrue(node.mastery_checks)
                self.assertTrue(node.resource_queries)
            milestone_nodes = [
                node_id
                for milestone in artifact.mastery_milestones
                for node_id in milestone.node_ids
            ]
            self.assertEqual(
                set(milestone_nodes),
                set(artifact.knowledge_scope.must_learn_node_ids),
            )
            self.assertEqual(len(milestone_nodes), len(set(milestone_nodes)))
            self.assertTrue(
                all(len(milestone.node_ids) <= 4 for milestone in artifact.mastery_milestones)
            )
            for resource in artifact.starter_resources:
                self.assertTrue(resource.url.startswith("https://"))
                self.assertTrue(resource.recommended_sections)
                self.assertTrue(resource.stop_rule)

    def test_learning_evidence_rejects_unverified_resource_url(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        snapshot = ResultStore(project_root / "data" / "web").get_snapshot(
            "ccfa_2026"
        )
        direction = snapshot.opportunities["directions"][0]
        paper_by_id = {paper["id"]: paper for paper in snapshot.papers}
        grounded = {
            **direction,
            "representative_papers": [
                {**paper_by_id[paper["id"]], **paper}
                for paper in direction["representative_papers"]
            ],
        }
        raw, _usage = MockCloudAIClient().generate_learning_plan(
            {
                "direction": grounded,
                "request": {
                    "language": "zh-CN",
                    "duration_days": 30,
                    "experience_level": "zero",
                },
            }
        )
        artifact = LearningPlanArtifact.model_validate(raw)
        context = {
            "direction": grounded,
            "verified_resource_catalog": [
                {"url": resource.url} for resource in artifact.starter_resources
            ],
        }
        LearningPlanService._validate_evidence(artifact, context)
        invalid_payload = artifact.model_dump(mode="json")
        invalid_payload["starter_resources"][0]["url"] = (
            "https://unverified.example.test/course"
        )
        invalid_artifact = LearningPlanArtifact.model_validate(invalid_payload)
        with self.assertRaisesRegex(ValueError, "unverified starter-resource"):
            LearningPlanService._validate_evidence(invalid_artifact, context)


if __name__ == "__main__":
    unittest.main()
