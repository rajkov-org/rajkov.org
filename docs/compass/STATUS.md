# Status board — rajkov.org

> ≤20 lines, always. In-flight + next + blocked. NOT a history: story detail lives
> in the story files, deploy facts live in `deploy/DEPLOYED.md`.

## Done
001 — WordPress → static rebuild: live on staging `rajkov.suryasoni.info` 2026-10-11 (see stories/001, deploy/DEPLOYED.md)

## Now
003 — FTP cut-over of rajkov.org on the existing LiteSpeed host (`stories/003-ftp-cutover.md`): tooling written; waiting on FTP credentials in `~/.config/rajkov/ftp.env`

## Next
- 002 — Events gallery (Gangaur etc.) if the owner supplies photos
- 004 — Later: move production to Cloudflare → prd01 (recreate MX/SPF/TXT first), then cancel the shared hosting

## Blocked / decisions needed
- Owner to supply the RAJKOV Stars + Mel Milaap WhatsApp group links (missing from the export)
