from __future__ import annotations

import re


def slugify(value: str) -> str:
    """Description: Convert a string into a URL-safe slug.
    Parameters:
        value: Input string.
    Returns:
        str: Slugified string.
    Usage Example:
        slug = slugify("QA Workspace")
    """

    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9\s-]", "", normalized)
    normalized = re.sub(r"[\s-]+", "-", normalized)
    return normalized.strip("-")
