#!/usr/bin/env python3
"""Cheap defensive network-exposure inventory from local config. No live scans."""

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
    ("public-cidr", "HIGH", re.compile(r"0\.0\.0\.0/0|::/0")),
    ("bind-all", "MED", re.compile(r"0\.0\.0\.0(?!/)|\[::\]")),
    ("host-net", "HIGH", re.compile(r"hostNetwork\s*:\s*true|network_mode:\s*host", re.I)),
    ("expose", "LOW", re.compile(r"^\s*EXPOSE\s+\d+", re.I | re.M)),
    ("ports-map", "MED", re.compile(r"ports\s*:")),
    ("nodeport", "MED", re.compile(r"type\s*:\s*(NodePort|LoadBalancer)", re.I)),
    ("listen", "LOW", re.compile(r"listen\s+\d+")),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() in {".png", ".jpg", ".lock", ".woff2", ".map", ".pyc"}:
                continue
            yield path


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def cmd_expose(root: Path, max_hits: int) -> int:
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
        rel = rel_posix(path, root)
        for i, line in enumerate(text.splitlines(), 1):
            for rule, sev, rx in RULES:
                if rx.search(line):
                    snippet = line.strip()
                    if len(snippet) > 80:
                        snippet = snippet[:77] + "..."
                    hits.append((sev, rule, rel, i, snippet))
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
        for sev, rule, rel, line, snippet in hits:
            print(f"  {sev:4} {rule:12} {rel}:{line} {snippet}")
    print("note local config only; do not nmap third parties")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-net trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-net-") as tmp:
        root = Path(tmp)
        (root / "compose.yaml").write_text(
            "services:\n  db:\n    ports:\n      - \"0.0.0.0:5432:5432\"\n    network_mode: host\n",
            encoding="utf-8",
        )
        (root / "sg.tf").write_text('cidr_blocks = ["0.0.0.0/0"]\n', encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_expose(root, 40)
        out = buf.getvalue()
        if "public-cidr" not in out or "host-net" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-net cheap exposure inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("expose")
    e.add_argument("root", nargs="?", default=".")
    e.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "expose":
        return cmd_expose(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
