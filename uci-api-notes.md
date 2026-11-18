# UCI Cinemas Verona — how to read the showtimes

Recorded 18 Nov 2026 from what was actually observed on the site.

## The problem with the public page

`https://www.ucicinemas.it/cinema/veneto/verona/uci-cinemas-verona/` cannot be scraped with
`curl`. It answers **302** into a Queue-it virtual waiting room:

```
location: https://uciitaly.queue-it.net/?c=uciitaly&e=681548&...&kupver=cloudflare-4.1.1
x-queueit-connector: cloudflare
```

A real browser gets through; `curl` does not. The page itself is Nuxt 3 and server-renders
only the selected day, so reading it would mean clicking all ~40 calendar dates.

## The endpoint to use instead

The Nuxt runtime config exposes `apiUrl: https://backend.ucicinemas.it`, and the client
calls `getTheatreProgramming` → `/theatres/{slug}/programming/{date}`. The working URL is:

```
https://backend.ucicinemas.it/api/theatres/uci-cinemas-verona/programming/YYYY-MM-DD
```

**This one works with plain `curl`** — no waiting room, no headers, no token needed.
Verified 200 / ~70 KB JSON. Other prefixes (`/api/v1`, `/api/website`, bare `/theatres/…`)
return `{"message":"API Endpoint Not Found..."}`.

A day with no programme returns `{"data":[],"meta":{...}}`, so you can probe forward
until the days run empty. On 18 Nov 2026 the programme ran 18 Nov → 30 Dec, with
10–14 Dec genuinely empty (the site's own date picker skips those dates too).

## Response shape

```
data[]                         one entry per film
  title, slug, poster, description, rating.name, genres[].name
  screens[]                    [{ "2D": [...] }, { "IMAX": [...] }]  — key is the screen type
    <screenname>[]             one entry per *version* of the film
      slug                     e.g. "ov-avengers-doomsday-14277", "jp-godzilla-minus-zero"
      language.name            ITA | ENG | KOR | JP | ... | "AUTISM FRIENDLY"
      subtitles.name           ITA | ENG   (an OBJECT, not a string — easy to miss)
      duration                 "02:15"
      performances[]
        day                    YYYY-MM-DD  — filter on this, entries for other days appear
        actual_start_at        "20:40"     — the printed admission time
        starts_at / ends_at    full timestamps
        room                   "SALA 08"
        price_starting_from    "7.9"
        cart_link              "/movies/<slug>/acquista/5116/9899/576745"
                               → https://www.ucicinemas.it + cart_link  = the buy page
```

## Reading the language

`language.name` **is** the per-showtime badge the website renders (`ENG` + `sottotitoli ITA`,
`KOR / sottotitoli ENG`). No badge on the site = `language.name == "ITA"` = Italian dub.

`AUTISM FRIENDLY` appears in the `language` field but is a screening type, not a language —
those screenings are in Italian. Exclude it along with `ITA`.

## Other notes

- Theatre id 46, coordinates 45.3966662 / 11.0164011, address "Via Monte Amiata,
  San Giovanni Lupatoto Verona", screens IMAX / XL / 3D / 2D.
- The site states: the film starts **about 25 minutes after the printed time**
  (about 15 for alternative-content events). Keep the printed time, carry the note.
- `programs-production` in the Nuxt payload lists site-wide strands and includes one
  called **"Film in English"** (`slug: film-in-english`) — a possible cross-check.

## Verification done on 18 Nov 2026

Loaded the real page in a browser, selected 15 Dec, and confirmed the only English
showtime that day is Avengers: Doomsday at 00:05, `2D / ENG / sottotitoli ITA`, from €7.90,
with buy link `/movies/avengers-doomsday/acquista/5116/9899/576745` — matching the API
byte for byte.
