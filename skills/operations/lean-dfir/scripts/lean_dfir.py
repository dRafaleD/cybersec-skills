#!/usr/bin/env python3
"""Hash evidence and summarize text logs. Does not parse disk/memory images."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", "node_modules"}
TS_RX = re.compile(
    r"(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
    r"|\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}"
    r"|\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
)
TOKEN_RX = re.compile(r"\b(?:ERROR|WARN|INFO|FATAL|Accepted|Failed|event_id|EventID)[=:]?\s*\w+\b", re.I)
MAX_FILE = 5_000_000
MAX_FILES = 40


def sha256_file(path: Path) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def cmd_hash(path: Path) -> int:
    path = path.resolve()
    targets = []
    if path.is_file():
        targets = [path]
    elif path.is_dir():
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                targets.append(Path(dirpath) / name)
                if len(targets) >= MAX_FILES:
                    break
            if len(targets) >= MAX_FILES:
                break
    else:
        print(f"error not found: {path}", file=sys.stderr)
        return 1
    print(f"root {path.as_posix()}")
    print(f"files {len(targets)}")
    for item in targets:
        size, digest = sha256_file(item)
        rel = item.as_posix() if path.is_file() else item.relative_to(path).as_posix()
        print(f"  sha256 {digest}  {size}  {rel}")
    print("note work on copies; do not modify evidence")
    return 0


def summarize_log(path: Path) -> dict:
    size = path.stat().st_size
    rec = {"path": path.name, "size": size, "lines": 0, "first_ts": "", "last_ts": "", "tokens": []}
    if size > MAX_FILE:
        rec["note"] = "too-large"
        return rec
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        rec["note"] = str(exc)
        return rec
    lines = text.splitlines()
    rec["lines"] = len(lines)
    times = []
    bag: Counter[str] = Counter()
    for line in lines:
        m = TS_RX.search(line)
        if m:
            times.append(m.group(1))
        for tok in TOKEN_RX.findall(line):
            bag[tok[:40]] += 1
    if times:
        rec["first_ts"] = times[0]
        rec["last_ts"] = times[-1]
    rec["tokens"] = [f"{k}:{v}" for k, v in bag.most_common(5)]
    return rec


def cmd_logs(root: Path) -> int:
    root = root.resolve()
    files = []
    if root.is_file():
        files = [root]
    else:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                path = Path(dirpath) / name
                if path.suffix.lower() in {".log", ".txt", ".json", ".csv", ""} or "log" in name.lower():
                    files.append(path)
                if len(files) >= MAX_FILES:
                    break
            if len(files) >= MAX_FILES:
                break
    print(f"root {root.as_posix()}")
    print(f"files {len(files)}")
    for path in files:
        rec = summarize_log(path)
        token_s = ",".join(rec["tokens"]) if rec["tokens"] else "-"
        extra = rec.get("note", "")
        print(
            f"  {rec['path']} size={rec['size']} lines={rec['lines']} "
            f"first={rec['first_ts'] or '-'} last={rec['last_ts'] or '-'} top={token_s} {extra}"
        )
    print("note do not paste full logs; rg for the few lines you need")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-dfir trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-dfir-") as tmp:
        root = Path(tmp)
        ev = root / "copy.log"
        ev.write_text(
            "2026-09-18T01:00:00 ERROR login Failed\n2026-09-18T01:02:00 INFO Accepted\n",
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_hash(ev)
            cmd_logs(root)
        out = buf.getvalue()
        if "sha256" not in out and len(out.split()) < 2:
            print("self-test failed hash", file=sys.stderr)
            return 1
        if "copy.log" not in out or "ERROR" not in out:
            print("self-test failed logs", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-dfir hash and log summary")
    sub = p.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hash")
    h.add_argument("path")
    lg = sub.add_parser("logs")
    lg.add_argument("path")
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "hash":
        return cmd_hash(Path(args.path))
    if args.cmd == "logs":
        return cmd_logs(Path(args.path))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
