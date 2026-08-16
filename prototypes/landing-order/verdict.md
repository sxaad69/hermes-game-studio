# LANDING ORDER — early-prototype feeler verdict (rule-12 gate)

Task: t_c1d5c402 · Date: 2026-08-16 · Skills: prototype-fast · Board directive: scope cut honored.

## Prototype brief (filled before coding)

- QUESTION: is the ATC tick-based ordering loop "flying" (tense, satisfying planning
  with visible stack-up + fuel pressure) or "queueing" (spreadsheet)? This is
  build-spec-02 kill-criterion #2: "fun-verdict wanted to fly, not queue" = KILL.
- CORE VERB: ordering decisions per tick — make-next (click chip), reroute (click
  plane → click other runway), hold (click plane → click HOLD circle). Two-click max.
- THROWAWAY: yes. prototypes/landing-order/index.html — single-file HTML5 canvas
  greybox, never promoted (the real build is Godot, W1-W5, and gets a rewrite).
- KEEP IF: fresh player does the verb unprompted in ~30s (L1 guided only); stack-up
  is VISIBLE and creates "one more landing" pull; soft clock = pressure on order,
  not reflex panic (min slack ≥ 1 tick for a reasonable policy, all tiers).
- KILL IF: verb only feels good after explanation; solving = reordering a list with
  no visible tension; art/audio required to make it fun; soft clock panics.

## What was built (few things only)

1. ONE core verb — ordering decisions. Tick-based integer-cell sim, no physics,
   deterministic (seeded patterns), spec §1.1 fuel rule: fuel = margin ×
   minimal_ticks_to_land (T1 3.0 → T3 1.8).
2. ONE interaction — click plane → click destination (queue chip = make-next, runway
   = reroute, HOLD circle = hold). No radio commands, no jargon.
3. ONE readable hook — the queue strip IS the plan + visible stack-up drama:
   planes visibly climb away on go-around (wrong order), fuel bars amber→red,
   touchdown payoff, incident budget (3), slack stats on the win banner.

## Evidence (headless CDP runs on the shipped file — evidence over vibes)

| Pass | Result | Incidents | Go-arounds | Slack p95/med/min (ticks) |
|------|--------|-----------|------------|---------------------------|
| L1 real mouse-input (fresh-player flow) | WON | 0 | 0 | 56 / 56 / 32 |
| L1 greedy policy | WON | 0 | 0 | 56 / 56 / 32 |
| L2 greedy policy | WON | 0 | 2 | 68 / 46 / 22 |
| L3 greedy policy (margin 2.25) | WON | 0 | 1 | 38 / 29 / 3 |
| L4 greedy policy (margin 1.8) | WON | 0 | 1 | 27 / 22 / 3 |

- Reroute B→A verified (queue + lane change). Hold cycle verified (orbit → rejoin →
  queue re-append). Console errors: 0.
- The slack curve degrades gracefully with density — the spec §1.3 signature of
  planning pressure, NOT panic collapse. A naive greedy policy (not even the solver)
  clears every tier with min slack ≥ 3 ticks. The soft clock's hard floor holds.

## Verdict: PULSE

The loop is structurally "flying", not "queueing":
- ordering is the ONLY verb — no reflex input, no timer, no parsing a radar;
- the soft clock holds at all densities with margin to spare, so the pressure reads
  as "plan your order", never "click faster";
- the drama layer (go-arounds as visible consequence, fuel-critical saves, touchdown
  payoff) is readable in greybox without art.

The pass-8 risk is reduced to the one thing a feeler cannot answer: whether a HUMAN
enjoys it. That is the product-overview-slice / human fun-verdict step.

## For the board

- PLAY IT: http://104.105.17.150/landing-order/ (file attached to the card works
  offline in any browser). L1 is guided; ramp to L4 for the pressure curve. SPACE
  pause, R restart, M mute.
- Honest caveats: no human has played it yet (L1 flow was driven by real mouse input
  headlessly); L4 (margin 1.8) is tight — calibration belongs to W1's solver
  window-width work; the shipped file carries a hidden LO API used for the headless
  pass (invisible in play).
- Decision rule: board plays → fun-verdict. PULSE stands unless the board's human
  verdict says "queueing" — then kill per spec, no appeal.
