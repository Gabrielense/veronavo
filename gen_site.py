#!/usr/bin/env python3
"""Writes index.html from verona-vo-schedule.json. Data is inlined so the page is self-contained."""
import json,os,datetime,urllib.parse,html
P=os.path.dirname(os.path.abspath(__file__))
d=json.load(open(os.path.join(P,'verona-vo-schedule.json')))

def maps(name,t):
    q=urllib.parse.quote_plus(f"{name}, {t['address']}")
    return (f"https://www.google.com/maps/search/?api=1&query={q}",
            f"https://www.google.com/maps/dir/?api=1&destination={q}")
for n,t in d['theaters'].items():
    t['map_url'],t['directions_url']=maps(n,t)
    t['screenings']=sum(1 for s in d['screenings'] if s['cinema']==n)

payload=json.dumps({'built_at':d['built_at'],'theaters':d['theaters'],
                    'films':d['films'],'screenings':d['screenings'],'sources':d['sources']},
                   ensure_ascii=False,separators=(',',':'))

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Verona in Original Language</title>
<meta name="description" content="Every film screening in Verona with English audio, English subtitles or Spanish original audio - across UCI Verona and the Cinema Fiume group.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ctext y='26' font-size='26'%3E%F0%9F%8E%AC%3C/text%3E%3C/svg%3E">
<style>
*{box-sizing:border-box}
:root{
 --bg:#0e1014; --bg2:#161a21; --card:#1b2029; --line:#2a313d;
 --txt:#e8eaee; --dim:#9aa3b2; --accent:#ff5c5c; --accent2:#4fc3f7;
 --en:#4ade80; --ensub:#4fc3f7; --es:#fbbf24; --other:#a78bfa;
 --r:14px; --max:1120px;
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--txt);
 font:16px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:inherit}
.wrap{max-width:var(--max);margin:0 auto;padding:0 16px}
header{background:linear-gradient(170deg,#1d2430,#0e1014 70%);border-bottom:1px solid var(--line);padding:30px 0 24px}
h1{margin:0 0 6px;font-size:clamp(1.6rem,4.6vw,2.4rem);letter-spacing:-.02em;line-height:1.1}
h1 .em{color:var(--accent)}
.sub{color:var(--dim);margin:0;font-size:.95rem}
.built{color:var(--dim);font-size:.82rem;margin-top:12px}
.next{margin-top:18px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:14px 16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.next b{color:var(--accent2)}
h2{font-size:1.18rem;margin:34px 0 4px;letter-spacing:-.01em}
h2 .count{color:var(--dim);font-weight:400;font-size:.85rem;margin-left:6px}
.hint{color:var(--dim);font-size:.86rem;margin:0 0 14px}
.bar{position:sticky;top:0;z-index:5;background:var(--bg);padding:10px 0 9px;border-bottom:1px solid var(--line);margin-top:18px}
.filters{display:flex;gap:8px;flex-wrap:wrap}
.views{display:inline-flex;background:var(--bg2);border:1px solid var(--line);border-radius:999px;padding:3px;margin-bottom:9px}
.views button{background:none;border:0;color:var(--dim);font:inherit;font-size:.84rem;font-weight:600;
 padding:6px 16px;border-radius:999px;cursor:pointer}
.views button[aria-pressed=true]{background:var(--accent);color:#fff}
.chip{background:var(--bg2);border:1px solid var(--line);color:var(--dim);border-radius:999px;
 padding:7px 13px;font-size:.84rem;cursor:pointer;font-family:inherit;white-space:nowrap}
.chip[aria-pressed=true]{background:var(--txt);color:#11141a;border-color:var(--txt);font-weight:600}
.daygroup{margin-top:22px}
.dayhead{font-size:.8rem;text-transform:uppercase;letter-spacing:.09em;color:var(--dim);
 border-bottom:1px solid var(--line);padding-bottom:6px;margin-bottom:12px;display:flex;justify-content:space-between;gap:10px}
.dayhead .rel{text-transform:none;letter-spacing:0;color:var(--accent2)}
.row{display:grid;grid-template-columns:62px 1fr auto;gap:14px;background:var(--card);
 border:1px solid var(--line);border-radius:var(--r);padding:12px;margin-bottom:10px;align-items:start}
.row img{width:62px;height:92px;object-fit:cover;border-radius:8px;background:var(--bg2);display:block}
.ti{font-weight:650;line-height:1.25;margin-bottom:3px}
.orig{color:var(--dim);font-weight:400;font-size:.88em}
.meta{color:var(--dim);font-size:.85rem;display:flex;gap:7px;flex-wrap:wrap;align-items:center;margin-top:5px}
.time{font-variant-numeric:tabular-nums;font-weight:700;font-size:1.06rem}
.badge{font-size:.72rem;padding:2px 8px;border-radius:999px;border:1px solid;white-space:nowrap;font-weight:600}
.b-english_audio{color:var(--en);border-color:color-mix(in srgb,var(--en) 45%,transparent);background:color-mix(in srgb,var(--en) 11%,transparent)}
.b-english_subs{color:var(--ensub);border-color:color-mix(in srgb,var(--ensub) 45%,transparent);background:color-mix(in srgb,var(--ensub) 11%,transparent)}
.b-spanish{color:var(--es);border-color:color-mix(in srgb,var(--es) 45%,transparent);background:color-mix(in srgb,var(--es) 11%,transparent)}
.b-other{color:var(--other);border-color:color-mix(in srgb,var(--other) 45%,transparent);background:color-mix(in srgb,var(--other) 11%,transparent)}
.fmt{font-size:.72rem;padding:2px 7px;border-radius:5px;background:var(--bg2);border:1px solid var(--line);color:var(--dim);font-weight:600}
.acts{display:flex;flex-direction:column;gap:6px;align-items:stretch;min-width:116px}
.btn{display:block;text-align:center;text-decoration:none;font-size:.8rem;font-weight:600;
 padding:7px 10px;border-radius:9px;border:1px solid var(--line);background:var(--bg2);color:var(--txt)}
.btn.buy{background:var(--accent);border-color:var(--accent);color:#fff}
.btn.cal{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 40%,transparent)}
.btn:hover{filter:brightness(1.15)}
.nobuy{font-size:.75rem;color:var(--dim);text-align:center;padding:7px 4px;line-height:1.3}
.film{display:grid;grid-template-columns:118px 1fr;gap:16px;background:var(--card);
 border:1px solid var(--line);border-radius:var(--r);padding:14px;margin-bottom:14px}
.film>img{width:118px;height:176px;object-fit:cover;border-radius:10px;background:var(--bg2);display:block}
.film h3{margin:0 0 2px;font-size:1.16rem;line-height:1.2;letter-spacing:-.01em}
.film .fmeta{color:var(--dim);font-size:.83rem;margin:0 0 9px}
.film .bl{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:11px;align-items:center}
.flink{font-size:.75rem;font-weight:600;text-decoration:none;padding:3px 10px;border-radius:999px;
 border:1px solid var(--line);background:var(--bg2);color:var(--dim)}
.flink.tr{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 42%,transparent)}
.flink:hover{filter:brightness(1.25)}
.syn.en{color:#c3cad6}
.synsrc{font-size:.72rem;color:var(--dim);margin:-6px 0 11px}
.syn{color:var(--dim);font-size:.84rem;line-height:1.5;margin:0 0 11px;
 display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.shows{display:flex;flex-direction:column;gap:5px}
.sh{display:grid;grid-template-columns:minmax(150px,auto) 62px minmax(0,1fr) auto;gap:14px;align-items:center;
 padding:7px 9px;border-radius:9px;background:var(--bg2);border:1px solid transparent;font-size:.86rem}
.sh:hover{border-color:var(--line)}
.sh .d{color:var(--dim);white-space:nowrap}
.sh .d.soon{color:var(--accent2);font-weight:600}
.sh .t{font-variant-numeric:tabular-nums;font-weight:700;font-size:.98rem}
.sh .w{color:var(--dim);min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sh .a{display:flex;gap:6px;justify-content:flex-end}
.sh .a a{font-size:.75rem;font-weight:600;text-decoration:none;padding:5px 10px;border-radius:7px;white-space:nowrap}
.sh .a .buy{background:var(--accent);color:#fff}
.sh .a .cal{border:1px solid color-mix(in srgb,var(--accent2) 40%,transparent);color:var(--accent2)}
.sh .a .box{color:var(--dim);font-size:.72rem;padding:5px 2px}
.more{background:none;border:0;color:var(--accent2);font:inherit;font-size:.82rem;font-weight:600;
 cursor:pointer;padding:7px 0 0;text-align:left}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:12px;margin-top:14px}
.tcard{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:14px}
.tcard h3{margin:0 0 4px;font-size:1rem}
.tcard .ad{color:var(--dim);font-size:.87rem;margin:0 0 8px}
.tcard .nt{color:var(--dim);font-size:.78rem;margin:8px 0 0;line-height:1.45}
.tcard .lk{display:flex;gap:7px;flex-wrap:wrap;margin-top:4px}
.pill{font-size:.76rem;text-decoration:none;padding:5px 10px;border-radius:999px;border:1px solid var(--line);background:var(--bg2);color:var(--txt);font-weight:600}
.pill.m{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 40%,transparent)}
.tcard .cnt{font-size:.74rem;color:var(--dim);margin-top:9px}
.empty{color:var(--dim);background:var(--card);border:1px dashed var(--line);border-radius:var(--r);padding:22px;text-align:center}
footer{margin:46px 0 30px;padding-top:20px;border-top:1px solid var(--line);color:var(--dim);font-size:.82rem;line-height:1.6}
footer h3{color:var(--txt);font-size:.92rem;margin:0 0 8px}
footer ul{margin:0 0 14px;padding-left:18px}
footer a{color:var(--accent2)}
@media (max-width:620px){
 .film{grid-template-columns:72px 1fr;gap:12px}
 .film>img{width:72px;height:108px}
 .sh{grid-template-columns:1fr auto;gap:4px 10px;padding:9px}
 .sh .d{grid-column:1}
 .sh .t{grid-column:2;text-align:right}
 .sh .w{grid-column:1/-1;white-space:normal}
 .sh .a{grid-column:1/-1;justify-content:flex-start;margin-top:3px}
}
@media (max-width:560px){
 .row{grid-template-columns:52px 1fr;gap:11px}
 .row img{width:52px;height:78px}
 .acts{grid-column:1/-1;flex-direction:row;min-width:0}
 .btn{flex:1}
}
@media print{.filters,.acts{display:none}body{background:#fff;color:#000}}
</style>
</head>
<body>
<header>
 <div class="wrap">
  <h1>Verona <span class="em">in original language</span></h1>
  <p class="sub">Every screening with <strong>English audio</strong>, <strong>English subtitles</strong> or <strong>Spanish original audio</strong> &mdash; UCI Verona plus the four Cinema Fiume houses.</p>
  <div class="next" id="next"></div>
  <p class="built" id="built"></p>
 </div>
</header>

<main class="wrap">
 <div class="bar">
  <div class="views" id="views">
   <button data-v="film" aria-pressed="true">By film</button>
   <button data-v="date" aria-pressed="false">By date</button>
  </div>
  <div class="filters" id="filters"></div>
 </div>
 <div id="films"></div>
 <div id="schedule" hidden></div>


 <h2>The five cinemas</h2>
 <p class="hint">Tap a map link to open it in Google Maps, or get directions from where you are.</p>
 <div class="cards" id="theaters"></div>
</main>

<footer class="wrap">
 <h3>How to read this</h3>
 <ul>
  <li><strong>UCI Verona</strong> labels each showtime with its audio and subtitle languages. The printed time is the admission time &mdash; the film itself starts about <strong>25 minutes later</strong> (about 15 for alternative-content events).</li>
  <li><strong>The Cinema Fiume group</strong> (Kappadue, Diamante, Fiume, Pindemonte) marks original-version slots with an asterisk and subtitles are Italian, but the page never states the audio language. Audio here is inferred from the film's production country and director; each entry records how.</li>
  <li>Showtimes with no original-version marker are Italian dubs and are left out.</li>
  <li>Online ticketing exists only at UCI. The Fiume houses sell at the box office.</li>
 </ul>
 <h3>Sources &amp; coverage</h3>
 <ul id="sources"></ul>
 <p id="credit"></p>
</footer>

<script id="data" type="application/json">__PAYLOAD__</script>
<script>
const D=JSON.parse(document.getElementById('data').textContent);
const WD=['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
const MO=['January','February','March','April','May','June','July','August','September','October','November','December'];
const CATS={english_audio:'English audio',english_subs:'English subtitles',spanish:'Spanish',other:'Other original version'};
// "Today"/"Tomorrow" are read off the visitor's clock, never off D.built_at:
// the labels must stay right on a day when no rebuild ran. Always resolved in
// Europe/Rome, so a visitor abroad still sees the cinemas' own calendar day.
function romeNow(){
 const p={};
 for(const x of new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Rome',
     year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false})
     .formatToParts(new Date())) if(x.type!=='literal')p[x.type]=x.value;
 const h=p.hour==='24'?'00':p.hour;        // some engines render midnight as 24
 return {date:p.year+'-'+p.month+'-'+p.day,time:h+':'+p.minute};
}
const NOW=romeNow();
const TODAY=NOW.date;

// A showtime leaves the page only once the film has actually ended, so nothing
// still running vanishes from under someone deciding whether to set off.
function isOver(s){
 if(s.date>TODAY)return false;
 if(s.date<TODAY)return true;
 const end=s.end_time||s.time;
 if(end<s.time)return false;               // runs past midnight, so still on today
 return end<=NOW.time;
}
// Every render reads LIVE, never D.screenings: the payload still holds the
// whole build, we just stop showing what the clock has overtaken.
const LIVE=D.screenings.filter(s=>!isOver(s));

function parseD(s){const[y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);}
function fmtDay(s){const t=parseD(s);return WD[t.getDay()]+', '+t.getDate()+' '+MO[t.getMonth()];}
function relDay(s){
 const a=parseD(TODAY),b=parseD(s);
 const n=Math.round((b-a)/86400000);
 if(n===0)return'Today';if(n===1)return'Tomorrow';
 if(n<7)return'in '+n+' days';return'';
}
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function langTxt(s){return s.audio+' audio &middot; '+(s.subs==='none'?'no subtitles':s.subs+' subtitles');}
function filmTitle(s){
 const f=D.films[s.film_key]||{};
 const o=s.film_original||f.film_original||'';
 return esc(s.film_it)+(o&&o.toLowerCase()!==s.film_it.toLowerCase()?' <span class="orig">('+esc(o)+')</span>':'');
}

let active='all';
let view='film';
const expanded={};
const counts={all:LIVE.length};
for(const k in CATS)counts[k]=LIVE.filter(s=>s.category===k).length;

function renderFilters(){
 const keys=['all',...Object.keys(CATS).filter(k=>counts[k]>0)];
 document.getElementById('filters').innerHTML=keys.map(k=>
  `<button class="chip" data-k="${k}" aria-pressed="${k===active}">`+
  (k==='all'?'All screenings':CATS[k])+` (${counts[k]})</button>`).join('');
 document.querySelectorAll('.chip').forEach(b=>b.onclick=()=>{active=b.dataset.k;renderFilters();renderAll();});
}

function renderViews(){
 document.querySelectorAll('#views button').forEach(b=>{
  b.setAttribute('aria-pressed',String(b.dataset.v===view));
  b.onclick=()=>{view=b.dataset.v;renderViews();renderAll();};
 });
 document.getElementById('films').hidden=view!=='film';
 document.getElementById('schedule').hidden=view!=='date';
}

function renderAll(){ view==='film'?renderFilms():renderSchedule(); }

const SHOW_LIMIT=6;

function showtimeRow(s){
 const rel=relDay(s.date);
 const t=parseD(s.date);
 const dd=WD[t.getDay()].slice(0,3)+' '+t.getDate()+' '+MO[t.getMonth()].slice(0,3);
 const where=esc(s.cinema)+(s.room?' &middot; '+esc(s.room):'')+(s.format?' &middot; '+esc(s.format):'')+
   (s.price_from?' &middot; from &euro;'+(+s.price_from).toFixed(2):'');
 const acts=(s.ticket_url
   ?`<a class="buy" href="${esc(s.ticket_url)}" target="_blank" rel="noopener noreferrer">Buy</a>`
   :`<span class="box">Box office</span>`)+
   `<a class="cal" href="${esc(s.calendar_url)}" target="_blank" rel="noopener noreferrer">+ Calendar</a>`;
 return `<div class="sh"><span class="d${rel?' soon':''}">${rel||dd}${rel?' &middot; '+dd:''}</span>`+
        `<span class="t">${esc(s.time)}</span><span class="w">${where}</span>`+
        `<span class="a">${acts}</span></div>`;
}

function renderFilms(){
 const rows=LIVE.filter(s=>active==='all'||s.category===active);
 const el=document.getElementById('films');
 if(!rows.length){el.innerHTML='<div class="empty">Nothing scheduled in this category right now.</div>';return;}
 const byFilm={};
 rows.forEach(s=>(byFilm[s.film_key]=byFilm[s.film_key]||[]).push(s));
 const keys=Object.keys(byFilm).sort((a,b)=>
   byFilm[a][0].date.localeCompare(byFilm[b][0].date)||byFilm[a][0].time.localeCompare(byFilm[b][0].time));
 el.innerHTML=keys.map(k=>{
  const ss=byFilm[k], f=D.films[k]||{}, first=ss[0];
  const cats=[...new Set(ss.map(s=>s.category))];
  const badges=cats.map(c=>{
    const ex=ss.find(s=>s.category===c);
    return `<span class="badge b-${c}">${langTxt(ex)}</span>`;}).join('')+
   (f.trailer_url?`<a class="flink tr" href="${esc(f.trailer_url)}" target="_blank" rel="noopener noreferrer">Trailer \u2197</a>`:'');
  const bits=[];
  if(f.genres&&f.genres.length)bits.push(esc(f.genres.join(', ')));
  if(first.runtime_min)bits.push(first.runtime_min+' min');
  if(f.director)bits.push('dir. '+esc(f.director));
  if(f.production)bits.push(esc(f.production));
  if(f.rating)bits.push(esc(f.rating));
  bits.push([...new Set(ss.map(s=>s.cinema))].map(esc).join(' &middot; '));
  const open=expanded[k], shown=open?ss:ss.slice(0,SHOW_LIMIT);
  const more=ss.length>SHOW_LIMIT
    ?`<button class="more" data-f="${esc(k)}">${open?'Show fewer':'Show all '+ss.length+' showtimes'}</button>`:'';
  const img=f.poster?`<img src="${esc(f.poster)}" alt="" loading="lazy" width="118" height="176">`:'<div></div>';
  return `<article class="film">${img}<div>
    <h3>${filmTitle(first)}</h3>
    <p class="fmeta">${bits.filter(Boolean).join(' &middot; ')}</p>
    <div class="bl">${badges}</div>`+

    `<div class="shows">${shown.map(showtimeRow).join('')}</div>${more}</div></article>`;
 }).join('');
 el.querySelectorAll('.more').forEach(b=>b.onclick=()=>{
   expanded[b.dataset.f]=!expanded[b.dataset.f];renderFilms();});
}

function actions(s){
 if(s.ticket_url)
  return `<a class="btn buy" href="${esc(s.ticket_url)}" target="_blank" rel="noopener noreferrer">Buy ticket</a>`+
         `<a class="btn cal" href="${esc(s.calendar_url)}" target="_blank" rel="noopener noreferrer">+ Calendar</a>`;
 return `<a class="btn cal" href="${esc(s.calendar_url)}" target="_blank" rel="noopener noreferrer">+ Calendar</a>`+
        `<span class="nobuy">Box office only</span>`;
}

function renderSchedule(){
 const rows=LIVE.filter(s=>active==='all'||s.category===active);
 const el=document.getElementById('schedule');
 if(!rows.length){el.innerHTML='<div class="empty">Nothing scheduled in this category right now.</div>';return;}
 const byDay={};
 rows.forEach(s=>(byDay[s.date]=byDay[s.date]||[]).push(s));
 el.innerHTML=Object.keys(byDay).sort().map(day=>{
  const rel=relDay(day);
  return `<section class="daygroup"><div class="dayhead"><span>${fmtDay(day)}</span>`+
   (rel?`<span class="rel">${rel}</span>`:'')+`</div>`+
   byDay[day].map(s=>{
    const f=D.films[s.film_key]||{};
    const img=f.poster?`<img src="${esc(f.poster)}" alt="" loading="lazy" width="62" height="92">`:`<div class="row-noimg"></div>`;
    return `<article class="row">${img}<div><div class="ti">${filmTitle(s)}</div>
     <div class="meta"><span class="time">${esc(s.time)}</span>`+
     (s.end_time?`<span>&ndash; ${esc(s.end_time)}</span>`:'')+
     `<span class="badge b-${s.category}">${langTxt(s)}</span>`+
     (s.format?`<span class="fmt">${esc(s.format)}</span>`:'')+
     `</div><div class="meta"><span>${esc(s.cinema)}</span>`+
     (s.room?`<span>&middot; ${esc(s.room)}</span>`:'')+
     (s.price_from?`<span>&middot; from &euro;${(+s.price_from).toFixed(2)}</span>`:'')+
     `<span>&middot; marked <code>${esc(s.marker)}</code></span></div></div>
     <div class="acts">${actions(s)}</div></article>`;
   }).join('')+`</section>`;
 }).join('');
}

function renderNext(){
 const n=LIVE.find(s=>s.category==='english_audio'||s.category==='english_subs');
 const el=document.getElementById('next');
 if(!n){el.innerHTML='<span>No English-friendly screening currently listed.</span>';return;}
 el.innerHTML=`<span>Next in English: <b>${esc(n.film_it)}</b> &mdash; ${fmtDay(n.date)} at ${esc(n.time)}, ${esc(n.cinema)}</span>`+
  (n.ticket_url?`<a class="btn buy" href="${esc(n.ticket_url)}" target="_blank" rel="noopener noreferrer">Buy ticket</a>`:'')+
  `<a class="btn cal" href="${esc(n.calendar_url)}" target="_blank" rel="noopener noreferrer">+ Calendar</a>`;
}


function renderTheaters(){
 document.getElementById('theaters').innerHTML=Object.entries(D.theaters).map(([n,t])=>{
  const cnt=LIVE.filter(s=>s.cinema===n).length;
  return `<div class="tcard"><h3>${esc(n)}</h3><p class="ad">${esc(t.address)}`+
  (t.phone?`<br>tel ${esc(t.phone)}`:'')+`</p>
   <div class="lk">
    <a class="pill m" href="${esc(t.map_url)}" target="_blank" rel="noopener noreferrer">Map</a>
    <a class="pill m" href="${esc(t.directions_url)}" target="_blank" rel="noopener noreferrer">Directions</a>
    <a class="pill" href="${esc(t.site)}" target="_blank" rel="noopener noreferrer">Programme</a>
   </div>
   <p class="cnt">${cnt} original-language showtime${cnt===1?'':'s'} listed</p>
   <p class="nt">${esc(t.note)} ${esc(t.booking_note)}</p></div>`;}).join('');
}

function renderFooter(){
 document.getElementById('sources').innerHTML=Object.entries(D.sources).map(([u,s])=>
  `<li>${esc(s.cinema)} &mdash; ${esc(s.status)}, covering ${esc(s.dates_covered)}`+
  (s.missing_dates&&s.missing_dates.length?`, no programme published for ${s.missing_dates.map(esc).join(', ')}`:'')+
  ` &middot; <a href="${esc(u)}" target="_blank" rel="noopener noreferrer">source</a></li>`).join('');
 const dt=D.built_at;
 const age=Math.round((parseD(TODAY)-parseD(dt.slice(0,10)))/86400000);
 document.getElementById('built').textContent='Schedule built '+dt.slice(0,10)+' at '+dt.slice(11,16)+' (Europe/Rome) from the cinemas\\u2019 own listings.'+
  (age>=2?' It has not been rebuilt for '+age+' days, so screenings announced since then are missing.':'');
 document.getElementById('credit').innerHTML='Posters and showtime data belong to the cinemas and distributors. '+
  'This page is an unofficial reading aid &mdash; always confirm on the cinema\\u2019s own site before travelling.';
}

renderFilters();renderViews();renderAll();renderNext();renderTheaters();renderFooter();
</script>
</body>
</html>
"""
open(os.path.join(P,'index.html'),'w').write(HTML.replace('__PAYLOAD__',payload))
print("wrote index.html",os.path.getsize(os.path.join(P,'index.html')),"bytes")
