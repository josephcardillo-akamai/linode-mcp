from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_regions() -> dict:
        """List all available Linode regions (data centers).

        Returns region IDs (e.g. 'us-east'), labels, and capabilities.
        Use region IDs when creating Linodes, NodeBalancers, etc.
        """
        return client.get("/regions")

    @mcp.tool()
    def list_linode_types(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List available Linode instance types (plans) with pricing.

        Returns type IDs (e.g. 'g6-nanode-1'), specs (CPU, RAM, disk), and monthly price.
        Use type IDs when creating or resizing Linodes.
        """
        return client.get("/linode/types", params={"page": page})

    @mcp.tool()
    def list_images(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List available Linode images (OS distributions and custom images).

        Returns image IDs (e.g. 'linode/ubuntu24.04'), labels, and status.
        Use image IDs when creating Linodes.
        """
        return client.get("/images", params={"page": page})
