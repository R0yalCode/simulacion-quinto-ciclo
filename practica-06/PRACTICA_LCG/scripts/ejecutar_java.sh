#!/usr/bin/env bash
# Ejecuta la implementación Java (menú interactivo autónomo).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JAR="$ROOT/java/target/lcg-simulator.jar"

if [[ -z "${JAVA_HOME:-}" ]]; then
    if [[ -x "$HOME/tools/jdk-21.0.13+9/bin/java" ]]; then
        JAVA_HOME="$HOME/tools/jdk-21.0.13+9"
    else
        for candidate in "$HOME"/tools/jdk-* /usr/lib/jvm/*; do
            if [[ -x "$candidate/bin/java" ]]; then
                JAVA_HOME="$candidate"
                break
            fi
        done
    fi
fi
if [[ -z "${JAVA_HOME:-}" || ! -x "$JAVA_HOME/bin/java" ]]; then
    echo "No se encontró Java. Defina JAVA_HOME o instale un JDK 21." >&2
    exit 1
fi

if [[ ! -f "$JAR" ]]; then
    echo "El JAR no existe; compilando con Maven…"
    "$ROOT/scripts/compilar_java.sh" -q
fi

cd "$ROOT"
exec "$JAVA_HOME/bin/java" -jar "$JAR" "$@"
