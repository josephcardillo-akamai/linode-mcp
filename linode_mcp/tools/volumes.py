from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_volumes(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all Block Storage volumes on the account."""
        return client.get("/volumes", params={"page": page})

    @mcp.tool()
    def create_volume(
        label: str = Field(description="A label for the volume (1-32 chars)."),
        size: int = Field(default=20, description="Size in GB (10-10240)."),
        region: str | None = Field(default=None, description="Region ID. Required if not attaching to a Linode. Use list_regions for valid values."),
        linode_id: int | None = Field(default=None, description="Linode ID to attach this volume to on creation."),
        tags: list[str] | None = Field(default=None, description="Tags to apply."),
    ) -> dict:
        """Create a new Block Storage volume.

        Provide either region (unattached) or linode_id (auto-attached to that Linode's region).
        """
        body = {"label": label, "size": size}
        if region is not None:
            body["region"] = region
        if linode_id is not None:
            body["linode_id"] = linode_id
        if tags is not None:
            body["tags"] = tags
        return client.post("/volumes", json=body)

    @mcp.tool()
    def delete_volume(
        volume_id: int = Field(description="The ID of the volume to delete. Must be detached first."),
    ) -> dict:
        """Delete a Block Storage volume. The volume must be detached from all Linodes first."""
        return client.delete(f"/volumes/{volume_id}")

    @mcp.tool()
    def attach_volume(
        volume_id: int = Field(description="The ID of the volume to attach"),
        linode_id: int = Field(description="The ID of the Linode to attach the volume to"),
    ) -> dict:
        """Attach a Block Storage volume to a Linode.

        The volume and Linode must be in the same region. The volume will appear as a block device on the Linode.
        """
        return client.post(f"/volumes/{volume_id}/attach", json={"linode_id": linode_id})

    @mcp.tool()
    def detach_volume(
        volume_id: int = Field(description="The ID of the volume to detach"),
    ) -> dict:
        """Detach a Block Storage volume from its Linode."""
        return client.post(f"/volumes/{volume_id}/detach")
