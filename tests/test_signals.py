"""Mixed-signal regression tests. No live calls; archived real captures are required."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from game import build,CATALOG
from qloo_client import Client,QlooError,unsupported,ROOT
from signals import normalize,parameters,pick_domains,validate_context,HOBBIES
import server

TAG=normalize({'id':'urn:tag:genre:media:architecture','type':'urn:tag:genre:media','name':'Architecture',
               'parents':[{'type':'urn:entity:book'},{'type':'urn:entity:author'}]},'tag')
AUD=normalize({'id':HOBBIES+':running','entity_id':'unused-uuid','type':HOBBIES,'name':'Running'},'audience')
ENT=[e for e in CATALOG if e['alias'] in ['radiohead','blue_bottle']]

def rows(domain='tv_show',flat=False):
    return [{'id':str(i),'name':'Candidate '+str(i),'type':domain,'score':1 if flat else i/20} for i in range(20)]

class SignalTests(unittest.TestCase):
    def test_routes_use_real_urns_and_omit_empty_families(self):
        params=parameters([ENT[0],TAG,AUD])
        self.assertEqual(params['signal.demographics.audiences'],[AUD['id']])
        self.assertNotIn('unused-uuid',str(params))
        self.assertEqual(set(parameters([TAG])),{'signal.interests.tags'})
        self.assertEqual(parameters([ENT[0]['id']]),parameters([ENT[0]]))

    def test_actual_insights_request_keeps_signals_and_candidate_panel_separate(self):
        c=Client()
        with patch.object(c,'get',return_value={'results':{'entities':[]}}) as get:
            c.insights([ENT[0],TAG,AUD],'movie',['candidate-b','candidate-a'])
            route,p=get.call_args.args
            self.assertEqual(route,'/v2/insights')
            self.assertEqual(p['signal.interests.tags'],[TAG['id']])
            self.assertEqual(p['signal.interests.entities'],[ENT[0]['id']])
            self.assertEqual(p['signal.demographics.audiences'],[AUD['id']])
            self.assertEqual(p['filter.results.entities'],['candidate-a','candidate-b'])

    def test_ignored_tags_and_audiences_fail_even_with_entity_results(self):
        for field,ident in [('signal.interests.tags',TAG['id']),('signal.demographics.audiences',AUD['id'])]:
            payload={'results':{'entities':[{'entity_id':'x','types':['urn:entity:movie'],'query':{'affinity':1}}]},
                     'warnings':[{'type':'not_found',field:[ident]}]}
            self.assertEqual(unsupported(payload),[ident])
            c=Client()
            with patch.object(c,'get',return_value=payload),self.assertRaises(QlooError) as err:c.insights([ENT[0],TAG,AUD],'movie')
            self.assertEqual(err.exception.ids,[ident])
        self.assertEqual(unsupported({'warnings':[{'type':'Could not calculate explainability'}]}),[])

    def test_tag_taxonomy_is_visible_and_parent_domains_held_out(self):
        self.assertEqual(TAG['type_label'],'Books genre tag')
        self.assertEqual(pick_domains([TAG,AUD]+ENT),['tv_show','movie'])
        keyword={**TAG,'parent_types':['tv_show','movie','podcast']}
        self.assertEqual(pick_domains([keyword]+ENT),['videogame','book'])

    def test_only_explicit_hobby_audiences_and_supported_tag_taxonomies(self):
        self.assertIsNone(normalize({'id':'urn:audience:life_stage:parents','type':'urn:audience:life_stage','name':'Parents'},'audience'))
        self.assertIsNone(normalize({'id':HOBBIES+':running','type':'urn:audience:life_stage','name':'Running'},'audience'))
        self.assertIsNone(normalize({'id':'urn:tag:occupation:wikidata:pilates','type':'urn:tag:occupation:wikidata','name':'Pilates'},'tag'))
        self.assertIn('hobby audience',AUD['label'])

    def test_flat_or_missing_singleton_cannot_hide_behind_entities(self):
        class Flat:
            def insights(self,*args,**kwargs):return rows(flat=True)
        with self.assertRaises(QlooError) as err:validate_context(Flat(),TAG,['tv_show','movie'])
        self.assertEqual(err.exception.ids,[TAG['id']])
        with self.assertRaises(QlooError):build(Flat(),ENT+[TAG])

    def test_tied_top_results_get_a_different_panel_before_rejection(self):
        class TiedTop:
            def insights(self,inputs,domain,panel=None,take=20):
                return rows(domain,flat=(inputs==[TAG] and panel is None))
        validate_context(TiedTop(),TAG,['tv_show','movie'])

    def test_mixed_leave_one_out_removes_only_the_selected_signal(self):
        class Fake:
            def __init__(self):self.requests=[]
            def insights(self,inputs,domain,panel=None,take=20):
                self.requests.append((parameters(inputs),domain,panel));return rows(domain)
        c=Fake();g=build(c,ENT+[TAG,AUD])
        full=parameters(ENT+[TAG,AUD])
        for removed in ENT+[TAG,AUD]:
            expected=parameters([e for e in ENT+[TAG,AUD] if e['id']!=removed['id']])
            matching=[r for r in c.requests if r[0]==expected and r[2]]
            self.assertEqual(len(matching),2)
            self.assertTrue(all(set(r[2])==set(str(i) for i in range(20)) for r in matching))
        self.assertEqual(g['sensitivity']['status'],'complete');self.assertIsNone(g['sensitivity']['winner'])
        self.assertIn('cohort context',g['signal_note'])
        self.assertEqual(g['signal_parameters']['signals'],full)

    def test_recheck_in_rounds_actual_domains_not_only_picker_domains(self):
        class Fake:
            def insights(self,inputs,domain,panel=None,take=20):return rows(domain,flat=(len(inputs)==1 and domain=='videogame'))
        tv=next(e for e in CATALOG if e['alias']=='severance')
        movie={'id':'movie','name':'Movie','type':'movie'}
        with self.assertRaises(QlooError):build(Fake(),[tv,movie,ENT[1],TAG])

    def test_search_prioritizes_hobby_over_incidental_titles_and_filters_other_audiences(self):
        class Fake:
            def get(self,route,params):
                if route=='/v2/audiences':return {'results':{'audiences':[
                    {'id':AUD['id'],'name':'Running','type':HOBBIES},
                    {'id':'urn:audience:life_stage:x','name':'Running','type':'urn:audience:life_stage'}]}}
                if route=='/v2/tags':return {'results':{'tags':[{'id':TAG['id'],'type':TAG['taxonomy'],'name':'Architecture','parents':[{'type':'urn:entity:book'}]}]}}
                return {'results':[{'entity_id':'11111111-1111-1111-1111-111111111111','name':'Running','types':['urn:entity:book']}]}
        with patch.object(server,'CLIENT',Fake()),patch.dict(server.REGISTRY),patch.dict(server.DISCOVERED):
            r=server.search_interests('Running','')['results']
            self.assertEqual(r[0]['id'],AUD['id']);self.assertEqual(len(r),3)
            self.assertTrue(any(e['type']=='book' for e in r))

    def test_partial_lookup_failure_is_visible_and_does_not_destroy_good_results(self):
        class Fake:
            def get(self,route,params):
                if route!='/search':raise QlooError('Network unavailable')
                return {'results':[{'entity_id':ENT[0]['id'],'name':'Radiohead','types':['urn:entity:artist']}]}
        with patch.object(server,'CLIENT',Fake()),patch.dict(server.REGISTRY):
            result=server.search_interests('Radiohead','')
            self.assertEqual(len(result['results']),1);self.assertEqual(len(result['notices']),2)

    def test_pilates_lookup_never_injects_a_broader_interest(self):
        class Empty:
            def get(self,*args):return {'results':{}}
        with patch.object(server,'CLIENT',Empty()):
            result=server.search_interests('Pilates','')
            self.assertEqual(result['results'],[]);self.assertIn('flat recommendations',result['notices'][0])

    def test_real_flat_pilates_and_weightlifting_captures(self):
        file=ROOT/'research/prototype/activity-signals/coverage.json'
        self.assertTrue(file.is_file(), 'Archived coverage must ship with the checkout')
        captures=json.loads(file.read_text())
        for case in captures:
            if 'pilates' in case['id'] or 'weightlifting' in case['id']:
                self.assertTrue(all(x['distinct_scores']==1 for x in case['domains'].values()))

if __name__=='__main__':unittest.main()
