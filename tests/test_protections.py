import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from protections import RateLimits, BoundedWorkers, Busy, task_deadline, check_deadline, WorkExpired


class ProtectionTests(unittest.TestCase):
    def test_limits_expire_and_do_not_retain_addresses(self):
        now=[0.0];limits=RateLimits(lambda:now[0])
        self.assertEqual([limits.allow('visitor','answer') for _ in range(30)],[0]*30)
        self.assertEqual(limits.allow('visitor','answer'),60)
        self.assertEqual(limits.allow('other','answer'),0)
        self.assertNotIn('visitor',repr(limits.entries))
        now[0]=61
        self.assertEqual(limits.allow('visitor','answer'),0)
        self.assertEqual(len(limits.entries),1)

    def test_global_limit_and_atomic_visitor_admission(self):
        limits=RateLimits(lambda:0)
        with ThreadPoolExecutor(max_workers=16) as pool:
            results=list(pool.map(lambda _:limits.allow('same','answer'),range(80)))
        self.assertEqual(results.count(0),30)
        limits=RateLimits(lambda:0)
        for i in range(120):self.assertEqual(limits.allow(str(i),'search'),0)
        self.assertEqual(limits.allow('new','validate'),60)

    def test_worker_reservations_bound_initial_and_followup_work(self):
        workers=BoundedWorkers(1);gate=threading.Event()
        try:
            workers.reserve();future=workers.submit(gate.wait)
            with self.assertRaises(Busy):workers.reserve()
            gate.set();future.result(timeout=2)
            workers.pool.shutdown(wait=True)
            workers.reserve()
            with self.assertRaises(RuntimeError):workers.submit(lambda:None)
            workers.reserve();workers.release()  # Failed submission returned its slot.
        finally:gate.set();workers.pool.shutdown(wait=True)

    def test_weighted_budget_covers_provider_cost_and_renews(self):
        now=[0.0];limits=RateLimits(lambda:now[0])
        self.assertEqual(limits.allow('a','game'),0)
        self.assertEqual(limits.allow('a','game'),0)
        self.assertEqual(limits.allow('a','game'),900)
        # Feedback is already covered by admission, so a round can still finish.
        self.assertEqual(limits.allow('a','answer'),0)
        self.assertEqual(limits.allow('b','game'),0)
        now[0]=901;self.assertEqual(limits.allow('a','game'),0)

    def test_task_deadline_is_cooperative_and_thread_scoped(self):
        with patch('protections.time.monotonic',return_value=10):
            with task_deadline(5):
                check_deadline()
                with patch('protections.time.monotonic',return_value=16):
                    with self.assertRaises(WorkExpired):check_deadline()
                    with ThreadPoolExecutor(max_workers=1) as pool:
                        pool.submit(check_deadline).result(timeout=2)
            check_deadline()
