---
name: lean-mobile
description: >-
  Runs token-efficient defensive mobile app reviews for Cursor and Codex.
  Inventories exported Android components, backup flags, ATS exceptions, and
  deep links in local manifests and plists, then reports compact hardening
  fixes. Use when the user asks for Android, iOS, mobile security, deep
  links, or certificate pinning review. Do not use for jailbreak exploits,
  store bypasses, or attacking other apps.
license: MIT
metadata:
  version: "1.0.0"
---

# Lean Mobile

Defensive review of **manifests and app config in this workspace**, not of devices you do not own.

Let `SKILL_ROOT` be the folder that contains this `SKILL.md`. Prefer `python3`; on Windows use `py -3`.

```text
python3 "$SKILL_ROOT/scripts/lean_mobile.py" manifest .
python3 "$SKILL_ROOT/scripts/lean_mobile.py" trim --chars 2500 path/to/out.txt
```

## Mode

Default `lean`.

| Mode | Budget |
|------|--------|
| `lean` | `manifest` + up to 8 slices; [references/android.md](references/android.md); ≤6 findings |
| `standard` | + [references/ios.md](references/ios.md); up to 16 slices; ≤10 findings |
| `deep` | needed refs only; ≤16 findings |

## Workflow

1. Run `manifest`. Queue exported activities, backup=true, cleartext traffic, ATS exceptions, custom URL schemes.
2. Slice-read the XML/plist. Cap quotes at 12 lines.
3. Report the safer flag. Stop unless asked to patch.

## Hard rules

- Workspace files only. No sideloading malware or store circumvention.
- No Frida/objection attack recipes.
- Do not print signing keys or keystore passwords.

## Report template

```markdown
## Lean-mobile (`<mode>`)

**App:** <package> | **Budget:** files_read=<n>

| Sev | Location | Issue | Fix |
|-----|----------|-------|-----|
| HIGH | AndroidManifest.xml | exported activity | exported=false or permission |
```
