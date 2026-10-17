import unittest

from vnd.follower import follower


class TestFollower(unittest.TestCase):
    def test_each_client_assigned_to_exactly_one_open_facility(self):
        y = [1, 0, 1]
        d = [[1, 2, 3],
             [4, 5, 6],
             [7, 8, 9]]

        x = follower(y, d)

        client_0 = x[0][0] + x[1][0] + x[2][0]
        client_1 = x[0][1] + x[1][1] + x[2][1]
        client_2 = x[0][2] + x[1][2] + x[2][2]
        self.assertEqual(client_0, 1)
        self.assertEqual(client_1, 1)
        self.assertEqual(client_2, 1)

    def test_client_goes_to_cheapest_open_facility(self):
        y = [1, 0, 1]
        d = [[10, 20, 30],
             [ 1,  1,  1],
             [ 5, 15, 25]]

        x = follower(y, d)

        self.assertEqual(x[2][0], 1)
        self.assertEqual(x[0][0], 0)
        self.assertEqual(x[2][1], 1)
        self.assertEqual(x[2][2], 1)

    def test_only_open_facility_receives_clients(self):
        y = [0, 1, 0]
        d = [[10, 10],
             [ 1,  1],
             [ 5,  5]]

        x = follower(y, d)

        self.assertEqual(x[1][0], 1)
        self.assertEqual(x[1][1], 1)
        self.assertEqual(x[0][0], 0)
        self.assertEqual(x[2][1], 0)
