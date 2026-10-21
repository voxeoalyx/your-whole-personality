"""Real local HTTP boundary tests with a stub upstream; no Qloo calls."""
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request,urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=server.LocalServer(('127.0.0.1',0),server.Handler)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        cls.base='http://127.0.0.1:'+str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close()

    def setUp(self):
        server.VISITORS.windows.clear()

    def request(self,path,body=None,headers=None):
        req=Request(self.base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json',**(headers or {})})
        try:r=urlopen(req,timeout=3)
        except HTTPError as exc:r=exc
        with r:return r.status,r.headers,r.read()

    def test_static_server_never_serves_credentials_or_source(self):
        for path in ['/.env','/server.py','/data/demos.json','/../civilizr-research/civilizr-research.env']:
            self.assertEqual(self.request(path)[0],404)

    def test_cross_origin_and_host_rejected(self):
        self.assertEqual(self.request('/api/config',headers={'Origin':'https://example.com'})[0],403)
        self.assertEqual(self.request('/api/config',headers={'Host':'attacker.test'})[0],403)

    def test_config_contains_no_key(self):
        status,headers,raw=self.request('/api/config');self.assertEqual(status,200)
        data=json.loads(raw);self.assertNotIn('key',data);self.assertEqual(headers['Cache-Control'],'no-store')
        if server.CLIENT.key:self.assertNotIn(server.CLIENT.key.encode(),raw)
        if server.MODEL.key:self.assertNotIn(server.MODEL.key.encode(),raw)

    def test_agent_feedback_is_idempotent_and_job_scoped(self):
        import time
        from investigator import Investigator
        from test_investigator import FixtureModel,demo
        engine=Investigator(demo(),FixtureModel());engine.advance()
        body={'id':'test-agent','prediction_id':engine.predictions[0]['id'],'response':'unknown','sequence':0}
        with patch.dict(server.INVESTIGATORS,{'test-agent':engine}),patch.dict(server.JOBS,{'test-agent':{'status':'waiting','created':time.monotonic()}}),patch.object(server.WORKERS,'submit') as submit:
            status,_,raw=self.request('/api/answer',body);self.assertEqual(status,202)
            self.assertFalse(json.loads(raw)['duplicate'])
            status,_,raw=self.request('/api/answer',body);self.assertEqual(status,202)
            self.assertTrue(json.loads(raw)['duplicate']);self.assertEqual(submit.call_count,1)
            self.assertEqual(self.request('/api/answer',{**body,'response':'no'})[0],400)
            self.assertEqual(self.request('/api/answer',{**body,'id':'missing-round'})[0],404)
            self.assertEqual(engine.answers[body['prediction_id']],'unknown')

    def test_invalid_interest_sets_are_rejected(self):
        for ids in [[],['x']*3,['x','y','z'],[None,'x','y']]:
            self.assertEqual(self.request('/api/game',{'mode':'live','ids':ids})[0],400)

    def test_known_unsupported_entity_not_substituted(self):
        dune=next(e for e in server.CATALOG if e['alias']=='dune')
        status,_,raw=self.request('/api/validate',{'id':dune['id']})
        self.assertEqual(status,200);data=json.loads(raw);self.assertFalse(data['valid']);self.assertEqual(data['entity']['id'],dune['id'])

    def test_recorded_round_stays_labeled_and_needs_no_upstream(self):
        before=server.CLIENT.calls
        for ident in ['overthinker','comfort','sidequest']:
            status,_,raw=self.request('/api/game',{'mode':'demo','demo_id':ident});self.assertEqual(status,202)
            status,_,raw=self.request('/api/game/'+json.loads(raw)['id']);data=json.loads(raw)
            self.assertEqual(data['game']['source'],'recorded');self.assertEqual(data['status'],'ready')
        self.assertEqual(before,server.CLIENT.calls)

    def test_typed_validation_and_job_preserve_audience_urn(self):
        from signals import normalize,HOBBIES
        audience=normalize({'id':HOBBIES+':running','type':HOBBIES,'name':'Running'},'audience')
        with patch.object(server.CLIENT,'insights',return_value=[{'id':str(i),'score':i/20} for i in range(20)]),patch.object(server.CLIENT,'key','test-key'),patch.dict(server.REGISTRY,{audience['id']:audience}),patch.dict(server.VALID),patch.dict(server.JOBS):
            status,_,raw=self.request('/api/validate',{'id':audience['id']});data=json.loads(raw)
            self.assertEqual(status,200);self.assertTrue(data['valid']);self.assertEqual(data['entity']['type'],'audience')
            es=[e for e in server.CATALOG if e['alias'] in ['radiohead','blue_bottle']]
            with patch.object(server.WORKERS,'submit') as submit:
                status,_,_=self.request('/api/game',{'mode':'live','ids':[e['id'] for e in es]+[audience['id']]})
                self.assertEqual(status,202)
                passed=submit.call_args.args[2];self.assertEqual(passed[-1]['id'],audience['id']);self.assertEqual(passed[-1]['type'],'audience')

    def test_flat_tag_validation_never_enables_play(self):
        from signals import normalize
        tag=normalize({'id':'urn:tag:genre:place:pilates_studio','type':'urn:tag:genre:place','name':'Pilates studio'},'tag')
        with patch.object(server.CLIENT,'insights',return_value=[{'id':str(i),'score':.765} for i in range(20)]),patch.dict(server.REGISTRY,{tag['id']:tag}),patch.dict(server.VALID),patch.dict(server.CHECK_MESSAGES):
            status,_,raw=self.request('/api/validate',{'id':tag['id']});data=json.loads(raw)
            self.assertEqual(status,200);self.assertFalse(data['valid']);self.assertIn('flat',data['message'])
            es=[e for e in server.CATALOG if e['alias'] in ['radiohead','blue_bottle']]
            self.assertEqual(self.request('/api/game',{'mode':'live','ids':[e['id'] for e in es]+[tag['id']]})[0],400)

if __name__=='__main__':unittest.main()
