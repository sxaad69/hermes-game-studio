---
name: smoke-playtest
description: "Headless smoke-playtest for HTML5 web games on the VPS. Loads a Godot web export (or any HTML5 game) in the chromium-cdp daemon via Playwright MCP, injects scripted inputs (clicks/keys), asserts the game reaches and stays in gameplay without errors, captures screenshots at defined checkpoints, and produces a pass/fail + evidence report. The automated proxy for 'does it run' — it never judges fun (that is the human board's job)."
version: 1.0.0
author: hermesagency
license: MIT
metadata:
  hermes:
    tags: [game-studio, testing, qa, playwright, godot]
    related_skills: [game-dev-qa-test, godot-export]
---

# Smoke-Playtest (Headless)

The factory's automated test gate between build and human fun-verdict.

## Preconditions
- chromium-cdp daemon active (CDP on 127.0.0.1:9222)
- Game served over HTTP(S) (nginx on the VPS, or a local port)
- Playwright MCP configured (it connects to the CDP endpoint)

## Procedure
1. Navigate to the game URL.
2. Assert load completes in <10s; record console errors.
3. Skip/close any menu; assert the game reaches gameplay (first interactive frame).
4. Inject a scripted interaction sequence (from the concept card's core loop):
   tap/click, one or two keys, wait, screenshot.
5. Assert: no crash, no black screen, game state advanced (score/level changed).
6. Screenshot at each checkpoint; save to the task workspace.
7. Repeat for 3 interaction runs to catch flakiness (portal requirement:
   physics consistent across refresh rates — run a high-fps pass too).

## Report format
```
SMOKE-PLAYTEST — <game name>
LOAD: <s elapsed, pass/fail>
CONSOLE ERRORS: <count + top 3>
GAMEPLAY REACHED: pass/fail
INTERACTION RUNS: 3/3 pass | N failed
SCREENSHOTS: <paths>
VERDICT: RUNNABLE | NEEDS-FIX (list) | NOT-PLAYABLE
FUN: <explicitly NOT evaluated — human board verdict required>
```

Rules: never claim "works" without the evidence; never evaluate fun; if the
game can't be loaded after 3 attempts, mark NOT-PLAYABLE with the console
errors rather than forcing a pass.
