"""Command-line entry point for the paper trend analysis pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import yaml

from src import analyze, get_papers, run_topic_modeling


PROJECT_ROOT = Path(__file__).resolve().parent
ALLOWED_ANALYSIS_TASKS = {
    "plot_paper_count",
    "plot_avg_rating",
    "plot_decision_breakdown",
    "generate_summary_table",
}


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file and validate the supported options."""
    with config_path.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, dict):
        raise ValueError("The configuration file must contain a YAML mapping.")

    conference_id = config.get("conference_id")
    if not isinstance(conference_id, str) or not conference_id.strip():
        raise ValueError("'conference_id' must be a non-empty string.")

    fetch_reviews = config.get("fetch_reviews", False)
    if not isinstance(fetch_reviews, bool):
        raise ValueError("'fetch_reviews' must be true or false.")

    limit = config.get("limit")
    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise ValueError("'limit' must be null or a positive integer.")

    output_folder = config.get("output_folder_name", "default_analysis")
    if (
        not isinstance(output_folder, str)
        or not output_folder.strip()
        or output_folder in {".", ".."}
        or Path(output_folder).name != output_folder
    ):
        raise ValueError("'output_folder_name' must be a single directory name.")

    topic_config = config.get("topic_modeling", {})
    if not isinstance(topic_config, dict):
        raise ValueError("'topic_modeling' must be a mapping.")
    if not isinstance(topic_config.get("enabled", False), bool):
        raise ValueError("'topic_modeling.enabled' must be true or false.")
    backend = topic_config.get("backend", "bertopic")
    if backend not in {"bertopic", "tfidf_kmeans"}:
        raise ValueError(
            "'topic_modeling.backend' must be 'bertopic' or 'tfidf_kmeans'."
        )
    topic_count = topic_config.get("topic_count", 24)
    if not isinstance(topic_count, int) or topic_count < 2:
        raise ValueError("'topic_modeling.topic_count' must be at least 2.")
    random_seed = topic_config.get("random_seed", 2026)
    if not isinstance(random_seed, int):
        raise ValueError("'topic_modeling.random_seed' must be an integer.")
    model_id = topic_config.get("model_id", "sentence-transformers/all-mpnet-base-v2")
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("'topic_modeling.model_id' must be a non-empty string.")
    min_topic_size = topic_config.get("min_topic_size", 30)
    if not isinstance(min_topic_size, int) or min_topic_size < 2:
        raise ValueError("'topic_modeling.min_topic_size' must be at least 2.")
    embedding_batch_size = topic_config.get("embedding_batch_size", 32)
    if not isinstance(embedding_batch_size, int) or embedding_batch_size <= 0:
        raise ValueError(
            "'topic_modeling.embedding_batch_size' must be a positive integer."
        )
    cpu_threads = topic_config.get("cpu_threads", 0)
    if not isinstance(cpu_threads, int) or cpu_threads < 0:
        raise ValueError("'topic_modeling.cpu_threads' must be zero or greater.")
    heartbeat_seconds = topic_config.get("heartbeat_seconds", 15)
    if not isinstance(heartbeat_seconds, int) or heartbeat_seconds <= 0:
        raise ValueError(
            "'topic_modeling.heartbeat_seconds' must be a positive integer."
        )

    analysis_config = config.get("analysis", {})
    if not isinstance(analysis_config, dict):
        raise ValueError("'analysis' must be a mapping.")
    analysis_enabled = analysis_config.get("enabled", False)
    if not isinstance(analysis_enabled, bool):
        raise ValueError("'analysis.enabled' must be true or false.")
    tasks = analysis_config.get("tasks", [])
    if not isinstance(tasks, list) or not all(isinstance(task, str) for task in tasks):
        raise ValueError("'analysis.tasks' must be a list of task names.")
    unknown_tasks = set(tasks) - ALLOWED_ANALYSIS_TASKS
    if unknown_tasks:
        raise ValueError(f"Unsupported analysis tasks: {sorted(unknown_tasks)}")
    if analysis_enabled and not tasks:
        raise ValueError("'analysis.tasks' cannot be empty when analysis is enabled.")
    top_n = analysis_config.get("top_n", 65)
    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("'analysis.top_n' must be a positive integer.")

    return config


def get_expected_filepaths(
    config: Dict[str, Any], raw_dir: Path, processed_dir: Path
) -> Dict[str, Path]:
    """Build the cached raw and processed data paths for a configuration."""
    raw_path = get_papers.build_output_path(config, raw_dir)
    return {
        "raw": raw_path,
        "processed": processed_dir / f"{raw_path.stem}_with_topics.csv",
    }


def run_pipeline(config: Dict[str, Any], force_rerun: bool = False) -> None:
    """Run fetching, topic modeling, and analysis in sequence."""
    output_dir = PROJECT_ROOT / "results" / config.get(
        "output_folder_name", "default_analysis"
    )
    raw_dir = PROJECT_ROOT / "data" / "raw"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = get_expected_filepaths(config, raw_dir, processed_dir)
    raw_path = paths["raw"]
    processed_path = paths["processed"]

    print(f"Results directory: {output_dir}")
    print("\n--- [1/3] Fetching OpenReview papers ---")
    if raw_path.exists() and not force_rerun:
        print(f"Using cached data: {raw_path}")
    else:
        raw_path = get_papers.main(config=config, raw_data_dir=raw_dir)
    print("--- [1/3] Fetch complete ---")

    topic_enabled = config.get("topic_modeling", {}).get("enabled", False)
    print("\n--- [2/3] Topic modeling ---")
    if topic_enabled:
        if processed_path.exists() and not force_rerun:
            print(f"Using cached topic assignments: {processed_path}")
        else:
            processed_path = run_topic_modeling.main(
                config=config,
                input_path=raw_path,
                processed_data_dir=processed_dir,
                output_dir=output_dir,
                models_cache_dir=PROJECT_ROOT / "models",
            )
    else:
        print("Topic modeling is disabled.")
    print("--- [2/3] Topic modeling complete ---")

    analysis_enabled = config.get("analysis", {}).get("enabled", False)
    print("\n--- [3/3] Analysis and visualization ---")
    if analysis_enabled:
        if not processed_path.exists():
            raise FileNotFoundError(
                "Analysis requires a processed CSV. Enable topic modeling or provide "
                f"the cached file at {processed_path}."
            )
        analyze.main(config=config, input_path=processed_path, output_dir=output_dir)
    else:
        print("Analysis is disabled.")
    print("--- [3/3] Analysis complete ---")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch public OpenReview papers and analyze research topics."
    )
    parser.add_argument(
        "--config", required=True, type=Path, help="Path to a YAML configuration file."
    )
    parser.add_argument(
        "--force-rerun",
        action="store_true",
        help="Ignore cached raw and processed data.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        config_path = args.config.expanduser().resolve()
        print(f"Loading configuration: {config_path}")
        config = load_config(config_path)
        run_pipeline(config, force_rerun=args.force_rerun)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Pipeline failed: {error}", file=sys.stderr)
        return 1

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
