# Game Studio Hermes — Charter

## Mission
Build and ship web games as a fully autonomous agent factory. Workers design,
build, test, and publish HTML5 games to portals (CrazyGames, Poki, itch.io);
the human board judges only what agents cannot: **fun**.

## Business model
- Portals provide distribution + monetization: submit → human QA → Basic Launch
  (metric gate) → Full Launch (~60% ad revenue share). No UA cost, no trust
  deficit, no cold-start network. Every accepted game gets a homepage-carousel boost.
- Dev-floor estimate: ~$1 per 1,000 plays (non-exclusive). €100 monthly payout
  threshold. Tier-1 (US/UK/AU) audiences pay the highest eCPM.
- Export ladder: Web (wave 1) → PWA (free) → Android ($25 once) for proven
  winners → iOS/Steam only for outliers.

## Category strategy (wave 1)
- **~60% procedural casual puzzle** — agent superpower: procedural level
  generation + automated solvability verification. Matches older,
  higher-retention demographics. Evergreen.
- **~30% physics one-button skill** — conversion machines, instant fun, Godot 2D
  physics strength.
- **~10% experiments** — idle/management sims next (best retention, slower build).
- Defer: .io multiplayer (needs servers/netcode), word/trivia (licensed/saturated),
  troll platformers (art/juice heavy).

## KPI gates (from portal benchmarks)
- Average playtime: **10+ min** (session-length hooks)
- Day-1 retention: **10-15%**
- Conversion (play ≥1 min): **80%+**
- Build: **no hard size cap — 3D allowed**; first load <10s on broadband, total <250MB, <1500 files; compression discipline still applies
- Load: **<10s**
- PEGI12, no kid-targeted content, original (no clones/asset-flips — human QA)

## Doctrine
- **Idle is a bug.** Research proposes → kill-gate kills → you (human) judge fun →
  portal metrics decide. Never-idle continues.
- **3-worker hard cap.** 4GB/2vCPU VPS. Never exceed 3 concurrent workers.
- **No local models.** Inference = opencode-go deepseek-flash. Nothing runs on-box.
- **Kill-first.** Every concept passes a red/blue gate before a build card exists.
  A gate that passes 100% is not a gate.
- **You are the fun-judge.** Every game before portal submission: playtest URL →
  your verdict. Your only recurring role, ~15 min/game.
- **Curated skills first, full catalogs after 2-3 shipped games.**

## Assets
- Hybrid stack: Kenney CC0 (structural) + AI-generated hero assets (originality)
  + jsfxr procedural SFX (original). `assets.json` provenance manifest per game.

## Roles (reuse existing 7 profiles, retargeted)
- research → 6-topic game research program + portal radar
- ceo → concept generation, kill-gates, portfolio verdicts
- design → assets, level-design, game-feel, UI
- engineering → Godot engine skills, build/export pipeline
- qa → smoke-playtest, QA skills, portal metric checks
- marketing → covers, metadata, portal listings
- strategy → scoring, whitespace scans, portfolio mix
