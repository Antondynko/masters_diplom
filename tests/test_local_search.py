import unittest

from vnd.local_search import N, Local_Search


class TestN(unittest.TestCase):
    def test_no_improvement_returns_same_y(self):
        y = [1, 0]
        d = [[1, 1],
             [1, 1]]
        c = [[10, 10],
             [10, 10]]

        result = N(y, d, c, 1000)

        self.assertEqual(result, y)

    def test_finds_improvement_when_exists(self):
        y = [1, 0]
        d = [[1, 1],
             [1, 1]]
        c = [[100, 100],
             [1, 1]]

        result = N(y, d, c, 1000)

        self.assertEqual(result, [0, 1])


class TestLocalSearch(unittest.TestCase):
    def test_stops_at_local_optimum(self):
        y = [1, 0, 0]
        d = [[1, 1, 1],
             [1, 1, 1],
             [1, 1, 1]]
        c = [[100, 100, 100],
             [1, 1, 1],
             [1, 1, 1]]

        result = Local_Search(y, d, c, 1000, verbose=False)

        self.assertEqual(sum(result), 1)
        self.assertIn(result, ([1, 0, 0], [0, 1, 0], [0, 0, 1]))
