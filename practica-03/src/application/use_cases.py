"""Casos de uso; no conocen HTTP ni elementos visuales."""
from dataclasses import asdict
from domain.models import Config
from domain.queueing import theoretical
from infrastructure.simpy_engine import MM1Engine

SCENARIOS = [
    {'name': 'Estable', 'arrival_rate': 2.0, 'service_rate': 3.0},
    {'name': 'Mayor utilización', 'arrival_rate': 2.5, 'service_rate': 3.0},
    {'name': 'Cerca de saturación', 'arrival_rate': 2.9, 'service_rate': 3.0},
]


def simulate(config: Config) -> dict:
    simulation = MM1Engine().run(config)
    return {'config': asdict(config), 'theory': theoretical(config).to_dict(), **simulation}


def compare(duration: float = 3000, seed: int = 42) -> list:
    rows = []
    for scenario in SCENARIOS:
        cfg = Config(scenario['arrival_rate'], scenario['service_rate'], duration, seed)
        result = simulate(cfg)
        rows.append({'scenario': scenario['name'], **scenario,
                     'theory': result['theory'], 'simulated': result['summary']})
    return rows
