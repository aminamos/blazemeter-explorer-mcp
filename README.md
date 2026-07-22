# BlazeMeter Explorer MCP

An MCP server for the public Swagger document served by [BlazeMeter's API v4 explorer](https://a.blazemeter.com/api/v4/explorer/). It is a companion to, not a replacement for, the official [BlazeMeter MCP](https://github.com/Blazemeter/bzm-mcp).

## Why this exists

The official server is an opinionated performance-testing workflow layer: its nine tool groups cover accounts, billing, executions, help, projects, skills, tests, users, and workspaces. The public explorer is a different, smaller API surface: 54 operations across 49 paths, mainly user/session, vault settings, RSS feed, static frontend asset, and CSP-report routes. It does not document the official server's core `/accounts`, `/workspaces`, `/projects`, `/tests`, or `/masters` operations.

This server makes that explorer surface queryable without pretending that its documentation is a complete BlazeMeter API reference.

## Install

```json
{
  "mcpServers": {
    "blazemeter-explorer": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/aminamos/blazemeter-explorer-mcp.git", "blazemeter-explorer-mcp"],
      "env": {
        "BLAZEMETER_API_KEY_ID": "your-key-id",
        "BLAZEMETER_API_KEY_SECRET": "your-key-secret"
      }
    }
  }
}
```

The server reads credentials only from environment variables and sends them as HTTP Basic authentication, matching BlazeMeter's official MCP convention. Do not put credentials in prompts or tool arguments.

## Tools

- `list_operations`: compact catalog of the checked-in OpenAPI operations.
- `get_operation`: full parameter and response metadata for an `operation_id`.
- `invoke_operation`: executes one documented operation. POST, PUT, PATCH, and DELETE calls return a confirmation response until `confirm=true` is supplied.

## Spec provenance and refresh

`openapi/blazemeter-v4-explorer.swagger.json` was retrieved from `https://a.blazemeter.com/api/v4/explorer/swagger.json` on 2026-07-22. It is checked in so clients have a reviewable, reproducible catalog. Refresh it with:

```powershell
Invoke-WebRequest https://a.blazemeter.com/api/v4/explorer/swagger.json -OutFile openapi/blazemeter-v4-explorer.swagger.json
```

Review the diff before committing a refresh: the public explorer can change independently from the official MCP.

## Comparison

| Aspect | Official `Blazemeter/bzm-mcp` | This companion |
| --- | --- | --- |
| Source of truth | Curated Python workflow implementation | Public explorer Swagger document |
| Shape | Nine high-level, domain-specific tool groups | Three generic spec discovery/invocation tools |
| Core load testing | Creates/configures/tests/runs/analyzes reports | Not documented in this Swagger document |
| Explorer-only value | No direct surface for these operations | Vault settings, BZM session inactivity, user UI messages, RSS feeds, static asset and CSP routes |
| Write safety | Official server has its own confirmation mode | Explicit `confirm=true` required for all mutating HTTP methods |

## Development

```powershell
uv sync --group dev
uv run pytest
```

This is an independent, unofficial project. BlazeMeter names and APIs belong to their respective owners.
