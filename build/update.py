#!/usr/bin/env python3
"""
Rebuilds the Verona original-language schedule end to end.

  python3 build/update.py            # full refresh
  python3 build/update.py --no-fetch # rebuild from the cached raw scrape

Sources (the cinemas' own listings only -- never aggregators):
  * Cinema Fiume group  : static HTML, one page per cinema.
                          VO is marked per showtime with '*'; subtitles are Italian;
                          the page never states the audio language.
  * UCI Cinemas Verona  : JSON API discovered 2026-11-18, see README.
                          https://backend.ucicinemas.it/api/theatres/<slug>/programming/<YYYY-MM-DD>
                          Each version carries language.name + subtitles.name.
                          NOTE: www.ucicinemas.it itself sits behind a Queue-it waiting room
                          and cannot be curled; the backend API can.
"""
import json,os,re,sys,html,glob,datetime,urllib.parse,subprocess,collections

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(ROOT,'build','raw')
JSON_PATH=os.path.join(ROOT,'verona-vo-schedule.json')
FETCH='--no-fetch' not in sys.argv

TZ_LABEL='Europe/Rome'
NOW=datetime.datetime.now()
TODAY=NOW.date()

UCI_SLUG='uci-cinemas-verona'
UCI_API='https://backend.ucicinemas.it/api/theatres/{slug}/programming/{date}'
UCI_LEAD_MIN=25
FIUME={'cinema-kappadue':'Cinema Kappadue','cinema-diamante':'Cinema Diamante',
       'cinema-fiume':'Cinema Fiume','cinema-pindemonte':'Cinema Pindemonte'}
HORIZON=140  # days of UCI dates to probe

THEATERS={
 "UCI Cinemas Verona":{"address":"Via Monte Amiata, 37057 San Giovanni Lupatoto VR",
   "lat":"45.3966662","lon":"11.0164011","phone":None,
   "site":"https://www.ucicinemas.it/cinema/veneto/verona/uci-cinemas-verona/",
   "note":"Multiplex (IMAX / XL / 3D / 2D). Films start about 25 minutes after the printed time (about 15 for alternative-content events).",
   "online_tickets":True,"booking_note":"Tickets on sale online, per showtime."},
 "Cinema Kappadue":{"address":"Via Antonio Rosmini 1, 37123 Verona","phone":"045 8005895",
   "site":"https://cinemafiume.it/cinema/cinema-kappadue/",
   "note":"Original-version slots are marked with * on the cinema's own programme; subtitles are Italian.",
   "online_tickets":False,"booking_note":"No online ticketing — box office only."},
 "Cinema Diamante":{"address":"Via Pietro Zecchinato 5, 37136 Verona","phone":"045 509911",
   "site":"https://cinemafiume.it/cinema/cinema-diamante/",
   "note":"Original-version slots are marked with * on the cinema's own programme; subtitles are Italian.",
   "online_tickets":False,"booking_note":"No online ticketing — box office only."},
 "Cinema Fiume":{"address":"Vicolo Cere 14, 37123 Verona","phone":"045 8002050",
   "site":"https://cinemafiume.it/cinema/cinema-fiume/",
   "note":"Part of the Cinema Fiume group; original-version slots would be marked with *.",
   "online_tickets":False,"booking_note":"No online ticketing — box office only."},
 "Cinema Pindemonte":{"address":"Via Sabotino 2/b, 37123 Verona","phone":"045 913591",
   "site":"https://cinemafiume.it/cinema/cinema-pindemonte/",
   "note":"Part of the Cinema Fiume group; original-version slots would be marked with *.",
   "online_tickets":False,"booking_note":"No online ticketing — box office only."},
}

MONTHS={'gennaio':1,'febbraio':2,'marzo':3,'aprile':4,'maggio':5,'giugno':6,'luglio':7,
        'agosto':8,'settembre':9,'ottobre':10,'novembre':11,'dicembre':12}
DOW=r'(?:luned|marted|mercoled|gioved|venerd|sabato|domenica)'
LANGMAP={'ENG':'EN','KOR':'KO','JP':'JA','JPN':'JA','ESP':'ES','SPA':'ES','FRA':'FR','FRE':'FR','ITA':'IT','GER':'DE','DEU':'DE'}
# Not language markers -- accessibility/technical screening types, Italian audio.
NON_LANGUAGE={'ITA','AUTISM FRIENDLY'}
# The Fiume group prints titles in ALL CAPS; these are the films' own printed titles.
DISPLAY_TITLE={"WILD HORSE NINE":"Wild Horse Nine","LOOK BACK":"Look Back",
               "L'ESSERE AMATO":"L'essere amato","RAGIONE E SENTIMENTO":"Ragione e sentimento"}

def log(*a): print(*a,flush=True)

# ---------------------------------------------------------------- fetching
def fetch():
    os.makedirs(RAW,exist_ok=True); os.makedirs(os.path.join(RAW,'uci'),exist_ok=True)
    for slug in FIUME:
        out=os.path.join(RAW,slug+'.html')
        subprocess.run(['curl','-sL','--max-time','60','-o',out,
                        f'https://cinemafiume.it/cinema/{slug}/'],check=False)
        log(f"  fiume  {slug:20s} {os.path.getsize(out) if os.path.exists(out) else 0} bytes")
    for old in glob.glob(os.path.join(RAW,'uci','*.json')): os.remove(old)
    dates=[(TODAY+datetime.timedelta(days=i)).isoformat() for i in range(HORIZON)]
    CHUNK=25  # dates per curl process; each date contributes an -o/path/url triple
    for i in range(0,len(dates),CHUNK):
        args=[]
        for d in dates[i:i+CHUNK]:
            args+=['-o',os.path.join(RAW,'uci',d+'.json'),UCI_API.format(slug=UCI_SLUG,date=d)]
        subprocess.run(['curl','-s','--max-time','120']+args,check=False)
    got=len(glob.glob(os.path.join(RAW,'uci','*.json')))
    log(f"  uci    {got}/{len(dates)} day files")

# ---------------------------------------------------------------- Fiume parsing
def fiume_tokens(path):
    s=open(path,encoding='utf-8',errors='replace').read()
    pat=re.compile(r'<h(\d) class="elementor-heading-title[^"]*">(.*?)</h\1>'
                   r'|<div class="jet-listing-dynamic-field__content"[^>]*>(.*?)</div>',re.S)
    toks=[]
    for m in pat.finditer(s):
        raw=m.group(2) if m.group(2) is not None else m.group(3)
        toks.append(html.unescape(re.sub(r'<[^>]+>','',raw)).strip())
    posters=[m.group(1) for m in re.finditer(
        r'(?:src|data-src)="(https://cinemafiume\.it/wp-content/uploads/(?!elementor/thumbs)[^"]*locandina[^"]*)"',s)]
    return toks,posters,('Proiezione in versione originale' in s)

def it_date(tok):
    m=re.match(r'^'+DOW+r'\S*\s+(\d{1,2})\s+([A-Za-zÀ-ÿ]+)\s*$',tok,re.I)
    if not m: return None
    mon=MONTHS.get(m.group(2).lower())
    if not mon: return None
    # the programme runs forward from today; a month earlier than this one belongs to next year
    year=TODAY.year if mon>=TODAY.month else TODAY.year+1
    return f"{year}-{mon:02d}-{int(m.group(1)):02d}"

def parse_fiume():
    out={}
    for slug,name in FIUME.items():
        p=os.path.join(RAW,slug+'.html')
        if not os.path.exists(p) or os.path.getsize(p)<5000:
            out[name]={'status':'failed','films':[],'has_vo_note':False}; continue
        toks,posters,note=fiume_tokens(p); films=[]; pi=0
        for i,t in enumerate(toks):
            if not t.startswith('Regia :'): continue
            title=toks[i-2]
            get=lambda k: next((x.split(':',1)[1].strip() for x in toks[i:i+5] if x.startswith(k)),'')
            j=i
            while j<len(toks) and toks[j]!='Programmazione:': j+=1
            shows=[]; j+=1; cur=None
            while j<len(toks):
                tk=toks[j]; d=it_date(tk)
                if d: cur=d; j+=1; continue
                if cur and re.match(r'^[\d\s:|*\.]+$',tk) and re.search(r'\d{1,2}[:\.]\d{2}',tk):
                    for part in tk.split('|'):
                        mm=re.match(r'^(\d{1,2})[:\.](\d{2})(\*?)$',part.strip())
                        if mm: shows.append({'date':cur,'time':f"{int(mm.group(1)):02d}:{mm.group(2)}",
                                             'vo':mm.group(3)=='*','marker':part.strip()})
                    j+=1; continue
                break
            films.append({'title':title,'director':t.split(':',1)[1].strip(),
                          'production':get('Produzione'),'cast':get('Cast'),'durata':get('Durata'),
                          'poster':posters[pi] if pi<len(posters) else None,'shows':shows})
            pi+=1
        out[name]={'status':'ok','films':films,'has_vo_note':note}
    return out

# ---------------------------------------------------------------- UCI parsing
def parse_uci():
    rows=[];posters={};probed=[]
    for f in sorted(glob.glob(os.path.join(RAW,'uci','*.json'))):
        day=os.path.basename(f)[:-5]; probed.append(day)
        try: d=json.load(open(f))
        except Exception: continue
        for mv in (d.get('data') or []):
            if mv.get('poster'):
                posters[mv['slug']]={'poster':mv['poster'],
                    'genres':[g['name'] for g in (mv.get('genres') or [])],
                    'description':html.unescape(re.sub(r'<[^>]+>',' ',mv.get('description') or '')).strip(),
                    'rating':(mv.get('rating') or {}).get('name')}
                posters[mv['slug']]['description']=re.sub(r'\s+',' ',posters[mv['slug']]['description'])
            for scr in (mv.get('screens') or []):
                for scrname,items in scr.items():
                    for it in items:
                        lang=((it.get('language') or {}).get('name') or '').strip()
                        sb=it.get('subtitles')
                        subs=(sb.get('name') or '').strip() if isinstance(sb,dict) else (sb or '').strip()
                        for p in (it.get('performances') or []):
                            if p.get('day')!=day: continue
                            rows.append({'date':day,'time':p.get('actual_start_at') or (p.get('starts_at') or '')[11:16],
                                'title':html.unescape(mv['title']),'slug':mv['slug'],'screen':scrname,'room':p.get('room'),
                                'lang':lang,'subs':subs,'price':p.get('price_starting_from'),
                                'perf_minutes':p.get('duration'),'cart_link':p.get('cart_link'),
                                'ends_at':p.get('ends_at')})
    return rows,posters,probed

# ---------------------------------------------------------------- shared
def split_title(t):
    m=re.match(r'^(.*?)\s*\((.+)\)\s*$',t)
    return (m.group(1).strip(),m.group(2).strip()) if m else (t.strip(),'')
def display(t): return DISPLAY_TITLE.get(t,t)
def fkey(t):
    import unicodedata
    return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',t.lower())
                  .encode('ascii','ignore').decode()).strip('-')
def category(audio,subs):
    if audio=='EN': return 'english_audio'
    if subs=='EN':  return 'english_subs'
    if audio=='ES': return 'spanish'
    return 'other'
def infer_audio(director,production):
    p=(production or '').lower()
    for keys,code in ((('giappone','japan'),'JA'),(('spagna','spain'),'ES'),
                      (('usa','g.b.','gran bretagna','u.k.','irlanda','australia','canada','nuova zelanda'),'EN'),
                      (('francia',),'FR'),(('germania',),'DE'),(('corea',),'KO'),(('italia',),'IT')):
        if any(k in p for k in keys):
            return code,f"inferred: production {production}, director {director}"
    return '?',f"inferred: undetermined (production {production or 'unknown'})"
def plus_minutes(date,time,minutes):
    dt=datetime.datetime.strptime(f"{date} {time}",'%Y-%m-%d %H:%M')+datetime.timedelta(minutes=minutes or 120)
    return dt.strftime('%Y-%m-%d'),dt.strftime('%H:%M')
def gcal(title,cinema,date,time,end,details):
    q={'action':'TEMPLATE','text':f"{title} — {cinema}",
       'dates':f"{date.replace('-','')}T{time.replace(':','')}00/{end[0].replace('-','')}T{end[1].replace(':','')}00",
       'location':THEATERS[cinema]['address'],'details':details,'ctz':TZ_LABEL}
    return 'https://calendar.google.com/calendar/render?'+urllib.parse.urlencode(q)

# ---------------------------------------------------------------- build
def build():
    prev={}
    if os.path.exists(JSON_PATH):
        try: prev=json.load(open(JSON_PATH))
        except Exception: prev={}

    fi=parse_fiume(); urows,uposters,probed=parse_uci()
    screenings=[];films={}

    for r in urows:
        if r['lang'] in NON_LANGUAGE or not r['lang']: continue
        audio=LANGMAP.get(r['lang'],r['lang'])
        subs=LANGMAP.get(r['subs'],r['subs']) if r['subs'] else 'none'
        it,orig=split_title(r['title']); key=fkey(it)
        po=uposters.get(r['slug'],{})
        films.setdefault(key,{'film_it':it,'film_original':orig,'poster_url':po.get('poster'),
            'genres':po.get('genres') or [],'director':'','production':'',
            'synopsis':po.get('description',''),'rating':po.get('rating')})
        end=(r['ends_at'][:10],r['ends_at'][11:16]) if r.get('ends_at') else plus_minutes(r['date'],r['time'],r.get('perf_minutes'))
        screenings.append({'date':r['date'],'time':r['time'],'film_key':key,'film_it':it,'film_original':orig,
            'cinema':'UCI Cinemas Verona','audio':audio,'subs':subs,'category':category(audio,subs),
            'format':'' if r['screen']=='2D' else r['screen'],'room':r['room'],'price_from':r.get('price'),
            'marker':f"{r['lang']} / sottotitoli {r['subs']}" if r['subs'] else r['lang'],
            'lang_source':'badge','end_time':end[1],'runtime_min':r.get('perf_minutes'),
            'ticket_url':('https://www.ucicinemas.it'+r['cart_link']) if r.get('cart_link') else None,
            'calendar_url':gcal(it,'UCI Cinemas Verona',r['date'],r['time'],end,
              f"{audio} audio, {'subtitles '+subs if subs!='none' else 'no subtitles'}"
              f" — {r['screen']}, {r['room']}. Admission time {r['time']}; the film itself starts about "
              f"{UCI_LEAD_MIN} minutes later. Source: ucicinemas.it")})

    for cinema,c in fi.items():
        for f in c['films']:
            vo=[s for s in f['shows'] if s['vo']]
            if not vo: continue
            raw_it,orig=split_title(f['title']); it=display(raw_it); key=fkey(it)
            audio,src=infer_audio(f['director'],f['production'])
            fm=films.setdefault(key,{'film_it':it,'film_original':orig,'poster_url':f.get('poster'),
                'genres':[],'director':f['director'],'production':f['production'],'synopsis':'','rating':None})
            for fld,val in (('director',f['director']),('production',f['production']),
                            ('film_original',orig),('poster_url',f.get('poster'))):
                if not fm.get(fld) and val: fm[fld]=val
            dm=re.search(r'(\d+)',f.get('durata') or ''); mins=int(dm.group(1)) if dm else None
            for s in vo:
                end=plus_minutes(s['date'],s['time'],mins)
                screenings.append({'date':s['date'],'time':s['time'],'film_key':key,'film_it':it,
                    'film_original':orig,'cinema':cinema,'audio':audio,'subs':'IT',
                    'category':category(audio,'IT'),'format':'','room':None,'price_from':None,
                    'marker':s['marker'],'lang_source':src,'end_time':end[1],'runtime_min':mins,
                    'ticket_url':None,
                    'calendar_url':gcal(it,cinema,s['date'],s['time'],end,
                      f"Original version with Italian subtitles (marked {s['marker']} on the programme). "
                      f"Audio language {audio} ({src}). No online ticketing — box office only. Source: cinemafiume.it")})

    screenings=[s for s in screenings if s['date']>=TODAY.isoformat()]
    screenings.sort(key=lambda s:(s['date'],s['time'],s['cinema'],s['film_it']))

    # ---- diff against the previous run
    def ident(s): return (s['film_it'],s['cinema'],s['date'],s['time'])
    old={ident(s):s for s in (prev.get('screenings') or [])}
    new_count=0
    for s in screenings:
        o=old.get(ident(s))
        if o:
            s['first_seen']=o.get('first_seen',TODAY.isoformat()); s['is_new']=False
        else:
            s['first_seen']=TODAY.isoformat(); s['is_new']=bool(prev); new_count+=bool(prev)
    cur=set(map(ident,screenings))
    removed=[{'film':k[0],'cinema':k[1],'date':k[2],'time':k[3]}
             for k,v in old.items() if k not in cur and k[2]>=TODAY.isoformat()]

    # ---- posters on disk
    os.makedirs(os.path.join(ROOT,'posters'),exist_ok=True)
    for key,fm in films.items():
        u=fm.get('poster_url')
        if not u: fm['poster']=None; continue
        ext=os.path.splitext(u.split('?')[0])[1].lower()
        if ext not in ('.jpg','.jpeg','.png','.webp'): ext='.jpg'
        rel=f"posters/{key}{ext}"; dst=os.path.join(ROOT,rel)
        if not os.path.exists(dst):
            subprocess.run(['curl','-sL','--max-time','60','-o',dst,u],check=False)
        fm['poster']=rel if os.path.exists(dst) and os.path.getsize(dst)>1000 else None
    used={f"{k}" for k in films}
    for p in glob.glob(os.path.join(ROOT,'posters','*')):
        if os.path.splitext(os.path.basename(p))[0] not in used: os.remove(p)

    # ---- sources
    sources={}
    for cinema,c in fi.items():
        alld=sorted({s['date'] for f in c['films'] for s in f['shows']})
        sources[THEATERS[cinema]['site']]={'cinema':cinema,'status':c['status'],
            'dates_covered':f"{alld[0]}..{alld[-1]}" if alld else '','missing_dates':[],
            'vo_footnote_present':c['has_vo_note']}
    withperf=sorted({r['date'] for r in urows})
    gaps=[d for d in probed if withperf and withperf[0]<d<withperf[-1] and d not in withperf]
    sources[THEATERS['UCI Cinemas Verona']['site']]={'cinema':'UCI Cinemas Verona',
        'status':'ok' if urows else 'failed',
        'dates_covered':f"{withperf[0]}..{withperf[-1]}" if withperf else '',
        'missing_dates':gaps,'api':UCI_API.format(slug=UCI_SLUG,date='{YYYY-MM-DD}'),
        'probed_through':probed[-1] if probed else ''}

    data={'built_at':NOW.strftime('%Y-%m-%dT%H:%M:%S'),'timezone':TZ_LABEL,
          'theaters':THEATERS,'sources':sources,'films':films,'screenings':screenings,
          'removed_since_last_run':removed,
          'previous_run':prev.get('built_at')}
    json.dump(data,open(JSON_PATH,'w'),ensure_ascii=False,indent=1)

    cc=collections.Counter(s['category'] for s in screenings)
    log(f"\n  {len(screenings)} qualifying showtimes  {dict(cc)}")
    log(f"  {len(films)} films, {sum(1 for f in films.values() if not f['poster'])} without a poster")
    if prev: log(f"  {new_count} new since {prev.get('built_at','?')[:16]}, {len(removed)} removed")
    else:    log("  first run — nothing to compare against")
    for u,s in sources.items():
        if s['status']!='ok': log(f"  !! SOURCE FAILED: {s['cinema']} {u}")
    return data

if __name__=='__main__':
    if FETCH: log("fetching sources..."); fetch()
    else: log("using cached raw scrape")
    build()
    for step in ('gen_md.py','gen_site.py'):
        subprocess.run([sys.executable,'-I',os.path.join(ROOT,step)],check=True)
