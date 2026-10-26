from dataclasses import dataclass
from enum import Enum


class HealthState(str, Enum):
    SUSCEPTIBLE = "S"
    INFECTED = "I"
    RECOVERED = "R"


# =========================
# CONFIGURACIÓN CENTRALIZADA
# =========================
# Modifica estos valores para experimentar. También puedes usar argumentos CLI.
DEFAULT_POPULATION = 100
DEFAULT_INITIAL_INFECTED = 5
DEFAULT_BETA = 0.30
DEFAULT_GAMMA = 0.10
DEFAULT_STEPS = 100
DEFAULT_SEED = 42


@dataclass(frozen=True)
class SirConfig:
    population: int = DEFAULT_POPULATION
    initially_infected: int = DEFAULT_INITIAL_INFECTED
    beta: float = DEFAULT_BETA
    gamma: float = DEFAULT_GAMMA
    steps: int = DEFAULT_STEPS
    seed: int = DEFAULT_SEED

    def __post_init__(self):
        if self.population < 1:
            raise ValueError("La población debe ser mayor a 0")
        if self.initially_infected < 0 or self.initially_infected > self.population:
            raise ValueError("Infectados iniciales inválidos")
        if not 0 <= self.beta <= 1 or not 0 <= self.gamma <= 1:
            raise ValueError("Las probabilidades beta/gamma deben estar en [0,1]")
        if self.steps < 0:
            raise ValueError("El número de pasos debe ser >= 0")


@dataclass(frozen=True)
class Snapshot:
    tiempo: int
    susceptibles: int
    infectados: int
    recuperados: int

    @property
    def total(self):
        return self.susceptibles + self.infectados + self.recuperados
