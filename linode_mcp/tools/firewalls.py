from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_firewalls(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all Cloud Firewalls on the account."""
        return client.get("/networking/firewalls", params={"page": page})

    @mcp.tool()
    def get_firewall(
        firewall_id: int = Field(description="The ID of the Firewall to retrieve"),
    ) -> dict:
        """Get detailed information about a specific Cloud Firewall."""
        return client.get(f"/networking/firewalls/{firewall_id}")

    @mcp.tool()
    def create_firewall(
        label: str = Field(description="A label for the Firewall (3-32 characters)."),
        rules: dict = Field(description=(
            "Firewall rules object with 'inbound' and 'outbound' arrays, plus 'inbound_policy' and 'outbound_policy' "
            "('ACCEPT' or 'DROP'). Each rule has: protocol ('TCP','UDP','ICMP'), ports (e.g. '22, 80, 443' or '1-65535'), "
            "addresses (object with 'ipv4' and/or 'ipv6' arrays of CIDRs, e.g. ['0.0.0.0/0']), action ('ACCEPT' or 'DROP'), "
            "and label."
        )),
        devices: list[dict] | None = Field(default=None, description=(
            "List of devices to apply this Firewall to. Each device is {'id': <linode_id>, 'type': 'linode'}."
        )),
        tags: list[str] | None = Field(default=None, description="Tags to apply to this Firewall."),
    ) -> dict:
        """Create a new Cloud Firewall with rules and optionally attach it to Linodes.

        Example rules:
        {
            "inbound_policy": "DROP",
            "outbound_policy": "ACCEPT",
            "inbound": [
                {"protocol": "TCP", "ports": "22", "addresses": {"ipv4": ["0.0.0.0/0"]}, "action": "ACCEPT", "label": "allow-ssh"},
                {"protocol": "TCP", "ports": "80, 443", "addresses": {"ipv4": ["0.0.0.0/0"]}, "action": "ACCEPT", "label": "allow-http"}
            ],
            "outbound": []
        }
        """
        body = {"label": label, "rules": rules}
        if devices is not None:
            body["devices"] = {"linodes": [d["id"] for d in devices if d.get("type") == "linode"]}
        if tags is not None:
            body["tags"] = tags
        return client.post("/networking/firewalls", json=body)

    @mcp.tool()
    def update_firewall(
        firewall_id: int = Field(description="The ID of the Firewall to update"),
        label: str | None = Field(default=None, description="New label for the Firewall."),
        status: str | None = Field(default=None, description="Set to 'enabled' or 'disabled'."),
        tags: list[str] | None = Field(default=None, description="New tags for the Firewall."),
    ) -> dict:
        """Update a Cloud Firewall's label, status, or tags."""
        body = {}
        if label is not None:
            body["label"] = label
        if status is not None:
            body["status"] = status
        if tags is not None:
            body["tags"] = tags
        return client.put(f"/networking/firewalls/{firewall_id}", json=body)

    @mcp.tool()
    def delete_firewall(
        firewall_id: int = Field(description="The ID of the Firewall to delete. This is irreversible."),
    ) -> dict:
        """Delete a Cloud Firewall. All rules and device associations will be removed."""
        return client.delete(f"/networking/firewalls/{firewall_id}")

    @mcp.tool()
    def get_firewall_rules(
        firewall_id: int = Field(description="The ID of the Firewall"),
    ) -> dict:
        """Get the current inbound and outbound rules for a Cloud Firewall."""
        return client.get(f"/networking/firewalls/{firewall_id}/rules")

    @mcp.tool()
    def update_firewall_rules(
        firewall_id: int = Field(description="The ID of the Firewall"),
        rules: dict = Field(description=(
            "Complete replacement rules object with 'inbound', 'outbound', 'inbound_policy', and 'outbound_policy'. "
            "See create_firewall for the format."
        )),
    ) -> dict:
        """Replace all rules on a Cloud Firewall.

        This is a full replacement — include all desired rules, not just changes.
        """
        return client.put(f"/networking/firewalls/{firewall_id}/rules", json=rules)
