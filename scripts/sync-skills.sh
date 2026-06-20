#!/usr/bin/env bash
# Keep the Codex skill folder in sync with the canonical Claude skills.
# Run once after cloning, and again whenever you add or edit a skill.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .agents/skills
if command -v rsync >/dev/null 2>&1; then
  rsync -a --delete .claude/skills/ .agents/skills/
else
  rm -rf .agents/skills/* && cp -R .claude/skills/. .agents/skills/
fi
echo "Synced .claude/skills -> .agents/skills"
