#!/usr/bin/env python3
"""Minimal CDP client over websocket for the charts tool.

Connects to the shared chromium-cdp daemon at 127.0.0.1:9222 (QA's harness).
Creates a dedicated page target per navigation so we never disturb existing
tabs. Extraction is done by evaluating page-side JS that returns JSON.
"""
import asyncio
import json
import time
import urllib.parse
import urllib.request

import websockets

CDP_HTTP = "http://127.0.0.1:9222"


class CDPError(RuntimeError):
    pass


async def _rpc(ws, method, params=None, msg_id=None):
    msg_id = msg_id if msg_id is not None else int(time.time() * 1000) % 10**9
    await ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=60)
        msg = json.loads(raw)
        if msg.get("id") == msg_id:
            if "error" in msg:
                raise CDPError(f"{method}: {msg['error']}")
            return msg.get("result", {})
        # Events and other responses: ignore (we only await our own ids)


def _http_json(path, method="GET"):
    req = urllib.request.Request(f"{CDP_HTTP}{path}", method=method)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())


async def new_page(ws_url, url="about:blank"):
    """Create a dedicated tab. Returns (target_id, ws)."""
    ws = await websockets.connect(ws_url, max_size=64 * 1024 * 1024)
    # Enable Page + Runtime so load events/console errors flow
    await _rpc(ws, "Page.enable")
    await _rpc(ws, "Runtime.enable")
    await _rpc(ws, "Page.navigate", {"url": url})
    return ws


async def wait_ready(ws, settle_js=None, timeout=45):
    """Wait for document.readyState=complete, then optional settle condition.

    settle_js: JS expression returning truthy when the page is considered
    rendered (e.g. a selector matching). Polls every 300ms.
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            state = await eval_js(ws, "document.readyState")
            if state == "complete":
                if settle_js:
                    try:
                        ok = await eval_js(ws, settle_js)
                        if ok:
                            return True
                    except CDPError:
                        pass
                else:
                    return True
        except CDPError:
            pass
        await asyncio.sleep(0.3)
    return False


async def eval_js(ws, expression, await_promise=False):
    """Evaluate JS in the page, return the JSON value."""
    res = await _rpc(
        ws, "Runtime.evaluate",
        {"expression": expression, "returnByValue": True,
         "awaitPromise": await_promise},
    )
    if "exceptionDetails" in res:
        exc = res["exceptionDetails"].get("exception", {}).get("description")
        raise CDPError(f"JS exception: {exc}")
    return res.get("result", {}).get("value")


async def close_page(ws, target_id):
    """Detach ws and close the tab."""
    try:
        await ws.close()
    except Exception:
        pass
    try:
        _http_json(f"/json/close/{target_id}")
    except Exception:
        pass


async def run_on_page(url, extract_js, settle_js=None, timeout=45, await_promise=False):
    """One-shot helper: open url in a fresh tab, wait, extract, close.

    Returns the JSON value of extract_js (parsed), or raises CDPError.
    """
    return await run_with_setup(url, None, extract_js, settle_js, timeout,
                                await_promise=await_promise)


async def run_with_setup(url, setup_js, extract_js, settle_js=None, timeout=45,
                         post_setup_delay=4.0, await_promise=False):
    """Like run_on_page but runs setup_js (e.g. a consent-button click) after
    the page settles, waits post_setup_delay, then extracts."""
    target = _http_json(f"/json/new?{urllib.parse.quote(url, safe='')}", method="PUT")
    target_id = target["id"]
    ws_url = target["webSocketDebuggerUrl"]
    ws = await new_page(ws_url, url)
    try:
        await wait_ready(ws, settle_js=settle_js, timeout=timeout)
        if setup_js:
            try:
                await eval_js(ws, setup_js)
                await asyncio.sleep(post_setup_delay)
            except CDPError:
                pass  # setup is best-effort
        raw = await eval_js(ws, extract_js, await_promise=await_promise)
        if raw is None:
            raise CDPError(f"extract_js returned null for {url}")
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        return raw
    finally:
        await close_page(ws, target_id)
