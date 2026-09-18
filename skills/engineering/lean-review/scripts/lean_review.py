#!/usr/bin/env python3
"""Git diff stats without dumping the patch. Stdlib + git."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SKIP_NAMES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "go.sum",
}


def git(root: Path, args: list[str]) -> str:
    r = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "git failed")
    return r.stdout


def cmd_stats(root: Path) -> int:
    root = root.resolve()
    try:
        git(root, ["rev-parse", "--is-inside-work-tree"])
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"error not a git repo: {exc}", file=sys.stderr)
        return 1
    name_status = git(root, ["diff", "--name-status", "HEAD"])
    staged = git(root, ["diff", "--cached", "--name-status"])
    numstat = git(root, ["diff", "--numstat", "HEAD"])
    rows = []
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        added, deleted, path = parts
        if Path(path).name in SKIP_NAMES:
            continue
        a = int(added) if added.isdigit() else 0
        d = int(deleted) if deleted.isdigit() else 0
        rows.append((a + d, a, d, path))
    rows.sort(reverse=True)
    print(f"root {root.as_posix()}")
    print(f"files {len(rows)}")
    print("name_status")
    blob = (name_status + staged).strip() or "(clean working tree vs HEAD)"
    for line in blob.splitlines()[:40]:
        print(f"  {line}")
    print("hotspots")
    if not rows:
        print("  (none)")
    else:
        for total, a, d, path in rows[:20]:
            print(f"  {total:5} +{a} -{d} {path}")
    print("note do not dump the full diff; slice-read hotspots")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-review trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    # stats needs git; just check parser helpers via empty trim
    from contextlib import redirect_stdout
    from io import StringIO
    import tempfile

    with tempfile.TemporaryDirectory(prefix="lean-review-") as tmp:
        p = Path(tmp) / "x.txt"
        p.write_text("abcd", encoding="utf-8")
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_trim(str(p), 2)
        if "ab" not in buf.getvalue():
            print("self-test failed trim", file=sys.stderr)
            return 1
    print("self-test ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-review diff stats")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stats")
    s.add_argument("root", nargs="?", default=".")
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "stats":
        return cmd_stats(Path(args.root))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
