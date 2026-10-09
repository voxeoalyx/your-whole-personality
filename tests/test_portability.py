"""Portable configuration and repository guard checks; no external requests."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import qloo_client

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('repository_audit', ROOT/'tools/audit_repository.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class PortabilityTests(unittest.TestCase):
    def test_checkout_env_works_without_sibling_and_environment_takes_precedence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)/'checkout'; root.mkdir()
            sibling = Path(temp)/'civilizr-research'; sibling.mkdir()
            (sibling/'civilizr-research.env').write_text('QLOO_API_KEY=unrelated-test')
            (root/'.env').write_text('QLOO_API_KEY=local-test\nNVIDIA_API_KEY="model-test" # comment\n')
            with patch.object(qloo_client, 'ROOT', root), patch.dict(os.environ, {}, clear=True):
                values = qloo_client.environment(['QLOO_API_KEY','NVIDIA_API_KEY'])
                self.assertEqual(values, {'QLOO_API_KEY':'local-test','NVIDIA_API_KEY':'model-test'})
                with patch.dict(os.environ, {'QLOO_API_KEY':'process-test'}):
                    self.assertEqual(qloo_client.environment()['QLOO_API_KEY'], 'process-test')
                (root/'.env').unlink()
                self.assertEqual(qloo_client.environment()['QLOO_API_KEY'], '')

    def test_audit_flags_tokens_and_exact_values_without_exposing_them(self):
        token = ('nv' + 'api-' + 'x'*32).encode()
        found = audit.findings('sample.txt', token, [('TEST_KEY', token)])
        self.assertIn(('nvidia_token', 1), found)
        self.assertIn(('configured_TEST_KEY', 1), found)
        self.assertNotIn(token.decode(), str(found))
        self.assertTrue(audit.forbidden_path('nested/.env.backup'))
        self.assertTrue(audit.forbidden_path('local.key'))
        self.assertFalse(audit.forbidden_path('.env.example'))
        self.assertTrue(audit.findings('.env.example', b'QLOO_API_KEY=placeholder', []))
        self.assertFalse(audit.findings('response.json', b'https://example.com/home/review', []))
        local_path = ('/' + 'Users' + '/example/project').encode()
        self.assertIn(('machine_home_path',1), audit.findings('bad.txt', local_path, []))

if __name__ == '__main__':
    unittest.main()
