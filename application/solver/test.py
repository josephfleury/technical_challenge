import unittest

from solver import solver


def convert_and_call(color, customers, demand):
    return solver({"colors": color, "customers": customers, "demands": demand})


class PaintshopTest(unittest.TestCase):

    def test_impossible(self):
        demand = [[1, 1, 0], [1, 1, 1]]
        self.assertEqual(convert_and_call(1, 2, demand), "IMPOSSIBLE")

    def test_no_matte(self):
        demand = [[1, 1, 0], [1, 2, 0]]
        self.assertEqual(convert_and_call(2, 2, demand), "0 0")

    def test_all_matte(self):
        demand = [[1, 1, 1], [2, 1, 0, 2, 1], [3, 1, 0, 2, 0, 3, 1]]
        self.assertEqual(convert_and_call(3, 3, demand), "1 1 1")

    def test_color_not_requested(self):
        demand = [[1, 5, 1], [2, 1, 0, 2, 1]]
        self.assertEqual(convert_and_call(5, 2, demand), "0 0 0 0 1")


if __name__ == "__main__":
    unittest.main()
