import unittest
from metrics import ranks, rho, compare, scores, invalid_inputs, equal_rank_mix


class MetricsTests(unittest.TestCase):
    def test_ties_and_flat(self):
        self.assertEqual(ranks([1,2,2]),[1,2.5,2.5])
        self.assertIsNone(rho([1,1],[1,1]))
    def test_missing_never_zero(self):
        self.assertIsNone(compare({"a":1},{"a":1,"b":2},["a","b"])["distance"])
    def test_reversed_and_identical(self):
        self.assertEqual(rho([1,2,3],[3,2,1]),-1)
        self.assertEqual(rho([1,2,3],[1,2,3]),1)
    def test_rank_mix_not_score_mean(self):
        a={"a":.1,"b":.9,"c":1};b={"a":100,"b":50,"c":0}
        self.assertEqual(equal_rank_mix(a,b,list(a)),{"a":2,"b":2,"c":2})
    def test_returned_unscored(self):
        self.assertEqual(scores({"results":{"entities":[{"entity_id":"a"}]}}),{})
    def test_tag_scores_and_input_warning(self):
        self.assertEqual(scores({"results":{"tags":[{"id":"urn:tag:test","query":{"affinity":1}}]}}),{"urn:tag:test":1})
        self.assertEqual(invalid_inputs({"warnings":[{"type":"not_found","signal.interests.entities":["book"]}]}),["book"])


if __name__=="__main__":
    unittest.main()
