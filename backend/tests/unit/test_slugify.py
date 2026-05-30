from __future__ import annotations

from veriq.application.utils.slug import slugify


def test_slugify() -> None:
    """Description: Validate slug generation.
    Parameters:
        None
    Returns:
        None
    Usage Example:
        test_slugify()
    """

    assert slugify("QA Workspace") == "qa-workspace"
    assert slugify("  Multi  Space  ") == "multi-space"
    assert slugify("Symbols!@#") == "symbols"
