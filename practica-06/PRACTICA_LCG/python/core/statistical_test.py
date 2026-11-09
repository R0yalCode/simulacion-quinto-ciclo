"""
Contrato (patrón Strategy) para las pruebas estadísticas de uniformidad.

Capa de dominio. Define el resultado estructurado de una prueba y la
interfaz común `StatisticalTest` que implementan ChiSquareTest y
KolmogorovSmirnovTest, de modo que los menús y servicios no quedan
acoplados al cálculo estadístico concreto.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Sequence


@dataclass
class TestResult:
    """Resultado estructurado de una prueba estadística."""

    test_name: str
    sample_size: int
    statistic: float
    p_value: float
    alpha: float
    reject_h0: bool
    decision: str
    degrees_freedom: Optional[int] = None
    observed: Optional[List[int]] = None
    expected: Optional[List[float]] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def validate_consistency(self) -> None:
        """Reglas invariantes que todo resultado debe cumplir."""
        if self.sample_size < 0:
            raise ValueError("El tamaño de muestra no puede ser negativo.")
        if self.p_value < 0.0 or self.p_value > 1.0:
            raise ValueError("El valor p debe pertenecer al intervalo [0, 1].")
        if self.statistic < 0.0:
            raise ValueError("El estadístico de prueba no puede ser negativo.")
        if self.reject_h0 != (self.p_value < self.alpha):
            raise ValueError("La decisión debe coherir con el criterio p < α.")
        if self.observed is not None and sum(self.observed) != self.sample_size:
            raise ValueError("Las frecuencias observadas deben sumar N.")

    def summary_line(self) -> str:
        """Texto corto para tablas comparativas."""
        return f"stat={self.statistic:.6f}, p={self.p_value:.6f}"

    def to_dict(self) -> Dict[str, Any]:
        """Representación serializable en JSON (protocolo Python ↔ Java)."""
        return asdict(self)


class StatisticalTest(ABC):
    """
    Interfaz Strategy para las pruebas de uniformidad.

    Cada estrategia recibe la secuencia normalizada U(i) ∈ [0,1) y los
    parámetros estadísticos, ejecuta su prueba y devuelve un `TestResult`.
    """

    name: str = "Prueba estadística"
    short_name: str = "test"

    @abstractmethod
    def execute(self, sequence: Sequence[float], alpha: float = 0.05,
                intervals: int = 10) -> TestResult:
        """Ejecuta la prueba sobre la secuencia y devuelve el resultado."""

    def decide(self, p_value: float, alpha: float) -> Tuple[bool, str]:
        """Criterio estándar: se rechaza H0 si p < α."""
        reject = p_value < alpha
        if reject:
            decision = (
                f"Valor p = {p_value:.6f} < α = {alpha}: SE RECHAZA H0 "
                f"(no hay evidencia de uniformidad)."
            )
        else:
            decision = (
                f"Valor p = {p_value:.6f} ≥ α = {alpha}: NO se rechaza H0 "
                f"(la secuencia es compatible con U(0,1))."
            )
        return reject, decision
