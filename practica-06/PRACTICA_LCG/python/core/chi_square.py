"""
Prueba de bondad de ajuste Chi-cuadrado.

Capa de dominio (implementación concrete del patrón Strategy). Divide
[0,1) en k intervalos semiabiertos [a, b), calcula las frecuencias
observadas y esperadas, el estadístico χ² = Σ (Oi − Ei)² / Ei con
Ei = N/k y los grados de libertad gl = k − 1; obtiene el valor p de la
distribución Chi-cuadrado mediante SciPy (`scipy.stats.chi2.sf`, cola
superior exacta para los gl dados).
"""

from __future__ import annotations

import math
from typing import List, Sequence

from scipy import stats as scipy_stats

from core.statistical_test import StatisticalTest, TestResult


class ChiSquareTestImplementationError(ValueError):
    """Errores internos del cálculo Chi-cuadrado."""


class ChiSquareTest(StatisticalTest):
    """Estrategia: prueba Chi-cuadrado de uniformidad."""

    name = "Chi-cuadrado"
    short_name = "chi_square"

    def execute(self, sequence: Sequence[float], alpha: float = 0.05,
                intervals: int = 10) -> TestResult:
        if len(sequence) == 0:
            raise ChiSquareTestImplementationError("La secuencia está vacía: no es posible ejecutar Chi-cuadrado.")
        if intervals < 2:
            raise ChiSquareTestImplementationError("Se requieren al menos 2 intervalos.")
        k = intervals
        n = len(sequence)
        expected = n / k
        if expected < 5.0:
            # Regla de Cochran: la validez de la aproximación χ² requiere Ei ≥ 5.
            raise ChiSquareTestImplementationError(
                f"La frecuencia esperada Ei = {expected:.2f} es menor que 5; "
                "aumente N o reduzca el número de intervalos."
            )

        observed = [0] * k
        for value in sequence:
            # El último intervalo absorbe por truncamiento cualquier borde
            # numérico; los demás son semiabiertos [a, b).
            index = int(math.floor(value * k))
            if index < 0 or index >= k:
                raise ChiSquareTestImplementationError(
                    f"Valor fuera de [0,1): no se puede clasificar ({value!r})."
                )
            observed[index] += 1

        chi_statistic = 0.0
        contributions: List[float] = []
        for i in range(k):
            contribution = (observed[i] - expected) ** 2 / expected
            contributions.append(contribution)
            chi_statistic += contribution

        degrees_freedom = k - 1
        # Valor p = P(χ²_gl ≥ estadístico), cola superior de `scipy.stats.chi2`.
        p_value = float(scipy_stats.chi2.sf(chi_statistic, degrees_freedom))

        reject_h0, decision = self.decide(p_value, alpha)
        result = TestResult(
            test_name=self.name,
            sample_size=n,
            statistic=chi_statistic,
            p_value=p_value,
            alpha=alpha,
            reject_h0=reject_h0,
            decision=decision,
            degrees_freedom=degrees_freedom,
            observed=observed,
            expected=[expected] * k,
            details={
                "expected_frequency": expected,
                "interval_labels": self.interval_labels(k),
                "contributions": contributions,
                "interval_edges": self.interval_edges(k),
                "p_value_source": "scipy.stats.chi2.sf (distribución chi-cuadrado, cola superior, gl=k-1)",
            },
        )
        result.validate_consistency()
        return result

    # ------------------------------------------------------------------ #
    # Etiquetas para la tabla de frecuencias
    # ------------------------------------------------------------------ #
    @staticmethod
    def interval_labels(k: int) -> List[str]:
        width = 1.0 / k
        return [f"{i * width:.4g} - {(i + 1) * width:.4g}" for i in range(k)]

    @staticmethod
    def interval_edges(k: int) -> List[List[float]]:
        width = 1.0 / k
        return [[i * width, (i + 1) * width] for i in range(k)]
