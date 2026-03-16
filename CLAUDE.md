# Linode MCP Server

MCP server for managing Linode/Akamai Compute infrastructure via natural language.

## Quick Start

```bash
uv sync
export LINODE_API_TOKEN="your-token"
claude mcp add linode -- uv run python server.py
```

## Architecture

- `server.py` — Entry point. Creates FastMCP server, registers all tools, runs stdio transport.
- `linode_mcp/client.py` — `LinodeClient`: synchronous httpx wrapper for Linode API v4. All HTTP errors return dicts (never raises to MCP layer).
- `linode_mcp/tools/` — One module per resource group. Each exports `register(mcp, client)`.

## Tool Naming Convention

`{verb}_{resource}` — verbs: list, get, create, update, delete, boot, reboot, shutdown, resize, attach, detach.

## Key Patterns

- Tools use `@mcp.tool()` with `pydantic.Field()` for parameter descriptions
- Optional params default to `None`, only included in API body when provided
- Tools return raw API response dicts
- HTTP errors return `{"error": True, "status": <code>, "message": "..."}`, not exceptions
- 204 responses return `{"success": True}`

## Dependencies

- `mcp[cli]` — FastMCP framework
- `httpx` — HTTP client for Linode API
- `pydantic` — Parameter validation and descriptions
