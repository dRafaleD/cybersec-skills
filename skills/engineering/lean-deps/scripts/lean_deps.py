#!/usr/bin/env python3
"""Summarize direct deps from manifests. Never dump lockfiles."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", "target", "vendor",
    ".next", ".venv", "venv", "coverage", "__pycache__",
}

LOCKFILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock",
    "poetry.lock", "Pipfile.lock", "Cargo.lock", "go.sum", "composer.lock",
    "Gemfile.lock",
}
MANIFESTS = {
    "package.json", "pyproject.toml", "requirements.txt", "Pipfile",
    "Cargo.toml", "go.mod", "composer.json", "Gemfile",
}
INTERESTING = re.compile(
    r"jwt|auth|passport|bcrypt|argon|helmet|cors|crypto|openssl|xml|yaml|pickle|docker|aws|azure|gcp",
    re.I,
)


def walk(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            yield Path(dirpath) / name


def names_from_package(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for key in ("dependencies", "devDependencies"):
        out.extend(sorted((data.get(key) or {})))
    return out


def names_from_requirements(path: Path) -> list[str]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        out.append(re.split(r"[<>=[~! ]", line, maxsplit=1)[0])
    return [n for n in out if n]


def cmd_summary(root: Path) -> int:
    root = root.resolve()
    manifests, locks, direct = [], [], []
    floating = []
    for path in walk(root):
        rel = path.relative_to(root).as_posix()
        if path.name in LOCKFILES:
            locks.append(rel)
        if path.name not in MANIFESTS:
            continue
        manifests.append(rel)
        try:
            if path.name == "package.json":
                text = path.read_text(encoding="utf-8")
                if re.search(r'":\s*"(latest|\*)"', text):
                    floating.append(rel)
                direct.extend(names_from_package(path))
            elif path.name == "requirements.txt":
                direct.extend(names_from_requirements(path))
            elif path.name == "go.mod":
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.startswith("require ") and not line.endswith("("):
                        direct.append(line.split()[1])
            elif path.name == "Cargo.toml":
                for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
                    if "=" in line and not line.strip().startswith("["):
                        name = line.split("=", 1)[0].strip()
                        if name and name.isidentifier():
                            direct.append(name)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"warn skip {rel}: {exc}", file=sys.stderr)
    unique = []
    seen = set()
    for n in direct:
        if n not in seen:
            seen.add(n)
            unique.append(n)
    surface = [n for n in unique if INTERESTING.search(n)]
    print(f"root {root.as_posix()}")
    print("manifests " + (" ".join(manifests) or "none"))
    print("lockfiles " + (" ".join(locks) or "none") + " (do not cat)")
    print(f"direct_deps {len(unique)}")
    print("direct " + (", ".join(unique[:30]) if unique else "none"))
    if len(unique) > 30:
        print(f"direct_truncated {len(unique) - 30}")
    print("security_surface " + (", ".join(surface[:20]) if surface else "none"))
    print("floating " + (", ".join(floating) if floating else "none"))
    print("note do not paste lockfile or CVE dumps")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    data = Path(source).read_bytes() if source else sys.stdin.buffer.read()
    label = source or "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-deps trim] {label} truncated {len(text) - chars} chars")
    return 0


def cmd_self_test() -> int:
    import tempfile
    from contextlib import redirect_stdout
    from io import StringIO

    with tempfile.TemporaryDirectory(prefix="lean-deps-") as tmp:
        root = Path(tmp)
        (root / "package.json").write_text(
            '{"dependencies": {"express": "4.19.2", "jsonwebtoken": "latest"}}',
            encoding="utf-8",
        )
        buf = StringIO()
        with redirect_stdout(buf):
            cmd_summary(root)
        out = buf.getvalue()
        if "jsonwebtoken" not in out or "floating" not in out:
            print("self-test failed", file=sys.stderr)
            print(out, file=sys.stderr)
            return 1
        print("self-test ok")
        return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="lean-deps manifest summary")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("summary")
    s.add_argument("root", nargs="?", default=".")
    t = sub.add_parser("trim")
    t.add_argument("source", nargs="?")
    t.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test")
    args = p.parse_args(argv)
    if args.cmd == "summary":
        return cmd_summary(Path(args.root))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    return cmd_self_test()


if __name__ == "__main__":
    sys.exit(main())
