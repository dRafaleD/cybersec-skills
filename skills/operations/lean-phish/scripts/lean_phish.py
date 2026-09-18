#!/usr/bin/env python3
"""Defensive email peek: headers and attachment hashes. Does not send or execute."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from email import policy
from email.parser import BytesParser
from pathlib import Path
from urllib.parse import urlparse

HOST_RX = re.compile(r"@([^>\s]+)")
URL_RX = re.compile(r"https?://[^\s\"'<>]+", re.I)
RISKY_EXT = {".html", ".htm", ".iso", ".img", ".js", ".jse", ".exe", ".scr", ".lnk", ".iso", ".docm", ".xlsm", ".pptm"}


def host_of(addr: str) -> str:
    m = HOST_RX.search(addr or "")
    return (m.group(1) if m else "").lower()


def cmd_peek(path: Path) -> int:
    raw = path.read_bytes()
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    frm = str(msg.get("From", ""))
    reply = str(msg.get("Reply-To", ""))
    rpath = str(msg.get("Return-Path", ""))
    subj = str(msg.get("Subject", ""))[:80]
    auth = str(msg.get("Authentication-Results", ""))[:160]
    print(f"path {path.as_posix()}")
    print(f"from_host {host_of(frm) or '-'}")
    print(f"reply_to_host {host_of(reply) or '-'}")
    print(f"return_path_host {host_of(rpath) or '-'}")
    print(f"subject {subj or '-'}")
    print(f"auth {auth or '(none)'}")
    mismatch = (
        host_of(frm)
        and host_of(reply)
        and host_of(frm) != host_of(reply)
    ) or (
        host_of(frm)
        and host_of(rpath)
        and host_of(frm) != host_of(rpath)
    )
    print(f"host_mismatch {'yes' if mismatch else 'no'}")
    urls = []
    if msg.get_body(preferencelist=("plain", "html")):
        body = msg.get_body(preferencelist=("plain", "html"))
        try:
            text = body.get_content()
        except (LookupError, TypeError, ValueError):
            text = ""
        urls = URL_RX.findall(text or "")[:5]
    print("urls")
    if not urls:
        print("  (none)")
    else:
        for u in urls:
            host = urlparse(u).hostname or "-"
            print(f"  host {host}")
    print("attachments")
    count = 0
    for part in msg.walk():
        name = part.get_filename()
        if not name:
            continue
        count += 1
        payload = part.get_payload(decode=True) or b""
        digest = hashlib.sha256(payload).hexdigest()
        ext = Path(name).suffix.lower()
        risky = "risky" if ext in RISKY_EXT else "ok"
        print(f"  {risky} {name} sha256 {digest} size {len(payload)}")
    if count == 0:
        print("  (none)")
    print("note do not open attachments or visit lure URLs")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-phish trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    eml = (
        "From: CEO <ceo@examp1e.com>\r\n"
        "Reply-To: help@evil.example\r\n"
        "Return-Path: <bounce@evil.example>\r\n"
        "Subject: Wire now\r\n"
        "MIME-Version: 1.0\r\n"
        "Content-Type: multipart/mixed; boundary=b\r\n"
        "\r\n"
        "--b\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "See https://evil.example/login\r\n"
        "--b\r\n"
        "Content-Type: application/octet-stream; name=\"invoice.iso\"\r\n"
        "Content-Disposition: attachment; filename=\"invoice.iso\"\r\n"
        "Content-Transfer-Encoding: base64\r\n\r\n"
        "QQ==\r\n"
        "--b--\r\n"
    )
    with tempfile.TemporaryDirectory(prefix="lean-phish-") as tmp:
        path = Path(tmp) / "msg.eml"
        path.write_bytes(eml.encode("utf-8"))
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_peek(path)
        out = buf.getvalue()
        if "host_mismatch yes" not in out or "invoice.iso" not in out or "evil.example" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-phish defensive peek")
    sub = p.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("peek")
    k.add_argument("path")
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "peek":
        return cmd_peek(Path(args.path))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
