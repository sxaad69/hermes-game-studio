---
name: games-doctrine
description: "The Game Studio Hermes never-idle doctrine — the games adaptation. Workers never wait: build -> smoke-test -> human fun-verdict -> portal submit -> metrics -> iterate/kill. Empty concept backlog -> research generates (games-research program). Idle is a bug. Hard rules carried from the SaaS era: 3-worker cap, no local models, kill-first gate, evidence over vibes. The only legal idle is a research scan that returns nothing, and the hunt resumes next cycle."
version: 1.0.0
author: hermesagency
license: MIT
metadata:
  hermes:
    tags: [game-studio, operations, never-idle, doctrine]
    related_skills: [games-research, portal-radar, board-report, debate, ceo]
---

# Games Doctrine (Never-Idle, Game Studio Edition)

The factory runs 24/7. Every worker hunts. Backlog depth is the CEO's problem,
never a worker's excuse to stop.

## Pipeline (the factory loop — v2 constitution 2026-08-21)
```
research proposes (evidence packs)
  -> kill-gate decides (red/blue; KILL/PARK/PITCH)
  -> ★DESIGN GATE★ (design co-signs a FEEL section on every surviving card;
     no FEEL signature = no build spec — ceo may not skip it)
  -> board pick
  -> W1 feeler (vibe floor: ambient loop + core-verb SFX + juice)
  -> smoke-playtest (headless, automated)
  -> PULSE GATE (board plays the feeler URL)
  -> full build (Godot, curated skills; design assets land at W2+)
  -> HUMAN FUN-VERDICT (board plays the URL)
  -> portal submit (Basic Launch)
  -> portal metrics (10+ min / 10-15% D1 / 80% conv)
  -> Full Launch (monetized) OR iterate OR kill
```

## Worker rules
1. Finish -> pull next. Never wait for handoffs.
2. Blocked on a human (credentials, money, out-of-scope) -> park as scheduled
   with ask-the-board + 4h default -> pull next.
3. **3-worker hard cap** (4GB/2vCPU VPS). Never spawn a 4th. Surplus stays
   ready/scheduled; the supervisor promotes parked cards as slots free.
4. **No local models. Ever.** Inference = opencode-go ox-alpha (fallback: OpenRouter
   stealth/ox-alpha). Any need beyond it -> ask-the-board immediately.
5. Never claim "nothing to do" — say so explicitly; generation fills it within
   one cycle. The dispatcher never idles >4h: when the idea pool is empty, mine
   the Boneyard (below).
6. **Repo law.** Every game = its own GitHub repo from W1 start. Code AND all
   assets (art/audio/fonts/SFX + `assets.json` manifest) live in that repo and
   push on every task completion. Feeler/playtest distribution = GitHub Pages
   from the repo. DONE means remote tip == local tip — an unpushed build is
   not a finished task. The VPS disk is scratch; GitHub is truth.

## Kill-first gate (mandatory before ANY build card)
Every concept passes red/blue debate with these mandatory questions:
- Originality: is this a clone/reskin? (portal QA rejects those)
- Testability: can we auto-verify it headless (solver/smoke-play)?
- Build cost: Godot <1-2 weeks (2D or low-poly 3D), export loads fast on web?
- Asset fit: does the hybrid pipeline produce consistent art?
- Fun-risk: is the fun driver a mechanic we can implement and tune, or
  a vibe we cannot?
- MONETIZATION (board mandate, Task 7): what is the revenue model (rewarded
  ads at natural breaks, premium, sponsorship)? Does the mechanic support it
  (hints, restart points, session length, replay)? Portal earning benchmarks
  for the genre? "Ads later, we'll figure it out" = PARK until a model exists.
A single hard NO on originality or testability = automatic KILL. A gate that
passes 100% is not a gate. Monetization is a gate, not an afterthought:
no concept passes without a revenue model + genre benchmarks.

## ★DESIGN GATE★ (mandatory between kill-gate and build spec)
The board killed LIE TO ME's greybox as DULL on 2026-08-21 while QA called the
same build "drama LANDS" — the pipeline had shipped a game whose soul was decided
entirely by market data. Never again:
1. After kill-gate PITCH verdicts, design reads every surviving card and co-signs
   a **FEEL section**: art direction, audio direction, drama beats, and THE ONE
   PAYOFF MOMENT (what the player physically feels when the core promise lands).
2. No FEEL signature = no build spec fires. Ceo cannot waive it; the
   pipeline-keeper cron audits for unsigned cards.
3. Design is honest, not protective: if the mechanic itself is flat, the gate
   says CONFIRM DEAD (see design review t_ee3f18c6 for the standard).
4. Narrative/fantasy concepts: "the payoff moment must be juiced even in W1 —
   a greybox may be ugly, never mute-and-motionless at its core beat."

## Repo law (board mandate 2026-08-21)
- One GitHub repo per game, created at W1 start (`sxaad69/<game-slug>`).
- Code AND all assets (art/audio/fonts/SFX) live in `<repo>/assets/` with the
  `assets.json` provenance manifest. NOTHING asset-wise lives server-only.
- Push on every task completion. Playtests ship via GitHub Pages from the repo.
- The pipeline-keeper cron audits hourly: missing remote / behind remote /
  orphan asset dirs → auto-fix task + Telegram alert.
- Retroactive: `set-piece-master` must be rescued to GitHub (no remote as of
  2026-08-21).

## Boneyard (dead concepts are inventory, not trash)
`wiki/boneyard.md` catalogs every KILLed/PARKed/board-rejected concept with:
rejection reason, date, which gate/verdict killed it, and explicit revival
criteria (e.g. SHADOW FORM: "promotes if a 2D pitch dies"). When generation
cannot find fresh whitespace, workers mine the boneyard against current radar
data: revive with a new twist (re-entering at kill-gate) or formally bury with
a written reason. Mining results report to Telegram.

## Early-prototype feeler (board mandate, Task 11 — the SCOPE GUARDRAIL)
The feeler before any full build is a MOST-VIABLE prototype, NOT a slice:
- **≤3 elements**: ONE core verb + ONE primitive interaction + ONE readable hook.
- **≤5 DECISIONS.md entries** — past 5 = you're building a slice, CUT.
- **NO** spec constants, tiered levels, solvers, test harnesses. The spec's numbers
  are W1 fodder; the feeler judges the LOOP.
- **AUDIO/JUICE REQUIRED (board amendment 2026-08-21 — "feelers must carry vibe";
  strengthened after design review t_ee3f18c6)**: a feeler MUST ship with ONE
  ambient music loop + core-action SFX stubs + minimal screen-shake/hit-flash
  juice on the core verb. For narrative/fantasy concepts the ONE PAYOFF MOMENT
  is juiced even in W1 — a greybox may be ugly, never mute-and-motionless at
  its core beat. Procedural WebAudio / jsfxr-style synthesis inside the single
  HTML file (no asset downloads, no build step). This is polish on the ONE verb,
  NOT extra elements: the ≤3 elements / ≤5 DECISIONS / ~15-20min caps are
  UNCHANGED. Silence kills a pulse verdict — a loop can verify correct and
  still be dead to play (LIE TO ME, pass 21).
- **If it takes more than ~15-20 min of actual work, the scope is too big —
  cut features, don't extend time.** The runtime cap is an upper bound, never
  the target.
- Single-file HTML greybox (opens in any browser) — no engine, no build step.
- Output: PULSE verdict → product overview slice → product verdict; or FLAT → kill.

## CEO generation priority
1. Sprint/work decomposition of in-flight games
2. New concept generation from whitespace scan (games-research topic 4)
3. Game hardening: juice (game-feel), levels, performance, cover assets
4. Portal submission pipeline (the finished-games lane)

## Ritual trigger (board-supervisor)
- Count running workers; if >=3, dispatch nothing, report slots full
- If running <3 AND ready exhausted: promote parked scheduled cards first, then
  trigger CEO generation (research -> concepts -> gate)
- Report: moved, blocked (with asks), generated, next generation due; [SILENT]
  if healthy
