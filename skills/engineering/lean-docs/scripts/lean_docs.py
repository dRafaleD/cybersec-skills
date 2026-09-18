#!/usr/bin/env python3
"""Find README heading gaps and a few undocumented defs. No file dumps."""

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

NEEDED = ("install", "usage", "license")
DEF_RX = re.compile(r"^(def |export (async )?function |export function |pub fn |func )", re.M)


def cmd_gaps(root: Path, max_hits: int) -> int:
    root = root.resolve()
    readmes = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.lower() in {"readme.md", "readme.rst", "readme.txt"}:
                readmes.append(Path(dirpath) / name)
    print(f"root {root.as_posix()}")
    print(f"readmes {len(readmes)}")
    if not readmes:
        print("  MISS README")
    for path in readmes[:5]:
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        missing = [h for h in NEEDED if h not in text]
        print(f"  {rel} missing={','.join(missing) if missing else 'none'}")
    hits = []
    scanned = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if Path(name).suffix.lower() not in {".py", ".ts", ".js", ".go", ".rs"}:
                continue
            path = Path(dirpath) / name
            try:
                if path.stat().st_size > 200_000:
                    continue
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            scanned += 1
            rel = path.relative_to(root).as_posix()
            for i, line in enumerate(lines):
                if not DEF_RX.match(line):
                    continue
                prev = lines[i - 1] if i else ""
                if prev.strip().startswith(('"""', "'''", "#", "//", "///", "/*")):
                    continue
                hits.append(f"{rel}:{i+1} {line.strip()[:60]}")
                if len(hits) >= max_hits:
                    break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    print(f"files_scanned {scanned}")
    print("undocumented_defs")
    if not hits:
        print("  (none)")
    else:
        for h in hits:
            print(f"  {h}")
    print("note do not rewrite entire docs; fill the gap")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-docs trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-docs-") as tmp:
        root = Path(tmp)
        (root / "README.md").write_text("# App\nHello\n", encoding="utf-8")
        (root / "app.py").write_text("def public():\n    return 1\n", encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_gaps(root, 10)
        out = buf.getvalue()
        if "install" not in out or "public" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-docs gap finder")
    sub = p.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gaps")
    g.add_argument("root", nargs="?", default=".")
    g.add_argument("--max", type=int, default=25)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "gaps":
        return cmd_gaps(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
