"""API v1 router registration."""

from fastapi import APIRouter

from veriq.api.v1.routes import (
    ai_config,
    auth,
    executions,
    health,
    organizations,
    projects,
    test_cases,
    test_generation,
    test_runs,
    workspaces,
)

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(organizations.router)
router.include_router(workspaces.router)
router.include_router(projects.router)
router.include_router(test_cases.router)
router.include_router(test_generation.router)
router.include_router(ai_config.router)
router.include_router(test_runs.router)
router.include_router(executions.router)
