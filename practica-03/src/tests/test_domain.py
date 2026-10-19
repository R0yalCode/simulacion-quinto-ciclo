import unittest
from domain.models import Config
from domain.queueing import theoretical


class TheoryTests(unittest.TestCase):
    def test_case_1(self):
        t = theoretical(Config(2, 3))
        self.assertAlmostEqual(t.rho, 2 / 3)
        self.assertAlmostEqual(t.L, 2)
        self.assertAlmostEqual(t.Lq, 4 / 3)
        self.assertAlmostEqual(t.W, 1)
        self.assertAlmostEqual(t.Wq, 2 / 3)

    def test_heavy_load(self):
        t = theoretical(Config(2.9, 3))
        self.assertAlmostEqual(t.L, 29)
        self.assertAlmostEqual(t.W, 10)

    def test_unstable(self):
        t = theoretical(Config(3, 3))
        self.assertFalse(t.stable)
        self.assertIsNone(t.W)

    def test_bad_config(self):
        with self.assertRaises(ValueError):
            theoretical(Config(-1, 3))


if __name__ == '__main__':
    unittest.main()
