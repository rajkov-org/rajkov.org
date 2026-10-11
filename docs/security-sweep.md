# Security sweep — `source/wordpress/` export (2026-10-11)

Scope: every file in `source/wordpress/html/*.html` (22 rendered pages),
`md/*.md` (22), `api/pages.json`, and the 42 media files under `media/`.
Method: scripted scans (a Python scanner kept outside the export, run with
`python3 -I`), `file(1)`, `pdfinfo`, `strings`, plus manual reading of every
inline script and every anchor on the home page. The export was treated as
untrusted input throughout; nothing in it was executed.

**Verdict in one line:** one confirmed injection (hidden SEO-spam link in the
home-page copy, present in the WordPress database itself), no other malicious
content found; all scripts are standard WordPress/Elementor/Blocksy/WPForms/
EmbedPress boilerplate loaded from rajkov.org, none of which ships; all binaries
are what they claim to be and contain no active content.

The live WordPress should still be treated as **compromised**: the injected
anchor sits inside the page's own post content (REST `pages.json`, author id 2,
page last modified 2026-09-14), which means someone wrote to the database
through an editor-level account or a plugin hole. See § 7.

---

## 1. External links (every non-rajkov.org host in html/ + md/)

| Host | Where (file:line, first occurrence) | Occurrences | Verdict |
|---|---|---|---|
| `evolution-zenithofficial.com` | `html/home.html:334`, `md/home.md:26`, `api/pages.json` (home `content.rendered`) | 2 files | **INJECTED — SEO spam.** `<a href="https://evolution-zenithofficial.com/" style="position: absolute; left: -10434px">Evolution Zenith – Smart Trading</a>` sits mid-sentence in the "About RAJKOV" paragraph, pushed 10,434 px off-screen so humans never see it. Classic cloaked backlink. **Not carried over.** |
| `forms.office.com` (`/pages/responsepage.aspx?id=jH-5bd0a4km9NpMS-9aBh7zRhE6KLVlJi_55S57R61lUMEJUS09MR0o1NDhFWVFTV0hHTkZWT1M1Mi4u`) | `html/home.html:122` (nav "Membership Enquiries", on all 22 pages) | 66 | Legitimate — RAJKOV's own Microsoft Form (tenant id matches the org's Microsoft 365 mail, see § 7). **Keep.** |
| `www.facebook.com/rajkovkutumb` | `html/home.html:146` (header social icons, all pages) | 44 | Legitimate social profile. **Keep** (owner to confirm the handle is current). |
| `www.instagram.com/rajkov.official/` | `html/home.html:157` (header social icons, all pages) | 44 | Legitimate social profile. **Keep** (owner to confirm). |
| `www.ranausa.org` | `html/partnerships.html:277`, `md/partnerships.md:11` | 2 | Partner (RANA — Rajasthan Association of North America), wraps the partner image. **Keep.** |
| `www.rajasthancharitabletrust.co.uk` | `html/partnerships.html:309`, `md/partnerships.md:18` | 2 | Partner (Rajasthan Charitable Trust UK), wraps the partner logo. **Keep.** |
| `fonts.googleapis.com` (Playfair Display 900) | `html/home.html:53` (stylesheet link, all pages) | 44 | Benign theme font. Not carried as-is; the new site makes its own Google Fonts request. |
| `mailto:soninikhil@hotmail.com` | `html/home.html:434` (footer "Website by Nikhil Soni") | 22 | Legitimate credit for the previous site builder. Carry only if the owner keeps the credit (KICKOFF decision 6). |
| `schema.org`, `ogp.me`, `gmpg.org/xfn/11`, `api.w.org` | `<html prefix>`, `itemtype`, `<link rel=profile>`, `<link rel=https://api.w.org/>` | 22–132 | Vocabulary/profile URIs in markup, not navigable links. Benign; not carried. |

Nothing else external exists. No `chat.whatsapp.com` links: the RAJKOV Stars
and Mel Milaap pages end with "join our … WhatsApp group here:" and **no link
follows** (`html/rajkov-stars.html`, `html/rajkov-mel-milaap.html`) — the
WordPress copy is simply missing them. Flag for the owner.

Internal links (`rajkov.org/...`): only the 22 page URLs, `wp-content/uploads`
media, theme/plugin assets, feeds, `wp-json`, and `/search/QUERY_STRING/`
(Blocksy live-search template). No internal link to any non-existent "pharma"
or doorway path — the compromise did not create extra pages (REST lists
exactly the 22 known pages).

## 2. Scripts, iframes, forms

**External `<script src>` hosts:** `rajkov.org` only (jQuery 3.7.1,
jquery-migrate, jQuery UI, underscore, wp-util, wp-i18n, Blocksy `main.js`,
Elementor `webpack.runtime/frontend-modules/frontend.js`, WPForms Lite
`wpforms.min.js` + `jquery.validate`, EmbedPress front/pdf-lightbox/yt-queue/
ads/analytics-tracker). No script is loaded from any third-party host — no
analytics, no tag manager, no CDN, no reCAPTCHA script (WPForms is *configured*
for reCAPTCHA v2 — `wpformsElementorVars` in `html/contact.html` — but the
Google script is not in the rendered page). **None of it ships.**

**Inline `<script>` blocks** (all read in full; counts are pages containing it):

| Block | Pages | What it is | Verdict |
|---|---|---|---|
| `document.write(new Date().getFullYear())` | 22 | footer © year | benign |
| `type="speculationrules"` prefetch JSON | 22 | WordPress core speculative loading | benign |
| Elementor `lazyloadRunObserver` IIFE | 22 | background-image lazy load | benign |
| `ct_localizations = {...}` (`id=ct-scripts-js-extra`) | 22 | Blocksy strings + `admin-ajax.php`/`wp-json` URLs | benign, same-origin |
| `jQuery.uiBackCompat = true` | 13 | jQuery UI shim | benign |
| `elementorFrontendConfig = {...}` | 13 | Elementor settings | benign |
| `embedpress_*` / `embedpressObj` localisations (4 blocks) | 2 (partnerships, business-network) | EmbedPress PDF viewer config; `pdfRenderer` points at the same-origin pdf.js viewer | benign |
| `wpforms_settings`, `_wpUtilSettings`, `wpformsElementorVars`, `wp.i18n.setLocaleData` | 1–2 | WPForms/i18n config | benign |
| `application/ld+json` (AIOSEO schema) | 22 | BreadcrumbList/Organization/WebPage | benign (note: its `logo` is the 646×135 "Proposed-Resolution…png", see § 5) |

No `eval`, `atob`, `unescape`, `String.fromCharCode`, `document.write` of
markup, `location.*` redirects, `<meta http-equiv=refresh>`, or hex/unicode-
escaped strings anywhere.

**Iframes (6):** all `https://rajkov.org/wp-content/plugins/embedpress/assets/pdf/web/viewer.html?file=…`
— the same-origin pdf.js viewer — for the five MoU PDFs (`html/partnerships.html:341,362,387,412,433`)
and the Business Network Directory (`html/rajkov-business-network.html:363`).
The long `#key=…` base64 blob on each decodes to EmbedPress viewer options
(`themeMode=default&toolbar=true&download=true…watermark_style=center`) —
not a payload. Replaced by plain download links / native viewers in `www/`.

**Forms (2):** Blocksy search form (`html/blog.html:246`, GET to `/`) and the
WPForms contact form (`html/contact.html:281`, POST to `/contact/`, fields:
name, email, subject, message). Neither can work on a static host; neither
ships.

## 3. Hidden / obfuscated content

| Check | Result |
|---|---|
| Off-screen positioning (`left/top/text-indent: -NNNpx`) | **1 hit — the injected anchor** (`html/home.html:334`). |
| `display:none` / `visibility:hidden` in content | 1 hit: WPForms `#wpforms-error-noscript` ("Please enable JavaScript…") — standard plugin markup, benign. |
| `opacity:0` / `font-size:0` / `height:0` | only `font-size: 0.9rem` in the theme footer CSS (regex false positive). |
| base64 blobs | only the 12 EmbedPress `#key=` option strings (decoded above). |
| Spam keywords (casino/viagra/crypto/trading/forex/loan/porn/…) | only "Smart Trading" in the injected anchor text. |
| `<a hidden>` / `aria-hidden` anchors | none. |
| Zero-width / bidi-override / control characters in `md/` | none; two U+00AD soft hyphens in `md/our-constitution.md:52` (typographic residue, stripped on carry-over). |
| Anchors inside prose that don't belong | only the injected one; every other `<a>` on the home page is nav, social, logo, the MS Form, or the footer mailto (full list checked). |

## 4. PDFs (11) — all to be offered as downloads

`file(1)` reports every `.pdf` as a PDF; `pdfinfo` reports **JavaScript: no,
Encrypted: no, Form: none** for all 11. `strings` was grepped for
`/JS /JavaScript /Launch /OpenAction /AA /URI /EmbeddedFile /RichMedia /SubmitForm /GoToR`:

| File | Pages | Producer | Active-content tokens | Verdict |
|---|---|---|---|---|
| `2024/05/MoU-Rajkov-RANA.pdf` | 2 | Adobe Photoshop (image PDF) | none | clean |
| `2024/05/Rajasthani-Yuva-Samiti-Rajkov-MoU-2024.pdf` | 3 | intsig (CamScanner) | none | clean |
| `2024/05/MoU-RAJKOV-AU-RCT-UK-2024.pdf` | 2 | iOS 17 Quartz | `/EmbeddedFile` ×2 = `pageEntities.json`, 83 bytes each: `{"type":"Document","isBackSide":false,"languages":["en-us"],"usedOnDeviceOCR":true}` — iOS Notes scan metadata | clean (inert JSON) |
| `2024/05/MoU-Rajkov-RAF.pdf` | 2 | iOS 17 Quartz | same two 79–83-byte JSON attachments | clean |
| `2024/05/MoU-Rajkov-RACTNZ-20241.pdf` | 2 | Canva | none | clean |
| `2024/06/Rajkov-Business-Network-Directory-2024.pdf` | 44 | Canva | none | clean |
| `2024/05/Msg-from-HCM-RAJKOV-2023.pdf` | 1 | HP Scan | `/OpenAction` → `<</D[1 0 R /FitH 2715] /S /GoTo>>` (open at top of page 1 — standard); the `/AA` string match is bytes inside the JPEG image stream, not a dictionary key | clean |
| `2024/05/Msg-from-CRF-RAJKOV-2023.pdf` | 1 | Word 2021 | none (`/ObjStm` is normal object streams) | clean |
| `2024/04/Media-Release-…Ram-Mandir-January-2024.pdf` | 1 | Acrobat PDFMaker | none | clean (VHP Australia media release — not RAJKOV content; **not shipped** unless the owner wants it) |
| `2024/04/RAJKOV-Umaid-Palace-2024.pdf`, `2024/05/RAJKOV-Umaid-Palace-2024-1.pdf` | 1 | Epson Scan (identical 158,480-byte scans) | none | clean (not linked from any page; **not shipped**) |

(`qpdf` is not installed on dev01; `pdfinfo` + `strings` were used instead.)

## 5. Images and SVGs

`file(1)` matches the extension for all 13 PNG, 14 JPEG, 2 WebP; `strings`
finds no `<?php`, `<script`, `eval(` or `base64_decode` in any image.

- `media/2024/03/logo.svg`, `logo-dark.svg` — Sketch "logo" placeholder (50×50, generator comment), no `<script>`, no `on*=` handlers, no external `xlink:href`. Not RAJKOV artwork; **not shipped**.
- `media/2024/03/Rajkov-Logo.png` (647×136) — the logo with the **"KUMTUMB"** typo.
- `media/2024/06/Proposed-Resolution-Rajkov-Constitutional-Amendments-2024.png` (646×135) — despite its filename this is the **corrected logo** ("RAJASTHANI KUTUMB OF VICTORIA"), and it is what the live header, AIOSEO schema and OG tags actually use on about-us/by-laws/partnerships/business-network. **This is the logo to ship.**
- `media/2024/03/hero_rajkov.webp` (1024²) — decorated camel at sunset (hero). `hero-1-….webp`, `rajkov-hero-….png` — Rajasthani musicians at sunset (AI-generated stock). `image.png`, `image-1.png`, `image-2.png`, `ravin4all_….png` — AI-generated Rajasthani portraits/scenes. `*-unsplash*.jpg` — Unsplash stock. `icon.jpeg`, `cropped-icon*.jpeg` — turban+moustache favicon.
- `media/2024/05/Rajkov-Business-Network-Directory-2024-{1..4}.png`, `Rajasthani-Yuva-Samiti-Rajkov-MoU.png` — partner logos (RCT UK, RAF, RACT NZ, RANA, Rajasthani Yuva Samiti) despite the misleading filenames.
- `media/2024/06/WhatsApp-Image-2024-05-24….jpeg` — "Introducing the RBN" tile. `2024/09/…jpeg` — Teej 2024 poster (contains role emails + phone numbers). `2025/03/…jpeg` — Gangaur Utsav 2025 poster (phone numbers). `2026/09/…jpeg` — 2026 sponsors poster (CYP Foods & Spices et al.).
- `media/2024/04/image-3-….png` — Rajasthani street-festival stock.

## 6. What is stripped on carry-over

1. The `evolution-zenithofficial.com` anchor and its text ("the Evolution Zenith – Smart Trading") — the sentence is restored to "Founded in 2001 by seven Rajasthani families in Melbourne, the Rajasthani Kutumb of Victoria (RAJKOV) celebrates…".
2. Every `<script>`, `<iframe>`, `<form>`, `<noscript>`, WordPress/Elementor/Blocksy markup and CSS, feeds, `wp-json` links, AIOSEO meta.
3. The two Sketch placeholder SVGs, the typo logo PNG, the two Umaid Palace scans and the VHP media release (unreferenced/not RAJKOV content).
4. Soft hyphens in the constitution text.
5. The WooCommerce/ticketing/blog/sample/privacy (lorem ipsum) pages.

Gate: story 001 acceptance includes `grep -ri "evolution-zenith" www/` → empty,
and every external host in `www/` must be in the keep-list above.

## 7. For the owner — the live site and the domain

- **The WordPress install is compromised.** The spam link is stored in the
  page content (not injected at render time), on a page last edited
  2026-09-14, by WordPress user id 2. Someone had write access — a stolen
  editor/admin password or a vulnerable plugin (stack: WordPress 7.1.3,
  Elementor 4.2.2, Blocksy child theme, AIOSEO 5.0.0.1, WPForms Lite 2.0.0.3,
  EmbedPress, iThemes Security, WooCommerce remnants; PHP 8.2 on LiteSpeed).
  Until the static site replaces it: change every WordPress password, review
  `Users` for unknown accounts, and delete the hidden link from the Home page.
  Once the new site is live and verified, **retire the WordPress hosting**
  rather than keep patching it.
- **Email lives on this domain.** `rajkov.org` MX → `rajkov-org.mail.protection.outlook.com`
  (Microsoft 365), SPF `v=spf1 include:spf.protection.outlook.com -all`, plus
  an `MS=ms23767526` verification TXT. Role addresses `president@`, `vp@`,
  `Secretary@rajkov.org` appear on the Teej 2024 poster. Current nameservers:
  `ns1/ns2.syd5.hostingplatform.net.au`. **When DNS moves to Cloudflare, the
  MX, SPF/TXT, and any DKIM/autodiscover CNAMEs must be re-created first**, or
  committee mail stops. Cancelling the web hosting must not cancel the DNS zone
  until Cloudflare is authoritative.
- WhatsApp group links for RAJKOV Stars and Mel Milaap are missing from the
  WordPress copy — supply them if they should be on the new site.
