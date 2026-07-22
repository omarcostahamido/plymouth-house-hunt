#!/usr/bin/env python3
"""
Plymouth house-hunt monitor.

Fetches configured listing sources, extracts property cards, applies
Sarah's criteria, diffs against state/state.json, and writes:

  - state/state.json      (seen listings + event history; committed)
  - README.md             (digest between HUNT markers)
  - docs/feed.xml         (RSS 2.0 of new/changed/removed events)
  - docs/index.html       (simple web digest, for GitHub Pages)
  - outputs/email.html    (email body — only when there are changes)

Exit code is always 0 on handled errors; individual source failures are
reported in the digest rather than failing the run.
"""

import html
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "hunt" / "config.yaml"
STATE = ROOT / "state" / "state.json"
README = ROOT / "README.md"
FEED = ROOT / "docs" / "feed.xml"
INDEX = ROOT / "docs" / "index.html"
EMAIL = ROOT / "outputs" / "email.html"
EMAIL_MD = ROOT / "outputs" / "email.md"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

PRICE_RE = re.compile(r"£\s?([0-9]{2,3}(?:,[0-9]{3})+|[0-9]{5,7})")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ── fetching & parsing ────────────────────────────────────────────────

def fetch(url, timeout=30):
    r = requests.get(url, headers={"User-Agent": UA, "Accept-Language": "en-GB,en"},
                     timeout=timeout)
    r.raise_for_status()
    return r.text


def parse_price(text):
    m = PRICE_RE.search(text)
    if not m:
        return None
    return int(m.group(1).replace(",", ""))


def card_container(a_tag, max_up=5):
    """Climb from a link to the smallest ancestor that mentions a price."""
    node = a_tag
    for _ in range(max_up):
        if node.parent is None:
            break
        node = node.parent
        if "£" in node.get_text():
            return node
    return a_tag.parent or a_tag


def extract_listings(source, html_text):
    """Generic extractor: links matching link_regex + price from card."""
    soup = BeautifulSoup(html_text, "html.parser")
    link_re = re.compile(source["link_regex"], re.I)
    found = {}
    for a in soup.find_all("a", href=True):
        absu = urljoin(source["url"], a["href"]).split("?")[0].split("#")[0]
        if not link_re.search(absu):
            continue
        card = card_container(a)
        text = " ".join(card.get_text(" ", strip=True).split())
        price = parse_price(text)
        # Title preference: the card's <address> element (portals like OTM
        # put the street address there), then meaningful link text, then a
        # heading, then the URL slug. Link text that is just a price or a
        # bare listing ID is not a usable title.
        title = ""
        addr = card.find("address")
        if addr:
            title = addr.get_text(" ", strip=True)
        if len(title) < 8:
            t = a.get_text(" ", strip=True)
            if len(t) >= 8 and not re.fullmatch(r"[£\d,. ]+", t):
                title = t
        if len(title) < 8:
            h = card.find(["h1", "h2", "h3", "h4"])
            if h:
                title = h.get_text(" ", strip=True)
        if len(title) < 8:
            title = absu.rstrip("/").rsplit("/", 1)[-1].replace("-", " ").title()
        cand = {
            "id": absu,
            "url": absu,
            "title": title[:160],
            "price": price,
            "card_text": text[:500],
            "source": source["id"],
            "source_name": source["name"],
        }
        prev = found.get(absu)
        if prev is None or listing_quality(cand) > listing_quality(prev):
            found[absu] = cand
    return list(found.values())


def listing_quality(l):
    """Rank duplicate captures of the same listing: a real address beats a
    bare ID/price title (portal 'featured' modules), having a price beats
    not, and more card context beats less."""
    has_words = 0 if re.fullmatch(r"[£\d,. ]*", l["title"] or "") else 1
    return (has_words, 1 if l["price"] is not None else 0,
            min(len(l.get("card_text", "")), 200))


def merge_listings(found_map, listings):
    """Merge listings (e.g. from multiple result pages) keeping the best
    capture of each id."""
    for l in listings:
        prev = found_map.get(l["id"])
        if prev is None or listing_quality(l) > listing_quality(prev):
            found_map[l["id"]] = l
    return found_map


def extract_feed(source, xml_text):
    """RSS feed extractor (WordPress agent feeds: newest listings first).

    Feed items rarely carry a price, so price stays None and the listing
    is flagged for manual checking — feeds are for *detecting* new stock.
    """
    listings = []
    root = ET.fromstring(xml_text)
    link_re = re.compile(source.get("link_regex", "."), re.I)
    for item in root.iter("item"):
        link = (item.findtext("link") or "").strip().split("?")[0]
        title = (item.findtext("title") or "").strip()
        desc = re.sub(r"<[^>]+>", " ", item.findtext("description") or "")
        if not link or not link_re.search(link):
            continue
        listings.append({
            "id": link,
            "url": link,
            "title": title[:160] or link,
            "price": parse_price(title + " " + desc),
            "card_text": " ".join((title + " " + desc).split())[:500],
            "source": source["id"],
            "source_name": source["name"],
        })
    return listings


# ── criteria ──────────────────────────────────────────────────────────

def apply_criteria(listings, crit):
    kept = []
    for l in listings:
        blob = (l["title"] + " " + l["card_text"]).lower()
        if any(re.search(p, blob) for p in crit["_exclude_res"]):
            continue
        # Area excludes match the TITLE (address) only, so a description
        # saying "short drive to Plymstock" can't wrongly drop a listing.
        if any(r.search(l["title"].lower())
               for r in crit.get("_exclude_area_res", [])):
            continue
        if l["price"] is not None and not (
                crit["min_price"] <= l["price"] <= crit["max_price"]):
            continue
        flags = [f["label"] for f in crit["_flag_res"] if f["re"].search(blob)]
        if l["price"] is None:
            flags.append("Price not read — open listing")
        if not any(k.lower() in blob for k in crit["area_keywords"]):
            flags.append("Location unverified — check it's central Plymouth")
        l["flags"] = sorted(set(flags))
        kept.append(l)
    return kept


# ── state & diffing ───────────────────────────────────────────────────

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"listings": {}, "events": [], "runs": []}


def diff(state, current):
    events = []
    cur_ids = {l["id"] for l in current}
    known = state["listings"]

    for l in current:
        old = known.get(l["id"])
        if old is None:
            events.append({"type": "new", "listing": l, "date": today()})
        elif old.get("price") != l["price"] and l["price"] is not None \
                and old.get("price") is not None:
            events.append({"type": "price_change", "listing": l,
                           "old_price": old["price"], "date": today()})

    for lid, old in list(known.items()):
        # Only mark removed if its source succeeded this run
        if lid not in cur_ids and old.get("source") in diff.ok_sources \
                and old.get("status") != "removed":
            events.append({"type": "removed", "listing": old, "date": today()})

    return events


def update_state(state, current, events, failures):
    for l in current:
        old = state["listings"].get(l["id"], {})
        state["listings"][l["id"]] = {
            **l,
            "first_seen": old.get("first_seen", today()),
            "last_seen": today(),
            "status": "active",
        }
    for e in events:
        if e["type"] == "removed":
            state["listings"][e["listing"]["id"]]["status"] = "removed"
    state["events"] = (state["events"] + [
        {"type": e["type"], "id": e["listing"]["id"],
         "title": e["listing"]["title"], "url": e["listing"]["url"],
         "price": e["listing"].get("price"),
         "old_price": e.get("old_price"),
         "source": e["listing"].get("source_name", ""),
         "flags": e["listing"].get("flags", []),
         "date": e["date"]}
        for e in events])[-int(state.get("max_events", 200)):]
    state["runs"] = (state["runs"] + [{
        "at": now_iso(), "found": len(current),
        "events": len(events), "failed_sources": failures}])[-50:]
    return state


# ── output rendering ──────────────────────────────────────────────────

def fmt_price(p):
    return f"£{p:,}" if p is not None else "price n/a"


def event_line(e):
    if e["type"] == "new":
        head = f"NEW {fmt_price(e.get('price'))}"
    elif e["type"] == "price_change":
        head = f"PRICE {fmt_price(e.get('old_price'))} → {fmt_price(e.get('price'))}"
    else:
        head = "REMOVED"
    flags = ("  ⚠ " + "; ".join(e.get("flags", []))) if e.get("flags") else ""
    return head, flags


def render_readme_digest(state, failures):
    active = sorted(
        [l for l in state["listings"].values() if l["status"] == "active"],
        key=lambda l: (l["price"] is None, l["price"] or 0))
    lines = [f"_Last run: {now_iso()} — {len(active)} active matches._", ""]
    if failures:
        lines += ["> ⚠ Sources that failed this run: " + ", ".join(failures), ""]
    lines += ["| Price | Property | Source | Flags |", "|---|---|---|---|"]
    for l in active:
        flags = "; ".join(l.get("flags", [])) or "—"
        lines.append(f"| {fmt_price(l['price'])} | [{l['title']}]({l['url']}) "
                     f"| {l['source_name']} | {flags} |")
    lines += ["", "### Recent events", ""]
    for e in reversed(state["events"][-25:]):
        head, flags = event_line(e)
        lines.append(f"- `{e['date']}` **{head}** — [{e['title']}]({e['url']}) "
                     f"({e['source']}){flags}")
    return "\n".join(lines)


def write_readme(digest):
    start, end = "<!--HUNT:START-->", "<!--HUNT:END-->"
    text = README.read_text() if README.exists() else f"# Hunt\n\n{start}\n{end}\n"
    pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.S)
    text = pattern.sub(f"{start}\n{digest}\n{end}", text)
    README.write_text(text)


def rss_escape(s):
    return html.escape(s, quote=True)


def write_feed(state, repo_url):
    items = []
    for e in reversed(state["events"][-50:]):
        head, flags = event_line(e)
        title = f"{head}: {e['title']}"
        desc = f"{e['source']}{flags}"
        guid = f"{e['id']}#{e['type']}#{e['date']}"
        items.append(
            "<item>"
            f"<title>{rss_escape(title)}</title>"
            f"<link>{rss_escape(e['url'])}</link>"
            f"<guid isPermaLink=\"false\">{rss_escape(guid)}</guid>"
            f"<pubDate>{e['date']}</pubDate>"
            f"<description>{rss_escape(desc)}</description>"
            "</item>")
    FEED.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        '<title>Plymouth House Hunt — new listings &amp; price changes</title>'
        f'<link>{rss_escape(repo_url)}</link>'
        '<description>Automated monitor of Plymouth property sources '
        'matching Sarah\'s criteria</description>'
        + "".join(items) + "</channel></rss>")


def write_index(state, failures):
    active = sorted(
        [l for l in state["listings"].values() if l["status"] == "active"],
        key=lambda l: (l["price"] is None, l["price"] or 0))
    rows = "".join(
        f"<tr><td><b>{fmt_price(l['price'])}</b></td>"
        f"<td><a href='{html.escape(l['url'])}'>{html.escape(l['title'])}</a></td>"
        f"<td>{html.escape(l['source_name'])}</td>"
        f"<td>{html.escape('; '.join(l.get('flags', [])) or '—')}</td></tr>"
        for l in active)
    events = "".join(
        f"<li><code>{e['date']}</code> <b>{html.escape(event_line(e)[0])}</b> "
        f"<a href='{html.escape(e['url'])}'>{html.escape(e['title'])}</a> "
        f"({html.escape(e['source'])})</li>"
        for e in reversed(state["events"][-25:]))
    warn = (f"<p class='warn'>⚠ Failed sources this run: "
            f"{html.escape(', '.join(failures))}</p>" if failures else "")
    INDEX.write_text(f"""<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plymouth House Hunt</title><style>
body{{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:2rem auto;
max-width:60rem;padding:0 1rem;color:#1a2332}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:.4rem .6rem;
border-bottom:1px solid #d8dde3;text-align:left;font-size:.95rem}}
a{{color:#0f6b5c}}.warn{{color:#8a5a00}}.muted{{color:#5a6472}}</style></head>
<body><h1>Plymouth House Hunt</h1>
<p class="muted">Last run {now_iso()} · {len(active)} active matches ·
<a href="feed.xml">RSS feed</a></p>{warn}
<table><tr><th>Price</th><th>Property</th><th>Source</th><th>Flags</th></tr>
{rows}</table><h2>Recent events</h2><ul>{events}</ul></body></html>""")


def write_email(events, state, first_run=False):
    groups = {"new": [], "price_change": [], "removed": []}
    for e in events:
        li = {"title": e["listing"]["title"], "url": e["listing"]["url"],
              "price": e["listing"].get("price"),
              "old_price": e.get("old_price"),
              "source": e["listing"].get("source_name", ""),
              "flags": e["listing"].get("flags", [])}
        groups[e["type"]].append(li)

    def section(title, items, kind):
        if not items:
            return ""
        lis = ""
        for l in items:
            if kind == "price_change":
                p = f"{fmt_price(l['old_price'])} → <b>{fmt_price(l['price'])}</b>"
            else:
                p = f"<b>{fmt_price(l['price'])}</b>"
            flags = (f"<br><span style='color:#8a5a00'>⚠ "
                     f"{html.escape('; '.join(l['flags']))}</span>") if l["flags"] else ""
            lis += (f"<li style='margin-bottom:10px'>{p} — "
                    f"<a href='{html.escape(l['url'])}'>{html.escape(l['title'])}</a> "
                    f"<span style='color:#5a6472'>({html.escape(l['source'])})</span>"
                    f"{flags}</li>")
        return f"<h3 style='color:#0f6b5c'>{title}</h3><ul>{lis}</ul>"

    n = len(events)
    disclaimer_html = disclaimer_md = ""
    if first_run:
        disclaimer_html = (
            "<p style='background:#f2f5f4;padding:8px 12px;border-radius:6px'>"
            "ℹ️ <b>First sweep.</b> This lists everything currently matching "
            "across the monitored sources — some of these may already be "
            "familiar from the earlier shortlist PDFs. From now on, emails "
            "only arrive when something genuinely changes.</p>")
        disclaimer_md = (
            "> ℹ️ **First sweep.** This lists everything currently matching "
            "across the monitored sources — some may already be familiar "
            "from the earlier shortlist PDFs. From now on, alerts only "
            "arrive when something genuinely changes.\n\n")
    body = (f"<div style='font-family:sans-serif;max-width:40rem'>"
            f"<h2>Plymouth house hunt — {n} update{'s' if n != 1 else ''}</h2>"
            + disclaimer_html
            + section("🆕 New listings", groups["new"], "new")
            + section("💷 Price changes", groups["price_change"], "price_change")
            + section("🚫 No longer listed", groups["removed"], "removed")
            + "<p style='color:#5a6472;font-size:.85rem'>Criteria: £90k–£140k, "
              "central Plymouth (~1 mi of Buckwell St/The Box), freehold or share "
              "of freehold preferred, no North Hill / Sydney St / Wyndham St W, "
              "service charge ≤£50/yr — always verify tenure, charges and "
              "availability with the agent.</p></div>")
    EMAIL.write_text(body)

    # Markdown twin — used as GitHub Release notes (watchers get emailed).
    def md_section(title, items, kind):
        if not items:
            return ""
        out = f"\n### {title}\n\n"
        for l in items:
            if kind == "price_change":
                p = f"{fmt_price(l['old_price'])} → **{fmt_price(l['price'])}**"
            else:
                p = f"**{fmt_price(l['price'])}**"
            out += f"- {p} — [{l['title']}]({l['url']}) ({l['source']})"
            if l["flags"]:
                out += f"\n  - ⚠ {'; '.join(l['flags'])}"
            out += "\n"
        return out

    EMAIL_MD.write_text(
        f"## Plymouth house hunt — {n} update{'s' if n != 1 else ''}\n"
        + disclaimer_md
        + md_section("🆕 New listings", groups["new"], "new")
        + md_section("💷 Price changes", groups["price_change"], "price_change")
        + md_section("🚫 No longer listed", groups["removed"], "removed")
        + "\n_Always verify tenure, service charges and availability "
          "with the agent._\n")


# ── main ──────────────────────────────────────────────────────────────

def main():
    cfg = yaml.safe_load(CONFIG.read_text())
    crit = cfg["criteria"]
    crit["_exclude_res"] = [re.compile(p, re.I) for p in crit["exclude_patterns"]]
    crit["_exclude_area_res"] = [re.compile(p, re.I)
                                 for p in crit.get("exclude_area_patterns", [])]
    crit["_flag_res"] = [{"re": re.compile(f["pattern"], re.I), "label": f["label"]}
                         for f in crit.get("flag_patterns", [])]

    state = load_state()
    state["max_events"] = cfg.get("max_events", 200)
    first_run = not state["listings"]

    current, failures, ok_sources = [], [], set()
    for source in cfg["sources"]:
        if not source.get("enabled", True):
            continue
        try:
            urls = source.get("urls") or [source["url"]]
            found_map = {}
            for u in urls:
                body = fetch(u)
                if source.get("type") == "feed":
                    page_listings = extract_feed(source, body)
                else:
                    page_listings = extract_listings(
                        {**source, "url": u}, body)
                merge_listings(found_map, page_listings)
                if len(urls) > 1:
                    time.sleep(2)  # be polite between pages
            listings = list(found_map.values())
            matched = apply_criteria(listings, crit)
            print(f"[{source['id']}] fetched: {len(listings)} listings "
                  f"across {len(urls)} page(s), {len(matched)} match criteria")
            current.extend(matched)
            ok_sources.add(source["id"])
        except Exception as exc:  # noqa: BLE001 — keep the run alive
            print(f"[{source['id']}] FAILED: {exc}", file=sys.stderr)
            failures.append(source["name"])
        time.sleep(2)  # be polite

    diff.ok_sources = ok_sources
    events = diff(state, current)
    state = update_state(state, current, events, failures)

    repo = os.environ.get("GITHUB_REPOSITORY", "")
    repo_url = f"https://github.com/{repo}" if repo else "https://example.invalid"

    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=1, ensure_ascii=False))
    FEED.parent.mkdir(exist_ok=True)
    write_readme(render_readme_digest(state, failures))
    write_feed(state, repo_url)
    write_index(state, failures)

    notify = bool(events) and (not first_run or cfg.get("first_run_notify"))
    EMAIL.parent.mkdir(exist_ok=True)
    if notify:
        write_email(events, state, first_run=first_run)
    else:
        for f in (EMAIL, EMAIL_MD):
            if f.exists():
                f.unlink()

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"changes={'true' if notify else 'false'}\n")
            fh.write(f"summary={len(events)} events, {len(current)} active, "
                     f"{len(failures)} failed sources\n")
    print(f"Done: {len(events)} events ({'notify' if notify else 'silent'}), "
          f"{len(current)} current matches, failures: {failures or 'none'}")


if __name__ == "__main__":
    main()