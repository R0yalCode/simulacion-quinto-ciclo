"""
Generador congruencial lineal (LCG).

Capa de dominio. Implementa manualmente la recurrencia

    X(n+1) = (a · X(n) + c) mod m
    U(n+1) = X(n+1) / m

Sin recurrir a generadores aleatorios nativos (random, numpy). Los enteros
de Python tienen precisión arbitraria, por lo que la operación
(a · X + c) no puede desbordarse; el módulo garantiza X ∈ [0, m) y la
normalización U ∈ [0, 1).
"""

from __future__ import annotations

import hashlib
from numbers import Integral, Real
from typing import Iterable, List, Sequence, Tuple

from config.generator_config import LcgParameters


class LcgError(ValueError):
    """Error de ejecución del generador LCG."""


class Lcg:
    """Generador congruencial lineal determinista a partir de una semilla."""

    def __init__(self, params: LcgParameters) -> None:
        params.validate()
        self.params = params

    # ------------------------------------------------------------------ #
    # Núcleo de la recurrencia
    # ------------------------------------------------------------------ #
    def next_state(self, state: int) -> int:
        """Aplica un paso de la recurrencia X <- (a·X + c) mod m."""
        if isinstance(state, bool) or not isinstance(state, Integral):
            raise LcgError("El estado del generador debe ser un entero.")
        return (self.params.multiplier * state + self.params.increment) % self.params.modulus

    def generate_states(self) -> List[int]:
        """
        Genera la secuencia de estados enteros X(1) ... X(n) a partir de la semilla X(0).

        Devuelve n estados HX posteriores a la semilla; la semilla misma no
        forma parte de la secuencia de salida (definición estándar del LCG).
        """
        p = self.params
        states: List[int] = []
        state = p.seed
        multiplier = p.multiplier
        increment = p.increment
        modulus = p.modulus
        append = states.append
        for _ in range(p.n):
            state = (multiplier * state + increment) % modulus
            append(state)
        return states

    def generate_uniforms(self) -> List[float]:
        """Genera la secuencia normalizada U(i) = X(i) / m ∈ [0, 1)."""
        modulus = self.params.modulus
        return [state / modulus for state in self.generate_states()]

    @staticmethod
    def uniform(states: Iterable[int], modulus: int) -> List[float]:
        """Normaliza una secuencia de estados previamente generada."""
        if modulus <= 0:
            raise LcgError("El módulo debe ser positivo para normalizar.")
        return [state / modulus for state in states]

    # ------------------------------------------------------------------ #
    # Verificaciones de calidad de la secuencia
    # ------------------------------------------------------------------ #
    @staticmethod
    def check_unit_interval(uniforms: Sequence[Real]) -> None:
        """Verifica que todos los valores normalizados pertenezcan a [0, 1)."""
        for value in uniforms:
            if value < 0.0 or value >= 1.0:
                raise LcgError("Valor normalizado fuera del intervalo [0, 1).")

    @classmethod
    def sequence_hash(cls, states: Sequence[int]) -> str:
        """
        Huella SHA-256 de la secuencia de estados enteros.

        Se usa para comparar con exactitud las secuencias producidas por la
        implementación en Java: ambas escriben los mismos enteros decimales
        separados por comas y calculan el mismo resumen.
        """
        digest = hashlib.sha256()
        digest.update(",".join(str(int(state)) for state in states).encode("ascii"))
        return digest.hexdigest()

    def describe(self) -> str:
        p = self.params
        return (
            f"X(n+1) = ({p.multiplier} · X(n) + {p.increment}) mod {p.modulus}, "
            f"X0 = {p.seed}, N = {p.n}"
        )


def build_lcg(params: LcgParameters) -> Lcg:
    """Constructor de conveniencia para el generador."""
    return Lcg(params)


def generate_pair(params: LcgParameters) -> Tuple[List[int], List[float]]:
    """Genera a la vez los estados enteros X(i) y los valores normalizados U(i)."""
    lcg = Lcg(params)
    states = lcg.generate_states()
    uniforms = Lcg.uniform(states, params.modulus)
    return states, uniforms
