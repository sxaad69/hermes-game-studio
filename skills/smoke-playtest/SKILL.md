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

## Pitfalls (Godot web exports — learned on Rulebreaker QA)

1. NEVER call `canvas.getContext(...)` from page JS on the game canvas. It
   returns/steals the engine's WebGL context (or creates one with wrong
   attributes) and the game then renders a BLACK canvas. Check WebGL presence
   with `!!window.WebGL2RenderingContext` only, and read pixels by drawing the
   game canvas into a TEMP 2D canvas (`t.getContext('2d').drawImage(gameCanvas,
   ...)`) then getImageData from the temp.
2. Headless Godot layout (rects from a `--headless` probe) DOES NOT match the
   browser render: font-metric differences shift UI ~20-40 game px. Never click
   using headless-measured coordinates. Instead detect the ACTUAL rendered
   controls in the browser: buttons are paper-light rectangles with dark
   borders (connected-component scan of the canvas pixels by color), or OCR
   word boxes (tesseract TSV) for text positions.
3. The CDP daemon window size is whatever it was launched with (e.g. 780x493,
   not the game's 1152x648). Always compute the game->page transform live from
   `canvas.getBoundingClientRect()`: s = min(w/1152, h/648), ox = x + (w-1152*s)/2,
   oy = y + (h-648*s)/2. Never hardcode offsets.
4. CDP `Input.insertText` (IME) is flaky for Godot LineEdits headless. Type
   with per-character `Input.dispatchKeyEvent` (keyDown with `text` + keyUp)
   and submit with an Enter key event.
5. OCR identify-matching: match by token RECALL against known rule strings
   (fraction of rule tokens present in OCR), not full-string equality — the
   status bar ("EMPLOYEE STATUS: ... FAILURES: N") and other chrome leak into
   wide crop bands.
6. Game state detection: `canvas.toDataURL()`/getImageData via JS is FRESH;
   `Page.captureScreenshot` can return stale compositor frames (swiftshader).
7. Load-time gate: wait for a stable canvas hash (a static title screen), not
   just canvas existence — the Godot loading screen has a static progress bar
   between updates and can false-stabilize.
8. Screenshots of "approved/solved" moments must be taken BEFORE slow OCR
   steps: tesseract takes ~1s+, and the game's 0.95s transition will have
   moved to the next page by the time you capture after OCR.
9. Interactive clicks on the LONG-RUNNING shared CDP daemon are unreliable
   (events reach the canvas but the engine ignores them — occlusion/focus
   quirk of a shared tab). Use it only for load/console-health checks; drive
   gameplay on a DEDICATED headless chromium (`--remote-debugging-port=<rand>`
   + `--window-size=1152,648` so canvas coords map 1:1).
10. Engine load-timing: poll `canvas.toDataURL().length` for first-frame
    detection and `document.getElementById('status')` removal for overlay-gone;
    read per-resource gz transfer from `performance.getEntriesByType('resource')
    .transferSize` (honest on-the-wire bytes, matches curl --compressed).
    Clear the browser cache + disable cache first for cold numbers.
