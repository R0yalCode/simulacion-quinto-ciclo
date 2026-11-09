"""
Configuración del sistema de simulación estadística (LCG).

Módulo de la capa de configuración: define los parámetros del generador
congruencial lineal, los parámetros estadísticos de las pruebas y los
parámetros del modo comparativo. Incluye la validación y la persistencia
en formato JSON.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List


class ParameterValidationError(ValueError):
    """Excepción lanzada cuando un parámetro configurado no es válido."""


@dataclass(frozen=True)
class LcgParameters:
    """Parámetros del generador congruencial lineal: X(n+1) = (a·X(n) + c) mod m."""

    seed: int = 12345
    multiplier: int = 1664525
    increment: int = 1013904223
    modulus: int = 4294967296  # 2^32
    n: int = 1000

    def validate(self) -> None:
        """Valida los parámetros del LCG y lanza ParameterValidationError si no lo son."""
        if self.modulus <= 0:
            raise ParameterValidationError("El módulo (m) debe ser un entero positivo.")
        if self.modulus < 2:
            raise ParameterValidationError("El módulo (m) debe ser mayor o igual que 2.")
        if not (0 <= self.seed < self.modulus):
            raise ParameterValidationError(
                f"La semilla debe estar en el rango [0, {self.modulus - 1}]."
            )
        if self.multiplier < 0:
            raise ParameterValidationError("El multiplicador (a) no puede ser negativo.")
        if self.increment < 0:
            raise ParameterValidationError("El incremento (c) no puede ser negativo.")
        if self.n <= 0:
            raise ParameterValidationError("La cantidad de números (N) debe ser mayor que cero.")
        if self.n > 20_000_000:
            raise ParameterValidationError("La cantidad de números (N) no puede exceder 20.000.000.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StatisticalParameters:
    """Parámetros de las pruebas de uniformidad (chi-cuadrado y Kolmogorov-Smirnov)."""

    alpha: float = 0.05
    intervals: int = 10
    tolerance: float = 1e-4  # tolerancia para comparar valores p entre bibliotecas

    def validate(self) -> None:
        if not (0.0 < self.alpha < 1.0):
            raise ParameterValidationError("El nivel de significancia (α) debe estar en (0, 1).")
        if self.intervals < 2:
            raise ParameterValidationError("El número de intervalos debe ser al menos 2.")
        if self.intervals > 1000:
            raise ParameterValidationError("El número de intervalos no puede exceder 1000.")
        if self.tolerance <= 0:
            raise ParameterValidationError("La tolerancia comparativa debe ser mayor que cero.")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AppConfig:
    """Configuración completa de la aplicación (generador + estadística + comparación)."""

    generator: LcgParameters = field(default_factory=LcgParameters)
    statistical: StatisticalParameters = field(default_factory=StatisticalParameters)
    comparison_sizes: List[int] = field(default_factory=lambda: [1000, 10000, 100000, 1000000])
    repetitions: int = 3  # repeticiones para promediar tiempos en el modo comparativo

    def validate(self) -> None:
        self.generator.validate()
        self.statistical.validate()
        if not self.comparison_sizes:
            raise ParameterValidationError("Debe existir al menos un tamaño N para la comparación.")
        for size in self.comparison_sizes:
            if size <= 0:
                raise ParameterValidationError(
                    "Los tamaños N del modo comparativo deben ser mayores que cero."
                )
            if size > 20_000_000:
                raise ParameterValidationError(
                    "Los tamaños N del modo comparativo no pueden exceder 20.000.000."
                )
        if self.repetitions < 1:
            raise ParameterValidationError("Las repeticiones de medición deben ser al menos 1.")
        if self.repetitions > 10:
            raise ParameterValidationError("Las repeticiones de medición no pueden exceder 10.")

    def with_n(self, n: int) -> "AppConfig":
        """Copia la configuración con un N específico (los parámetros son inmutables)."""
        return replace(self, generator=replace(self.generator, n=n))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generator": self.generator.to_dict(),
            "statistical": self.statistical.to_dict(),
            "comparison_sizes": list(self.comparison_sizes),
            "repetitions": self.repetitions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        """Construye una configuración a partir de un diccionario JSON parseado."""
        def _int(value: Any) -> int:
            # Google Gson (Java) puede entregar enteros grandes como float 1.0E9.
            if isinstance(value, bool):
                raise ParameterValidationError("Se esperaba un número entero.")
            if isinstance(value, float):
                if not value.is_integer():
                    raise ParameterValidationError(f"Se esperaba un entero y se recibió: {value}")
                return int(value)
            if isinstance(value, int):
                return value
            raise ParameterValidationError(f"Valor no numérico: {value!r}")

        def _float(value: Any) -> float:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return float(value)
            raise ParameterValidationError(f"Valor no numérico: {value!r}")

        generator = data.get("generator", {})
        statistical = data.get("statistical", {})
        config = cls(
            generator=LcgParameters(
                seed=_int(generator.get("seed", 12345)),
                multiplier=_int(generator.get("multiplier", 1664525)),
                increment=_int(generator.get("increment", 1013904223)),
                modulus=_int(generator.get("modulus", 4294967296)),
                n=_int(generator.get("n", 1000)),
            ),
            statistical=StatisticalParameters(
                alpha=_float(statistical.get("alpha", 0.05)),
                intervals=_int(statistical.get("intervals", 10)),
                tolerance=_float(statistical.get("tolerance", 1e-4)),
            ),
            comparison_sizes=[_int(x) for x in data.get("comparison_sizes", [1000, 10000, 100000, 1000000])],
            repetitions=_int(data.get("repetitions", 3)),
        )
        config.validate()
        return config


def default_config() -> AppConfig:
    """Configuración por defecto de la práctica."""
    return AppConfig()


def load_config(path: Path) -> AppConfig:
    """Carga la configuración desde un archivo JSON; valida y devuelve AppConfig."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ParameterValidationError(f"No se encontró el archivo de configuración: {path}") from exc
    except OSError as exc:
        raise ParameterValidationError(f"No se pudo leer la configuración {path}: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ParameterValidationError(f"JSON inválido en {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ParameterValidationError(f"El contenido de {path} debe ser un objeto JSON.")
    return AppConfig.from_dict(data)


def save_config(config: AppConfig, path: Path) -> None:
    """Guarda la configuración en JSON (formato canónico compartido con Java)."""
    config.validate()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as exc:
        raise ParameterValidationError(f"No se pudo guardar la configuración en {path}: {exc}") from exc
