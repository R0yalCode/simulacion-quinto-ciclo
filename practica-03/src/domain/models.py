"""Entidades y contratos independientes de SimPy y de la interfaz."""
from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Config:
    arrival_rate: float = 2.0
    service_rate: float = 3.0
    duration: float = 120.0
    seed: int = 42

    def validate(self):
        if not 0 < self.arrival_rate <= 100 or not 0 < self.service_rate <= 100:
            raise ValueError('Las tasas λ y μ deben estar en (0, 100].')
        if not 1 <= self.duration <= 10000:
            raise ValueError('La duración debe estar entre 1 y 10000.')
        if not 0 <= self.seed <= 2**32 - 1:
            raise ValueError('La semilla debe ser un entero sin signo de 32 bits.')


@dataclass(frozen=True)
class Theory:
    rho: float
    L: float | None
    Lq: float | None
    W: float | None
    Wq: float | None
    stable: bool

    def to_dict(self):
        return asdict(self)
