#!/usr/bin/env zsh
set -euo pipefail

PY_VERSION=${PY_VERSION:-3.11.9}
PROJECT_DIR="/Users/kirtantegsingh/Public/tools/chrome/chromeguard"

# Ensure pyenv is available
if ! command -v pyenv >/dev/null 2>&1; then
  echo "pyenv no encontrado. Instálalo antes de continuar."
  exit 1
fi

export PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
eval "$(pyenv init -)"

# Prefer pyenv if version exists; otherwise fall back to current python.
if pyenv versions --bare | grep -qx "${PY_VERSION}"; then
  export PYENV_VERSION="${PY_VERSION}"
  pyenv shell "${PY_VERSION}"
  echo "Usando pyenv ${PY_VERSION}"
else
  echo "Python ${PY_VERSION} no está en pyenv; usando python actual ($(python -V))."
fi

cd "${PROJECT_DIR}"

python -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[dev]"

# Playwright runtime
playwright install chromium

echo "Listo. Activa el entorno con: source ${PROJECT_DIR}/.venv/bin/activate"

