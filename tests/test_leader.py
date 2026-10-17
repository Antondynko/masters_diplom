import unittest

from vnd.leader import leader, leader_simplified


class TestLeaderFull(unittest.TestCase):
    def test_objective_is_v_minus_f(self):
        x = [[1, 0],
             [0, 1]]
        c = [[100, 200],
             [300, 400]]

        _, val = leader(x, c, 1000)

        self.assertEqual(val, 500)

    def test_rho_normalized_by_assignment_count(self):
        x = [[1, 0],
             [0, 1]]
        c = [[100, 200],
             [300, 400]]

        rho, _ = leader(x, c, 1000)

        expected_delta = 500 / 2
        self.assertAlmostEqual(rho[0][0], expected_delta)
        self.assertAlmostEqual(rho[1][1], expected_delta)
        self.assertEqual(rho[0][1], 0)
        self.assertEqual(rho[1][0], 0)

    def test_single_assignment_full_value_in_one_cell(self):
        x = [[1, 0],
             [0, 0]]
        c = [[50, 200],
             [300, 400]]

        rho, val = leader(x, c, 1000)

        self.assertEqual(val, 950)
        self.assertAlmostEqual(rho[0][0], 950)
        self.assertEqual(rho[1][1], 0)


class TestLeaderSimplified(unittest.TestCase):
    def test_objective_is_v_minus_f(self):
        x = [[1, 0],
             [0, 1]]
        c = [[100, 200],
             [300, 400]]

        _, val = leader_simplified(x, c, 1000)

        self.assertEqual(val, 500)

    def test_single_nonzero_cell_at_min_cost_assignment(self):
        x = [[1, 0],
             [0, 1]]
        c = [[100, 200],
             [300, 400]]

        rho, _ = leader_simplified(x, c, 1000)

        self.assertEqual(rho[0][0], 500)
        self.assertEqual(rho[0][1], 0)
        self.assertEqual(rho[1][0], 0)
        self.assertEqual(rho[1][1], 0)

    def test_empty_assignment_gives_zero_rho(self):
        x = [[0, 0],
             [0, 0]]
        c = [[100, 200],
             [300, 400]]

        rho, val = leader_simplified(x, c, 1000)

        self.assertEqual(rho, [[0, 0], [0, 0]])
        self.assertEqual(val, 1000)
