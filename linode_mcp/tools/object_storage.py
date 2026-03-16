import boto3

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from linode_mcp.client import LinodeClient


def register(mcp: FastMCP, client: LinodeClient):

    @mcp.tool()
    def list_object_storage_buckets() -> dict:
        """List all Object Storage buckets on the account."""
        return client.get("/object-storage/buckets")

    @mcp.tool()
    def create_object_storage_bucket(
        label: str = Field(description="Bucket name (3-63 chars, lowercase alphanumeric and hyphens). Must be globally unique."),
        region: str = Field(description="Region ID for the bucket (e.g. 'us-east-1'). Note: Object Storage regions may differ from compute regions."),
        cors_enabled: bool = Field(default=False, description="Whether to enable CORS on this bucket."),
    ) -> dict:
        """Create a new Object Storage bucket.

        Bucket names must be globally unique across all Linode customers.
        Use list_regions to find regions with Object Storage capability.
        """
        body = {"label": label, "region": region}
        if cors_enabled:
            body["cors_enabled"] = True
        return client.post("/object-storage/buckets", json=body)

    @mcp.tool()
    def delete_object_storage_bucket(
        region: str = Field(description="Region ID where the bucket is located."),
        label: str = Field(description="The bucket label/name to delete."),
    ) -> dict:
        """Delete an Object Storage bucket. The bucket must be empty first."""
        return client.delete(f"/object-storage/buckets/{region}/{label}")

    @mcp.tool()
    def create_object_storage_key(
        label: str = Field(description="A label for this access key (e.g. 'demo-app-key')."),
        bucket_access: list[dict] | None = Field(default=None, description=(
            "List of bucket access grants. Each item: {'region': 'us-east-1', 'bucket_name': 'my-bucket', "
            "'permissions': 'read_write'}. Permissions: 'read_only' or 'read_write'. "
            "Omit for unrestricted access to all buckets."
        )),
    ) -> dict:
        """Create an Object Storage access key (S3-compatible credentials).

        Returns access_key and secret_key. The secret_key is only shown once — save it immediately.
        Use bucket_access to restrict the key to specific buckets.
        """
        body = {"label": label}
        if bucket_access is not None:
            body["bucket_access"] = bucket_access
        return client.post("/object-storage/keys", json=body)

    @mcp.tool()
    def list_object_storage_keys() -> dict:
        """List all Object Storage access keys on the account."""
        return client.get("/object-storage/keys")

    @mcp.tool()
    def delete_object_storage_key(
        key_id: int = Field(description="The ID of the Object Storage key to revoke/delete."),
    ) -> dict:
        """Revoke an Object Storage access key."""
        return client.delete(f"/object-storage/keys/{key_id}")

    @mcp.tool()
    def list_object_storage_objects(
        region: str = Field(description="Region ID where the bucket is located (e.g. 'us-east-1')."),
        bucket: str = Field(description="The bucket label/name."),
        prefix: str | None = Field(default=None, description="Filter objects by prefix (e.g. 'images/')."),
    ) -> dict:
        """List objects in an Object Storage bucket."""
        params = {}
        if prefix is not None:
            params["prefix"] = prefix
        return client.get(f"/object-storage/buckets/{region}/{bucket}/object-list", params=params)

    @mcp.tool()
    def delete_object_storage_object(
        region: str = Field(description="Region ID where the bucket is located (e.g. 'us-east-1')."),
        bucket: str = Field(description="The bucket label/name."),
        object_name: str = Field(description="The key/name of the object to delete (e.g. 'style.css' or 'images/logo.png')."),
        access_key: str = Field(description="OBJ access key (from create_object_storage_key)."),
        secret_key: str = Field(description="OBJ secret key (from create_object_storage_key)."),
    ) -> dict:
        """Delete an object from an Object Storage bucket.

        Requires S3-compatible credentials (access_key and secret_key) from create_object_storage_key.
        The Linode API does not support object deletion directly — this uses the S3-compatible API.
        """
        try:
            s3 = boto3.client(
                "s3",
                region_name=region,
                endpoint_url=f"https://{region}.linodeobjects.com",
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            s3.delete_object(Bucket=bucket, Key=object_name)
            return {"success": True}
        except Exception as e:
            return {"error": True, "message": str(e)}
