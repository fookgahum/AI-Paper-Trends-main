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
            "avg_rating": None,
            "topic_id": 0,
            "topic_name": "Graph learning",
            "source_url": "https://example.test/a",
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
            "avg_rating": None,
            "topic_id": 1,
            "topic_name": "Language evaluation",
            "source_url": "https://example.test/b",
        },
    ]
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    (run_dir / "papers.json").write_text(json.dumps(papers), encoding="utf-8")


class ResultStoreTests(unittest.TestCase):
    def test_dashboard_reconciles_counts_and_filters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_snapshot(root)
            dashboard = ResultStore(root).dashboard("demo")

        self.assertEqual(dashboard["overview"]["paper_count"], 2)
        self.assertEqual(dashboard["overview"]["conference_count"], 2)
        self.assertEqual(dashboard["overview"]["topic_count"], 2)
        self.assertEqual(dashboard["overview"]["rated_paper_count"], 0)
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

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["id"], "paper-a")
        self.assertEqual(filtered["total"], 1)
        self.assertEqual(filtered["items"][0]["conference"], "ACL")

    def test_rejects_unsafe_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ResultStoreError):
                ResultStore(Path(directory)).get_snapshot("../outside")


class WebApiTests(unittest.IsolatedAsyncioTestCase):
    async def test_home_health_and_data_endpoints(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_snapshot(root)
            transport = httpx.ASGITransport(app=create_app(root))
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                home = await client.get("/")
                health = await client.get("/api/health")
                runs = await client.get("/api/runs")
                dashboard = await client.get("/api/runs/demo/dashboard")
                papers = await client.get("/api/runs/demo/papers?q=language")

        self.assertEqual(home.status_code, 200)
        self.assertIn("AI Paper Trends", home.text)
        self.assertEqual(health.json(), {"status": "ok", "run_count": 1})
        self.assertEqual(runs.json()["items"][0]["run_id"], "demo")
        self.assertEqual(dashboard.json()["overview"]["paper_count"], 2)
        self.assertEqual(papers.json()["total"], 1)

    async def test_missing_run_returns_404(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transport = httpx.ASGITransport(app=create_app(Path(directory)))
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                response = await client.get("/api/runs/missing/dashboard")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
