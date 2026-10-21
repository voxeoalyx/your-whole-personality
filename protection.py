"""Single-instance abuse controls; durable provider spend ceilings, no user payloads."""
import hashlib
import os
from pathlib import Path
import sqlite3
import threading
import time


class LimitReached(Exception):
    pass


class Ledger:
    def __init__(self, path):
        self.path = str(path)
        if self.path != ':memory:':
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()
        self.db = sqlite3.connect(self.path, check_same_thread=False, timeout=5)
        self.db.execute('CREATE TABLE IF NOT EXISTS usage (bucket TEXT PRIMARY KEY, n INTEGER NOT NULL)')
        self.db.commit()

    def take(self, bucket, maximum):
        # BEGIN IMMEDIATE also coordinates independent connections after restart.
        with self.lock:
            try:
                self.db.execute('BEGIN IMMEDIATE')
                row = self.db.execute('SELECT n FROM usage WHERE bucket=?', (bucket,)).fetchone()
                if (row[0] if row else 0) >= maximum:
                    raise LimitReached('The live request budget is used up. Play a recorded round.')
                self.db.execute('INSERT INTO usage VALUES (?,1) ON CONFLICT(bucket) DO UPDATE SET n=n+1', (bucket,))
                self.db.commit()
            except Exception:
                self.db.rollback()
                raise


LEDGER = Ledger(os.environ.get('BUDGET_DB', ':memory:'))


def provider_call(provider):
    # Lifetime ceilings intentionally do not reset at midnight or on redeploy.
    maximum = int(os.environ.get(provider.upper() + '_TOTAL_LIMIT', '1000' if provider == 'qloo' else '500'))
    try:
        LEDGER.take('provider:' + provider, maximum)
    except (sqlite3.Error, OSError):
        raise LimitReached('The live budget store is unavailable. Play a recorded round.') from None


class VisitorLimits:
    def __init__(self):
        self.lock = threading.Lock()
        self.windows = {}

    def take(self, address, category, maximum, seconds):
        now = time.monotonic()
        # Raw addresses are never retained. No proxy-header trust by default.
        ident = hashlib.sha256(address.encode()).hexdigest()
        with self.lock:
            self.windows = {k:v for k,v in self.windows.items() if v[1] > now}
            key = (ident, category)
            count, until = self.windows.get(key, (0, now + seconds))
            if count >= maximum or key not in self.windows and len(self.windows) >= 4096:
                raise LimitReached('Too many live requests. Wait a minute or play a recorded round.')
            self.windows[key] = (count + 1, until)


VISITORS = VisitorLimits()
