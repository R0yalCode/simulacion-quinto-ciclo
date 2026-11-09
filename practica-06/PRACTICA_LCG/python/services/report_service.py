"""
Servicio de presentación con Rich (capa de presentación).

Encapsula todos los formatos visuales de terminal: banners, menús, tablas
de frecuencias, resúmenes, comparaciones, mensajes de estado e
información de la práctica. Además expone utilidades de ruta/timestamp
y de exportación CSV/JSON usadas por los demás servicios.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

console = Console()


# ---------------------------------------------------------------------- #
# Utilidades de archivos
# ---------------------------------------------------------------------- #
def timestamped_name(prefix: str, suffix: str) -> str:
    """Nombre de archivo con fecha/hora para no sobrescribir resultados."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}.{suffix}"


def export_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[Any]]) -> Path:
    """Guarda una tabla en CSV codificado UTF-8."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerows(rows)
        return path
    except OSError as exc:
        raise OSError(f"No se pudo exportar el CSV {path}: {exc}") from exc


def export_json(path: Path, payload: Dict[str, Any]) -> Path:
    """Guarda un objeto estructurado en JSON con formato legible."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str),
                        encoding="utf-8")
        return path
    except (OSError, TypeError) as exc:
        raise OSError(f"No se pudo exportar el JSON {path}: {exc}") from exc


def read_json_config(path: Path) -> Dict[str, Any]:
    """Lee JSON de intercambio escribiendo un mensaje de error claro."""
    if not path.exists():
        raise FileNotFoundError(f"El archivo no existe: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido en {path}: {exc}") from exc


# ---------------------------------------------------------------------- #
# Encabezados y estados
# ---------------------------------------------------------------------- #
def print_banner() -> None:
    banner = Panel(
        Align.center(
            Text.from_markup(
                "[bold cyan]SISTEMA DE SIMULACIÓN ESTADÍSTICA[/]\n"
                "[bold]GENERADOR PSEUDOALEATORIO LCG[/]\n"
                "[dim]Pruebas Chi-cuadrado y Kolmogorov-Smirnov — Python & Java[/]"
            )
        ),
        border_style="bright_blue",
        box=box.DOUBLE,
        padding=(1, 4),
    )
    console.print(banner)


def print_section(title: str) -> None:
    console.print(Rule(title, style="cyan"))


def print_success(message: str) -> None:
    console.print(f"[bold green]✔[/] {message}")


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]![/] {message}")


def print_error(message: str) -> None:
    console.print(f"[bold red]✘ Error:[/] {message}")


def print_paths(paths: Sequence[Path], label: str = "Resultados exportados") -> None:
    if not paths:
        return
    table = Table(title=label, box=box.SIMPLE, header_style="bold magenta")
    table.add_column("Archivo", overflow="fold")
    for p in paths:
        table.add_row(str(p))
    console.print(table)


# ---------------------------------------------------------------------- #
# Configuración
# ---------------------------------------------------------------------- #
def show_config(app_config: Any) -> None:
    table = Table(title="Configuración actual", box=box.ROUNDED, header_style="bold cyan")
    table.add_column("Parámetro", style="bold")
    table.add_column("Valor")
    g = app_config.generator
    s = app_config.statistical
    table.add_row("Semilla X0", str(g.seed))
    table.add_row("Multiplicador a", str(g.multiplier))
    table.add_row("Incremento c", str(g.increment))
    table.add_row("Módulo m", str(g.modulus))
    table.add_row("Cantidad de números N", str(g.n))
    table.add_row("Nivel de significancia α", str(s.alpha))
    table.add_row("Número de intervalos k", str(s.intervals))
    table.add_row("Tolerancia comparativa", str(s.tolerance))
    table.add_row("Tamaños N comparativos", ", ".join(map(str, app_config.comparison_sizes)))
    table.add_row("Repeticiones para promedio", str(app_config.repetitions))
    console.print(table)


# ---------------------------------------------------------------------- #
# Resultados LCG
# ---------------------------------------------------------------------- #
def show_lcg_preview(states: Sequence[int], uniforms: Sequence[float], params: Any) -> None:
    count = min(10, len(states))
    table = Table(
        title=f"Primeros {count} números generados",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold cyan",
    )
    table.add_column("i", justify="right")
    table.add_column("X(i) entero", justify="right")
    table.add_column("U(i) = X/m", justify="right")
    table.add_column("U(i) con 10 decimales", justify="right")
    for i in range(count):
        table.add_row(str(i + 1), str(states[i]), f"{uniforms[i]:.6f}", f"{uniforms[i]:.10f}")
    console.print(table)
    console.print(
        f"[dim]Parámetros: X0={params.seed}, a={params.multiplier}, "
        f"c={params.increment}, m={params.modulus}, N={params.n}[/]"
    )


def show_sequence_stats(uniforms: Sequence[float]) -> None:
    from statistics import fmean

    info = Table(title="Resumen de la secuencia", box=box.SIMPLE, header_style="bold magenta")
    info.add_column("Serie")
    info.add_column("Mínimo", justify="right")
    info.add_column("Media", justify="right")
    info.add_column("Máximo", justify="right")
    info.add_row(
        f"N = {len(uniforms)}",
        f"{min(uniforms):.8f}",
        f"{fmean(uniforms):.8f}",
        f"{max(uniforms):.8f}",
    )
    console.print(info)


# ---------------------------------------------------------------------- #
# Pruebas estadísticas
# ---------------------------------------------------------------------- #
def render_test_result(result: Any, engine_label: str = "Python") -> None:
    if result.observed is not None and result.expected is not None:
        show_chi_frequency_table(result)
    show_summary_table(result, engine_label)


def show_chi_frequency_table(result: Any) -> None:
    labels = result.details.get("interval_labels") or []
    table = Table(
        title=f"Tabla de frecuencias — Prueba Chi-cuadrado (N = {result.sample_size})",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold cyan",
    )
    table.add_column("Intervalo")
    table.add_column("Frecuencia observada", justify="right")
    table.add_column("Frecuencia esperada", justify="right")
    table.add_column("(Oi − Ei)² / Ei", justify="right")
    contributions = result.details.get("contributions", [""] * len(result.observed))
    for label, oi, ei, contrib in zip(labels, result.observed, result.expected, contributions):
        table.add_row(f"[{label}]", str(oi), f"{ei:.1f}", f"{contrib:.4f}")
    table.add_row("Total", str(sum(result.observed)), f"{sum(result.expected):.1f}",
                  f"{result.statistic:.4f}")
    console.print(table)


def show_summary_table(result: Any, engine_label: str = "Python") -> None:
    table = Table(
        title=f"Resumen estadístico — {result.test_name} ({engine_label})",
        box=box.ROUNDED,
        header_style="bold magenta",
    )
    table.add_column("Indicador", style="bold")
    table.add_column("Resultado")
    if result.degrees_freedom is not None:
        table.add_row("Grados de libertad", str(result.degrees_freedom))
        table.add_row("Estadístico Chi-cuadrado", f"{result.statistic:.6f}")
        table.add_row("Valor p Chi-cuadrado", f"{result.p_value:.6f}")
    else:
        table.add_row("Estadístico D Kolmogorov-Smirnov", f"{result.statistic:.6f}")
        table.add_row("Valor p Kolmogorov-Smirnov", f"{result.p_value:.6f}")
        dp = result.details.get("d_plus")
        dm = result.details.get("d_minus")
        if dp is not None and dm is not None:
            table.add_row("D+ / D−", f"{dp:.6f} / {dm:.6f}")
    table.add_row("Cantidad de datos", str(result.sample_size))
    table.add_row("Nivel de significancia", f"{result.alpha}")
    verdict_style = "red" if result.reject_h0 else "green"
    verdict = "Se rechaza H0" if result.reject_h0 else "No se rechaza H0"
    table.add_row("Decisión", f"[{verdict_style}]{verdict}[/]")
    console.print(table)
    console.print(Panel(Text(result.decision, justify="full"),
                        title="Interpretación", border_style="cyan"))


def show_full_summary(chi: Any, ks: Optional[Any], times: Dict[str, float],
                      engine_label: str = "Python") -> None:
    table = Table(
        title=f"Resumen estadístico del proceso completo ({engine_label})",
        box=box.ROUNDED,
        header_style="bold magenta",
    )
    table.add_column("Indicador", style="bold")
    table.add_column("Resultado")
    table.add_row("Cantidad de datos", str(chi.sample_size))
    table.add_row("Estadístico Chi-cuadrado", f"{chi.statistic:.6f}")
    table.add_row("Grados de libertad", str(chi.degrees_freedom))
    table.add_row("Valor p Chi-cuadrado", f"{chi.p_value:.6f}")
    if ks is not None:
        table.add_row("Estadístico KS", f"{ks.statistic:.6f}")
        table.add_row("Valor p KS", f"{ks.p_value:.6f}")
    table.add_row("Nivel de significancia", str(chi.alpha))
    for key, label in (
        ("generation", "Tiempo generación LCG"),
        ("chi_square", "Tiempo Chi-cuadrado"),
        ("ks", "Tiempo Kolmogorov-Smirnov"),
        ("total", "Tiempo proceso estadístico"),
    ):
        if key in times:
            table.add_row(label, f"{times[key] * 1000:.2f} ms")
    if ks is not None:
        d_chi = "Se rechaza H0" if chi.reject_h0 else "No se rechaza H0"
        d_ks = "Se rechaza H0" if ks.reject_h0 else "No se rechaza H0"
        table.add_row("Decisión Chi-cuadrado", d_chi)
        table.add_row("Decisión KS", d_ks)
    console.print(table)


# ---------------------------------------------------------------------- #
# Comparación
# ---------------------------------------------------------------------- #
def show_comparison_rows(rows: List[Dict[str, Any]]) -> None:
    table = Table(
        title="Comparación Python vs Java",
        box=box.SQUARE,
        header_style="bold white on blue",
        caption="Las secuencias se comparan de forma EXACTA (enteros, SHA-256); "
                "los valores p se comparan con la tolerancia configurada; "
                "los tiempos se presentan aparte (promedio de repeticiones).",
        caption_style="dim",
    )
    for col, justify in (
        ("N", "right"),
        ("Secuencias iguales", None),
        ("Chi² Py / Java", "right"),
        ("p Chi² Py / Java", "right"),
        ("p iguales (tol)", None),
        ("KS Py / Java", "right"),
        ("p KS Py / Java", "right"),
        ("pKS iguales (tol)", None),
        ("t Py (gen+pru)", "right"),
        ("t Java (gen+pru)", "right"),
    ):
        table.add_column(col, justify=justify)
    for row in rows:
        ok = row["sequences_equal"]
        table.add_row(
            f"{row['n']:,}".replace(",", "."),
            "✔" if ok else f"✘ ({row['first_diff_pos']})",
            f"{row['chi_py']:.4f} / {row['chi_java']:.4f}",
            f"{row['p_chi_py']:.5f} / {row['p_chi_java']:.5f}",
            "✔" if row["p_chi_eq"] else f"✘ Δ={row['p_chi_absdiff']:.1e}",
            f"{row['ks_py']:.6f} / {row['ks_java']:.6f}",
            f"{row['p_ks_py']:.5f} / {row['p_ks_java']:.5f}",
            "✔" if row["p_ks_eq"] else f"✘ Δ={row['p_ks_absdiff']:.1e}",
            f"{row['t_python']:.1f} ms",
            f"{row['t_java']:.1f} ms",
        )
    console.print(table)


def show_info() -> None:
    print_section("INFORMACIÓN DE LA PRÁCTICA")
    panels = [
        ("Método congruencial lineal (LCG)",
         "X(n+1) = (a·X(n) + c) mod m; U(n) = X(n)/m.\n"
         "Por defecto: X0 = 12345, a = 1664525, c = 1013904223, m = 2^32 (Numerical Recipes).\n"
         "El periodo completo depende de que c sea coprimo con m, a ≡ 1 (mod 4) si m es "
         "múltiplo de 4, etc. (condiciones de Hull-Dobrel)."),
        ("Hipótesis estadísticas",
         "H0: los datos siguen una distribución Uniforme U(0,1).\n"
         "H1: los datos no siguen una distribución U(0,1)."),
        ("Prueba Chi-cuadrado",
         "Bondad de ajuste sobre k intervalos en [0,1). χ² = Σ (Oi − Ei)² / Ei; "
         "Ei = N/k; gl = k − 1 (por defecto k = 10, gl = 9). "
         "Valor p por la distribución chi-cuadrado (cola superior)."),
        ("Prueba Kolmogorov-Smirnov",
         "De una muestra frente a la CDF teórica F(u) = u. "
         "D = max(D+, D−) con D+ = max(i/N − U(i)) y D− = max(U(i) − (i−1)/N). "
         "Con datos discretos y fuertes empates el valor p pierde exactitud."),
        ("Nivel de significancia",
         "α = 0.05 (por defecto). Criterio: si p ≥ α no se rechaza H0; "
         "si p < α se rechaza H0."),
    ]
    console.print(
        "\n".join(
            Panel(Text(txt, justify="full"), title=f"[bold cyan]{title}[/]",
                  border_style="cyan", box=box.ROUNDED)
            for title, txt in panels
        )
    )
    console.print(Text.from_markup(
        "[dim]Referencias: Press et al. «Numerical Recipes»; Hull & Dobel (1962); "
        "Kolmogorov (1933); Smirnov (1948).[/]"
    ))
