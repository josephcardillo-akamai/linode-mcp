from mcp.server.fastmcp import FastMCP

from linode_mcp.client import LinodeClient
from linode_mcp.tools import register_all_tools

mcp = FastMCP(
    name="Linode MCP",
    instructions="""
        This server manages Akamai Cloud Compute Infrastructure
        via the Linode APIv4. Use it to create and manage Linodes,
        NodeBalancers, Firewalls, DNS records, Object Storage
        buckets/keys/objects, StackScripts, and more.
        All tools follow the pattern {verb}_{resource} (e.g. list_linodes,
        create_linode, etc). Resources are created in the us-east
        region by default unless otherwise specified.
    """
    )
client = LinodeClient()
register_all_tools(mcp, client)

if __name__ == "__main__":
    mcp.run(transport="stdio")