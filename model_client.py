"""Bounded NVIDIA hosted tool calls. No SDK, redirects, raw logging or client credentials."""
import json
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from qloo_client import environment
from protection import provider_call, LimitReached

MODEL = 'nvidia/nemotron-3-super-120b-a12b'
ENDPOINT = 'https://integrate.api.nvidia.com/v1/chat/completions'


class ModelError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__('Investigator model unavailable: ' + code)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class ModelClient:
    def __init__(self):
        env = environment(['NVIDIA_API_KEY', 'NVIDIA_MODEL', 'NVIDIA_CALL_LIMIT'])
        self.key = env['NVIDIA_API_KEY']
        self.model = env['NVIDIA_MODEL'] or MODEL
        self.limit = max(0, min(1000, int(env['NVIDIA_CALL_LIMIT'] or 150)))
        self.calls = 0
        self.lock = threading.Lock()
        self.opener = build_opener(NoRedirect())

    def decide(self, instructions, state, schema):
        if not self.key:
            raise ModelError('not_configured')
        with self.lock:
            if self.calls >= self.limit:
                raise ModelError('process_budget')
            try: provider_call("nvidia")
            except (LimitReached, OSError): raise ModelError("total_budget") from None
            self.calls += 1
        payload = {
            'model': self.model,
            'messages': [{'role': 'system', 'content': instructions},
                         {'role': 'user', 'content': json.dumps(state, ensure_ascii=False)}],
            'tools': [{'type': 'function', 'function': {'name': 'investigate',
                'description': 'Choose the next bounded investigative action.', 'parameters': schema}}],
            'tool_choice': {'type': 'function', 'function': {'name': 'investigate'}},
            'temperature': 0.2, 'max_tokens': 850, 'stream': False,
            'chat_template_kwargs': {'thinking': False} if self.model.startswith('moonshotai/') else {'enable_thinking': False},
        }
        req = Request(ENDPOINT, data=json.dumps(payload).encode(),
                      headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        start = time.monotonic()
        try:
            with self.opener.open(req, timeout=30) as response:
                if response.status != 200:
                    raise ModelError('pending_or_failed')
                raw = response.read(262145)
                if len(raw) > 262144:
                    raise ModelError('response_too_large')
                data = json.loads(raw)
            choice = data['choices'][0]
            calls = choice['message'].get('tool_calls', [])
            if choice['finish_reason'] not in {'tool_calls', 'stop'} or len(calls) != 1:
                raise ModelError('invalid_tool_response')
            call = calls[0]['function']
            if call['name'] != 'investigate':
                raise ModelError('invalid_tool_name')
            action = json.loads(call['arguments'])
            if not isinstance(action, dict):
                raise ModelError('invalid_action')
            # Reasoning/content fields are intentionally discarded, never traced or exported.
            return action, {'provider': 'NVIDIA', 'model': data.get('model', self.model),
                            'seconds': round(time.monotonic() - start, 3), 'usage': data.get('usage', {})}
        except HTTPError as exc:
            raise ModelError({401: 'authentication', 402: 'quota', 403: 'access', 429: 'rate_limit'}.get(exc.code, 'http_' + str(exc.code))) from None
        except (URLError, TimeoutError, OSError):
            raise ModelError('timeout_or_network') from None
        except (KeyError, TypeError, ValueError, IndexError):
            raise ModelError('malformed_response') from None
