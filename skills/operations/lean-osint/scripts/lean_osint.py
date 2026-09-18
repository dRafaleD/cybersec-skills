#!/usr/bin/env python3
"""Validate compact OSINT cards. Does not scrape the web."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

REQUIRED = ("claim", "source_url", "accessed", "confidence", "next_action")
CONF = {"high", "med", "low"}


def cmd_template() -> int:
    today = date.today().isoformat()
    doc = {
        "question": "What public exposure does example.com have?",
        "scope": "example.com",
        "cards": [
            {
                "claim": "Official site lists a status page at status.example.com",
                "source_url": "https://example.com/",
                "accessed": today,
                "confidence": "high",
                "next_action": "Watch the status page; do not scan unrelated hosts",
                "tags": ["web"],
            }
        ],
    }
    json.dump(doc, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


def cmd_check(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    cards = data.get("cards")
    if not isinstance(cards, list) or not cards:
        print("error cards must be a non-empty list", file=sys.stderr)
        return 1
    print(f"question {data.get('question', '(missing)')}")
    print(f"scope {data.get('scope', '(missing)')}")
    print(f"cards {len(cards)}")
    bad = 0
    for i, card in enumerate(cards, 1):
        missing = [k for k in REQUIRED if not str(card.get(k, "")).strip()]
        conf = str(card.get("confidence", "")).lower()
        url = str(card.get("source_url", ""))
        if missing:
            print(f"  FAIL {i} missing={','.join(missing)}")
            bad += 1
            continue
        if conf not in CONF:
            print(f"  FAIL {i} confidence")
            bad += 1
            continue
        if not url.startswith(("http://", "https://")):
            print(f"  FAIL {i} source_url")
            bad += 1
            continue
        claim = str(card["claim"]).replace("\n", " ")
        if len(claim) > 140:
            claim = claim[:137] + "..."
        print(f"  OK {i} {conf:4} {claim}")
    print(f"failed {bad}")
    print("note keep raw search pages out of chat")
    return 1 if bad else 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-osint trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-osint-") as tmp:
        path = Path(tmp) / "cards.json"
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_template()
        path.write_text(buf.getvalue(), encoding="utf-8")
        rc = cmd_check(path)
        if rc != 0:
            print("self-test failed", file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-osint card helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template")
    c = sub.add_parser("check")
    c.add_argument("path")
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "template":
        return cmd_template()
    if args.cmd == "check":
        return cmd_check(Path(args.path))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
