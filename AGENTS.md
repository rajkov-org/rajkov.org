# AGENTS.md — working guide for rajkov.org

This file is the standing guide. The original handoff lives in
`docs/KICKOFF-2026-10-11.md` (archived once story 001 shipped).

## What this is

The website of **Rajasthani Kutumb of Victoria Inc. (RAJKOV)**, Melbourne —
a hand-built **static site**: plain HTML + one CSS file + a little vanilla JS.
No build step, no framework. What is in `www/` is exactly what ships.

- Production: https://rajkov.org (apex canonical; www redirects) — currently on
  the original shared LiteSpeed host, deployed over FTPS with `make ftp-deploy`
  (`deploy/htaccess.production` is the Caddyfile's twin; keep them in step).
  Credentials: `~/.config/rajkov/ftp.env` on dev01, never in the repo.
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

## File naming (assets, downloads, pages)

- **Lowercase, hyphen-separated, descriptive, no dates in page names.** Say what
  the file *is*, not where it came from: `rajasthani-decorated-camel-sunset.webp`,
  `rajkov-teej-utsav-2026-flyer.webp`, `rajasthan-association-france-raf-logo.png`,
  `rajkov-rana-memorandum-of-understanding-2024.pdf`. Never `IMG_1234.jpeg`,
  `WhatsApp-Image-…`, `image-3-e1712…png`, `hero-1.webp`, `poster.jpg`.
- Suffix by role: `-logo`, `-flyer`, `-poster`, `-icon-192`; year last when the
  document is dated (`…-2024.pdf`).
- Photos → `.webp` (ffmpeg `-c:v libwebp -quality 80–85`, ≤1200 px wide unless
  it is a hero); logos → `.png` if they came as PNG, `.webp` otherwise;
  documents → `.pdf`. Always set `width`/`height` on `<img>`.
- The whole tree was renamed to this convention on 2026-10-11 while the site was
  on staging only. **After production go-live, never rename a published file**
  (bookmarks, search results, partner links, sitemap). Add a new file and a
  301 in `deploy/Caddyfile` instead.

## SEO conventions

- `<title>` ≤ 60 characters, pattern `<what this page is> | RAJKOV` (home:
  `RAJKOV — Rajasthani Kutumb of Victoria, Melbourne`). One `<h1>` per page.
- `meta description` 120–160 characters, a sentence a human would click on, no
  keyword lists.
- Canonical is the clean URL on `https://rajkov.org` (`/about`, never
  `/about.html`); the origin serves both, the canonical de-duplicates them.
- Every page: OG + Twitter meta with an absolute `og:image`; inner pages carry
  `BreadcrumbList` JSON-LD; home carries `Organization` + `WebSite`; `/events`
  carries one `Event` per flyer; `/contact` carries `ContactPage`.
- Link text names the destination (`About RAJKOV Stars →`), never
  `Learn more` / `Click here`.
- `alt` describes the picture; a logo next to its own name gets `alt="<Name> logo"`;
  purely decorative images (the brand mark beside hidden text) get `alt=""`.
- Staging is `noindex` via the origin header; production strips it at the edge.
  `sitemap.xml` lists every indexable page; `404.html` is `noindex`.

## Weekly Rajasthan Bulletin (story 004)

A ~2-minute spoken bulletin every **Sunday 17:00 Australia/Melbourne**, in English and
Rajasthani (Marwari, Devanagari), opening with *Khamma Ghani* and *Ram Ram sa*. The
generator is **local only** — `bulletin/` on dev01 is gitignored by owner decision
(2026-10-11); the method is the `news-bulletin` skill on dev01 (`~/.claude/skills/`).
What the repo holds is the **output text** under `www/bulletin/` (transcript pages,
archive index, podcast feed). **Audio is never committed**; the mp3s are uploaded to
production out-of-band and only the **last 4 weeks** are kept there. The bulletin never
invents: headlines from RSS, gold/silver/A$→₹ from live key-less APIs, the kahavat of the
week from a committee-vetted list, RAJKOV event mentions (manuhaar to register) from a
committee-maintained `events.json`. Gateway key: `rajkov` on llm-gw (`sonnet,haiku,kokoro`),
stored in `~/.config/rajkov/llm.env`, never in the repo.

## Lessons learned (keep this list current)

- **`curl | grep -q` under `pipefail` lies.** grep exits on the first match,
  curl gets SIGPIPE and the pipeline fails. `deploy/verify.sh` buffers the body
  first (`body=$(curl …); grep … <<<"$body"`). Found on the first staging deploy.
- **No emoji in markup.** The headless Chromium on dev01 (and some phones) has
  no emoji font → tofu boxes. Icons are inline SVG via the generator's `icon()`.
- **Percentage `max-height` does nothing inside an auto-sized grid cell.** Use
  pixel limits on logo boxes (`.sponsor-logo img { max-height: 110px }`).
- **Cloudflare rewrites `mailto:` on the wire** (Email Address Obfuscation →
  `/cdn-cgi/l/email-protection`). The origin HTML is right; grep the origin, not
  the edge, when verifying addresses. Turn it off under Scrape Shield if plain
  addresses are wanted.
- **Hand edits and the generator drift.** Pages are stamped by a generator kept
  in the session scratchpad (header/footer byte-identical, `?v=N` bumps). When
  someone edits `www/*.html` by hand (as upstream did for the 2026 flyers), port
  the edit into the generator first and confirm a regeneration changes nothing
  else (`git status` should show only the intended files).
- **Sponsor/partner logos usually arrive only inside a composite flyer.** Crop
  from the highest-resolution source available (ffmpeg `crop` + 2× lanczos) and
  ask the sponsor for the real file; store the crop under the final name.
- **Docker image pulls can fail transiently** (`containerd … ingest … no such
  file`). Re-run `docker pull caddy:2-alpine`, then `make check` again.
- **`www/healthz` is a real file** ("ok") so `verify.sh` passes on the FTP host too; on
  Caddy the `/healthz` handle answers first, so the file is harmless there.
- **The repo is public** (`rajkov-org/rajkov.org`): never commit credentials,
  member lists, or anything beyond what the website itself publishes.
- **The logo is a 647×136 banner with three parts** (couple illustration, text, official
  Vijay Stambh photo). The ONLY sources are that PNG (transparent) and a 56×82 copy inside
  a MoU PDF — no high-resolution original exists in the export; the scanned letterheads
  are the same low-res file printed. Ask the committee for the original before any redraw.
- **Never run a heavy CPU job on dev01 next to a bulletin run.** A software-Vulkan
  upscaler (Real-ESRGAN via lavapipe) pushed the 6 GB box into swap; ffmpeg/ffprobe sat
  in D-state for minutes and looked hung. Upscaling belongs on a box with a GPU, or use a
  light model with `nice`.
- **`ffmpeg` in a script/timer needs `-nostdin`** (and `stdin=DEVNULL`), or it waits on the
  terminal forever. **Python 3.13+ rejects the edge local CA** unless
  `verify_flags &= ~ssl.VERIFY_X509_STRICT` (verification stays on). Both found building
  the bulletin generator.

## Gate + deploy

```
make check         # Caddy configs validate + every internal link/asset resolves
make dev           # serve www/ locally with the real origin Caddyfile (:8086)
make edge-deploy   # push www/ + config → recreate container → ship route → smoke test (staging)
make edge-verify   # smoke test only (EDGE_URL=… to point elsewhere)
make ftp-backup    # mirror the whole FTP account to ~/backups (once, before the first cut-over)
make ftp-retire    # move the old WordPress out of the web root, deny-all (once)
make ftp-deploy    # upload www/ + .htaccess over FTPS → smoke test https://rajkov.org (production)
```

Never trust `caddy reload` exit 0 — `deploy/verify.sh` asks the live URL.
Commit after every deploy, tag it, add a row to `deploy/DEPLOYED.md`.
