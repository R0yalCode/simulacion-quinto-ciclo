"""Teoría M/M/1, válida en régimen estacionario si λ < μ."""
from .models import Config, Theory


def theoretical(config: Config) -> Theory:
    config.validate()
    lam, mu = config.arrival_rate, config.service_rate
    rho = lam / mu
    if lam >= mu:
        return Theory(rho, None, None, None, None, False)
    return Theory(rho, lam / (mu - lam), lam * lam / (mu * (mu - lam)),
                  1 / (mu - lam), lam / (mu * (mu - lam)), True)
