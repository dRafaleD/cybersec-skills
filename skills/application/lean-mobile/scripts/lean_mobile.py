#!/usr/bin/env python3
"""Cheap defensive mobile manifest inventory. No device attacks."""

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
    ("exported", "HIGH", re.compile(r"android:exported\s*=\s*\"true\"")),
    ("backup", "MED", re.compile(r"android:allowBackup\s*=\s*\"true\"")),
    ("cleartext", "HIGH", re.compile(r"usesCleartextTraffic\s*=\s*\"true\"")),
    ("debuggable", "HIGH", re.compile(r"android:debuggable\s*=\s*\"true\"")),
    ("ats", "HIGH", re.compile(r"NSAllowsArbitraryLoads</key>\s*<true", re.I | re.S)),
    ("url-scheme", "MED", re.compile(r"CFBundleURLSchemes|android:scheme=")),
    ("file-share", "MED", re.compile(r"UIFileSharingEnabled</key>\s*<true", re.I | re.S)),
)

INTERESTING = re.compile(r"(AndroidManifest\.xml|Info\.plist|network_security_config|\.entitlements)$", re.I)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def cmd_manifest(root: Path, max_hits: int) -> int:
    hits = []
    scanned = 0
    for path in iter_files(root):
        rel = path.resolve().relative_to(root.resolve()).as_posix()
        if not INTERESTING.search(rel) and path.suffix.lower() not in {".xml", ".plist"}:
            continue
        try:
            if path.stat().st_size > 400_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        # Multiline ATS: search whole file once
        if RULES[4][2].search(text):
            hits.append(("HIGH", "ats", rel, 1))
        if RULES[6][2].search(text):
            hits.append(("MED", "file-share", rel, 1))
        for i, line in enumerate(text.splitlines(), 1):
            for rule, sev, rx in RULES[:4] + RULES[5:6]:
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
    print("note workspace manifests only; do not jailbreak")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-mobile trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-mobile-") as tmp:
        root = Path(tmp)
        (root / "AndroidManifest.xml").write_text(
            '<activity android:exported="true"/>\n'
            '<application android:allowBackup="true"/>\n'
            '<application android:usesCleartextTraffic="true"/>\n',
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_manifest(root, 40)
        out = buf.getvalue()
        if "exported" not in out or "cleartext" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-mobile manifest inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest")
    m.add_argument("root", nargs="?", default=".")
    m.add_argument("--max", type=int, default=40)
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "manifest":
        return cmd_manifest(Path(args.root), args.max)
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
