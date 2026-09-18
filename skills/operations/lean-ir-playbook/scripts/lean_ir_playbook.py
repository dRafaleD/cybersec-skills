#!/usr/bin/env python3
"""Validate compact IR playbook JSON. Defense only."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("when", "action", "owner", "done_when")
ORDER = ("isolate", "preserve", "rotate", "communicate", "recover")


def cmd_template() -> int:
    doc = {
        "incident_class": "leaked-api-key",
        "steps": [
            {
                "when": "0-15m",
                "phase": "isolate",
                "action": "revoke the leaked key at the provider",
                "owner": "on-call",
                "done_when": "key disabled; [REDACTED]",
            },
            {
                "when": "15-30m",
                "phase": "preserve",
                "action": "copy CI logs that show the leak to an evidence folder and hash them",
                "owner": "on-call",
                "done_when": "sha256 recorded",
            },
        ],
    }
    json.dump(doc, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_check(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        print("error steps must be a non-empty list", file=sys.stderr)
        return 1
    print(f"incident_class {data.get('incident_class', '(missing)')}")
    print(f"steps {len(steps)}")
    bad = 0
    for i, row in enumerate(steps, 1):
        missing = [k for k in REQUIRED if not str(row.get(k, "")).strip()]
        phase = str(row.get("phase", "")).lower()
        if missing:
            print(f"  FAIL {i} missing={','.join(missing)}")
            bad += 1
            continue
        if phase and phase not in ORDER:
            print(f"  FAIL {i} phase")
            bad += 1
            continue
        print(f"  OK {i} {phase or '-'} {str(row['action'])[:70]}")
    print(f"failed {bad}")
    print("note no wipe or exploit steps")
    return 1 if bad else 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-ir-") as tmp:
        path = Path(tmp) / "pb.json"
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_template()
        path.write_text(buf.getvalue(), encoding="utf-8")
        if cmd_check(path) != 0:
            print("self-test failed", file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-ir-playbook helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template")
    c = sub.add_parser("check")
    c.add_argument("path")
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "template":
        return cmd_template()
    if args.cmd == "check":
        return cmd_check(Path(args.path))
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
