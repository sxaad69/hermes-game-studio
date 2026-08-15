---
name: portal-radar
description: "Weekly web-game portal radar. Scrapes CrazyGames and Poki new/hot/trending pages via the jina.ai keyless reader and normalizes each game into a structured record (name, category, mechanics, plays, rating, cover style, age, tags). Detects mechanics that are rising vs saturating and feeds the genre-whitespace scan. Appends to radar.jsonl in company memory so all factory workers share the same dataset."
version: 1.0.0
author: hermesagency
license: MIT
metadata:
  hermes:
    tags: [game-studio, radar, scraping, market-research]
    related_skills: [games-research, market-research]
---

# Portal Radar

Weekly sweep of the two main portals to keep the factory's category map fresh.

## Sources (keyless, verified)
- CrazyGames: /new, /hot, category pages (/c/puzzle, /c/arcade, etc.)
- Poki: /en (popular this week), /en/puzzle, /en/skill
- Fetch via jina.ai reader: `https://r.jina.ai/<url>` (works without a key;
  handles JS-walled pages the portals' own docs do not)

## Record per game
```
- name, url
- category / tags
- mechanics (inferred from title/desc/tags)
- plays (if shown), rating (if shown)
- cover style (screenshot description)
- age (weeks since first seen, from prior runs)
```

## Detection rules
- MECHANIC-UP: same mechanic appearing across 3+ new games this week.
- MECHANIC-SATURATED: mechanic already over-represented in catalog with no
  new variants — add to the saturation kill-list.
- WHITESPACE: proven mechanic with few or no games in a given theme/skin.
- NEW: genuinely novel mechanic no prior game used.

## Data-completeness fallback
Do NOT declare a field null on the first miss. For each game, before marking
a field missing, attempt:
1. The game's own detail page (jina.ai reader) for plays/votes/developer.
2. The portal's tag/search page for that game title.
3. Only if both fail, write null AND note `"fetch_failed": true` in the row
   so the next run knows to re-attempt (backfill pass). Never fabricate a
   number; a verified-null with a re-attempt marker is more useful to the
   factory than a silent gap.

## Output
Append one JSONL row per game to the shared radar dataset:
`~/.hermes/company-memory/radar.jsonl` (create if missing). Write a compact
summary block for the games board: counts, mechanic-up list, saturation
kill-list, whitespace candidates (max 3).

Rules: never fabricate play counts/ratings (mark unseen as null); state when a
page failed to load (partial coverage) instead of skipping silently.
