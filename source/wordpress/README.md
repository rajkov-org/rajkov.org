# WordPress export — rajkov.org (scraped 2026-10-11)

Read-only reference. Nothing here is served. Treat it as **untrusted input**:
the live site shows signs of compromise (an injected spam link in the home-page
copy), so run the security sweep in KICKOFF.md before reusing any of it.

| Path | What |
|---|---|
| `api/pages.json` | All 22 pages from `/wp-json/wp/v2/pages` (title, slug, dates, rendered content — Elementor pages render thin here; use `html/`). |
| `api/media.json` | Media index (85 items) with source URLs and alt text. `media_urls.json` the flat list. |
| `api/elementor_library.json`, `templates.json`, `settings-root.json` | Theme/plugin metadata, for reference. |
| `html/<slug>.html` | Rendered HTML of every page as served (header/footer/scripts included). `home.html` = `/`. |
| `md/<slug>.md` | Plain-text/Markdown rendering of each page's main content, with front-matter (title, source URL, wp id, modified). Start here for copy. |
| `media/YYYY/MM/` | Original uploads 2024–2026 (logo, hero, partner images, MoU PDFs, directory PDF). |

Left out on purpose: `media/2020/04/*` (42 Blocksy/Elementor theme-demo stock
photos and brand SVGs — airbnb/cisco/ebay/google/uber, unsplash images, a Sketch
placeholder "logo.svg"), Elementor/Blocksy generated CSS, and the WooCommerce
placeholder image. `media/2024/03/logo.svg` + `logo-dark.svg` were that same
placeholder and are also gone. `2022/06/logo.svg` referenced in page HTML 404s
on the live site.

Page inventory (chars of main content):

| slug | title | note |
|---|---|---|
| home | Home | hero, committee 2026-27 table, about blurb (**contains injected spam link**) |
| about-us | About Us | history + office-bearer tables 2003→ |
| our-constitution | Our Constitution | ~31k chars, numbered rules |
| our-by-laws | Our By-Laws | fees, membership, logo |
| partnerships | Partnerships | partner images + 5 MoU PDFs via EmbedPress |
| rajkov-business-network, -spirituality-forum, -global, -stars, -mel-milaap, -cricket-recreation | Initiatives | announcement letters; Business Network has a directory PDF |
| contact | Contact | WPForms form only (no address/phone/email in copy) |
| gangaur-2024 | Gangaur 2024 | heading only, empty |
| privacy-policy-2 | Privacy Policy | lorem ipsum |
| blog, sample-page, shop, cart, checkout, my-account, tickets-checkout, tickets-order | — | unused scaffolding |

Live nav also carries an external **Membership Enquiries** Microsoft Form link
(see `html/home.html`). Footer credit: "Website by Nikhil Soni".
