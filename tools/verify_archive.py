#!/usr/bin/env python3
"""Verify the retained transfer manifest without API calls or file mutations."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / 'research/TRANSFER_MANIFEST.json').read_text(encoding='utf-8'))
failures = []
for record in manifest['retained']:
    path = ROOT / record['path']
    if not path.is_file():
        failures.append(record['path'] + ': missing')
        continue
    raw = path.read_bytes()
    if len(raw) != record['bytes'] or hashlib.sha256(raw).hexdigest() != record['sha256']:
        failures.append(record['path'] + ': hash/size mismatch')
for message in failures:
    print(message)
print(('FAIL' if failures else 'PASS') + ': ' + str(len(manifest['retained'])) + ' archived files checked.')
raise SystemExit(1 if failures else 0)
