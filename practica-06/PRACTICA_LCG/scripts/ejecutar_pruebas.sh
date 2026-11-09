#!/usr/bin/env bash
# Ejecuta las pruebas automatizadas de Python y Java.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== Pruebas Python =="
cd "$ROOT/python"
"$ROOT/.venv/bin/python" -m pytest tests -q

echo
echo "== Pruebas Java =="
if [[ -z "${JAVA_HOME:-}" ]]; then
    for candidate in "$HOME"/tools/jdk-* /usr/lib/jvm/*; do
        if [[ -x "$candidate/bin/javac" ]]; then
            JAVA_HOME="$candidate"
            break
        fi
    done
fi
MVN="$(command -v mvn || true)"
if [[ -z "$MVN" ]]; then
    for candidate in "$HOME"/tools/apache-maven-*/bin/mvn /opt/maven*/bin/mvn; do
        if [[ -x "$candidate" ]]; then
            MVN="$candidate"
            break
        fi
    done
fi
cd "$ROOT/java"
PATH="${JAVA_HOME:-}/bin:$(dirname "${MVN:-mvn}"):$PATH" "$MVN" test
