#!/usr/bin/env python3
"""Cheap defensive inventory for lean-sec. Stdlib only. Prints summaries, never secret values."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".turbo",
    ".cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "vendor",
    "coverage",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    ".idea",
    ".vscode",
    "site-packages",
}

SKIP_FILE_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tgz",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
    ".min.js",
    ".min.css",
    ".lock",
    ".pyc",
    ".wasm",
}

LOCKFILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lock",
    "bun.lockb",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
    "composer.lock",
    "Gemfile.lock",
}

MANIFESTS = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "Pipfile",
    "Cargo.toml",
    "go.mod",
    "composer.json",
    "Gemfile",
}

PATH_TAGS = (
    ("secrets", re.compile(r"(^|/)(\.env|\.env\.|secrets?|credentials|id_rsa|id_ed25519|kubeconfig)|\.pem$", re.I)),
    ("auth", re.compile(r"auth|session|oauth|oidc|sso|jwt|rbac|permission|acl|login|passwd|password", re.I)),
    ("crypto", re.compile(r"crypto|kdf|bcrypt|argon|pbkdf|hmac|keystore|kms", re.I)),
    ("sql", re.compile(r"sql|query|prisma|sequelize|knex|drizzle|typeorm|hibernate|mybatis", re.I)),
    ("upload", re.compile(r"upload|multipart|s3|blob|storage", re.I)),
    ("ssrf", re.compile(r"fetch|axios|httpclient|requests|urllib|got\b|webhook|proxy", re.I)),
    ("web", re.compile(r"(^|/)(app|server|api|route|controller|handler|graphql|websocket)s?(\.|/)", re.I)),
    ("ci", re.compile(r"(^|/)\.github/|(^|/)\.gitlab-ci|jenkinsfile|azure-pipelines", re.I)),
    ("infra", re.compile(r"dockerfile|compose\.ya?ml|\.tf$|kubernetes|helm|terraform|ansible", re.I)),
)

SECRET_RULES = (
    ("private-key", "HIGH", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")),
    ("aws-access-key", "HIGH", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", "HIGH", re.compile(r"\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_]{20,}\b")),
    ("slack-token", "HIGH", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("google-api-key", "HIGH", re.compile(r"\bAIza[0-9A-Za-z\-_]{20,}\b")),
    ("stripe-secret", "HIGH", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b")),
    ("generic-secret", "MED", re.compile(
        r"(?i)\b(api[_-]?key|secret(?:_key)?|access[_-]?token|auth[_-]?token|password|passwd)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    )),
)

TEXT_LIMIT = 1_000_000
DEFAULT_MAX_HOTSPOTS = 40
DEFAULT_MAX_SECRETS = 25


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def iter_files(root: Path):
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            if name in LOCKFILES:
                continue
            if path.suffix.lower() in SKIP_FILE_SUFFIXES:
                continue
            yield path


def rel_posix(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def tag_path(rel: str) -> list[str]:
    tags = [name for name, rx in PATH_TAGS if rx.search(rel)]
    return tags or []


def cmd_scope(root: Path, max_hotspots: int) -> int:
    counts = defaultdict(int)
    grouped = defaultdict(list)
    scanned = 0
    for path in iter_files(root):
        scanned += 1
        rel = rel_posix(path, root)
        tags = tag_path(rel)
        if not tags:
            continue
        for tag in tags:
            counts[tag] += 1
            if len(grouped[tag]) < 8:
                grouped[tag].append(rel)

    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    hotspots = []
    seen = set()
    for tag, _ in ranked:
        for rel in grouped[tag]:
            if rel in seen:
                continue
            seen.add(rel)
            hotspots.append(f"{tag:8} {rel}")
            if len(hotspots) >= max_hotspots:
                break
        if len(hotspots) >= max_hotspots:
            break

    print(f"root {root.resolve().as_posix()}")
    print(f"files_scanned {scanned}")
    print(f"hotspot_files {len(seen)}")
    print("tags " + " ".join(f"{k}={v}" for k, v in ranked) if ranked else "tags none")
    print("hotspots")
    if not hotspots:
        print("  (none)")
    else:
        for line in hotspots:
            print(f"  {line}")
    print("note read only hotspot files; do not dump contents here")
    return 0


def is_probably_binary(sample: bytes) -> bool:
    if not sample:
        return False
    if b"\x00" in sample:
        return True
    # High ratio of non-text bytes
    nontext = sum(b < 9 or (13 < b < 32) for b in sample)
    return (nontext / len(sample)) > 0.30


def cmd_secrets(root: Path, max_findings: int) -> int:
    findings = []
    scanned = 0
    for path in iter_files(root):
        rel = rel_posix(path, root)
        if rel.lower().endswith(".md"):
            continue
        try:
            raw = path.read_bytes()
        except OSError:
            continue
        if len(raw) > TEXT_LIMIT or is_probably_binary(raw[:2048]):
            continue
        scanned += 1
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            for rule_id, sev, rx in SECRET_RULES:
                if rx.search(line):
                    findings.append((sev, rel, i, rule_id))
                    break
            if len(findings) >= max_findings:
                break
        if len(findings) >= max_findings:
            break

    print(f"root {root.resolve().as_posix()}")
    print(f"files_scanned {scanned}")
    print(f"findings {len(findings)}")
    print("hits")
    if not findings:
        print("  (none)")
    else:
        order = {"HIGH": 0, "MED": 1, "LOW": 2}
        findings.sort(key=lambda x: (order.get(x[0], 9), x[1], x[2]))
        for sev, rel, line, rule_id in findings:
            print(f"  {sev:4} {rel}:{line} {rule_id} [REDACTED]")
    print("note never print secret values; tell the owner to rotate HIGH hits")
    return 0


def parse_package_json(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    names = []
    for key in ("dependencies", "devDependencies", "optionalDependencies"):
        block = data.get(key) or {}
        names.extend(sorted(block))
    return names


def parse_requirements(path: Path) -> list[str]:
    names = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        names.append(re.split(r"[<>=[~! ]", line, maxsplit=1)[0].strip())
    return [n for n in names if n]


def parse_pyproject(path: Path) -> list[str]:
    names = []
    in_deps = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and "dependencies" in stripped.lower():
            in_deps = True
            continue
        if stripped.startswith("["):
            in_deps = False
        if in_deps and stripped.startswith('"'):
            names.append(stripped.strip('",'))
        if stripped.startswith("requires-python"):
            continue
    return names


def parse_cargo_toml(path: Path) -> list[str]:
    names = []
    in_deps = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped in ("[dependencies]", "[dev-dependencies]", "[build-dependencies]"):
            in_deps = True
            continue
        if stripped.startswith("["):
            in_deps = False
            continue
        if in_deps and stripped and not stripped.startswith("#") and "=" in stripped:
            names.append(stripped.split("=", 1)[0].strip().strip('"'))
    return names


def parse_go_mod(path: Path) -> list[str]:
    names = []
    in_block = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_block = True
            continue
        if in_block and stripped == ")":
            in_block = False
            continue
        if stripped.startswith("require ") and not stripped.endswith("("):
            names.append(stripped.split()[1])
        elif in_block and stripped and not stripped.startswith("//"):
            names.append(stripped.split()[0])
    return names


def cmd_deps(root: Path) -> int:
    root = root.resolve()
    manifests = []
    lock_hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            if name in LOCKFILES:
                try:
                    with path.open("rb") as fh:
                        lines = sum(1 for _ in fh)
                except OSError:
                    lines = -1
                lock_hits.append((rel, lines))
            if name in MANIFESTS:
                manifests.append(path)

    direct = []
    for path in manifests:
        try:
            if path.name == "package.json":
                direct.extend(parse_package_json(path))
            elif path.name == "requirements.txt":
                direct.extend(parse_requirements(path))
            elif path.name == "pyproject.toml":
                direct.extend(parse_pyproject(path))
            elif path.name == "Cargo.toml":
                direct.extend(parse_cargo_toml(path))
            elif path.name == "go.mod":
                direct.extend(parse_go_mod(path))
            elif path.name in {"Pipfile", "Gemfile"}:
                direct.append(f"(see {path.relative_to(root).as_posix()})")
            elif path.name == "composer.json":
                data = json.loads(path.read_text(encoding="utf-8"))
                require = data.get("require") or {}
                direct.extend(sorted(k for k in require if k != "php"))
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            eprint(f"warn skip {path}: {exc}")

    unique = []
    seen = set()
    for name in direct:
        if name not in seen:
            seen.add(name)
            unique.append(name)

    interesting = [
        n for n in unique
        if re.search(
            r"jwt|auth|passport|bcrypt|argon|helmet|cors|crypto|openssl|xml|yaml|serialize|pickle|child.process|docker|aws|azure|gcp",
            n,
            re.I,
        )
    ]

    print(f"root {root.as_posix()}")
    print("manifests " + (" ".join(p.relative_to(root).as_posix() for p in manifests) or "none"))
    print("lockfiles")
    if not lock_hits:
        print("  (none)")
    else:
        for rel, lines in lock_hits:
            print(f"  {rel} lines={lines} (do not cat)")
    print(f"direct_deps {len(unique)}")
    preview = unique[:30]
    print("direct " + (", ".join(preview) if preview else "none"))
    if len(unique) > 30:
        print(f"direct_truncated {len(unique) - 30}")
    print("security_surface " + (", ".join(interesting[:20]) if interesting else "none"))
    print("note do not paste lockfile or CVE dumps into context")
    return 0


def cmd_trim(source: str | None, chars: int) -> int:
    if source:
        data = Path(source).read_bytes()
        label = source
    else:
        data = sys.stdin.buffer.read()
        label = "stdin"
    text = data.decode("utf-8", errors="replace")
    if len(text) <= chars:
        print(text, end="" if text.endswith("\n") or text == "" else "\n")
        return 0
    print(text[:chars].rstrip() + "\n")
    print(f"[lean-sec trim] {label} truncated {len(text) - chars} chars; do not re-read the rest")
    return 0


def cmd_self_test() -> int:
    import tempfile

    with tempfile.TemporaryDirectory(prefix="lean-sec-") as tmp:
        root = Path(tmp)
        auth = root / "src" / "auth"
        auth.mkdir(parents=True)
        fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"
        (auth / "login.py").write_text("def login():\n    return True\n", encoding="utf-8")
        (root / ".env").write_text(f"AWS_ACCESS_KEY_ID={fake_aws}\n", encoding="utf-8")
        (root / "package.json").write_text(
            json.dumps({"dependencies": {"express": "4.19.2", "jsonwebtoken": "9.0.2"}}),
            encoding="utf-8",
        )
        (root / "package-lock.json").write_text("{}\n" * 20, encoding="utf-8")

        from io import StringIO
        from contextlib import redirect_stdout

        buf = StringIO()
        with redirect_stdout(buf):
            cmd_scope(root, 40)
            cmd_secrets(root, 25)
            cmd_deps(root)
        out = buf.getvalue()
        checks = {
            "auth hotspot": "auth" in out and "login.py" in out,
            "secret redacted": "aws-access-key" in out and fake_aws not in out,
            "lockfile not dumped": "package-lock.json" in out and "do not cat" in out,
            "jwt surface": "jsonwebtoken" in out,
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            eprint("self-test failed:", ", ".join(failed))
            eprint(out)
            return 1
        print("self-test ok")
        return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="lean-sec cheap defensive inventory")
    sub = p.add_subparsers(dest="cmd", required=True)
    scope = sub.add_parser("scope", help="rank high-risk paths without file contents")
    scope.add_argument("root", nargs="?", default=".")
    scope.add_argument("--max", type=int, default=DEFAULT_MAX_HOTSPOTS)
    secrets = sub.add_parser("secrets", help="find likely secrets; print kinds, never values")
    secrets.add_argument("root", nargs="?", default=".")
    secrets.add_argument("--max", type=int, default=DEFAULT_MAX_SECRETS)
    deps = sub.add_parser("deps", help="summarize manifests; do not dump lockfiles")
    deps.add_argument("root", nargs="?", default=".")
    trim = sub.add_parser("trim", help="truncate a file or stdin for context")
    trim.add_argument("source", nargs="?", help="file path; omit to read stdin")
    trim.add_argument("--chars", type=int, default=2500)
    sub.add_parser("self-test", help="run a tiny fixture test")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "scope":
        return cmd_scope(Path(args.root), args.max)
    if args.cmd == "secrets":
        return cmd_secrets(Path(args.root), args.max)
    if args.cmd == "deps":
        return cmd_deps(Path(args.root))
    if args.cmd == "trim":
        return cmd_trim(args.source, args.chars)
    if args.cmd == "self-test":
        return cmd_self_test()
    return 2


if __name__ == "__main__":
    sys.exit(main())
