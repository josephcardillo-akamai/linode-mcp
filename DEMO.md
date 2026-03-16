# Demo Script: Full Multi-Tier Deployment

End result: a load-balanced, HTTPS-secured web app at `https://mcpdemo.nothingtoteach.com` deployed entirely through natural language via MCP + Claude.

**Architecture:** 2 web servers + NodeBalancer (HTTP/HTTPS) + Cloud Firewall + DNS + Object Storage + SSL cert

**Domain:** Use `mcpdemo.nothingtoteach.com`. If DNS is cached from a prior demo, use `mcpdemo1.nothingtoteach.com` as fallback.

**Pre-demo:** Copy your SSH public key — you'll need it for Prompt 2:
```bash
cat ~/.ssh/id_rsa.pub
```

---

## Prompt 1 — Object Storage for static assets

> Create an Object Storage bucket called `demo-assets` in the `us-east-1` cluster, then create an access key called `demo-assets-key` with read/write access to it.

*Deploys: OBJ bucket + access key. Note the access key and secret key — the StackScript needs them.*

---

## Prompt 2 — StackScript for web servers

> Create a StackScript called `demo-web-app` for `linode/ubuntu24.04` with this script:
>
> ```bash
> #!/bin/bash
> # <UDF name="ssh_pubkey" label="SSH Public Key" />
> # <UDF name="obj_access_key" label="OBJ Access Key" />
> # <UDF name="obj_secret_key" label="OBJ Secret Key" />
> # <UDF name="obj_bucket_url" label="OBJ Bucket URL" example="https://demo-assets.us-east-1.linodeobjects.com" />
>
> set -e
>
> # Install packages
> apt-get update && apt-get install -y nginx s3cmd
>
> # Configure s3cmd for Linode Object Storage
> cat > /root/.s3cfg << EOF
> [default]
> access_key = $OBJ_ACCESS_KEY
> secret_key = $OBJ_SECRET_KEY
> host_base = us-east-1.linodeobjects.com
> host_bucket = %(bucket)s.us-east-1.linodeobjects.com
> use_https = True
> EOF
>
> # Create and upload CSS to OBJ bucket (with correct MIME type)
> cat > /tmp/style.css << 'CSSEOF'
> * { margin: 0; padding: 0; box-sizing: border-box; }
> body { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; background: #0a0e17; color: #e2e8f0; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
> .dashboard { max-width: 720px; width: 90%; padding: 2.5rem; }
> .header { text-align: center; margin-bottom: 2.5rem; }
> .header h1 { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg, #00b4d8, #06d6a0); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.25rem; }
> .header p { color: #64748b; font-size: 0.95rem; }
> .card { background: #131926; border: 1px solid #1e293b; border-radius: 12px; padding: 1.25rem 1.5rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 1rem; transition: border-color 0.2s; }
> .card:hover { border-color: #00b4d8; }
> .icon { width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; flex-shrink: 0; }
> .icon.server { background: #0e2a3d; color: #00b4d8; }
> .icon.storage { background: #0a2e26; color: #06d6a0; }
> .icon.lb { background: #1f0e2a; color: #a78bfa; }
> .icon.fw { background: #2a0e1f; color: #f472b6; }
> .icon.ssl { background: #0e2a1f; color: #34d399; }
> .card-content h3 { font-size: 0.95rem; font-weight: 600; margin-bottom: 0.2rem; }
> .card-content p { font-size: 0.82rem; color: #64748b; }
> .status { margin-left: auto; padding: 0.3rem 0.75rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; background: #062e22; color: #06d6a0; flex-shrink: 0; }
> .footer { text-align: center; margin-top: 2rem; color: #334155; font-size: 0.8rem; }
> CSSEOF
>
> s3cmd put /tmp/style.css s3://demo-assets/style.css --acl-public --mime-type="text/css"
>
> HOSTNAME=$(hostname)
> PRIVATE_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if($i ~ /^192\.168\./) print $i}')
> PUBLIC_IP=$(hostname -I | awk '{for(i=1;i<=NF;i++) if($i !~ /^192\.168\./ && $i !~ /:/) print $i}')
>
> # Write index.html — shows which backend is responding
> cat > /var/www/html/index.html << HTMLEOF
> <!DOCTYPE html>
> <html lang="en">
> <head>
>   <meta charset="UTF-8">
>   <meta name="viewport" content="width=device-width, initial-scale=1.0">
>   <title>Akamai Cloud - Demo Deployment</title>
>   <link rel="stylesheet" href="${OBJ_BUCKET_URL}/style.css">
> </head>
> <body>
>   <div class="dashboard">
>     <div class="header">
>       <h1>Akamai Cloud &mdash; Demo Deployment</h1>
>       <p>Infrastructure deployed via MCP + Claude</p>
>     </div>
>     <div class="card">
>       <div class="icon server">&#9881;</div>
>       <div class="card-content">
>         <h3>Compute Instance</h3>
>         <p>Responding from: <strong>${HOSTNAME}</strong></p>
>       </div>
>       <div class="status">Active</div>
>     </div>
>     <div class="card">
>       <div class="icon storage">&#9729;</div>
>       <div class="card-content">
>         <h3>Object Storage</h3>
>         <p>CSS loaded from: ${OBJ_BUCKET_URL}</p>
>       </div>
>       <div class="status">Active</div>
>     </div>
>     <div class="card">
>       <div class="icon lb">&#8644;</div>
>       <div class="card-content">
>         <h3>NodeBalancer</h3>
>         <p>Traffic load balanced across web servers</p>
>       </div>
>       <div class="status">Active</div>
>     </div>
>     <div class="card">
>       <div class="icon ssl">&#128274;</div>
>       <div class="card-content">
>         <h3>TLS/SSL</h3>
>         <p>HTTPS via Let's Encrypt cert on NodeBalancer</p>
>       </div>
>       <div class="status">Active</div>
>     </div>
>     <div class="card">
>       <div class="icon fw">&#128737;</div>
>       <div class="card-content">
>         <h3>Cloud Firewall</h3>
>         <p>SSH + HTTP + HTTPS (backends firewalled)</p>
>       </div>
>       <div class="status">Active</div>
>     </div>
>     <div class="footer">
>       Deployed with Linode MCP Server &bull; Powered by Akamai Cloud Computing
>     </div>
>   </div>
> </body>
> </html>
> HTMLEOF
>
> # Configure nginx: serve content on private IP only, redirect public IP to HTTPS
> cat > /etc/nginx/sites-available/default << NGINXEOF
> # Private IP — serves content to NodeBalancer
> server {
>     listen ${PRIVATE_IP}:80;
>     root /var/www/html;
>     index index.html;
>     server_name _;
>
>     # Redirect HTTP->HTTPS when accessed through NodeBalancer port 80
>     if (\$http_x_forwarded_proto = "http") {
>         return 301 https://\$host\$request_uri;
>     }
>
>     location / {
>         try_files \$uri \$uri/ =404;
>     }
> }
>
> # Public IP — redirect any direct HTTP access to HTTPS
> server {
>     listen ${PUBLIC_IP}:80;
>     server_name _;
>     return 301 https://mcpdemo.nothingtoteach.com\$request_uri;
> }
> NGINXEOF
>
> # SSH hardening: key-only auth, no root password login
> sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
> sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
>
> # Add authorized SSH key from UDF
> mkdir -p /root/.ssh
> echo "$SSH_PUBKEY" >> /root/.ssh/authorized_keys
> chmod 600 /root/.ssh/authorized_keys
>
> systemctl restart ssh
> systemctl restart nginx
> ```

*Deploys: StackScript with SSH hardening baked in. Note the StackScript ID for the next prompts.*

---

## Prompt 3 — Web servers

> Create two Nanodes (`g6-nanode-1`) in `us-east` labeled `demo-web-1` and `demo-web-2`, both running Ubuntu 24.04 with private IPs, tagged `demo`. Deploy them with StackScript ID `<STACKSCRIPT_ID>` and these UDF values:
> - `ssh_pubkey`: `<YOUR_SSH_PUBKEY>`
> - `obj_access_key`: `<OBJ_ACCESS_KEY>`
> - `obj_secret_key`: `<OBJ_SECRET_KEY>`
> - `obj_bucket_url`: `https://demo-assets.us-east-1.linodeobjects.com`

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

> Create a NodeBalancer in `us-east` labeled `demo-nb`. Add an HTTP config on port 80 with roundrobin algorithm and HTTP health checks on `/` (check interval 15s, timeout 10s, 3 attempts). Then add both web servers as backend nodes:
> - `demo-web-1` at `<WEB1_PRIVATE_IP>:80`
> - `demo-web-2` at `<WEB2_PRIVATE_IP>:80`

*Deploys: NodeBalancer with HTTP load balancing. Note the NodeBalancer's public IP for DNS.*

---

## Prompt 6 — DNS

> Create a domain for `nothingtoteach.com` (SOA email: `admin@nothingtoteach.com`) with type `master`. Then add an A record pointing `mcpdemo` to the NodeBalancer's IP `<NB_PUBLIC_IP>`.

*Deploys: DNS so `mcpdemo.nothingtoteach.com` resolves to the NodeBalancer.*

---

## Prompt 7 — SSL Certificate (manual step + MCP)

This step combines local certbot with MCP for DNS verification. SSL certs are generated fresh each demo — new deployment means new IPs, new cert.

> I need to generate a Let's Encrypt SSL certificate for `mcpdemo.nothingtoteach.com`. Run certbot locally with DNS challenge:
> ```bash
> certbot certonly --key-type rsa --manual --preferred-challenges dns \
>   -d mcpdemo.nothingtoteach.com \
>   --config-dir /tmp/certbot/config --work-dir /tmp/certbot/work --logs-dir /tmp/certbot/logs \
>   --agree-tos --email <YOUR_EMAIL>
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

## Architecture Summary

```
User Browser
    |
    | HTTPS (443) / HTTP (301 -> HTTPS)
    v
NodeBalancer (<NB_PUBLIC_IP>)
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
