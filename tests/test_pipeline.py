"""Offline pipeline test — no network. Run: python tests/test_pipeline.py"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hunt"))
import hunt  # noqa: E402

FIXTURE = """
<html><body>
<div class="card"><h3><a href="/property/nice-flat-pl1/">1 bed flat, Hoe Road, Plymouth PL1</a></h3>
<p>Guide price £120,000 · share of freehold · chain free</p></div>
<div class="card"><h3><a href="/property/north-hill-flat/">2 bed flat, North Hill, Plymouth PL4</a></h3>
<p>£115,000</p></div>
<div class="card"><h3><a href="/property/pricey-house/">3 bed house, Embankment Rd, Plymouth PL4</a></h3>
<p>£165,000 freehold</p></div>
<div class="card"><h3><a href="/property/auction-terrace/">2 bed terrace, Cattedown, Plymouth PL4</a></h3>
<p>Guide £100,000 — for sale by auction, currently let to tenants</p></div>
<div class="card"><h3><a href="/about-us/">About us</a></h3></div>
</body></html>
"""

SRC = {"id": "test", "name": "Test Agent", "url": "https://agent.example/list/",
       "link_regex": r"agent\.example/property/[a-z0-9-]+/?$"}

CRIT = {
    "min_price": 90000, "max_price": 140000,
    "area_keywords": ["PL1", "PL4", "Plymouth"],
    "_exclude_res": [re.compile(p, re.I) for p in
                     ["north hill", "sydney street", "wyndham street", "retirement"]],
    "_flag_res": [
        {"re": re.compile("auction", re.I), "label": "Auction"},
        {"re": re.compile("tenant|currently let", re.I), "label": "May have sitting tenants"},
    ],
}

listings = hunt.extract_listings(SRC, FIXTURE)
assert len(listings) == 4, f"expected 4 property links, got {len(listings)}"
matched = hunt.apply_criteria(listings, CRIT)
titles = sorted(m["title"] for m in matched)
assert len(matched) == 2, f"expected 2 matches, got {titles}"
assert any("Hoe Road" in t for t in titles)
auction = next(m for m in matched if "Cattedown" in m["title"])
assert "Auction" in auction["flags"] and "May have sitting tenants" in auction["flags"]

# run 1: baseline
state = {"listings": {}, "events": [], "runs": [], "max_events": 200}
hunt.diff.ok_sources = {"test"}
ev1 = hunt.diff(state, matched)
assert len(ev1) == 2 and all(e["type"] == "new" for e in ev1)
state = hunt.update_state(state, matched, ev1, [])

# run 2: price drop on one, other disappears
m2 = [dict(matched[0], price=110000)]
ev2 = hunt.diff(state, m2)
types = sorted(e["type"] for e in ev2)
assert types == ["price_change", "removed"], types
state = hunt.update_state(state, m2, ev2, [])
assert sum(1 for l in state["listings"].values() if l["status"] == "active") == 1

# feed parsing
FEED_XML = """<?xml version="1.0"?><rss version="2.0"><channel>
<title>Agent</title>
<item><title>Notte Street, Plymouth, PL1</title>
<link>https://agent.example/property/notte-street-plymouth/</link>
<description>&lt;p&gt;Two bed apartment, chain free&lt;/p&gt;</description></item>
<item><title>Somewhere, Bude, EX23</title>
<link>https://agent.example/property/somewhere-bude/</link>
<description>Cottage to let &#163;950 pcm</description></item>
</channel></rss>"""
feed_src = {"id": "feedtest", "name": "Feed Agent", "type": "feed",
            "url": "https://agent.example/property/feed/",
            "link_regex": r"agent\.example/property/[a-z0-9-]+/?$"}
fl = hunt.extract_feed(feed_src, FEED_XML)
assert len(fl) == 2, f"feed items: {len(fl)}"
fm = hunt.apply_criteria(fl, CRIT)
assert len(fm) == 2  # no prices → not price-filtered
plymouth_item = next(m for m in fm if "Notte" in m["title"])
assert any("Price not read" in f for f in plymouth_item["flags"])
bude_item = next(m for m in fm if "Bude" in m["title"])
assert any("Location unverified" in f for f in bude_item["flags"])

# outputs render without crashing
hunt.STATE.parent.mkdir(exist_ok=True)
hunt.FEED.parent.mkdir(exist_ok=True)
hunt.EMAIL.parent.mkdir(exist_ok=True)
hunt.write_readme(hunt.render_readme_digest(state, ["Broken Source"]))
hunt.write_feed(state, "https://github.com/example/repo")
hunt.write_index(state, [])
hunt.write_email(ev2, state)
assert "PRICE" in hunt.FEED.read_text()
assert "£110,000" in hunt.EMAIL.read_text()
assert "Broken Source" in hunt.README.read_text()
json.loads(json.dumps(state))  # serialisable

print("ALL PIPELINE TESTS PASSED")
