"""Spend ceilings and public boundary regressions; no provider credentials."""
from concurrent.futures import ThreadPoolExecutor
import tempfile
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from protection import Ledger, LimitReached, VisitorLimits
import test_http
import server

class LedgerTests(unittest.TestCase):
    def test_provider_ceiling_prevents_any_transport(self):
        import protection
        from qloo_client import Client, QlooError
        from model_client import ModelClient, ModelError
        with patch.object(protection,'LEDGER',Ledger(':memory:')), patch.dict(os.environ,{'QLOO_TOTAL_LIMIT':'0','NVIDIA_TOTAL_LIMIT':'0'}):
            qloo=Client();qloo.key='synthetic'
            with patch('qloo_client.build_opener',side_effect=AssertionError('network')):
                with self.assertRaises(QlooError):qloo.get('/search',{'query':'test'})
            model=ModelClient();model.key='synthetic'
            with patch.object(model.opener,'open',side_effect=AssertionError('network')):
                with self.assertRaises(ModelError):model.decide('test',{}, {})
            self.assertEqual((qloo.calls,model.calls),(0,0))

    def test_restart_and_concurrent_reservations_never_exceed_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/'budget.db'
            first, second = Ledger(file), Ledger(file)
            def reserve(i):
                try: (first if i%2 else second).take('qloo',7); return 1
                except LimitReached: return 0
            with ThreadPoolExecutor(max_workers=12) as pool:
                self.assertEqual(sum(pool.map(reserve,range(30))),7)
            with self.assertRaises(LimitReached): Ledger(file).take('qloo',7)

    def test_visitor_limit_expires_and_is_independent(self):
        v=VisitorLimits()
        with patch('protection.time.monotonic',return_value=10):
            v.take('one','search',1,60)
            with self.assertRaises(LimitReached):v.take('one','search',1,60)
            v.take('two','search',1,60)
        with patch('protection.time.monotonic',return_value=71):v.take('one','search',1,60)

class PublicHTTPTests(unittest.TestCase):
    setUpClass = classmethod(test_http.HTTPTests.setUpClass.__func__)
    tearDownClass = classmethod(test_http.HTTPTests.tearDownClass.__func__)
    setUp = test_http.HTTPTests.setUp
    request = test_http.HTTPTests.request

    def test_recorded_round_does_not_allocate_jobs_and_survives_full_capacity(self):
        jobs={str(i):{'status':'working','created':0} for i in range(24)}
        with patch.dict(server.JOBS,jobs,clear=True), patch.object(server.CLIENT,'get',side_effect=AssertionError('upstream called')):
            for _ in range(30):
                status,_,raw=self.request('/api/game',{'mode':'demo','demo_id':'comfort'})
                self.assertEqual(status,202)
            self.assertEqual(len(server.JOBS),24)
            self.assertEqual(self.request('/api/game/recorded-comfort')[0],200)

    def test_search_quota_stops_before_upstream_and_ignores_spoofed_proxy(self):
        with patch.object(server,'search_interests',return_value={'results':[]}):
            for i in range(20):self.assertEqual(self.request('/api/search?q=test',headers={'X-Forwarded-For':str(i)})[0],200)
            self.assertEqual(self.request('/api/search?q=test')[0],429)
            self.assertEqual(self.request('/api/game',{'mode':'demo','demo_id':'comfort'})[0],202)

    def test_body_framing_rejected_and_health_is_provider_independent(self):
        self.assertEqual(self.request('/api/game',{'mode':'demo'},headers={'Transfer-Encoding':'chunked'})[0],400)
        self.assertEqual(self.request('/api/game',{'mode':'demo'},headers={'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.request('/healthz',headers={'Host':'internal-health-check'})[0],200)
