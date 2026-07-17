"""Tests for official 2026 sample parsing and web export conversion."""

from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

import pandas as pd

from scripts.export_web_data import build_manifest, build_papers
from scripts.fetch_2026_samples import _deterministic_sample, parse_acl_long_papers
from web.result_store import ResultStore


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SampleImportTests(unittest.TestCase):
    def test_deterministic_sample_is_stable(self) -> None:
        papers = [{"id": f"paper-{index}"} for index in range(20)]
        first = _deterministic_sample(papers, "TEST", 5, 2026)
        second = _deterministic_sample(reversed(papers), "TEST", 5, 2026)
        self.assertEqual(first, second)

    def test_acl_parser_extracts_one_long_paper_and_skips_volume(self) -> None:
        html = """
        <a href="/2026.acl-long.0/">Proceedings volume</a>
        <div class="d-sm-flex">
          <strong><a href="/2026.acl-long.42/">A Long Paper</a></strong>
          <a href="/people/a/">Alice</a><a href="/people/b/">Bob</a>
        </div>
        <div id="abstract-2026--acl-long--42"><div class="card-body">
          A public abstract.
        </div></div>
        """
        papers = parse_acl_long_papers(html)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0]["id"], "acl-2026.acl-long.42")
        self.assertEqual(papers[0]["authors"], ["Alice", "Bob"])


class WebExportTests(unittest.TestCase):
    def test_build_papers_maps_topics_and_list_fields(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    "id": "paper-1",
                    "conference": "ICLR",
                    "year": 2026,
                    "title": "A paper",
                    "abstract": "An abstract",
                    "authors": "['Alice']",
                    "keywords": "['topic']",
                    "decision": "Poster",
                    "source_url": "https://example.test/paper",
                    "Topic": 3,
                }
            ]
        )
        papers = build_papers(dataframe, {3: "Topic label"})
        self.assertEqual(papers[0]["topic_name"], "Topic label")
        self.assertEqual(papers[0]["authors"], ["Alice"])
        self.assertNotIn("avg_rating", papers[0])

    def test_manifest_counts_sources(self) -> None:
        papers = [
            {"conference": conference}
            for conference in ("ICLR", "ICML", "ACL")
            for _ in range(2)
        ]
        manifest = build_manifest(papers, "demo", seed=7, sample_size=2)
        self.assertEqual(manifest["paper_count"], 6)
        self.assertEqual(
            [source["paper_count"] for source in manifest["sources"]], [2, 2, 2]
        )

    def test_tracked_2026_snapshot_is_complete_and_not_topic_collapsed(self) -> None:
        store = ResultStore(PROJECT_ROOT / "data" / "web")
        dashboard = store.dashboard("ccfa_2026")
        papers = json.loads(
            (
                PROJECT_ROOT / "data" / "web" / "ccfa_2026" / "papers.json"
            ).read_text(encoding="utf-8")
        )
        conference_counts = Counter(paper["conference"] for paper in papers)
        topic_counts = Counter(paper["topic_id"] for paper in papers)
        opportunities = json.loads(
            (
                PROJECT_ROOT
                / "data"
                / "web"
                / "ccfa_2026"
                / "opportunities.json"
            ).read_text(encoding="utf-8")
        )
        directions = opportunities["directions"]

        self.assertEqual(dashboard["overview"]["paper_count"], 600)
        self.assertEqual(conference_counts, {"ICLR": 200, "ICML": 200, "ACL": 200})
        self.assertEqual(len(topic_counts), 24)
        self.assertLessEqual(max(topic_counts.values()), 100)
        self.assertGreaterEqual(min(topic_counts.values()), 5)
        self.assertEqual(len(directions), 13)
        self.assertEqual(sum(item["paper_count"] for item in directions), 600)
        self.assertEqual(
            {topic for item in directions for topic in item["topic_ids"]},
            set(topic_counts),
        )
        self.assertEqual(
            {paper["direction_id"] for paper in papers},
            {item["id"] for item in directions},
        )
        expected_paper_fields = {
            "id",
            "conference",
            "year",
            "title",
            "abstract",
            "authors",
            "keywords",
            "decision",
            "topic_id",
            "topic_name",
            "source_url",
            "direction_id",
            "direction_title",
        }
        self.assertTrue(
            all(set(paper) == expected_paper_fields for paper in papers)
        )
        self.assertTrue(
            all(
                "sample_share" not in item
                and "heavy_compute_signal_rate" not in item
                for item in directions
            )
        )
        self.assertTrue(
            all(
                0 <= score["score"] <= 100
                for item in directions
                for score in item["scores"].values()
            )
        )
        self.assertTrue(
            all(
                isinstance(item["title"]["zh-CN"], str)
                and isinstance(item["title"]["en-US"], str)
                for item in directions
            )
        )
        self.assertTrue(
            all(
                len(item["entry_points"][language]) == 3
                for item in directions
                for language in ("zh-CN", "en-US")
            )
        )
        self.assertEqual(len(opportunities["limitations"]["zh-CN"]), 4)


if __name__ == "__main__":
    unittest.main()
