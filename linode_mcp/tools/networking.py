from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_ips() -> dict:
        """List all IP addresses on the account, including public and private IPs for all Linodes."""
        return client.get("/networking/ips")

    @mcp.tool()
    def list_vlans(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all VLANs on the account.

        VLANs provide private layer 2 networking between Linodes in the same region.
        VLANs are created implicitly when a Linode is created with a VLAN interface —
        use the 'interfaces' parameter on create_linode.
        """
        return client.get("/networking/vlans", params={"page": page})

    @mcp.tool()
    def get_linode_networking(
        linode_id: int = Field(description="The ID of the Linode"),
    ) -> dict:
        """Get detailed networking information for a Linode, including public/private IPs and VLAN interfaces."""
        return client.get(f"/linode/instances/{linode_id}/ips")
