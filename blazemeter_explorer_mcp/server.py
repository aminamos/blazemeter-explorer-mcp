"""A deliberately narrow, spec-driven MCP server for BlazeMeter's API explorer."""

from __future__ import annotations

import base64
import os
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from .catalog import MUTATING_METHODS, operation_by_id, operation_details, operations


API_BASE_URL = "https://a.blazemeter.com/api/v4"
mcp = FastMCP("BlazeMeter Explorer")


def _authorization_header() -> str:
    key_id = os.environ.get("BLAZEMETER_API_KEY_ID")
    secret = os.environ.get("BLAZEMETER_API_KEY_SECRET")
    if not key_id or not secret:
        raise ValueError(
            "Set BLAZEMETER_API_KEY_ID and BLAZEMETER_API_KEY_SECRET. "
            "Credentials are never accepted as tool arguments."
        )
    token = base64.b64encode(f"{key_id}:{secret}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _render_path(template: str, path_params: dict[str, Any]) -> str:
    rendered = template
    for name, value in path_params.items():
        rendered = rendered.replace("{" + name + "}", str(value))
    if "{" in rendered or "}" in rendered:
        raise ValueError(f"Missing path parameter for {template}")
    return rendered


@mcp.tool()
def list_operations() -> list[dict[str, Any]]:
    """List all operations in the checked-in public BlazeMeter v4 explorer spec."""
    return operations()


@mcp.tool()
def get_operation(operation_id: str) -> dict[str, Any]:
    """Get parameters and response schemas for one public explorer operation."""
    return operation_details(operation_id)


@mcp.tool()
async def invoke_operation(
    operation_id: str,
    path_params: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | list[Any] | str | None = None,
    confirm: bool = False,
) -> dict[str, Any]:
    """Call one documented explorer operation. Writes require explicit confirm=true."""
    method, path_template, _ = operation_by_id(operation_id)
    if method.lower() in MUTATING_METHODS and not confirm:
        return {
            "error": "This is a mutating operation. Review get_operation output, then retry with confirm=true.",
            "operation_id": operation_id,
        }

    path = _render_path(path_template, path_params or {})
    headers = {"Authorization": _authorization_header(), "Accept": "application/json"}
    request_kwargs: dict[str, Any] = {"params": query or {}, "headers": headers}
    if body is not None:
        request_kwargs["json"] = body

    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0, http2=True) as client:
        response = await client.request(method, path, **request_kwargs)

    content_type = response.headers.get("content-type", "")
    payload: Any = response.json() if "json" in content_type.lower() else response.text
    return {
        "operation_id": operation_id,
        "status_code": response.status_code,
        "ok": response.is_success,
        "result": payload.get("result", payload) if isinstance(payload, dict) else payload,
        "error": payload.get("error") if isinstance(payload, dict) else None,
    }


def main() -> None:
    mcp.run(transport="stdio")
