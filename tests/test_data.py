import os
import unittest

from vnd.data import Dataset, load_dataset

DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "datasets", "20_20_15.txt"
)


class TestLoadDataset(unittest.TestCase):
    def test_parses_matrices_and_dimensions(self):
        ds = load_dataset(DATASET_PATH, n=20, m=20)

        self.assertIsInstance(ds, Dataset)
        self.assertEqual(ds.n, 20)
        self.assertEqual(ds.m, 20)
        self.assertEqual(len(ds.c), 20)
        self.assertEqual(len(ds.c[0]), 20)
        self.assertEqual(len(ds.d), 20)
        self.assertEqual(len(ds.d[0]), 20)
        self.assertIsInstance(ds.c[0][0], float)

    def test_median_parsed_from_filename(self):
        ds = load_dataset(DATASET_PATH, n=20, m=20)

        self.assertEqual(ds.median, 15)

    def test_explicit_median_overrides_filename(self):
        ds = load_dataset(DATASET_PATH, n=20, m=20, median=99)

        self.assertEqual(ds.median, 99)
