#!/usr/bin/env zsh
set -euo pipefail

PROJECT_DIR="/Users/kirtantegsingh/Public/tools/chrome/chromeguard"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "No se encontró el venv en ${VENV_DIR}. Crea uno primero."
  exit 1
fi

source "${VENV_DIR}/bin/activate"

echo "== ruff =="
ruff check "${PROJECT_DIR}"

echo "== mypy =="
mypy "${PROJECT_DIR}/src"

echo "Checks OK"

