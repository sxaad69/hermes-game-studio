---
name: games-research
description: "The Game Studio Hermes research program. Six recurring topics feed the game factory: (1) portal radar — new/hot/trending on CrazyGames/Poki, mechanics rising vs saturating; (2) mechanic teardowns of top games in target category; (3) player sentiment mining — 1-3 star complaints, bounce patterns; (4) genre whitespace — mechanic x theme grid vs live catalog; (5) dev economics benchmarks — real portal earnings; (6) Godot-web + portal SDK watch. Output is evidence packs (sources/URLs/quotes, why-now) consumed by the kill-gate before any build card."
version: 1.0.0
author: hermesagency
license: MIT
metadata:
  hermes:
    tags: [game-studio, research, radar, market-research]
    related_skills: [market-research, portal-radar, last30days, debate, idea-pipeline]
---

# Game Research Program

Research is the intake of the factory. It never builds, never approves — it
proposes evidence, the kill-gate decides, the human board judges fun.

## Evidence pack format (per topic output)

```
EVIDENCE PACK — <topic/game/mechanic>
SOURCES: <URLs + what they prove, quoted>
SIGNAL: <rising | saturating | whitespace | broken>
RELEVANCE TO FACTORY: <which game category / mechanic it feeds>
WHY-NOW: <one line>
```

Rules: evidence over vibes; no single-source packs; URLs+quotes mandatory;
state gaps honestly (never pad); do NOT re-ideate the 3 lighthouse products or
the 5 SaaS products (that era is over).

## Topic 1 — Portal radar (weekly)

Scrape CrazyGames /new, /hot, category pages and Poki trending via jina.ai
reader (keyless, verified working). Record per game: name, category, mechanics,
plays, rating, cover style, age. Output a structured radar.jsonl row each run
(append to shared company memory).

## Topic 2 — Mechanic teardowns (per concept batch)

Pick top 5 games in the target category. Document: first-10-seconds hook,
core loop, difficulty curve, session-length drivers, why players return,
what makes it feel good. Translate each into a buildable checklist item.

## Topic 3 — Player sentiment mining (before each submission)

1-3 star ratings on portal games + r/WebGames, r/incremental_games, HN threads.
Patterns: too short, boring, buggy, confusing onboarding. Feed the
pre-submission checklist and the fun-gate questions.

## Topic 4 — Genre whitespace scan (bi-weekly)

Mechanic x theme grid cross-checked against the live portal catalog: proven
mechanic + untouched theme = candidate; saturation = kill-list (what NOT to
build). This is the ideation engine's filter.

## Topic 5 — Dev economics benchmarks (monthly)

Indie dev reports of actual portal earnings: $/1k plays variance, eCPM by geo,
Basic-Launch pass rates. Sets portfolio expectations and kill-gate thresholds.
Be honest: median games earn little; the portfolio bets on outliers.

## Topic 6 — Godot-web + SDK watch (weekly digest)

CrazyGames SDK changelog, Godot web-export regressions, browser API shifts
(SharedArrayBuffer/COOP-COEP), engine-specific portal wins. Feed the build and
export pipeline.

## Concept card requirements

Every whitespace scan run MUST produce max 3 concept cards, and of those at
least 1 MUST be an **agent-native concept** — a game whose design specifically
exploits the factory's structural edge (procedural level generation +
automated solvability/win-loss verification + headless smoke-play) such that
no human team could produce the same depth at the same cost. Example: a puzzle
with 1,000 auto-verified generated levels, or a roguelike whose runs are
machine-tuned. The other 1-2 may be portal-derivative (proven mechanic + twist).
A scan that returns only portal-derivative cards has failed this requirement.

Each card uses the concept-card template at the repo path
`/root/hermes-game-studio/templates/concept-card.md` (copy it into the task
workspace; do NOT create a divergent copy in a skill dir).

Each card ends with a one-line scored recommendation so the kill-gate has an
ordering:

```
SCORED RECOMMENDATION: <rank 1-3> — PROBABILITY-OF-HIT (high/med/low) —
REASON: <one line: why this is the factory's best shot this batch>
```

## Delivery contract

Every run ends with evidence packs → red/blue debate → top 1-3 concept cards
(mechanic/twist/theme/asset-plan/testability/scored-recommendation) →
kill-gate. Research never skips the gate. A run that returns "nothing solid
this window" is a valid, honest outcome — never pad, never force a winner.
