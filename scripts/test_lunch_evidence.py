#!/usr/bin/env python3
"""Tests for fail-closed promotion and evidence completeness; no network needed."""
import copy
import json
from pathlib import Path
import unittest
from lunch_evidence import evidence_errors, promotion_ready

ROOT=Path(__file__).resolve().parents[1]
class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.entries=json.loads((ROOT/'data/lunch_specials.json').read_text())['entries']
        self.entry=copy.deepcopy(next(e for e in self.entries if e['id']=='L01'))
    def test_complete_record(self):
        self.assertTrue(promotion_ready(self.entry))
    def test_legacy_official_is_not_verification(self):
        del self.entry['deal_audit']
        self.assertFalse(promotion_ready(self.entry))
    def test_unknown_schedule_blocks_promotion(self):
        self.entry['deal_audit']['fields']['schedule']['status']='unknown'
        self.assertFalse(promotion_ready(self.entry))
    def test_search_or_review_not_primary(self):
        self.entry['deal_audit']['fields']['price']['source_type']='search_extract'
        self.assertFalse(promotion_ready(self.entry))
    def test_missing_quote(self):
        del self.entry['deal_audit']['fields']['price']['quote']
        self.assertFalse(promotion_ready(self.entry))
    def test_unregistered_source(self):
        self.entry['deal_audit']['fields']['price']['source_url']='https://example.com/'
        self.assertFalse(promotion_ready(self.entry))
    def test_missing_price(self):
        self.entry['lunch_special']['price_from']=None
        self.assertFalse(promotion_ready(self.entry))
    def test_partial_not_promoted(self):
        for id in ['L184','L76','L03','L12','L104','L896']:
            e=next(e for e in self.entries if e['id']==id)
            self.assertEqual(evidence_errors(e),[])
            self.assertFalse(promotion_ready(e))
    def test_every_audit_valid(self):
        audited=[e for e in self.entries if e.get('deal_audit')]
        self.assertEqual(len(audited),11)
        self.assertEqual(sum(map(promotion_ready,audited)),5)
        for e in audited:self.assertEqual(evidence_errors(e),[],e['id'])
    def test_duplicates_stay_removed(self):
        self.assertFalse({'L649','L650','L676','L678','L679','L681','L815'} & {e['id'] for e in self.entries})
        for e in self.entries:
            self.assertNotIn(e['name'],['Sushi Roku Palo Alto Verified','Lotus Thai Bistro Palo Alto Official'])
    def test_no_fictional_bulk_success(self):
        screen=json.loads((ROOT/'data/research/pass24_screen.json').read_text())
        self.assertEqual(len(screen['rows']),100)
        self.assertEqual(len({r['url'] for r in screen['rows']}),100)
        self.assertTrue(all(r['decision']=='not_promoted_automated_screen_only' for r in screen['rows']))

    def test_pass25_duplicate_queue_recorded(self):
        q=json.loads((ROOT/'data/research/pass25_duplicate_queue.json').read_text())
        self.assertEqual(len(q['queue']),25)
        self.assertEqual(len(q['resolved_this_pass']),5)
        self.assertTrue(all('queued' in p['status'] for p in q['queue']))
    def test_pass25_search_log_counts(self):
        log=json.loads((ROOT/'data/research/pass25_search_log.json').read_text())
        self.assertEqual(log['totals']['queries_executed'],len(log['queries']))
        self.assertEqual(log['totals']['duplicate_rows_removed_with_proof'],5)
        self.assertEqual(log['totals']['new_businesses_with_a_published_priced_lunch_special'],1)

if __name__=='__main__':unittest.main()
