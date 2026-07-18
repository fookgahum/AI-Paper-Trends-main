"""Shared runtime helpers for observable cloud-AI jobs."""

from __future__ import annotations

from threading import Event, Thread
from typing import Callable, TypeVar

from src.storage import LocalDatabase


ResultT = TypeVar("ResultT")


def run_with_heartbeat(
    database: LocalDatabase,
    job_id: str,
    stage: str,
    operation: Callable[[], ResultT],
    *,
    progress_current: int = 1,
    progress_total: int = 4,
) -> ResultT:
    """Run a blocking model call while keeping its job heartbeat fresh."""
    stop = Event()

    def refresh() -> None:
        while not stop.wait(10):
            try:
                database.update_job(
                    job_id,
                    status="running",
                    stage=stage,
                    progress_current=progress_current,
                    progress_total=progress_total,
                )
            except KeyError:
                return

    heartbeat = Thread(target=refresh, daemon=True)
    heartbeat.start()
    try:
        return operation()
    finally:
        stop.set()
        heartbeat.join(timeout=1)
