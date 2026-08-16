# DECISIONS.md — t_c1d5c402 LANDING ORDER feeler (rule-12 early-prototype gate)

Board directive (mid-run, chairman): scope guardrail — vertical slice, not a feeler:
≤3 elements, ≤5 DECISIONS.md entries, no solver/tiered-levels/sound/test-harness.
Complied: cut here, delivered verdict + playable greybox. Partial > complete.

## PROTOTYPE BRIEF (prototype-fast, filled before coding)

QUESTION: Is the ATC tick-based ordering loop "flying" (tense, satisfying planning
with visible stack-up + fuel pressure) or "queueing" (spreadsheet)? = spec-02
kill-criterion #2 ("wanted to fly, not queue" = KILL, no appeal).
CORE VERB: ordering decisions per tick (make-next, reroute, hold). Two-click max.
THROWAWAY: yes — prototypes/landing-order/, single-file HTML5 greybox, never promoted.
TIMEBOX: 60-90 min. KEEP IF: fresh player does the verb unprompted in ~30s (L1 hints
only); stack-up visible + "one more landing" pull; soft clock reads as pressure-on-order,
not reflex panic (min slack ≥ 1 tick for a reasonable policy). KILL IF: verb only feels
good after explanation; solving = reordering a list with no visible tension; art/audio
would be required to make it fun; soft clock panics (greedy policy can't clear with
slack ≥ 0).

## Decisions (5)

1. Single-file HTML5 canvas greybox, not Godot — rule-12 wants near-zero resources;
   one file = board-presentable (any browser), attachable, headless-testable via CDP.
2. Sim fidelity = build-spec-02 §1.1 fuel rule exactly (fuel = margin × minimal_ticks;
   T1 3.0 → T3 1.8) so the verdict is honest evidence about the spec's soft clock.
3. Interaction = spec §2 model: the queue strip IS the plan; planes auto-queue on
   arrival; player reorders (chip = make-next), reroutes (plane → other runway),
   holds (plane → HOLD circle). No radio commands, no jargon.
4. Go-around = the visible consequence of wrong ordering (plane climbs away, re-joins
   short-final, ~18-20 ticks burned). 3 incidents = fail; missed landing ≠ fail.
5. Instrumentation = live HUD (fuel bars, CRITICAL count, go-arounds, incidents) +
   win-banner slack p95/med/min (spec §1.2 metric) — the board sees planning margin,
   not vibes.

## Playtest log (evidence, headless CDP — all on the shipped file)

- L1 real mouse-input run (fresh-player simulation, two-click verb): WON, 0 incidents,
  0 go-arounds, slack 56/56/32. Hint flow advanced correctly through select→chip→next.
- Greedy-policy passes (same code path): L1 0 incidents slack 56/56/32 · L2 0 slack
  68/46/22 · L3 0 slack 38/29/3 · L4 0 slack 27/22/3. Graceful degradation = planning
  pressure, NOT panic collapse (spec §1.3 signature; min slack ≥ 3 at every tier).
- Reroute B→A verified (queue + lane move). Hold cycle verified (orbit 12t → rejoin
  → queue re-append). Console errors: 0.

## VERDICT: PULSE

The feeler proves the loop is structurally "flying": ordering is the only verb, the
soft clock holds at all densities with margin to spare (greedy, non-optimal policy
clears L4 at margin 1.8 with min slack 3), and the drama layer (go-arounds, fuel
critical, touchdown payoff) is visible in greybox. The pass-8 risk ("wanted to fly,
not queue") is now reduced to a HUMAN fun-verdict on the playable — the board plays
http://104.105.17.150/landing-order/ (attached file works offline too). Caveat: no
human has played it yet; L4 margin 1.8 is tight; calibration data belongs to W1's
solver window-width work. PULSE → W1 (t_448c7043) may proceed once pick-gate lands.
