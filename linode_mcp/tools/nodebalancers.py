from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_nodebalancers(
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all NodeBalancers (load balancers) on the account."""
        return client.get("/nodebalancers", params={"page": page})

    @mcp.tool()
    def get_nodebalancer(
        nodebalancer_id: int = Field(description="The ID of the NodeBalancer to retrieve"),
    ) -> dict:
        """Get detailed information about a specific NodeBalancer, including its public IP."""
        return client.get(f"/nodebalancers/{nodebalancer_id}")

    @mcp.tool()
    def create_nodebalancer(
        region: str = Field(description="Region ID for the NodeBalancer (e.g. 'us-east'). Use list_regions for valid values."),
        label: str | None = Field(default=None, description="A label for the NodeBalancer."),
        tags: list[str] | None = Field(default=None, description="Tags to apply."),
    ) -> dict:
        """Create a new NodeBalancer (load balancer) in a region.

        After creation, add configs (ports) with create_nodebalancer_config,
        then add backend nodes with create_nodebalancer_node.
        """
        body = {"region": region}
        if label is not None:
            body["label"] = label
        if tags is not None:
            body["tags"] = tags
        return client.post("/nodebalancers", json=body)

    @mcp.tool()
    def delete_nodebalancer(
        nodebalancer_id: int = Field(description="The ID of the NodeBalancer to delete. This is irreversible."),
    ) -> dict:
        """Delete a NodeBalancer and all its configs and nodes."""
        return client.delete(f"/nodebalancers/{nodebalancer_id}")

    @mcp.tool()
    def list_nodebalancer_configs(
        nodebalancer_id: int = Field(description="The ID of the NodeBalancer"),
        page: int = Field(default=1, description="Page number for pagination"),
    ) -> dict:
        """List all configs (port listeners) for a NodeBalancer."""
        return client.get(f"/nodebalancers/{nodebalancer_id}/configs", params={"page": page})

    @mcp.tool()
    def create_nodebalancer_config(
        nodebalancer_id: int = Field(description="The ID of the NodeBalancer"),
        port: int = Field(default=80, description="The port this config listens on (e.g. 80, 443)."),
        protocol: str = Field(default="http", description="Protocol: 'http', 'https', or 'tcp'."),
        algorithm: str = Field(default="roundrobin", description="Load balancing algorithm: 'roundrobin', 'leastconn', or 'source'."),
        check: str = Field(default="connection", description="Health check type: 'none', 'connection', 'http', or 'http_body'."),
        check_path: str | None = Field(default=None, description="URL path for HTTP health checks (e.g. '/health')."),
        check_interval: int = Field(default=31, description="Seconds between health checks (2-3600)."),
        check_timeout: int = Field(default=30, description="Seconds to wait for a health check response (1-30)."),
        check_attempts: int = Field(default=3, description="Number of failed checks before marking unhealthy (1-30)."),
        stickiness: str = Field(default="none", description="Session persistence: 'none', 'table', or 'http_cookie'."),
        ssl_cert: str | None = Field(default=None, description="PEM-formatted SSL certificate. Required when protocol is 'https'. Include full chain (cert + intermediates). Must be RSA — ECDSA not supported."),
        ssl_key: str | None = Field(default=None, description="PEM-formatted private key for the SSL certificate. Must not have a passphrase. Required when protocol is 'https'."),
    ) -> dict:
        """Create a config (port listener) on a NodeBalancer.

        After creating a config, add backend nodes with create_nodebalancer_node.
        For HTTPS, provide ssl_cert and ssl_key with PEM-formatted RSA certificate and key.
        """
        body = {
            "port": port,
            "protocol": protocol,
            "algorithm": algorithm,
            "check": check,
            "check_interval": check_interval,
            "check_timeout": check_timeout,
            "check_attempts": check_attempts,
            "stickiness": stickiness,
        }
        if check_path is not None:
            body["check_path"] = check_path
        if ssl_cert is not None:
            body["ssl_cert"] = ssl_cert
        if ssl_key is not None:
            body["ssl_key"] = ssl_key
        return client.post(f"/nodebalancers/{nodebalancer_id}/configs", json=body)

    @mcp.tool()
    def create_nodebalancer_node(
        nodebalancer_id: int = Field(description="The ID of the NodeBalancer"),
        config_id: int = Field(description="The ID of the NodeBalancer config (from create_nodebalancer_config or list_nodebalancer_configs)"),
        label: str = Field(description="A label for this backend node (e.g. 'web-1')."),
        address: str = Field(description="The private IP and port of the backend Linode (e.g. '192.168.1.1:80'). Must be a private IP in the same data center."),
        weight: int = Field(default=100, description="Load balancing weight (1-255). Higher = more traffic."),
        mode: str = Field(default="accept", description="Node mode: 'accept', 'reject', 'backup', or 'drain'."),
    ) -> dict:
        """Add a backend node (Linode) to a NodeBalancer config.

        The node's address must be a private IP:port in the same region as the NodeBalancer.
        Use get_linode to find a Linode's private IP.
        """
        body = {
            "label": label,
            "address": address,
            "weight": weight,
            "mode": mode,
        }
        return client.post(f"/nodebalancers/{nodebalancer_id}/configs/{config_id}/nodes", json=body)
