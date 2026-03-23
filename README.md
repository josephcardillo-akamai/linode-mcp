# Linode MCP Server

An MCP (Model Context Protocol) server that lets you manage Linode/Akamai Compute infrastructure through natural language using Claude Code or Claude Desktop.

## What it does

Talk to Claude in plain English to manage your Linode infrastructure:
- Create, manage, and delete Linode instances
- Set up Cloud Firewalls with custom rules
- Configure NodeBalancers for load balancing
- Manage DNS domains and records
- Create Object Storage buckets and access keys
- Manage Block Storage volumes
- Deploy applications with StackScripts

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- A [Linode API token](https://cloud.linode.com/profile/tokens)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

## Setup

1. **Clone the repo:**
   ```bash
   git clone <repo-url>
   cd linode-mcp
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Set your API token:**
   ```bash
   export LINODE_API_TOKEN="your-token-here"
   ```

4. **Add the MCP server to Claude Code:**
   ```bash
   claude mcp add linode -- uv run python server.py

   # output
   Added stdio MCP server linode with command: uv run python server.py to local config
   File modified: ~/.claude.json
   ```

   Or pass the token directly:
   ```bash
   claude mcp add linode --env LINODE_API_TOKEN=your-token -- uv run python server.py
   ```

5. **Verify** — open Claude Code and run `/mcp` to confirm the Linode server is connected.

**Note:** This is not a full-service Linode API wrapper — it covers the essential infrastructure tasks for common workflows (compute, networking, storage, DNS). More tools are being added over time.

## Available Tools (57 total)

| Category | Tools |
|---|---|
| **Reference** | list_regions, list_linode_types, list_images |
| **Linodes** | list, get, create, update, delete, boot, reboot, shutdown, resize |
| **StackScripts** | list, create, delete |
| **Firewalls** | list, get, create, update, delete, get_rules, update_rules, list_devices, add_device, remove_device |
| **NodeBalancers** | list, get, create, delete, list_configs, create_config, create_node |
| **Domains** | list, get, create, update, delete + record CRUD (list, create, update, delete) |
| **Object Storage** | list_buckets, create_bucket, delete_bucket, create_key, list_keys, delete_key, list_objects, delete_object |
| **Volumes** | list, create, delete, attach, detach |
| **Networking** | list_ips, get_linode_networking, list_vlans |

## Example Usage

Once connected, just talk to Claude:

> "What regions and instance types does Linode offer?"

> "Create a Nanode in us-east labeled 'my-server' with Ubuntu 24.04"

> "Set up a firewall allowing SSH and HTTP, then apply it to my-server"

> "Create a NodeBalancer in us-east and add my web servers as backends"

## Security

Your Linode API token stays on your machine. The MCP server runs as a local subprocess — no network exposure, no shared credentials.

## License

MIT
