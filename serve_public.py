"""Fail-closed entrypoint for one HTTPS-proxied judging instance."""
import os
from pathlib import Path
from urllib.parse import urlsplit

def main():
    origin = os.environ.get('PUBLIC_ORIGIN') or os.environ.get('RENDER_EXTERNAL_URL', '')
    p = urlsplit(origin)
    if p.scheme != 'https' or not p.hostname or p.username or p.password or p.path or p.query or p.fragment:
        raise SystemExit('Set PUBLIC_ORIGIN to the exact HTTPS origin, without a trailing slash.')
    if os.environ.get('QLOO_DISPLAY_APPROVED') != '1':
        raise SystemExit('Confirm applicable Qloo demo/display/recorded-data rights before public launch; then set QLOO_DISPLAY_APPROVED=1.')
    path = os.environ.get('BUDGET_DB', '')
    if not path or path == ':memory:' or not Path(path).is_absolute():
        raise SystemExit('BUDGET_DB must name an absolute database file on a persistent volume.')
    # Import only after the durable ledger configuration is validated.
    from server import LocalServer, Handler
    http = LocalServer(('0.0.0.0', int(os.environ.get('PORT', '10000'))), Handler)
    http.public_origin = origin
    http.serve_forever()

if __name__ == '__main__':
    main()
