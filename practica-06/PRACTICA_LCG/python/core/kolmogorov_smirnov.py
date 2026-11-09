"""
Prueba Kolmogorov-Smirnov de una muestra.

Capa de dominio (implementación concreta del patrón Strategy). Compara la
función de distribución acumulada empírica F_N con la uniforme teórica
U(0, 1):

    D+ = max(i/N − U(i)),   D− = max(U(i) − (i−1)/N),   D = max(D+, D−)

Los datos se ordenan ascendentemente. El estadístico D se calcula
manualmente y el valor p se obtiene con SciPy (`scipy.stats.kstest`
contra la hipótesis nula 'uniform'), que emplea la distribución exacta de
Kolmogorov para muestras pequeñas y la asintótica para muestras grandes;
Apache Commons Math (en Java) aplica la misma convención, por lo que los
valores p entre ambos lenguajes son comparables.

LIMITACIÓN DOCUMENTADA: la prueba KS asume una variable continua con
valores distintos. Con datos discretos con pocas cuantías distintas, el
valor p pierde exactitud y debe interpretarse como aproximado. Con los
parámetros por defecto (m = 2³²) los valores U(i) son puntos de una malla
de 2³² niveles y los empates son prácticamente imposibles; si el usuario
elige módulos pequeños, la consecuencia anterior debe recordarse.
"""

from __future__ import annotations

from math import sqrt
from typing import Sequence

from scipy import stats as scipy_stats

from core.statistical_test import StatisticalTest, TestResult


class KolmogorovSmirnovImplementationError(ValueError):
    """Errores internos del cálculo Kolmogorov-Smirnov."""


def uniform_theoretical_cdf(x: float) -> float:
    """Función de distribución acumulada teórica de U(0, 1)."""
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


class KolmogorovSmirnovTest(StatisticalTest):
    """Estrategia: prueba Kolmogorov-Smirnov de uniformidad."""

    name = "Kolmogorov-Smirnov"
    short_name = "ks"

    def execute(self, sequence: Sequence[float], alpha: float = 0.05,
                intervals: int = 10) -> TestResult:
        del intervals  # parámetro homogéneo de la interfaz Strategy; KS no lo usa
        n = len(sequence)
        if n == 0:
            raise KolmogorovSmirnovImplementationError(
                "La secuencia está vacía: no es posible ejecutar Kolmogorov-Smirnov."
            )
        ordered = sorted(sequence)
        for value in ordered:
            if value < 0.0 or value >= 1.0:
                raise KolmogorovSmirnovImplementationError(
                    f"Valor fuera de [0,1): no es una variable U(0,1) ({value!r})."
                )

        d_plus = 0.0
        d_minus = 0.0
        for i in range(1, n + 1):
            u = ordered[i - 1]
            d_plus = max(d_plus, i / n - u)
            d_minus = max(d_minus, u - (i - 1) / n)
        statistic = max(d_plus, d_minus)

        # Valor p con SciPy (implementación estadística confiable), misma
        # convención exacta/asintótica que Apache Commons Math.
        ks_result = scipy_stats.kstest(ordered, "uniform")
        p_value = float(ks_result.pvalue)
        scipy_statistic = float(ks_result.statistic)  # verificación cruzada

        # Referencia de diagnóstico: aproximación asintótica de Kolmogorov
        # Q(D·(√n + 0.12 + 0.11/√n)). No se usa como valor p principal.
        corrected = statistic * (sqrt(n) + 0.12 + 0.11 / sqrt(n))
        asymptotic_reference = float(scipy_stats.kstwobign.sf(corrected))

        reject_h0, decision = self.decide(p_value, alpha)
        result = TestResult(
            test_name=self.name,
            sample_size=n,
            statistic=statistic,
            p_value=p_value,
            alpha=alpha,
            reject_h0=reject_h0,
            decision=decision,
            degrees_freedom=None,
            observed=None,
            expected=None,
            details={
                "d_plus": d_plus,
                "d_minus": d_minus,
                "scipy_statistic": scipy_statistic,
                "asymptotic_reference_p": asymptotic_reference,
                "p_value_source": (
                    "scipy.stats.kstest: distribución exacta de Kolmogorov para n pequeño "
                    "y aproximación asintótica para n grande"
                ),
                "discrete_data_caveat": (
                    "Con módulos pequeños (p. ej. m ≤ 10⁶) aparecen empates; el valor p "
                    "de KS es entonces aproximado, no exacto."
                ),
            },
        )
        result.validate_consistency()
        return result
