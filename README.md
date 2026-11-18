# Verona in original language

A small static site listing every cinema screening in Verona that is **not** an Italian dub:
English audio, English subtitles, or Spanish original audio, with the other original-version
showings kept in a separate group.

**The page:** `index.html` — self-contained, data inlined, no build step to view it.

## What it covers

Five cinemas, read from their own listings only (never an aggregator — aggregators show
today only and miss UCI's English screenings entirely):

| Cinema | Source |
|---|---|
| UCI Cinemas Verona | JSON API — see [uci-api-notes.md](uci-api-notes.md) |
| Cinema Kappadue | cinemafiume.it programme page |
| Cinema Diamante | cinemafiume.it programme page |
| Cinema Fiume | cinemafiume.it programme page |
| Cinema Pindemonte | cinemafiume.it programme page |

## What counts as a screening worth listing

A showtime is kept only when the cinema's own listing marks it, per showtime:

- **English audio**, any subtitles → *English audio*
- **any audio with English subtitles** → *English subtitles*
- **Spanish original audio** → *Spanish*
- any other original version → *Other original version*

No marker means an Italian dub and is dropped. A film's country of origin is never
treated as evidence on its own — only the marker on that specific showtime counts.

### The two sources say different amounts

UCI labels each showtime with both audio and subtitle language, so those entries are
exact (`lang_source: "badge"`).

The Cinema Fiume group marks original-version slots with an asterisk (`21:00*`) and states
that subtitles are Italian, but **never names the audio language**. For those the audio is
inferred from the film's production country and director, and every screening records how
it was decided in its `lang_source` field, e.g.
`"inferred: production USA/G.B. 2026, director Martin McDonagh"`.

## Files

```
index.html                 the site (generated; data inlined)
verona-vo-schedule.json    the data + source coverage
verona-vo-schedule.md      the same schedule as readable Markdown
posters/                   poster images, one per film
build/update.py            fetch → parse → diff → write everything
gen_site.py                verona-vo-schedule.json → index.html
gen_md.py                  verona-vo-schedule.json → verona-vo-schedule.md
uci-api-notes.md           how UCI's showtimes are actually obtained
```

## Updating

```
python3 build/update.py
```

That refetches both sources, rebuilds the JSON, Markdown and `index.html`, downloads any
new posters and drops posters no longer referenced. It compares against the previous
`verona-vo-schedule.json`, so each screening keeps a `first_seen` date, newly appeared
showtimes are flagged `is_new`, and future showtimes that have disappeared are listed under
`removed_since_last_run`.

`python3 build/update.py --no-fetch` rebuilds from the cached scrape in `build/raw/`
(not committed) without touching the network.

## Caveats

- UCI's printed time is the **admission** time; the film starts about 25 minutes later
  (about 15 for alternative-content events). The site shows the printed time and says so.
- Only UCI sells tickets online. The Fiume houses are box office only.
- The Fiume programme runs several weeks further ahead than UCI's, so the far end of the
  schedule is Fiume-only. Coverage per source is printed at the bottom of the page.
- Always confirm on the cinema's own site before travelling.
