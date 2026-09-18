#!/usr/bin/env python3
"""Cheap cloud/CI spend inventory from local config. No billing APIs."""

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
    ("fat-instance", "MED", re.compile(r"instance_type\s*=\s*\"[^\"]*(xlarge|2xlarge|4xlarge)", re.I)),
    ("latest-image", "LOW", re.compile(r"image\s*[:=].*:latest|:latest\"")),
    ("always-on", "MED", re.compile(r"desired_capacity\s*=\s*[1-9]|min_size\s*=\s*[1-9]")),
    ("artifact", "LOW", re.compile(r"actions/upload-artifact|artifacts:")),
    ("debug-log", "LOW", re.compile(r"LOG_LEVEL\s*=\s*debug|verbose:\s*true", re.I)),
    ("nat", "MED", re.compile(r"aws_nat_gateway|CloudNat", re.I)),
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


def cmd_spend(root: Path, max_hits: int) -> int:
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
            print(f"  {sev:4} {rule:14} {rel}:{line}")
    print("note local config only; do not scrape other bills")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-cost trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-cost-") as tmp:
        root = Path(tmp)
        (root / "main.tf").write_text(
            'instance_type = "t3.2xlarge"\nimage = "nginx:latest"\n',
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_spend(root, 20)
        out = buf.getvalue()
        if "fat-instance" not in out or "latest-image" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-cost spend inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spend")
    s.add_argument("root", nargs="?", default=".")
    s.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "spend":
        return cmd_spend(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
