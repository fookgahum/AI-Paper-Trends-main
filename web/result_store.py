"""Validated, cached access to read-only web result snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import fmean
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional


class ResultStoreError(RuntimeError):
    """Raised when a result snapshot is missing or malformed."""


@dataclass(frozen=True)
class RunSnapshot:
    """One immutable result export loaded from disk."""

    manifest: Dict[str, Any]
    papers: List[Dict[str, Any]]


class ResultStore:
    """Discover and query exported paper-analysis runs."""

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self._cache: Dict[str, tuple[tuple[int, int], RunSnapshot]] = {}
        self._lock = RLock()

    def list_runs(self) -> List[Dict[str, Any]]:
        """Return valid manifests, newest first."""
        if not self.data_root.exists():
            return []

        manifests: List[Dict[str, Any]] = []
        for path in sorted(self.data_root.glob("*/manifest.json")):
            try:
                snapshot = self.get_snapshot(path.parent.name)
            except (OSError, ValueError, ResultStoreError):
                continue
            manifests.append(snapshot.manifest)
        return sorted(
            manifests,
            key=lambda item: (item.get("year", 0), item.get("generated_at", "")),
            reverse=True,
        )

    def get_snapshot(self, run_id: str) -> RunSnapshot:
        """Load and cache one validated run."""
        run_dir = self._safe_run_directory(run_id)
        manifest_path = run_dir / "manifest.json"
        papers_path = run_dir / "papers.json"
        if not manifest_path.exists() or not papers_path.exists():
            raise ResultStoreError(f"Unknown or incomplete run: {run_id}")

        fingerprint = (
            manifest_path.stat().st_mtime_ns,
            papers_path.stat().st_mtime_ns,
        )
        with self._lock:
            cached = self._cache.get(run_id)
            if cached and cached[0] == fingerprint:
                return cached[1]

            manifest = self._read_json(manifest_path)
            papers = self._read_json(papers_path)
            self._validate_manifest(manifest, manifest_path)
            self._validate_papers(papers, papers_path)
            if manifest["run_id"] != run_id:
                raise ResultStoreError(
                    f"Run id mismatch in {manifest_path}: {manifest['run_id']}"
                )
            self._validate_snapshot(manifest, papers, run_dir)
            snapshot = RunSnapshot(manifest=manifest, papers=papers)
            self._cache[run_id] = (fingerprint, snapshot)
            return snapshot

    def dashboard(self, run_id: str, conference: Optional[str] = None) -> Dict[str, Any]:
        """Build reconciled overview, filter, and topic data for a run."""
        snapshot = self.get_snapshot(run_id)
        papers = self._filter_conference(snapshot.papers, conference)
        conferences = sorted({paper["conference"] for paper in papers})
        topics = self._topic_rows(papers)
        ratings = [
            float(paper["avg_rating"])
            for paper in papers
            if paper.get("avg_rating") is not None
        ]
        decisions: Dict[str, int] = {}
        for paper in papers:
            decision = str(paper.get("decision") or "N/A")
            decisions[decision] = decisions.get(decision, 0) + 1

        conference_counts = [
            {
                "conference": name,
                "paper_count": sum(
                    paper["conference"] == name for paper in papers
                ),
            }
            for name in conferences
        ]
        return {
            "manifest": snapshot.manifest,
            "overview": {
                "paper_count": len(papers),
                "conference_count": len(conferences),
                "topic_count": len(topics),
                "rated_paper_count": len(ratings),
                "avg_rating": round(fmean(ratings), 2) if ratings else None,
            },
            "filters": {
                "conferences": sorted(
                    {paper["conference"] for paper in snapshot.papers}
                ),
                "topics": [row["topic_name"] for row in topics],
                "decisions": sorted(decisions),
            },
            "conference_counts": conference_counts,
            "decision_counts": [
                {"decision": name, "paper_count": count}
                for name, count in sorted(
                    decisions.items(), key=lambda item: item[1], reverse=True
                )
            ],
            "topics": topics,
        }

    def query_papers(
        self,
        run_id: str,
        *,
        conference: Optional[str] = None,
        topic: Optional[str] = None,
        decision: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "title",
    ) -> Dict[str, Any]:
        """Search, filter, sort, and paginate papers."""
        papers: Iterable[Dict[str, Any]] = self.get_snapshot(run_id).papers
        papers = self._filter_conference(papers, conference)
        if topic:
            papers = [paper for paper in papers if paper["topic_name"] == topic]
        if decision:
            papers = [paper for paper in papers if paper["decision"] == decision]
        if query:
            needle = query.casefold().strip()
            papers = [
                paper
                for paper in papers
                if needle
                in " ".join(
                    [
                        paper["title"],
                        paper["abstract"],
                        " ".join(paper.get("authors", [])),
                        " ".join(paper.get("keywords", [])),
                    ]
                ).casefold()
            ]

        sorters = {
            "title": lambda paper: paper["title"].casefold(),
            "conference": lambda paper: (
                paper["conference"].casefold(),
                paper["title"].casefold(),
            ),
            "topic": lambda paper: (
                paper["topic_name"].casefold(),
                paper["title"].casefold(),
            ),
            "rating": lambda paper: (
                paper.get("avg_rating") is None,
                -(paper.get("avg_rating") or 0),
                paper["title"].casefold(),
            ),
        }
        sorted_papers = sorted(papers, key=sorters.get(sort, sorters["title"]))
        total = len(sorted_papers)
        start = (page - 1) * page_size
        return {
            "items": sorted_papers[start : start + page_size],
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size if total else 0,
        }

    def get_paper(self, run_id: str, paper_id: str) -> Dict[str, Any]:
        """Return one paper by its stable exported id."""
        for paper in self.get_snapshot(run_id).papers:
            if paper["id"] == paper_id:
                return paper
        raise ResultStoreError(f"Unknown paper: {paper_id}")

    def _safe_run_directory(self, run_id: str) -> Path:
        if not run_id or Path(run_id).name != run_id or run_id in {".", ".."}:
            raise ResultStoreError("Invalid run id")
        run_dir = (self.data_root / run_id).resolve()
        root = self.data_root.resolve()
        if run_dir.parent != root:
            raise ResultStoreError("Invalid run path")
        return run_dir

    @staticmethod
    def _read_json(path: Path) -> Any:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _validate_manifest(manifest: Any, path: Path) -> None:
        required = {"run_id", "title", "year", "generated_at", "sources"}
        if not isinstance(manifest, dict) or not required.issubset(manifest):
            raise ResultStoreError(f"Invalid manifest: {path}")
        if not isinstance(manifest["sources"], list):
            raise ResultStoreError(f"Manifest sources must be a list: {path}")

    @staticmethod
    def _validate_papers(papers: Any, path: Path) -> None:
        required = {
            "id",
            "conference",
            "year",
            "title",
            "abstract",
            "authors",
            "decision",
            "topic_name",
            "source_url",
        }
        if not isinstance(papers, list):
            raise ResultStoreError(f"Papers must be a list: {path}")
        seen_ids = set()
        for index, paper in enumerate(papers):
            if not isinstance(paper, dict) or not required.issubset(paper):
                raise ResultStoreError(f"Invalid paper at row {index}: {path}")
            if not isinstance(paper["authors"], list):
                raise ResultStoreError(f"Paper authors must be a list: {path}")
            paper_id = paper["id"]
            if not isinstance(paper_id, str) or not paper_id:
                raise ResultStoreError(f"Paper id must be non-empty: {path}")
            if paper_id in seen_ids:
                raise ResultStoreError(f"Duplicate paper id {paper_id}: {path}")
            seen_ids.add(paper_id)
            if not str(paper["title"]).strip() or not str(paper["abstract"]).strip():
                raise ResultStoreError(f"Paper text must be non-empty: {path}")
            if not str(paper["source_url"]).startswith("https://"):
                raise ResultStoreError(f"Paper source URL must use HTTPS: {path}")

    @staticmethod
    def _validate_snapshot(
        manifest: Dict[str, Any], papers: List[Dict[str, Any]], run_dir: Path
    ) -> None:
        declared_total = manifest.get("paper_count")
        if declared_total is not None and declared_total != len(papers):
            raise ResultStoreError(
                f"Manifest paper count does not match papers.json: {run_dir}"
            )
        actual_counts: Dict[str, int] = {}
        for paper in papers:
            conference = paper["conference"]
            actual_counts[conference] = actual_counts.get(conference, 0) + 1
        for source in manifest["sources"]:
            if not isinstance(source, dict) or "conference" not in source:
                raise ResultStoreError(f"Invalid source entry: {run_dir}")
            declared = source.get("paper_count")
            actual = actual_counts.get(source["conference"], 0)
            if declared is not None and actual != declared:
                raise ResultStoreError(
                    f"Source paper count does not match papers.json: {run_dir}"
                )

    @staticmethod
    def _filter_conference(
        papers: Iterable[Dict[str, Any]], conference: Optional[str]
    ) -> List[Dict[str, Any]]:
        if not conference:
            return list(papers)
        return [paper for paper in papers if paper["conference"] == conference]

    @staticmethod
    def _topic_rows(papers: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[str, Dict[str, Any]] = {}
        for paper in papers:
            name = paper["topic_name"]
            row = grouped.setdefault(
                name,
                {
                    "topic_id": paper.get("topic_id"),
                    "topic_name": name,
                    "paper_count": 0,
                    "conferences": {},
                },
            )
            row["paper_count"] += 1
            conference = paper["conference"]
            row["conferences"][conference] = (
                row["conferences"].get(conference, 0) + 1
            )
        return sorted(
            grouped.values(),
            key=lambda row: (-row["paper_count"], row["topic_name"].casefold()),
        )
