import unittest
from unittest.mock import patch

from vnd.parallel import solve_multistart


def _c():
    return [[10, 20, 30, 40],
            [40, 10, 20, 30],
            [30, 40, 10, 20],
            [20, 30, 40, 10]]


def _d():
    return [[1, 2, 3, 4],
            [4, 1, 2, 3],
            [3, 4, 1, 2],
            [2, 3, 4, 1]]


def _fake_solve(objectives):
    """
    Подмена solve: возвращает заданные значения целевой функции по порядку вызовов.
    """
    it = iter(objectives)

    def fake(y_start, c, d, V, n, p, mode="full", verbose=True, tracer=None):
        return y_start, next(it), 0.1

    return fake


class TestSolveMultistart(unittest.TestCase):
    def test_seed_fixes_starts(self):
        expected_start_0 = [1, 0, 0, 1]
        expected_start_1 = [1, 1, 0, 0]
        expected_start_2 = [0, 1, 1, 0]

        result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=1, seed=2)

        self.assertEqual(result.runs[0].y_start, expected_start_0)
        self.assertEqual(result.runs[1].y_start, expected_start_1)
        self.assertEqual(result.runs[2].y_start, expected_start_2)

    def test_parallel_runs_match_serial_values(self):
        expected_workers = 2
        expected_y_0 = [0, 1, 0, 1]
        expected_y_1 = [0, 1, 0, 1]
        expected_y_2 = [1, 0, 1, 0]
        expected_objective = 940

        result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=2, seed=2)

        self.assertEqual(result.workers, expected_workers)
        self.assertEqual(result.runs[0].y, expected_y_0)
        self.assertEqual(result.runs[1].y, expected_y_1)
        self.assertEqual(result.runs[2].y, expected_y_2)
        self.assertEqual(result.runs[0].objective, expected_objective)
        self.assertEqual(result.runs[1].objective, expected_objective)
        self.assertEqual(result.runs[2].objective, expected_objective)

    def test_runs_ordered_by_start_index(self):
        expected_indices = [0, 1, 2]

        result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=2, seed=2)

        self.assertEqual([result.runs[0].index, result.runs[1].index, result.runs[2].index], expected_indices)

    def test_best_is_run_with_max_objective(self):
        expected_index = 1
        expected_objective = 30

        with patch("vnd.parallel.solve", _fake_solve([10, 30, 20])):
            result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=1, seed=2)

        self.assertEqual(result.best.index, expected_index)
        self.assertEqual(result.best.objective, expected_objective)

    def test_best_tie_goes_to_lower_index(self):
        expected_index = 0

        with patch("vnd.parallel.solve", _fake_solve([30, 10, 30])):
            result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=1, seed=2)

        self.assertEqual(result.best.index, expected_index)

    def test_summary(self):
        expected = {"starts": 3, "best": 30, "worst": 10, "mean": 20.0, "stdev": 10.0}

        with patch("vnd.parallel.solve", _fake_solve([10, 30, 20])):
            result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=3, workers=1, seed=2)
        summary = result.summary()

        self.assertEqual(summary, expected)

    def test_summary_single_start_has_zero_stdev(self):
        expected_stdev = 0.0

        with patch("vnd.parallel.solve", _fake_solve([10])):
            result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=1, workers=1, seed=2)
        summary = result.summary()

        self.assertEqual(summary["stdev"], expected_stdev)

    def test_workers_capped_by_starts(self):
        expected_workers = 2

        result = solve_multistart(_c(), _d(), 1000, 4, 2, starts=2, workers=16, seed=2)

        self.assertEqual(result.workers, expected_workers)

    def test_zero_starts_rejected(self):
        expected_error = ValueError

        with self.assertRaises(expected_error):
            solve_multistart(_c(), _d(), 1000, 4, 2, starts=0)


if __name__ == "__main__":
    unittest.main()
