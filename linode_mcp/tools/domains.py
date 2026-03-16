from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_domains(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all DNS domains on the account."""
        return client.get("/domains", params={"page": page})

    @mcp.tool()
    def get_domain(
        domain_id: int = Field(description="The ID of the Domain to retrieve"),
    ) -> dict:
        """Get detailed information about a specific DNS domain."""
        return client.get(f"/domains/{domain_id}")

    @mcp.tool()
    def create_domain(
        domain: str = Field(description="The domain name (e.g. 'example.com')."),
        type: str = Field(default="master", description="Domain type: 'master' or 'slave'."),
        soa_email: str | None = Field(default=None, description="SOA email address (required for master domains, e.g. 'admin@example.com')."),
        tags: list[str] | None = Field(default=None, description="Tags to apply."),
    ) -> dict:
        """Create a new DNS domain (zone).

        For master domains, provide soa_email. After creation, add records with create_domain_record.
        """
        body = {"domain": domain, "type": type}
        if soa_email is not None:
            body["soa_email"] = soa_email
        if tags is not None:
            body["tags"] = tags
        return client.post("/domains", json=body)

    @mcp.tool()
    def update_domain(
        domain_id: int = Field(description="The ID of the Domain to update"),
        domain: str | None = Field(default=None, description="New domain name."),
        soa_email: str | None = Field(default=None, description="New SOA email address."),
        tags: list[str] | None = Field(default=None, description="New tags."),
    ) -> dict:
        """Update a DNS domain's settings."""
        body = {}
        if domain is not None:
            body["domain"] = domain
        if soa_email is not None:
            body["soa_email"] = soa_email
        if tags is not None:
            body["tags"] = tags
        return client.put(f"/domains/{domain_id}", json=body)

    @mcp.tool()
    def delete_domain(
        domain_id: int = Field(description="The ID of the Domain to delete. All records will be removed."),
    ) -> dict:
        """Delete a DNS domain and all its records. This is irreversible."""
        return client.delete(f"/domains/{domain_id}")

    @mcp.tool()
    def list_domain_records(
        domain_id: int = Field(description="The ID of the Domain"),
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all DNS records for a domain."""
        return client.get(f"/domains/{domain_id}/records", params={"page": page})

    @mcp.tool()
    def create_domain_record(
        domain_id: int = Field(description="The ID of the Domain"),
        type: str = Field(description="Record type: 'A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SRV', 'NS', 'CAA'."),
        name: str | None = Field(default=None, description="The hostname or subdomain (e.g. 'www'). Empty string or omit for the zone apex."),
        target: str = Field(description="The record's target value (e.g. IP address for A records, hostname for CNAME)."),
        ttl_sec: int = Field(default=0, description="TTL in seconds. 0 uses the domain's default."),
        priority: int | None = Field(default=None, description="Priority for MX and SRV records."),
        weight: int | None = Field(default=None, description="Weight for SRV records."),
        port: int | None = Field(default=None, description="Port for SRV records."),
    ) -> dict:
        """Create a DNS record in a domain.

        Common examples:
        - A record: type='A', name='www', target='203.0.113.1'
        - CNAME: type='CNAME', name='app', target='lb.example.com'
        - MX: type='MX', target='mail.example.com', priority=10
        """
        body = {"type": type, "target": target}
        if name is not None:
            body["name"] = name
        if ttl_sec:
            body["ttl_sec"] = ttl_sec
        if priority is not None:
            body["priority"] = priority
        if weight is not None:
            body["weight"] = weight
        if port is not None:
            body["port"] = port
        return client.post(f"/domains/{domain_id}/records", json=body)

    @mcp.tool()
    def update_domain_record(
        domain_id: int = Field(description="The ID of the Domain"),
        record_id: int = Field(description="The ID of the DNS record to update"),
        name: str | None = Field(default=None, description="New hostname/subdomain."),
        target: str | None = Field(default=None, description="New target value."),
        ttl_sec: int | None = Field(default=None, description="New TTL in seconds."),
    ) -> dict:
        """Update a DNS record in a domain."""
        body = {}
        if name is not None:
            body["name"] = name
        if target is not None:
            body["target"] = target
        if ttl_sec is not None:
            body["ttl_sec"] = ttl_sec
        return client.put(f"/domains/{domain_id}/records/{record_id}", json=body)

    @mcp.tool()
    def delete_domain_record(
        domain_id: int = Field(description="The ID of the Domain"),
        record_id: int = Field(description="The ID of the DNS record to delete"),
    ) -> dict:
        """Delete a DNS record from a domain."""
        return client.delete(f"/domains/{domain_id}/records/{record_id}")
