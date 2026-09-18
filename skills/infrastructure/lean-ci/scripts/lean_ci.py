#!/usr/bin/env python3
"""Cheap defensive CI workflow inventory. No live GitHub/GitLab APIs."""

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
    ("write-all", "HIGH", re.compile(r"write-all")),
    ("pr-target", "HIGH", re.compile(r"pull_request_target")),
    ("unpinned", "MED", re.compile(r"uses:\s*\S+@(v\d+|main|master|latest)\b")),
    ("secret-echo", "HIGH", re.compile(r"echo\s+.*\{\{\s*secrets\.", re.I)),
    ("title-interp", "HIGH", re.compile(r"\$\{\{\s*github\.event\.(issue|pull_request|comment)\.", re.I)),
    ("id-token", "MED", re.compile(r"id-token:\s*write")),
    ("curl-bash", "MED", re.compile(r"curl\s+.*\|\s*(ba)?sh", re.I)),
)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix().replace("\\", "/")
            if (
                "/.github/workflows/" in f"/{rel}"
                or name in {".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml"}
                or name.endswith(".gitlab-ci.yml")
            ):
                yield path


def cmd_workflows(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        for i, line in enumerate(text.splitlines(), 1):
            for rule, sev, rx in RULES:
                if rx.search(line):
                    snippet = line.strip()
                    if "secrets." in snippet.lower():
                        snippet = "[REDACTED secret expression]"
                    elif len(snippet) > 80:
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
    print(f"workflows {scanned}")
    print(f"hits {len(hits)}")
    if not hits:
        print("  (none)")
    else:
        for sev, rule, rel, line, snippet in hits:
            print(f"  {sev:4} {rule:14} {rel}:{line} {snippet}")
    print("note do not exploit CI; pin and drop write-all")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-ci trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-ci-") as tmp:
        root = Path(tmp)
        wf = root / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text(
            "on: pull_request_target\npermissions: write-all\njobs:\n"
            "  a:\n    steps:\n      - uses: actions/checkout@v4\n"
            "      - run: echo ${{ secrets.TOKEN }}\n",
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_workflows(root, 40)
        out = buf.getvalue()
        if "write-all" not in out or "pr-target" not in out or "unpinned" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        if "secrets.TOKEN" in out:
            print("self-test leaked secret expression", file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-ci workflow inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("workflows")
    w.add_argument("root", nargs="?", default=".")
    w.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "workflows":
        return cmd_workflows(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
