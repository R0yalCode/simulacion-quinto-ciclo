#!/usr/bin/env bash
# Compila el proyecto Java con Maven y genera java/target/lcg-simulator.jar.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Localiza un JDK 21+ si JAVA_HOME no está definido.
if [[ -z "${JAVA_HOME:-}" ]]; then
    for candidate in "$HOME"/tools/jdk-* /usr/lib/jvm/*; do
        if [[ -x "$candidate/bin/javac" ]]; then
            JAVA_HOME="$candidate"
            break
        fi
    done
fi
if [[ -z "${JAVA_HOME:-}" || ! -x "$JAVA_HOME/bin/javac" ]]; then
    echo "No se encontró un JDK. Defina JAVA_HOME o instale Temurin 21." >&2
    exit 1
fi

# Localiza Maven si no está en el PATH.
MVN="$(command -v mvn || true)"
if [[ -z "$MVN" ]]; then
    for candidate in "$HOME"/tools/apache-maven-*/bin/mvn /opt/maven*/bin/mvn; do
        if [[ -x "$candidate" ]]; then
            MVN="$candidate"
            break
        fi
    done
fi
if [[ -z "$MVN" ]]; then
    echo "No se encontró Maven. Instale Maven 3.9+ o agregue su bin/ al PATH." >&2
    exit 1
fi

cd "$ROOT/java"
PATH="$JAVA_HOME/bin:$(dirname "$MVN"):$PATH" "$MVN" package "$@"
echo "JAR generado: $ROOT/java/target/lcg-simulator.jar"
