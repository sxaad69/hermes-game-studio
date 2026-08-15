# Game Studio Hermes

An autonomous agent factory that builds and ships web games. Godot 4 -> headless
web export -> portal submission (CrazyGames / Poki / itch.io) -> metric-driven
iterate/kill. The human board judges what agents cannot: **fun**.

## Structure
- `charter/` — mission, category strategy, KPI gates, doctrine
- `skills/` — custom agency skills (games-research, portal-radar, smoke-playtest,
  portal-publish, games-doctrine)
- `vendor/` — curated third-party gamedev skills (awesome-gamedev-agent-skills
  Apache-2.0, Claude-Code-Game-Studios MIT) with attribution
- `scripts/` — radar sweep, headless godot export
- `templates/` — concept card, playtest report
- `wiki/` — runbooks (godot headless export, asset provenance), decision log

## Pipeline
research -> kill-gate -> build (Godot, curated skills) -> smoke-playtest ->
human fun-verdict -> portal Basic Launch -> metrics -> Full Launch | iterate | kill

## Operators
- VPS: `/root/hermes-game-studio` (clone), `~/.hermes/skills/*` symlink farm
- GitHub: `sxaad69/hermes-game-studio` (public)

See `charter/README.md` for the full doctrine.
