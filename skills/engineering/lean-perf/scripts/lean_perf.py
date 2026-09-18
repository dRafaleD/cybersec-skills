#!/usr/bin/env python3
"""Cheap hot-path inventory: loops with I/O and unbounded queries."""

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
    ("select-star", "MED", re.compile(r"SELECT\s+\*", re.I)),
    ("await-loop", "HIGH", re.compile(r"for\s*\(.*of|for\s+\w+\s+in|forEach\(")),
    ("no-limit", "MED", re.compile(r"\.(all|findMany|find)\(\s*\)")),
    ("sync-io", "MED", re.compile(r"readFileSync|writeFileSync|urllib\.request\.urlopen")),
    ("query-call", "HIGH", re.compile(r"\.(query|execute|fetch|get)\(")),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in {".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rb"}:
                continue
            yield path


def cmd_hot(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        try:
            if path.stat().st_size > 400_000:
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        scanned += 1
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        in_for = 0
        for i, line in enumerate(lines, 1):
            if RULES[1][2].search(line):
                in_for = 8
            if in_for:
                in_for -= 1
                if RULES[4][2].search(line) or "await " in line:
                    hits.append(("HIGH", "n-plus-1", rel, i))
            for rule, sev, rx in RULES:
                if rule in {"await-loop", "query-call"}:
                    continue
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
    print("note do not dump profiles; fix the loop")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-perf trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-perf-") as tmp:
        root = Path(tmp)
        (root / "db.py").write_text(
            "for u in users:\n    db.query(u)\nSELECT * FROM t\n",
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_hot(root, 20)
        out = buf.getvalue()
        if "n-plus-1" not in out or "select-star" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-perf hot path inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hot")
    h.add_argument("root", nargs="?", default=".")
    h.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "hot":
        return cmd_hot(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
