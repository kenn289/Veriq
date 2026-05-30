from __future__ import annotations

from fastapi import APIRouter, Body
from pydantic import BaseModel

from veriq.infrastructure.config.runtime import (
    get_runtime_config,
    persist_runtime_to_env,
    set_runtime_config,
)

router = APIRouter(prefix="/ai", tags=["ai-config"])


class RuntimeConfigRequest(BaseModel):
    test_generation_provider: str | None = None
    llm_model_name: str | None = None
    llm_adapter_dir: str | None = None
    generation_defaults: dict | None = None


class RuntimeConfigResponse(BaseModel):
    test_generation_provider: str | None = None
    llm_model_name: str | None = None
    llm_adapter_dir: str | None = None
    generation_defaults: dict | None = None


@router.get("/config", response_model=RuntimeConfigResponse)
def get_config() -> RuntimeConfigResponse:
    runtime = get_runtime_config()
    # Fall back to global Settings when runtime value not explicitly set
    from veriq.infrastructure.config.settings import get_settings

    settings = get_settings()
    return RuntimeConfigResponse(
        test_generation_provider=runtime.test_generation_provider
        or settings.test_generation_provider,
        llm_model_name=runtime.llm_model_name or settings.llm_model_name,
        llm_adapter_dir=runtime.llm_adapter_dir or settings.llm_adapter_dir,
        generation_defaults=runtime.generation_defaults or settings.generation_defaults,
    )


@router.post("/config", response_model=RuntimeConfigResponse)
def update_config(payload: RuntimeConfigRequest = Body(...)) -> RuntimeConfigResponse:
    # Only update provided fields
    updates: dict = {}
    if payload.test_generation_provider is not None:
        updates["test_generation_provider"] = payload.test_generation_provider
    if payload.llm_model_name is not None:
        updates["llm_model_name"] = payload.llm_model_name
    if payload.llm_adapter_dir is not None:
        updates["llm_adapter_dir"] = payload.llm_adapter_dir
    if payload.generation_defaults is not None:
        updates["generation_defaults"] = payload.generation_defaults

    set_runtime_config(**updates)
    # Persist to .env so changes survive restarts (best-effort)
    try:
        persist_runtime_to_env(updates)
        # Clear cached Settings so subsequent reads pick up the .env changes
        from veriq.infrastructure.config.settings import get_settings

        try:
            get_settings.cache_clear()
        except Exception:
            pass
    except Exception:
        # Non-fatal: persistence failures shouldn't block the API
        pass
    runtime = get_runtime_config()
    return RuntimeConfigResponse(
        test_generation_provider=runtime.test_generation_provider,
        llm_model_name=runtime.llm_model_name,
        llm_adapter_dir=runtime.llm_adapter_dir,
        generation_defaults=runtime.generation_defaults,
    )
