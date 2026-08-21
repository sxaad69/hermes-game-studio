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

## Pipeline (the factory loop)
```
research proposes (evidence packs)
  -> kill-gate decides (red/blue; KILL/PARK/PITCH)
  -> concept card (mechanic/twist/theme/asset-plan/testability)
  -> build (Godot, curated skills)
  -> smoke-playtest (headless, automated)
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
4. **No local models. Ever.** Inference = opencode-go deepseek-flash. Any need
   beyond it -> ask-the-board immediately. "Real local inference" is never a
   reason to consume box resources.
5. Never claim "nothing to do" — say so explicitly; generation fills it within
   one cycle.

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

## Early-prototype feeler (board mandate, Task 11 — the SCOPE GUARDRAIL)
The feeler before any full build is a MOST-VIABLE prototype, NOT a slice:
- **≤3 elements**: ONE core verb + ONE primitive interaction + ONE readable hook.
- **≤5 DECISIONS.md entries** — past 5 = you're building a slice, CUT.
- **NO** spec constants, tiered levels, solvers, test harnesses. The spec's numbers
  are W1 fodder; the feeler judges the LOOP.
- **AUDIO/JUICE REQUIRED-BY-OPTION (board amendment 2026-08-21 — "feelers must carry
  vibe")**: a feeler SHOULD ship with ONE ambient music loop + core-action SFX stubs +
  minimal screen-shake/hit-flash juice on the core verb. Procedural WebAudio / jsfxr-
  style synthesis inside the single HTML file (no asset downloads, no build step).
  This is polish on the ONE verb, NOT extra elements: the ≤3 elements / ≤5 DECISIONS /
  ~15-20min caps are UNCHANGED. Silence is allowed to kill a pulse verdict — a loop
  can verify correct and still be dead to play (LIE TO ME, pass 21).
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
