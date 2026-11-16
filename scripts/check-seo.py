#!/usr/bin/env python3
"""Page metadata + crawl-file checks for the static site in www/ (stdlib only).

Usage: scripts/check-seo.py www [--strict]

Errors (exit 1):
  - a page without a non-empty <title> or <meta name="description">
  - sitemap.xml not well-formed, not a <urlset>, or a <loc> that is not an
    absolute https://rajkov.org URL / does not map to a file in www/
  - robots.txt with an unknown directive or a relative Sitemap: URL
  - bulletin/feed.xml or site.webmanifest that does not parse
Warnings (printed as ::warning:: in GitHub Actions, never fail unless --strict):
  - AGENTS.md "SEO conventions" drift: title > 60 chars, description outside
    120-160 chars, not exactly one <h1>, missing canonical, indexable page not
    in the sitemap, sitemap page marked noindex
"""
import html, json, os, re, sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ORIGIN = "https://rajkov.org"
GHA = os.environ.get("GITHUB_ACTIONS") == "true"
errors, warnings = [], []


def err(msg):
    errors.append(msg)
    print(f"::error::{msg}" if GHA else f"  ERROR {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"::warning::{msg}" if GHA else f"  WARN  {msg}")


class Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.in_title, self.meta, self.canonical, self.h1 = None, False, {}, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title" and self.title is None:
            self.in_title, self.title = True, ""
        elif tag == "meta" and a.get("name"):
            self.meta.setdefault(a["name"].lower(), a.get("content") or "")
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href")
        elif tag == "h1":
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def url_for(rel):
    """www-relative file path -> clean public URL (the origin serves /about for about.html)."""
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return ORIGIN + "/"
    if rel.endswith("/index.html"):
        return f"{ORIGIN}/{rel[:-10]}"
    return f"{ORIGIN}/{rel[:-5]}"


def file_for(root, url):
    path = url[len(ORIGIN):].lstrip("/")
    if not path:
        return os.path.join(root, "index.html")
    cands = [os.path.join(root, path), os.path.join(root, path + ".html"), os.path.join(root, path, "index.html")]
    return next((c for c in cands if os.path.isfile(c)), None)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    strict = "--strict" in sys.argv
    root = args[0] if args else "www"

    pages = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            if f.endswith(".html"):
                p = os.path.join(d, f)
                rel = os.path.relpath(p, root)
                h = Head()
                h.feed(open(p, encoding="utf-8", errors="replace").read())
                pages[rel] = h
                title = html.unescape(h.title or "").strip()
                desc = h.meta.get("description", "").strip()
                if not title:
                    err(f"{rel}: missing <title>")
                elif len(title) > 60:
                    warn(f"{rel}: <title> is {len(title)} chars (> 60)")
                if not desc:
                    err(f"{rel}: missing meta description")
                elif not 120 <= len(desc) <= 160:
                    warn(f"{rel}: meta description is {len(desc)} chars (want 120-160)")
                if h.h1 != 1:
                    warn(f"{rel}: {h.h1} <h1> elements (want exactly 1)")
                noindex = "noindex" in h.meta.get("robots", "").lower()
                if not noindex and not h.canonical:
                    warn(f"{rel}: no <link rel=canonical>")
    print(f"  {len(pages)} pages checked for title + description")

    # sitemap.xml
    sm = os.path.join(root, "sitemap.xml")
    listed = set()
    if os.path.isfile(sm):
        try:
            tree = ET.parse(sm)
            ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
            if tree.getroot().tag != ns + "urlset":
                err(f"sitemap.xml: root is {tree.getroot().tag}, want {ns}urlset")
            for loc in tree.getroot().iter(ns + "loc"):
                u = (loc.text or "").strip()
                listed.add(u)
                if not u.startswith(ORIGIN + "/"):
                    err(f"sitemap.xml: <loc> {u!r} is not an absolute {ORIGIN}/ URL")
                    continue
                f = file_for(root, u)
                if not f:
                    err(f"sitemap.xml: {u} has no file in {root}/")
                else:
                    h = pages.get(os.path.relpath(f, root))
                    if h and "noindex" in h.meta.get("robots", "").lower():
                        warn(f"sitemap.xml: {u} is listed but the page is noindex")
            print(f"  sitemap.xml: {len(listed)} URLs")
        except ET.ParseError as e:
            err(f"sitemap.xml: not well-formed XML ({e})")
        for rel, h in sorted(pages.items()):
            if "noindex" in h.meta.get("robots", "").lower():
                continue
            if url_for(rel) not in listed:
                warn(f"{rel}: indexable page not in sitemap.xml ({url_for(rel)})")

    # robots.txt
    rb = os.path.join(root, "robots.txt")
    if os.path.isfile(rb):
        known = {"user-agent", "allow", "disallow", "sitemap", "crawl-delay", "host"}
        for i, line in enumerate(open(rb, encoding="utf-8"), 1):
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            key, sep, val = line.partition(":")
            key, val = key.strip().lower(), val.strip()
            if not sep or key not in known:
                err(f"robots.txt:{i}: unrecognised line {line!r}")
            elif key == "sitemap" and not re.match(r"https?://", val):
                err(f"robots.txt:{i}: Sitemap must be an absolute URL")
            elif key == "sitemap" and val != ORIGIN + "/sitemap.xml":
                warn(f"robots.txt:{i}: Sitemap points at {val}")
        print("  robots.txt parsed")

    # other machine-read files
    feed = os.path.join(root, "bulletin", "feed.xml")
    if os.path.isfile(feed):
        try:
            ET.parse(feed)
            print("  bulletin/feed.xml well-formed")
        except ET.ParseError as e:
            err(f"bulletin/feed.xml: not well-formed XML ({e})")
    man = os.path.join(root, "site.webmanifest")
    if os.path.isfile(man):
        try:
            json.load(open(man, encoding="utf-8"))
            print("  site.webmanifest is valid JSON")
        except ValueError as e:
            err(f"site.webmanifest: invalid JSON ({e})")

    print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors or (strict and warnings) else 0)


if __name__ == "__main__":
    main()
