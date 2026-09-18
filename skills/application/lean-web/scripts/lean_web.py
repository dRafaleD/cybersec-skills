#!/usr/bin/env python3
"""Cheap defensive web inventory. Stdlib only. No live HTTP."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor",
    ".next", ".venv", "venv", "coverage", "__pycache__",
}

PATH_TAGS = (
    ("cookie", re.compile(r"cookie|session", re.I)),
    ("cors", re.compile(r"cors", re.I)),
    ("csp", re.compile(r"csp|helmet|content-security", re.I)),
    ("csrf", re.compile(r"csrf", re.I)),
    ("proxy", re.compile(r"nginx|caddy|traefik|haproxy|httpd\.conf|apache", re.I)),
    ("upload", re.compile(r"upload|multer|multipart", re.I)),
    ("html", re.compile(r"\.(tsx|jsx|vue|html|ejs|hbs)$", re.I)),
)

HEADER_RX = (
    ("cors-star", re.compile(r"Access-Control-Allow-Origin['\"\s:=*]*\*|origin:\s*['\"]?\*", re.I)),
    ("cookie-set", re.compile(r"Set-Cookie|setHeader\(\s*['\"]Set-Cookie", re.I)),
    ("csp", re.compile(r"Content-Security-Policy|contentSecurityPolicy", re.I)),
    ("unsafe-inline", re.compile(r"unsafe-inline|unsafe-eval", re.I)),
    ("x-frame", re.compile(r"X-Frame-Options|frame-ancestors", re.I)),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def cmd_scope(root: Path) -> int:
    grouped = defaultdict(list)
    counts = defaultdict(int)
    scanned = 0
    for path in iter_files(root):
        scanned += 1
        rel = rel_posix(path, root)
        for tag, rx in PATH_TAGS:
            if rx.search(rel):
                counts[tag] += 1
                if len(grouped[tag]) < 8:
                    grouped[tag].append(rel)
    print(f"root {root.resolve().as_posix()}")
    print(f"files_scanned {scanned}")
    print("tags " + " ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])) if counts else "tags none")
    print("hotspots")
    if not counts:
        print("  (none)")
    else:
        for tag, _ in sorted(counts.items(), key=lambda kv: -kv[1]):
            for rel in grouped[tag]:
                print(f"  {tag:8} {rel}")
    print("note do not dump config files; slice-read hotspots only")
    return 0


def cmd_headers(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        if path.suffix.lower() in {".png", ".jpg", ".lock", ".woff", ".woff2", ".map"}:
            continue
        try:
            if path.stat().st_size > 400_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        rel = rel_posix(path, root)
        for i, line in enumerate(text.splitlines(), 1):
            for rule, rx in HEADER_RX:
                if rx.search(line):
                    hits.append((rule, rel, i))
                    break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    print(f"root {root.resolve().as_posix()}")
    print(f"files_scanned {scanned}")
    print(f"hits {len(hits)}")
    if not hits:
        print("  (none)")
    else:
        for rule, rel, line in hits:
            print(f"  {rule:14} {rel}:{line}")
    print("note confirm flags in-file; do not paste full middleware")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-web trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-web-") as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "src" / "cors.js").write_text("app.use(cors({ origin: '*' }))\n", encoding="utf-8")
        (root / "src" / "session.js").write_text("res.setHeader('Set-Cookie', 'sid=1')\n", encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_scope(root)
            cmd_headers(root, 25)
        out = buf.getvalue()
        if "cors.js" not in out or "cors-star" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-web cheap inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scope")
    s.add_argument("root", nargs="?", default=".")
    h = sub.add_parser("headers")
    h.add_argument("root", nargs="?", default=".")
    h.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "scope":
        return cmd_scope(Path(args.root))
    if args.cmd == "headers":
        return cmd_headers(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
