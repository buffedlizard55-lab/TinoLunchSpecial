#!/usr/bin/env python3
"""Build a no-JavaScript research page and field-level evidence CSV, deterministically."""
import csv
from html import escape
import json
from pathlib import Path
from lunch_evidence import evidence_errors

ROOT = Path(__file__).resolve().parents[1]
def load(name): return json.loads((ROOT/name).read_text())
def esc(value): return escape(str(value), quote=True)
def link(url, label): return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
def table(headers, rows):
    return '<div class="scrollpanel" tabindex="0" role="region" aria-label="'+esc(headers[0])+' table"><table class="grid-table evidence-table"><thead><tr>'+''.join('<th scope="col">'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def main():
    entries=load('data/lunch_specials.json')['entries']
    audited=[e for e in entries if e.get('deal_audit')]
    for entry in audited:
        assert not evidence_errors(entry), (entry['id'],evidence_errors(entry))
    discovery=load('data/research/pass24_discovery.json')
    screen=load('data/research/pass24_screen.json')
    assert len(screen['rows'])==100 and len({r['sequence'] for r in screen['rows']})==100
    assert len(discovery['queries'])==20
    complete=sum(e['deal_audit']['status']=='complete' for e in audited)
    parts=['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Lunch research & evidence | Tino Lunch Special</title><link rel="stylesheet" href="assets/styles.css"></head><body class="research-page"><header class="site-header"><div class="wrap"><nav class="pagebar" aria-label="Main"><a href="index.html" class="brandmark">Tino Lunch Special</a><span class="spacer"></span><a class="pagelink" href="index.html">Lunch specials</a><span class="pagelink is-active" aria-current="page">Research & evidence</span><a class="pagelink" href="transit.html">Trip & transit plan</a></nav><h1>Evidence before entries.</h1><p class="sub">September 17, 2026 · Cupertino first, then nearby cities · Pass 24</p></div></header><main class="wrap"><div class="research-notice"><strong>The 100-new-restaurant goal is not complete.</strong><p>20 discovery queries; 100 existing-source bulk attempts at checkpoints 20 → 50 → 100, all failed at the network/TLS layer. Targeted page-reader checks recovered useful evidence. Failed requests, duplicate hits and ordinary lunch service are never counted as new verified restaurants.</p></div>''']
    parts.append(f'<p><strong>{complete} complete field audits · {len(audited)-complete} partial field audits · 0 new businesses · 2 duplicates consolidated.</strong> Research archive: {len(entries)} rows, not {len(entries)} verified lunch deals.</p>')
    parts.append('<p><a href="data/research/pass24_evidence.csv" download>Download evidence CSV</a> · <a href="data/research/pass24_screen.json">Bulk attempt log (JSON)</a> · <a href="data/research/pass24_discovery.json">Search log (JSON)</a></p>')
    parts.append('<section><h2>What, how much, and when?</h2><p>“Complete” means all five required fields were checked against primary sources. “Partial” rows remain outside the complete-deal view. A named lunch menu is eligible even if no discount is claimed. Prices exclude tax/tip; exceptions and card fees are recorded. Source excerpts may join adjacent menu lines; they are not full-page snapshots.</p>')
    rows=[]
    for e in audited:
        a=e['deal_audit'];ls=e['lunch_special'];f=a['fields']
        rows.append([esc(e['id']+' · '+e['name']),esc(e['city']+' — '+e['address']),esc(a['status']),esc(ls['name']),esc(f['price']['value']+'; '+a['price_basis']),esc(f['schedule']['value']),esc(f['hours']['value']),link(f['price']['source_url'],'Official price/menu')+'<p>'+esc(a['notes'])+'</p>'])
    parts.append(table(['Restaurant','Location','Audit','Offer','Price','Lunch schedule','Business hours','Source & limitations'],rows)+'</section>')
    parts.append('<section><h2>Field-by-field evidence</h2>')
    csvrows=[]
    for e in audited:
        a=e['deal_audit'];parts.append('<details><summary>'+esc(e['id']+' · '+e['name'])+'</summary>');rows=[]
        for key,f in a['fields'].items():
            rows.append([esc(key),esc(f['status']),esc(f['value']),esc(f.get('quote','Not captured')),link(f['source_url'],'Primary source') if f.get('source_url') else 'Unresolved'])
            csvrows.append([e['id'],e['name'],e['city'],a['checked_on'],a['status'],key,f['status'],f['value'],f.get('quote',''),f.get('source_url','')])
        parts.append(table(['Field','Status','Value','Evidence excerpt','Source'],rows)+'</details>')
    parts.append('</section><section><h2>20 discovery queries</h2><p>Result links below are for review. An outcome labeled excluded or unresolved is not an accepted deal.</p>')
    parts.append(table(['Query','Observed outcome','Result link'],[[esc(q['query']),esc(q['outcome']),link(q['url'],'Review result')] for q in discovery['queries']])+'</section>')
    parts.append('<section><h2>100-source retry queue</h2><p>Existing restaurant URLs, not new entries. A network failure says nothing about whether a restaurant is open or a special exists. The separate page-reader tool successfully read some of these URLs; it did not turn the failed bulk run into 100 successful checks.</p>')
    parts.append(table(['Checkpoint','Attempts','Failed','Promotions'],[[str(n),str(n),str(sum(r['result']=='fetch_failed' for r in screen['rows'][:n])),'0'] for n in [20,50,100]]))
    parts.append('<details><summary>Show all 100 source attempts</summary>'+table(['# / existing ID','Restaurant','City','Result','Requested URL'],[[str(r['sequence'])+' / '+esc(r['existing_id']),esc(r['name']),esc(r['city']),esc(r['result']+' — '+r.get('error','')),link(r['url'],'Retry official/source page')] for r in screen['rows']])+'</details></section>')
    parts.append('<section><h2>Next-session work</h2><ol>'+''.join('<li>'+esc(t)+'</li>' for t in discovery['follow_up'])+'</ol><p>Automated validation checks recorded structure and provenance; it cannot prove restaurant truth or guarantee future availability. No claim is made that every historical row was reverified this session.</p></section></main><footer class="site-footer"><div class="wrap"><a href="index.html">Back to lunch specials</a></div></footer></body></html>')
    (ROOT/'research.html').write_text('\n'.join(parts)+'\n')
    with (ROOT/'data/research/pass24_evidence.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['id','name','city','checked_on','audit','field','status','value','excerpt','source_url']);writer.writerows(csvrows)
    print(f'Built research.html and {len(csvrows)} field-evidence CSV rows')

if __name__=='__main__':main()
