"""Build the complete official 2026 CCF-A dashboard dataset."""

from __future__ import annotations

import argparse
from pathlib import Path

import main as pipeline
from scripts.export_web_data import export_snapshot
from scripts.fetch_2026_samples import fetch_samples, write_jsonl
from src import run_topic_modeling


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "ccfa_2026_sample200.jsonl"
PROCESSED_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ccfa_2026_sample200_with_topics.csv"
)
RESULT_DIR = PROJECT_ROOT / "results" / "ccfa_2026_web"
WEB_DIR = PROJECT_ROOT / "data" / "web" / "ccfa_2026"
CONFIG_PATH = PROJECT_ROOT / "configs" / "ccfa_2026_web.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch, model, and export the 2026 three-conference dashboard."
    )
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-model", action="store_true")
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_size != 200:
        raise ValueError(
            "This published dashboard run is fixed at 200 papers per conference."
        )
    config = pipeline.load_config(CONFIG_PATH)

    if args.skip_fetch:
        if not RAW_PATH.exists():
            raise FileNotFoundError(f"Missing cached sample: {RAW_PATH}")
        print(f"[2026-build] Reusing sample: {RAW_PATH}", flush=True)
    else:
        write_jsonl(fetch_samples(args.sample_size, args.seed), RAW_PATH)

    if args.skip_model:
        if not PROCESSED_PATH.exists():
            raise FileNotFoundError(f"Missing processed topic data: {PROCESSED_PATH}")
        print(f"[2026-build] Reusing topic output: {PROCESSED_PATH}", flush=True)
        processed_path = PROCESSED_PATH
    else:
        processed_path = run_topic_modeling.main(
            config=config,
            input_path=RAW_PATH,
            processed_data_dir=PROCESSED_PATH.parent,
            output_dir=RESULT_DIR,
            models_cache_dir=PROJECT_ROOT / "models",
        )

    export_snapshot(
        input_path=processed_path,
        labels_path=RESULT_DIR / "topic_labels.yaml",
        output_dir=WEB_DIR,
        run_id="ccfa_2026",
        seed=args.seed,
        sample_size=args.sample_size,
        topic_model=(
            "TF-IDF (1-2 grams) + KMeans, 24 topics, random seed 2026"
        ),
    )
    print("[2026-build] Dashboard dataset is ready.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
