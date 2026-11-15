"""Capa de persistencia: lectura y escritura de archivos CSV."""

import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # carpeta python/
ARCHIVO_PYTHON = BASE / "resultados" / "resultados_python.csv"
ARCHIVO_JAVA = BASE.parent / "java" / "resultados" / "resultados_java.csv"
ARCHIVO_COMPARACION = BASE.parent / "comparacion" / "tabla_comparacion.csv"

ENCABEZADO = ["n", "puntos_circulo", "pi_estimado", "error", "tiempo_ms"]


def existe(archivo):
    """Indica si el archivo CSV indicado existe."""
    return Path(archivo).is_file()


def guardar_resultados(resultados, archivo=ARCHIVO_PYTHON):
    """Guarda la lista de ResultadoExperimento en un CSV."""
    Path(archivo).parent.mkdir(parents=True, exist_ok=True)
    with open(archivo, "w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(ENCABEZADO)
        for r in resultados:
            escritor.writerow([
                r.n,
                r.puntos_circulo,
                f"{r.pi_estimado:.10f}",
                f"{r.error:.10f}",
                f"{r.tiempo_ms:.3f}",
            ])


def leer_resultados(archivo):
    """Lee un CSV de resultados y devuelve una lista de diccionarios.

    Devuelve None si el archivo todavía no existe.
    """
    if not existe(archivo):
        return None
    resultados = []
    with open(archivo, "r", newline="", encoding="utf-8") as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            resultados.append({
                "n": int(fila["n"]),
                "puntos_circulo": int(fila["puntos_circulo"]),
                "pi_estimado": float(fila["pi_estimado"]),
                "error": float(fila["error"]),
                "tiempo_ms": float(fila["tiempo_ms"]),
            })
    return resultados


def guardar_tabla_comparacion(resultados_py, resultados_java,
                              archivo=ARCHIVO_COMPARACION):
    """Guarda la tabla comparativa de Python y Java en un CSV."""
    Path(archivo).parent.mkdir(parents=True, exist_ok=True)
    with open(archivo, "w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(["n", "pi_python", "pi_java",
                           "error_python", "error_java",
                           "tiempo_python_ms", "tiempo_java_ms"])
        for r_py, r_jv in zip(resultados_py, resultados_java):
            escritor.writerow([
                r_py["n"],
                f"{r_py['pi_estimado']:.10f}",
                f"{r_jv['pi_estimado']:.10f}",
                f"{r_py['error']:.10f}",
                f"{r_jv['error']:.10f}",
                f"{r_py['tiempo_ms']:.3f}",
                f"{r_jv['tiempo_ms']:.3f}",
            ])
