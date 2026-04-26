import unittest

from data.processor import process_numbers, compute_factorials, multiply_pairs


class TestProcessor(unittest.TestCase):
    def test_process_numbers(self):
        self.assertEqual(process_numbers([1, 2, 3]), 6)

    def test_process_single_number(self):
        self.assertEqual(process_numbers([42]), 42)

    def test_compute_factorials(self):
        self.assertEqual(compute_factorials([1, 2, 3, 4, 5]), [1, 2, 6, 24, 120])

    def test_multiply_pairs(self):
        self.assertEqual(multiply_pairs([(2, 3), (4, 5)]), [6, 20])


if __name__ == "__main__":
    unittest.main()
