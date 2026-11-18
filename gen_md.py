#!/usr/bin/env python3
"""Writes verona-vo-schedule.md from verona-vo-schedule.json."""
import json,datetime,os,sys
P=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(P,'verona-vo-schedule.json')))
S=d['screenings']; F=d['films']; T=d['theaters']
TODAY=datetime.date.fromisoformat(d['built_at'][:10])
WD=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
MO=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def fd(s):
    dt=datetime.date.fromisoformat(s); return f"{WD[dt.weekday()]} {dt.day} {MO[dt.month-1]}"
def langs(s):
    a=s['audio']; sub=s['subs']
    return f"{a} audio / {'no subs' if sub=='none' else sub+' subs'}"
def title(s):
    o=s.get('film_original') or F.get(s['film_key'],{}).get('film_original') or ''
    return f"{s['film_it']} ({o})" if o and o.lower()!=s['film_it'].lower() else s['film_it']
def links(s):
    out=[]
    if s.get('ticket_url'): out.append(f"[tickets]({s['ticket_url']})")
    if s.get('calendar_url'): out.append(f"[+calendar]({s['calendar_url']})")
    return ' '.join(out)
def table(rows,newcol=False):
    if not rows: return "_none_\n"
    h="| Date | Time | Film | Cinema | Audio / Subs | Links |"
    sep="|---|---|---|---|---|---|"
    if newcol: h=h[:-1]+" NEW |"; sep=sep+"---|"
    L=[h,sep]
    for s in rows:
        c=f"| {fd(s['date'])} | {s['time']} | {title(s)} | {s['cinema']} | {langs(s)} | {links(s)} |"
        if newcol: c+=(" NEW |" if s.get('is_new') else "  |")
        L.append(c)
    return '\n'.join(L)+'\n'

CAT=[('english_audio','English audio'),('english_subs','English subtitles'),('spanish','Spanish')]
out=[]
out.append(f"# Verona original-language screenings — updated {d['built_at'][:10]} {d['built_at'][11:16]} (Europe/Rome)\n")
out.append(f"{len(S)} qualifying showtimes across {len({s['cinema'] for s in S})} of the {len(T)} cinemas tracked.\n")

wk=[s for s in S if s['date']<=(TODAY+datetime.timedelta(days=7)).isoformat()]
out.append("## Next 7 days\n"); out.append(table(wk,newcol=True))

out.append("\n## Full schedule\n")
for key,label in CAT:
    rows=[s for s in S if s['category']==key]
    out.append(f"### {label}\n"); out.append(table(rows,newcol=True))

oth=[s for s in S if s['category']=='other']
out.append("\n## Other original-version\n")
if oth:
    for s in oth:
        out.append(f"- {fd(s['date'])} {s['time']} — {title(s)}, {s['cinema']} ({langs(s)}) {links(s)}")
    out.append("")
else: out.append("_none_\n")

out.append("\n## Removed since last run\n")
out.append("_first run — nothing to compare against_\n" if not d.get('previous_run') else
           ('\n'.join(f"- {r}" for r in d['removed_since_last_run']) or "_none_\n"))

out.append("\n## Cinemas\n")
for n,t in T.items():
    import urllib.parse
    q=urllib.parse.quote_plus(f"{n}, {t['address']}")
    out.append(f"- **{n}** — {t['address']}"+(f" · tel {t['phone']}" if t.get('phone') else "")+
               f" · [map](https://www.google.com/maps/search/?api=1&query={q})"
               f" · [directions](https://www.google.com/maps/dir/?api=1&destination={q})"
               f" · {t['booking_note']}")

out.append("\n## Sources & coverage\n")
for u,s in d['sources'].items():
    md=f", missing dates: {', '.join(s['missing_dates'])}" if s.get('missing_dates') else ""
    out.append(f"- {s['cinema']} — {s['status']}, covered {s['dates_covered']}{md}  \n  <{u}>")
out.append("\nUCI: films start about 25 minutes after the printed time (about 15 for alternative-content events).")
out.append("\nThe Cinema Fiume group marks original-version slots with `*` and does not state the audio language; "
           "audio is inferred from the film's production country and director, and every showtime records how.\n")
open(os.path.join(P,'verona-vo-schedule.md'),'w').write('\n'.join(out))
print("wrote verona-vo-schedule.md")
