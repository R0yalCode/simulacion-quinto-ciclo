#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NETLOGO_HOME="${NETLOGO_HOME:-/home/rnull/Aplicaciones/NetLogo 7.0.4}"

if [ ! -x "$NETLOGO_HOME/netlogo-gui.sh" ]; then
  echo "No se encontro NetLogo en: $NETLOGO_HOME"
  echo "Define NETLOGO_HOME o abre el modelo manualmente desde la interfaz."
  exit 1
fi

exec "$NETLOGO_HOME/netlogo-gui.sh" "$ROOT/netlogo/modelo_sir_netlogo.nlogox"
