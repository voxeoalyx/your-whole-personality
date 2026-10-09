"""Offline tests use synthetic data only; never write research findings."""
import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import qloo


class HarnessTests(unittest.TestCase):
    def test_censoring_and_similarity(self):
        self.assertEqual(qloo.similarities([], []), (None, None))
        self.assertEqual(qloo.similarities(["a", "b"], ["c", "d"]), (0, 0))
        j, c = qloo.similarities(["a", "b"], ["b", "a"])
        self.assertEqual(j, 1)
        self.assertAlmostEqual(c, .8)

    def test_zero_scores_survive_normalization(self):
        rows = qloo.normalized({"results": {"tags": [{"tag_id": "a", "query": {"affinity": 0}, "popularity": 0}]}})
        self.assertEqual(rows[0]["affinity"], 0)
        self.assertEqual(rows[0]["popularity"], 0)

    def test_dotenv_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text('\ufeffQLOO_API_KEY="synthetic#value" # comment\n', encoding="utf-8")
            with patch.dict(qloo.os.environ, {}, clear=True):
                self.assertEqual(qloo.load_env(p)["QLOO_API_KEY"], "synthetic#value")
            with patch.dict(qloo.os.environ, {"QLOO_API_KEY": "environment-value"}):
                self.assertEqual(qloo.load_env(p)["QLOO_API_KEY"], "environment-value")

    def test_host_and_url_safety(self):
        for bad in ("http://api.qloo.com", "https://api.qloo.com.evil.test", "https://api.qloo.com/v2", "https://secret@api.qloo.com"):
            with self.assertRaises(ValueError):
                qloo.base_url(bad)
        self.assertEqual(qloo.wire_params({"flag": False, "radius": 0, "ids": ["a", "b"]}),
                         {"flag": "false", "radius": "0", "ids": "a,b"})

    def test_budget_resume_auth_stop_and_secret_redaction(self):
        specs = [{"id": str(i), "kind": "lookup", "endpoint": "/search", "params": {"query": "synthetic"}} for i in range(2)]
        plan = {"requests": specs}
        env = {"QLOO_API_KEY": "synthetic-test-secret"}
        def fake(url, key, timeout):
            return 200, {}, json.dumps({"results": [], "echo": key}).encode()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(qloo.run(plan, d, env, budget=1, delay=0, request_fn=fake), 1)
            self.assertEqual(qloo.run(plan, d, env, budget=1, delay=0, request_fn=fake), 0)
            attempts = (Path(d) / "requests.jsonl").read_text()
            self.assertEqual(len(attempts.splitlines()), 2)
            for p in Path(d).iterdir():
                self.assertNotIn(env["QLOO_API_KEY"], p.read_text(encoding="utf-8-sig"))
            altered = {"requests": [dict(specs[0], params={"query": "changed"})]}
            with self.assertRaises(ValueError):
                qloo.run(altered, d, env, request_fn=fake)
        with tempfile.TemporaryDirectory() as d:
            def unauthorized(*args):
                return 401, {}, b'{"error":"unauthorized"}'
            qloo.run(plan, d, env, budget=5, retries=3, delay=0, request_fn=unauthorized)
            self.assertEqual(len((Path(d) / "requests.jsonl").read_text().splitlines()), 1)

    def test_sparse_and_failed_profiles_do_not_create_matrices(self):
        spec = {"id": "sparse", "area": "Synthetic", "kind": "profile", "dimension": "tags",
                "geography_verified": True, "endpoint": "/v2/insights", "params": {"filter.type": "urn:tag", "take": 20}}
        with tempfile.TemporaryDirectory() as d:
            def fake(*args):
                return 200, {}, b'{"results":{"tags":[{"tag_id":"a","query":{"affinity":1}}]}}'
            qloo.run({"requests": [spec]}, d, {"QLOO_API_KEY": "fake-secret"}, delay=0, request_fn=fake)
            self.assertFalse(list(Path(d).glob("matrix_*.csv")))
            with (Path(d) / "similarity_pairs.csv").open(encoding="utf-8-sig") as f:
                self.assertEqual(list(csv.DictReader(f)), [])

    def test_network_retry_obeys_attempt_budget(self):
        plan = {"requests": [{"id": "timeout", "kind": "lookup", "endpoint": "/search", "params": {"query": "synthetic"}}]}
        def timeout(*args):
            raise TimeoutError("synthetic timeout")
        with tempfile.TemporaryDirectory() as d, patch.object(qloo.time, "sleep"):
            qloo.run(plan, d, {"QLOO_API_KEY": "fake-secret"}, budget=2, retries=3, request_fn=timeout)
            attempts = (Path(d) / "requests.jsonl").read_text().splitlines()
            self.assertEqual(len(attempts), 2)
            self.assertTrue(all(not json.loads(a)["ok"] for a in attempts))

    def test_heatmap_popularity_and_profile_compatibility(self):
        row = qloo.normalized({"results": {"heatmap": [{"location": {"geohash": "abc123", "latitude": 1, "longitude": 2},
                                                       "query": {"affinity": 1, "popularity": 0}}]}})[0]
        self.assertEqual(row["popularity"], 0)
        a = {"endpoint": "/v2/insights", "params": {"signal.location": "a", "signal.location.radius": 500, "take": 20}}
        b = {"endpoint": "/v2/insights", "params": {"signal.location": "b", "signal.location.radius": 500, "take": 20}}
        self.assertEqual(qloo.profile_signature(a), qloo.profile_signature(b))
        b["params"]["signal.location.radius"] = 1000
        self.assertNotEqual(qloo.profile_signature(a), qloo.profile_signature(b))


if __name__ == "__main__":
    unittest.main()
