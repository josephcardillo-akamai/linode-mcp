from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_stackscripts(
        page: int = Field(default=1, description="Page number for pagination"),
        mine: bool = Field(default=True, description="If true, only return your own StackScripts. If false, returns all public StackScripts."),
    ) -> dict:
        """List StackScripts (deployment scripts for Linodes).

        By default returns only your own StackScripts. Set mine=False to browse public ones.
        """
        params = {"page": page}
        if mine:
            params["mine"] = "true"
        return client.get("/linode/stackscripts", params=params)

    @mcp.tool()
    def create_stackscript(
        label: str = Field(description="A label for the StackScript (3-128 characters)."),
        script: str = Field(description="The bash script content. Can include StackScript UDF tags like '<UDF name=\"db_ip\" label=\"Database IP\" />' for variables."),
        images: list[str] = Field(description="List of image IDs this StackScript is compatible with (e.g. ['linode/ubuntu24.04'])."),
        description: str | None = Field(default=None, description="A description of what this StackScript does."),
        is_public: bool = Field(default=False, description="Whether to make this StackScript public."),
    ) -> dict:
        """Create a new StackScript for automated Linode deployment.

        StackScripts run on first boot of a Linode. Use UDF tags in the script to define
        variables that are passed via stackscript_data when creating a Linode.

        Example UDF: <UDF name="db_ip" label="Database Private IP" />
        Then reference as $DB_IP in the script.
        """
        body = {
            "label": label,
            "script": script,
            "images": images,
        }
        if description is not None:
            body["description"] = description
        body["is_public"] = is_public
        return client.post("/linode/stackscripts", json=body)

    @mcp.tool()
    def delete_stackscript(
        stackscript_id: int = Field(description="The ID of the StackScript to delete"),
    ) -> dict:
        """Delete a StackScript. Only StackScripts you own can be deleted."""
        return client.delete(f"/linode/stackscripts/{stackscript_id}")
