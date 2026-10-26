#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== Python =="
cd "$ROOT/python_sir"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
.venv/bin/python -m pip install -q -r requirements.txt
.venv/bin/python -m sir.presentation.cli

echo "== Tests =="
cd "$ROOT"
"$ROOT/python_sir/.venv/bin/python" -m pytest -q tests

echo "Listo. Ahora abre netlogo/modelo_sir_netlogo.nlogox (o ejecuta ./run_netlogo.sh)."
