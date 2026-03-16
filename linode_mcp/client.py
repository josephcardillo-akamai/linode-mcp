import os
import httpx # python's way of making web requests; used to send http requests over the internet to the linode api endpoint


class LinodeClient: # this is the blueprint to make the client; creating the thing that talks to linode's api on our behalf.
    """Thin synchronous wrapper around the Linode API v4.""" # synchronous because we're making calls one at a time

    BASE_URL = "https://api.linode.com/v4" # since this URL is used more than once

    def __init__(self): # The constructor - the code that runs automatically when the LinodeClient object is being created. Sets the object up so it's ready to use. To read the token from the environment, and sue it to configure and store a ready-to-use HTTP connection.
        token = os.environ.get("LINODE_API_TOKEN")
        if not token:
            raise RuntimeError( # if the token isn't found, stop and raise error
                "LINODE_API_TOKEN environment variable is required. "
                "Generate one at https://cloud.linode.com/profile/tokens"
            )
        self._client = httpx.Client( # creates persistent http connection; self is the client's way of referring to itself. https://www.python-httpx.org/advanced/clients/. The underscore prefix on _client is a common convention in Python to indicate that this attribute is intended for internal use within the class and should not be accessed directly from outside the class.
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _handle_response(self, resp: httpx.Response) -> dict: # Send an HTTP GET request to base_url + path (with optional query parameters), wait for Linode's response, clean it up into a Python dict, and return it.
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

    def get(self, path: str, params: dict | None = None) -> dict: # the URL path to append to the base URL. Arg should be a string. if no additional parameters are specified, params will be None. Returns a dictionary containing the response data from the API. 
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
