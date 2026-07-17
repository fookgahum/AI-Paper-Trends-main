"""SQLite-backed state for local paper ingestion and AI learning tasks."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LocalDatabase:
    """Own the local SQLite schema and its small set of application queries."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = RLock()

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;
                PRAGMA foreign_keys = ON;

                CREATE TABLE IF NOT EXISTS paper_sources (
                    id TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    conference TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    parser_type TEXT NOT NULL,
                    download_pdf INTEGER NOT NULL DEFAULT 0,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_pulled_at TEXT
                );

                CREATE TABLE IF NOT EXISTS papers (
                    id TEXT PRIMARY KEY,
                    official_id TEXT,
                    conference TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    abstract TEXT NOT NULL,
                    authors_json TEXT NOT NULL,
                    keywords_json TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    pdf_url TEXT,
                    code_urls_json TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    analysis_status TEXT NOT NULL DEFAULT 'unanalysed',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS papers_source_url_idx
                    ON papers(source_url);
                CREATE INDEX IF NOT EXISTS papers_title_year_idx
                    ON papers(title, year);

                CREATE TABLE IF NOT EXISTS paper_source_links (
                    paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
                    source_id TEXT NOT NULL REFERENCES paper_sources(id) ON DELETE CASCADE,
                    PRIMARY KEY (paper_id, source_id)
                );

                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    progress_current INTEGER NOT NULL DEFAULT 0,
                    progress_total INTEGER NOT NULL DEFAULT 0,
                    heartbeat_at TEXT NOT NULL,
                    input_json TEXT NOT NULL,
                    result_json TEXT,
                    error_json TEXT,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    finished_at TEXT
                );

                CREATE TABLE IF NOT EXISTS learning_plans (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    direction_id TEXT NOT NULL,
                    direction_version TEXT NOT NULL,
                    duration_days INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    paper_cutoff TEXT,
                    artifact_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS learning_progress (
                    plan_id TEXT NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
                    task_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    notes TEXT NOT NULL DEFAULT '',
                    actual_hours REAL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (plan_id, task_id)
                );

                CREATE TABLE IF NOT EXISTS direction_updates (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    run_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt_version TEXT NOT NULL,
                    artifact_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usage_records (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL REFERENCES jobs(id),
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    request_key TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL,
                    cached INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def seed_papers(self, papers: Iterable[Dict[str, Any]]) -> int:
        rows = list(papers)
        if not rows:
            return 0
        inserted = 0
        with self._lock, self._connect() as connection:
            for paper in rows:
                content_hash = self._paper_hash_payload(paper)
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO papers (
                        id, official_id, conference, year, title, abstract,
                        authors_json, keywords_json, decision, source_url,
                        pdf_url, code_urls_json, content_hash, analysis_status,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        paper["id"],
                        paper.get("official_id") or paper["id"],
                        paper["conference"],
                        int(paper["year"]),
                        paper["title"],
                        paper["abstract"],
                        json.dumps(paper.get("authors", []), ensure_ascii=False),
                        json.dumps(paper.get("keywords", []), ensure_ascii=False),
                        paper.get("decision") or "Published",
                        paper["source_url"],
                        paper.get("pdf_url"),
                        json.dumps(paper.get("code_urls", []), ensure_ascii=False),
                        content_hash,
                        "analysed" if paper.get("direction_id") else "unanalysed",
                        _utc_now(),
                        _utc_now(),
                    ),
                )
                inserted += cursor.rowcount
        return inserted

    def create_source(self, payload: Dict[str, Any]) -> str:
        source_id = f"source_{uuid4().hex}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO paper_sources (
                    id, url, conference, year, parser_type, download_pdf,
                    enabled, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    payload["url"],
                    payload["conference"],
                    int(payload["year"]),
                    payload.get("parser", "auto"),
                    int(bool(payload.get("download_pdf", False))),
                    int(bool(payload.get("remember_source", True))),
                    _utc_now(),
                ),
            )
        return source_id

    def get_source(self, source_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM paper_sources WHERE id = ?", (source_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown paper source: {source_id}")
        return dict(row)

    def list_sources(self) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM paper_sources WHERE enabled = 1 ORDER BY created_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def mark_source_pulled(self, source_id: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "UPDATE paper_sources SET last_pulled_at = ? WHERE id = ?",
                (_utc_now(), source_id),
            )

    def upsert_papers(
        self, papers: Iterable[Dict[str, Any]], source_id: str
    ) -> Dict[str, int]:
        counts = {"new": 0, "updated": 0, "duplicate": 0}
        with self._lock, self._connect() as connection:
            for paper in papers:
                existing = connection.execute(
                    "SELECT id, content_hash FROM papers WHERE id = ? OR source_url = ?",
                    (paper["id"], paper["source_url"]),
                ).fetchone()
                content_hash = self._paper_hash_payload(paper)
                if existing is None:
                    connection.execute(
                        """
                        INSERT INTO papers (
                            id, official_id, conference, year, title, abstract,
                            authors_json, keywords_json, decision, source_url,
                            pdf_url, code_urls_json, content_hash, analysis_status,
                            created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'unanalysed', ?, ?)
                        """,
                        (
                            paper["id"],
                            paper.get("official_id"),
                            paper["conference"],
                            int(paper["year"]),
                            paper["title"],
                            paper["abstract"],
                            json.dumps(paper.get("authors", []), ensure_ascii=False),
                            json.dumps(paper.get("keywords", []), ensure_ascii=False),
                            paper.get("decision") or "Published",
                            paper["source_url"],
                            paper.get("pdf_url"),
                            json.dumps(paper.get("code_urls", []), ensure_ascii=False),
                            content_hash,
                            _utc_now(),
                            _utc_now(),
                        ),
                    )
                    paper_id = paper["id"]
                    counts["new"] += 1
                else:
                    paper_id = existing["id"]
                    if existing["content_hash"] == content_hash:
                        counts["duplicate"] += 1
                    else:
                        connection.execute(
                            """
                            UPDATE papers SET title = ?, abstract = ?, authors_json = ?,
                                keywords_json = ?, decision = ?, pdf_url = ?,
                                code_urls_json = ?, content_hash = ?, updated_at = ?,
                                analysis_status = 'unanalysed'
                            WHERE id = ?
                            """,
                            (
                                paper["title"],
                                paper["abstract"],
                                json.dumps(paper.get("authors", []), ensure_ascii=False),
                                json.dumps(paper.get("keywords", []), ensure_ascii=False),
                                paper.get("decision") or "Published",
                                paper.get("pdf_url"),
                                json.dumps(paper.get("code_urls", []), ensure_ascii=False),
                                content_hash,
                                _utc_now(),
                                paper_id,
                            ),
                        )
                        counts["updated"] += 1
                connection.execute(
                    "INSERT OR IGNORE INTO paper_source_links (paper_id, source_id) VALUES (?, ?)",
                    (paper_id, source_id),
                )
        return counts

    def list_local_papers(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, conference, year, title, abstract, authors_json,
                       keywords_json, decision, source_url, pdf_url,
                       code_urls_json, analysis_status, updated_at
                FROM papers ORDER BY updated_at DESC, title LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._decode_paper(row) for row in rows]

    def count_papers(self) -> int:
        with self._connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM papers").fetchone()
        return int(row["count"])

    def list_unanalysed_papers(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, conference, year, title, abstract, authors_json,
                       keywords_json, decision, source_url, pdf_url,
                       code_urls_json, analysis_status, updated_at
                FROM papers WHERE analysis_status = 'unanalysed'
                ORDER BY updated_at, title LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._decode_paper(row) for row in rows]

    def mark_papers_analysed(self, paper_ids: Iterable[str]) -> None:
        ids = list(paper_ids)
        if not ids:
            return
        placeholders = ",".join("?" for _ in ids)
        with self._connect() as connection:
            connection.execute(
                f"UPDATE papers SET analysis_status = 'analysed' WHERE id IN ({placeholders})",
                ids,
            )

    def create_job(self, job_type: str, payload: Dict[str, Any]) -> str:
        job_id = f"job_{uuid4().hex}"
        now = _utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO jobs (
                    id, job_type, status, stage, heartbeat_at, input_json, created_at
                ) VALUES (?, ?, 'queued', 'queued', ?, ?, ?)
                """,
                (job_id, job_type, now, json.dumps(payload, ensure_ascii=False), now),
            )
        return job_id

    def update_job(
        self,
        job_id: str,
        *,
        status: Optional[str] = None,
        stage: Optional[str] = None,
        progress_current: Optional[int] = None,
        progress_total: Optional[int] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None,
    ) -> None:
        assignments = ["heartbeat_at = ?"]
        values: List[Any] = [_utc_now()]
        for column, value in (
            ("status", status),
            ("stage", stage),
            ("progress_current", progress_current),
            ("progress_total", progress_total),
        ):
            if value is not None:
                assignments.append(f"{column} = ?")
                values.append(value)
        if result is not None:
            assignments.append("result_json = ?")
            values.append(json.dumps(result, ensure_ascii=False))
        if error is not None:
            assignments.append("error_json = ?")
            values.append(json.dumps(error, ensure_ascii=False))
        if status == "running":
            assignments.append("started_at = COALESCE(started_at, ?)")
            values.append(_utc_now())
        if status in {"completed", "failed", "cancelled"}:
            assignments.append("finished_at = ?")
            values.append(_utc_now())
        values.append(job_id)
        with self._connect() as connection:
            cursor = connection.execute(
                f"UPDATE jobs SET {', '.join(assignments)} WHERE id = ?", values
            )
        if cursor.rowcount != 1:
            raise KeyError(f"Unknown job: {job_id}")

    def get_job(self, job_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM jobs WHERE id = ?", (job_id,)
            ).fetchone()
        if row is None:
            raise KeyError(f"Unknown job: {job_id}")
        result = dict(row)
        for key in ("input_json", "result_json", "error_json"):
            result[key.removesuffix("_json")] = (
                json.loads(result.pop(key)) if result[key] else None
            )
        return result

    def save_learning_plan(
        self,
        *,
        job_id: str,
        direction_id: str,
        direction_version: str,
        duration_days: int,
        language: str,
        provider: str,
        model: str,
        prompt_version: str,
        paper_cutoff: Optional[str],
        artifact: Dict[str, Any],
    ) -> str:
        plan_id = f"plan_{uuid4().hex}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO learning_plans (
                    id, job_id, direction_id, direction_version, duration_days,
                    language, provider, model, prompt_version, paper_cutoff,
                    artifact_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    job_id,
                    direction_id,
                    direction_version,
                    duration_days,
                    language,
                    provider,
                    model,
                    prompt_version,
                    paper_cutoff,
                    json.dumps(artifact, ensure_ascii=False),
                    _utc_now(),
                ),
            )
        return plan_id

    def get_learning_plan(self, plan_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM learning_plans WHERE id = ?", (plan_id,)
            ).fetchone()
            progress_rows = connection.execute(
                "SELECT * FROM learning_progress WHERE plan_id = ?",
                (plan_id,),
            ).fetchall()
        if row is None:
            raise KeyError(f"Unknown learning plan: {plan_id}")
        result = dict(row)
        result["artifact"] = json.loads(result.pop("artifact_json"))
        result["progress"] = [dict(item) for item in progress_rows]
        return result

    def update_learning_progress(
        self,
        plan_id: str,
        task_id: str,
        *,
        status: str,
        notes: str = "",
        actual_hours: Optional[float] = None,
    ) -> None:
        plan = self.get_learning_plan(plan_id)
        known_tasks = {
            task["id"]
            for stage in plan["artifact"]["stages"]
            for task in stage["tasks"]
        }
        if task_id not in known_tasks:
            raise KeyError(f"Unknown learning task: {task_id}")
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO learning_progress (
                    plan_id, task_id, status, notes, actual_hours, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(plan_id, task_id) DO UPDATE SET
                    status = excluded.status,
                    notes = excluded.notes,
                    actual_hours = excluded.actual_hours,
                    updated_at = excluded.updated_at
                """,
                (plan_id, task_id, status, notes, actual_hours, _utc_now()),
            )

    def record_usage(self, job_id: str, usage: Dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO usage_records (
                    id, job_id, provider, model, request_key, input_tokens,
                    output_tokens, cached, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"usage_{uuid4().hex}",
                    job_id,
                    usage["provider"],
                    usage["model"],
                    usage["request_key"],
                    int(usage.get("input_tokens", 0)),
                    int(usage.get("output_tokens", 0)),
                    int(bool(usage.get("cached", False))),
                    _utc_now(),
                ),
            )

    def save_direction_update(
        self,
        *,
        job_id: str,
        run_id: str,
        provider: str,
        model: str,
        prompt_version: str,
        artifact: Dict[str, Any],
    ) -> str:
        update_id = f"direction_update_{uuid4().hex}"
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO direction_updates (
                    id, job_id, run_id, provider, model, prompt_version,
                    artifact_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    update_id,
                    job_id,
                    run_id,
                    provider,
                    model,
                    prompt_version,
                    json.dumps(artifact, ensure_ascii=False),
                    _utc_now(),
                ),
            )
        return update_id

    def list_direction_updates(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM direction_updates ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        results = []
        for row in rows:
            item = dict(row)
            item["artifact"] = json.loads(item.pop("artifact_json"))
            results.append(item)
        return results

    @contextmanager
    def _connect(self) -> Iterable[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _paper_hash_payload(paper: Dict[str, Any]) -> str:
        import hashlib

        payload = json.dumps(
            {
                "title": paper["title"],
                "abstract": paper["abstract"],
                "authors": paper.get("authors", []),
                "keywords": paper.get("keywords", []),
                "source_url": paper["source_url"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _decode_paper(row: sqlite3.Row) -> Dict[str, Any]:
        paper = dict(row)
        paper["authors"] = json.loads(paper.pop("authors_json"))
        paper["keywords"] = json.loads(paper.pop("keywords_json"))
        paper["code_urls"] = json.loads(paper.pop("code_urls_json"))
        return paper
