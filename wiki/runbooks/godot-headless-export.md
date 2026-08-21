# Godot Headless Web Export on the VPS

Goal: export a Godot 4.x project to HTML5/WASM with no display, serve it via
nginx, and smoke-test it in headless Chromium.

## Install
```bash
# Godot 4.x (headless-capable) — download the Linux x86_64 binary from godotengine.org
# Example for 4.3+: godot-4.3-stable_linux.x86_64.zip
curl -LO https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_linux.x86_64.zip
unzip Godot_v4.3-stable_linux.x86_64.zip
mv Godot_v4.3-stable_linux.x86_64 /usr/local/bin/godot
chmod +x /usr/local/bin/godot
godot --version   # sanity check

# Web export templates
curl -LO https://github.com/godotengine/godot/releases/download/4.3-stable/Godot_v4.3-stable_export_templates.tpz
# extract to ~/.local/share/godot/export_templates/4.3.stable/ (rename the dir properly)
```
Note: single-threaded web export (Godot 4.3+) avoids the SharedArrayBuffer /
COOP-COEP header requirement — preferred for portal hosting.

## Export (headless)
```bash
godot --headless --path <project> --export-release "Web" <project>/build/web/index.html
```
The "Web" preset must exist in `export_presets.cfg` (a worker sets this up via
the godot-export skill / editor headless `--headless --export-preset` flow).

## Serve via nginx
```conf
server {
  listen 8080;
  root /opt/games/<game>/build/web;
  index index.html;
  location / { try_files $uri $uri/ =404; }
}
```
(Add COOP/COEP headers only if a threaded export is used.)

## Smoke-test
Use the chromium-cdp daemon (CDP 127.0.0.1:9222) + Playwright MCP:
navigate to `http://127.0.0.1:8080/`, assert load <10s, reach gameplay,
inject inputs, screenshot. Full procedure in `skills/smoke-playtest/SKILL.md`.

## Public playtest URL (Cloudflare quick tunnel)
The games server (nginx on port 8080) is fronted by a Cloudflare quick tunnel
so every playtest gets a public https URL without a domain:

```bash
systemctl status cf-games                 # active = tunnel up
journalctl -u cf-games | rg -o 'https://[a-z0-9-]+\.trycloudflare\.com' | tail -1
```

The URL changes on each tunnel restart (ephemeral). For a stable URL during a
playtest session, keep the tunnel running and send the current URL to the board.
Unit file: /etc/systemd/system/cf-games.service.

## Size discipline
- No hard size cap (board decision 2026-08-21: 3D allowed). Brotli-compressed
  serving + texture/audio compression + module stripping still mandatory;
  gate on first-load <10s on broadband rather than raw MB.
- Verify with: `du -sh build/web && find build/web -type f | wc -l`
