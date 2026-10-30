import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from investigator import Investigator, EvidenceClient, accuracy
from model_client import ModelClient, ModelError
from qloo_client import ROOT, QlooError


def demo():
    return json.loads((ROOT/'data/demos.json').read_text(encoding='utf-8'))['overthinker']


def action(state, name='TEST_PREDICTION', candidate=None):
    p=candidate or state['candidates'][0]
    return {'action':name,'domain':p['domain'],'candidate_id':p['id'],'basis':'original',
            'observation':'My theory is available for demolition.','decision_summary':'Test a supplied cultural candidate.',
            'hypotheses':[]}


class FixtureModel:
    """Explicit test double, never evidence of LLM adaptation."""
    model='fixture-not-a-model'
    def __init__(self):self.states=[]
    def decide(self,instructions,state,schema):
        self.states.append(state)
        if not state['questions_remaining']:
            result=action(state);result['action']='DELIVER_VERDICT';return result,{'fixture':True}
        rows=state['candidates']
        p=rows[-1] if any(r['response']=='no' for r in state['feedback']) else rows[0]
        return action(state,'INVESTIGATE_CONTRADICTION' if any(r['response']=='no' for r in state['feedback']) else 'TEST_PREDICTION',p),{'fixture':True}


class InvestigatorTests(unittest.TestCase):
    def test_actual_feedback_changes_selected_candidate_in_fixture_loop(self):
        paths=[]
        for response in ['yes','no']:
            model=FixtureModel();e=Investigator(demo(),model)
            for n in range(3):
                e.advance();p=e.predictions[-1]
                if n<2:e.answer(p['id'],response,n)
            paths.append(e)
            self.assertEqual(model.states[-1]['feedback'][-1]['response'],response)
        self.assertNotEqual(paths[0].predictions[2]['id'],paths[1].predictions[2]['id'])
        self.assertNotEqual(paths[0].trace[-1]['action']['action'],paths[1].trace[-1]['action']['action'])

    def test_question_budget_accuracy_unknown_and_final_call(self):
        e=Investigator(demo(),FixtureModel())
        for n,response in enumerate(['yes','no','unknown','yes','unknown']):
            e.advance();e.answer(e.predictions[-1]['id'],response,n)
        e.advance();e.advance()
        self.assertTrue(e.finished);self.assertEqual(len(e.predictions),5)
        s=accuracy(e.predictions,e.answers);self.assertEqual(s['known'],3);self.assertEqual(s['rate'],2/3)
        self.assertEqual(s['unknown'],2)

    def test_retries_stale_feedback_and_session_isolation(self):
        e=Investigator(demo(),FixtureModel());other=Investigator(demo(),FixtureModel());e.advance();p=e.predictions[0]
        self.assertTrue(e.answer(p['id'],'yes',0));self.assertFalse(e.answer(p['id'],'yes',0))
        with self.assertRaises(ValueError):e.answer(p['id'],'no',0)
        with self.assertRaises(ValueError):e.answer('invented','yes',1)
        self.assertEqual(other.answers,{})

    def test_unknown_is_forwarded_without_becoming_a_negative_signal(self):
        model=FixtureModel();e=Investigator(demo(),model);e.advance();e.answer(e.predictions[-1]['id'],'unknown',0);e.advance()
        self.assertEqual(model.states[-1]['feedback'][0]['response'],'unknown')
        self.assertEqual(model.states[-1]['accuracy']['known'],0)

    def test_invalid_candidate_repetition_and_false_hypothesis_rejected(self):
        e=Investigator(demo(),FixtureModel());s=e.context();a=action(s);a['candidate_id']='invented'
        with self.assertRaises(ValueError):e.validate(a,False)
        a=action(s);a['hypotheses']=[{'domain':a['domain'],'fit':'promising','confidence':'medium','evidence_ids':[]}]
        with self.assertRaises(ValueError):e.validate(a,False)
        e.advance();a=action(s)
        with self.assertRaises(ValueError):e.validate(a,False)

    def test_model_failure_is_labeled_and_completable(self):
        class Broken:
            def decide(self,*args):raise ModelError('rate_limit')
        e=Investigator(demo(),Broken())
        for n in range(5):e.advance();e.answer(e.predictions[-1]['id'],'yes',n)
        e.advance();snap=e.snapshot()
        self.assertEqual(snap['game']['investigator']['mode'],'fixed_qloo_fallback')
        self.assertEqual(e.fallback_reason,'rate_limit');self.assertTrue(e.finished);self.assertEqual(e.calls,1)

    def test_final_call_failure_and_exhaustion_are_closing_only_fallbacks(self):
        class FailClosing(FixtureModel):
            def decide(self,instructions,state,schema):
                if not state['questions_remaining']:raise ModelError('timeout')
                return super().decide(instructions,state,schema)
        for exhausted in [False,True]:
            e=Investigator(demo(),FailClosing())
            for n in range(5):e.advance();e.answer(e.predictions[-1]['id'],'yes',n)
            if exhausted:e.calls=e.max_calls
            e.advance();a=e.snapshot()['game']['investigator']
            self.assertTrue(a['closing_fallback']);self.assertIsNone(a['fallback_reason'])
            self.assertEqual(a['mode'],'agentic_qloo');self.assertEqual(len(e.predictions),5)
            self.assertEqual(a['trace'][-1]['event'],'closing_fallback')

    def test_fresh_configuration_uses_verified_model(self):
        with patch('model_client.environment',return_value={'NVIDIA_API_KEY':'','NVIDIA_MODEL':'','NVIDIA_CALL_LIMIT':''}):
            self.assertEqual(ModelClient().model,'nvidia/nemotron-3.5-lightning-30b-a3b')

    def test_round_budget_and_invalid_action_loops_are_bounded(self):
        class Invalid:
            def decide(self,*args):return {},{}
        e=Investigator(demo(),Invalid());e.advance()
        self.assertEqual(e.calls,3);self.assertEqual(e.fallback_reason,'invalid_actions');self.assertEqual(len(e.predictions),1)
        e=Investigator(demo(),FixtureModel());e.calls=10;e.advance();self.assertEqual(e.fallback_reason,'round_model_budget')

    def test_sparse_evidence_and_qloo_failure_are_explicit(self):
        g=demo();g['full']={};g['predictions']=[];e=Investigator(g,FixtureModel());e.advance()
        self.assertTrue(e.finished);self.assertIn('evidence',e.stop_reason)
        class Broken:
            def insights(self,*args):raise QlooError('Offline','service_unavailable')
        c=EvidenceClient(Broken(),1)
        with self.assertRaises(QlooError):c.insights(demo()['interests'],'movie')
        self.assertEqual(c.snapshot()[0]['error'],'service_unavailable')
        with self.assertRaises(QlooError):c.insights(demo()['interests'],'movie')
        self.assertEqual(c.calls,1)

    def test_llm_only_context_has_no_qloo_scores_rank_order_or_influence(self):
        e=Investigator(demo(),FixtureModel(),mode='llm_only');s=e.context()
        self.assertIsNone(s['influence']);self.assertEqual(s['discovery_queries_remaining'],0)
        self.assertEqual(list(s['candidates'][0]),['id','name','domain'])
        self.assertEqual([p['id'] for p in s['candidates']],sorted(p['id'] for p in s['candidates']))

    def test_dynamic_schema_and_unknown_feedback_cannot_confirm_a_hypothesis(self):
        e=Investigator(demo(),FixtureModel());self.assertEqual(e.action_schema()['properties']['hypotheses']['maxItems'],0)
        e.advance();p=e.predictions[-1];e.answer(p['id'],'unknown',0)
        self.assertNotIn(p['id'],e.action_schema()['properties']['candidate_id']['enum'])
        a=action(e.context());a['hypotheses']=[{'domain':p['domain'],'fit':'promising','confidence':'medium','evidence_ids':[p['id']]}]
        with self.assertRaises(ValueError):e.validate(a,False)

    def test_mixed_signal_receipt_and_influence_remain_unchanged_after_feedback(self):
        from signals import HOBBIES
        g=demo();g['interests'].append({'id':HOBBIES+':running','name':'Running','type':'audience'})
        e=Investigator(g,FixtureModel());before=json.dumps(g['sensitivity'],sort_keys=True)
        e.advance();e.answer(e.predictions[-1]['id'],'no',0);e.advance()
        self.assertEqual(before,json.dumps(e.snapshot()['game']['sensitivity'],sort_keys=True))

    def test_credentials_never_in_deliverables(self):
        key=ModelClient().key
        if not key:self.skipTest('No NVIDIA key')
        for folder in ['static','data','tests']:
            for p in (ROOT/folder).rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:self.assertNotIn(key.encode(),p.read_bytes())

    def test_confirmed_discovery_uses_only_yes_and_keeps_original_signals(self):
        from copy import deepcopy
        from signals import HOBBIES, parameters
        g=demo();g['interests'].append({'id':HOBBIES+':running','name':'Running','type':'audience'})
        original=deepcopy(g)
        class Qloo:
            def insights(self,interests,domain,panel=None,take=20):
                self.interests=interests
                return [{'id':'book'+str(n),'name':'Book '+str(n),'score':0.9-n/10} for n in range(4)]
        class QueryModel(FixtureModel):
            def decide(self,instructions,state,schema):
                if not self.states:
                    self.states.append(state);a=action(state,'QUERY_QLOO')
                    a.update(domain='book',candidate_id='',basis='confirmed');return a,{}
                return action(state,candidate=next(p for p in state['candidates'] if p['id']=='book0')),{}
        q=Qloo();e=Investigator(g,QueryModel(),EvidenceClient(q))
        e.predictions=deepcopy(g['predictions'][:3])
        e.answers={p['id']:r for p,r in zip(e.predictions,['yes','no','unknown'])}
        e.advance()
        self.assertEqual(e.predictions[-1]['id'],'book0')
        self.assertEqual([p['id'] for p in q.interests], [p['id'] for p in g['interests']]+[g['predictions'][0]['id']])
        receipt=e.qloo.snapshot()[0]
        self.assertEqual(receipt['parameters']['signal.demographics.audiences'],parameters(g['interests'])['signal.demographics.audiences'])
        self.assertEqual(e.game['sensitivity'],original['sensitivity'])
        self.assertEqual(e.query_count,1)

    def test_flat_or_failed_discovery_never_becomes_a_prediction(self):
        for failure in [None,'unsupported','service_unavailable']:
            class Qloo:
                def insights(self,*args):
                    if failure:raise QlooError('Unavailable',failure)
                    return [{'id':'flat'+str(n),'name':'Flat','score':1.0} for n in range(4)]
            class QueryModel(FixtureModel):
                def decide(self,instructions,state,schema):
                    if not self.states:
                        self.states.append(state);a=action(state,'CHANGE_DOMAIN');a.update(domain='book',candidate_id='');return a,{}
                    return action(state),{}
            e=Investigator(demo(),QueryModel(),EvidenceClient(Qloo()));e.advance()
            self.assertIn('book',e.unsupported)
            self.assertFalse(any(p.startswith('flat') for p in e.candidates))
            self.assertIsNone(e.fallback_reason);self.assertEqual(len(e.predictions),1)

    def test_discovery_caps_and_influence_pending_are_explicit(self):
        e=Investigator(demo(),FixtureModel(),EvidenceClient(object()))
        a=action(e.context(),'QUERY_QLOO');a.update(domain='book',candidate_id='')
        e.query_count=3
        with self.assertRaises(ValueError):e.validate(a,False)
        e.query_count=0;a['basis']='confirmed'
        with self.assertRaises(ValueError):e.validate(a,False)
        a['basis']='original';e.queried.add(('book','original'))
        with self.assertRaises(ValueError):e.validate(a,False)
        a['action']='ANALYZE_INFLUENCE';e.analyzed=True
        with self.assertRaises(ValueError):e.validate(a,False)


class ModelTransportTests(unittest.TestCase):
    def client(self,payload):
        from unittest.mock import MagicMock
        c=ModelClient();c.key='test-placeholder';c.opener=MagicMock()
        response=c.opener.open.return_value.__enter__.return_value
        response.status=200;response.read.return_value=json.dumps(payload).encode()
        return c

    def test_structured_response_discards_private_reasoning(self):
        c=self.client({'choices':[{'finish_reason':'tool_calls','message':{
            'reasoning_content':'PRIVATE-THOUGHT','content':'PRIVATE-CONTENT',
            'tool_calls':[{'function':{'name':'investigate','arguments':'{"action":"TEST_PREDICTION"}'}}]}}],
            'usage':{'total_tokens':12}})
        a,meta=c.decide('Instructions',{},{});self.assertEqual(a['action'],'TEST_PREDICTION')
        self.assertNotIn('PRIVATE',json.dumps([a,meta]));self.assertNotIn(c.key,json.dumps([a,meta]))
        req=c.opener.open.call_args.args[0]
        self.assertEqual(req.full_url,'https://integrate.api.nvidia.com/v1/chat/completions')
        self.assertEqual(c.opener.open.call_args.kwargs['timeout'],30)

    def test_truncated_multiple_or_invented_tools_are_rejected(self):
        for finish,calls in [('length',[]),('tool_calls',[{},{}]),('tool_calls',[{'function':{'name':'shell','arguments':'{}'}}])]:
            c=self.client({'choices':[{'finish_reason':finish,'message':{'tool_calls':calls}}]})
            with self.assertRaises(ModelError):c.decide('',{},{})

    def test_process_budget_and_http_errors_do_not_leak_credentials(self):
        from urllib.error import HTTPError
        c=self.client({});c.limit=0
        with self.assertRaises(ModelError) as exc:c.decide('',{},{})
        self.assertEqual(exc.exception.code,'process_budget');c.opener.open.assert_not_called()
        c.limit=1;c.opener.open.side_effect=HTTPError('https://integrate.api.nvidia.com',429,'sensitive-body',{},None)
        with self.assertRaises(ModelError) as exc:c.decide('',{},{})
        self.assertEqual(exc.exception.code,'rate_limit');self.assertNotIn('sensitive',str(exc.exception))


if __name__=='__main__':unittest.main()
