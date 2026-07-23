"""Offline pipeline test — no network. Run: python tests/test_pipeline.py"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "hunt"))
import hunt  # noqa: E402

FIXTURE = """
<html><body>
<div class="card"><a href="/property/otm-style/">£125,000</a>
<address>Gascoyne Place, Plymouth, PL4</address><p>Offers over £125,000 · flat</p></div>
<div class="card"><h3><a href="/property/far-away/">3 bed house in Sherford</a></h3>
<p>£130,000 · lovely, short drive to Plymstock</p></div>
<div class="card"><h3><a href="/property/nice-flat-pl1/">1 bed flat, Hoe Road, Plymouth PL1</a></h3>
<p>Guide price £120,000 · share of freehold · chain free · near Plymstock shops</p></div>
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
    "_exclude_area_res": [re.compile(p, re.I) for p in
                          [r"\bsherford\b", r"\bplymstock\b", r"\bstoke\b"]],
    "_flag_res": [
        {"re": re.compile("auction", re.I), "label": "Auction"},
        {"re": re.compile("tenant|currently let", re.I), "label": "May have sitting tenants"},
    ],
}

listings = hunt.extract_listings(SRC, FIXTURE)
assert len(listings) == 6, f"expected 6 property links, got {len(listings)}"
# OTM-style card: <address> wins over price-only link text
otm = next(l for l in listings if l["id"].endswith("/otm-style/"))
assert otm["title"] == "Gascoyne Place, Plymouth, PL4", otm["title"]
matched = hunt.apply_criteria(listings, CRIT)
titles = sorted(m["title"] for m in matched)
# Sherford house dropped (area in title); Hoe Road flat kept despite
# "near Plymstock shops" in its DESCRIPTION (area excludes are title-only)
assert not any("Sherford" in t for t in titles), titles
assert any("Hoe Road" in t for t in titles), titles
assert any("Gascoyne" in t for t in titles), titles
assert len(matched) == 3, f"expected 3 matches, got {titles}"
auction = next(m for m in matched if "Cattedown" in m["title"])
assert "Auction" in auction["flags"] and "May have sitting tenants" in auction["flags"]

# run 1: baseline
state = {"listings": {}, "events": [], "runs": [], "max_events": 200}
hunt.diff.ok_sources = {"test"}
ev1 = hunt.diff(state, matched)
assert len(ev1) == 3 and all(e["type"] == "new" for e in ev1)
state = hunt.update_state(state, matched, ev1, [])

# run 2: price drop on one, the other two disappear
hoe = next(m for m in matched if "Hoe Road" in m["title"])
m2 = [dict(hoe, price=110000)]
ev2 = hunt.diff(state, m2)
types = sorted(e["type"] for e in ev2)
assert types == ["price_change", "removed", "removed"], types
state = hunt.update_state(state, m2, ev2, [])
assert sum(1 for l in state["listings"].values() if l["status"] == "active") == 1

# duplicate-merge: featured module (ID title, no address/price) loses to real card
FEATURED = """
<html><body>
<div class="promo"><a href="/details/12345">See it</a><span>£99,999 featured</span></div>
</body></html>"""
REAL = """
<html><body>
<div class="card"><a href="/details/12345">£110,000</a>
<address>Wyndham Street West, Plymouth PL1</address><p>Offers over £110,000</p></div>
</body></html>"""
otm_src = {"id": "otm", "name": "OTM", "url": "https://portal.example/list",
           "link_regex": r"/details/\d+"}
fmap = {}
hunt.merge_listings(fmap, hunt.extract_listings(otm_src, FEATURED))
hunt.merge_listings(fmap, hunt.extract_listings(otm_src, REAL))
merged = list(fmap.values())
assert len(merged) == 1 and "Wyndham Street" in merged[0]["title"], merged
assert merged[0]["has_address"] is True

# require_address: a promo-module-only capture is droppable
fmap2 = {}
hunt.merge_listings(fmap2, hunt.extract_listings(otm_src, FEATURED))
only_promo = [l for l in fmap2.values() if l.get("has_address")]
assert only_promo == [], "promo capture must not carry has_address"

# conditional exclude: confirmed leasehold drops, unless shared ownership
COND = [{"re": re.compile(r"tenure:\s*leasehold", re.I),
         "unless_re": re.compile("shared ownership", re.I)}]
crit_cond = dict(CRIT, _exclude_cond_res=COND)
lease = {"id": "l1", "url": "u", "title": "Moon Street, Plymouth PL4",
         "price": 120000, "card_text": "Flat Tenure: Leasehold nice",
         "source": "t", "source_name": "T"}
so = {"id": "l2", "url": "u2", "title": "Ballad Gardens, Plymouth PL5",
      "price": 100000, "card_text": "Shared ownership resale Tenure: Leasehold 990 yrs",
      "source": "t", "source_name": "T"}
out = hunt.apply_criteria([dict(lease), dict(so)], crit_cond)
assert [o["id"] for o in out] == ["l2"], out
# ...and the merged (address) title now hits Sarah's street excludes:
assert hunt.apply_criteria(merged, CRIT) == [] if any(
    r.pattern == "wyndham street" for r in CRIT["_exclude_res"]) else True

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

# card_container: deep climb finds the full card (price in sub-block,
# address elsewhere), but never swallows the multi-card results list
DEEP = """
<html><body><ul>
<li class="card"><div class="pricebox"><a href="/details/777">£120,000</a></div>
<div class="info"><address>Ebrington Street, Plymouth PL4</address>
<p>Tenure: Freehold</p></div></li>
<li class="card"><div class="pricebox"><a href="/details/888">£130,000</a></div>
<div class="info"><address>Pier Street, Plymouth PL1</address>
<p>Tenure: Share of freehold</p></div></li>
</ul></body></html>"""
deep = hunt.extract_listings({"id": "otm", "name": "OTM",
                              "url": "https://portal.example/x",
                              "link_regex": r"/details/\d+"}, DEEP)
assert len(deep) == 2, deep
by_id = {l["id"].rsplit("/", 1)[-1]: l for l in deep}
assert by_id["777"]["title"] == "Ebrington Street, Plymouth PL4", by_id
assert by_id["888"]["title"] == "Pier Street, Plymouth PL1", by_id
assert all(l["has_address"] for l in deep)

# price enrichment: cache first, then page fetch, respecting the cap
orig_fetch = hunt.fetch
hunt.fetch = lambda url, timeout=30: "<title>2 bed flat £128,000</title><body>x</body>"
ls = [{"id": "a", "url": "https://e/a", "price": None},
      {"id": "b", "url": "https://e/b", "price": None},
      {"id": "c", "url": "https://e/c", "price": 95000}]
known_state = {"a": {"price": 111000}}
budget = {"left": 1}
_sleep = hunt.time.sleep
hunt.time.sleep = lambda s: None
hunt.enrich_prices(ls, known_state, budget)
hunt.fetch = orig_fetch
assert ls[0]["price"] == 111000        # from cache, no fetch spent
assert ls[1]["price"] == 128000        # fetched from page title
assert ls[2]["price"] == 95000         # untouched
assert budget["left"] == 0

# letting detection on detail pages: '£895 pcm' page → is_letting, dropped
hunt.fetch = lambda url, timeout=30: ("<title>1 bed flat to rent</title>"
                                      "<body>Available now £895 pcm</body>")
lt = [{"id": "r1", "url": "https://e/r1", "price": None,
       "title": "Notte Street, Plymouth PL1", "card_text": "flat",
       "source": "t", "source_name": "T"}]
budget2 = {"left": 5}
hunt.enrich_prices(lt, {}, budget2)
hunt.fetch = orig_fetch
hunt.time.sleep = _sleep
assert lt[0]["is_letting"] is True
out2 = hunt.apply_price_and_flags(lt, CRIT, {"letting": 0, "price": 0})
assert out2 == []

# sale page with a mortgage-calculator 'per month' is NOT a letting
p, isl = hunt.price_from_page("<title>House £270,000</title><body>"
                              "Estimated mortgage £1,318 per month</body>")
assert p == 270000 and isl is False

# feed url_exclude_regex drops '-l' letting slugs
FEED2 = """<?xml version="1.0"?><rss version="2.0"><channel><title>A</title>
<item><title>Sale House, PL4</title><link>https://a.example/property/abc123/</link>
<description>house</description></item>
<item><title>Rental Flat, PL1</title><link>https://a.example/property/def456-l/</link>
<description>flat</description></item>
</channel></rss>"""
f2 = hunt.extract_feed({"id": "a", "name": "A", "type": "feed",
                        "url": "https://a.example/property/feed/",
                        "link_regex": r"a\.example/property/[a-z0-9-]+/?$",
                        "url_exclude_regex": r"-l/?$"}, FEED2)
assert [l["title"] for l in f2] == ["Sale House, PL4"], f2

# stretch band: 140k–160k kept with an over-budget flag; >160k dropped
crit_s = dict(CRIT, stretch_max=160000)
sl = [{"id": "s1", "url": "u", "title": "Ford Park Road, Mutley, Plymouth PL4",
       "price": 155000, "card_text": "maisonette", "source": "t", "source_name": "T"},
      {"id": "s2", "url": "u", "title": "Somewhere, Plymouth PL4",
       "price": 175000, "card_text": "house", "source": "t", "source_name": "T"},
      {"id": "s3", "url": "u", "title": "Cheap Corner, Plymouth PL1",
       "price": 60000, "card_text": "studio", "source": "t", "source_name": "T"}]
outs = hunt.apply_price_and_flags([dict(x) for x in sl],
                                  dict(crit_s, min_price=50000),
                                  {"letting": 0, "price": 0})
ids = [o["id"] for o in outs]
assert ids == ["s1", "s3"], ids
assert any("Over budget" in f for f in outs[0]["flags"])
assert not any("Over budget" in f for f in outs[1]["flags"])

# sanity floor: below-min extraction raises instead of returning partials
calls = {"n": 0}
orig_once = hunt.fetch_source_once
def fake_once(source):
    calls["n"] += 1
    return []  # simulate a bot-challenge page: valid HTML, zero listings
hunt.fetch_source_once = fake_once
try:
    hunt.fetch_source_with_retry({"id": "x", "name": "X", "url": "u",
                                  "min_listings": 5}, retry_wait=0)
    raise SystemExit("sanity floor did not raise")
except RuntimeError as e:
    assert "sanity floor" in str(e)
assert calls["n"] == 2, "should retry exactly once"
hunt.fetch_source_once = orig_once

print("ALL PIPELINE TESTS PASSED")
