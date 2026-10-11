# AGENTS.md — working guide for rajkov.org

This file is the standing guide. The original handoff lives in
`docs/KICKOFF-2026-10-11.md` (archived once story 001 shipped).

## What this is

The website of **Rajasthani Kutumb of Victoria Inc. (RAJKOV)**, Melbourne —
a hand-built **static site**: plain HTML + one CSS file + a little vanilla JS.
No build step, no framework. What is in `www/` is exactly what ships.

- Production: https://rajkov.org (apex canonical; www redirects)
- Staging: https://rajkov.suryasoni.info (noindex)
- Repo: github.com/rajkov-org/rajkov.org (org `rajkov-org`; **public** as of 2026-10-11 — the owner may flip it to private)
- Host: prd01, behind the shared `edge` Caddy (`/opt/edge`), per the
  `edge-onboard` skill.

## Layout

```
www/                      ← deployable site (web root)
  index.html 404.html …   ← pages; clean URLs (/about → about.html) via the origin Caddyfile
                            pages: / about constitution by-laws initiatives business-network
                                   partnerships membership events contact 404
  assets/css/styles.css   ← the single stylesheet; design tokens at the top
  assets/js/main.js       ← progressive enhancement only
  assets/img/             ← logo, hero, partner logos
  downloads/              ← PDFs (MoUs, directory, constitution if offered as PDF)
  robots.txt sitemap.xml site.webmanifest favicon.ico
deploy/                   ← Caddyfile (origin), docker-compose.edge.yml, caddy/rajkov.caddy (edge route), verify.sh, DEPLOYED.md
scripts/check-links.py    ← part of `make check`
source/wordpress/         ← the scraped WordPress export (read-only reference, never served)
docs/                     ← compass/ (stories, STATUS.md), security-sweep.md
Makefile  README.md  AGENTS.md  CLAUDE.md  requirements.md
```

Supporting files stay at the repo root, never inside `www/`.

## Hard content rules

- Organisation name: **Rajasthani Kutumb of Victoria Inc.** ("Kutumb", never
  "Kumtumb" — the old logo PNG has that typo). Short form **RAJKOV**.
- ABN 91 393 557 191 · Reg. No A 0044973G — keep exactly.
- Never carry over anything flagged in `docs/security-sweep.md`. Every external
  link in `www/` must be one we chose on purpose (partners, Microsoft Form).
- No third-party scripts. No analytics unless the owner asks. Fonts self-hosted
  or from Google Fonts only.
- Contact details appear only as the owner decided (secretary@rajkov.org + Microsoft Form for membership; names only — story 001).
- Don't rename files once live (URLs/bookmarks/sitemap break). Old WordPress
  URLs (`/about-us/`, `/rajkov-stars/`, …) are 301'd to the new pages in
  `deploy/Caddyfile`; keep those redirects.
- Contact: general committee contact is **secretary@rajkov.org** (owner,
  2026-10-11, amending the earlier form-only decision); **membership enquiries**
  go to the Microsoft Form; **sponsorship** goes to president@rajkov.org. No
  phone numbers and no personal emails in page copy. Committee = names + roles.
- Logo: `www/assets/img/rajkov-logo.png` is the corrected "KUTUMB" artwork
  (it was `Proposed-Resolution-…png` in the WordPress uploads).

## Coding conventions (same as aryasamajofmelbourne.com)

- Header and footer are duplicated in every page: change one → change all with
  a scripted pass, keep them byte-identical. Check with
  `for f in www/*.html; do sed -n '/<header class="site-header">/,/<main id="main">/p' $f | md5sum; done | sort | uniq -c`
  (one line = identical) and the same for `'/<\/main>/,$p'`.
- Icons are inline SVG (`.ico`), never emoji — the headless renderer on dev01
  has no emoji font, and neither do some members' devices.
- Fonts: Playfair Display (display), Source Sans 3 (body), Noto Serif
  Devanagari (tagline) from Google Fonts — the only third-party host besides
  the Microsoft Form and partner sites.
- CSS/JS are versioned `styles.css?v=N`; **bump N on every CSS/JS change**
  across all pages. HTML is served `no-cache`; assets cache 1 h.
- Animations CSS-only, `transform`/`opacity` only, gated by
  `prefers-reduced-motion`; a `.js` class gates `.reveal` so content shows
  without JS.
- Full `.container` for heroes; `.article-body` (left-aligned, max-width) for
  prose. Devanagari text set in a font that has it (e.g. Noto Serif Devanagari).

## Gate + deploy

```
make check         # Caddy configs validate + every internal link/asset resolves
make dev           # serve www/ locally with the real origin Caddyfile (:8086)
make edge-deploy   # push www/ + config → recreate container → ship route → smoke test
make edge-verify   # smoke test only (EDGE_URL=https://rajkov.org for prod)
```

Never trust `caddy reload` exit 0 — `deploy/verify.sh` asks the live URL.
Commit after every deploy, tag it, add a row to `deploy/DEPLOYED.md`.
