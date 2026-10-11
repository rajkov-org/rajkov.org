#!/usr/bin/env python3
"""FTP/FTPS tooling for the shared LiteSpeed host that serves rajkov.org.

Credentials come from an env file OUTSIDE the repo (default ~/.config/rajkov/ftp.env):
    FTP_HOST=ftp.example.com
    FTP_USER=...
    FTP_PASS=...
    FTP_ROOT=public_html          # the document root, relative to the FTP login dir
    FTP_TLS=1                     # 1 = require FTPS (explicit TLS); 0 = plain FTP (last resort)

Commands:
    list   [path]                 show a directory
    backup <local-dir>            mirror the WHOLE FTP account into <local-dir> (+ manifest.tsv)
    retire                        move every entry in FTP_ROOT into _retired-wordpress-<date>/ and deny web access to it
    upload                        mirror www/ + deploy/htaccess.production (as .htaccess) into FTP_ROOT (adds/updates only)
    prune                         delete files in FTP_ROOT that are not in www/ (never touches _retired-wordpress-*)
Nothing here stores or prints the password.
"""
import os, sys, io, ssl, time, posixpath, ftplib, hashlib, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WWW = os.path.join(ROOT, "www")
HTACCESS = os.path.join(ROOT, "deploy", "htaccess.production")
ENV = os.environ.get("RAJKOV_FTP_ENV", os.path.expanduser("~/.config/rajkov/ftp.env"))

def load_env():
    cfg = {}
    if not os.path.exists(ENV):
        sys.exit(f"missing {ENV} — create it with FTP_HOST/FTP_USER/FTP_PASS/FTP_ROOT (see deploy/ftp/ftp.py)")
    for line in open(ENV):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1); cfg[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("FTP_HOST", "FTP_USER", "FTP_PASS"):
        if k not in cfg: sys.exit(f"{ENV}: {k} missing")
    cfg.setdefault("FTP_ROOT", "public_html"); cfg.setdefault("FTP_TLS", "1")
    return cfg

def connect(cfg):
    host = cfg["FTP_HOST"]
    if cfg["FTP_TLS"] != "0":
        ctx = ssl.create_default_context()
        ftp = ftplib.FTP_TLS(context=ctx, timeout=60)
        ftp.connect(host, 21); ftp.auth(); ftp.login(cfg["FTP_USER"], cfg["FTP_PASS"]); ftp.prot_p()
        mode = "FTPS (explicit TLS, data channel protected)"
    else:
        ftp = ftplib.FTP(timeout=60); ftp.connect(host, 21); ftp.login(cfg["FTP_USER"], cfg["FTP_PASS"])
        mode = "PLAIN FTP — credentials and files travel unencrypted"
    ftp.set_pasv(True)
    print(f"connected to {host} as {cfg['FTP_USER']} via {mode}; server dir {ftp.pwd()}")
    return ftp

def listdir(ftp, path):
    """Return [(name, type, size)] using MLSD, falling back to LIST parsing."""
    out = []
    try:
        for name, facts in ftp.mlsd(path):
            if name in (".", ".."): continue
            t = facts.get("type", "file"); t = "dir" if t in ("dir", "cdir", "pdir") else "file"
            out.append((name, t, int(facts.get("size", 0) or 0)))
        return out
    except ftplib.error_perm:
        pass
    lines = []
    ftp.retrlines(f"LIST -a {path}" if path else "LIST -a", lines.append)
    for l in lines:
        parts = l.split(None, 8)
        if len(parts) < 9: continue
        name = parts[8]
        if name in (".", ".."): continue
        if l.startswith("l"):  # symlink "name -> target": skip, never follow
            continue
        out.append((name, "dir" if l.startswith("d") else "file", int(parts[4]) if parts[4].isdigit() else 0))
    return out

def walk(ftp, path):
    for name, t, size in listdir(ftp, path):
        full = posixpath.join(path, name) if path else name
        if t == "dir":
            yield from walk(ftp, full)
        else:
            yield full, size

def cmd_list(ftp, cfg, args):
    path = args[0] if args else ""
    for name, t, size in sorted(listdir(ftp, path)):
        print(f"{t:4s} {size:>10d}  {name}")

def cmd_backup(ftp, cfg, args):
    if not args: sys.exit("usage: backup <local-dir>")
    dest = os.path.abspath(args[0]); os.makedirs(dest, exist_ok=True)
    manifest = open(os.path.join(dest, "manifest.tsv"), "a")
    n = 0; total = 0; skipped = 0; t0 = time.time()
    for rel, size in walk(ftp, ""):
        local = os.path.join(dest, rel)
        if os.path.exists(local) and os.path.getsize(local) == size and size > 0:
            skipped += 1; continue
        os.makedirs(os.path.dirname(local), exist_ok=True)
        with open(local, "wb") as fh:
            try:
                ftp.retrbinary(f"RETR {rel}", fh.write)
            except ftplib.all_errors as e:
                print(f"  !! {rel}: {e}"); manifest.write(f"ERROR\t{rel}\t{e}\n"); continue
        n += 1; total += os.path.getsize(local)
        manifest.write(f"{size}\t{rel}\n")
        if n % 100 == 0: print(f"  {n} files, {total/1e6:.1f} MB, {time.time()-t0:.0f}s …", flush=True)
    manifest.close()
    print(f"backup complete: {n} files downloaded ({total/1e6:.1f} MB), {skipped} already present → {dest}")

def ensure_dir(ftp, path):
    try: ftp.mkd(path)
    except ftplib.error_perm: pass

def cmd_retire(ftp, cfg, args):
    root = cfg["FTP_ROOT"]; stamp = datetime.date.today().strftime("%Y%m%d")
    ret = f"_retired-wordpress-{stamp}"
    entries = [n for n, t, s in listdir(ftp, root) if not n.startswith("_retired-wordpress-")]
    print(f"retiring {len(entries)} entries from {root}/ into {root}/{ret}/")
    ensure_dir(ftp, f"{root}/{ret}")
    for name in entries:
        ftp.rename(f"{root}/{name}", f"{root}/{ret}/{name}"); print(f"  moved {name}")
    deny = b"# Retired WordPress install: nothing in here may be served or executed.\nRequire all denied\n<IfModule !mod_authz_core.c>\nOrder deny,allow\nDeny from all\n</IfModule>\nphp_flag engine off\n"
    ftp.storbinary(f"STOR {root}/{ret}/.htaccess", io.BytesIO(deny)); print(f"  wrote {ret}/.htaccess (deny all)")

def local_files():
    for d, _, fs in os.walk(WWW):
        for f in fs:
            p = os.path.join(d, f); yield os.path.relpath(p, WWW).replace(os.sep, "/"), p

def cmd_upload(ftp, cfg, args):
    root = cfg["FTP_ROOT"]; n = 0; made = set()
    files = list(local_files()) + [(".htaccess", HTACCESS)]
    for rel, p in sorted(files):
        d = posixpath.dirname(rel); parts = []
        for seg in d.split("/") if d else []:
            parts.append(seg); dp = f"{root}/{'/'.join(parts)}"
            if dp not in made: ensure_dir(ftp, dp); made.add(dp)
        with open(p, "rb") as fh:
            ftp.storbinary(f"STOR {root}/{rel}", fh)
        n += 1
    print(f"uploaded {n} files into {root}/ (www/ + .htaccess)")

def cmd_prune(ftp, cfg, args):
    root = cfg["FTP_ROOT"]; keep = {rel for rel, _ in local_files()} | {".htaccess"}
    removed = 0
    for rel, size in list(walk(ftp, root)):
        sub = rel[len(root)+1:]
        if sub.startswith("_retired-wordpress-") or sub in keep: continue
        ftp.delete(rel); removed += 1; print(f"  deleted {sub}")
    print(f"prune complete: {removed} stray files removed")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "backup", "retire", "upload", "prune"):
        sys.exit(__doc__)
    cfg = load_env(); ftp = connect(cfg)
    try:
        {"list": cmd_list, "backup": cmd_backup, "retire": cmd_retire, "upload": cmd_upload, "prune": cmd_prune}[sys.argv[1]](ftp, cfg, sys.argv[2:])
    finally:
        try: ftp.quit()
        except Exception: pass
