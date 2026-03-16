from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_ips() -> dict:
        """List all IP addresses on the account, including public and private IPs for all Linodes."""
        return client.get("/networking/ips")
