"""Unit tests for the lightweight parts of the analysis pipeline."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

import main
from src import analyze, get_papers, run_topic_modeling


class ConfigTests(unittest.TestCase):
    def test_all_repository_configs_are_valid(self) -> None:
        config_directory = Path(__file__).resolve().parents[1] / "configs"
        config_paths = sorted(config_directory.glob("*.yaml"))
        self.assertTrue(config_paths)
        for config_path in config_paths:
            with self.subTest(config=config_path.name):
                main.load_config(config_path)

    def test_load_config_accepts_supported_options(self) -> None:
        content = """
conference_id: ICLR.cc/2025/Conference
fetch_reviews: false
limit: 10
topic_modeling:
  enabled: true
  min_topic_size: 2
  cpu_threads: 0
  heartbeat_seconds: 10
analysis:
  enabled: true
  top_n: 5
  tasks: [plot_paper_count]
output_folder_name: test_analysis
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            config = main.load_config(path)
        self.assertEqual(config["limit"], 10)

    def test_load_config_rejects_invalid_parallelism(self) -> None:
        content = """
conference_id: ICLR.cc/2025/Conference
topic_modeling:
  cpu_threads: -1
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "cpu_threads"):
                main.load_config(path)

    def test_load_config_rejects_unknown_task(self) -> None:
        content = """
conference_id: ICLR.cc/2025/Conference
analysis:
  tasks: [unknown_task]
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Unsupported analysis tasks"):
                main.load_config(path)

    def test_load_config_rejects_unknown_topic_backend(self) -> None:
        content = """
conference_id: ICLR.cc/2025/Conference
topic_modeling:
  backend: unknown
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            path.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "topic_modeling.backend"):
                main.load_config(path)


class PaperExtractionTests(unittest.TestCase):
    def test_extracts_nested_content_reviews_and_decision(self) -> None:
        note = SimpleNamespace(
            id="paper-1",
            content={
                "title": {"value": "A paper"},
                "abstract": {"value": "An abstract"},
                "keywords": {"value": ["topic"]},
                "authors": {"value": ["Author"]},
            },
            details={
                "replies": [
                    {
                        "invitations": ["Venue/Submission1/-/Official_Review"],
                        "content": {"rating": {"value": "8: accept"}},
                    },
                    {
                        "invitations": ["Venue/Submission1/-/Official_Review"],
                        "content": {"rating": {"value": 6}},
                    },
                    {
                        "invitations": ["Venue/Submission1/-/Decision"],
                        "content": {"decision": {"value": "Accept (Poster)"}},
                    },
                ]
            },
        )

        paper = get_papers._extract_paper(note, fetch_reviews=True)

        self.assertEqual(paper["title"], "A paper")
        self.assertEqual(paper["decision"], "Accept (Poster)")
        self.assertEqual(paper["review_ratings"], [8.0, 6.0])
        self.assertEqual(paper["avg_rating"], 7.0)

    def test_output_path_is_shared_with_scheduler(self) -> None:
        config = {
            "conference_id": "ICLR.cc/2025/Conference",
            "fetch_reviews": True,
            "limit": 25,
        }
        raw_directory = Path("data/raw")
        expected = raw_directory / "ICLRcc_2025_Conference_papers_reviews_limit25.jsonl"
        self.assertEqual(get_papers.build_output_path(config, raw_directory), expected)
        self.assertEqual(
            main.get_expected_filepaths(config, raw_directory, Path("data/processed"))["raw"],
            expected,
        )

    def test_limited_fetch_uses_one_request_with_embedded_replies(self) -> None:
        note = SimpleNamespace(
            id="paper-1",
            content={"title": {"value": "A"}, "abstract": {"value": "B"}},
            details={"replies": []},
        )

        class FakeClient:
            request = None

            def get_group(self, conference_id):
                self.assert_conference = conference_id
                return SimpleNamespace(content={"submission_name": {"value": "Paper"}})

            def get_notes(self, **kwargs):
                self.request = kwargs
                return [note]

        client = FakeClient()
        papers = get_papers.get_all_papers(
            client, "Venue/2025/Conference", fetch_reviews=True, limit=1
        )

        self.assertEqual(len(papers), 1)
        self.assertEqual(
            client.request,
            {
                "invitation": "Venue/2025/Conference/-/Paper",
                "limit": 1,
                "details": "replies",
            },
        )


class AnalysisTests(unittest.TestCase):
    def test_acceptance_rate_excludes_unknown_decisions(self) -> None:
        dataframe = pd.DataFrame(
            {
                "id": ["a", "b", "c", "d", "outlier"],
                "Topic": [0, 0, 0, 1, -1],
                "decision": ["Accept (Poster)", "Reject", "N/A", "N/A", "Reject"],
                "avg_rating": [8, 3, None, None, 1],
            }
        )

        result = analyze.create_analysis_dataframe(dataframe, {0: "Known topic"})
        topic_zero = result[result["Topic"] == 0].iloc[0]
        topic_one = result[result["Topic"] == 1].iloc[0]

        self.assertEqual(topic_zero["Topic_Name"], "Known topic")
        self.assertEqual(topic_zero["paper_count"], 3)
        self.assertAlmostEqual(topic_zero["acceptance_rate"], 0.5)
        self.assertTrue(pd.isna(topic_one["acceptance_rate"]))

    def test_analysis_without_review_columns_still_counts_topics(self) -> None:
        dataframe = pd.DataFrame({"id": ["a", "b"], "Topic": [0, 0]})
        result = analyze.create_analysis_dataframe(dataframe, {})
        self.assertEqual(result.iloc[0]["paper_count"], 2)
        self.assertEqual(result.iloc[0]["N/A"], 2)
        self.assertTrue(pd.isna(result.iloc[0]["avg_rating"]))


class TopicModelingTests(unittest.TestCase):
    def test_preprocessing_creates_text_when_keywords_are_missing(self) -> None:
        dataframe = pd.DataFrame(
            [
                {"id": "a", "title": "First", "abstract": "Alpha"},
                {"id": "b", "title": "Second", "abstract": "Beta"},
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "papers.jsonl"
            dataframe.to_json(path, orient="records", lines=True)
            processed, documents = run_topic_modeling.load_and_preprocess_data(path)

        self.assertIn("keywords", processed.columns)
        self.assertEqual(documents, ["First. . Alpha", "Second. . Beta"])

    def test_lightweight_backend_writes_topics_and_labels(self) -> None:
        dataframe = pd.DataFrame(
            [
                {
                    "id": f"graph-{index}",
                    "title": "Graph model",
                    "abstract": "Graph node edge learning",
                }
                for index in range(3)
            ]
            + [
                {
                    "id": f"language-{index}",
                    "title": "Language model",
                    "abstract": "Text token language generation",
                }
                for index in range(3)
            ]
        )
        config = {
            "topic_modeling": {
                "backend": "tfidf_kmeans",
                "topic_count": 2,
                "random_seed": 2026,
                "cpu_threads": 1,
                "heartbeat_seconds": 60,
            }
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "papers.jsonl"
            dataframe.to_json(input_path, orient="records", lines=True)
            output_path = run_topic_modeling.main(
                config,
                input_path,
                root / "processed",
                root / "results",
                root / "models",
            )
            processed = pd.read_csv(output_path, encoding="utf-8-sig")
            labels_path = root / "results" / "topic_labels.yaml"

            self.assertTrue(labels_path.exists())
            self.assertEqual(set(processed["Topic"]), {0, 1})


if __name__ == "__main__":
    unittest.main()
