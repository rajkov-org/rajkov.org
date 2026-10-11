# rajkov.org

Website of **Rajasthani Kutumb of Victoria Inc. (RAJKOV)** — a Melbourne
community association celebrating Rajasthani culture since 2001.

Hand-built static site (HTML + CSS + a little JS, no build step), hosted on
prd01 behind the shared edge Caddy. Replaces the previous WordPress site, whose
content was exported into `source/wordpress/`.

- `make help` — targets
- `AGENTS.md` — how the codebase works
- `docs/compass/` — stories + status board; `docs/security-sweep.md` — audit of the WordPress export
- `source/wordpress/` — the scraped WordPress export (read-only, untrusted; never served)
