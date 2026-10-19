import unittest
from domain.models import Config
try:
    from application.use_cases import simulate
    SIMPY_AVAILABLE = True
except ModuleNotFoundError as exc:
    if exc.name != "simpy":
        raise
    SIMPY_AVAILABLE = False

@unittest.skipUnless(SIMPY_AVAILABLE, "SimPy no está instalado")


class SimulationTests(unittest.TestCase):
    def test_reproducible_and_conserves_packages(self):
        config = Config(2, 3, 200, 42)
        one = simulate(config)
        two = simulate(config)
        self.assertEqual(one['events'], two['events'])
        summary = one['summary']
        self.assertEqual(summary['arrived'], summary['completed'] + summary['pending'])
        self.assertEqual(one['events'][-1]['type'], 'end')
        self.assertTrue(0 <= summary['utilization'] <= 1)
        self.assertTrue(all(e['queue'] >= 0 for e in one['events']))

    def test_fifo(self):
        jobs = simulate(Config(2.9, 3, 200, 9))['jobs']
        self.assertEqual([j['id'] for j in jobs], sorted(j['id'] for j in jobs))


if __name__ == '__main__':
    unittest.main()
