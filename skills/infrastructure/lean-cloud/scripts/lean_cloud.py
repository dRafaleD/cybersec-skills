#!/usr/bin/env python3
"""Cheap defensive cloud/IAM inventory from local config. No live cloud APIs."""

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
    ("wildcard-action", "HIGH", re.compile(r'Action["\s:=\[\]*]*\*|"Action"\s*:\s*"\*"', re.I)),
    ("wildcard-resource", "HIGH", re.compile(r'Resource["\s:=\[\]*]*\*|"Resource"\s*:\s*"\*"', re.I)),
    ("principal-star", "HIGH", re.compile(r'Principal["\s:{]*\*|"AWS"\s*:\s*"\*"', re.I)),
    ("admin", "HIGH", re.compile(r"AdministratorAccess|roles/owner|Owner\s*=", re.I)),
    ("public-acl", "HIGH", re.compile(r"public-read|allUsers|allAuthenticatedUsers|acl\s*=\s*\"public", re.I)),
    ("imds", "MED", re.compile(r"169\.254\.169\.254|IMDSv1|http_tokens\s*=\s*optional", re.I)),
    ("open-cidr", "HIGH", re.compile(r"0\.0\.0\.0/0")),
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


def cmd_iam(root: Path, max_hits: int) -> int:
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
                    snippet = snippet.replace("*", "[star]")
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
            print(f"  {sev:4} {rule:18} {rel}:{line} {snippet}")
    print("note local config only; do not call live cloud APIs")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-cloud trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-cloud-") as tmp:
        root = Path(tmp)
        (root / "iam.tf").write_text(
            'Action = "*"\nResource = "*"\ncidr_blocks = ["0.0.0.0/0"]\n',
            encoding="utf-8",
        )
        (root / "bucket.json").write_text('{"acl": "public-read"}\n', encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_iam(root, 40)
        out = buf.getvalue()
        if "wildcard-action" not in out or "public-acl" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-cloud cheap IAM inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("iam")
    i.add_argument("root", nargs="?", default=".")
    i.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "iam":
        return cmd_iam(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
