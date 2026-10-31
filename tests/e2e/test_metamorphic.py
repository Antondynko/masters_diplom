"""
Метаморфные e2e-тесты: вход (c, d, V) преобразуется так, что ожидаемое изменение
результата известно заранее, без знания оптимума. При заданном y_start алгоритм
детерминирован, поэтому сравнивается весь ход поиска (все вычисленные соседи по
порядку), итоговый y и значение целевой функции.
"""
import os
import random
import unittest

from vnd.core import solve
from vnd.data import load_dataset
from vnd.neighborhoods import generate_y_start
from vnd.trace import Tracer

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets", "20_20_15.txt"
)
V = 47000
P = 5
SEEDS = (0, 1, 2, 3)


def _run(c, d, V, y_start):
    """
    :return: (y, значение, ход поиска) - ход поиска это последовательность (kind, move, child)
    """
    tracer = Tracer()
    y, value, _ = solve(y_start, c, d, V, len(c), P, verbose=False, tracer=tracer)
    path = [(e.kind, e.move, e.child) for e in tracer.events]
    return y, value, path


def _permute_columns(matrix, perm):
    return [[row[j] for j in perm] for row in matrix]


class TestMetamorphic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ds = load_dataset(DATASET_PATH, n=20, m=20)
        cls.c, cls.d, cls.n, cls.m = ds.c, ds.d, ds.n, ds.m
        cls.starts = [generate_y_start(cls.n, P, random.Random(s)) for s in SEEDS]
        cls.base = [_run(cls.c, cls.d, V, y0) for y0 in cls.starts]

    def test_starts_cover_swap2(self):
        """Хотя бы на одном старте 2-swap даёт улучшение - иначе Improve не проверяется."""
        accepted_swap2 = any(
            kind == "accept" and move == "swap2"
            for _, _, path in self.base
            for kind, move, _ in path
        )
        self.assertTrue(accepted_swap2)

    def _assert_same_run(self, base, other, expected_value, places=6):
        y, _, path = base
        y_other, value_other, path_other = other
        self.assertEqual(y_other, y)
        self.assertEqual(path_other, path)
        self.assertAlmostEqual(value_other, expected_value, places=places)

    def test_m1_shift_V(self):
        """M1: V -> V + k. Тот же ход поиска, значение больше на k."""
        for k in (1000, -5000, 123456):
            for y0, base in zip(self.starts, self.base):
                with self.subTest(k=k, y_start=y0):
                    other = _run(self.c, self.d, V + k, y0)
                    self._assert_same_run(base, other, base[1] + k)

    def test_m2_scale_c_and_V(self):
        """M2: c -> a*c, V -> a*V, a > 0. Тот же ход поиска, значение умножается на a."""
        # Степени двойки - умножение на них в float точное, округление не мешает
        for a in (2, 4, 0.5):
            c_scaled = [[a * x for x in row] for row in self.c]
            for y0, base in zip(self.starts, self.base):
                with self.subTest(a=a, y_start=y0):
                    other = _run(c_scaled, self.d, a * V, y0)
                    self._assert_same_run(base, other, a * base[1])

    def test_m3_shift_c_per_client(self):
        """M3: c[i][j] -> c[i][j] + b_j. Каждый клиент назначен ровно один раз,
        поэтому f сдвигается на sum(b_j) при любом y: тот же ход поиска, значение меньше на sum(b_j)."""
        rng = random.Random(42)
        b = [rng.uniform(0, 1000) for _ in range(self.m)]
        c_shifted = [[x + b[j] for j, x in enumerate(row)] for row in self.c]
        for y0, base in zip(self.starts, self.base):
            with self.subTest(y_start=y0):
                other = _run(c_shifted, self.d, V, y0)
                self._assert_same_run(base, other, base[1] - sum(b), places=4)

    def test_m4_monotone_transform_d(self):
        """M4: d[i][j] -> g_j(d[i][j]), g_j строго возрастает. Порядок предпочтений
        каждого клиента сохраняется, follower назначает так же: ход поиска и значение те же."""
        rng = random.Random(7)
        coef = [(rng.uniform(0.5, 10), rng.uniform(-50, 50)) for _ in range(self.m)]
        transforms = {
            "affine": lambda x, j: coef[j][0] * x + coef[j][1],
            "cube": lambda x, j: x ** 3,
            "mixed": lambda x, j: x ** 3 if j % 2 else coef[j][0] * x + coef[j][1],
        }
        for name, g in transforms.items():
            d_transformed = [[g(x, j) for j, x in enumerate(row)] for row in self.d]
            for y0, base in zip(self.starts, self.base):
                with self.subTest(transform=name, y_start=y0):
                    other = _run(self.c, d_transformed, V, y0)
                    self._assert_same_run(base, other, base[1])

    def test_m5_permute_clients(self):
        """M5: перестановка клиентов (столбцов c и d одновременно). Клиенты независимы,
        f - сумма по ним: ход поиска тот же, значение то же с точностью до порядка суммирования."""
        perm = list(range(self.m))
        random.Random(13).shuffle(perm)
        c_perm = _permute_columns(self.c, perm)
        d_perm = _permute_columns(self.d, perm)
        for y0, base in zip(self.starts, self.base):
            with self.subTest(y_start=y0):
                other = _run(c_perm, d_perm, V, y0)
                self._assert_same_run(base, other, base[1], places=6)


if __name__ == "__main__":
    unittest.main()
