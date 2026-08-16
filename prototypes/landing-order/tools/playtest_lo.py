#!/usr/bin/env python3
"""Headless playtest for the LANDING ORDER feeler (throwaway).

Boots index.html in the shared chromium-cdp daemon, checks console health,
runs greedy-bot passes on L1-L4 (slack distributions = spec 1.2 evidence),
drives a REAL mouse-input L1 run (the two-click verb), captures screenshots.
"""
import asyncio, base64, json, os, sys, time, urllib.parse, urllib.request
import websockets

CDP_HTTP = "http://127.0.0.1:9222"
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "http://127.0.0.1/landing-order/index.html"
EVID = os.path.join(HERE, "evidence")
os.makedirs(EVID, exist_ok=True)

class CDPError(RuntimeError): pass

async def rpc(ws, method, params=None, msg_id=None, on_event=None):
    msg_id = msg_id or int(time.time()*1000) % 10**9
    await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=60)
        msg = json.loads(raw)
        if msg.get("id") == msg_id:
            if "error" in msg: raise CDPError(f"{method}: {msg['error']}")
            return msg.get("result", {})
        if on_event: on_event(msg)

async def eval_js(ws, expr):
    res = await rpc(ws, "Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    if "exceptionDetails" in res:
        d = res["exceptionDetails"].get("exception", {}).get("description", "")
        raise CDPError(f"JS exception: {d}")
    return res.get("result", {}).get("value")

async def click(ws, x, y, evts=None):
    for t, b in [("mousePressed", "left"), ("mouseReleased", "left")]:
        await rpc(ws, "Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": b, "clickCount": 1})
    if evts is not None: evts.append(f"click({x:.0f},{y:.0f})")

async def shot(ws, name):
    res = await rpc(ws, "Page.captureScreenshot", {"format": "png"})
    p = os.path.join(EVID, name + ".png")
    open(p, "wb").write(base64.b64decode(res["data"]))
    return p

def http_json(path, method="GET"):
    req = urllib.request.Request(CDP_HTTP + path, method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

async def main():
    target = http_json(f"/json/new?{urllib.parse.quote(URL, safe='')}", method="PUT")
    ws = await websockets.connect(target["webSocketDebuggerUrl"], max_size=128*1024*1024)
    events = []
    def collect(msg):
        if msg.get("method") in ("Runtime.exceptionThrown", "Log.entryAdded", "Runtime.consoleAPICalled"):
            events.append(msg.get("params", {}).get("entry", msg.get("params", {})))
    async def rpc_ev(method, params=None):
        return await rpc(ws, method, params, on_event=collect)
    await rpc_ev("Page.enable"); await rpc_ev("Runtime.enable"); await rpc_ev("Log.enable")
    await rpc(ws, "Page.navigate", {"url": URL})
    # wait for LO
    for _ in range(100):
        try:
            if await eval_js(ws, "typeof window.LO === 'object' && !!LO.state"): break
        except CDPError: pass
        await asyncio.sleep(0.3)
    else:
        print("FAIL: LO never appeared"); return 1

    print("BOOT:", await eval_js(ws, "document.title"))
    print("canvas:", await eval_js(ws, "JSON.stringify((()=>{const r=document.getElementById('c').getBoundingClientRect();return {w:r.width,h:r.height}})())"))
    print("state0:", json.dumps(await eval_js(ws, "LO.snapshot()")))
    p = await shot(ws, "s01_l1_start"); print("shot", p)

    # ---- bot passes (single code path) ----
    print("\n=== BOT PASSES (greedy policy, LO API) ===")
    for lvl in (1,2,3,4):
        snap = await eval_js(ws, f"LO.setup({lvl}); LO.botRun(5000); JSON.stringify(LO.snapshot())")
        s = json.loads(snap)
        print(f"L{lvl}: phase={s['phase']} tick={s['tick']} landings={s['landings']} incidents={s['incidents']} "
              f"goArounds={s['goArounds']} score={s['score']} slack={json.dumps(s['slackStats'])}")
        if s["phase"] == "won" and lvl == 1:
            p = await shot(ws, "s02_l1_bot_won"); print("shot", p)

    # ---- L3 mid-run screenshot (stack-up visible) ----
    await eval_js(ws, "LO.setup(3); LO.fastForward(60)")
    p = await shot(ws, "s03_l3_stackup"); print("shot", p)
    await eval_js(ws, "LO.setup(4); LO.fastForward(50)")
    p = await shot(ws, "s04_l4_pressure"); print("shot", p)

    # ---- REAL mouse-input L1 run (the two-click verb) ----
    print("\n=== REAL-INPUT L1 (CDP mouse events) ===")
    await eval_js(ws, "LO.setup(1); LO.state.tick=0; 0")
    rect = json.loads(await eval_js(ws, "JSON.stringify((()=>{const r=document.getElementById('c').getBoundingClientRect();return {l:r.left,t:r.top,w:r.width,h:r.height}})())"))
    def g2c(gx, gy):  # game px -> client px
        return rect["l"] + gx * rect["w"] / 900, rect["t"] + gy * rect["h"] / 640
    CELL = 12
    def plane_xy(snap, pid):
        for pl in snap["planes"]:
            if pl["id"] == pid and pl["state"] not in ("hold", "landed") and not pl.get("wait"):
                return pl["x"] * CELL, pl["y"] * CELL
        return None
    def runway_y(r): return 14 * CELL if r == "A" else 28 * CELL

    # wait for plane 0 spawn (tick 0-3)
    for _ in range(50):
        snap = json.loads(await eval_js(ws, "JSON.stringify(LO.snapshot())"))
        if snap["tick"] > 0: break
        await asyncio.sleep(0.1)
    print("tick at start of input run:", snap["tick"])

    def chip_xy(snap, pid):
        rwy = None
        for r in ("A", "B"):
            if pid in snap["queues"][r]: rwy = r; qi = snap["queues"][r].index(pid); break
        if rwy is None: return None
        cols = ["A", "B"] if snap["level"] >= 2 else ["A"]
        ci = cols.index(rwy); cw = 880 / len(cols)
        x0 = 10 + ci * cw
        return x0 + min(cw - 20, 240) / 2, 486 + 22 + qi * 26 + 11

    # plane 0 -> select (hint: click the plane)
    xy = plane_xy(snap, 0); cx, cy = g2c(*xy)
    await click(ws, cx, cy, events)
    sel = await eval_js(ws, "LO.state.selected")
    hint = await eval_js(ws, "LO.state.hint ? LO.state.hint.txt : null")
    print("after click plane0: selected =", sel, "hint =", hint)
    # plane 0 chip -> make next (click IMMEDIATELY — plane 0 approaches fast)
    cxy = chip_xy(snap, 0); cx, cy = g2c(*cxy)
    await click(ws, cx, cy, events)
    print("after chip click: queue A =", await eval_js(ws, "JSON.stringify(LO.state.queues.A)"), "hint =", await eval_js(ws, "LO.state.hint ? LO.state.hint.txt : null"))
    await shot(ws, "s05_l1_selected")

    # wait for plane 1 spawn -> select -> chip
    for _ in range(120):
        snap = json.loads(await eval_js(ws, "JSON.stringify(LO.snapshot())"))
        xy = plane_xy(snap, 1)
        if xy and snap["tick"] > 3: break
        await asyncio.sleep(0.05)
    cx, cy = g2c(*plane_xy(snap, 1)); await click(ws, cx, cy, events)
    cxy = chip_xy(snap, 1); cx, cy = g2c(*cxy)
    await click(ws, cx, cy, events)
    print("after plane1+chip: queue A =", await eval_js(ws, "JSON.stringify(LO.state.queues.A)"))

    # let it run in real time until won (timeout 30s)
    for _ in range(300):
        snap = json.loads(await eval_js(ws, "JSON.stringify(LO.snapshot())"))
        if snap["phase"] == "won": break
        await asyncio.sleep(0.1)
    print("real-input L1 final:", json.dumps(snap))
    p = await shot(ws, "s06_l1_real_win"); print("shot", p)

    # reroute + hold checks (API-level, same code path as UI clicks)
    await eval_js(ws, "LO.setup(2); LO.fastForward(6)")
    rr = await eval_js(ws, """(()=>{ const s=LO.state;
      const p=s.planes.find(pl=>pl.state==='approach' && !pl.wait);
      if(!p) return 'no approach plane';
      const from=p.runway, to=from==='A'?'B':'A';
      const beforeA=[...s.queues.A], beforeB=[...s.queues.B];
      LO.assign(s,p.id,to);
      return JSON.stringify({from, to, beforeA, beforeB, afterA:[...s.queues.A], afterB:[...s.queues.B], targetRow:s.planes[p.id].targetRow});
    })()""")
    print("reroute:", rr)
    await eval_js(ws, "LO.setup(3); LO.fastForward(40)")
    hd = await eval_js(ws, """(()=>{ const s=LO.state;
      const p=s.planes.find(pl=>pl.state==='approach' && !pl.wait);
      if(!p) return 'no approach plane';
      LO.sendHold(s,p.id);
      const inHold=s.holdQ.includes(p.id), inQueueA=s.queues.A.includes(p.id), inQueueB=s.queues.B.includes(p.id);
      LO.fastForward(20);
      const rejoined = s.planes[p.id].state==='approach';
      const backInQueue = s.queues.A.includes(p.id) || s.queues.B.includes(p.id);
      return JSON.stringify({sentToHold:inHold, removedFromQueues:!inQueueA&&!inQueueB, after20Ticks:{state:s.planes[p.id].state, x:s.planes[p.id].x}, rejoined, backInQueue});
    })()""")
    print("hold cycle:", hd)

    # ---- console health ----
    print("\nconsole/exception events:", len(events))
    for e in events[:6]:
        if isinstance(e, dict):
            m = e.get("params", e)
            print("  -", json.dumps(m)[:200])
        else:
            print("  -", str(e)[:200])

    await ws.close()
    try: http_json(f"/json/close/{target['id']}")
    except Exception: pass
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
