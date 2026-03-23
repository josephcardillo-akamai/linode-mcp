import os
import httpx

class LinodeClient:
    """Thin synchronous wrapper around the Linode API v4."""

    BASE_URL = "https://api.linode.com/v4"

    def __init__(self):
        token = os.environ.get("LINODE_API_TOKEN")
        if not token:
            raise RuntimeError(
                "LINODE_API_TOKEN environment variable is required. "
                "Generate one at https://cloud.linode.com/profile/tokens"
            )
        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _handle_response(self, resp: httpx.Response) -> dict:
        if resp.status_code == 204:
            return {"success": True}
        try:
            body = resp.json()
        except Exception:
            body = {"raw": resp.text}
        if resp.status_code >= 400:
            errors = body.get("errors", [])
            message = "; ".join(e.get("reason", str(e)) for e in errors) if errors else str(body)
            return {"error": True, "status": resp.status_code, "message": message}
        return body

    def get(self, path: str, params: dict | None = None) -> dict:
        resp = self._client.get(path, params=params)
        return self._handle_response(resp)

    def post(self, path: str, json: dict | None = None) -> dict:
        resp = self._client.post(path, json=json or {})
        return self._handle_response(resp)

    def put(self, path: str, json: dict | None = None) -> dict:
        resp = self._client.put(path, json=json or {})
        return self._handle_response(resp)

    def delete(self, path: str) -> dict:
        resp = self._client.delete(path)
        return self._handle_response(resp)
