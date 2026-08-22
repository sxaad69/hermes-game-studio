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
- Build: **no hard size cap — 3D allowed**; first load <10s on broadband; compression
  discipline still applies. NO storage/file-count caps: all artifacts (code + assets)
  live in the game's GitHub repo — the VPS is scratch, GitHub is truth.
- Load: **<10s**
- PEGI12, no kid-targeted content, original (no clones/asset-flips — human QA)

## Doctrine
- **Idle is a bug.** Research proposes → kill-gate kills → design gates feel → you
  (human) judge fun → portal metrics decide. Never-idle continues: the dispatcher
  never idles >4h — out of new ideas is not out of work (see Boneyard, below).
- **Worker cap: 4** (raised from 3 on 2026-08-22 after headroom audit: 2 vCPU /
  3.9GB RAM, ~200MB per worker, 2GB available). Guardrail: pipeline-keeper keeps
  it at 3 whenever available RAM drops below 800MB. Never exceed 4 concurrent workers.
- **No local models.** Inference = opencode-go ox-alpha (fallback OpenRouter). Nothing runs on-box.
- **Kill-first.** Every concept passes a red/blue gate before a build card exists.
  A gate that passes 100% is not a gate.
- **Design gates feel.** No build spec fires without a design-co-signed FEEL
  section (art/audio/drama direction) on the concept card. A game whose soul was
  decided by market data alone is dead on arrival — see LIE TO ME postmortem 2026-08-21.
- **Repo law.** Every game = its own GitHub repo from W1 start; code AND all assets
  pushed continuously; `assets.json` provenance manifest in-repo. Done means remote
  tip == local tip. Feeler/playtest distribution = GitHub Pages from that repo.
  The pipeline-keeper cron audits remotes hourly and auto-fixes drift.
- **Boneyard.** Every KILLed/PARKed/board-rejected concept is catalogued in
  `wiki/boneyard.md` with rejection reason + revival criteria. When the idea pool
  is empty, workers mine the boneyard against fresh radar data — revive with a
  twist or formally bury with a written reason. Dead concepts are inventory, not trash.
- **Board absence protocol (2026-08-21).** The board has delegated ALL gate
  decisions to the factory: PICK-GATEs resolve by ceo+strategy consensus,
  PULSE GATEs by design+qa playthrough consensus, fun-verdicts likewise.
  Ship without waiting. Every auto-decision is logged on the board with its
  rationale; the board retains retroactive veto. Never block on human presence.
- **You are the fun-judge.** Every game before portal submission: playtest URL →
  your verdict — *or* the delegated consensus above when you are away.
  Your recurring role stays ~15 min/game whenever you choose to show up.
- **Curated skills first, full catalogs after 2-3 shipped games.**

## Assets
- Hybrid stack: Kenney CC0 (structural) + AI-generated hero assets (originality)
  + jsfxr procedural SFX (original). `assets.json` provenance manifest per game.

## Roles (reuse existing 7 profiles, retargeted)
- research → 6-topic game research program + portal radar
- ceo → concept generation, kill-gates, portfolio verdicts, pipeline orchestration
- design → **experience owner from concept stage**: FEEL sections on every card
  (art/audio/drama direction), juice spec for feelers, asset packs at build
- engineering → Godot engine skills, build/export pipeline
- qa → smoke-playtest, QA skills, portal metric checks
- marketing → covers, metadata, portal listings
- strategy → scoring, whitespace scans, portfolio mix

## Pipeline (v2 constitution — 2026-08-21)
```
radar → concept cards → KILL-GATE → ★DESIGN GATE★ → board pick
→ W1 feeler (vibe floor) → QA → PULSE GATE → full build W2-W5
→ fun-verdict → portal submit
```
★DESIGN GATE★: design reads the surviving cards and co-signs a FEEL section
(pillars: art direction, audio direction, drama beats, the ONE payoff moment).
No FEEL signature → no build spec. Ceo may not skip it; the keeper cron checks it.
