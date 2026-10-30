"""Single-process admission controls. Proxy/distributed limits remain a hosting duty."""
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import hashlib
import hmac
import math
import secrets
import threading
import time
from contextlib import contextmanager

_TASK = threading.local()


class WorkExpired(Exception):
    pass


@contextmanager
def task_deadline(seconds=180):
    _TASK.expires = time.monotonic() + seconds
    try:yield
    finally:del _TASK.expires


def check_deadline():
    if time.monotonic() >= getattr(_TASK, 'expires', float('inf')):
        raise WorkExpired()


class RateLimits:
    limits = {'search': 30, 'validate': 30, 'game': 6, 'answer': 30, 'game_request': 30}

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.salt = secrets.token_bytes(32)
        self.entries = {}
        self.global_calls = deque()
        self.costs = {}
        self.lock = threading.Lock()

    def allow(self, address, route):
        # Never trust client-supplied forwarding headers or retain raw IP addresses.
        ident = hmac.new(self.salt, address.encode(), hashlib.sha256).digest()
        now = self.clock()
        with self.lock:
            self._prune(now)
            cost = {'search': 3, 'validate': 8, 'game': 42, 'answer': 0, 'game_request': 0}[route]
            costs = self.costs.get(ident, deque())
            if sum(c for _, c in costs) + cost > 120:
                return max(1, math.ceil(900 - (now - costs[0][0])))
            if cost and ident not in self.costs and len(self.costs) >= 1024:return 900
            key = (ident, route)
            events = self.entries.get(key)
            if len(self.global_calls) >= 120:
                return max(1, math.ceil(60 - (now - self.global_calls[0])))
            if events is not None and len(events) >= self.limits[route]:
                return max(1, math.ceil(60 - (now - events[0])))
            if events is None:
                if len(self.entries) >= 1024:
                    return 60  # Fail closed instead of evicting an active visitor's limit.
                events = self.entries[key] = deque()
            events.append(now)
            if cost:
                costs.append((now, cost));self.costs[ident]=costs
            self.global_calls.append(now)
            return 0

    def _prune(self, now):
        self.entries = {k: v for k, v in self.entries.items() if v and v[-1] > now - 60}
        self.costs = {k: v for k, v in self.costs.items() if v and v[-1][0] > now - 900}
        for costs in self.costs.values():
            while costs and costs[0][0] <= now - 900:costs.popleft()
        for events in [self.global_calls, *self.entries.values()]:
            while events and events[0] <= now - 60:
                events.popleft()

    def cleanup(self):
        with self.lock:self._prune(self.clock())


class Busy(Exception):
    pass


class BoundedWorkers:
    """Reserve before accepting state changes; no unbounded executor queue."""
    def __init__(self, size=2):
        self.pool = ThreadPoolExecutor(max_workers=size)
        self.slots = threading.BoundedSemaphore(size)

    def reserve(self):
        if not self.slots.acquire(blocking=False):
            raise Busy()

    def release(self):
        self.slots.release()

    def submit(self, fn, *args):
        # Caller already owns one reservation; transfer it to the future.
        try:
            future = self.pool.submit(self._run, fn, args)
        except BaseException:
            self.release()
            raise
        future.add_done_callback(lambda _: self.release())
        return future

    @staticmethod
    def _run(fn, args):
        with task_deadline():return fn(*args)
