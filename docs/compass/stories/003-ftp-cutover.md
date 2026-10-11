# Story 003 — ftp-cutover

> Cut rajkov.org over to the new static site **on the existing shared
> LiteSpeed host via FTPS**, instead of waiting for the Cloudflare → prd01 move.
> High blast radius (production, the live WordPress is replaced in place), so it
> gets a story. The prd01/edge path stays in place as staging and as the future
> home; this story does not touch DNS, Cloudflare or email.

**Status:** in-progress
**Depends on:** 001 (built + verified on staging)

## Goal
Replace the compromised WordPress install at rajkov.org with the static site
from `www/`, with a complete, verified backup taken first and the old install
moved out of the web root (not deleted) so it can be restored or inspected.
After this, rajkov.org serves exactly what staging serves, indexable, with the
same clean URLs, redirects and headers expressed as `.htaccess` instead of a
Caddyfile.

Interpretation: "full backup" = every file in the FTP account (not just the
document root), mirrored to dev01 with a manifest. The WordPress **database**
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
- [ ] `make ftp-backup` completes; `manifest.tsv` has no `ERROR` rows; count + bytes recorded here; a spot-check restores one upload and one PHP file byte-identical
- [ ] `make ftp-retire` moves every entry of the document root into `_retired-wordpress-<date>/` with a deny-all `.htaccess`; `curl -I https://rajkov.org/_retired-wordpress-<date>/wp-login.php` is 404/403, not 200
- [ ] `make ftp-upload` puts `www/` + `.htaccess` in the document root
- [ ] `make ftp-verify` → `deploy/verify.sh https://rajkov.org` prints PASS (healthz is a Caddy-only route — see Notes), all pages 200, **no** `X-Robots-Tag`
- [ ] Redirect table works live: `/about-us/` → `/about`, `/rajkov-stars/` → `/initiatives#stars`, `www.` → apex, `/about.html` → `/about`, `/wp-login.php` → 410
- [ ] `https://rajkov.org/` serves the new homepage (title "RAJKOV — Rajasthani Kutumb of Victoria, Melbourne"); no PHP banner (`x-powered-by` gone)
- [ ] Row in `deploy/DEPLOYED.md`; owner told the backup location and what remains (DB, hosting account) to clean up

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
