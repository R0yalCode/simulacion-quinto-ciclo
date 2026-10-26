import random
import simpy
from sir.domain.model import HealthState, Snapshot, SirConfig
from sir.domain.rules import infection_probability

class SirSimulator:
    def __init__(self, config: SirConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.states = ([HealthState.INFECTED] * config.initially_infected
                       + [HealthState.SUSCEPTIBLE] * (config.population - config.initially_infected))
        self.rng.shuffle(self.states)
        self.history: list[Snapshot] = []

    def _record(self, time: int) -> None:
        s = self.states.count(HealthState.SUSCEPTIBLE)
        i = self.states.count(HealthState.INFECTED)
        r = self.states.count(HealthState.RECOVERED)
        self.history.append(Snapshot(time, s, i, r))

    def _step(self) -> None:
        old = list(self.states)
        count_i = old.count(HealthState.INFECTED)
        p_infect = infection_probability(self.config.beta, count_i, self.config.population)
        next_states = list(old)
        for idx, state in enumerate(old):
            if state is HealthState.SUSCEPTIBLE and self.rng.random() < p_infect:
                next_states[idx] = HealthState.INFECTED
            elif state is HealthState.INFECTED and self.rng.random() < self.config.gamma:
                next_states[idx] = HealthState.RECOVERED
        self.states = next_states

    def _process(self, env: simpy.Environment):
        self._record(0)
        for time in range(1, self.config.steps + 1):
            yield env.timeout(1)
            self._step()
            self._record(time)

    def run(self) -> list[Snapshot]:
        env = simpy.Environment()
        env.process(self._process(env))
        env.run()
        return self.history
