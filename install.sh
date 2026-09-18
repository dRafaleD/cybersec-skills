#!/usr/bin/env bash
# Install each skill folder (the directory that contains SKILL.md) into
# the user-level Agent Skills paths. Category folders are skipped.
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
SKILL_ROOT="$REPO/skills"
if [[ ! -d "$SKILL_ROOT" ]]; then
  echo "skills/ folder not found at $SKILL_ROOT" >&2
  exit 1
fi

dests=(
  "$HOME/.agents/skills"
  "$HOME/.cursor/skills"
  "$HOME/.codex/skills"
)

while IFS= read -r skill_md; do
  skill="$(dirname "$skill_md")"
  name="$(basename "$skill")"
  for dest in "${dests[@]}"; do
    mkdir -p "$dest"
    link="$dest/$name"
    ln -sfn "$skill" "$link"
    echo "linked $link -> $skill"
  done
done < <(find "$SKILL_ROOT" -name SKILL.md -type f | sort)
