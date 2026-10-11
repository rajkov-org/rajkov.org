# requirements.md — rajkov.org

Captured by the hub session on 2026-10-11 from the owner's brief plus a scout of
the live site. Items marked **(assumed)** are hub defaults awaiting owner
confirmation (see KICKOFF.md § Open decisions).

## Owner's brief (verbatim intent)

> create a new project rajkov.org, i want to scrap wordpress website and convert
> the content into a professional beautiful website like aryasamajofmelbourne.com
> and maintain it via github and host it on prd01. i did not setup cloudflare and
> migrated it to point to prd01 yet, but i will do it as one of the next step.

> yes scan for any vulnerable link and content (and javascript code). ideally, we
> should do all such activity as part of kickoff instruction.

## Goals

1. Replace the WordPress site with a static site that looks professional and
   is cheap and safe to run (no PHP, no plugins, nothing to patch).
2. Same craft as aryasamajofmelbourne.com: hand-built HTML + one CSS + a little
   JS, accessible, responsive, fast, SEO basics done (titles, descriptions,
   OG, JSON-LD, sitemap, canonical).
3. Maintained in GitHub (`spsoni/rajkov.org`, private), deployed to prd01
   behind the shared edge Caddy, with a staging mirror.
4. Content carried over faithfully — minus anything injected/spam, and minus
   dead WooCommerce/ticketing scaffolding.

## Non-goals

- No CMS, no admin UI, no comments, no shop/ticketing (the live site's
  WooCommerce pages are unused scaffolding).
- No blog (the live Blog page is empty; zero posts exist).
- No attempt to preserve WordPress URLs with trailing-slash/`?p=` forms beyond
  sensible clean-URL equivalents (map old → new in a redirect table if needed).

## Source of truth

`source/wordpress/` — scraped 2026-10-11 from https://rajkov.org via the public
REST API (`/wp-json/wp/v2/pages`, `/media`) plus the rendered HTML of each page.
There are 22 pages, 0 posts, 85 media items. Content last modified on the live
site: 2026-09-14 (home, partnerships).

## Live-site facts worth keeping straight

- Legal name: **Rajasthani Kutumb of Victoria Inc.** — ABN 91 393 557 191,
  Registration No A 0044973G. Short name **RAJKOV**.
- Formed 2001 by seven Rajasthani families in Melbourne; incorporated 2003;
  founder member families: Jawale, Goyal, Manihar, Panwar, Sharma, Soni.
- Financial/membership year 1 May – 30 April.
- Tagline on logo: पधारो म्हारे देस ("Padharo mhare des").
- Current committee 2026-27: President Vishal Gupta; Vice President Rahul
  Jain; Secretary TBD; Treasurer Ritu Singh; Committee Akshat Soni, Bhoomija
  Chauhan. (About page carries the full 2003→ history of office bearers.)
- Conveners: Business Network — Shri Neelesh Mehta; Spirituality Forum — Shri
  Ranjeet Verma. (Other initiative pages name their own conveners.)
- Partnerships (MoUs, PDFs in `media/2024/05`): RANA (ranausa.org),
  Rajasthani Yuva Samiti, Rajasthan Charitable Trust UK, RAF, RACT NZ; plus
  Business Network Directory 2024 (PDF).
- Membership enquiries go to a Microsoft Form (link in the nav).
- Live nav: Home · About · Our Constitution · Our By-Laws · Contact ·
  Membership Enquiries (external) · Partnerships · Initiatives (6 pages).

## Proposed information architecture (assumed)

```
/                   Home — hero, who we are, committee 2026-27, initiatives, partners, join CTA
/about              About — history + full office-bearer history (tables)
/constitution       Our Constitution (long; sectioned with an in-page TOC)
/by-laws            Our By-Laws
/initiatives/       Index + one page per initiative (or sections — decision 5)
/partnerships       Partners with logos + MoU downloads
/membership         Fees (from by-laws) + Microsoft Form CTA
/contact            Committee + contact method (decision 1/2)
/404
```

## Hosting / deploy

- Origin: `caddy:2-alpine` serving `www/`, container `rajkov-web`, alias
  `rajkov` on the `edge` network, `/opt/rajkov.org` on prd01.
- Edge route: `deploy/caddy/rajkov.caddy` → `/opt/edge/conf.d/`.
- Staging: `https://rajkov.suryasoni.info` **(assumed)**, noindex.
- Production: `https://rajkov.org` (apex canonical, www → apex) — DNS/Cloudflare
  cut-over is the owner's step, after staging is approved.
- The hub did NOT deploy anything; the hostnames do not exist on the tunnel yet.

## Quality bar

- `make check` (config validates + no broken internal links) before every commit.
- `make edge-verify` after every deploy; never trust a reload's exit 0.
- Lighthouse-level sanity: accessible contrast, keyboard nav, reduced-motion
  respected, images sized/optimised (WebP where it helps), no layout shift.
