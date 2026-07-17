"""Download deterministic 2026 paper samples from official conference sites."""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROGRAM_SOURCES = {
    "ICLR": {
        "program": "https://iclr.cc/static/virtual/data/iclr-2026-orals-posters.json",
        "abstracts": "https://iclr.cc/static/virtual/data/iclr-2026-abstracts.json",
        "base_url": "https://iclr.cc",
    },
    "ICML": {
        "program": "https://icml.cc/static/virtual/data/icml-2026-orals-posters.json",
        "abstracts": "https://icml.cc/static/virtual/data/icml-2026-abstracts.json",
        "base_url": "https://icml.cc",
    },
}
ACL_URL = "https://aclanthology.org/events/acl-2026/"
ACL_PAPER_PATTERN = re.compile(r"^/2026\.acl-long\.(\d+)/$")


def log(message: str) -> None:
    """Emit an immediate progress marker for long downloads and parsing."""
    print(f"[2026-sample] {message}", flush=True)


def _request(session: requests.Session, url: str) -> requests.Response:
    log(f"Downloading {url}")
    response = session.get(url, timeout=(15, 120))
    response.raise_for_status()
    return response


def _normalise_keywords(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _deterministic_sample(
    papers: Iterable[Dict[str, Any]], conference: str, size: int, seed: int
) -> List[Dict[str, Any]]:
    ordered = sorted(papers, key=lambda paper: paper["id"])
    if len(ordered) < size:
        raise RuntimeError(
            f"{conference} only yielded {len(ordered)} valid papers; {size} requested."
        )
    selected = random.Random(f"{seed}:{conference}:2026").sample(ordered, size)
    return sorted(selected, key=lambda paper: paper["id"])


def fetch_virtual_program(
    session: requests.Session, conference: str, size: int, seed: int
) -> List[Dict[str, Any]]:
    """Fetch ICLR/ICML papers from their official public program JSON."""
    source = PROGRAM_SOURCES[conference]
    program = _request(session, source["program"]).json()
    abstracts = _request(session, source["abstracts"]).json()
    records = program.get("results", []) if isinstance(program, dict) else program
    if not isinstance(records, list) or not isinstance(abstracts, dict):
        raise RuntimeError(f"Unexpected {conference} program response format.")

    papers: List[Dict[str, Any]] = []
    for record in records:
        record_id = str(record.get("id", "")).strip()
        title = str(record.get("name") or record.get("title") or "").strip()
        abstract = str(abstracts.get(record_id) or "").strip()
        authors = [
            str(author.get("fullname") or author.get("name") or "").strip()
            for author in record.get("authors", [])
            if isinstance(author, dict)
        ]
        authors = [author for author in authors if author]
        if not record_id or not title or not abstract:
            continue
        paper_url = (
            record.get("paper_url")
            or record.get("sourceurl")
            or f"/virtual/2026/poster/{record_id}"
        )
        papers.append(
            {
                "id": f"{conference.lower()}-2026-{record_id}",
                "conference": conference,
                "year": 2026,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "keywords": _normalise_keywords(record.get("keywords")),
                "decision": str(record.get("decision") or "Accepted").strip(),
                "source_url": urljoin(source["base_url"], str(paper_url)),
            }
        )
    log(f"{conference}: {len(papers)} valid public program papers found")
    return _deterministic_sample(papers, conference, size, seed)


def parse_acl_long_papers(html: str) -> List[Dict[str, Any]]:
    """Parse ACL 2026 long-paper metadata from the official Anthology page."""
    soup = BeautifulSoup(html, "html.parser")
    abstracts: Dict[str, str] = {}
    for container in soup.select('[id^="abstract-2026--acl-long--"]'):
        number = str(container.get("id", "")).rsplit("--", 1)[-1]
        body = container.select_one(".card-body")
        if number and body is not None:
            abstracts[number] = body.get_text(" ", strip=True)

    papers: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=ACL_PAPER_PATTERN):
        match = ACL_PAPER_PATTERN.match(str(anchor.get("href", "")))
        if not match or match.group(1) == "0":
            continue
        anthology_id = f"2026.acl-long.{match.group(1)}"
        if anthology_id in seen:
            continue
        entry = anchor.find_parent("div", class_="d-sm-flex")
        title = anchor.get_text(" ", strip=True)
        abstract = abstracts.get(match.group(1), "")
        authors = (
            [
                author.get_text(" ", strip=True)
                for author in entry.select('a[href^="/people/"]')
                if author.get_text(" ", strip=True)
            ]
            if entry is not None
            else []
        )
        if not title or not abstract:
            continue
        seen.add(anthology_id)
        papers.append(
            {
                "id": f"acl-{anthology_id}",
                "conference": "ACL",
                "year": 2026,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "keywords": [],
                "decision": "Published (Long Paper)",
                "source_url": f"https://aclanthology.org/{anthology_id}/",
            }
        )
    return papers


def fetch_acl(
    session: requests.Session, size: int, seed: int
) -> List[Dict[str, Any]]:
    html = _request(session, ACL_URL).text
    papers = parse_acl_long_papers(html)
    log(f"ACL: {len(papers)} valid long papers found")
    return _deterministic_sample(papers, "ACL", size, seed)


def fetch_samples(size: int, seed: int) -> List[Dict[str, Any]]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "AI-Paper-Trends/1.0 "
                "(public academic metadata sampler; contact via repository)"
            )
        }
    )
    papers: List[Dict[str, Any]] = []
    for conference in ("ICLR", "ICML"):
        papers.extend(fetch_virtual_program(session, conference, size, seed))
    papers.extend(fetch_acl(session, size, seed))
    return papers


def write_jsonl(papers: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as file:
        for paper in papers:
            file.write(json.dumps(paper, ensure_ascii=False) + "\n")
    log(f"Saved {len(papers)} papers to {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch deterministic samples from official 2026 proceedings."
    )
    parser.add_argument("--sample-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "raw" / "ccfa_2026_sample200.jsonl",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_size < 1:
        raise ValueError("--sample-size must be positive")
    papers = fetch_samples(args.sample_size, args.seed)
    write_jsonl(papers, args.output)
    counts = {
        conference: sum(paper["conference"] == conference for paper in papers)
        for conference in ("ICLR", "ICML", "ACL")
    }
    log(f"Complete. Conference counts: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
