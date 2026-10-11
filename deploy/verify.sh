#!/usr/bin/env bash
# Smoke-test the deployed site over the real hostname. Never trust `caddy
# reload` exiting 0 — ask the live URL (edge-onboard rule).
#   deploy/verify.sh https://rajkov.suryasoni.info   (default)
#   deploy/verify.sh https://rajkov.org
set -uo pipefail
BASE="${1:-https://rajkov.suryasoni.info}"
WWW="$(dirname "$0")/../www"
CB="cb=$RANDOM$$"
fail=0
printf '\n  verifying %s\n\n' "$BASE"

# 1. /healthz answers (proves tunnel → edge → fragment → container).
code=$(curl -sS -o /dev/null -m 20 -w '%{http_code}' "$BASE/healthz?$CB")
[ "$code" = 200 ] && printf '  ok   /healthz 200\n' || { printf '  FAIL /healthz %s\n' "$code"; fail=1; }

# 2. every page in www/ answers 200 at its clean URL.
n=0; bad=0
while read -r f; do
  r="/${f#./}"; r="${r%index.html}"; r="${r%.html}"
  n=$((n+1))
  code=$(curl -sS -o /dev/null -m 20 -w '%{http_code}' "$BASE$r?$CB")
  [ "$code" = 200 ] || { printf '  FAIL %-50s %s\n' "$r" "$code"; bad=$((bad+1)); }
done < <(cd "$WWW" && find . -name '*.html' ! -name 404.html | sort)
printf '  %d/%d pages return 200\n' "$((n-bad))" "$n"
[ "$bad" -eq 0 ] || fail=1

# 3. indexing: staging must carry noindex, production must NOT.
rob=$(curl -sSI -m 20 "$BASE/?$CB" | tr -d '\r' | grep -i '^x-robots-tag' || true)
case "$BASE" in
  *suryasoni.info*) [ -n "$rob" ] && printf '  ok   staging noindex (%s)\n' "$rob" || { printf '  FAIL staging is indexable\n'; fail=1; } ;;
  *) [ -z "$rob" ] && printf '  ok   production indexable\n' || { printf '  FAIL production carries %s\n' "$rob"; fail=1; } ;;
esac

# 4. the homepage is ours, not the edge's styled 404 or cloudflared's.
# (buffer the body first: `curl | grep -q` under pipefail fails with "Failed
# writing body" as soon as grep closes the pipe on the first match)
body=$(curl -sS -m 20 "$BASE/?$CB")
grep -qi 'Rajasthani Kutumb' <<<"$body" && printf '  ok   homepage content\n' || { printf '  FAIL homepage does not mention Rajasthani Kutumb\n'; fail=1; }

[ "$fail" -eq 0 ] && printf '\n  PASS\n\n' || printf '\n  FAIL\n\n'
exit $fail
