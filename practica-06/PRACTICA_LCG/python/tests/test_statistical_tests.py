"""
Pruebas unitarias de Chi-cuadrado y Kolmogorov-Smirnov con secuencias
conocidas (independientes de los parámetros LCG).
"""

from __future__ import annotations

import pytest

from core.chi_square import ChiSquareTest
from core.kolmogorov_smirnov import KolmogorovSmirnovTest


def _perfectly_uniform_sequence(k: int, per_bin: int):
    # per_bin valores en el centro de cada intervalo ⇒ O_i = per_bin, χ² = 0.
    sequence = []
    for i in range(k):
        center = (i + 0.5) / k
        sequence.extend([center] * per_bin)
    return sequence


def test_chi_square_zero_for_perfect_uniformity():
    k, per_bin = 10, 10
    result = ChiSquareTest().execute(_perfectly_uniform_sequence(k, per_bin),
                                     alpha=0.05, intervals=k)
    assert result.statistic == pytest.approx(0.0, abs=1e-12)
    assert result.sample_size == k * per_bin
    assert result.degrees_freedom == 9
    assert sum(result.observed) == result.sample_size  # observadas suman N
    assert result.expected == [result.sample_size / k] * k  # esperadas suman N
    assert sum(result.expected) == result.sample_size
    assert result.p_value == pytest.approx(1.0)
    assert result.reject_h0 == False  # noqa: E712 — criterio p >= α ⇒ no rechazo


def test_chi_square_known_extreme_case():
    # Todos los valores en el primer intervalo: χ² = 9·(0−10)²/10 + (100−10)²/10
    k = 10
    sequence = [0.05] * 100
    result = ChiSquareTest().execute(sequence, intervals=k)
    expected_value = (9 * 100.0 + 8100.0) / 10.0
    assert result.statistic == pytest.approx(expected_value, rel=1e-12)
    assert result.p_value == pytest.approx(0.0, abs=1e-12)
    assert result.reject_h0 is True


def test_chi_square_grades_of_freedom_follow_k():
    result = ChiSquareTest().execute(_perfectly_uniform_sequence(5, 20), intervals=5)
    assert result.degrees_freedom == 4


def test_chi_square_requires_expected_frequency_at_least_5():
    with pytest.raises(ValueError):
        ChiSquareTest().execute([0.5] * 40, intervals=10)  # Ei = 4 < 5


def test_ks_known_d_minus_diagonal():
    # U(i) = i/(n+1) ⇒ D+ = 1/(n+1) (en i=n) y D− = 1/(n+1) (en i=1) ⇒ D = 1/(n+1).
    # Con this form todos los valores quedan estrictamente dentro de [0, 1).
    n = 100
    sequence = [i / (n + 1) for i in range(1, n + 1)]
    result = KolmogorovSmirnovTest().execute(sequence)
    assert result.statistic == pytest.approx(1.0 / (n + 1), rel=1e-9)
    assert result.details["d_plus"] == pytest.approx(1.0 / (n + 1), rel=1e-9)
    assert 0.0 <= result.p_value <= 1.0
    assert result.reject_h0 is False  # D=1/N ⇒ p≈0.99, no se rechaza


def test_ks_statistic_bounds_and_decision():
    import random as _random

    # Ojo: se usa random solo para construir CASO DE PRUEBA conocido, no para el LCG.
    _random.seed(42)
    sequence = sorted(_random.random() for _ in range(500))
    result = KolmogorovSmirnovTest().execute(sequence)
    assert 0.0 <= result.statistic <= 1.0
    assert 0.0 <= result.p_value <= 1.0
    assert result.reject_h0 == (result.p_value < result.alpha)


def test_ks_empty_sequence_rejected():
    with pytest.raises(ValueError):
        KolmogorovSmirnovTest().execute([])


def test_chi_square_empty_sequence_rejected():
    with pytest.raises(ValueError):
        ChiSquareTest().execute([], intervals=10)
