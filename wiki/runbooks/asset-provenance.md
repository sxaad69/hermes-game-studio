# Asset Sourcing & Provenance

Every game ships an `assets.json` manifest proving asset legality + originality.
This is our defense against portal QA rejection for "unoriginal content
(clones/asset flips)" and future AI-disclosure policies.

## Hybrid sourcing stack

| Layer | Source | License | Use |
|---|---|---|---|
| Structural | Kenney.nl | CC0 (verify per-pack) | base tiles, UI, fonts, generic props |
| Hero/identity | AI-generated (image_gen) + programmatic post (palette-lock, outline, resize) | commercial-licensed tool + human/agent modification = practice-original | main character, key art, icon |
| Audio SFX | jsfxr/sfxr procedural generation | generated-original, zero risk | all sound effects |
| Audio music | Kenney CC0 loops | CC0 | background loops |

## Rules
- Never ship a raw Kenney pack unchanged as the whole visual identity — that is
  the "asset flip" failure mode. Modify (palette, outline, scale) or combine.
- AI assets must be post-processed for consistency (locked palette, uniform
  outline) so the game has ONE art style — portal QA rejects inconsistent art.
- Record EVERY asset in assets.json at build time, not after the fact.

## assets.json schema
```json
{
  "game": "<name>",
  "date": "YYYY-MM-DD",
  "assets": [
    {"name": "<file>", "source": "kenney|ai-gen|jsfxr|other",
     "license": "CC0|commercial-ok|generated-original",
     "modified": ["palette-shift", "outline", "resize"]}
  ]
}
```

## Checks
- `assets.json` complete and committed with the game repo before portal submit.
- No asset with "unknown" license source.
- All AI assets list the generating tool (for disclosure if asked).
