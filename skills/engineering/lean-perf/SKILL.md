---
name: lean-perf
description: >-
  Runs token-efficient performance reviews for Cursor and Codex. Inventories
  N-plus-1 loops, SELECT star, unbounded reads, and sync I/O in request
  paths, then reports compact hot-path fixes. Use when the user asks for
  performance, slow queries, N+1, latency, or cheaper I/O. Do not dump
  profiles, flame graphs, or rewrite unrelated modules.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Perf

Hot-path hygiene. Scripts list likely N+1 and unbounded reads; you confirm a few loops.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_perf.py" hot .
python3 "$SKILL_ROOT/scripts/lean_perf.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `hot` + up to 8 slices; [references/io.md](references/io.md); ≤6 findings |
| `standard` | up to 16 slices; ≤10 findings |
| `deep` | still no full profiler dump; ≤16 findings |

## Workflow

1. Run `hot`. Queue await-in-loop, query-in-loop, `SELECT *`, no pagination.
2. Slice-read. Cap quotes at 12 lines.
3. Report batching, indexes, pagination. Stop unless asked to patch.

## Hard rules

- Do not paste flame graphs or 10k-line profiles. `trim` if the user already has one.
- No drive-by micro-optimizations of cold code.

## Report template

```markdown
## Lean-perf (`<mode>`)

**Hot path:** <handler> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | file:line | await inside map of N | Promise.all / batch query |
```
