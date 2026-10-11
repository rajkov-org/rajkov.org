# Story 003 — ftp-cutover

> Cut rajkov.org over to the new static site **on the existing shared
> LiteSpeed host via FTPS**, instead of waiting for the Cloudflare → prd01 move.
> High blast radius (production, the live WordPress is replaced in place), so it
> gets a story. The prd01/edge path stays in place as staging and as the future
> home; this story does not touch DNS, Cloudflare or email.

**Status:** done (production live 2026-10-11)
**Depends on:** 001 (built + verified on staging)

## Goal
Replace the compromised WordPress install at rajkov.org with the static site
from `www/`, with a complete, verified backup taken first and the old install
moved out of the web root (not deleted) so it can be restored or inspected.
After this, rajkov.org serves exactly what staging serves, indexable, with the
same clean URLs, redirects and headers expressed as `.htaccess` instead of a
Caddyfile.

Interpretation as first written: "full backup" = mirror the account to dev01.
**Owner changed this mid-story:** nothing is to be downloaded to dev01; the
backup is a server-side move of `public_html` into `wordpress-backups/`
(a cPanel `rajkov.org__2026-10-11T19_32_43+1100.tar.gz` was already there). The WordPress **database**
is not reachable over FTP; the content is already in `source/wordpress/`
(REST export + rendered HTML). If the owner wants the SQL too, that is a
cPanel/phpMyAdmin export they do themselves before step 3.

## Scope — touch ONLY these
- `deploy/ftp/ftp.py` — FTPS tool: list / backup / retire / upload / prune (no secrets)
- `deploy/htaccess.production` — Apache/LiteSpeed rules mirroring `deploy/Caddyfile`
- `Makefile` — `ftp-*` targets
- `deploy/DEPLOYED.md` — production row
- `docs/compass/STATUS.md`, this story
- `~/.config/rajkov/ftp.env` on dev01 (outside the repo) — credentials, owner-supplied
- `~/backups/rajkov.org-ftp-<date>/` on dev01 — the backup (never inside the repo; the repo is public)
- NOT: `www/**` (ships as is), DNS, Cloudflare, the prd01 deploy, email

## Acceptance check (how we verify)
- [x] ~~`make ftp-backup`~~ replaced by `make ftp-archive`: `public_html` → `wordpress-backups/public_html-20261011` (server-side rename, verified by listing); owner declined any download
- [x] Old install is outside the web root: `https://rajkov.org/wordpress-backups/public_html-20261011/wp-login.php` → 404; `/wp-login.php`, `/xmlrpc.php` → 410
- [x] `make ftp-upload` put 54 files (`www/` + `.htaccess`) into the fresh `public_html`
- [x] `make ftp-verify` → PASS: healthz 200 (static `www/healthz`), 10/10 pages 200, production indexable, homepage content
- [x] Live: `/about-us/` → 301 `/about`; `/rajkov-stars/` → 301 `/initiatives#stars`; `/about.html` → 301 `/about`; `http://www.rajkov.org/` → 301 `https://rajkov.org/`; `/wp-login.php` → 410; `/nope` → our 404 page
- [x] `https://rajkov.org/` title is "RAJKOV — Rajasthani Kutumb of Victoria, Melbourne"; headers: nosniff, referrer-policy, x-frame-options, HSTS, `cache-control: no-cache` on HTML; `x-powered-by` gone
- [x] Row in `deploy/DEPLOYED.md`; owner told (chat 2026-10-11): rotate FTP/hosting/WordPress passwords, the DB still exists, delete `wordpress-backups/public_html-20261011` when satisfied, resubmit `sitemap.xml` in Search Console

## Notes
- `verify.sh` checks `/healthz`, which only the Caddy origin answers. On the FTP
  host it will 404 → treat as a known difference or add a static `healthz` file
  to `www/` (decided at deploy time; a static file is the simplest).
- The host answered with `server: LiteSpeed`, `x-powered-by: PHP/8.2.34` and no
  Cloudflare headers on 2026-10-11, so DNS currently points straight at it.
- The WordPress DB, cron entries and any mail/other services on the hosting
  account are untouched by this story. Recommend the owner changes the hosting
  account + FTP passwords after cut-over and deletes `_retired-wordpress-*`
  once satisfied (it is denied, not gone).
