from mcp.server.fastmcp import FastMCP

from linode_mcp.client import LinodeClient
from linode_mcp.tools import (
    domains,
    firewalls,
    linodes,
    networking,
    nodebalancers,
    object_storage,
    reference,
    stackscripts,
    volumes,
)


def register_all_tools(mcp: FastMCP, client: LinodeClient):
    """Register all Linode MCP tools with the server."""
    reference.register(mcp, client)
    linodes.register(mcp, client)
    stackscripts.register(mcp, client)
    firewalls.register(mcp, client)
    nodebalancers.register(mcp, client)
    domains.register(mcp, client)
    object_storage.register(mcp, client)
    volumes.register(mcp, client)
    networking.register(mcp, client)
