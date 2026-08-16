#!/usr/bin/env python3
"""charts-tool — CDP-driven topping-games scraper (harness Task 8).

Answers "what games are topping right now, with real numbers" across the
web-game funnel. Replaces the jina-based fetch in portal-radar: a CDP
(browser) fetch sees the JS-rendered play/vote counts jina's markdown misses.

Surfaces (source tags):
  crazygames/top      CrazyGames /top  (12+ per page, real totalPlays)
  crazygames/new      CrazyGames /new  (SSG, real totalPlays)
  crazygames/hot      CrazyGames /hot  (SSG, real totalPlays)
  poki/trending       Poki homepage rail + detail pages (rating, votes, likes)
  itch/top-puzzle     itch.io top-rated puzzle listing (rating, engine, size)
  itch/top-arcade     itch.io top-rated arcade listing
  steam/top-sellers   Steam top-sellers search (price, review % + count)

Output: normalized JSONL rows appended/merged into radar.jsonl (dedupe by
slug, source-tagged, existing plays=null rows backfilled with real plays).

Usage:
  python3 fetch_charts.py                 # full sweep
  python3 fetch_charts.py --surfaces crazygames/top,steam/top-sellers
  python3 fetch_charts.py --output /tmp/radar.jsonl --limit 5
  python3 fetch_charts.py --no-enrich      # skip detail-page enrichment
  python3 fetch_charts.py --dry-run        # fetch but do not write

Requires: chromium-cdp daemon on 127.0.0.1:9222 (QA's harness).
"""
import argparse
import asyncio
import json
import os
import re
import sys
from datetime import date, datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cdp  # noqa: E402

RADAR_DEFAULT = os.path.expanduser("~/.hermes/company-memory/radar.jsonl")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36")

# --------------------------------------------------------------------------
# number parsing helpers
# --------------------------------------------------------------------------

def parse_count(s):
    """'1.2M' -> 1200000, '2,595,079' -> 2595079, 'Free' -> None."""
    if s is None:
        return None
    s = str(s).strip().replace(",", "")
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([KMB])?$", s, re.I)
    if not m:
        return None
    val = float(m.group(1))
    mult = {"": 1, "K": 1_000, "M": 1_000_000, "B": 1_000_000_000}
    return int(val * mult.get((m.group(2) or "").upper(), 1))


def parse_float(s):
    if s is None:
        return None
    m = re.search(r"[0-9]+(?:\.[0-9]+)?", str(s).replace(",", "."))
    return float(m.group(0)) if m else None


def slug_of(url):
    """Canonical dedupe slug from a game URL."""
    url = url.split("?")[0].rstrip("/")
    m = re.search(r"crazygames\.com/game/([a-z0-9-]+)$", url)
    if m:
        return "cg:" + m.group(1)
    m = re.search(r"poki\.com/en/g/([a-z0-9-]+)$", url)
    if m:
        return "poki:" + m.group(1)
    m = re.search(r"itch\.io/([a-z0-9-]+)/([a-z0-9-]+)$", url)
    if m:
        return "itch:" + m.group(1) + "/" + m.group(2)
    m = re.search(r"steampowered\.com/app/([0-9]+)", url)
    if m:
        return "steam:" + m.group(1)
    return url


# --------------------------------------------------------------------------
# CrazyGames
# --------------------------------------------------------------------------

CG_LIST_SETTLE = ("(() => { const c = document.querySelectorAll('.game-thumb-test-class, "
                  "[class*=\"gameThumbLink\"]'); return c.length > 5; })()")

CG_NEXT_DATA = r"""
(() => {
  const nd = document.getElementById('__NEXT_DATA__');
  if (!nd) return null;
  try {
    const st = JSON.parse(nd.textContent);
    const items = st.props && st.props.pageProps && st.props.pageProps.games && st.props.pageProps.games.items;
    if (!Array.isArray(items)) return null;
    return items.map((g, i) => ({
      rank: i + 1,
      name: g.name,
      slug: g.slug,
      url: 'https://www.crazygames.com/game/' + g.slug,
      plays: g.totalPlays != null ? Number(g.totalPlays) : null,
      likes: g.totalLikes != null ? Number(g.totalLikes) : null,
      category: g.categoryName || null,
      releaseYear: g.releaseYear != null ? String(g.releaseYear) : null,
      isOriginal: !!g.isOriginal,
      hasIap: g.hasIap != null ? !!g.hasIap : null,
    }));
  } catch (e) { return null; }
})()
"""

CG_API_FETCH = r"""
(async () => {
  const pages = [];
  try {
    const r = await fetch('https://api.crazygames.com/v4/en_US/games?paginationPage=1&paginationSize=12&sorting=default&device=desktop', {headers: {'accept': 'application/json'}});
    const d = await r.json();
    const items = (d.games && d.games.items) || [];
    return items.map((g, i) => ({
      rank: i + 1,
      name: g.name,
      slug: g.slug,
      url: 'https://www.crazygames.com/game/' + g.slug,
      plays: g.totalPlays != null ? Number(g.totalPlays) : null,
      likes: g.totalLikes != null ? Number(g.totalLikes) : null,
      category: g.categoryName || null,
      releaseYear: g.releaseYear != null ? String(g.releaseYear) : null,
      isOriginal: !!g.isOriginal,
      hasIap: g.hasIap != null ? !!g.hasIap : null,
    }));
  } catch (e) { return [{_error: String(e)}]; }
})()
"""

CG_DETAIL_EXTRACT = r"""
(() => {
  const nd = document.getElementById('__NEXT_DATA__');
  if (!nd) return null;
  try {
    const g = JSON.parse(nd.textContent).props.pageProps.game;
    if (!g) return null;
    return {
      name: g.name,
      url: 'https://www.crazygames.com/game/' + g.slug,
      engine: g.loaderTypeLabel || g.technology || null,
      sdk: g.loaderType ? ('crazygames:' + g.loaderType) : null,
      desktopUrl: g.desktopUrl || null,
      developer: g.developer || null,
      category: g.category && g.category.name ? g.category.name : null,
      tags: Array.isArray(g.tags) ? g.tags.map(t => typeof t === 'string' ? t : (t && t.name)) : [],
      rating: g.rating != null ? Number(g.rating) : null,
      upvotes: g.upvotes != null ? Number(g.upvotes) : null,
      downvotes: g.downvotes != null ? Number(g.downvotes) : null,
      released: (g.basicLaunchOn || g.addedOn || '').slice(0, 7)
        .replace(/^(\d{4})-(\d{2})$/, (_, y, m) => new Date(y, m - 1, 1).toLocaleString('en-US', {month: 'long'}) + ' ' + y) || null,
    };
  } catch (e) { return null; }
})()
"""


async def fetch_crazygames_surface(surface):
    """surface: 'top' | 'new' | 'hot'. Returns list of row dicts."""
    if surface == "top":
        url = "https://www.crazygames.com/top"
        rows = await cdp.run_on_page(url, CG_API_FETCH, settle_js=CG_LIST_SETTLE,
                                     timeout=60, await_promise=True)
    else:
        url = f"https://www.crazygames.com/{surface}"
        rows = await cdp.run_on_page(url, CG_NEXT_DATA, settle_js=CG_LIST_SETTLE, timeout=60)
    if not rows:
        raise cdp.CDPError(f"crazygames/{surface}: no game rows extracted ({url})")
    if isinstance(rows, dict) and rows.get("_error"):
        raise cdp.CDPError(f"crazygames/{surface} API error: {rows['_error']}")
    for r in rows:
        r["source"] = f"crazygames/{surface}"
    return rows


async def enrich_crazygames_detail(slug):
    url = f"https://www.crazygames.com/game/{slug}"
    d = await cdp.run_on_page(url, CG_DETAIL_EXTRACT, timeout=55)
    return d


# --------------------------------------------------------------------------
# Poki
# --------------------------------------------------------------------------

POKI_TRENDING_EXTRACT = r"""
(() => {
  const slugs = [...document.querySelectorAll('a[href*="/en/g/"]')]
    .map(a => a.getAttribute('href'))
    .filter(h => h && /^\/en\/g\/[a-z0-9-]+$/.test(h));
  return [...new Set(slugs)].slice(0, 12);
})()
"""

POKI_AGREE = r"""
(() => {
  const btns = [...document.querySelectorAll('button, a, [role="button"]')];
  const t = btns.find(b => /^(AGREE|Agree|ACCEPT|Accept)$/i.test((b.innerText||'').trim()));
  if (t) { t.click(); return true; }
  return false;
})()
"""

POKI_DETAIL_EXTRACT = r"""
(() => {
  const out = {};
  const lds = [...document.querySelectorAll('script[type="application/ld+json"]')];
  for (const s of lds) {
    try {
      const d = JSON.parse(s.textContent);
      const graph = d['@graph'] || [d];
      for (const node of graph) {
        const me = node.mainEntity;
        if (me && (me['@type'] === 'VideoGame' || (Array.isArray(me['@type']) && me['@type'].includes('VideoGame')))) {
          out.name = me.name;
          out.url = 'https://poki.com/en/g/' + (location.pathname.match(/\/g\/([a-z0-9-]+)/) || [,''])[1];
          out.description = (me.description || '').slice(0, 300);
          if (me.author) out.developer = (me.author.name || me.author['@id'] || null);
          if (me.aggregateRating) {
            out.rating = me.aggregateRating.ratingValue != null ? Number(me.aggregateRating.ratingValue) : null;
            out.rating_votes = me.aggregateRating.ratingCount != null ? Number(me.aggregateRating.ratingCount) : null;
          }
        }
      }
      break;
    } catch (e) {}
  }
  const body = document.body ? document.body.innerText : '';
  const likes = body.match(/([0-9.]+[KMB]?)\s*\n?Like/i);
  const dis = body.match(/([0-9.]+[KMB]?)\s*\n?Dislike/i);
  if (likes) out.likes = likes[1];
  if (dis) out.dislikes = dis[1];
  return JSON.stringify(out);
})()
"""


async def fetch_poki_trending(limit=12):
    slugs = await cdp.run_on_page("https://poki.com/en", POKI_TRENDING_EXTRACT, timeout=60)
    if not slugs:
        raise cdp.CDPError("poki/trending: no game slugs found on homepage")
    # slugs come back as full hrefs ("/en/g/gobattle2"); keep the bare slug
    slugs = [s.split("/en/g/")[-1] if "/en/g/" in s else s for s in slugs]
    rows = []
    for slug in slugs[:limit]:
        try:
            d = await cdp.run_with_setup(
                f"https://poki.com/en/g/{slug}", POKI_AGREE,
                POKI_DETAIL_EXTRACT, timeout=50)
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except json.JSONDecodeError:
                    d = {}
            if not d or not d.get("name"):
                d = d or {}
                d["name"] = slug.replace("-", " ").title()
                d["url"] = f"https://poki.com/en/g/{slug}"
                d["_partial"] = True
            d["slug"] = slug
            d["plays"] = None  # Poki does not expose play counts
            d["likes"] = parse_count(d.get("likes"))
            d["dislikes"] = parse_count(d.get("dislikes"))
            d["source"] = "poki/trending"
            rows.append(d)
        except cdp.CDPError as e:
            print(f"  [warn] poki detail {slug}: {e}", file=sys.stderr)
    if not rows:
        raise cdp.CDPError("poki/trending: no detail rows collected")
    return rows


# --------------------------------------------------------------------------
# itch.io
# --------------------------------------------------------------------------

ITCH_LIST_SETTLE = "document.querySelectorAll('.game_cell').length > 5"

ITCH_LIST_EXTRACT = r"""
(() => {
  const rows = [...document.querySelectorAll('.game_cell')];
  return rows.slice(0, 20).map(r => {
    const a = r.querySelector('a[href*="itch.io/"]');
    const title = r.querySelector('.game_title');
    const author = r.querySelector('.game_author');
    const text = (r.innerText || '');
    const ratingM = text.match(/Rated ([0-9.]+) out of 5 stars\s*\(([0-9.,]+)\s*total ratings\)/);
    const href = a ? a.getAttribute('href') : null;
    return {
      name: title ? title.innerText.trim() : null,
      url: href,
      author: author ? author.innerText.trim() : null,
      rating: ratingM ? parseFloat(ratingM[1]) : null,
      rating_votes: ratingM ? parseInt(ratingM[2].replace(/,/g, ''), 10) : null,
      genre: (text.match(/\n(Puzzle|Arcade|Action|Adventure|RPG|Simulation|Strategy|Platformer|Casual|Other)$/m) || [,''])[1] || null,
    };
  }).filter(r => r.url && r.name);
})()
"""

ITCH_DETAIL_EXTRACT = r"""
(() => {
  const out = {};
  const tables = [...document.querySelectorAll('table')];
  const info = tables.find(t => /Rating|Made with|Platforms|Status/i.test(t.innerText));
  if (info) {
    for (const tr of info.querySelectorAll('tr')) {
      const cells = [...tr.querySelectorAll('td')].map(c => (c.innerText||'').trim().replace(/\s+/g,' '));
      if (cells.length < 2) continue;
      const k = cells[0].toLowerCase();
      if (k === 'made with') out.engine = cells[1];
      else if (k === 'platforms') out.platforms = cells[1];
      else if (k === 'status') out.status = cells[1];
      else if (k === 'rating') {
        const m = cells[1].match(/Rated ([0-9.]+) out of 5 stars\s*\(([0-9.,]+)\s*total ratings\)/);
        if (m) { out.rating = parseFloat(m[1]); out.rating_votes = parseInt(m[2].replace(/,/g,''), 10); }
      }
      else if (k === 'author') out.author = cells[1];
      else if (k === 'genre') out.genre = cells[1];
      else if (k === 'tags') out.tags = cells[1].split(',').map(s => s.trim());
    }
  }
  const body = document.body ? document.body.innerText : '';
  const sizeM = body.match(/([0-9.,]+)\s*(MB|KB|GB)/i);
  if (sizeM) {
    const v = parseFloat(sizeM[1].replace(/,/g, '.'));
    out.file_size_mb = sizeM[2].toUpperCase() === 'MB' ? v : sizeM[2].toUpperCase() === 'GB' ? v * 1024 : v / 1024;
  }
  return JSON.stringify(out);
})()
"""


async def fetch_itch_surface(genre, enrich_top=6):
    url = f"https://itch.io/games/top-rated/genre-{genre}"
    rows = await cdp.run_on_page(url, ITCH_LIST_EXTRACT, settle_js=ITCH_LIST_SETTLE, timeout=60)
    if not rows:
        raise cdp.CDPError(f"itch/top-{genre}: no game cells extracted")
    for i, r in enumerate(rows):
        r["rank"] = i + 1
        r["source"] = f"itch/top-{genre}"
        r["plays"] = None  # itch.io does not expose play/view counts on this layout
    # enrich top N detail pages for engine/size
    for r in rows[:enrich_top]:
        try:
            d = await cdp.run_on_page(r["url"], ITCH_DETAIL_EXTRACT, timeout=50)
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except json.JSONDecodeError:
                    d = {}
            for k, v in (d or {}).items():
                if v is not None and r.get(k) is None:
                    r[k] = v
        except cdp.CDPError as e:
            print(f"  [warn] itch detail {r['name']}: {e}", file=sys.stderr)
    return rows


# --------------------------------------------------------------------------
# Steam
# --------------------------------------------------------------------------

STEAM_SETTLE = "document.querySelectorAll('.search_result_row').length > 5"

STEAM_EXTRACT = r"""
(() => {
  const rows = [...document.querySelectorAll('.search_result_row')];
  return rows.slice(0, 15).map((r, i) => {
    const href = r.getAttribute('href') || '';
    const appidM = href.match(/\/app\/([0-9]+)/);
    const title = (r.querySelector('.title') || {}).innerText;
    const date = (r.querySelector('.col.search_released, .search_released') || {}).innerText;
    const finalPrice = (r.querySelector('.discount_final_price') || {}).innerText || '';
    const origPrice = (r.querySelector('.discount_original_price') || {}).innerText || '';
    const pct = (r.querySelector('.discount_pct') || {}).innerText || '';
    const rs = r.querySelector('.search_review_summary');
    const tooltip = rs ? (rs.getAttribute('data-tooltip-html') || '') : '';
    let review_label = null, review_percent = null, review_count = null;
    const tm = tooltip.match(/([A-Za-z ]+?)<br>([0-9]+)% of the ([0-9.,]+) user reviews/);
    if (tm) {
      review_label = tm[1].trim();
      review_percent = parseInt(tm[2], 10);
      review_count = parseInt(tm[3].replace(/,/g, ''), 10);
    }
    return {
      rank: i + 1,
      name: title ? title.trim() : null,
      url: href.split('?')[0],
      appid: appidM ? appidM[1] : null,
      released: date ? date.trim() : null,
      price: (finalPrice || origPrice || '').replace(/\s+/g, ' ').trim() || null,
      original_price: (origPrice || '').replace(/\s+/g, ' ').trim() || null,
      discount: (pct || '').replace(/\s+/g, ' ').trim() || null,
      review_label, review_percent, review_count,
      plays: null,  // Steam store does not expose play counts publicly
    };
  }).filter(r => r.name);
})()
"""


async def fetch_steam_topsellers():
    url = "https://store.steampowered.com/search/?filter=topsellers&os=win"
    rows = await cdp.run_on_page(url, STEAM_EXTRACT, settle_js=STEAM_SETTLE, timeout=90)
    if not rows:
        raise cdp.CDPError("steam/top-sellers: no rows extracted")
    for r in rows:
        r["source"] = "steam/top-sellers"
    return rows


# --------------------------------------------------------------------------
# radar.jsonl merge
# --------------------------------------------------------------------------

def load_radar(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  [warn] skipping malformed radar line: {line[:80]}", file=sys.stderr)
    return rows


def merge_row(existing, new):
    """Merge a fetched row into an existing radar row (in place-ish).
    Fills nulls with new data; always adopts non-null plays; merges sources."""
    src = new.pop("source", None)
    new.pop("rank", None)
    slug = new.pop("_slug", None)
    # source merge, existing convention: "crazygames/new+hot"
    if src:
        cur = existing.get("source")
        tokens = [t.strip() for t in (cur or "").split("+") if t.strip()]
        if not tokens:
            existing["source"] = src
        elif src not in tokens:
            existing["source"] = "+".join(tokens + [src])
    # adopt new data where existing is null; plays always refresh when non-null
    for k, v in new.items():
        if v is None or v == "" or v == []:
            continue
        if existing.get(k) in (None, "", []) or k in ("plays", "likes", "rating_votes", "rating", "upvotes", "downvotes", "review_count", "rating_count"):
            existing[k] = v
    if slug:
        existing["_slug"] = slug
    return existing


def write_radar(path, rows):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in rows:
            # drop internal keys
            r = {k: v for k, v in r.items() if not k.startswith("_")}
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

SURFACE_FNS = {
    "crazygames/top": lambda: fetch_crazygames_surface("top"),
    "crazygames/new": lambda: fetch_crazygames_surface("new"),
    "crazygames/hot": lambda: fetch_crazygames_surface("hot"),
    "poki/trending": lambda: fetch_poki_trending(),
    "itch/top-puzzle": lambda: fetch_itch_surface("puzzle"),
    "itch/top-arcade": lambda: fetch_itch_surface("arcade"),
    "steam/top-sellers": lambda: fetch_steam_topsellers(),
}


async def sweep(surfaces, limit, output, dry_run, no_enrich, max_details):
    today = date.today().isoformat()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    existing = load_radar(output)
    by_slug = {}
    for r in existing:
        s = r.get("_slug") or slug_of(r.get("url", ""))
        by_slug.setdefault(s, r)

    stats = {"surfaces_ok": 0, "surfaces_failed": 0, "new_rows": 0,
             "updated_rows": 0, "plays_touched": 0, "total_fetched": 0}
    pending_details = []

    def _mark(row):
        row["_touched"] = True

    for name in surfaces:
        fn = SURFACE_FNS[name]
        print(f"[charts] fetching {name} ...", flush=True)
        try:
            rows = await fn()
        except Exception as e:
            print(f"  [FAIL] {name}: {e}", file=sys.stderr)
            stats["surfaces_failed"] += 1
            continue
        stats["surfaces_ok"] += 1
        stats["total_fetched"] += len(rows)
        for r in rows[:limit] if limit else rows:
            r["_slug"] = slug_of(r.get("url", ""))
            r["first_seen"] = today
            r["fetched_at"] = now
            existing_row = by_slug.get(r["_slug"])
            if existing_row is None:
                existing_row = dict(r)
                by_slug[r["_slug"]] = existing_row
                existing.append(existing_row)
                stats["new_rows"] += 1
                _mark(existing_row)
            else:
                merge_row(existing_row, dict(r))
                stats["updated_rows"] += 1
                _mark(existing_row)
            # queue detail enrichment (CrazyGames: engine/sdk; itch: engine/size)
            if not no_enrich and r["_slug"].startswith(("cg:", "itch:")):
                pending_details.append(existing_row)

    # detail enrichment pass (engine/SDK/file-size monetization comparators)
    if not no_enrich and pending_details:
        seen = set()
        todo = []
        for row in pending_details:
            s = row.get("_slug")
            if s in seen:
                continue
            seen.add(s)
            todo.append(row)
            if len(todo) >= max_details:
                break
        print(f"[charts] enriching {len(todo)} detail pages (engine/sdk/size) ...", flush=True)
        for row in todo:
            s = row.get("_slug")
            try:
                if s.startswith("cg:"):
                    slug = s[3:]
                    d = await enrich_crazygames_detail(slug)
                    if d:
                        d["_slug"] = s
                        merge_row(row, d)
                        if d.get("engine"):
                            print(f"  {row.get('name')}: engine={d['engine']} sdk={d.get('sdk')}", file=sys.stderr)
                elif s.startswith("itch:"):
                    url = row.get("url")
                    d = await cdp.run_on_page(url, ITCH_DETAIL_EXTRACT, timeout=50)
                    if isinstance(d, str):
                        try:
                            d = json.loads(d)
                        except json.JSONDecodeError:
                            d = {}
                    if d:
                        for k, v in d.items():
                            if v is not None and row.get(k) is None:
                                row[k] = v
                        if d.get("engine"):
                            print(f"  {row.get('name')}: engine={d['engine']} size={d.get('file_size_mb')}", file=sys.stderr)
            except cdp.CDPError as e:
                print(f"  [warn] detail enrich {s}: {e}", file=sys.stderr)
            await asyncio.sleep(0.4)

    # summary
    with_plays = sum(1 for r in existing if r.get("plays") is not None)
    touched_with_plays = sum(1 for r in existing
                             if r.get("_touched") and r.get("plays") is not None)
    print()
    print(f"[charts] SWEEP COMPLETE — surfaces ok: {stats['surfaces_ok']}/{len(surfaces)} "
          f"(failed: {stats['surfaces_failed']})")
    print(f"[charts] fetched {stats['total_fetched']} rows; new: {stats['new_rows']}, "
          f"updated/merged: {stats['updated_rows']}")
    print(f"[charts] radar.jsonl now {len(existing)} rows; {with_plays} with non-null plays "
          f"({touched_with_plays} touched this sweep)")
    per_source = {}
    for r in existing:
        src = r.get("source", "?")
        per_source[src] = per_source.get(src, 0) + 1
    print(f"[charts] source distribution: {json.dumps(per_source)}")

    if dry_run:
        print("[charts] DRY RUN — radar.jsonl NOT written")
        return stats, existing
    write_radar(output, existing)
    print(f"[charts] wrote {output}")
    return stats, existing


def main():
    ap = argparse.ArgumentParser(description="CDP-driven topping-games radar scraper")
    ap.add_argument("--surfaces", default=",".join(SURFACE_FNS),
                    help="comma-separated surfaces (default: all)")
    ap.add_argument("--output", default=RADAR_DEFAULT)
    ap.add_argument("--limit", type=int, default=0, help="max rows per surface (0=all)")
    ap.add_argument("--no-enrich", action="store_true", help="skip detail-page enrichment")
    ap.add_argument("--max-details", type=int, default=20,
                    help="max detail pages to enrich per sweep")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    surfaces = [s.strip() for s in args.surfaces.split(",") if s.strip()]
    unknown = [s for s in surfaces if s not in SURFACE_FNS]
    if unknown:
        ap.error(f"unknown surface(s): {', '.join(unknown)}; known: {', '.join(SURFACE_FNS)}")

    try:
        stats, rows = asyncio.run(sweep(args.surfaces.split(",") if args.surfaces else list(SURFACE_FNS),
                                        args.limit, args.output, args.dry_run,
                                        args.no_enrich, args.max_details))
    except cdp.CDPError as e:
        print(f"[charts] FATAL: {e}", file=sys.stderr)
        print("[charts] is the chromium-cdp daemon up on 127.0.0.1:9222?", file=sys.stderr)
        sys.exit(2)
    sys.exit(0 if stats["surfaces_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
