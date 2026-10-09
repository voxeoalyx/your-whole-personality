import hashlib
import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scoring import ranks,distance,sensitivity
from game import CATALOG,build,pick_domains
from qloo_client import ROOT,QlooError,unsupported,environment


class ScoringTests(unittest.TestCase):
    def test_ties_and_reversal(self):
        self.assertEqual(ranks([10,10,20,30]),[1.5,1.5,3,4])
        a={str(i):i for i in range(10)}
        self.assertEqual(distance(a,a,list(a)),0)
        self.assertEqual(distance(a,{k:9-v for k,v in a.items()},list(a)),1)

    def test_missing_and_flat_are_undefined(self):
        a={str(i):i for i in range(10)}
        self.assertIsNone(distance(a,{},list(a)))
        self.assertIsNone(distance(a,{k:1 for k in a},list(a)))

    def test_dominance_requires_two_complete_domains_and_halves(self):
        es=[{'id':'a','name':'A'},{'id':'b','name':'B'},{'id':'c','name':'C'}]
        rows=[{'id':str(i),'score':i} for i in range(20)]
        reverse=[{'id':str(i),'score':19-i} for i in range(20)]
        full={'movie':rows,'brand':rows}; ab={x['id']:{'movie':rows,'brand':rows} for x in es}
        ab['a']={'movie':reverse,'brand':reverse}
        self.assertEqual(sensitivity(es,full,ab)['winner']['id'],'a')
        ab['b']['brand']=rows[:-1]
        self.assertIsNone(sensitivity(es,full,ab)['winner'])
        self.assertEqual(sensitivity(es,full,ab)['status'],'incomplete')

    def test_tied_influences_have_no_winner(self):
        es=[{'id':'a','name':'A'},{'id':'b','name':'B'}]; rows=[{'id':str(i),'score':i} for i in range(20)]
        rev=[{'id':str(i),'score':19-i} for i in range(20)]
        self.assertIsNone(sensitivity(es,{'movie':rows,'brand':rows},{x['id']:{'movie':rev,'brand':rev} for x in es})['winner'])

    def test_domains_are_held_out(self):
        es=[e for e in CATALOG if e['alias'] in ['radiohead','blue_bottle','severance']]
        self.assertEqual(pick_domains(es),['movie','videogame'])
        self.assertFalse(set(pick_domains(es)) & {e['type'] for e in es})

    def test_actual_unsupported_warning(self):
        research=ROOT/'research/civilizr-research/whole-personality/runs/04_matrix/single_dune_brand.a1.json'
        self.assertTrue(research.is_file(), 'Archived research response must ship with the checkout')
        data=json.loads(research.read_text(encoding='utf-8')); self.assertIn(next(e['id'] for e in CATALOG if e['alias']=='dune'),unsupported(data))
        self.assertEqual(unsupported({'warnings':[{'type':'not_found','signal.interests.entities':['dune']}]}),['dune'])

    def test_incomplete_game_never_names_winner(self):
        class Fake:
            def insights(self,ids,domain,panel=None,take=20):
                rows=[{'id':str(i),'name':'Entity '+str(i),'type':domain,'score':i} for i in range(20)]
                return rows[:-1] if panel and len(ids)==2 else rows
        es=[e for e in CATALOG if e['alias'] in ['radiohead','blue_bottle','severance']]
        g=build(Fake(),es)
        self.assertEqual(g['sensitivity']['status'],'incomplete');self.assertIsNone(g['sensitivity']['winner'])

    def test_partial_baseline_fails_before_guesses(self):
        class Fake:
            def insights(self,ids,domain,panel=None,take=20):
                return [{'id':str(i),'score':i} for i in range(19 if panel else 20)]
        with self.assertRaises(QlooError): build(Fake(),CATALOG[:3])

    def test_three_recordings_trace_to_raw_and_recompute(self):
        demos=json.loads((ROOT/'data/demos.json').read_text(encoding='utf-8'))
        self.assertEqual(len(demos),3)
        archived={}
        for p in (ROOT/'research/prototype/verification').glob('*.meta.json'):
            m=json.loads(p.read_text());raw=p.with_name(p.name.replace('.meta.json','.json'))
            self.assertEqual(hashlib.sha256(raw.read_bytes()).hexdigest(),m['response_sha256'])
            archived[m['request_hash']]=json.loads(raw.read_bytes())
        self.assertEqual(len(archived),30)
        for demo in demos.values():
            self.assertEqual(demo['sensitivity'],sensitivity(demo['interests'],demo['full'],demo['ablations']))
            self.assertEqual(len(demo['predictions']),6)
            self.assertFalse(set(demo['domains']) & {e['type'] for e in demo['interests']})
            if archived:
                for p in demo['predictions']:
                    found=[x for h in demo['provenance']['request_hashes'] for x in archived.get(h,{}).get('results',{}).get('entities',[]) if x.get('entity_id')==p['id'] and x.get('query',{}).get('affinity')==p['score']]
                    self.assertTrue(any(x['name']==p['name'] for x in found),p['name'])

    def test_no_active_key_in_deliverables(self):
        key=environment()['QLOO_API_KEY']
        if not key: self.skipTest('No key configured for exact-value scan')
        for directory in ['static','data','tests']:
            for file in (ROOT/directory).rglob('*'):
                if file.is_file() and '__pycache__' not in file.parts:self.assertNotIn(key.encode(),file.read_bytes(),str(file))

if __name__=='__main__':unittest.main()
