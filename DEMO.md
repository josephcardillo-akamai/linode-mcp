# Demo Script: Full Multi-Tier Deployment

End result: a load-balanced, HTTPS-secured web app at `https://mcpdemo.nothingtoteach.com` deployed entirely through natural language via MCP + Claude.

**Architecture:** 2 web servers + NodeBalancer (HTTP/HTTPS) + Cloud Firewall + DNS + Object Storage + SSL cert

**Pre-demo requirements:**
- Linode API token set as `LINODE_API_TOKEN`
- Your SSH public key: `cat ~/.ssh/id_rsa.pub`
- The base domain `nothingtoteach.com` must already exist in Linode DNS Manager
- The StackScript source lives in the [linode-mcp-demo](https://github.com/josephcardillo-akamai/linode-mcp-demo) repo

---

## Prompt 0 — Discovery

> What regions and affordable instance types does Linode offer?

*Shows off the MCP server's read capabilities before we start building anything. Good ice-breaker prompt.*

---

## Prompt 1 — Object Storage for static assets

> Create an Object Storage bucket called `demo-assets` in the `us-east-1` cluster, then create an access key called `demo-assets-key` with read/write access to it.

*Deploys: OBJ bucket + access key. Note the access key and secret key — the StackScript needs them.*

---

## Prompt 2 — StackScript for web servers

> Fetch the StackScript from `https://raw.githubusercontent.com/josephcardillo-akamai/linode-mcp-demo/refs/heads/main/stackscript.sh` and use its contents to create a StackScript called `demo-web-app` for `linode/ubuntu24.04`. The description should be "Nginx web server with OBJ-hosted CSS and SSH hardening".

*Deploys: StackScript with SSH hardening baked in. The script source lives in the [linode-mcp-demo](https://github.com/josephcardillo-akamai/linode-mcp-demo) repo — single source of truth. Note the StackScript ID for the next prompts.*

---

## Prompt 3 — Web servers

> Create two Nanodes (`g6-nanode-1`) in `us-east` labeled `demo-web-1` and `demo-web-2`, both running Ubuntu 24.04 with private IPs, tagged `demo`. Deploy them with StackScript ID `<STACKSCRIPT_ID>` and these UDF values:
> - `ssh_pubkey`: `<YOUR_SSH_PUBKEY>`
> - `obj_access_key`: `<OBJ_ACCESS_KEY>`
> - `obj_secret_key`: `<OBJ_SECRET_KEY>`
> - `obj_bucket_url`: `https://demo-assets.us-east-1.linodeobjects.com`
> - `domain`: `mcpdemo.nothingtoteach.com`

*Deploys: 2 web servers with nginx, CSS uploaded to OBJ, SSH hardened. Note their private IPs for NodeBalancer setup.*

---

## Prompt 4 — Cloud Firewall

> Create a Cloud Firewall called `demo-firewall` with these inbound rules:
> - Allow SSH (port 22) from anywhere
> - Allow HTTP (port 80) from anywhere
> - Allow HTTPS (port 443) from anywhere
>
> Set inbound policy to DROP and outbound policy to ACCEPT. Assign it to `demo-web-1` and `demo-web-2`.

*Deploys: firewall. Port 80 is needed for NodeBalancer health checks. Backends are protected by nginx only listening on private IPs.*

---

## Prompt 5 — NodeBalancer with HTTP config

> Create a NodeBalancer in `us-east` labeled `demo-lb`. Add an HTTP config on port 80 with roundrobin algorithm and HTTP health checks on `/` (check interval 15s, timeout 10s, 3 attempts). Then add both web servers as backend nodes:
> - `demo-web-1` at `<WEB1_PRIVATE_IP>:80`
> - `demo-web-2` at `<WEB2_PRIVATE_IP>:80`

*Deploys: NodeBalancer with HTTP load balancing. Note the NodeBalancer's public IP for DNS.*

---

## Prompt 6 — DNS A record

> Add an A record on the `nothingtoteach.com` domain (ID 3393917) pointing `mcpdemo` to the NodeBalancer's IP `<NB_PUBLIC_IP>`.

*Deploys: DNS so `mcpdemo.nothingtoteach.com` resolves to the NodeBalancer. The base domain already exists with other records — we only add the `mcpdemo` A record.*

---

## Prompt 7 — SSL Certificate (manual step + MCP)

This step combines local certbot with MCP for DNS verification. SSL certs are generated fresh each demo — new deployment means new IPs, new cert.

> I need to generate a Let's Encrypt SSL certificate for `mcpdemo.nothingtoteach.com`. Run certbot locally with DNS challenge:
> ```bash
> certbot certonly --key-type rsa --manual --preferred-challenges dns \
>   -d mcpdemo.nothingtoteach.com \
>   --config-dir /tmp/certbot/config --work-dir /tmp/certbot/work --logs-dir /tmp/certbot/logs \
>   --agree-tos --email admin@nothingtoteach.com
> ```
> When certbot gives you the ACME challenge value, create a TXT record on the `nothingtoteach.com` domain for `_acme-challenge.mcpdemo` with that value. Then continue certbot.

*Generates: RSA cert at `/tmp/certbot/config/live/mcpdemo.nothingtoteach.com/fullchain.pem` and key at `privkey.pem`.*

*This is a great demo moment — MCP creates the ACME TXT record for DNS challenge validation.*

---

## Prompt 8 — HTTPS NodeBalancer config

> Read the SSL certificate from `/tmp/certbot/config/live/mcpdemo.nothingtoteach.com/fullchain.pem` and the private key from `/tmp/certbot/config/live/mcpdemo.nothingtoteach.com/privkey.pem`. Create an HTTPS config on NodeBalancer `<NB_ID>` with port 443, protocol `https`, roundrobin algorithm, HTTP health checks on `/` (interval 15s, timeout 10s, 3 attempts), and pass the cert and key as `ssl_cert` and `ssl_key`. Then add both web servers as backend nodes to the new HTTPS config:
> - `demo-web-1` at `<WEB1_PRIVATE_IP>:80`
> - `demo-web-2` at `<WEB2_PRIVATE_IP>:80`

*Deploys: HTTPS termination on the NodeBalancer. SSL is terminated at the NB and forwarded as HTTP to backends.*

**Note:** If the `create_nodebalancer_config` MCP tool returns "Could not load certificate", the cert may need to be passed via the Linode API directly using curl — MCP tool JSON serialization can sometimes mangle PEM newlines.

---

## Prompt 9 — Verify

> Verify the deployment:
> 1. `curl -sI https://mcpdemo.nothingtoteach.com` — should return 200 with valid cert
> 2. `curl -sI http://mcpdemo.nothingtoteach.com` — should return 301 redirect to HTTPS
> 3. Run `curl -s https://mcpdemo.nothingtoteach.com | grep "Responding from"` multiple times — should alternate between `demo-web-1` and `demo-web-2`
> 4. `curl -sI http://<WEB1_PUBLIC_IP>` — should return 301 (not serve content directly)

---

## Prompt 10 — Cleanup / Teardown

> Tear down the demo deployment in this order:
> 1. Delete the `mcpdemo` A record from the `nothingtoteach.com` domain (do NOT delete the domain itself — it has other records)
> 2. Delete the `_acme-challenge.mcpdemo` TXT record if it still exists
> 3. Delete the NodeBalancer `demo-lb`
> 4. Delete the Cloud Firewall `demo-firewall`
> 5. Delete the Linodes `demo-web-1` and `demo-web-2`
> 6. Delete the StackScript `demo-web-app`
> 7. Delete the `style.css` object from the `demo-assets` bucket (use `delete_object_storage_object` with the OBJ access key and secret key)
> 8. Delete the Object Storage key `demo-assets-key`
> 9. Delete the Object Storage bucket `demo-assets`

*Tears down all demo resources in reverse dependency order. The base domain `nothingtoteach.com` and all non-demo resources are preserved.*

---

## Architecture Summary

```
User Browser
    |
    | HTTPS (443) / HTTP (301 -> HTTPS)
    v
NodeBalancer (demo-lb)
    |--- port 443: TLS termination (Let's Encrypt RSA cert)
    |--- port 80:  forwards to backends (which return 301 -> HTTPS)
    |
    | HTTP (private network, 192.168.x.x:80)
    v
+------------------+    +------------------+
| demo-web-1       |    | demo-web-2       |
| nginx            |    | nginx            |
| private IP only  |    | private IP only  |
+------------------+    +------------------+

Static assets: demo-assets.us-east-1.linodeobjects.com/style.css
DNS: mcpdemo.nothingtoteach.com -> NodeBalancer IP
Firewall: SSH + HTTP + HTTPS inbound, DROP all else
```

## Security Notes

- Backends only serve content on private IPs — no direct public access to app
- Public IPs redirect to `https://mcpdemo.nothingtoteach.com`
- HTTP traffic through the NodeBalancer is redirected to HTTPS via `X-Forwarded-Proto` check
- SSH key-only auth (password auth disabled, root password login prohibited)
- Cloud Firewall blocks all ports except 22, 80, 443
- SSL cert is RSA (required by Linode NodeBalancers), no passphrase on key
