"""FastAPI application for the AI Paper Trends result dashboard."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.cloud_ai import (
    CloudAIConfig,
    DirectionUpdateService,
    LearningPlanService,
    create_cloud_client,
    load_cloud_config,
)
from src.cloud_ai.client import CloudAIClient
from src.paper_analysis import PaperAnalysisService, PaperDocumentService
from src.paper_sources import FetchedDocument, PaperPullService
from src.storage import LocalDatabase
from web.result_store import ResultStore, ResultStoreError
from web.routes.workbench import create_workbench_router


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent


def create_app(
    data_root: Optional[Path] = None,
    *,
    local_root: Optional[Path] = None,
    cloud_config: Optional[CloudAIConfig] = None,
    cloud_client: Optional[CloudAIClient] = None,
    paper_fetch: Optional[Callable[[str], FetchedDocument]] = None,
    paper_document_fetch: Optional[Callable[[str], FetchedDocument]] = None,
    initialize_immediately: bool = True,
) -> FastAPI:
    """Create the dashboard and its local ingestion/learning workbench."""
    resolved_data_root = data_root or Path(
        os.getenv("AI_PAPER_WEB_DATA", PROJECT_ROOT / "data" / "web")
    )
    store = ResultStore(resolved_data_root)
    resolved_local_root = local_root or Path(
        os.getenv("AI_PAPER_LOCAL_DATA", PROJECT_ROOT / "data" / "local")
    )
    database = LocalDatabase(resolved_local_root / "app.db")
    initialized = False

    def initialize_local_state() -> None:
        nonlocal initialized
        if initialized:
            return
        database.initialize()
        for run in store.list_runs():
            database.seed_papers(store.get_snapshot(run["run_id"]).papers)
        initialized = True
    config = cloud_config or load_cloud_config(PROJECT_ROOT / "settings" / "cloud_ai.yaml")
    client = cloud_client or create_cloud_client(config)
    pull_service = PaperPullService(
        database, resolved_local_root / "artifacts", fetch=paper_fetch
    )
    document_service = PaperDocumentService(
        database,
        resolved_local_root / "artifacts",
        fetch=paper_document_fetch,
    )
    learning_service = LearningPlanService(database, store, client, config)
    direction_update_service = DirectionUpdateService(database, store, client, config)
    paper_analysis_service = PaperAnalysisService(
        database, store, document_service, client, config
    )
    app = FastAPI(
        title="AI Paper Trends Dashboard",
        description="Local paper-ingestion, frontier-analysis, and learning workbench.",
        version="2.0.0",
    )
    app.state.result_store = store
    app.state.local_database = database
    app.state.cloud_config = config
    app.state.paper_pull_service = pull_service
    app.state.learning_plan_service = learning_service
    app.state.direction_update_service = direction_update_service
    app.state.paper_document_service = document_service
    app.state.paper_analysis_service = paper_analysis_service
    if initialize_immediately:
        initialize_local_state()
    else:
        app.add_event_handler("startup", initialize_local_state)
    app.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")
    app.include_router(create_workbench_router())
    templates = Jinja2Templates(directory=WEB_ROOT / "templates")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/api/health")
    async def health() -> dict:
        return {
            "status": "ok",
            "run_count": len(store.list_runs()),
            "cloud_provider": config.provider,
        }

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
        direction: Optional[str] = None,
        topic: Optional[str] = None,
        decision: Optional[str] = None,
        q: Optional[str] = None,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        sort: str = Query("title", pattern="^(title|conference|topic)$"),
    ) -> dict:
        try:
            return store.query_papers(
                run_id,
                conference=conference,
                direction=direction,
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


app = create_app(initialize_immediately=False)
