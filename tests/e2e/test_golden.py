"""
Эталонные e2e-тесты: фиксированный старт -> заранее известный ответ.
Ответы получены один раз и записаны константами, см. docs/testing.md.
Решение задаётся множеством номеров открытых предприятий.
"""
import os
import unittest

from vnd.core import solve
from vnd.data import load_dataset
from vnd.trace import Tracer

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "datasets", "20_20_15.txt"
)
V = 47000

# (p, старт, ожидаемый ответ, значение V - f, принято шагов 1-swap, принято шагов 2-swap)
GOLDEN = [
    (5, [1, 8, 12, 13, 15], [3, 8, 12, 15, 17], 37384.00732232507, 9, 2),
    (5, [1, 2, 5, 11, 18], [3, 8, 12, 15, 17], 37384.00732232507, 11, 3),
    (10, [1, 4, 5, 6, 7, 8, 12, 13, 15, 19], [1, 3, 4, 6, 8, 11, 13, 14, 15, 18], 37057.45272328355, 7, 1),
    # 2-swap ни разу не улучшил: неглобальный локальный оптимум, это корректный ответ VND
    (5, [0, 8, 11, 16, 19], [2, 5, 13, 18, 19], 37043.69944254178, 10, 0),
    (5, [2, 3, 4, 8, 18], [3, 8, 12, 15, 17], 37384.00732232507, 5, 1),
    (10, [1, 2, 4, 5, 8, 9, 10, 12, 13, 16], [1, 2, 3, 6, 13, 15, 16, 17, 18, 19], 37024.691269907664, 12, 2),
]


def _to_y(open_idx, n):
    return [1 if i in open_idx else 0 for i in range(n)]


class TestGolden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ds = load_dataset(DATASET_PATH, n=20, m=20)
        cls.c, cls.d, cls.n = ds.c, ds.d, ds.n
        cls.runs = {}
        for case in GOLDEN:
            p, start = case[0], case[1]
            tracer = Tracer()
            y, value, _ = solve(_to_y(start, cls.n), cls.c, cls.d, V, cls.n, p, verbose=False, tracer=tracer)
            cls.runs[tuple(start)] = (y, value, tracer)

    def test_value(self):
        for p, start, _, expected_value, _, _ in GOLDEN:
            with self.subTest(p=p, start=start):
                _, value, _ = self.runs[tuple(start)]
                self.assertAlmostEqual(value, expected_value, places=6)

    def test_moves(self):
        """Алгоритм прошёл тот же путь: столько же принятых шагов каждого типа."""
        for p, start, _, _, swap1, swap2 in GOLDEN:
            with self.subTest(p=p, start=start):
                _, _, tracer = self.runs[tuple(start)]
                accepted = [e.move for e in tracer.events if e.kind == "accept"]
                self.assertEqual(accepted.count("swap1"), swap1)
                self.assertEqual(accepted.count("swap2"), swap2)

    def test_placement(self):
        for p, start, expected, _, _, _ in GOLDEN:
            with self.subTest(p=p, start=start):
                y, _, _ = self.runs[tuple(start)]
                self.assertEqual(y, _to_y(expected, self.n))


if __name__ == "__main__":
    unittest.main()
