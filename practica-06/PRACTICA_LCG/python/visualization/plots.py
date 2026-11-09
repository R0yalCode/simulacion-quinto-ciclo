"""
Gráficas con Matplotlib (capa de infraestructura de presentación visual).

Se establece el backend no interactivo 'Agg' para poder generar PNG incluso
en terminales sin entorno gráfico. Las funciones reciben rutas de destino y
guardan las imágenes; nunca muestran ventanas.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")  # backend sin pantalla: solo guardar a disco

from pathlib import Path
from typing import List, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams

from core.kolmogorov_smirnov import uniform_theoretical_cdf

_SEED_PLOT_POINTS = 2000  # puntos para dibujar la ECDF sin saturar la memoria

rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 150,
    "font.family": "DejaVu Sans",
    "axes.grid": True,
    "grid.alpha": 0.3,
})

_COLOR_EMP = "#1565c0"
_COLOR_THEO = "#c62828"


class PlotError(RuntimeError):
    """Error al generar o guardar una gráfica."""


def _prepare_axes(title: str, xlabel: str, ylabel: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(0, 1)
    return fig, ax


def _save(fig: plt.Figure, path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(path, format="png")
        plt.close(fig)
    except OSError as exc:
        plt.close(fig)
        raise PlotError(f"No se pudo guardar la gráfica {path}: {exc}") from exc


def _ecdf_points(ordered: Sequence[float], n: int):
    """
    Puntos (u, F) de la ECDF. Con muestras grandes se submuestrean las
    posiciones ordenadas, pero la altura se calcula con el índice real
    sobre N (no sobre el submuestreo), de modo que la curva sigue siendo
    la ECDF de la muestra completa y alcanza F = 1.
    """
    if n <= _SEED_PLOT_POINTS:
        sub = np.asarray(ordered, dtype=float)
        positions = np.arange(1, n + 1)
    else:
        indices = np.linspace(0, n - 1, _SEED_PLOT_POINTS, dtype=int)
        sub = np.asarray([ordered[int(i)] for i in indices], dtype=float)
        positions = indices + 1
    ux = np.concatenate(([0.0], sub))
    uy = np.concatenate(([0.0], positions / n))
    return ux, uy


def plot_empirical_cdf(sequence: Sequence[float], path: Path) -> Path:
    """
    Distribución acumulada empírica (escalonada) de la secuencia LCG.

    La ECDF evalúa F(i/n) sobre la muestra ordenada (submuestreada para
    mantener la gráfica legible); `where='post'` produce la escalera
    verdadera de una función acumulada empírica.
    """
    ordered = sorted(sequence)
    n = len(sequence)
    fig, ax = _prepare_axes(
        "Distribución acumulada empírica (LCG)", "u", "F(u) empírica"
    )
    ux, uy = _ecdf_points(ordered, n)
    ax.step(ux, uy, where="post", color=_COLOR_EMP, lw=1.6, label="ECDF empírica F_N(u)")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="upper left")
    _save(fig, path)
    return path


def plot_uniform_cdf(path: Path) -> Path:
    """Función de distribución acumulada uniforme teórica U(0,1): diagonal."""
    fig, ax = _prepare_axes(
        "Distribución acumulada uniforme teórica U(0,1)", "u", "F(u) teórica"
    )
    x = np.linspace(0, 1, 400)
    y = [uniform_theoretical_cdf(float(v)) for v in x]
    ax.plot(x, y, color=_COLOR_THEO, lw=2, label="CDF teórica U(0,1)")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="upper left")
    _save(fig, path)
    return path


def plot_cdf_comparison(sequence: Sequence[float], path: Path) -> Path:
    """Empírica vs teórica en la misma gráfica (base de la prueba KS)."""
    ordered = sorted(sequence)
    fig, ax = _prepare_axes(
        "Comparación CDF empírica vs distribución acumulada U(0,1)", "u", "F(u)"
    )
    n = len(sequence)
    ux, uy = _ecdf_points(ordered, n)
    ax.step(ux, uy, where="post", color=_COLOR_EMP, lw=1.6, label="ECDF empírica F_N(u)")
    x = np.linspace(0, 1, 400)
    ax.plot(x, [uniform_theoretical_cdf(float(v)) for v in x], color=_COLOR_THEO, lw=2,
            label="CDF teórica U(0,1)")
    d = max(max((i + 1) / n - u for i, u in enumerate(ordered)),
            max(u - i / n for i, u in enumerate(ordered)))
    ax.set_ylim(0, 1.02)
    ax.set_xlim(0, 1)
    ax.annotate(f"D (KS) = {d:.6f}", xy=(0.05, 0.92), xycoords="axes fraction",
                bbox=dict(boxstyle="round", fc="white", ec="gray"))
    ax.legend(loc="lower right")
    _save(fig, path)
    return path


def plot_frequency_histogram(sequence: Sequence[float], intervals: int, path: Path,
                             expected: Sequence[float] | None = None) -> Path:
    """Histograma con `intervals` intervalos de igual amplitud."""
    counts, bin_edges = np.histogram(list(sequence), bins=intervals, range=(0.0, 1.0))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.set_title(
        f"Histograma de frecuencias ({intervals} intervalos)", fontsize=13, fontweight="bold"
    )
    ax.set_xlabel("Intervalo de u")
    ax.set_ylabel("Frecuencia observada")
    centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    width = (bin_edges[1] - bin_edges[0]) * 0.86
    ax.bar(centers, counts, width=width, edgecolor="white", color="#1565c0",
           label="Frecuencia observada")
    if expected is not None:
        ax.axhline(float(np.mean(expected)), color="#c62828", lw=2, ls="--",
                   label=f"Frecuencia esperada Ei = {float(np.mean(expected)):.1f}")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right")
    _save(fig, path)
    return path


def generate_default_graphs(sequence: Sequence[float], out_dir: Path,
                            intervals: int = 10) -> List[Path]:
    """Conjunto mínimo de gráficas de la práctica (secciones 11.1 a 11.4)."""
    paths = [
        plot_empirical_cdf(sequence, out_dir / "ecdf_empirica_lcg.png"),
        plot_uniform_cdf(out_dir / "cdf_uniforme_teorica.png"),
        plot_cdf_comparison(sequence, out_dir / "ecdf_vs_uniforme_lcg.png"),
        plot_frequency_histogram(sequence, intervals,
                                 out_dir / "histograma_frecuencias_lcg.png"),
    ]
    return paths


__all__ = [
    "PlotError",
    "plot_empirical_cdf",
    "plot_uniform_cdf",
    "plot_cdf_comparison",
    "plot_frequency_histogram",
    "generate_default_graphs",
]
