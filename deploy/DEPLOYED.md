# Deploy ledger — rajkov.org

What is live, where, since when. One row per deploy. Story detail lives in
`docs/compass/stories/`; this file only records what shipped.

| Date (AEDT) | Target | Commit / tag | Deployed by | Verify | Notes |
|---|---|---|---|---|---|
| 2026-10-11 | staging `https://rajkov.suryasoni.info` | `9897844` → tag `v1.0.0` | `make edge-deploy` from dev01 | PASS — `/healthz` 200, 10/10 pages 200, `x-robots-tag: noindex, nofollow`, homepage content ok; old WP URLs 301 (`/about-us/` → `/about`, `/rajkov-stars/` → `/initiatives#stars`), `/nope` → 404 page, PDFs served as `application/pdf` | First deploy of story 001. Container `rajkov-web` created on prd01 (`/opt/rajkov.org`), edge route `/opt/edge/conf.d/rajkov.caddy` installed. Production hostnames `rajkov.org` / `www.rajkov.org` are in the route but inert until the owner adds them to the Cloudflare tunnel and moves DNS (remember MX/SPF/TXT for Microsoft 365 mail). |
| 2026-10-11 | staging `https://rajkov.suryasoni.info` | `0e966e0` → tag `v1.1.0` | `make edge-deploy` from dev01 | PASS — healthz 200, 10/10 pages 200, noindex, homepage content; sponsors images 200 | Sponsors section (platinum CYP Foods & Spices + 8 sponsors + anonymous) added to Home and Partnerships; `styles.css?v=2`. |
