# Infrastructure & DNS Configuration

## Overview

MetaAI Platform uses three subdomains under `sushantdev.com`, all pointing to the same VPS (`80.225.207.230`). SSL is handled by Cloudflare with Full (Strict) mode.

## DNS Records

All records are `A` records pointing to `80.225.207.230`:

| Type | Name | Value | Proxy |
|------|------|-------|-------|
| A | `metaai` | `80.225.207.230` | Proxied (orange cloud) |
| A | `metaai-api` | `80.225.207.230` | Proxied (orange cloud) |
| A | `metaai-observability` | `80.225.207.230` | Proxied (orange cloud) |
| A | `staging-metaai` | `80.225.207.230` | Proxied (orange cloud) |
| A | `staging-metaai-api` | `80.225.207.230` | Proxied (orange cloud) |

## Cloudflare Configuration

### SSL/TLS Settings

- **SSL**: Full (Strict)
- **Minimum TLS Version**: 1.2
- **Always Use HTTPS**: On
- **Automatic HTTPS Rewrites**: On

### Proxy Status

Enable the orange cloud (proxied) for all A records to benefit from:
- DDoS protection
- CDN caching
- SSL termination
- IP obfuscation

### Page Rules (Optional)

| URL Pattern | Setting |
|------------|---------|
| `metaai-api.sushantdev.com/*` | Cache Level: Bypass |
| `metaai.sushantdev.com/*` | Cache Level: Standard |

## Traefik SSL Configuration

SSL is handled by the existing Traefik instance on the VPS via Let's Encrypt (certresolver). Traefik automatically discovers services through Docker labels and provisions certificates.

No manual certbot commands needed — Traefik handles the ACME protocol automatically.

## Network Architecture

```
Internet
  │
  ▼
Cloudflare (SSL termination, DDoS protection)
  │
  ▼
VPS :80/:443
  │
  ▼
Traefik (reverse proxy, SSL, Docker provider)
  │
  ├── metaai.sushantdev.com ──► frontend:8501
  ├── metaai-api.sushantdev.com ──► backend:8000
  └── metaai-observability.sushantdev.com ──► grafana:3000
  │
  └── All internal services on `web` Docker network
```
