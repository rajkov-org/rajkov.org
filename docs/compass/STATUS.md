# Status board — rajkov.org

> ≤20 lines, always. In-flight + next + blocked. NOT a history: story detail lives
> in the story files, deploy facts live in `deploy/DEPLOYED.md`.

## Done
001 — WordPress → static rebuild: live on staging `rajkov.suryasoni.info` 2026-10-11 (see stories/001, deploy/DEPLOYED.md)

## Now
nothing in flight — owner reviewing staging

## Next
- 002 — Events gallery (Gangaur etc.) if the owner supplies photos
- 003 — Production cut-over: owner adds rajkov.org + www to the tunnel, recreates MX/SPF/TXT in Cloudflare, moves DNS; then `make edge-verify EDGE_URL=https://rajkov.org`; then retire WordPress hosting

## Blocked / decisions needed
- Owner to supply the RAJKOV Stars + Mel Milaap WhatsApp group links (missing from the export)
