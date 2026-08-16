---
name: godot-export
description: >
  Export and build a Godot 4.7 project for distribution: install export templates,
  define export presets (Windows/macOS/Linux/Web/Android), run headless command-line
  exports for CI, and handle web (HTML5) COOP/COEP and dedicated-server/headless
  builds. Use when exporting a Godot game, configuring export_presets.cfg, building
  for web/desktop/mobile, or automating builds from the command line.
---

# Godot Export & Builds (4.x)

Turn a project into runnable platform builds via export presets and the command line, and
handle the web/dedicated-server gotchas. Targets **Godot 4.7**.

## When to use

- Use when producing a shippable build: installing export templates, creating/editing
  export presets, exporting from the editor or headless CLI (CI), or troubleshooting web
  (HTML5) and dedicated-server exports.

**When *not* to use:** storefront publishing flows → `steam-publish`/`itch-publish`; the
networking code of a server → `godot-multiplayer` (this skill covers building it headless).

## Core workflow

1. **Install export templates** matching your engine version: Editor menu >
   *Manage Export Templates* (download), or install the `.tpz` offline. Versions must
   match the editor exactly.
2. **Add export presets** in *Project > Export*: pick a platform (Windows Desktop, macOS,
   Linux, Web, Android, iOS), set the export path, icons, features, and resource
   include/exclude filters. Presets are saved to `export_presets.cfg`.
3. **Export from the editor** with *Export Project* (release) or *Export PCK/ZIP*.
4. **Or export headless from the CLI** for automation/CI using
   `--export-release "<preset name>" <output path>`.
5. **Per platform:** Web needs cross-origin isolation (COOP/COEP) for threads; Android
   needs the SDK/keystore; macOS/iOS need signing for distribution.
6. **Smoke-test the build** on the target before shipping — exported builds use `res://`
   read-only; write to `user://`.

## Patterns

### 1. Headless CLI export (CI-friendly)

```bash
# Preset name must match exactly what's in Project > Export (quote it).
# Run from the project directory (where project.godot lives).
godot --headless --export-release "Windows Desktop" build/windows/game.exe
godot --headless --export-release "Linux/X11"       build/linux/game.x86_64
godot --headless --export-release "Web"             build/web/index.html

# Debug build (includes debug symbols / remote debug):
godot --headless --export-debug "Windows Desktop" build/windows/game_debug.exe

# Export only the data pack (no executable):
godot --headless --export-pack "Linux/X11" build/game.pck
```

### 2. Run a project headless (dedicated server / tests)

```bash
# No window/GPU — for a server build or automated runs.
godot --headless --path . res://server_main.tscn
# Quit after N main-loop iterations (frames, NOT seconds) — handy for a headless smoke test:
godot --headless --path . --quit-after 600
```

### 3. Detect the build context at runtime

```gdscript
func _ready() -> void:
    if OS.has_feature("dedicated_server") or DisplayServer.get_name() == "headless":
        _start_server_only()          # skip rendering/UI on a headless server
    if OS.has_feature("web"):
        _apply_web_tweaks()
    # Custom feature tags (added per preset) are also queryable:
    # if OS.has_feature("demo"): limit_content()
```

### 4. Choose write paths that survive export

```gdscript
# res:// is READ-ONLY in exported games. Always write to user://.
func save_path() -> String:
    return "user://savegame.tres"     # resolves to the OS app-data dir

func _ready() -> void:
    print(OS.get_user_data_dir())     # where user:// actually lives
```

## Pitfalls

- **"No export template found".** Templates must match the exact editor version (incl.
  beta/rc). Re-download via *Manage Export Templates* after upgrading Godot.
- **Preset name mismatch in CLI.** `--export-release "Windows"` fails if the preset is
  named `"Windows Desktop"`. Names are case- and space-sensitive; quote them.
- **Web build shows a blank page / threads error.** HTML5 builds that use threads require
  the server to send `Cross-Origin-Opener-Policy: same-origin` and
  `Cross-Origin-Embedder-Policy: require-corp` (cross-origin isolation for
  `SharedArrayBuffer`). Must be served over HTTP(S), not opened as a `file://`. itch.io has
  a "SharedArrayBuffer support" toggle for this.
- **Game refuses to start on plain-http public IPs (Secure Context).** The generated
  loader (`Engine.getMissingFeatures`) unconditionally requires a secure context, even
  with threads disabled — `http://<public-ip>:port` fails the check and the shell shows
  an error notice instead of the game. localhost/127.0.0.1 counts as secure, so QA on
  localhost masks this. If the deployment must stay plain-http, post-process the
  generated `index.js` after every export to drop the `isSecureContext` missing-feature
  push (game uses only WebGL2/fetch/IndexedDB, all available on insecure origins).
- **No audio on plain http (AudioWorklet).** Godot's web audio driver requires
  AudioWorklet, which Chrome only exposes in secure contexts. On an insecure origin the
  engine logs "All audio drivers failed, falling back to the dummy driver" — the game
  runs silently. Reproducible: public-IP runs fail, localhost runs pass
  (`window.isSecureContext` / `audioWorklet` probe). Only HTTPS fixes it; plan audio QA
  on a secure origin and warn stakeholders about http-only deployments.
- **Mobile browsers: virtual keyboard never appears when tapping a LineEdit.** Two export
  defaults cause this. (1) Godot's default HTML shell ships
  `<meta name="viewport" content="width=device-width, user-scalable=no, ...">` — iOS
  Safari refuses to summon the keyboard when `user-scalable=no` is set. Fix: set
  `html/head_include` in `export_presets.cfg` to emit a later viewport meta with
  `user-scalable=yes` (last meta wins; the shell default stays, so re-exports keep the
  fix). (2) The engine's hidden-textarea keyboard fallback is gated on
  `html/experimental_virtual_keyboard` — it defaults to `false`; set it to `true` so
  `GodotConfig.virtual_keyboard` enables `DisplayVK` on touch devices (Android + desktop
  touch). Verify after patching: `grep -o 'user-scalable=[a-z]*\|experimentalVK[^,]*'
  build/web/index.html` should show `user-scalable=yes` and `"experimentalVK":true`. This
  also breaks headless/QA bots that rely on the keyboard — re-check `text_submitted` flows
  after changing it.
- **Writing to `res://` at runtime fails** in exports (read-only, packed). Use `user://`.
- **Missing resources in the build.** Non-resource files (e.g. external `.json`, `.txt`)
  are not auto-included — add them via the preset's *Resources > Filters to export
  non-resource files* (e.g. `*.json`).
- **Android export needs setup**: Android SDK/JDK paths in Editor Settings, a debug or
  release **keystore**, and the `INTERNET` permission for networked games.
- **macOS/iOS distribution requires signing/notarization**; unsigned macOS apps are
  blocked by Gatekeeper.
- **Debug vs release.** `--export-debug` enables remote debugging and debug checks; ship
  `--export-release`.

## References

- For the `export_presets.cfg` structure, all useful CLI flags, custom feature tags,
  PCK/expansion patching, encryption, and per-platform setup (Android keystore, macOS
  signing, web headers), read `references/presets-and-cli.md`.

## Related skills

- `godot-multiplayer` — the dedicated-server code you export headless.
- `steam-publish` / `itch-publish` — getting the build to players.
- `prototype-fast` / `game-jam` — quick web/desktop builds for sharing.
