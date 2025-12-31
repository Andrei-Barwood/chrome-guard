# Instalación

Requisitos: Python 3.11+, git, pyenv opcional.

```bash
pyenv install 3.11.9
pyenv local 3.11.9
python -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
playwright install chromium
```

Para Windows/WSL: ejecuta el mismo flujo desde PowerShell/WSL con rutas equivalentes.

