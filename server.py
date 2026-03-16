from mcp.server.fastmcp import FastMCP

from linode_mcp.client import LinodeClient
from linode_mcp.tools import register_all_tools

mcp = FastMCP("Linode MCP")
client = LinodeClient()
register_all_tools(mcp, client)

if __name__ == "__main__":
    mcp.run(transport="stdio")
