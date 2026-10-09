#!/usr/bin/env python3
"""Scan the Git index and optional reachable history. Never print matched contents."""
import argparse
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'nvidia_token': rb'nvapi-[A-Za-z0-9_-]{20,}',
    'github_token': rb'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'openai_token': rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}',
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'aws_key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'literal_credential': rb'''(?im)\b[A-Z0-9_]*(?:API_KEY|ACCESS_TOKEN|CLIENT_SECRET|PASSWORD)["']?\s*[:=]\s*["']([A-Za-z0-9_./+=-]{16,})["']''',
    'machine_home_path': rb'(?i)(?<![a-z0-9_.:/])(?:[a-z]:[\\/](?:Users|Documents and Settings)[\\/]|/(?:Users|home)/)[^\s"<>]+',
}
# Reviewed synthetic literals in the original frozen runner tests only.
FIXTURES = {
    ('research/civilizr-research/test_qloo.py', 'literal_credential'): {
        '94653caa7be45a267037ad3d19bcead5b3ba1316c45cb01975cdcfb356bad2f8',
        'f9fc9db69231b19a2b526f0f1c00665d1bb14623fe2807e422b1b7ce1a3d9041',
    }
}
SECRET_NAMES = ('QLOO_API_KEY', 'NVIDIA_API_KEY', 'OPENAI_API_KEY', 'GH_TOKEN', 'GITHUB_TOKEN')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, stderr=subprocess.PIPE)


def known_secrets():
    values = {name: os.environ.get(name, '') for name in SECRET_NAMES}
    file = ROOT / '.env'
    if file.exists():
        for line in file.read_text(encoding='utf-8-sig').splitlines():
            line = line.strip().removeprefix('export ')
            if not line or line.startswith('#') or '=' not in line:
                continue
            name, value = line.split('=', 1)
            if name.strip() not in SECRET_NAMES:
                continue
            value = value.strip()
            if value.startswith(('"', "'")):
                value = value[1:].split(value[0], 1)[0]
            else:
                value = re.split(r'\s+#', value, 1)[0].strip()
            if value and not values[name.strip()]:
                values[name.strip()] = value
    return [(name, value.encode()) for name, value in values.items() if value]


def forbidden_path(path):
    p = PurePosixPath(path)
    name = p.name.lower()
    if name in {'.env.example'} or name.endswith('.env.example'):
        return False
    return (name == '.env' or name.startswith('.env.') or name.endswith('.env')
            or '.env.' in name or p.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}
            or name in {'credentials.json', 'secrets.json'}
            or any(part in {'.cache', '__pycache__', '.venv', 'node_modules', 'test-results'} for part in p.parts))


def findings(path, raw, secrets):
    result = []
    for name, value in secrets:
        if value in raw:
            result.append(('configured_' + name, raw[:raw.index(value)].count(b'\n') + 1))
    for rule, pattern in PATTERNS.items():
        for match in re.finditer(pattern, raw):
            if hashlib.sha256(match.group(1) if rule == 'literal_credential' else match.group()).hexdigest() in FIXTURES.get((path, rule), set()):
                continue
            result.append((rule, raw[:match.start()].count(b'\n') + 1))
    if path.endswith('.env.example'):
        for n, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
            if '=' in line and line.split('=', 1)[0].strip() in SECRET_NAMES and line.split('=', 1)[1].strip():
                result.append(('nonempty_example_credential', n))
    return sorted(set(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true', help='Also inspect every object reachable from all local refs.')
    args = parser.parse_args()
    if Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() != ROOT:
        raise RuntimeError('Run inside this project\'s dedicated repository, not a parent workspace repository.')
    entries = []
    for record in git('ls-files', '--stage', '-z').split(b'\0'):
        if not record:
            continue
        meta, path = record.split(b'\t', 1)
        mode, oid, stage = meta.decode().split()
        if stage != '0':
            raise RuntimeError('Resolve merge conflicts before auditing.')
        entries.append((oid, path.decode('utf-8')))
    if not entries:
        raise RuntimeError('No files are staged/tracked to audit.')
    staged = len(entries)
    if args.history:
        for line in git('rev-list', '--objects', '--all').decode('utf-8').splitlines():
            oid, _, path = line.partition(' ')
            entries.append((oid, path or 'history-object:' + oid))
    secrets = known_secrets()
    proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    checked, total_bytes, problems = set(), 0, 0
    try:
        for oid, path in entries:
            if forbidden_path(path):
                print('FAIL forbidden_path ' + path)
                problems += 1
            # A blob can be renamed, so retain path-specific allowlist checks.
            identity = (oid, path)
            if identity in checked:
                continue
            checked.add(identity)
            proc.stdin.write((oid + '\n').encode()); proc.stdin.flush()
            header = proc.stdout.readline().decode().split()
            if len(header) != 3:
                raise RuntimeError('Unable to read a Git object for audit.')
            kind, size = header[1], int(header[2])
            raw = proc.stdout.read(size)
            if len(raw) != size or proc.stdout.read(1) != b'\n':
                raise RuntimeError('Incomplete Git object read.')
            if kind not in {'blob', 'commit', 'tag'}:
                continue
            total_bytes += size
            for rule, line in findings(path, raw, secrets):
                print('FAIL ' + rule + ' ' + path + ':' + str(line))
                problems += 1
    finally:
        proc.stdin.close(); proc.stdout.close(); proc.wait()
    print(('PASS' if not problems else 'FAIL') + ': ' + str(staged) + ' indexed files; '
          + str(len(checked)) + ' index/history objects; ' + str(total_bytes) + ' bytes; '
          + str(len(secrets)) + ' configured secrets checked; ' + str(problems) + ' findings.')
    print('Scope: Git index' + (' and all reachable local-ref history.' if args.history else '.'))
    print('Pattern scans cannot prove the absence of all secrets. Review new data before staging.')
    return 1 if problems else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError):
        print('Audit could not complete; no file or credential contents are displayed.', file=sys.stderr)
        sys.exit(2)
