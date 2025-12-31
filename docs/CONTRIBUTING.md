# Contribuir

1. Haz fork y crea una branch: `feat/<nombre>`.
2. Añade firmas en `data/signatures.json` y permisos en `data/dangerous_permissions.yaml`.
3. Corre linters y tests:
   ```bash
   ruff check .
   mypy src
   pytest --cov=chromeguard
   ```
4. Incluye tests para nuevas reglas.
5. Abre un PR usando la plantilla incluida.

