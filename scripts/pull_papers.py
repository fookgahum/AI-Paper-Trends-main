"""Command-line entry point for the same paper pull used by the website."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.paper_sources import PaperPullService
from src.storage import LocalDatabase


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pull, normalize, and deduplicate papers from a public URL."
    )
    parser.add_argument("url", help="Public proceedings page or JSON-feed URL")
    parser.add_argument("--conference", required=True, help="Conference label")
    parser.add_argument("--year", required=True, type=int, help="Publication year")
    parser.add_argument(
        "--parser", choices=("auto", "json", "html", "acl"), default="auto"
    )
    parser.add_argument("--download-pdf", action="store_true")
    parser.add_argument(
        "--local-root",
        type=Path,
        default=PROJECT_ROOT / "data" / "local",
        help="SQLite and artifact directory",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    database = LocalDatabase(args.local_root / "app.db")
    database.initialize()
    service = PaperPullService(database, args.local_root / "artifacts")
    created = service.create_job(
        {
            "url": args.url,
            "conference": args.conference,
            "year": args.year,
            "parser": args.parser,
            "download_pdf": args.download_pdf,
            "remember_source": True,
        }
    )
    service.run_job(created["job_id"], created["source_id"])
    job = database.get_job(created["job_id"])
    print(json.dumps(job, ensure_ascii=False, indent=2))
    return 0 if job["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
