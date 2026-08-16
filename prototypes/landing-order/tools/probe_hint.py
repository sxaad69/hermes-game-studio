#!/usr/bin/env python3
"""Probe the chip-click hint advance: API path vs real click path."""
import asyncio, json, time, urllib.parse, urllib.request
import websockets

CDP_HTTP = "http://127.0.0.1:9222"
URL = "http://127.0.0.1/landing-order/index.html"

def http_json(path, method="GET"):
    req = urllib.request.Request(CDP_HTTP + path, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

async def main():
    target = http_json(f"/json/new?{urllib.parse.quote(URL, safe='')}", method="PUT")
    ws = await websockets.connect(target["webSocketDebuggerUrl"], max_size=64*1024*1024)
    async def rpc(method, params=None, mid=None):
        mid = mid or int(time.time()*1000) % 10**9
        await ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            raw = await asyncio.wait_for(ws.recv(), timeout=30)
            msg = json.loads(raw)
            if msg.get("id") == mid:
                return msg.get("result", {})
    async def ev(expr):
        res = await rpc("Runtime.evaluate", {"expression": expr, "returnByValue": True})
        if "exceptionDetails" in res:
            return "EXC: " + res["exceptionDetails"].get("exception", {}).get("description", "")[:200]
        return res.get("result", {}).get("value")
    await rpc("Page.enable"); await rpc("Runtime.enable")
    await rpc("Page.navigate", {"url": URL})
    for _ in range(80):
        if await ev("typeof LO === 'object' && !!LO.state"): break
        await asyncio.sleep(0.2)

    print("== API path ==")
    print(await ev("LO.setup(1); LO.fastForward(5); JSON.stringify(LO.state.hint)"))
    print(await ev("LO.select(0); JSON.stringify(LO.state.hint)"))
    print(await ev("LO.makeNext(0); JSON.stringify(LO.state.hint)"))
    print("queues:", await ev("JSON.stringify(LO.state.queues)"))
    print("front0:", await ev("LO.state.queues.A[0]"))

    print("== click path ==")
    await ev("LO.setup(1); LO.fastForward(5); window.__clicks=0; window.__raw=[]; "
             "document.addEventListener('click',(e)=>window.__raw.push([e.clientX,e.clientY]),true); "
             "document.getElementById('c').addEventListener('click',()=>window.__clicks++); 0")
    rect = json.loads(await ev("JSON.stringify((()=>{const r=document.getElementById('c').getBoundingClientRect();return {l:r.left,t:r.top,w:r.width,h:r.height}})())"))
    print("rect:", rect)
    def g2c(gx, gy): return rect["l"] + gx*rect["w"]/900, rect["t"] + gy*rect["h"]/640
    async def click(x, y):
        for t, b in [("mousePressed","left"), ("mouseReleased","left")]:
            await rpc("Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": b, "clickCount": 1})
    # select plane 0 via real click
    snap = json.loads(await ev("JSON.stringify(LO.snapshot())"))
    p0 = [p for p in snap["planes"] if p["id"]==0 and not p["wait"]][0]
    cx, cy = g2c(p0["x"]*12, p0["y"]*12)
    print("plane0 at game", (p0["x"]*12, p0["y"]*12), "-> client", (round(cx,1), round(cy,1)))
    await click(cx, cy); await asyncio.sleep(0.05)
    print("t+0.05: selected =", await ev("LO.state.selected"), "| hint =", await ev("LO.state.hint && LO.state.hint.txt"),
          "| clicks =", await ev("window.__clicks"), "| raw =", await ev("JSON.stringify(window.__raw)"),
          "| events =", await ev("JSON.stringify(LO.state.events.slice(0,2))"))
    await asyncio.sleep(0.3)
    print("t+0.35: selected =", await ev("LO.state.selected"), "| hint =", await ev("LO.state.hint && LO.state.hint.txt"))
    # click the chip
    snap = json.loads(await ev("JSON.stringify(LO.snapshot())"))
    if 0 not in snap["queues"]["A"]:
        print("plane0 not in queue A! queues =", snap["queues"]); return
    qi = snap["queues"]["A"].index(0)
    chip = (10 + min(880-20,240)/2, 486+22+qi*26+11)
    cx, cy = g2c(*chip)
    print("chip game coords:", chip, "-> client:", (round(cx,1), round(cy,1)))
    await click(cx, cy); await asyncio.sleep(0.05)
    print("t+0.05: selected =", await ev("LO.state.selected"), "| hint =", await ev("LO.state.hint && LO.state.hint.txt"),
          "| clicks =", await ev("window.__clicks"), "| raw =", await ev("JSON.stringify(window.__raw)"))
    await asyncio.sleep(0.3)
    print("t+0.35: hint =", await ev("LO.state.hint && JSON.stringify(LO.state.hint)"),
          "| events =", await ev("JSON.stringify(LO.state.events.slice(0,2))"))

    await ws.close()
    try: http_json(f"/json/close/{target['id']}")
    except Exception: pass

asyncio.run(main())
