#!/usr/bin/env python3
"""Watch sponsors' official logo sources for changes (owner's standing instruction, 2026-10-11).

`deploy/sponsor-logo-sources.json` lists, per sponsor, the public URL we took the official logo from and
the sha256 of the bytes we fetched then. This script re-fetches each URL and reports which have changed
(or vanished). It changes nothing on the site: a change means "re-cut the logo with the same treatment,
bump LOGO_V in the generator, redeploy, tell the owner" (see AGENTS.md § Lessons).

Usage: python3 tools/logo-watch.py [--update]   (--update rewrites the stored hashes after a refresh)
Exit code 0 = no change, 2 = at least one source changed or failed.
"""
import hashlib, json, sys, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deploy" / "sponsor-logo-sources.json"
UA = "Mozilla/5.0 (compatible; rajkov-logo-watch/1.0; +https://rajkov.org)"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def main():
    update = "--update" in sys.argv
    data = json.loads(SRC.read_text())
    changed = 0
    for s in data["sponsors"]:
        url = s.get("source_url")
        if not url:
            print(f"  ?  {s['name']}: no official source on record ({s.get('note','')})"); continue
        try:
            digest = hashlib.sha256(fetch(url)).hexdigest()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            print(f"  !  {s['name']}: fetch failed — {e}"); changed += 1; continue
        if digest == s.get("sha256"):
            print(f"  ok {s['name']}")
        else:
            print(f"  ** {s['name']}: CHANGED at {url}"); changed += 1
            if update: s["sha256"] = digest
    if update:
        SRC.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    print(f"{changed} change(s)/failure(s)")
    sys.exit(2 if changed else 0)

if __name__ == "__main__":
    main()
