#!/usr/bin/env python3
"""Non-promoting source screen. Network retrieval is NOT factual verification.
Run explicitly; never in CI. Preserves compact provenance, not full third-party pages.
"""
import concurrent.futures
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.skip = max(0, self.skip - 1)
    def handle_data(self, text):
        if not self.skip: self.parts.append(text)

def screen(row):
    row = dict(row)
    try:
        req = Request(row['url'], headers={'User-Agent': 'TinoLunchSpecial-source-audit/1.0'})
        with urlopen(req, timeout=20) as response:
            raw = response.read(2_000_000)
            row.update(http_status=response.status, final_url=response.url,
                       content_type=response.headers.get('Content-Type', ''),
                       response_sha256=hashlib.sha256(raw).hexdigest())
        if 'html' not in row['content_type']:
            row.update(result='non_html_needs_review', excerpts=[])
        else:
            parser = Text(); parser.feed(raw.decode('utf-8', errors='replace'))
            text = re.sub(r'\s+', ' ', ' '.join(parser.parts)).strip()
            matches = list(re.finditer(r'\blunch\b|\bmidday\b|\bprix fixe\b', text, re.I))
            row['excerpts'] = [text[max(0,m.start()-60):m.end()+230] for m in matches[:3]]
            row['result'] = 'lunch_text_needs_review' if matches else 'no_lunch_text_extracted'
            row['text_length'] = len(text)
    except Exception as exc:
        row.update(result='fetch_failed', error=str(exc)[:240], excerpts=[])
    row['decision'] = 'not_promoted_automated_screen_only'
    return row

def main():
    targets = json.loads((ROOT/'data/research/pass24_targets.json').read_text())
    rows = []
    # Real sequential checkpoints: first 20, then 50, then 100 target pages.
    for start, end in [(0,20),(20,50),(50,100)]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            rows.extend(pool.map(screen, targets[start:end]))
        payload = {'checked_on':'2026-09-17', 'method':'Automated HTTP/text screening of existing restaurant source URLs. NOT 100 new restaurants or line-by-line factual verification.',
                   'checkpoint':end, 'rows':rows}
        (ROOT/'data/research/pass24_screen.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n')
        print(f'Checkpoint {end}: {len(rows)} source screens; zero automatic promotions', flush=True)

if __name__ == '__main__': main()
