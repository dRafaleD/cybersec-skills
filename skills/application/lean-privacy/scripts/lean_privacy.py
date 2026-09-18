#!/usr/bin/env python3
"""Find likely PII locations. Never prints the matched values."""

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
    ("email", "MED", re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)),
    ("phone", "MED", re.compile(r"(?<!\d)(?:\+?\d[\s\-()]*){10,15}\d(?!\d)")),
    ("cardish", "HIGH", re.compile(r"\b(?:\d[ \-]?){13,19}\b")),
    ("id-field", "MED", re.compile(r"(?i)\b(ssn|national[_-]?id|passport|tax[_-]?id)\b\s*[:=]")),
    ("log-body", "HIGH", re.compile(r"(?i)(log|logger|console\.log|print).{0,40}(req\.body|request\.body|user\.email)")),
)

SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".lock", ".woff2", ".map", ".pyc", ".pdf"}


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in SKIP_SUFFIX:
                continue
            yield path


def cmd_pii(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        if rel.lower().endswith(".md"):
            continue
        try:
            if path.stat().st_size > 400_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
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
            print(f"  {sev:4} {rel}:{line} {rule} [REDACTED]")
    print("note never print PII values; this is not a contact list")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-privacy trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-priv-") as tmp:
        root = Path(tmp)
        (root / "app.py").write_text(
            "logger.info(req.body)\nemail = 'user@example.com'\n",
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_pii(root, 25)
        out = buf.getvalue()
        if "log-body" not in out or "email" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        if "user@example.com" in out:
            print("self-test leaked email", file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-privacy PII inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("pii")
    s.add_argument("root", nargs="?", default=".")
    s.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "pii":
        return cmd_pii(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
