#!/usr/bin/env python3
"""
Sistema de simulación estadística — Generador pseudoaleatorio LCG.

Punto de entrada de la implementación Python:

- menú principal interactivo (opciones 1 a 5, 0);
- submenú de ejecución con generación y pruebas (patrón Strategy);
- edición de parámetros con validación y persistencia JSON;
- modo comparativo Python <-> Java coordinado por subprocess;
- modo headless (CLI) para el coordinador comparativo.

Ejemplos:
    python python/main.py                                  # modo interactivo
    python python/main.py --headless --config cfg.json --output out.json --n 1000
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Tuple

PYTHON_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PYTHON_DIR.parent
for candidate in (PYTHON_DIR, PROJECT_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from config.generator_config import (  # noqa: E402
    AppConfig,
    ParameterValidationError,
    load_config,
    save_config,
)
from core.chi_square import ChiSquareTest  # noqa: E402
from core.kolmogorov_smirnov import KolmogorovSmirnovTest  # noqa: E402
from core.lcg import LcgError  # noqa: E402
from services import report_service as ui  # noqa: E402
from services.comparison_service import (  # noqa: E402
    ComparisonService,
    CoordinatorError,
    JavaToolchain,
)
from services.execution_service import ExecutionService, ExecutionError  # noqa: E402

CONFIG_PATH = PYTHON_DIR / "config" / "parameters.json"
CURRENT_CONFIG: AppConfig


# ---------------------------------------------------------------------- #
# Lectura validada de entradas
# ---------------------------------------------------------------------- #
def read_int(prompt: str, default: int, validator: Optional[Callable[[int], None]] = None) -> int:
    """Lee un entero; empty line valida el valor por defecto."""
    while True:
        raw = ui.console.input(f"[bold cyan]{prompt}[/] [dim](enter = {default})[/]: ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            ui.print_error("Debe escribir un número entero (sin decimales).")
            continue
        if validator is not None:
            try:
                validator(value)
            except ParameterValidationError as exc:
                ui.print_error(str(exc))
                continue
            except (ValueError, OverflowError) as exc:
                ui.print_error(f"Valor no permitido: {exc}")
                continue
        return value


def read_float(prompt: str, default: float,
               validator: Optional[Callable[[float], None]] = None) -> float:
    while True:
        raw = ui.console.input(f"[bold cyan]{prompt}[/] [dim](enter = {default})[/]: ").strip()
        if not raw:
            return default
        try:
            value = float(raw.replace(",", "."))
        except ValueError:
            ui.print_error("Debe escribir un número decimal (ejemplo: 0.05).")
            continue
        if validator is not None:
            try:
                validator(value)
            except ParameterValidationError as exc:
                ui.print_error(str(exc))
                continue
            except (ValueError, OverflowError) as exc:
                ui.print_error(f"Valor no permitido: {exc}")
                continue
        return value


def read_bool(prompt: str, default: bool = False) -> bool:
    hint = "s/n" if default else "n/s"
    while True:
        raw = ui.console.input(f"[bold cyan]{prompt}[/] [dim]({hint})[/]: ").strip().lower()
        if not raw:
            return default
        if raw in ("s", "si", "sí", "y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        ui.print_error("Responda con «s» o «n».")


def ask_menu_option(label: str, valid: Tuple[str, ...]) -> str:
    while True:
        option = ui.console.input(f"[bold yellow]{label}[/]: ").strip()
        if option in valid:
            return option
        ui.print_error(f"Opción inválida. Debe ser una de: {', '.join(valid)}")


# ---------------------------------------------------------------------- #
# Menús
# ---------------------------------------------------------------------- #
def _menu_table(entries) -> None:
    from rich.table import Table

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan")
    table.add_column()
    for key, text in entries:
        table.add_row(f"[{key}]", text)
    ui.console.print(table)


def main_menu() -> str:
    ui.console.print()
    ui.console.print(ui.Text.from_markup("[bold]MENÚ PRINCIPAL[/]"))
    _menu_table([
        ("1", "Ejecutar implementación Python"),
        ("2", "Ejecutar implementación Java"),
        ("3", "Ejecutar ambas implementaciones y comparar"),
        ("4", "Configurar parámetros del generador"),
        ("5", "Consultar información de la práctica"),
        ("0", "Salir del programa"),
    ])
    return ask_menu_option("Seleccione una opción", ("0", "1", "2", "3", "4", "5"))


def execution_menu() -> str:
    ui.print_section("MENÚ DE EJECUCIÓN")
    _menu_table([
        ("1", "Generar números pseudoaleatorios (LCG)"),
        ("2", "Ejecutar prueba Chi-cuadrado"),
        ("3", "Ejecutar prueba Kolmogorov-Smirnov"),
        ("4", "Ejecutar proceso completo (pruebas + gráficas + reporte)"),
        ("0", "Regresar al menú principal"),
    ])
    ui.show_config(CURRENT_CONFIG)
    return ask_menu_option("Seleccione una opción", ("0", "1", "2", "3", "4"))


# ---------------------------------------------------------------------- #
# Acciones
# ---------------------------------------------------------------------- #
def run_python_implementation(session: ExecutionService) -> None:
    while True:
        option = execution_menu()
        if option == "0":
            return
        try:
            if option == "1":
                session.flow_generate()
            elif option == "2":
                session.flow_test(session.chi_strategy)
            elif option == "3":
                session.flow_test(session.ks_strategy)
            elif option == "4":
                session.flow_full()
        except ExecutionError as exc:
            ui.print_error(str(exc))
            ui.print_warning(
                "Volvemos al menú de ejecución; puede ajustar los parámetros "
                "en la opción 4 del menú principal."
            )
        except LcgError as exc:
            ui.print_error(f"Error del generador LCG: {exc}")


def run_java_implementation() -> None:
    jar = JavaToolchain.find_jar()
    if jar is None:
        if JavaToolchain.find_java() is None:
            ui.print_error(
                "Java no está disponible. Instale un JDK (p. ej. Temurin 21) o configure "
                "JAVA_HOME; instrucciones en README.md → «Configuración de Java»."
            )
            return
        if not read_bool("No existe el JAR compilado. ¿Compilar el proyecto Java ahora con Maven?", True):
            return
        try:
            with ui.console.status("[cyan]Compilando el proyecto Java…[/]"):
                jar = JavaToolchain.build_jar()
        except CoordinatorError as exc:
            ui.print_error(str(exc))
            return
    ui.print_section(f"IMPLEMENTACIÓN JAVA — {jar.name}")
    ui.print_warning("El menú interactivo mostrado pertenece a la implementación Java (autónoma).")
    import os

    java_exe = JavaToolchain.find_java()
    proc = subprocess.run([str(java_exe), "-jar", str(jar)], env={**os.environ})
    if proc.returncode != 0:
        ui.print_error(f"La implementación Java finalizó con código {proc.returncode}.")
    else:
        ui.print_success("La implementación Java finalizó correctamente.")


def run_comparison_mode() -> None:
    ui.print_section("MODO COMPARATIVO (OPCIÓN 3)")
    ui.show_config(CURRENT_CONFIG)
    if not read_bool("¿Ejecutar la comparación con esta configuración?", True):
        return
    try:
        ComparisonService(CURRENT_CONFIG).run_comparison()
        ui.print_success(
            "Comparación completada: results/comparison.csv y "
            "results/comparison.json; informe en results/final_report/."
        )
    except CoordinatorError as exc:
        ui.print_error(str(exc))
        ui.print_warning("Verifique la instalación de Java o compile el JAR (README, sección Java).")
    except (OSError, ValueError) as exc:
        ui.print_error(f"Error inesperado en la comparación: {exc}")


def configure_parameters() -> AppConfig:
    """Edita y persiste los parámetros; devuelve la configuración vigente."""
    global CURRENT_CONFIG
    ui.print_section("CONFIGURACIÓN DE PARÁMETROS")
    ui.show_config(CURRENT_CONFIG)
    ui.console.print("[dim]Deje el campo vacío para conservar el valor actual.[/]\n")

    g, s = CURRENT_CONFIG.generator, CURRENT_CONFIG.statistical
    try:
        new_generator = g.__class__(
            seed=read_int("Semilla X0", g.seed),
            multiplier=read_int("Multiplicador a", g.multiplier),
            increment=read_int("Incremento c", g.increment),
            modulus=read_int("Módulo m", g.modulus),
            n=read_int("Cantidad de números N", g.n),
        )
        new_statistical = s.__class__(
            alpha=read_float("Nivel de significancia α", s.alpha),
            intervals=read_int("Número de intervalos k", s.intervals),
            tolerance=read_float("Tolerancia comparativa", s.tolerance),
        )
        sizes_raw = ui.console.input(
            "[bold cyan]Tamaños N comparativos separados por espacios o comas[/] "
            f"[dim](enter = {', '.join(map(str, CURRENT_CONFIG.comparison_sizes))})[/]: "
        ).strip()
        sizes = CURRENT_CONFIG.comparison_sizes
        if sizes_raw:
            sizes = [int(tok) for tok in sizes_raw.replace(",", " ").split()]
        repetitions = read_int("Repeticiones para el promedio de tiempos", CURRENT_CONFIG.repetitions)
    except ValueError as exc:
        ui.print_error(f"Entrada no válida: {exc}")
        return CURRENT_CONFIG

    candidate = AppConfig(
        generator=new_generator,
        statistical=new_statistical,
        comparison_sizes=sizes,
        repetitions=repetitions,
    )
    try:
        candidate.validate()
    except ParameterValidationError as exc:
        ui.print_error(str(exc))
        ui.print_warning("No se aplicaron los cambios.")
        return CURRENT_CONFIG

    try:
        save_config(candidate, CONFIG_PATH)
    except ParameterValidationError as exc:
        ui.print_error(str(exc))
        return CURRENT_CONFIG
    ui.print_success(f"Configuración guardada en {CONFIG_PATH}")
    CURRENT_CONFIG = candidate
    return candidate


# ---------------------------------------------------------------------- #
# Ciclo interactivo
# ---------------------------------------------------------------------- #
def interactive_loop(config: AppConfig) -> None:
    global CURRENT_CONFIG
    CURRENT_CONFIG = config
    ui.print_banner()
    session = ExecutionService(CURRENT_CONFIG)
    while True:
        option = main_menu()
        if option == "0":
            ui.print_success("Gracias por usar el sistema de simulación. ¡Hasta pronto!")
            return
        if option == "1":
            session = ExecutionService(CURRENT_CONFIG)
            run_python_implementation(session)
        elif option == "2":
            run_java_implementation()
        elif option == "3":
            run_comparison_mode()
        elif option == "4":
            configure_parameters()
            session = ExecutionService(CURRENT_CONFIG)
        elif option == "5":
            ui.show_info()


# ---------------------------------------------------------------------- #
# Modo headless para el coordinador
# ---------------------------------------------------------------------- #
def headless_cli(args: argparse.Namespace) -> int:
    try:
        config = load_config(Path(args.config)) if args.config else AppConfig()
        if args.n is not None:
            config = config.with_n(args.n)
        if args.repetitions is not None:
            config.repetitions = args.repetitions
        config.validate()
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        service = ExecutionService(config)
        payload = service.headless_run(output_path, no_plots=args.no_plots)
        print(json.dumps({
            "status": "ok",
            "engine": payload["engine"],
            "sequence_sha256": payload["sequence"]["sha256"],
        }))
        return 0
    except (ParameterValidationError, ValueError, FileNotFoundError, OSError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}), file=sys.stderr)
        return 2


def bootstrap_config() -> AppConfig:
    """Carga parameters.json si existe (válido); si no, lo crea y devuelve el default."""
    if CONFIG_PATH.exists():
        try:
            return load_config(CONFIG_PATH)
        except ParameterValidationError as exc:
            ui.print_error(f"{CONFIG_PATH} inválida: {exc}. Se usan los valores por defecto.")
            return AppConfig()
    config = AppConfig()
    try:
        save_config(config, CONFIG_PATH)
    except ParameterValidationError as exc:  # pragma: no cover
        ui.print_error(str(exc))
    return config


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generador LCG + pruebas Chi-cuadrado y Kolmogorov-Smirnov (Python)"
    )
    parser.add_argument("--headless", action="store_true",
                        help="Ejecución no interactiva para el coordinador")
    parser.add_argument("--config", help="Ruta del JSON de configuración")
    parser.add_argument("--output", help="Ruta del JSON de resultados")
    parser.add_argument("--n", type=int, help="Sobrescribe la cantidad de números N")
    parser.add_argument("--no-plots", action="store_true", help="Omite las gráficas")
    parser.add_argument("--repetitions", type=int, default=None,
                        help="Repeticiones para el promedio de tiempos (default: el del JSON)")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if args.headless:
        return headless_cli(args)
    try:
        interactive_loop(bootstrap_config())
    except KeyboardInterrupt:
        ui.console.print("\n[yellow]Programa interrumpido. Adiós.[/]")
        return 130
    except EOFError:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
