"""FastAPI application for the AI Paper Trends result dashboard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web.result_store import ResultStore, ResultStoreError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent


def create_app(data_root: Optional[Path] = None) -> FastAPI:
    """Create a dashboard app for the supplied exported-data directory."""
    resolved_data_root = data_root or Path(
        os.getenv("AI_PAPER_WEB_DATA", PROJECT_ROOT / "data" / "web")
    )
    store = ResultStore(resolved_data_root)
    app = FastAPI(
        title="AI Paper Trends Dashboard",
        description="Read-only explorer for public conference-paper samples.",
        version="1.0.0",
    )
    app.state.result_store = store
    app.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")
    templates = Jinja2Templates(directory=WEB_ROOT / "templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/health")
    async def health() -> dict:
        return {"status": "ok", "run_count": len(store.list_runs())}

    @app.get("/api/runs")
    async def runs() -> dict:
        return {"items": store.list_runs()}

    @app.get("/api/runs/{run_id}/dashboard")
    async def dashboard(run_id: str, conference: Optional[str] = None) -> dict:
        try:
            return store.dashboard(run_id, conference=conference)
        except ResultStoreError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/papers")
    async def papers(
        run_id: str,
        conference: Optional[str] = None,
        topic: Optional[str] = None,
        decision: Optional[str] = None,
        q: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        sort: str = Query("title", pattern="^(title|conference|topic|rating)$"),
    ) -> dict:
        try:
            return store.query_papers(
                run_id,
                conference=conference,
                topic=topic,
                decision=decision,
                query=q,
                page=page,
                page_size=page_size,
                sort=sort,
            )
        except ResultStoreError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @app.get("/api/runs/{run_id}/papers/{paper_id}")
    async def paper_detail(run_id: str, paper_id: str) -> dict:
        try:
            return store.get_paper(run_id, paper_id)
        except ResultStoreError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return app


app = create_app()
