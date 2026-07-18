"""Tests for the read-only dashboard store and HTTP API."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import httpx

from web.app import create_app
from web.result_store import ResultStore, ResultStoreError


def _write_snapshot(root: Path) -> None:
    run_dir = root / "demo"
    run_dir.mkdir(parents=True)
    manifest = {
        "run_id": "demo",
        "title": "Demo run",
        "year": 2026,
        "generated_at": "2026-07-17T00:00:00+00:00",
        "sample_seed": 2026,
        "sample_size_per_conference": 1,
        "frontier_analysis": {
            "file": "opportunities.json",
            "direction_count": 2,
            "default_profile": "individual",
            "score_is_acceptance_probability": False,
        },
        "sources": [
            {
                "conference": "ICLR",
                "label": "Official source",
                "url": "https://example.test/iclr",
                "paper_count": 1,
            },
            {
                "conference": "ACL",
                "label": "Official source",
                "url": "https://example.test/acl",
                "paper_count": 1,
            },
        ],
    }
    papers = [
        {
            "id": "paper-a",
            "conference": "ICLR",
            "year": 2026,
            "title": "Alpha model",
            "abstract": "Graph representation learning.",
            "authors": ["Ada"],
            "keywords": ["graph"],
            "decision": "Poster",
            "topic_id": 0,
            "topic_name": "Graph learning",
            "direction_id": "graph_systems",
            "direction_title": {
                "zh-CN": "图系统",
                "en-US": "Graph systems",
            },
            "source_url": "https://example.test/a",
            "pdf_url": "https://example.test/a.pdf",
        },
        {
            "id": "paper-b",
            "conference": "ACL",
            "year": 2026,
            "title": "Beta language",
            "abstract": "Language model evaluation.",
            "authors": ["Bo"],
            "keywords": ["evaluation"],
            "decision": "Published (Long Paper)",
            "topic_id": 1,
            "topic_name": "Language evaluation",
            "direction_id": "language_evaluation",
            "direction_title": {
                "zh-CN": "语言模型评测",
                "en-US": "Language-model evaluation",
            },
            "source_url": "https://example.test/b",
        },
    ]
    opportunities = {
        "profiles": [
            {
                "id": "individual",
                "title": {"zh-CN": "个人", "en-US": "Individual"},
                "capabilities": {
                    "compute": 2,
                    "data": 2,
                    "engineering": 2,
                    "theory": 2,
                },
            }
        ],
        "directions": [
            {
                "id": "graph_systems",
                "title": {"zh-CN": "图系统", "en-US": "Graph systems"},
                "summary": {"zh-CN": "图系统总结", "en-US": "Graph summary"},
                "topic_ids": [0],
                "paper_count": 1,
                "barriers": {"compute": 2, "data": 2, "engineering": 2, "theory": 2},
                "scores": {"individual": {"score": 75}},
                "representative_papers": [{"id": "paper-a"}],
            },
            {
                "id": "language_evaluation",
                "title": {"zh-CN": "语言模型评测", "en-US": "Language-model evaluation"},
                "summary": {"zh-CN": "语言评测总结", "en-US": "Language evaluation summary"},
                "topic_ids": [1],
                "paper_count": 1,
                "barriers": {"compute": 2, "data": 2, "engineering": 2, "theory": 2},
                "scores": {"individual": {"score": 80}},
                "representative_papers": [{"id": "paper-b"}],
            },
        ],
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (run_dir / "papers.json").write_text(json.dumps(papers), encoding="utf-8")
    (run_dir / "opportunities.json").write_text(
        json.dumps(opportunities), encoding="utf-8"
    )


class ResultStoreTests(unittest.TestCase):
    def test_dashboard_reconciles_counts_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_snapshot(root)
            dashboard = ResultStore(root).dashboard("demo")

        self.assertEqual(dashboard["overview"]["paper_count"], 2)
        self.assertEqual(set(dashboard["overview"]), {"paper_count"})
        self.assertEqual(
            dashboard["filters"]["conferences"], ["ACL", "ICLR"]
        )

    def test_query_searches_and_paginates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_snapshot(root)
            store = ResultStore(root)
            result = store.query_papers("demo", query="graph", page_size=1)
            filtered = store.query_papers("demo", conference="ACL")
            direction = store.query_papers(
                "demo", direction="language_evaluation"
            )

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["id"], "paper-a")
        self.assertEqual(filtered["total"], 1)
        self.assertEqual(filtered["items"][0]["conference"], "ACL")
        self.assertEqual(direction["total"], 1)
        self.assertEqual(direction["items"][0]["id"], "paper-b")

    def test_rejects_unsafe_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ResultStoreError):
                ResultStore(Path(directory)).get_snapshot("../outside")


class WebApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_home_health_and_data_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_snapshot(root)
            transport = httpx.ASGITransport(
                app=create_app(root, local_root=root / "local")
            )
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                home = await client.get("/")
                health = await client.get("/api/health")
                runs = await client.get("/api/runs")
                dashboard = await client.get("/api/runs/demo/dashboard")
                papers = await client.get(
                    "/api/runs/demo/papers?direction=language_evaluation"
                )

        self.assertEqual(home.status_code, 200)
        self.assertIn("AI Paper Trends", home.text)
        self.assertEqual(health.json()["status"], "ok")
        self.assertEqual(health.json()["run_count"], 1)
        self.assertEqual(health.json()["cloud_provider"], "mock")
        self.assertEqual(runs.json()["items"][0]["run_id"], "demo")
        self.assertEqual(dashboard.json()["overview"]["paper_count"], 2)
        self.assertEqual(
            len(dashboard.json()["opportunities"]["directions"]), 2
        )
        self.assertEqual(papers.json()["total"], 1)

    async def test_missing_run_returns_404(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transport = httpx.ASGITransport(
                app=create_app(root, local_root=root / "local")
            )
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                response = await client.get("/api/runs/missing/dashboard")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
