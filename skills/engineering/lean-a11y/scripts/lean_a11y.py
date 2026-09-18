#!/usr/bin/env python3
"""Cheap a11y inventory on UI files. No full tree dumps."""

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
    ("img-alt", "HIGH", re.compile(r"<img\b(?![^>]*\balt=)", re.I)),
    ("click-div", "HIGH", re.compile(r"<(div|span)[^>]*(onClick|onclick)=", re.I)),
    ("input-bare", "MED", re.compile(r"<input\b(?![^>]*(aria-label|id=))", re.I)),
    ("blank", "LOW", re.compile(r'target=["\']_blank["\'](?![^>]*rel=)', re.I)),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in {".tsx", ".jsx", ".html", ".vue", ".svelte"}:
                continue
            yield path


def cmd_ui(root: Path, max_hits: int) -> int:
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
    print("note prefer native elements; do not dump JSX trees")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-a11y trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-a11y-") as tmp:
        root = Path(tmp)
        (root / "App.tsx").write_text(
            '<img src="x.png"/>\n<div onClick={go}>x</div>\n',
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_ui(root, 20)
        out = buf.getvalue()
        if "img-alt" not in out or "click-div" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-a11y UI inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("ui")
    u.add_argument("root", nargs="?", default=".")
    u.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "ui":
        return cmd_ui(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
