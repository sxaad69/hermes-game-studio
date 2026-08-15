---
name: portal-publish
description: "Submits a Godot web export to web-game portals (CrazyGames, Poki, itch.io). Covers SDK integration (CrazyGames/Poki), metadata (title, description, controls, cover images/video), technical compliance (build size, PEGI12, delta-time physics, land-in-gameplay), and the Basic Launch → Full Launch progression. Also maintains the per-game assets.json provenance manifest required to survive human QA originality review."
version: 1.0.0
author: hermesagency
license: MIT
metadata:
  hermes:
    tags: [game-studio, publish, crazygames, poki, itch, sdk]
    related_skills: [godot-export, smoke-playtest, itch-publish]
---

# Portal Publish

Takes a smoke-verified, human-fun-approved web build and ships it to portals.

## Pre-submission checklist (all must pass)
- Build: initial download <50MB (target <20MB), total <250MB, <1500 files
- Load <10s; lands directly in gameplay; onboarding skippable
- PEGI12, no kid-targeted content, no external ads, no portal branding
- Original (not a clone/reskin/asset flip): proven by assets.json provenance
- English text present; controls overlay; delta-time physics (no frame-rate bugs)
- Unique name + iconography (not confusable with existing games)

## Per-portal
### CrazyGames
- Basic Launch: upload build, metadata, cover images; SDK optional; monetization off
- Metric gate: 7-21 days, 500+ plays; benchmarks = 10+ min playtime, 10-15% D1,
  80%+ conversion → invited to Full Launch
- Full Launch: integrate CrazyGames SDK (ads via SDK only, rewards/midgame/banner;
  pause + block input during ads; mute audio), account integration, cloud saves
- Payout: €100 monthly threshold via Tipalti (wire/ACH/PayPal)
### Poki
- Integrate Poki SDK (loading events, ads at natural breaks, gameplay rules);
  Poki curates heavily — quality and uniqueness bar is high
### itch.io
- Open publishing; upload via butler; set your own price/monetization; no gate

## assets.json (per game, committed with the repo)
```
{ "game": "<name>", "assets": [
  {"name": "tileset.png", "source": "kenney", "license": "CC0", "modified": ["palette-shift"]},
  {"name": "hero.png", "source": "ai-gen", "tool": "image_gen", "license": "commercial-ok", "modified": ["outline","resize"]},
  {"name": "sfx-jump.wav", "source": "jsfxr", "license": "generated-original"}
]}
```

## Rules
- Never fake a sandbox/QA result; never submit before human fun-verdict
- On rejection: relay the exact QA feedback; fix; resubmit (not a new game)
- Record submission status + metrics on the games board card
