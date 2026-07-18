"""Write APIs for paper ingestion and AI-guided learning workflows."""

from __future__ import annotations

import os
from typing import Literal, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, status
from pydantic import AnyHttpUrl, BaseModel, Field

from src.cloud_ai.schemas import LEARNING_ARTIFACT_VERSION


class PaperPullRequest(BaseModel):
    url: AnyHttpUrl
    conference: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1950, le=2100)
    parser: Literal["auto", "json", "html", "acl"] = "auto"
    download_pdf: bool = False
    remember_source: bool = True


class LearningPlanRequest(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    direction_id: str = Field(min_length=1, max_length=120)
    duration_days: Literal[7, 30, 90] = 30
    language: Literal["zh-CN", "en-US"] = "zh-CN"
    experience_level: Literal["zero", "beginner", "intermediate", "advanced"] = "intermediate"
    weekly_hours: int = Field(default=10, ge=1, le=80)
    compute_profile: Literal[
        "cpu_only", "single_gpu_or_cpu", "multi_gpu", "cloud_flexible"
    ] = "single_gpu_or_cpu"


class DirectionUpdateRequest(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    paper_limit: int = Field(default=50, ge=1, le=200)
    language: Literal["zh-CN", "en-US"] = "zh-CN"


class ProgressRequest(BaseModel):
    status: Literal["todo", "doing", "done", "blocked"]
    notes: str = Field(default="", max_length=3000)
    actual_hours: Optional[float] = Field(default=None, ge=0, le=10000)


def create_workbench_router() -> APIRouter:
    router = APIRouter(prefix="/api")

    @router.get("/cloud/status")
    async def cloud_status(request: Request) -> dict:
        config = request.app.state.cloud_config
        configured = config.provider == "mock" or bool(os.getenv(config.api_key_env))
        return {
            "provider": config.provider,
            "model": config.model,
            "configured": configured,
            "api_key_env": config.api_key_env,
            "prompt_version": config.prompt_version,
            "learning_artifact_version": LEARNING_ARTIFACT_VERSION,
        }

    @router.post("/paper-pulls", status_code=status.HTTP_202_ACCEPTED)
    async def create_paper_pull(
        payload: PaperPullRequest,
        background_tasks: BackgroundTasks,
        request: Request,
    ) -> dict:
        service = request.app.state.paper_pull_service
        values = payload.model_dump(mode="json")
        created = service.create_job(values)
        background_tasks.add_task(
            service.run_job, created["job_id"], created["source_id"]
        )
        return created

    @router.post(
        "/paper-sources/{source_id}/pull", status_code=status.HTTP_202_ACCEPTED
    )
    async def pull_saved_source(
        source_id: str,
        background_tasks: BackgroundTasks,
        request: Request,
    ) -> dict:
        service = request.app.state.paper_pull_service
        try:
            job_id = service.create_job_for_source(source_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        background_tasks.add_task(service.run_job, job_id, source_id)
        return {"source_id": source_id, "job_id": job_id}

    @router.get("/paper-sources")
    async def list_paper_sources(request: Request) -> dict:
        return {"items": request.app.state.local_database.list_sources()}

    @router.get("/local/papers")
    async def list_local_papers(
        request: Request, limit: int = Query(50, ge=1, le=500)
    ) -> dict:
        papers = request.app.state.local_database.list_local_papers(limit)
        return {
            "items": papers,
            "count": request.app.state.local_database.count_papers(),
        }

    @router.get("/jobs/{job_id}")
    async def get_job(job_id: str, request: Request) -> dict:
        try:
            return request.app.state.local_database.get_job(job_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @router.post("/direction-updates", status_code=status.HTTP_202_ACCEPTED)
    async def create_direction_update(
        payload: DirectionUpdateRequest,
        background_tasks: BackgroundTasks,
        request: Request,
    ) -> dict:
        values = payload.model_dump(mode="json")
        service = request.app.state.direction_update_service
        job_id = service.create_job(values)
        background_tasks.add_task(service.run_job, job_id, values)
        return {"job_id": job_id}

    @router.get("/direction-updates")
    async def list_direction_updates(
        request: Request, limit: int = Query(20, ge=1, le=100)
    ) -> dict:
        items = request.app.state.local_database.list_direction_updates(limit)
        return {"items": items}

    @router.post("/learning/plans", status_code=status.HTTP_202_ACCEPTED)
    async def create_learning_plan(
        payload: LearningPlanRequest,
        background_tasks: BackgroundTasks,
        request: Request,
    ) -> dict:
        values = payload.model_dump(mode="json")
        service = request.app.state.learning_plan_service
        job_id = service.create_job(values)
        background_tasks.add_task(service.run_job, job_id, values)
        return {"job_id": job_id}

    @router.get("/learning/plans/{plan_id}")
    async def get_learning_plan(plan_id: str, request: Request) -> dict:
        try:
            return request.app.state.local_database.get_learning_plan(plan_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    @router.patch("/learning/plans/{plan_id}/tasks/{task_id}")
    async def update_learning_progress(
        plan_id: str,
        task_id: str,
        payload: ProgressRequest,
        request: Request,
    ) -> dict:
        try:
            request.app.state.local_database.update_learning_progress(
                plan_id,
                task_id,
                status=payload.status,
                notes=payload.notes,
                actual_hours=payload.actual_hours,
            )
            return request.app.state.local_database.get_learning_plan(plan_id)
        except KeyError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error

    return router
