"""
Servicio del modo comparativo — coordinador Python ↔ Java.

Capa de aplicación (con integraciones de infraestructura). Ejecuta de
forma independiente ambas implementaciones mediante `subprocess` y el
protocolo JSON compartido, y compara:

1. Secuencias de enteros X(n) — comparación EXACTA (SHA-256 + extremos).
2. Frecuencias observadas Chi-cuadrado (enteros exactos).
3. Estadísticos y valores p de Chi-cuadrado (tolerancia configurable).
4. Estadísticos y valores p de Kolmogorov-Smirnov (tolerancia configurable).
5. Tiempos de ejecución — presentados APARTE, promedio de repeticiones.

Java nunca depende de Python: el coordinador solo lo invoca por subprocess.
"""

from __future__ import annotations

import copy
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from config.generator_config import AppConfig, save_config
from services import report_service as ui

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = PROJECT_ROOT / "python"
JAVA_DIR = PROJECT_ROOT / "java"

COMPARISON_HEADER = [
    "n", "secuencias_iguales", "primera_diferencia",
    "chi2_python", "chi2_java", "chi2_iguales",
    "p_chi2_python", "p_chi2_java", "p_chi2_iguales",
    "d_ks_python", "d_ks_java", "d_ks_iguales",
    "p_ks_python", "p_ks_java", "p_ks_iguales",
    "frecuencias_iguales", "decision_chi_py", "decision_chi_java",
    "decision_ks_py", "decision_ks_java",
    "tiempo_gen_python_s", "tiempo_chi_python_s", "tiempo_ks_python_s",
    "tiempo_total_python_s",
    "tiempo_gen_java_s", "tiempo_chi_java_s", "tiempo_ks_java_s",
    "tiempo_total_java_s",
    "sha256",
]


class CoordinatorError(RuntimeError):
    """Error del coordinador: localización o ejecución del entorno."""


class JavaToolchain:
    """Localiza y ejecuta el JAR de Java (infraestructura)."""

    JDK_CANDIDATE_GLOBS = (
        "/home/royeljima/tools/jdk*/bin/java",
        "/opt/jdk*/bin/java",
        "/usr/lib/jvm/*/bin/java",
    )
    MAVEN_CANDIDATE_GLOBS = (
        "/home/royeljima/tools/apache-maven*/bin/mvn",
        "/opt/maven*/bin/mvn",
    )

    @classmethod
    def find_java(cls) -> Optional[Path]:
        candidates: List[Path] = []
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            candidates.append(Path(java_home) / "bin" / "java")
        for pattern in cls.JDK_CANDIDATE_GLOBS:
            candidates.extend(sorted(Path(p).resolve() for p in glob.glob(pattern)))
        which = shutil.which("java")
        if which:
            candidates.append(Path(which))
        for candidate in candidates:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    @classmethod
    def find_maven(cls) -> Optional[Path]:
        candidates: List[Path] = []
        for pattern in cls.MAVEN_CANDIDATE_GLOBS:
            candidates.extend(sorted(Path(p) for p in glob.glob(pattern)))
        which = shutil.which("mvn")
        if which:
            candidates.append(Path(which))
        for candidate in candidates:
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return candidate
        return None

    @classmethod
    def find_jar(cls) -> Optional[Path]:
        """El JAR elegible: el ejecutable con Main-Class (el más pesado distinto de «original»)."""
        target = JAVA_DIR / "target"
        if not target.is_dir():
            return None
        jars = sorted(
            (p for p in target.glob("*.jar")
             if "sources" not in p.name and "javadoc" not in p.name
             and not p.name.startswith("original")),
            key=lambda p: p.stat().st_size,
            reverse=True,
        )
        return jars[0] if jars else None

    @classmethod
    def build_jar(cls, quiet: bool = True) -> Path:
        """Compila el proyecto Java con Maven (lleva consigo la ventana de espera)."""
        mvn = cls.find_maven()
        if mvn is None:
            raise CoordinatorError(
                "Maven no está disponible para compilar el JAR de Java. "
                "Consulte README.md, sección «Compilación del proyecto Java»."
            )
        args: List[str] = [str(mvn), "package"]
        if quiet:
            args.insert(1, "-q")
        result = subprocess.run(args, cwd=JAVA_DIR, capture_output=True, text=True,
                                timeout=1800)
        if result.returncode != 0:
            raise CoordinatorError(
                "La compilación Maven falló:\n"
                f"{(result.stdout or '')[-2500:]}\n{(result.stderr or '')[-2500:]}"
            )
        jar = cls.find_jar()
        if jar is None:
            raise CoordinatorError(
                "La compilación terminó, pero no se encontró el JAR en java/target/."
            )
        return jar


class ComparisonService:
    """Coordinador del modo de comparación (opción 3 del menú principal)."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        config.validate()

    # ------------------------------------------------------------------ #
    # Localización del entorno Java
    # ------------------------------------------------------------------ #
    def _ensure_jar(self) -> Path:
        jar = JavaToolchain.find_jar()
        if jar is not None:
            return jar
        if JavaToolchain.find_java() is None:
            raise CoordinatorError(
                "Java no está instalado y no se encontró JDK en JAVA_HOME, el PATH o "
                "~/tools/jdk*/bin/java. Consulte README.md, sección «Configuración de Java»."
            )
        ui.print_warning("JAR no encontrado: se compila con Maven antes de comparar…")
        with ui.console.status("[cyan]Compilando el proyecto Java con Maven…[/]"):
            return JavaToolchain.build_jar()

    # ------------------------------------------------------------------ #
    # Ejecución de un motor headless
    # ------------------------------------------------------------------ #
    def _run_engine(self, engine: str, jar: Optional[Path], config_path: Path,
                    output_path: Path, n: int) -> Dict[str, Any]:
        if engine == "python":
            cmd = [
                sys.executable, str(PYTHON_DIR / "main.py"), "--headless",
                "--config", str(config_path), "--output", str(output_path),
                "--n", str(n), "--no-plots",
            ]
        else:
            java_exe = JavaToolchain.find_java()
            if java_exe is None or jar is None:
                raise CoordinatorError(
                    "No se dispone de Java o del JAR para ejecutar la implementación Java."
                )
            cmd = [
                str(java_exe), "-jar", str(jar), "--headless",
                "--config", str(config_path), "--output", str(output_path),
                "--n", str(n), "--no-plots",
            ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        except FileNotFoundError as exc:
            raise CoordinatorError(f"Comando inexistente al ejecutar {engine}: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise CoordinatorError(f"La implementación {engine} excedió el límite de tiempo.") from exc
        if proc.returncode != 0:
            raise CoordinatorError(
                f"La implementación {engine} terminó con error (rc={proc.returncode}):\n"
                f"stdout: {proc.stdout[-2000:]}\nstderr: {proc.stderr[-2000:]}"
            )
        return ui.read_json_config(output_path)

    # ------------------------------------------------------------------ #
    # Comparación
    # ------------------------------------------------------------------ #
    def _within(self, a: float, b: float) -> bool:
        return abs(a - b) <= self.config.statistical.tolerance

    @staticmethod
    def _sequences_equal(seq_py: Dict[str, Any], seq_jv: Dict[str, Any]) -> bool:
        """Comparación EXACTA: mismo conteo, mismos extremos y misma huella SHA-256."""
        return (
            seq_py.get("count") == seq_jv.get("count")
            and seq_py["first_20_integers"] == seq_jv["first_20_integers"]
            and seq_py["last_20_integers"] == seq_jv["last_20_integers"]
            and seq_py["sha256"] == seq_jv["sha256"]
        )

    def compare_one_n(self, n: int, jar: Path, workdir: Path) -> Dict[str, Any]:
        ui.print_section(f"Comparando para N = {n:,} (reps = {self.config.repetitions})")
        workdir.mkdir(parents=True, exist_ok=True)
        cfg_path = self._config_for_n(n, workdir)
        out_py = workdir / f"resultado_python_n{n}.json"
        out_jv = workdir / f"resultado_java_n{n}.json"

        with ui.console.status("[cyan]Ejecutando implementación Python (subprocess)…[/]"):
            py = self._run_engine("python", None, cfg_path, out_py, n)
        with ui.console.status(f"[cyan]Ejecutando implementación Java por subprocess (Java)…[/]"):
            jv = self._run_engine("java", jar, cfg_path, out_jv, n)

        chi_py, chi_jv = py["chi_square"], jv["chi_square"]
        ks_py, ks_jv = py["kolmogorov_smirnov"], jv["kolmogorov_smirnov"]
        seq_py, seq_jv = py["sequence"], jv["sequence"]
        t_py, t_jv = py["times_seconds"], jv["times_seconds"]

        sequences_equal = self._sequences_equal(seq_py, seq_jv)
        row: Dict[str, Any] = {
            "n": n,
            "sequences_equal": sequences_equal,
            "first_diff": None if sequences_equal else self._search_first_diff(seq_py, seq_jv),
            "chi_py": chi_py["statistic"], "chi_java": chi_jv["statistic"],
            "chi_stats_equal": self._within(chi_py["statistic"], chi_jv["statistic"]),
            "p_chi_py": chi_py["p_value"], "p_chi_java": chi_jv["p_value"],
            "p_chi_absdiff": abs(chi_py["p_value"] - chi_jv["p_value"]),
            "p_chi_eq": self._within(chi_py["p_value"], chi_jv["p_value"]),
            "ks_py": ks_py["statistic"], "ks_java": ks_jv["statistic"],
            "d_ks_eq": self._within(ks_py["statistic"], ks_jv["statistic"]),
            "p_ks_py": ks_py["p_value"], "p_ks_java": ks_jv["p_value"],
            "p_ks_absdiff": abs(ks_py["p_value"] - ks_jv["p_value"]),
            "p_ks_eq": self._within(ks_py["p_value"], ks_jv["p_value"]),
            "frequencies_equal": chi_py["observed"] == chi_jv["observed"],
            "t_gen_python": t_py["generation"] * 1000.0,
            "t_gen_java": t_jv["generation"] * 1000.0,
            "t_chi_python": t_py["chi_square"] * 1000.0,
            "t_chi_java": t_jv["chi_square"] * 1000.0,
            "t_ks_python": t_py["ks"] * 1000.0,
            "t_ks_java": t_jv["ks"] * 1000.0,
            "t_python": (t_py["generation"] + t_py["chi_square"] + t_py["ks"]) * 1000.0,
            "t_java": (t_jv["generation"] + t_jv["chi_square"] + t_jv["ks"]) * 1000.0,
            "sha256": seq_py["sha256"],
            "raw": {"python": py, "java": jv},
        }
        row["decisions_equal"] = (
            chi_py["reject_h0"] == chi_jv["reject_h0"]
            and ks_py["reject_h0"] == ks_jv["reject_h0"]
        )
        ui.show_comparison_rows([self._display_row(row)])
        self._report_mismatches(row)
        return row

    @staticmethod
    def _search_first_diff(seq_py: Dict[str, Any], seq_jv: Dict[str, Any]) -> Optional[int]:
        """Posición conocida de la primera diferencia (en los extremos exportados)."""
        py_ints = list(seq_py["first_20_integers"]) + list(seq_py["last_20_integers"])
        jv_ints = list(seq_jv["first_20_integers"]) + list(seq_jv["last_20_integers"])
        for i, (a, b) in enumerate(zip(py_ints, jv_ints)):
            if a != b:
                return i
        return None if py_ints == jv_ints else 0

    @staticmethod
    def _display_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Fila lista para `show_comparison_rows` (sin el JSON crudo)."""
        cloned = {k: v for k, v in row.items() if k != "raw"}
        cloned["first_diff_pos"] = row["first_diff"] if row["first_diff"] is not None else "—"
        return cloned

    def _report_mismatches(self, row: Dict[str, Any]) -> None:
        if not row["sequences_equal"]:
            ui.print_error(
                f"Las secuencias NO coinciden exactamente para N={row['n']}: "
                "revisar la implementación del LCG en ambos lenguajes."
            )
        if not row["frequencies_equal"]:
            ui.print_warning(
                f"Las frecuencias observadas difieren para N={row['n']} "
                "(consecuencia de una secuencia distinta)."
            )
        if not row["p_chi_eq"]:
            ui.print_warning(
                f"Valores p de Chi-cuadrado difieren más que la tolerancia "
                f"(Δ = {row['p_chi_absdiff']:.2e})."
            )
        if not row["p_ks_eq"]:
            ui.print_warning(
                f"Valores p de KS difieren más que la tolerancia "
                f"(Δ = {row['p_ks_absdiff']:.2e})."
            )

    def _config_for_n(self, n: int, workdir: Path) -> Path:
        """Escribe un JSON de configuración con el N específico (protocolo compartido)."""
        cfg = copy.deepcopy(self.config).with_n(n)
        path = workdir / f"config_n{n}.json"
        save_config(cfg, path)
        return path

    # ------------------------------------------------------------------ #
    # Flujo completo
    # ------------------------------------------------------------------ #
    def run_comparison(self, sizes: Optional[List[int]] = None) -> List[Dict[str, Any]]:
        sizes = sizes or self.config.comparison_sizes
        jar = self._ensure_jar()
        out_root = PROJECT_ROOT / "results"
        final_dirs = out_root / "final_report"
        workdir = Path(os.environ.get("TMPDIR", "/tmp")) / "opencode" / "lcg_runs"

        ui.print_section("MODO COMPARATIVO PYTHON ↔ JAVA")
        rows: List[Dict[str, Any]] = []
        for n in sizes:
            rows.append(self.compare_one_n(n, jar, workdir))

        csv_rows = [self._csv_row(r) for r in rows]
        csv_path = ui.export_csv(out_root / "comparison.csv", COMPARISON_HEADER, csv_rows)
        stamped_csv_path = ui.export_csv(
            final_dirs / ui.timestamped_name("comparacion", "csv"),
            COMPARISON_HEADER, csv_rows,
        )
        json_payload = {
            "parameters": self.config.to_dict(),
            "rows": [{k: v for k, v in r.items() if k != "raw"} for r in rows],
        }
        json_path = ui.export_json(out_root / "comparison.json", json_payload)
        report_path = final_dirs / ui.timestamped_name("informe_comparativo", "md")
        report_path.write_text(self._markdown_report(rows), encoding="utf-8")

        ui.print_paths([csv_path, stamped_csv_path, json_path, report_path],
                       "Archivos del modo comparativo")
        return rows

    def _csv_row(self, row: Dict[str, Any]) -> List[Any]:
        py = row["raw"]["python"]
        jv = row["raw"]["java"]
        decision_py_chi = "Rechaza H0" if py["chi_square"]["reject_h0"] else "No rechaza H0"
        decision_jv_chi = "Rechaza H0" if jv["chi_square"]["reject_h0"] else "No rechaza H0"
        decision_py_ks = "Rechaza H0" if py["kolmogorov_smirnov"]["reject_h0"] else "No rechaza H0"
        decision_jv_ks = "Rechaza H0" if jv["kolmogorov_smirnov"]["reject_h0"] else "No rechaza H0"
        return [
            row["n"], "SI" if row["sequences_equal"] else "NO",
            row["first_diff"] if row["first_diff"] is not None else "",
            row["chi_py"], row["chi_java"], "SI" if row["chi_stats_equal"] else "NO",
            row["p_chi_py"], row["p_chi_java"], "SI" if row["p_chi_eq"] else "NO",
            row["ks_py"], row["ks_java"], "SI" if row["d_ks_eq"] else "NO",
            row["p_ks_py"], row["p_ks_java"], "SI" if row["p_ks_eq"] else "NO",
            "SI" if row["frequencies_equal"] else "NO",
            decision_py_chi, decision_jv_chi, decision_py_ks, decision_jv_ks,
            row["t_gen_python"], row["t_chi_python"], row["t_ks_python"], row["t_python"],
            row["t_gen_java"], row["t_chi_java"], row["t_ks_java"], row["t_java"],
            row["sha256"],
        ]

    def _markdown_report(self, rows: List[Dict[str, Any]]) -> str:
        cfg = self.config
        lines = [
            "# Reporte comparativo Python ↔ Java",
            "",
            "- Valores provenientes de ejecuciones reales coordinadas por subprocess.",
            f"- Parámetros: X0 = {cfg.generator.seed}, a = {cfg.generator.multiplier}, "
            f"c = {cfg.generator.increment}, m = {cfg.generator.modulus}.",
            f"- α = {cfg.statistical.alpha}; intervalos k = {cfg.statistical.intervals}; "
            f"grados de libertad = {cfg.statistical.intervals - 1}.",
            f"- Repeticiones para el promedio de tiempos: {cfg.repetitions} "
            "(tras 1 ejecución de calentamiento no medida).",
            f"- Tolerancia para estadísticos/valores p entre bibliotecas: "
            f"{cfg.statistical.tolerance}.",
            "- Comparación de secuencias: EXACTA (SHA-256 + enteros iniciales/finales).",
            "",
            "| N | Sec. iguales | χ² Py | χ² Jv | p χ² Py | p χ² Jv | "
            "D KS Py | D KS Jv | p KS Py | p KS Jv | Tiempo Py (ms) | Tiempo Jv (ms) |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
        for row in rows:
            lines.append(
                f"| {row['n']} | {'SÍ' if row['sequences_equal'] else 'NO'} "
                f"| {row['chi_py']:.4f} | {row['chi_java']:.4f} "
                f"| {row['p_chi_py']:.6f} | {row['p_chi_java']:.6f} "
                f"| {row['ks_py']:.6f} | {row['ks_java']:.6f} "
                f"| {row['p_ks_py']:.6f} | {row['p_ks_java']:.6f} "
                f"| {row['t_python']:.1f} | {row['t_java']:.1f} |"
            )
        lines += [
            "",
            "## Interpretación",
            "",
            "- «Sec. iguales»: las secuencias de enteros X(n) coinciden exactamente "
            "(misma semilla, multiplicador, incremento, módulo y N).",
            "- Estadísticos valores p: chi-cuadrado usa la cola superior de la "
            "distribución χ² (SciPy en Python; Commons Math en Java); KS usa "
            "convenciones exacta/asintótica compatibles según el tamaño de muestra.",
            "- Los tiempos por biblioteca no son resultados estadísticos y se "
            "presentan por separado; NO incluyen importación, carga de la JVM "
            "ni generación de gráficas.",
        ]
        return "\n".join(lines) + "\n"
