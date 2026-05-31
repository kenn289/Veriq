"""Execution package: pluggable test executors.

This package provides a `TestExecutor` interface and a small local
executor implementation used for synchronous, local test execution in
production-ready deployments where a simple runner is sufficient.
"""

from .executor import TestExecutor  # re-export

__all__ = ["TestExecutor"]
