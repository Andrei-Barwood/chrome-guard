# Arquitectura

- `cli.py`: Typer CLI, coordina extractores, escáneres y reportes.
- `extractors/`: paths de extensiones (Chrome/Edge/Brave).
- `scanners/manifest_analyzer.py`: reglas estáticas de permisos, CSP y WER.
- `scanners/signature_matcher.py`: regex extensibles para código malicioso.
- `scanners/behavior_monitor.py`: base para monitoreo Playwright (network + DOM).
- `reporters/`: export a JSON/CSV y output de terminal.
- `data/`: firmas, permisos peligrosos y whitelist.
- `scripts/`: tooling de actualización de firmas y helpers de instalación.

