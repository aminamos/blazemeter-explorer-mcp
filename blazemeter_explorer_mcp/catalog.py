"""Load and query the checked-in public BlazeMeter explorer specification."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


SPEC_PATH = Path(__file__).resolve().parents[1] / "openapi" / "blazemeter-v4-explorer.swagger.json"
MUTATING_METHODS = frozenset({"delete", "patch", "post", "put"})


@lru_cache(maxsize=1)
def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def operations() -> list[dict[str, Any]]:
    """Return a compact catalog that is useful to an MCP client."""
    result = []
    for path, methods in load_spec()["paths"].items():
        for method, operation in methods.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete"}:
                continue
            result.append(
                {
                    "operation_id": operation["operationId"],
                    "method": method.upper(),
                    "path": path,
                    "summary": operation.get("summary", ""),
                    "mutating": method.lower() in MUTATING_METHODS,
                }
            )
    return sorted(result, key=lambda item: item["operation_id"])


def operation_by_id(operation_id: str) -> tuple[str, str, dict[str, Any]]:
    for path, methods in load_spec()["paths"].items():
        for method, operation in methods.items():
            if isinstance(operation, dict) and operation.get("operationId") == operation_id:
                return method.upper(), path, operation
    raise ValueError(f"Unknown operation_id: {operation_id}")


def operation_details(operation_id: str) -> dict[str, Any]:
    method, path, operation = operation_by_id(operation_id)
    return {
        "operation_id": operation_id,
        "method": method,
        "path": path,
        "summary": operation.get("summary", ""),
        "description": operation.get("description", ""),
        "mutating": method.lower() in MUTATING_METHODS,
        "parameters": operation.get("parameters", []),
        "responses": operation.get("responses", {}),
    }
