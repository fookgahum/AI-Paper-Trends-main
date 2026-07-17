"""Validated, cached access to read-only web result snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional


class ResultStoreError(RuntimeError):
    """Raised when a result snapshot is missing or malformed."""


@dataclass(frozen=True)
class RunSnapshot:
    """One immutable result export loaded from disk."""

    manifest: Dict[str, Any]
    papers: List[Dict[str, Any]]
    opportunities: Dict[str, Any]


class ResultStore:
    """Discover and query exported paper-analysis runs."""

    def __init__(self, data_root: Path) -> None:
        self.data_root = data_root
        self._cache: Dict[str, tuple[tuple[int, int, int], RunSnapshot]] = {}
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
        opportunities_path = run_dir / "opportunities.json"
        if not manifest_path.exists() or not papers_path.exists():
            raise ResultStoreError(f"Unknown or incomplete run: {run_id}")

        fingerprint = (
            manifest_path.stat().st_mtime_ns,
            papers_path.stat().st_mtime_ns,
            opportunities_path.stat().st_mtime_ns
            if opportunities_path.exists()
            else 0,
        )
        with self._lock:
            cached = self._cache.get(run_id)
            if cached and cached[0] == fingerprint:
                return cached[1]

            manifest = self._read_json(manifest_path)
            papers = self._read_json(papers_path)
            opportunities = (
                self._read_json(opportunities_path)
                if opportunities_path.exists()
                else {"profiles": [], "directions": []}
            )
            self._validate_manifest(manifest, manifest_path)
            self._validate_papers(papers, papers_path)
            self._validate_opportunities(opportunities, opportunities_path)
            if manifest["run_id"] != run_id:
                raise ResultStoreError(
                    f"Run id mismatch in {manifest_path}: {manifest['run_id']}"
                )
            self._validate_snapshot(manifest, papers, run_dir)
            if manifest.get("frontier_analysis") and not opportunities_path.exists():
                raise ResultStoreError(
                    f"Frontier analysis declared but file is missing: {run_dir}"
                )
            self._validate_frontier_coverage(
                manifest, papers, opportunities, run_dir
            )
            snapshot = RunSnapshot(
                manifest=manifest,
                papers=papers,
                opportunities=opportunities,
            )
            self._cache[run_id] = (fingerprint, snapshot)
            return snapshot

    def dashboard(self, run_id: str, conference: Optional[str] = None) -> Dict[str, Any]:
        """Build reconciled overview, filter, and topic data for a run."""
        snapshot = self.get_snapshot(run_id)
        papers = self._filter_conference(snapshot.papers, conference)
        topics = self._topic_rows(papers)
        opportunities = self._opportunity_view(snapshot.opportunities, papers)
        decisions = sorted(
            {str(paper.get("decision") or "N/A") for paper in papers}
        )
        return {
            "manifest": snapshot.manifest,
            "overview": {
                "paper_count": len(papers),
            },
            "filters": {
                "conferences": sorted(
                    {paper["conference"] for paper in snapshot.papers}
                ),
                "topics": [row["topic_name"] for row in topics],
                "decisions": decisions,
                "directions": [
                    {
                        "id": direction["id"],
                        "title": direction["title"],
                    }
                    for direction in snapshot.opportunities.get("directions", [])
                ],
            },
            "topics": topics,
            "opportunities": opportunities,
        }

    def query_papers(
        self,
        run_id: str,
        *,
        conference: Optional[str] = None,
        direction: Optional[str] = None,
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
        if direction:
            papers = [
                paper for paper in papers if paper.get("direction_id") == direction
            ]
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
    def _validate_opportunities(opportunities: Any, path: Path) -> None:
        if not isinstance(opportunities, dict):
            raise ResultStoreError(f"Invalid opportunities payload: {path}")
        profiles = opportunities.get("profiles", [])
        directions = opportunities.get("directions", [])
        if not isinstance(profiles, list) or not isinstance(directions, list):
            raise ResultStoreError(f"Invalid opportunity collections: {path}")
        if any(not isinstance(profile, dict) for profile in profiles):
            raise ResultStoreError(f"Invalid opportunity profile: {path}")
        profile_ids = {profile.get("id") for profile in profiles}
        if None in profile_ids or len(profile_ids) != len(profiles):
            raise ResultStoreError(f"Invalid or duplicate profile id: {path}")
        seen_ids = set()
        for direction in directions:
            required = {
                "id",
                "title",
                "summary",
                "topic_ids",
                "paper_count",
                "barriers",
                "scores",
                "representative_papers",
            }
            if not isinstance(direction, dict) or not required.issubset(direction):
                raise ResultStoreError(f"Invalid frontier direction: {path}")
            if direction["id"] in seen_ids:
                raise ResultStoreError(f"Duplicate frontier direction id: {path}")
            seen_ids.add(direction["id"])
            for bilingual_key in ("title", "summary"):
                bilingual = direction[bilingual_key]
                if (
                    not isinstance(bilingual, dict)
                    or not isinstance(bilingual.get("zh-CN"), str)
                    or not isinstance(bilingual.get("en-US"), str)
                ):
                    raise ResultStoreError(
                        f"Direction {bilingual_key} must be bilingual text: {path}"
                    )
            if profile_ids and set(direction["scores"]) != profile_ids:
                raise ResultStoreError(f"Direction profile scores do not match: {path}")
            for score in direction["scores"].values():
                if (
                    not isinstance(score, dict)
                    or not isinstance(score.get("score"), (int, float))
                    or not 0 <= score["score"] <= 100
                ):
                    raise ResultStoreError(f"Invalid direction score: {path}")

    @staticmethod
    def _validate_frontier_coverage(
        manifest: Dict[str, Any],
        papers: List[Dict[str, Any]],
        opportunities: Dict[str, Any],
        run_dir: Path,
    ) -> None:
        directions = opportunities.get("directions", [])
        if not directions:
            return

        direction_by_id = {direction["id"]: direction for direction in directions}
        declared = manifest.get("frontier_analysis", {}).get("direction_count")
        if declared is not None and declared != len(directions):
            raise ResultStoreError(
                f"Frontier direction count does not match opportunities.json: {run_dir}"
            )

        actual_counts: Dict[str, int] = {}
        actual_topics: Dict[str, set[int]] = {}
        for paper in papers:
            direction_id = paper.get("direction_id")
            if direction_id not in direction_by_id:
                raise ResultStoreError(
                    f"Paper has an unknown frontier direction: {run_dir}"
                )
            actual_counts[direction_id] = actual_counts.get(direction_id, 0) + 1
            actual_topics.setdefault(direction_id, set()).add(int(paper["topic_id"]))
            if paper.get("direction_title") != direction_by_id[direction_id]["title"]:
                raise ResultStoreError(
                    f"Paper direction title does not match opportunities.json: {run_dir}"
                )

        paper_ids = {paper["id"] for paper in papers}
        for direction in directions:
            direction_id = direction["id"]
            if actual_counts.get(direction_id, 0) != direction["paper_count"]:
                raise ResultStoreError(
                    f"Frontier paper count does not match papers.json: {run_dir}"
                )
            if actual_topics.get(direction_id, set()) != set(direction["topic_ids"]):
                raise ResultStoreError(
                    f"Frontier topic coverage does not match papers.json: {run_dir}"
                )
            if any(
                paper.get("id") not in paper_ids
                for paper in direction["representative_papers"]
            ):
                raise ResultStoreError(
                    f"Unknown representative paper in opportunities.json: {run_dir}"
                )

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
                    "direction_id": paper.get("direction_id"),
                    "direction_title": paper.get("direction_title"),
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

    @staticmethod
    def _opportunity_view(
        opportunities: Dict[str, Any], papers: Iterable[Dict[str, Any]]
    ) -> Dict[str, Any]:
        selected_papers = list(papers)
        view = {
            key: value
            for key, value in opportunities.items()
            if key != "directions"
        }
        directions = []
        for direction in opportunities.get("directions", []):
            direction_papers = [
                paper
                for paper in selected_papers
                if paper.get("direction_id") == direction["id"]
            ]
            conference_counts = {
                conference: sum(
                    paper["conference"] == conference
                    for paper in direction_papers
                )
                for conference in sorted(
                    {paper["conference"] for paper in direction_papers}
                )
            }
            directions.append(
                {
                    **direction,
                    "filtered_paper_count": len(direction_papers),
                    "filtered_conference_counts": conference_counts,
                }
            )
        view["directions"] = directions
        return view
