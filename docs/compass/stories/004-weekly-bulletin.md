# Story 004 — weekly-bulletin (RAJKOV Weekly Rajasthan Bulletin, English + Rajasthani)

**Status:** in-progress — draft edition generated 2026-10-11 for committee approval; nothing
scheduled or published yet.
**Depends on:** 001 (site live), 003 (production on the shared host via FTPS).

## Goal

Every **Sunday at 5 pm Melbourne time** the site publishes a ~2-minute spoken bulletin, in
**English** and in **Rajasthani (standard Marwari, Devanagari)**, that opens with *Khamma
Ghani* and *Ram Ram sa*, and covers — for fun, for every generation, but factually and
professionally — the week's **cultural** news from Rajasthan, **big investment / development**
news, the **Rajasthani diaspora** around the world, RAJKOV's own **noticeboard** (this week's
event, or a *manuhaar* to register for the next one), a **market corner** (gold and silver:
A$/oz in English, ₹/10 g and ₹/kg in Rajasthani, plus the A$→₹ rate, as of 5 pm Sunday) and
a **kahavat of the week** (a Rajasthani saying, explained). Each edition is a page under
`/bulletin/` with a player and transcript, an archive index and a podcast feed.

Interpretation of the owner's instructions (2026-10-11, mid-session):
- Modelled on tickerlab's daily briefing (feeds → grounded LLM script → Kokoro TTS).
- **Generator code stays on dev01, gitignored** (`bulletin/`); only the weekly **text** is
  committed; **audio is never committed** and production keeps only the **last 4 weeks** of
  recordings. Scripts/transcripts are kept forever (they are tiny).
- The bulletin never invents: headlines come from RSS, prices from a live source, the
  kahavat from a curated list (`bulletin/idioms.json`, rotated by ISO week, **to be vetted by
  a native speaker on the committee**), and RAJKOV events from `bulletin/events.json`
  (committee-maintained; standing membership appeal when nothing is scheduled).
- A **draft edition is produced first** and sent to the owner for committee approval
  before any timer exists.

Added 2026-10-11 (owner): each edition page must share well on **WhatsApp** — a
"Share on WhatsApp" link, a "Share audio" button that hands the MP3 to the phone's share
sheet as an attachment (Web Share API with files; falls back to download), and proper
link-preview metadata (og:title/description, an og:image per edition at 1200×630 under
300 KB with width/height, og:audio, twitter card).

## Scope — touch ONLY these

- `bulletin/` (gitignored, local): `generate.py`, `idioms.json`, `events.json`,
  `prices.jsonl`, `out/<date>/…` — generation; later `publish.py` (page + archive + feed +
  FTP upload + prune) and `bulletin.service`/`bulletin.timer` for dev01 (`systemd --user`).
- `.gitignore` — `bulletin/`, `www/bulletin/**/*.mp3`.
- `www/bulletin/index.html`, `www/bulletin/<date>/index.html`, `www/bulletin/feed.xml` —
  generated output (text committed; mp3 uploaded only).
- `www/index.html` — one card linking to the latest bulletin; `www/sitemap.xml`.
- Generator (`scratchpad gen/`) if the header nav gains a "Bulletin" link.
- `deploy/htaccess.production` — mp3 mime + cache header if needed.
- `AGENTS.md` (bulletin section + lessons), `deploy/DEPLOYED.md`, this story, STATUS.md.
- Gateway: `rajkov` key minted on prd01 (`sonnet,haiku,kokoro`, $10/30d) → `~/.config/rajkov/llm.env`.

## Acceptance check (how we verify)

- [x] Draft edition generated end to end on dev01 from live feeds, live prices and the idiom
      list, both languages, with MP3s — evidence: `bulletin/out/2026-10-11/meta.json` (see
      Notes), files sent to the owner 2026-10-11.
- [x] Owner approved the audio 2026-10-11: voices en `af_heart` (same as the ebook
      audiobooks, locked) and raj `hf_alpha`; speech-only pronunciation map
      (`bulletin/pronounce.json`) judged good on before/after samples.
- [ ] Committee approves tone, greeting and sections, or returns changes; idiom list
      vetted by a native speaker.
- [ ] `publish.py` writes `www/bulletin/<date>/index.html` + transcript, updates the archive
      index and `feed.xml`, commits text only, uploads the mp3s + pages by FTPS, prunes audio
      older than 4 weeks on prod — proven by a dry run then a real run, and `ls` on the host.
- [ ] Timer on dev01 fires Sunday 17:00 Australia/Melbourne (`systemctl --user list-timers`),
      run time < 30 min, non-zero exit + owner email on a failed run (nothing published).
- [ ] Live page passes `make check` (header/footer identical, links, html-validate), player
      works on iPhone Safari and Android Chrome, podcast feed validates.
- [ ] Rotation proof: after the 5th week the first week's mp3 is gone from prod, its
      transcript page still serves.

## Notes

- Draft run 2026-10-11 (v2, after tone/topic-balance/noticeboard changes): see
  `bulletin/out/2026-10-11/meta.json` for chars/seconds per language; v1 English ran 145 s
  from 2,284 chars, so the two-minute target is ~1,800 en / ~1,450 raj chars.
- Prices: gold-api.com (USD spot) × open.er-api.com (USD→INR, USD→AUD). Indian jeweller rates
  run ~9 % above the converted spot (customs + GST) — the script says so.
- Open questions for the committee: male or female Rajasthani voice; whether to name
  sponsors in the sign-off; whether the English edition should also carry ₹ prices.
