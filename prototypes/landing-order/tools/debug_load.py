#!/usr/bin/env python3
"""Debug: load the feeler in CDP, dump page state + console."""
import asyncio, json, time, urllib.parse, urllib.request
import websockets

CDP_HTTP = "http://127.0.0.1:9222"
URL = "file:///root/.hermes/kanban/boards/games/workspaces/t_c1d5c402/prototypes/landing-order/index.html"

def http_json(path, method="GET"):
    req = urllib.request.Request(CDP_HTTP + path, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

async def main():
    target = http_json(f"/json/new?{urllib.parse.quote(URL, safe='')}", method="PUT")
    ws = await websockets.connect(target["webSocketDebuggerUrl"], max_size=128*1024*1024)
    msgs = []
    async def rpc(method, params=None, mid=None):
        mid = mid or int(time.time()*1000) % 10**9
        await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=30)
            msg = json.loads(raw)
            if msg.get("id") == mid:
                return msg.get("result", {})
            if msg.get("method") in ("Runtime.exceptionThrown", "Log.entryAdded", "Runtime.consoleAPICalled"):
                msgs.append(msg)
    await rpc("Page.enable"); await rpc("Runtime.enable"); await rpc("Log.enable")
    await rpc("Page.navigate", {"url": URL})
    await asyncio.sleep(4)
    for expr in ["document.readyState", "document.title",
                 "document.getElementById('c') ? 'canvas exists' : 'NO canvas'",
                 "typeof LO", "window.location.href",
                 "document.body ? document.body.innerHTML.slice(0,200) : 'no body'"]:
        try:
            res = await rpc("Runtime.evaluate", {"expression": expr, "returnByValue": True})
            print(expr, "=>", json.dumps(res.get("result", {}).get("value"))[:300])
        except Exception as e:
            print(expr, "ERR", e)
    print("--- captured events ---")
    for m in msgs[:10]:
        print(json.dumps(m)[:400])
    await ws.close()
    try: http_json(f"/json/close/{target['id']}")
    except Exception: pass

asyncio.run(main())
