from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_linodes(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all Linodes on the account.

        Returns each Linode's ID, label, status, region, type, and IP addresses.
        """
        return client.get("/linode/instances", params={"page": page})

    @mcp.tool()
    def get_linode(
        linode_id: int = Field(description="The ID of the Linode to retrieve"),
    ) -> dict:
        """Get detailed information about a specific Linode.

        Returns full details including status, specs, IPs, and backups info.
        """
        return client.get(f"/linode/instances/{linode_id}")

    @mcp.tool()
    def create_linode(
        region: str = Field(description="Region ID (e.g. 'us-east'). Use list_regions to see valid values."),
        type: str = Field(description="Instance type ID (e.g. 'g6-nanode-1'). Use list_linode_types to see valid values."),
        image: str | None = Field(default=None, description="Image ID (e.g. 'linode/ubuntu24.04'). Use list_images to see valid values. Required unless restoring from backup."),
        label: str | None = Field(default=None, description="A label for the Linode (3-64 characters, alphanumeric/dashes/underscores)."),
        root_pass: str | None = Field(default=None, description="Root password for the Linode. Required when an image is provided."),
        authorized_keys: list[str] | None = Field(default=None, description="List of SSH public keys to install for root user."),
        private_ip: bool = Field(default=False, description="Whether to assign a private IPv4 address."),
        tags: list[str] | None = Field(default=None, description="Tags to apply to this Linode."),
        stackscript_id: int | None = Field(default=None, description="StackScript ID to deploy with. Use list_stackscripts or create_stackscript first."),
        stackscript_data: dict | None = Field(default=None, description="Key-value pairs for StackScript UDF variables."),
        interfaces: list[dict] | None = Field(default=None, description=(
            "Network interfaces for VPC/VLAN configuration. List of interface objects in priority order. "
            "Each interface: {'purpose': 'public'|'vlan'|'vpc', 'label': 'my-vlan' (required for VLAN), "
            "'ipam_address': '10.0.0.1/24' (optional CIDR for VLAN)}. "
            "Example for public + VLAN: [{'purpose': 'public'}, {'purpose': 'vlan', 'label': 'my-vlan', 'ipam_address': '10.0.0.1/24'}]"
        )),
        firewall_id: int | None = Field(default=None, description="Firewall ID to attach to this Linode on creation."),
    ) -> dict:
        """Create a new Linode instance.

        The Linode will boot automatically after creation. Use get_linode to check status.
        For app deployment, use stackscript_id + stackscript_data to run setup scripts on first boot.
        Use interfaces to attach to a VLAN for private networking between Linodes.
        Use firewall_id to attach a Cloud Firewall on creation.
        """
        body = {"region": region, "type": type}
        if image is not None:
            body["image"] = image
        if label is not None:
            body["label"] = label
        if root_pass is not None:
            body["root_pass"] = root_pass
        if authorized_keys is not None:
            body["authorized_keys"] = authorized_keys
        if private_ip:
            body["private_ip"] = True
        if tags is not None:
            body["tags"] = tags
        if stackscript_id is not None:
            body["stackscript_id"] = stackscript_id
        if stackscript_data is not None:
            body["stackscript_data"] = stackscript_data
        if interfaces is not None:
            body["interfaces"] = interfaces
        if firewall_id is not None:
            body["firewall_id"] = firewall_id
        return client.post("/linode/instances", json=body)

    @mcp.tool()
    def update_linode(
        linode_id: int = Field(description="The ID of the Linode to update"),
        label: str | None = Field(default=None, description="New label for the Linode."),
        tags: list[str] | None = Field(default=None, description="New tags for the Linode."),
    ) -> dict:
        """Update a Linode's label or tags."""
        body = {}
        if label is not None:
            body["label"] = label
        if tags is not None:
            body["tags"] = tags
        return client.put(f"/linode/instances/{linode_id}", json=body)

    @mcp.tool()
    def delete_linode(
        linode_id: int = Field(description="The ID of the Linode to delete. This action is irreversible."),
    ) -> dict:
        """Delete a Linode instance permanently.

        All disks, configs, and data will be destroyed. This cannot be undone.
        """
        return client.delete(f"/linode/instances/{linode_id}")

    @mcp.tool()
    def boot_linode(
        linode_id: int = Field(description="The ID of the Linode to boot"),
    ) -> dict:
        """Boot (power on) a Linode that is currently offline."""
        return client.post(f"/linode/instances/{linode_id}/boot")

    @mcp.tool()
    def reboot_linode(
        linode_id: int = Field(description="The ID of the Linode to reboot"),
    ) -> dict:
        """Reboot a running Linode."""
        return client.post(f"/linode/instances/{linode_id}/reboot")

    @mcp.tool()
    def shutdown_linode(
        linode_id: int = Field(description="The ID of the Linode to shut down"),
    ) -> dict:
        """Shut down (power off) a running Linode."""
        return client.post(f"/linode/instances/{linode_id}/shutdown")

    @mcp.tool()
    def resize_linode(
        linode_id: int = Field(description="The ID of the Linode to resize"),
        type: str = Field(description="New instance type ID (e.g. 'g6-standard-2'). Use list_linode_types to see valid values."),
    ) -> dict:
        """Resize a Linode to a different plan.

        The Linode will be shut down, migrated, and rebooted. This may take several minutes.
        """
        return client.post(f"/linode/instances/{linode_id}/resize", json={"type": type})
