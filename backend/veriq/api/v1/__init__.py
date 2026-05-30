"""API v1 router registration."""

from fastapi import APIRouter

from veriq.api.v1.routes import auth, health, organizations, projects, workspaces
from veriq.api.v1.routes import test_cases, test_runs

router = APIRouter()
router.include_router(health.router)
router.include_router(auth.router)
router.include_router(organizations.router)
router.include_router(workspaces.router)
router.include_router(projects.router)
router.include_router(test_cases.router)
router.include_router(test_runs.router)
