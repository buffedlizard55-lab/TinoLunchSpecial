#!/usr/bin/env python3
"""Pass-8 master fix-ups found while verifying batch8 (2026-09-08):
 - L121 Shan Restaurant (20007 Stevens Creek) is marked CLOSED on Yelp; the space is now Kabab & Curry's.
 - L268 Little India Cafe (415 N Mary Ste 101) now trades as Desi Dhaba (same Yelp listing/phone).
"""
import json, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,'data')
m=json.load(open(os.path.join(D,'lunch_specials.json')))
r=json.load(open(os.path.join(D,'lunch_rejected.json')))
DAY='2026-09-08'
for e in m['entries']:
    if e['id']=='L121':
        e.update({
          'name':"Kabab & Curry's (formerly Shan Restaurant)",'cuisine':'Indian / Pakistani',
          'days_open':'Tue-Sun lunch & dinner; closed Mon',
          'hours_tuesday':'11:30 AM - 2:30 PM, 5:00 PM - 9:30 PM','open_on_trip_date':True,
          'lunch_special':{'name':'Lunch platter (weekday)','price_from':None,'price_to':None,'days':'Tue-Fri','window':'11:30 AM - 2:30 PM','includes':None},
          'phone':'(669) 230-3993',
          'review_links':{'yelp':'https://www.yelp.com/biz/kabab-and-currys-cupertino','google_maps':'https://www.google.com/maps/search/?api=1&query=Kabab+%26+Curry%27s+20007+Stevens+Creek+Blvd+Cupertino'},
        })
        e['flags']=['REPLACED (pass 8): Shan Restaurant at this address is marked CLOSED on Yelp; row now describes Kabab & Curry\'s, the current tenant.','Lunch price not printed by any checked source - confirm on arrival.','Official menu is posted as images only.']
        e['verification']={'level':'review','accessed':DAY,'sources':[
          {'label':"Yelp - Kabab & Curry's Cupertino (20007 Stevens Creek; closed Mon; lunch Tue-Thu 11:30-2:30, Fri-Sun 11:30-3)",'url':'https://www.yelp.com/biz/kabab-and-currys-cupertino'},
          {'label':'Yelp - Shan (marked CLOSED)','url':'https://www.yelp.com/biz/shan-cupertino'},
          {'label':'Official site (image-only menu)','url':'https://www.kababandcurrys.com/'}]}
    if e['id']=='L268':
        e['name']='Desi Dhaba (formerly Little India Cafe)'
        e['days_open']='Mon-Sat lunch & dinner; Sun dinner only (Yelp snapshots also show Sun closed)'
        e['hours_tuesday']='11:00 AM - 2:30 PM, 4:30 PM - 9:00 PM'
        e['lunch_special']['name']='Weekday lunch buffet (availability conflicted)'
        e['lunch_special']['price_from']=16.99
        e['lunch_special']['includes']='CONFLICT: Yelp Q&A answer "weekday buffet, $16.99" vs "no buffet at the moment". Call (408) 245-6200 to confirm.'
        e['flags']=['RENAMED (pass 8): the Yelp listing at this address now trades as Desi Dhaba (same phone); hours updated.','IRREGULARITY: Yelp Q&A answers contradict each other on whether the lunch buffet still runs ($16.99 is a Q&A figure, not a menu price).']
        e['review_links']['yelp']='https://www.yelp.com/biz/desi-dhaba-sunnyvale-2'
        e['verification']['accessed']=DAY
        e['verification']['sources'].insert(0,{'label':'Yelp - Desi Dhaba (415 N Mary Ave Ste 101; Mon-Sat 10/11-2:30 & 4:30-9; buffet Q&A conflict)','url':'https://www.yelp.com/biz/desi-dhaba-sunnyvale-2'})
keep=r['rejected']  # Yokohama / Sushi Confidential rejections are superseded by merge_incoming (supersedes_rejection)
json.dump(m,open(os.path.join(D,'lunch_specials.json'),'w'),indent=2,ensure_ascii=False); open(os.path.join(D,'lunch_specials.json'),'a').write('\n')
json.dump(r,open(os.path.join(D,'lunch_rejected.json'),'w'),indent=2,ensure_ascii=False); open(os.path.join(D,'lunch_rejected.json'),'a').write('\n')
print('fixups applied; rejected now',len(keep))
