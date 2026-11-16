"""Capa de gráficas: genera las imágenes PNG con Matplotlib.

Todas las gráficas se generan a partir de resultados reales guardados
en los archivos CSV.
"""

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # permite generar imágenes sin ventana gráfica

import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent  # carpeta python/
CARPETA_GRAFICAS_PYTHON = BASE / "graficas"
CARPETA_GRAFICAS_COMPARACION = BASE.parent / "comparacion" / "graficas"


def generar_graficas_python(resultados):
    """Genera las tres gráficas individuales de Python.

    resultados: lista de diccionarios con las claves n, pi_estimado,
    error y tiempo_ms.
    """
    ns = [r["n"] for r in resultados]
    _graficar(ns, [r["error"] for r in resultados],
              "Error absoluto - Python",
              "Error absoluto",
              CARPETA_GRAFICAS_PYTHON / "error_python.png",
              log_y=True)
    _graficar(ns, [r["tiempo_ms"] for r in resultados],
              "Tiempo de ejecución - Python",
              "Tiempo (ms)",
              CARPETA_GRAFICAS_PYTHON / "tiempo_python.png")
    _graficar(ns, [r["pi_estimado"] for r in resultados],
              "Aproximación de π - Python",
              "Valor de π",
              CARPETA_GRAFICAS_PYTHON / "pi_python.png",
              valor_real=math.pi)


def generar_graficas_comparacion(resultados_py, resultados_java):
    """Genera las tres gráficas comparativas entre Python y Java."""
    ns = [r["n"] for r in resultados_py]
    _graficar_comparacion(ns, [r["error"] for r in resultados_py],
                          [r["error"] for r in resultados_java],
                          "Comparación del error absoluto - Python vs Java",
                          "Error absoluto",
                          CARPETA_GRAFICAS_COMPARACION / "comparacion_error.png",
                          log_y=True)
    _graficar_comparacion(ns, [r["tiempo_ms"] for r in resultados_py],
                          [r["tiempo_ms"] for r in resultados_java],
                          "Comparación del tiempo de ejecución - Python vs Java",
                          "Tiempo (ms)",
                          CARPETA_GRAFICAS_COMPARACION / "comparacion_tiempo.png")
    _graficar_comparacion(ns, [r["pi_estimado"] for r in resultados_py],
                          [r["pi_estimado"] for r in resultados_java],
                          "Comparación de la aproximación de π - Python vs Java",
                          "Valor de π",
                          CARPETA_GRAFICAS_COMPARACION / "comparacion_pi.png",
                          valor_real=math.pi)


def _graficar(ns, valores, titulo, etiqueta_y, ruta, valor_real=None, log_y=False):
    """Dibuja y guarda una gráfica con una sola serie."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ns, valores, marker="o", color="tab:blue", label="Python")
    _configurar(ax, titulo, etiqueta_y, valor_real,
                log_y and all(v > 0 for v in valores))
    ax.legend()
    _guardar(fig, ruta)


def _graficar_comparacion(ns, valores_py, valores_java, titulo, etiqueta_y,
                          ruta, valor_real=None, log_y=False):
    """Dibuja y guarda una gráfica con las series de Python y Java."""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ns, valores_py, marker="o", color="tab:blue", label="Python")
    ax.plot(ns, valores_java, marker="s", color="tab:orange",
            linestyle="--", label="Java")
    _configurar(ax, titulo, etiqueta_y, valor_real,
                log_y and all(v > 0 for v in valores_py))
    ax.legend()
    _guardar(fig, ruta)


def _configurar(ax, titulo, etiqueta_y, valor_real, log_y):
    """Aplica título, etiquetas de ejes, escalas y cuadrícula."""
    ax.set_xscale("log")
    ax.set_xlabel("Número de puntos (N) - escala logarítmica")
    ax.set_ylabel(etiqueta_y)
    ax.set_title(titulo)
    ax.grid(True, which="both", linestyle="--", alpha=0.6)
    if log_y:
        ax.set_yscale("log")
    if valor_real is not None:
        ax.axhline(valor_real, color="red", linestyle="--", label="π real")


def _guardar(fig, ruta):
    """Guarda la figura como PNG en la ruta indicada."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
