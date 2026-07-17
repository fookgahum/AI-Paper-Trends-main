"""End-to-end tests for URL ingestion and mock AI learning plans."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

import httpx

from src.cloud_ai.client import CloudAIConfig, OpenAICompatibleCloudAIClient
from src.cloud_ai.schemas import LearningPlanArtifact
from src.paper_sources import FetchedDocument
from src.paper_sources.service import parse_document
from tests.test_web import _write_snapshot
from web.app import create_app


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


if __name__ == "__main__":
    unittest.main()
