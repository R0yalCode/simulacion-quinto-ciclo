"""Generador congruencial lineal (LCG) compartido por Python y Java.

Garantiza exactamente la misma secuencia de números pseudoaleatorios en
ambos lenguajes usando la misma semilla, el mismo multiplicador y el
mismo módulo.

Fórmula:
    X(n+1) = (48271 * X(n)) mod 2147483647
    U(n)   = X(n) / 2147483647
"""


class LCG:
    """Generador congruencial lineal (algoritmo Lehmer / MINSTD)."""

    SEMILLA = 123456789
    MULTIPLICADOR = 48271
    MODULO = 2147483647

    def __init__(self, semilla=SEMILLA):
        self.estado = semilla

    def siguiente(self):
        """Avanza el estado y devuelve el siguiente número U en [0, 1)."""
        self.estado = (self.MULTIPLICADOR * self.estado) % self.MODULO
        return self.estado / self.MODULO

    def reiniciar(self, semilla=SEMILLA):
        """Restablece el estado del generador a la semilla indicada."""
        self.estado = semilla
