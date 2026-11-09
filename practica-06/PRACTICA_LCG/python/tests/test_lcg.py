"""
Pruebas unitarias del generador LCG (fórmulas por casos conocidos).

Casos didácticos con parámetros pequeños verificados a mano:
con m = 8, a = 5, c = 1, X0 = 1 el periodo es:
    6, 7, 4, 5, 2, 3, 0, 1 → repetición.
"""

from __future__ import annotations

import pytest

from config.generator_config import LcgParameters, ParameterValidationError
from core.lcg import Lcg, LcgError, generate_pair


def test_lcg_known_cycle():
    params = LcgParameters(seed=1, multiplier=5, increment=1, modulus=8, n=8)
    states = Lcg(params).generate_states()
    assert states == [6, 7, 4, 5, 2, 3, 0, 1]


def test_lcg_default_parameters_first_states():
    # X1 = (1664525 · 12345 + 1013904223) mod 2^32, con aritmética exacta de Python.
    params = LcgParameters()  # valores por defecto de la práctica
    x0 = params.seed
    x1 = (params.multiplier * x0 + params.increment) % params.modulus
    x2 = (params.multiplier * x1 + params.increment) % params.modulus
    states = Lcg(params).generate_states()
    assert states[0] == x1
    assert states[1] == x2
    assert len(states) == params.n


def test_uniforms_in_unit_interval_and_count():
    params = LcgParameters(n=500)
    states, uniforms = generate_pair(params)
    assert len(states) == 500
    assert len(uniforms) == 500
    assert all(0.0 <= u < 1.0 for u in uniforms)
    assert all(0 <= x < params.modulus for x in states)


def test_uniforms_match_states_divided_by_modulus():
    params = LcgParameters(n=50)
    states, uniforms = generate_pair(params)
    for x, u in zip(states, uniforms):
        assert u == x / params.modulus


def test_invalid_parameters_rejected():
    with pytest.raises(ParameterValidationError):
        LcgParameters(n=0).validate()
    with pytest.raises(ParameterValidationError):
        LcgParameters(seed=4294967296).validate()  # semilla >= módulo
    with pytest.raises(ParameterValidationError):
        LcgParameters(modulus=1).validate()
    with pytest.raises(ParameterValidationError):
        LcgParameters(multiplier=-1).validate()


def test_next_state_rejects_non_integer():
    lcg = Lcg(LcgParameters(n=1))
    with pytest.raises(LcgError):
        lcg.next_state(0.5)
    with pytest.raises(LcgError):
        lcg.next_state(True)  # bool no se admite como estado


def test_sequence_hash_stability():
    params = LcgParameters(seed=1, multiplier=5, increment=1, modulus=8, n=8)
    states_a = Lcg(params).generate_states()
    params2 = LcgParameters(seed=1, multiplier=5, increment=1, modulus=8, n=8)
    states_b = Lcg(params2).generate_states()
    assert Lcg.sequence_hash(states_a) == Lcg.sequence_hash(states_b)
    params3 = LcgParameters(seed=2, multiplier=5, increment=1, modulus=8, n=8)
    assert Lcg.sequence_hash(states_a) != Lcg.sequence_hash(Lcg(params3).generate_states())
