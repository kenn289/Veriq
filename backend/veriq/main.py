from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from veriq.api.v1 import router as v1_router
from veriq.infrastructure.config.settings import get_settings
from veriq.infrastructure.db.seed import seed_roles
from veriq.infrastructure.db.session import get_session_factory


def create_app(seed_roles_on_startup: bool | None = None) -> FastAPI:
    """Description: Build the FastAPI application.
    Parameters:
        seed_roles_on_startup: Optional override for role seeding.
    Returns:
        FastAPI: Configured application instance.
    Usage Example:
        app = create_app(seed_roles_on_startup=False)
    """

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Veriq API for autonomous test engineering.",
    )

    # CORS
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root() -> dict[str, str]:
        """Description: Provide a friendly API root response.
        Parameters:
            None
        Returns:
            dict[str, str]: API entry point guidance.
        Usage Example:
            GET /
        """

        return {
            "message": "Veriq API is running",
            "health": "/api/v1/health",
            "version": "/api/v1/version",
            "docs": "/docs",
        }

    @app.on_event("startup")
    def _startup() -> None:
        """Description: Run startup hooks for database seeding.
        Parameters:
            None
        Returns:
            None
        Usage Example:
            _startup()
        """

        should_seed = (
            settings.seed_roles_on_startup
            if seed_roles_on_startup is None
            else seed_roles_on_startup
        )
        if not should_seed:
            return

        session_factory = get_session_factory()
        session = session_factory()
        try:
            seed_roles(session)
        finally:
            session.close()

    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()
