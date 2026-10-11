# Story 001 — static-rebuild

> Written from KICKOFF.md on 2026-10-11. The owner reviews the interpretation
> below plus the eight open decisions (one AskUserQuestion round) before pages
> are built; that review is the plan approval.

**Status:** done (staging live; production cut-over is story 003)
**Depends on:** none

## Goal
Replace the WordPress site at rajkov.org with a hand-built static site (plain
HTML + one CSS file + a little vanilla JS) in the craft of
aryasamajofmelbourne.com but with RAJKOV's own identity (palette from the
red/orange turban logo and the sunset-camel hero; Devanagari tagline
पधारो म्हारे देस). Content is carried over faithfully from
`source/wordpress/` **after** a security sweep — the live WordPress shows signs
of compromise (injected SEO-spam link on the home page), so every external
link, script, hidden element and binary is audited and anything injected is
left behind. Dead WooCommerce/ticketing/blog scaffolding is dropped. The result
deploys to prd01 behind the shared edge Caddy, first to the staging mirror
`rajkov.suryasoni.info`; the production DNS cut-over is the owner's separate step.

Owner decisions (AskUserQuestion round, 2026-10-11):
1. **Contact:** Microsoft Form for membership enquiries; **amended later on 2026-10-11:** general "contact the committee" links go to `secretary@rajkov.org` (role address, Microsoft 365). Still no phone numbers or personal emails.
2. **Committee:** names and roles only.
3. **Logo:** ship the corrected "KUTUMB" PNG from the export as-is (`media/2024/06/Proposed-Resolution-…png`, 646×135, "EST. 2003").
4. **Pages:** Shop/Cart/Checkout/My account/Tickets/Blog/Sample/Privacy (lorem ipsum)/empty Gangaur 2024 are dropped
   (not ticked explicitly, but a static site cannot carry a cart and `requirements.md` lists them as non-goals — flagged to the owner).
   New `/events` page built from the three posters in the export (Teej 2024, Gangaur 2025, 2026 sponsors).
5. **Initiatives:** one `/initiatives` page with sections + separate `/business-network` page (directory PDF).
6. **Footer credit:** "Website by Nikhil Soni" removed.
7. **Staging:** `rajkov.suryasoni.info` confirmed.
8. **MoU PDFs:** download links, no inline viewers.
Also: keep Facebook + Instagram links; the two WhatsApp group links are missing from the export (owner to supply).

## Scope — touch ONLY these
- `docs/compass/STATUS.md`, `docs/compass/stories/001-static-rebuild.md` — this story
- `docs/security-sweep.md` — sweep findings (step 1 of the build)
- `www/**` — the whole site (pages, `assets/css/styles.css`, `assets/js/main.js`,
  `assets/img/`, `downloads/`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, favicon)
- `scripts/check-links.py` — only if the gate needs a fix
- `deploy/Caddyfile` — old WordPress URL → new clean URL redirects only (scope widened 2026-10-11 before the edit)
- `deploy/DEPLOYED.md` — new ledger, first row on staging deploy
- `deploy/verify.sh` — only if a smoke check needs adjusting
- `README.md`, `AGENTS.md` — small updates once the IA is final; `KICKOFF.md` archived when the story ships
- NOT: `source/wordpress/**` (read-only), Cloudflare/DNS, `/opt/edge` beyond `make edge-route`

## Acceptance check (how we verify)
- [x] `docs/security-sweep.md` lists every external link, script, hidden element and binary in the export with file:line and a verdict; summary reported to the owner 2026-10-11
- [x] Owner has answered KICKOFF decisions 1–8 (AskUserQuestion round 2026-10-11, recorded in Goal)
- [x] No flagged URL/host from the sweep appears anywhere in `www/` — `grep -ri 'evolution-zenith|soninikhil|wp-content|elementor|embedpress' www/` → no matches (2026-10-11)
- [x] No third-party `<script>` (only `/assets/js/main.js` + 2 JSON-LD blocks); external hosts in `www/`: forms.office.com, fonts.googleapis/gstatic.com, facebook.com, instagram.com, ranausa.org, rajasthancharitabletrust.co.uk, schema.org/sitemaps.org vocab URIs
- [x] "Kumtumb" does not appear in `www/` (grep -ri → 0); ABN 91 393 557 191 and Reg. No. A 0044973G on footer, contact, constitution, by-laws
- [x] `make check` passes — `Valid configuration` ×2, `359/359 internal references resolve` (2026-10-11)
- [x] Header + footer byte-identical across all 11 pages (md5 of the header and footer regions: one hash each)
- [x] Each page has title, description, canonical, OG/Twitter meta; Organization JSON-LD on home, ContactPage on contact; `sitemap.xml` lists all 10 indexable pages; 404 is noindex. Rendered in headless Chromium at 1400px and 390px — screenshots reviewed.
- [x] `make edge-deploy` → `deploy/verify.sh https://rajkov.suryasoni.info` prints PASS (2026-10-11; output in Notes and `deploy/DEPLOYED.md`). First run FAILED on the homepage-content check only because `curl | grep -q` under `pipefail` trips on an early pipe close; `verify.sh` now buffers the body.
- [x] Owner told in writing (chat 2026-10-11 + `docs/security-sweep.md` § 7) that the live WordPress is likely compromised and should be retired after cut-over, and that rajkov.org mail (Microsoft 365 MX/SPF) must be recreated in Cloudflare before DNS moves

## Notes
- Source inventory: 22 pages, 0 posts, 42 media files kept in the export (PDF ×11, PNG ×13, JPEG ×14, WebP ×2, SVG ×2). Keep: home, about-us, our-constitution, our-by-laws, partnerships, 6 initiatives, contact. Drop: shop, cart, checkout, my-account, tickets-*, blog, sample-page, privacy-policy-2 (lorem ipsum), gangaur-2024 (empty) — pending decision 4.
- Reference implementation: `~/projects/aryasamajofmelbourne.com/www` (styles.css tokens at top, main.js nav/reveal, `?v=N` cache busting).
- Owner decisions: see Goal section above.

Smoke test, 2026-10-11 (second run, after the verify.sh fix):

```
  verifying https://rajkov.suryasoni.info

  ok   /healthz 200
  10/10 pages return 200
  ok   staging noindex (x-robots-tag: noindex, nofollow)
  ok   homepage content

  PASS
```
