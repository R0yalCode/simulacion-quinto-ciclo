"""Modelo: lógica del método Monte Carlo para aproximar el valor de π."""

import math
import time

from modelo.lcg import LCG


class ResultadoExperimento:
    """Representa el resultado de un experimento Monte Carlo."""

    def __init__(self, n, puntos_circulo, pi_estimado, error, tiempo_ms):
        self.n = n
        self.puntos_circulo = puntos_circulo
        self.pi_estimado = pi_estimado
        self.error = error
        self.tiempo_ms = tiempo_ms

    def a_diccionario(self):
        """Devuelve los datos del resultado como un diccionario."""
        return {
            "n": self.n,
            "puntos_circulo": self.puntos_circulo,
            "pi_estimado": self.pi_estimado,
            "error": self.error,
            "tiempo_ms": self.tiempo_ms,
        }


class ExperimentoMonteCarlo:
    """Ejecuta el experimento Monte Carlo con los tamaños de muestra fijados."""

    TAMANOS = [1_000, 10_000, 100_000, 1_000_000]
    SEMILLA = LCG.SEMILLA

    def ejecutar(self, n):
        """Ejecuta el experimento con n puntos y devuelve un ResultadoExperimento.

        El tiempo medido corresponde únicamente al experimento (generación
        de puntos y conteo), no a la lectura ni escritura de archivos.
        """
        lcg = LCG(self.SEMILLA)
        puntos_en_circulo = 0

        inicio = time.perf_counter()
        for _ in range(n):
            x = lcg.siguiente()
            y = lcg.siguiente()
            if x * x + y * y <= 1.0:
                puntos_en_circulo += 1
        fin = time.perf_counter()

        pi_estimado = 4.0 * puntos_en_circulo / n
        error = abs(math.pi - pi_estimado)
        tiempo_ms = (fin - inicio) * 1000.0
        return ResultadoExperimento(n, puntos_en_circulo, pi_estimado, error, tiempo_ms)

    def ejecutar_todos(self):
        """Ejecuta los cuatro experimentos obligatorios y devuelve la lista."""
        return [self.ejecutar(n) for n in self.TAMANOS]
