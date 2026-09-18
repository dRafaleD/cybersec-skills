#!/usr/bin/env python3
"""Validate compact threat-model cards. No exploit content."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED = ("asset", "actor", "boundary", "abuse", "control")


def cmd_template() -> int:
    doc = {
        "system": "example-api",
        "threats": [
            {
                "asset": "user records",
                "actor": "stolen session",
                "boundary": "app to database",
                "abuse": "read another user's row by id",
                "control": "authorize every object access with the session subject",
            }
        ],
    }
    json.dump(doc, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_check(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    threats = data.get("threats")
    if not isinstance(threats, list) or not threats:
        print("error threats must be a non-empty list", file=sys.stderr)
        return 1
    print(f"system {data.get('system', '(missing)')}")
    print(f"threats {len(threats)}")
    bad = 0
    for i, row in enumerate(threats, 1):
        missing = [k for k in REQUIRED if not str(row.get(k, "")).strip()]
        if missing:
            print(f"  FAIL {i} missing={','.join(missing)}")
            bad += 1
            continue
        abuse = str(row["abuse"]).replace("\n", " ")[:80]
        print(f"  OK {i} {abuse}")
    print(f"failed {bad}")
    print("note controls only; no exploit steps")
    return 1 if bad else 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-tm-") as tmp:
        path = Path(tmp) / "model.json"
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
    p = argparse.ArgumentParser(description="lean-threat-model card helper")
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
