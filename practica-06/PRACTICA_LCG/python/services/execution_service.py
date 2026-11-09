"""
Servicio de ejecución (capa de aplicación).

Coordina el flujo para el lenguaje Python: generación LCG, ejecución de
las pruebas estadísticas (patrón Strategy), medición del tiempo con
`time.perf_counter()`, exportación de secuencias/JSON/CSV y gráficas.
También implementa el modo headless (CLI) que utiliza el coordinador
comparativo mediante subprocess, con un protocolo JSON idéntico al de Java.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, List, Literal, Optional, Tuple

from config.generator_config import AppConfig
from core.chi_square import ChiSquareTest
from core.kolmogorov_smirnov import KolmogorovSmirnovTest
from core.lcg import Lcg, LcgError, generate_pair
from core.statistical_test import StatisticalTest, TestResult
from services import report_service as ui
from visualization.plots import generate_default_graphs

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = PROJECT_ROOT / "python" / "results"
SEQUENCES_DIR = RESULTS_DIR / "sequences"
GRAPHS_DIR = RESULTS_DIR / "graphs"
REPORTS_DIR = RESULTS_DIR / "reports"


class ExecutionError(RuntimeError):
    """Error controlado durante la ejecución del pipeline."""


class PipelineResult:
    """Todo lo producido por un proceso completo."""

    def __init__(self, states: List[int], uniforms: List[float],
                 chi_result: TestResult, ks_result: TestResult,
                 times: Dict[str, float]) -> None:
        self.states = states
        self.uniforms = uniforms
        self.chi_result = chi_result
        self.ks_result = ks_result
        self.times = times
        self.exported: List[Path] = []

    @property
    def sha256(self) -> str:
        return Lcg.sequence_hash(self.states)


class ExecutionService:
    """
    Coordinación de la sesión para la implementación Python.

    Mantiene en caché la secuencia generada para no regenerarla cuando se
    ejecutan varias pruebas consecutivas. Cada medición se realiza con
    `time.perf_counter()` de forma independiente: la generación, cada
    prueba y el proceso completo se miden por separado. La exportación de
    archivos y las gráficas NUNCA se incluyen en el tiempo estadístico.
    """

    def __init__(self, app_config: AppConfig) -> None:
        self.config = app_config
        app_config.validate()
        self._cached_uniforms: Optional[List[float]] = None
        self._cached_states: Optional[List[int]] = None
        self.chi_strategy: StatisticalTest = ChiSquareTest()
        self.ks_strategy: StatisticalTest = KolmogorovSmirnovTest()

    # ------------------------------------------------------------------ #
    # Generación
    # ------------------------------------------------------------------ #
    def generate(self, force: bool = False) -> Tuple[List[int], List[float]]:
        """Genera la secuencia o la recupera de la caché de sesión."""
        if self._cached_states is not None and not force:
            assert self._cached_uniforms is not None
            return self._cached_states, self._cached_uniforms
        start = perf_counter()
        states, uniforms = generate_pair(self.config.generator)
        elapsed = perf_counter() - start
        Lcg.check_unit_interval(uniforms)
        self._last_generation_seconds = elapsed
        self._cached_states = states
        self._cached_uniforms = uniforms
        return states, uniforms

    @property
    def last_generation_seconds(self) -> float:
        return self._last_generation_seconds

    # ------------------------------------------------------------------ #
    # Pruebas (patrón Strategy)
    # ------------------------------------------------------------------ #
    def run_strategy(self, strategy: StatisticalTest) -> Tuple[TestResult, float]:
        """Ejecuta una prueba sobre la secuencia con caché; devuelve (resultado, segundos)."""
        _, uniforms = self.generate()
        start = perf_counter()
        result = strategy.execute(
            uniforms,
            alpha=self.config.statistical.alpha,
            intervals=self.config.statistical.intervals,
        )
        return result, perf_counter() - start

    # ------------------------------------------------------------------ #
    # Exportaciones (infraestructura)
    # ------------------------------------------------------------------ #
    def export_sequence(self) -> List[Path]:
        """Guarda la secuencia: CSV de enteros, CSV normalizado y metadatos JSON."""
        states, uniforms = self.generate()
        params = self.config.generator
        int_csv = ui.export_csv(
            SEQUENCES_DIR / ui.timestamped_name(f"secuencia_enteros_python_n{params.n}", "csv"),
            ["i", "X(n)"],
            [(i + 1, x) for i, x in enumerate(states)],
        )
        float_csv = ui.export_csv(
            SEQUENCES_DIR / ui.timestamped_name(f"secuencia_normalizada_python_n{params.n}", "csv"),
            ["i", "U(n)"],
            [(i + 1, f"{u:.12f}") for i, u in enumerate(uniforms)],
        )
        meta = {
            "parameters": params.to_dict(),
            "sha256": Lcg.sequence_hash(states),
            "first_20_integers": states[:20],
            "last_20_integers": states[-20:],
        }
        meta_json = ui.export_json(
            SEQUENCES_DIR / ui.timestamped_name(f"secuencia_metadatos_python_n{params.n}", "json"),
            meta,
        )
        return [int_csv, float_csv, meta_json]

    def export_statistics(self, results: List[Tuple[StatisticalTest, TestResult]],
                          times: Dict[str, float]) -> List[Path]:
        """Exporta frecuencias (CSV) y resultados/tiempos (JSON)."""
        paths: List[Path] = []
        for strategy, result in results:
            if result.observed is not None and result.expected is not None:
                labels = result.details.get("interval_labels", [])
                paths.append(ui.export_csv(
                    REPORTS_DIR / ui.timestamped_name(
                        f"frecuencias_{strategy.short_name}_python_n{result.sample_size}", "csv"
                    ),
                    ["intervalo", "observada", "esperada", "contribucion"],
                    list(zip(labels, result.observed, result.expected,
                             result.details.get("contributions", [""] * len(result.observed)))),
                ))
        payload = {
            "engine": "python",
            "parameters": self.config.to_dict(),
            "results": {strategy.short_name: result.to_dict()
                        for strategy, result in results},
            "times_seconds": {
                key: round(value, 9)
                for key, value in times.items()
                if key in ("generation", "chi_square", "ks", "total")
            },
            "times_meta": {
                "repetitions": times.get("repetitions"),
                "warmup_discarded": times.get("warmup_discarded"),
            },
            "sequence_sha256": "" if self._cached_states is None
            else Lcg.sequence_hash(self._cached_states),
        }
        paths.append(ui.export_json(
            REPORTS_DIR / ui.timestamped_name("resultados_python", "json"), payload
        ))
        return paths

    def export_plots(self) -> List[Path]:
        """Genera el paquete mínimo de gráficas (sección 11)."""
        _, uniforms = self.generate()
        return generate_default_graphs(uniforms, GRAPHS_DIR,
                                       intervals=self.config.statistical.intervals)

    # ------------------------------------------------------------------ #
    # Flujos interactivos
    # ------------------------------------------------------------------ #
    def flow_generate(self) -> None:
        states, uniforms = self.generate()
        ui.print_success(f"Secuencia generada: N = {self.config.generator.n:,}")
        ui.show_lcg_preview(states, uniforms, self.config.generator)
        ui.show_sequence_stats(uniforms)
        try:
            ui.print_paths(self.export_sequence(), "Secuencias exportadas")
        except OSError as exc:
            ui.print_error(str(exc))

    def flow_test(self, strategy: StatisticalTest) -> None:
        ui.print_section(f"PRUEBA {strategy.name.upper()}")
        try:
            result, seconds = self.run_strategy(strategy)
        except (LcgError, ValueError) as exc:
            raise ExecutionError(str(exc)) from exc
        verdict = "SE RECHAZA H0" if result.reject_h0 else "NO SE RECHAZA H0"
        ui.print_section(f"p = {result.p_value:.6f} | {verdict}")
        ui.render_test_result(result, engine_label="Python")
        ui.print_success(f"Tiempo de cálculo de la prueba: {seconds * 1000:.2f} ms")

    def flow_full(self) -> PipelineResult:
        """Generación → Chi-cuadrado → KS → gráficas → reportes."""
        ui.print_section("PROCESO COMPLETO")
        states, uniforms, chi_result, ks_result, times = self.measure_pipeline()
        ui.show_lcg_preview(states, uniforms, self.config.generator)
        ui.show_full_summary(chi_result, ks_result, times, engine_label="Python")

        exported: List[Path] = []
        try:
            exported.extend(self.export_sequence())
            exported.extend(self.export_statistics(
                [(self.chi_strategy, chi_result), (self.ks_strategy, ks_result)], times
            ))
            exported.extend(self.export_plots())
        except (OSError, Exception) as exc:  # noqa: BLE001 — se informa, no interrumpe
            ui.print_error(f"Error al exportar resultados: {exc}")
        ui.print_paths(exported, "Archivos generados")

        pipeline = PipelineResult(states, uniforms, chi_result, ks_result, times)
        pipeline.exported = exported
        return pipeline

    def measure_pipeline(self) -> Tuple[List[int], List[float], TestResult, TestResult,
                                        Dict[str, float]]:
        """
        Genera y ejecuta ambas pruebas con la misma metodología del modo
        headless: 1 ejecución de calentamiento no medida + `repetitions`
        repeticiones medidas, promediadas. Los estadísticos reportados son
        los de la última repetición (son deterministas).
        """
        reps = max(1, self.config.repetitions)
        self._execute_pipeline_once()  # calentamiento descartado

        gen_times: List[float] = []
        chi_times: List[float] = []
        ks_times: List[float] = []
        states: List[int] = []
        uniforms: List[float] = []
        chi_result: Optional[TestResult] = None
        ks_result: Optional[TestResult] = None

        for _ in range(reps):
            t0 = perf_counter()
            states, uniforms = generate_pair(self.config.generator)
            gen_times.append(perf_counter() - t0)
            t1 = perf_counter()
            chi_result = self.chi_strategy.execute(
                uniforms, alpha=self.config.statistical.alpha,
                intervals=self.config.statistical.intervals)
            chi_times.append(perf_counter() - t1)
            t2 = perf_counter()
            ks_result = self.ks_strategy.execute(
                uniforms, alpha=self.config.statistical.alpha,
                intervals=self.config.statistical.intervals)
            ks_times.append(perf_counter() - t2)

        assert chi_result is not None and ks_result is not None
        Lcg.check_unit_interval(uniforms)
        self._cached_states = states
        self._cached_uniforms = uniforms
        self._last_generation_seconds = statistics.fmean(gen_times)
        times: Dict[str, float] = {
            "generation": statistics.fmean(gen_times),
            "chi_square": statistics.fmean(chi_times),
            "ks": statistics.fmean(ks_times),
            "total": statistics.fmean(gen_times) + statistics.fmean(chi_times)
            + statistics.fmean(ks_times),
            "repetitions": reps,
            "warmup_discarded": 1,
        }
        return states, uniforms, chi_result, ks_result, times

    # ------------------------------------------------------------------ #
    # Modo headless (usado por el coordinador Python↔Java vía subprocess)
    # ------------------------------------------------------------------ #
    def headless_run(self, output_path: Path, no_plots: bool = False) -> Dict[str, Any]:
        """
        Ejecución no interactiva del proceso completo.

        Protocolo JSON compartido con Java (fuente única de comparación):

        - Medición: 1 ejecución de calentamiento (no medida) + `repetitions`
          repeticiones medidas; se promedian los tiempos de generación,
          Chi-cuadrado, KS y el total estadístico.
        - Identidad de secuencias: huella SHA-256 de los enteros decimales.
        - Las gráficas (opcional aquí) se generan FUERA de la medición.
        - Estadísticas: se reportan las de la última repetición (deterministas).
        """
        reps = max(1, self.config.repetitions)
        gen_times: List[float] = []
        chi_times: List[float] = []
        ks_times: List[float] = []

        # Calentamiento: descartado de la medición (análogo al warmup de la JVM en Java).
        warm_result = self._execute_pipeline_once()
        for _ in range(reps):
            self._cached_uniforms = None
            self._cached_states = None
            t0 = perf_counter()
            states, uniforms = generate_pair(self.config.generator)
            gen_times.append(perf_counter() - t0)
            t1 = perf_counter()
            chi_result = self.chi_strategy.execute(
                uniforms, alpha=self.config.statistical.alpha,
                intervals=self.config.statistical.intervals)
            chi_times.append(perf_counter() - t1)
            t2 = perf_counter()
            ks_result = self.ks_strategy.execute(
                uniforms, alpha=self.config.statistical.alpha,
                intervals=self.config.statistical.intervals)
            ks_times.append(perf_counter() - t2)

        del warm_result
        times = {
            "generation": statistics.fmean(gen_times),
            "chi_square": statistics.fmean(chi_times),
            "ks": statistics.fmean(ks_times),
            "total": sum((statistics.fmean(gen_times),
                          statistics.fmean(chi_times),
                          statistics.fmean(ks_times))),
            "repetitions": reps,
            "warmup_discarded": 1,
        }

        payload: Dict[str, Any] = {
            "engine": "python",
            "generator": self.config.generator.to_dict(),
            "statistical": self.config.statistical.to_dict(),
            "sequence": {
                "count": len(states),
                "sha256": Lcg.sequence_hash(states),
                "first_20_integers": states[:20],
                "last_20_integers": states[-20:],
                "first_20_uniforms": [round(u, 12) for u in uniforms[:20]],
                "last_20_uniforms": [round(u, 12) for u in uniforms[-20:]],
            },
            "chi_square": {
                "statistic": chi_result.statistic,
                "p_value": chi_result.p_value,
                "degrees_freedom": chi_result.degrees_freedom,
                "observed": chi_result.observed,
                "expected": chi_result.expected,
                "reject_h0": chi_result.reject_h0,
            },
            "kolmogorov_smirnov": {
                "statistic": ks_result.statistic,
                "p_value": ks_result.p_value,
                "d_plus": ks_result.details["d_plus"],
                "d_minus": ks_result.details["d_minus"],
                "reject_h0": ks_result.reject_h0,
            },
            "times_seconds": {k: round(v, 9) for k, v in times.items()
                              if isinstance(v, float)},
            "times_meta": {"repetitions": reps, "warmup_discarded": 1},
            "p_value_source": {
                "chi_square": "scipy.stats.chi2.sf (cola superior, gl = k-1)",
                "kolmogorov_smirnov": (
                    "scipy.stats.kstest: exacto para n pequeño, asintótico para n grande "
                    "(convención compatible con Apache Commons Math)"
                ),
            },
        }
        ui.export_json(output_path, payload)
        if not no_plots:
            try:
                self.export_plots()
            except Exception as exc:  # noqa: BLE001
                print(f"[aviso] gráficas no generadas: {exc}")
        return payload

    def _execute_pipeline_once(self) -> Tuple[TestResult, TestResult]:
        """Ejecuta generación + ambas pruebas (para calentamiento)."""
        _, uniforms = self.generate(force=True)
        chi_result = self.chi_strategy.execute(
            uniforms, alpha=self.config.statistical.alpha,
            intervals=self.config.statistical.intervals)
        ks_result = self.ks_strategy.execute(
            uniforms, alpha=self.config.statistical.alpha,
            intervals=self.config.statistical.intervals)
        return chi_result, ks_result
