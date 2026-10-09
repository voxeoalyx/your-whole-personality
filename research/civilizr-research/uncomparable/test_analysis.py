"""Only checks research-critical missingness and tie semantics; fully offline."""
import unittest
from analyze import compare, ranks, spearman


class ResearchMathTests(unittest.TestCase):
    def test_tied_rank_average(self):
        self.assertEqual(ranks([1, 2, 2, 4]), [1, 2.5, 2.5, 4])

    def test_flat_is_not_perfect_similarity(self):
        self.assertIsNone(spearman([1, 1, 1], [1, 1, 1]))

    def test_missing_is_not_zero_or_pairwise_complete(self):
        result = compare({"a": 1, "b": 2}, {"a": 1}, ["a", "b"])
        self.assertFalse(result["complete"])
        self.assertIsNone(result["spearman"])

    def test_reversal_and_subset(self):
        self.assertEqual(spearman([1, 2, 3], [3, 2, 1]), -1)
        self.assertEqual(compare({"a": 1, "b": 2, "c": 3}, {"a": 1, "c": 3}, ["a", "c"])["spearman"], 1)


if __name__ == "__main__":
    unittest.main()
