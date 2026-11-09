#!/usr/bin/env bash
# Ejecuta la implementación Python (menú interactivo).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
    echo "No se encontró el entorno virtual .venv." >&2
    echo "Créelo con: python3 -m venv .venv && .venv/bin/pip install -r python/requirements.txt" >&2
    exit 1
fi

cd "$ROOT"
exec "$ROOT/.venv/bin/python" python/main.py "$@"
