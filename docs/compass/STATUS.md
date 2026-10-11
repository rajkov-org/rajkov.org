# Status board — rajkov.org

> ≤20 lines, always. In-flight + next + blocked. NOT a history: story detail lives
> in the story files, deploy facts live in `deploy/DEPLOYED.md`.

## Done
001 — WordPress → static rebuild: live on staging `rajkov.suryasoni.info` 2026-10-11 (see stories/001, deploy/DEPLOYED.md)
003 — Production cut-over on the shared host via FTPS: **https://rajkov.org live 2026-10-11** (stories/003, deploy/DEPLOYED.md)

## Now
- 004 — Weekly Rajasthan Bulletin (en + Rajasthani, Sunday 17:00 Melbourne): draft edition generated 2026-10-11, awaiting committee approval (stories/004)
- Logo: split the banner into couple mark + live text + official Vijay Stambh — analysis sent to owner 2026-10-11; awaiting go-ahead (no story: small change)

## Next
- 002 — Events gallery (Gangaur etc.) if the owner supplies photos
- 005 — Later: move production to Cloudflare → prd01 (recreate MX/SPF/TXT first), then cancel the shared hosting

## Blocked / decisions needed
- Owner: rotate the FTP password (it was shared in chat) + hosting/WordPress passwords; decide when to delete `wordpress-backups/public_html-20261011` and the WordPress database
- Owner to supply the RAJKOV Stars + Mel Milaap WhatsApp group links (missing from the export)
- Committee: approve bulletin draft, vet `bulletin/idioms.json` (native speaker), keep `bulletin/events.json` current; a high-res original of the Vijay Stambh logo if one exists
