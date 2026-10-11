# Status board — rajkov.org

> ≤20 lines, always. In-flight + next + blocked. NOT a history: story detail lives
> in the story files, deploy facts live in `deploy/DEPLOYED.md`.

## Done
(nothing shipped yet)

## Now
001 — WordPress → static rebuild (`stories/001-static-rebuild.md`): built + `make check` green,
waiting on the staging hostname on the prd01 tunnel → `make edge-deploy`.

## Next
- 002 — Events gallery (Gangaur etc.) if the owner supplies photos
- 003 — Production cut-over checklist (owner moves DNS → Cloudflare → prd01), retire WordPress hosting

## Blocked / decisions needed
- Owner to supply the RAJKOV Stars + Mel Milaap WhatsApp group links (missing from the export)
- Staging hostname `rajkov.suryasoni.info` must exist on prd01's Cloudflare tunnel before `make edge-deploy` can pass verify
