import unittest

from vnd.core import solve


def _c():
    return [[10, 20, 30],
            [40,  5, 60],
            [70, 80,  3]]


def _d():
    return [[1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]]


class TestSolve(unittest.TestCase):
    def test_full_mode_returns_valid_placement(self):
        c = _c()
        d = _d()

        y, rho, elapsed = solve(None, c, d, 1000, 3, 2, mode="full", verbose=False)

        self.assertEqual(sum(y), 2)
        self.assertIsInstance(rho, (int, float))
        self.assertGreater(elapsed, 0)

    def test_simplified_mode_returns_valid_placement(self):
        c = _c()
        d = _d()

        y, rho, elapsed = solve(None, c, d, 1000, 3, 2, mode="simplified", verbose=False)

        self.assertEqual(sum(y), 2)
        self.assertIsInstance(rho, (int, float))
        self.assertGreater(elapsed, 0)

    def test_both_modes_produce_numeric_result(self):
        c = _c()
        d = _d()

        _, rho_full, _ = solve(None, c, d, 1000, 3, 2, mode="full", verbose=False)
        _, rho_simp, _ = solve(None, c, d, 1000, 3, 2, mode="simplified", verbose=False)

        self.assertIsInstance(rho_full, (int, float))
        self.assertIsInstance(rho_simp, (int, float))
