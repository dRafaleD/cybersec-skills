#!/usr/bin/env python3
"""Cheap defensive crypto inventory. Stdlib only. No cracking."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor",
    ".next", ".venv", "venv", "coverage", "__pycache__",
}

RULES = (
    ("md5", "HIGH", re.compile(r"\bmd5\b|MD5|hashlib\.md5", re.I)),
    ("sha1", "MED", re.compile(r"\bsha1\b|SHA-?1|hashlib\.sha1", re.I)),
    ("ecb", "HIGH", re.compile(r"AES/ECB|MODE_ECB|aes-?ecb", re.I)),
    ("des", "HIGH", re.compile(r"\b(3DES|DES|RC4)\b")),
    ("weak-rng", "HIGH", re.compile(r"Math\.random\(|random\.random\(|rand\(\)")),
    ("skip-verify", "HIGH", re.compile(r"verify\s*=\s*False|InsecureSkipVerify|rejectUnauthorized\s*:\s*false", re.I)),
    ("alg-none", "HIGH", re.compile(r"alg['\"]?\s*:\s*['\"]none['\"]", re.I)),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in {".png", ".jpg", ".lock", ".woff2", ".map", ".pyc", ".md"}:
                continue
            yield path


def cmd_weak(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        try:
            if path.stat().st_size > 400_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for rule, sev, rx in RULES:
                if rx.search(line):
                    hits.append((sev, rule, rel, i))
                    break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    order = {"HIGH": 0, "MED": 1, "LOW": 2}
    hits.sort(key=lambda h: (order.get(h[0], 9), h[2], h[3]))
    print(f"root {root.resolve().as_posix()}")
    print(f"files_scanned {scanned}")
    print(f"hits {len(hits)}")
    if not hits:
        print("  (none)")
    else:
        for sev, rule, rel, line in hits:
            print(f"  {sev:4} {rule:12} {rel}:{line}")
    print("note do not crack or forge; upgrade the primitive")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-crypto trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-crypto-") as tmp:
        root = Path(tmp)
        (root / "auth.py").write_text("hashlib.md5(pw)\ntoken = random.random()\n", encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_weak(root, 25)
        out = buf.getvalue()
        if "md5" not in out or "weak-rng" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-crypto weak primitive inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("weak")
    w.add_argument("root", nargs="?", default=".")
    w.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "weak":
        return cmd_weak(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
