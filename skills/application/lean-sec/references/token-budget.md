# Token budget

Load this only when the default budget in `SKILL.md` is not enough, or the user is fighting context bloat.

## Do not put in context

- Lockfiles, `node_modules`, `dist`, `build`, `target`, coverage, source maps
- Full SARIF, `npm audit` JSON, `pip-audit` JSON, Trivy/Grype dumps
- Entire Dockerfiles, compose files, or Terraform state
- Git history, `git show` of large blobs, binary files
- This skill's `README.md` or LICENSE

Pipe bulky CLI output through:

```text
python3 "$SKILL_ROOT/scripts/lean_sec.py" trim --chars 2500 path/to/output.txt
```

## Read strategy

1. `rg -n` with a tight pattern; take the first few hits per class.
2. Open a file at the matching line (`offset`/`limit` or equivalent). Cap a quote at 12 lines.
3. After two confirmed issues in one file, stop mining that file unless `deep`.
4. Prefer one finding per root cause. Five copies of the same `innerHTML` sink are one finding plus "also on N other lines".

## Subagents

If you delegate, the child must return the report table only: severity, `file:line`, issue, fix. No transcripts, no file dumps, no CVE lists.

## Spending extra budget

Spend remaining file reads on (in order): authz, secrets, injection, SSRF, upload, crypto, CI permissions. Do not spend them on style, tests-as-docs, or generated code.
