#!/usr/bin/env python3
"""Cheap OS/container hardening inventory. No privilege-escalation."""

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
    ("root-ssh", "HIGH", re.compile(r"PermitRootLogin\s+yes")),
    ("password-ssh", "MED", re.compile(r"PasswordAuthentication\s+yes")),
    ("sudo-nopass", "HIGH", re.compile(r"NOPASSWD\s*:\s*ALL")),
    ("docker-root", "HIGH", re.compile(r"^USER\s+root\b", re.I | re.M)),
    ("privileged", "HIGH", re.compile(r"privileged\s*:\s*true|--privileged", re.I)),
    ("cap-add", "MED", re.compile(r"cap_add:|SYS_ADMIN")),
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


def cmd_baseline(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    dockerfiles = []
    for path in iter_files(root):
        try:
            if path.stat().st_size > 400_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        if path.name.lower().startswith("dockerfile"):
            dockerfiles.append((rel, text))
        for i, line in enumerate(text.splitlines(), 1):
            for rule, sev, rx in RULES:
                if rx.search(line):
                    hits.append((sev, rule, rel, i))
                    break
            if len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    for rel, text in dockerfiles:
        if not re.search(r"^USER\s+", text, re.M):
            hits.append(("HIGH", "no-user", rel, 1))
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
    print("note config only; no privilege-escalation")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-hardening trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-hard-") as tmp:
        root = Path(tmp)
        (root / "Dockerfile").write_text("FROM alpine\nUSER root\n", encoding="utf-8")
        (root / "sshd_config").write_text("PermitRootLogin yes\n", encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_baseline(root, 40)
        out = buf.getvalue()
        if "root-ssh" not in out or "docker-root" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-hardening baseline inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline")
    b.add_argument("root", nargs="?", default=".")
    b.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "baseline":
        return cmd_baseline(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
