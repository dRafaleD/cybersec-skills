# Contributing

Thanks for helping. This repository is a set of **Agent Skills**: small, token-efficient packages that tell an agent how to review code or evidence without dumping entire files into context.

## Layout

```text
skills/
  <category>/
    <skill-name>/
      SKILL.md
      scripts/
      references/
      agents/openai.yaml
```

- `SKILL.md` is required. `name` in the frontmatter must match the folder name (`lean-web` lives in `lean-web/`).
- Put a skill in the category that a user would look in first: application, infrastructure, operations, or engineering.
- Keep `SKILL.md` short. Put extra checklists in `references/` and load one file per run.
- Scripts must be Python 3 stdlib only (no pip). Every script needs a `self-test` command.

## Adding a skill

1. Copy the structure of a similar skill in the same category.
2. Write a third-person `description` that states **what** it does and **when** to use it. Stay under 1024 characters. Do not put `<` or `>` in the description.
3. Default mode is `lean`. `deep` only when the user asks.
4. Output a compact table: severity, location, issue, fix.
5. Update `skills/README.md` and the category `README.md`.
6. Run:

```bash
python3 skills/<category>/<skill-name>/scripts/<script>.py self-test
```

On Windows: `py -3 path\to\script.py self-test`.

## Policy

These skills are **defensive and authorized**:

- Describe location, impact, and a fix. Do not add exploit PoCs, payloads, bypass recipes, malware, or attack steps.
- Never print secret or PII values. Use `[REDACTED]`.
- Do not paste lockfiles, SARIF, pcaps, disk images, or full diffs into chat.
- Review only code, config, and evidence the user already has a right to.

If a request is both a fix and an exploit, implement the fix and refuse the exploit in one sentence.

## Pull requests

- One skill or one focused change per PR.
- Include `self-test` output for any script you touch.
- Do not commit secrets, sample malware blobs, or live credentials.
- Commit messages: imperative mood, describe the change (for example `Add lean-iot device-config inventory`). Do not mention tools or products used to author the patch.

## License

Contributions are accepted under the MIT License. See [LICENSE](LICENSE).
