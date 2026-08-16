# charts-tool — CDP-driven topping-games radar scraper (harness Task 8)

Answers "what games are topping right now, with real numbers" across the
web-game funnel. A browser-driven (CDP) fetch sees the JS-rendered play/vote
counts that jina's markdown reader misses — this fixes the radar's historical
`plays=null` data gap and replaces jina as the primary portal-radar fetch.

- Stack: Python + websockets (CDP client) + chromium-cdp daemon on
  127.0.0.1:9222 (QA's harness; `curl -s 127.0.0.1:9222/json/version` to check)
- Requires: `websockets` (present in the hermes venv)

## Usage

    python3 tools/charts/fetch_charts.py                    # full sweep (7 surfaces)
    python3 tools/charts/fetch_charts.py --surfaces crazygames/top,steam/top-sellers
    python3 tools/charts/fetch_charts.py --limit 10         # cap rows per surface
    python3 tools/charts/fetch_charts.py --no-enrich        # skip detail pages
    python3 tools/charts/fetch_charts.py --dry-run          # fetch, don't write
    python3 tools/charts/fetch_charts.py --output /tmp/x.jsonl

Convenience wrapper: `scripts/charts-sweep.sh`.

## Surfaces

| source tag        | page                                              | real numbers captured                              |
|-------------------|---------------------------------------------------|----------------------------------------------------|
| crazygames/top    | /top (in-page API)                                | plays, likes, category, year                       |
| crazygames/new    | /new (SSG __NEXT_DATA__)                          | plays, likes, category, year                       |
| crazygames/hot    | /hot (SSG __NEXT_DATA__)                          | plays, likes, category, year                       |
| poki/trending     | homepage rail -> detail pages                     | rating, votes, likes, dislikes, developer          |
| itch/top-puzzle   | top-rated genre-puzzle                            | rating, rating count, author, engine ("Made with") |
| itch/top-arcade   | top-rated genre-arcade                            | rating, rating count, author, engine ("Made with") |
| steam/top-sellers | search topsellers                                 | price, discount, review label/%/count, released    |

Output appends/merges normalized rows into `~/.hermes/company-memory/radar.jsonl`,
deduped by slug (existing rows are backfilled: `plays=null` → real plays, engine,
sdk, rating refreshed). Every row carries a `source` tag; rows seen on multiple
surfaces get `source` joined with `+` (e.g. `crazygames/new+hot`).

## Monetization comparators (Task 7 hook)

Per topping game the sweep also captures, where the surface exposes it:

- `engine` — CrazyGames `loaderTypeLabel` (HTML5 / Unity 2022 / Unity 6 / ...),
  itch.io "Made with" row (GameMaker / Godot / ...)
- `sdk` — CrazyGames loader type (`crazygames:html5`, `crazygames:unity2022`,
  `crazygames:iframe`...) — the v2/v3-style SDK signal
- `file_size_mb` — itch.io download file sizes (≤20MB mobile-homepage eligibility)
- `upvotes`/`downvotes` — CrazyGames detail pages
- Steam: `price`, `original_price`, `discount`, `review_label`, `review_percent`,
  `review_count` (genre-demand pulse; Steam does not expose play counts publicly)

## Honesty rules

- Never fabricate numbers. `plays=null` is written when the surface does not
  expose plays (Poki, itch.io listing, Steam), with the real engagement fields
  that ARE exposed (likes/votes/reviews).
- A surface that fails to load is reported as `[FAIL]` in the run log and the
  sweep continues; the run exits non-zero so callers can alert.
- CrazyGames `plays` comes from the portal's own API/SSG payload (totalPlays) —
  the same number the portal displays.

## Notes / pitfalls (production run 2026-08-16)

- CDP: create a fresh page target per URL (`PUT /json/new?<url>`), connect to
  the TARGET's websocket (browser-level ws lacks Page domain), close after.
  Never touch other agents' tabs on the shared daemon.
- Poki throws a Sourcepoint consent wall; clicking AGREE unlocks Like/Dislike
  counts. Rating+votes come from the page's JSON-LD (works behind the wall).
- CrazyGames /top renders client-side (API call); /new and /hot are SSG with
  the list embedded in `__NEXT_DATA__`.
- itch.io /tag-* redirects to /genre-*; game detail "More information" table
  holds rating, engine ("Made with"), platforms, tags.
- Steam search results need the rendered DOM (`.search_result_row`); review
  summary lives in `data-tooltip-html` on `.search_review_summary`.
- One full sweep ≈ 6-8 min (7 surfaces + ~32 detail pages). Cadence: bi-weekly,
  on-demand for launch waves (plan Task 8 Step 3).
