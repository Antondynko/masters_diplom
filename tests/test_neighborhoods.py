import unittest

from vnd.neighborhoods import Generate_y_start, Pairs, Swap, Swap_2


class TestGenerateYStart(unittest.TestCase):
    def test_count_ones(self):
        y = Generate_y_start(10, 3)

        self.assertEqual(sum(y), 3)

    def test_p_zero(self):
        y = Generate_y_start(2, 0)

        self.assertEqual(y, [0, 0])

    def test_p_equals_n(self):
        y = Generate_y_start(2, 2)

        self.assertEqual(y, [1, 1])


class TestSwap(unittest.TestCase):
    def test_neighbor_count_is_p_times_n_minus_p(self):
        y = [1, 1, 0, 0]

        neighbors = Swap(y)

        self.assertEqual(len(neighbors), 4)

    def test_concrete_neighbor(self):
        y = [1, 0]

        neighbors = Swap(y)

        self.assertEqual(neighbors, [[0, 1]])

    def test_no_ones_gives_empty(self):
        y = [0, 0, 0]

        neighbors = Swap(y)

        self.assertEqual(neighbors, [])

    def test_no_zeros_gives_empty(self):
        y = [1, 1, 1]

        neighbors = Swap(y)

        self.assertEqual(neighbors, [])


class TestPairs(unittest.TestCase):
    def test_all_pairs_in_order(self):
        result = Pairs([1, 2, 3])

        self.assertEqual(result, [(1, 2), (1, 3), (2, 3)])


class TestSwap2(unittest.TestCase):
    def test_single_pair_gives_one_neighbor(self):
        y = [1, 1, 0, 0]

        neighbors = Swap_2(y)

        self.assertEqual(len(neighbors), 1)

    def test_concrete_neighbor(self):
        y = [1, 1, 0, 0]

        neighbors = Swap_2(y)

        self.assertEqual(neighbors, [[0, 0, 1, 1]])

    def test_two_pairs_gives_nine_neighbors(self):
        y = [1, 1, 1, 0, 0, 0]

        neighbors = Swap_2(y)

        self.assertEqual(len(neighbors), 9)
