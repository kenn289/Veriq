from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeTestGenerationConfig:
    # When None, the global Settings or environment variables are used.
    test_generation_provider: str | None = None
    llm_model_name: str | None = None
    llm_adapter_dir: str | None = None
    generation_defaults: dict[str, Any] = field(default_factory=dict)


# Module-level runtime config instance (mutable during process lifetime)
_runtime_config = RuntimeTestGenerationConfig()


def get_runtime_config() -> RuntimeTestGenerationConfig:
    return _runtime_config


def set_runtime_config(**kwargs) -> None:
    for k, v in kwargs.items():
        if hasattr(_runtime_config, k):
            setattr(_runtime_config, k, v)


def persist_runtime_to_env(updates: dict) -> None:
    """Persist selected runtime values into a .env file as VERIQ_ env vars.

    This performs a best-effort update: existing keys are replaced, new keys
    are appended. Non-VERIQ entries are preserved.
    """
    import json
    from pathlib import Path

    env_map = {
        "test_generation_provider": "VERIQ_TEST_GENERATION_PROVIDER",
        "llm_model_name": "VERIQ_LLM_MODEL_NAME",
        "llm_adapter_dir": "VERIQ_LLM_ADAPTER_DIR",
        "generation_defaults": "VERIQ_GENERATION_DEFAULTS",
    }

    env_path = Path.cwd() / ".env"
    lines = []
    existing = {}
    if env_path.exists():
        text = env_path.read_text(encoding="utf-8")
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in line:
                lines.append(line)
                continue
            key, val = line.split("=", 1)
            existing[key] = val
            lines.append(line)

    # Apply updates
    for k, v in updates.items():
        if k not in env_map:
            continue
        env_key = env_map[k]
        if v is None:
            # remove key if present
            if env_key in existing:
                existing.pop(env_key, None)
        else:
            # dump dicts as JSON strings
            if isinstance(v, (dict, list)):
                existing[env_key] = json.dumps(v, ensure_ascii=False)
            else:
                existing[env_key] = str(v)

    # Rebuild lines: keep original non-key lines, replace/add env_map keys
    out_lines = []
    seen = set()
    for line in lines:
        if not line or line.strip().startswith("#") or "=" not in line:
            out_lines.append(line)
            continue
        key, _ = line.split("=", 1)
        if key in existing and key in env_map.values():
            out_lines.append(f"{key}={existing[key]}")
            seen.add(key)
        else:
            out_lines.append(line)

    # Append any missing keys
    for k, v in existing.items():
        if k in seen:
            continue
        out_lines.append(f"{k}={v}")

    env_path.write_text(
        "\n".join(out_lines) + ("\n" if out_lines else ""), encoding="utf-8"
    )
