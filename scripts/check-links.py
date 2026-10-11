#!/usr/bin/env python3
"""Fail if any internal href/src/srcset in www/ points at a file that does not exist.
Usage: scripts/check-links.py www
"""
import re, sys, os, html
from urllib.parse import urlparse, unquote
root = sys.argv[1] if len(sys.argv) > 1 else "www"
pat = re.compile(r'(?:href|src|poster|data)="([^"#]+)(?:#[^"]*)?"|url\(["\']?([^"\')]+)["\']?\)')
bad = 0; n = 0
for d, _, fs in os.walk(root):
    for f in fs:
        if not f.endswith((".html", ".css")): continue
        p = os.path.join(d, f); txt = open(p, encoding="utf-8", errors="ignore").read()
        for m in pat.finditer(txt):
            u = html.unescape(m.group(1) or m.group(2) or "").strip()
            if not u or u.startswith(("http:", "https:", "mailto:", "tel:", "data:", "javascript:", "//")): continue
            path = unquote(urlparse(u).path)
            if not path: continue
            tgt = os.path.join(root, path.lstrip("/")) if path.startswith("/") else os.path.normpath(os.path.join(d, path))
            n += 1
            cands = [tgt, tgt + ".html", os.path.join(tgt, "index.html")]
            if not any(os.path.isfile(c) for c in cands):
                print(f"  BROKEN {os.path.relpath(p, root)} -> {u}"); bad += 1
print(f"  {n - bad}/{n} internal references resolve")
sys.exit(1 if bad else 0)
