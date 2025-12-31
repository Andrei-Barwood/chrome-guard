#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
playwright install chromium
echo "ChromeGuard installed. Run: chromeguard scan --browser chrome"

