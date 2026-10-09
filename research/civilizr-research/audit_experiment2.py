"""Read-only research artifact audit. Prints counts, never credentials."""
import hashlib
from pathlib import Path
import qloo
from experiment2 import E, ROOT


def main():
    checked=0; statuses={}; plan_hash=hashlib.sha256((ROOT/'EXPERIMENT_2_PLAN.md').read_bytes()).hexdigest()
    for folder in (E/'runs').iterdir():
        manifest=qloo.read_json(folder/'manifest.json')
        assert manifest['identity']['plan']['experiment2']['plan_sha256']==plan_hash
        for meta_file in folder.glob('*.meta.json'):
            meta=qloo.read_json(meta_file)
            raw=folder/meta['raw_file']
            assert hashlib.sha256(raw.read_bytes()).hexdigest()==meta['response_sha256'], raw.name
            statuses[meta['http_status']]=statuses.get(meta['http_status'],0)+1
            checked+=1
    attempts=sum(len(p.read_text(encoding='utf8').splitlines()) for p in (E/'runs').glob('*/requests.jsonl'))
    assert checked==attempts==80
    assert statuses=={200:80}
    # Ensure the original shared runner's contents still match Experiment 1.
    # Experiment 1 evolved the runner; compare its final live run, not the early pilot.
    old=qloo.read_json(ROOT/'runs/09-sensitivity/manifest.json')
    assert old['identity']['code_sha256']==hashlib.sha256((ROOT/'qloo.py').read_bytes()).hexdigest()
    secret=qloo.load_env(ROOT/'civilizr-research.env')['QLOO_API_KEY'].encode()
    assert secret, 'Credential missing; cannot perform exact-value leakage audit'
    scanned=0
    for f in ROOT.rglob('*'):
        if not f.is_file() or f.name.endswith('.env') or f.name.startswith('.env') or '__pycache__' in f.parts: continue
        assert secret not in f.read_bytes(), 'Credential appears outside environment file: '+str(f.relative_to(ROOT))
        scanned+=1
    print(f'PASS: {checked} raw response hashes; {attempts} attempts; HTTP statuses {statuses}.')
    print(f'PASS: frozen plan hashes, original runner unchanged, no API-key value in {scanned} non-env files.')


if __name__=='__main__': main()
