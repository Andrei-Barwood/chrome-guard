#!/usr/bin/env zsh
set -euo pipefail

REPO_NAME="chrome-guard"
REPO_VISIBILITY="public"  # cambia a "private" si prefieres
ROOT="/Users/kirtantegsingh/Public/tools/chrome/chromeguard"

cd "$ROOT"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI no encontrado. Instálalo y autentica: gh auth login"
  exit 1
fi

# init git si no existe
if [ ! -d ".git" ]; then
  git init
fi

# aseguramos remote correcto
if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote origin ya existe: $(git remote get-url origin)"
else
  gh repo create "$REPO_NAME" --"$REPO_VISIBILITY" --source . --remote origin --push --description "ChromeGuard: auditoría de extensiones Chrome/Edge"
fi

git add .
git commit -m "chore: initial chrome-guard release" || echo "Nada nuevo que commitear"

# sincroniza con GitHub
git push -u origin HEAD
