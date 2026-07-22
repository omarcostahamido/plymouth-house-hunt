# 🏠 Plymouth House Hunt

Automated monitor for Sarah's Plymouth property search. Twice a day, a
GitHub Action fetches the sources below, applies her criteria, diffs
against the last run, and — when something changed (new listing, price
change, or delisting) — sends notifications and updates the
[RSS feed](docs/feed.xml), the README digest below, and the web digest
(if GitHub Pages is enabled).

**Criteria:** £90,000–£140,000 · central Plymouth (~1 mile of Buckwell
Street / The Box) · freehold or share of freehold preferred · excludes
North Hill, Sydney Street, Wyndham Street West and retirement homes ·
flags auctions, possible sitting tenants, unknown tenure, and
possible lettings.

**Monitored sources** (all live-tested 2026-07-21/22 — see per-source
notes in [`hunt/config.yaml`](hunt/config.yaml)): Lang Town & Country
(RSS feed), Atwell Martin (RSS feed), Cross Keys Estates (RSS feed),
DC Lane, SO Living / Plymouth Community Homes shared-ownership
resales, OnTheMarket (best-effort — may be bot-blocked from GitHub's
servers; the digest shows if so). Disabled with reasons in the config:
Pilkington (JavaScript-only site), LiveWest (bot-protected; resales
reach Share to Buy anyway), Share to Buy (Cloudflare challenge +
robots.txt disallow; use its native alert).

> **Not monitored here (by design):** Zoopla, Rightmove and Share to
> Buy block automated fetching and their terms/robots rules prohibit
> scraping, so Sarah should set their own free email alerts once —
> Zoopla *Create email alert* on [this exact search](https://www.zoopla.co.uk/for-sale/property/plymouth/buckwell-street/pl1-2da/?is_retirement_home=false&price_max=140000&price_min=90000&property_sub_type=detached&property_sub_type=semi_detached&property_sub_type=terraced&property_sub_type=flats&property_sub_type=bungalow&radius=1&tenure=freehold&tenure=share_of_freehold),
> a Rightmove alert on [this search](https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=POSTCODE%5E665046&maxPrice=140000&radius=1.0&minPrice=90000&dontShow=retirement)
> (no tenure filter there — expect some leasehold noise), and Share to
> Buy *Create Alert* for Plymouth. Between those three alerts and this
> repo, every source is covered.

## How Sarah gets notified (pick any, or all)

Channels 1 and 2 are both free — try both and keep whichever email
layout Sarah prefers.

1. **Watch the repo (free, no setup).** Each alert is published as a
   GitHub Release. Sarah creates a free GitHub account, opens this
   repo, clicks **Watch → Custom → Releases**. GitHub then emails her
   every alert, full details in the release notes.
   *Easy off-switch:* Settings → Secrets and variables → Actions →
   Variables → add `RELEASES_OFF` = `true`. The RSS feed and digests
   keep updating regardless.
2. **RSS by email (free).** The [feed](docs/feed.xml) is always
   generated, whatever other channels are on. Once GitHub Pages is
   enabled, subscribe its Pages URL
   (`https://<user>.github.io/<repo>/feed.xml`) with
   [Feedrabbit](https://feedrabbit.com) (free plan: 10 feeds,
   20 emails/day, polls every 3 hours — comfortably enough for a
   twice-daily monitor) or [Blogtrottr](https://blogtrottr.com)
   (free, unlimited feeds, ad-supported).
3. **Direct SMTP email (optional, when you get round to it).** Add
   repo secrets `MAIL_USERNAME` + `MAIL_PASSWORD` (Gmail app password
   or any SMTP) and variable `MAIL_TO` = Sarah's address. Without
   these the step simply skips — nothing breaks.

## Setup (one-time, ~10 minutes)

1. **Create the repo.** Push these files to a new **public** GitHub
   repo (public = Actions free without limits).
2. **Allow the workflow to write.** Settings → Actions → General →
   Workflow permissions → *Read and write permissions*.
3. **Web digest + feed URL (optional).** Settings → Pages → Deploy
   from branch → `main` / `docs`. Digest + `feed.xml` go live at
   `https://<user>.github.io/<repo>/`.
4. **First run.** Actions tab → *House hunt* → *Run workflow*. The
   first sweep sends a full "everything currently matching" alert with
   a disclaimer that some entries may already be familiar from the
   earlier shortlist PDFs. From the second run onward, only genuine
   changes notify. (Prefer a silent baseline instead? Set
   `first_run_notify: false` in `hunt/config.yaml` before the first
   run.)
5. **Check the first run's log.** Each source prints how many listings
   it fetched; failures are listed in the README digest. If a source
   shows 0 or fails, paste the log back into the Claude session to get
   the config tuned.

The workflow commits its state every run, which also keeps GitHub's
60-day scheduled-workflow auto-disable at bay. Edit
`hunt/config.yaml` any time to change criteria — the next run picks
it up automatically.

## Current digest

<!--HUNT:START-->
_Last run: 2026-07-22T16:39:32Z — 83 active matches._

| Price | Property | Source | Flags |
|---|---|---|---|
| £90,000 | [19790425](https://www.onthemarket.com/details/19790425/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [North Road West, Plymouth](https://www.onthemarket.com/details/19146127/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £90,000 | [19903154](https://www.onthemarket.com/details/19903154/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [19563126](https://www.onthemarket.com/details/19563126/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [16705428](https://www.onthemarket.com/details/16705428/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [North Road West, Plymouth, Devon, PL1](https://www.onthemarket.com/details/18945835/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £90,000 | [17879716](https://www.onthemarket.com/details/17879716/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [17751552](https://www.onthemarket.com/details/17751552/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £90,000 | [18063813](https://www.onthemarket.com/details/18063813/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £95,000 | [Dale Road, Plymouth, Devon, PL4](https://www.onthemarket.com/details/19808047/) | OnTheMarket (portal) | Auction; Leasehold? — check tenure |
| £95,000 | [Flat 2, 62 Dale Road, Plymouth, Devon, PL4 6PA](https://www.onthemarket.com/details/19777673/) | OnTheMarket (portal) | Auction; Leasehold? — check tenure |
| £100,000 | [Thompson Road, Plymouth*](https://www.so-living.co.uk/find-a-home/our-developments/devon/homes-for-resale-devon/thompson-road-plymouthstar/thompson-road-plymouthstar/) | SO Living / Plymouth Community Homes (shared-ownership resales) | Shared ownership / share price |
| £100,000 | [19951472](https://www.onthemarket.com/details/19951472/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [19876855](https://www.onthemarket.com/details/19876855/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [19856242](https://www.onthemarket.com/details/19856242/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [Ebrington Street, Plymouth](https://www.onthemarket.com/details/18878125/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £100,000 | [Cattedown Road, Plymouth, Devon, PL4](https://www.onthemarket.com/details/19070183/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £100,000 | [15185827](https://www.onthemarket.com/details/15185827/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [19065581](https://www.onthemarket.com/details/19065581/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [18011542](https://www.onthemarket.com/details/18011542/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [19839506](https://www.onthemarket.com/details/19839506/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £100,000 | [19176060](https://www.onthemarket.com/details/19176060/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £105,000 | [Ford Park Road, Plymouth](https://www.onthemarket.com/details/17508392/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £110,000 | [Stillman Court, Plymouth](https://www.onthemarket.com/details/19689865/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £110,000 | [19775476](https://www.onthemarket.com/details/19775476/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £110,000 | [19608500](https://www.onthemarket.com/details/19608500/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £110,000 | [Sutton Wharf, Plymouth](https://www.onthemarket.com/details/19169216/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £110,000 | [Alexandra Road, Mutley, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18926524/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £110,000 | [17455724](https://www.onthemarket.com/details/17455724/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £110,000 | [19516810](https://www.onthemarket.com/details/19516810/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £115,000 | [19469900](https://www.onthemarket.com/details/19469900/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £115,000 | [19013663](https://www.onthemarket.com/details/19013663/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £117,500 | [19503626](https://www.onthemarket.com/details/19503626/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £117,500 | [18684298](https://www.onthemarket.com/details/18684298/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £120,000 | [Grenville Road, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18945894/) | OnTheMarket (portal) | Shared ownership / share price |
| £120,000 | [Castle Dyke Lane, Plymouth](https://www.onthemarket.com/details/19260382/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £120,000 | [19713473](https://www.onthemarket.com/details/19713473/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £120,000 | [Moon Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/19464194/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £120,000 | [Regent Street, Plymouth](https://www.onthemarket.com/details/19304343/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £120,000 | [King Street, Plymouth](https://www.onthemarket.com/details/18878244/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £123,000 | [18743343](https://www.onthemarket.com/details/18743343/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £125,000 | [17748051](https://www.onthemarket.com/details/17748051/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £125,000 | [Mildmay Street, Plymouth](https://www.onthemarket.com/details/19919472/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £125,000 | [19165028](https://www.onthemarket.com/details/19165028/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £125,000 | [Gascoyne Place, Plymouth](https://www.onthemarket.com/details/19548143/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £125,000 | [Morley Court, Plymouth](https://www.onthemarket.com/details/19533457/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £125,000 | [Clifton Place, Greenbank, Plymouth](https://www.onthemarket.com/details/18886681/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £130,000 | [Exeter Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18945901/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £130,000 | [19961185](https://www.onthemarket.com/details/19961185/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [19932652](https://www.onthemarket.com/details/19932652/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [Moon Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18951909/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £130,000 | [19819774](https://www.onthemarket.com/details/19819774/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [19776211](https://www.onthemarket.com/details/19776211/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [19538833](https://www.onthemarket.com/details/19538833/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [Moon Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/19660073/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £130,000 | [19489978](https://www.onthemarket.com/details/19489978/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [How Street, Plymouth](https://www.onthemarket.com/details/18913922/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £130,000 | [19008343](https://www.onthemarket.com/details/19008343/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £130,000 | [19895470](https://www.onthemarket.com/details/19895470/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £135,000 | [19562416](https://www.onthemarket.com/details/19562416/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £135,000 | [19275236](https://www.onthemarket.com/details/19275236/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £135,000 | [16293795](https://www.onthemarket.com/details/16293795/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [Citadel Road, Plymouth, Devon, PL1](https://www.onthemarket.com/details/18704541/) | OnTheMarket (portal) | Leasehold? — check tenure |
| £140,000 | [19431408](https://www.onthemarket.com/details/19431408/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19684875](https://www.onthemarket.com/details/19684875/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19781378](https://www.onthemarket.com/details/19781378/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19094566](https://www.onthemarket.com/details/19094566/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19654667](https://www.onthemarket.com/details/19654667/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [17171237](https://www.onthemarket.com/details/17171237/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19593904](https://www.onthemarket.com/details/19593904/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [19007028](https://www.onthemarket.com/details/19007028/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| £140,000 | [18816143](https://www.onthemarket.com/details/18816143/) | OnTheMarket (portal) | Location unverified — check it's central Plymouth |
| price n/a | [Notte Street, Plymouth, PL1](https://plymouth.atwellmartin.co.uk/property/f112bea4-e4eb-4197-8a4a-205c84114acb-l/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [Salisbury Road, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/dbb96270-b0ae-460b-b9a4-caee94522e4f-l/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [Greenbank Road, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/9fee3d69-478a-43f2-8e62-ac2898e7d32d-l/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [Beaumont Road, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/32e2c5d0-d3bc-41de-a5cf-5d00f6f2ee3a/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [60 Exeter Street, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/ceb58ab5-bea5-479d-bc5a-08868de1f7e2/) | Atwell Martin Plymouth (agent) | May have sitting tenants; Price not read — open listing |
| price n/a | [Cliff Road, Plymouth, PL1](https://plymouth.atwellmartin.co.uk/property/e8f24d5d-15f8-420e-92f4-06b0979ba408-l/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [Neath Road, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/319151ea-7c15-496f-b3f4-644102b35d8d/) | Atwell Martin Plymouth (agent) | May have sitting tenants; Price not read — open listing; Shared ownership / share price |
| price n/a | [Lipson Road, Plymouth, PL4](https://plymouth.atwellmartin.co.uk/property/4b71cd32-c6ba-4771-829a-70b2335dc4d8-l/) | Atwell Martin Plymouth (agent) | Price not read — open listing |
| price n/a | [Castle Street, The Barbican](https://www.crosskeysestates.net/property/castle-street-the-barbican/) | Cross Keys Estates (agent) | Location unverified — check it's central Plymouth; Price not read — open listing |
| price n/a | [Custom House Lane, The Hoe](https://www.crosskeysestates.net/property/custom-house-lane-the-hoe/) | Cross Keys Estates (agent) | Location unverified — check it's central Plymouth; Price not read — open listing |
| price n/a | [Cremyll Street, Stonehouse](https://www.crosskeysestates.net/property/cremyll-street-stonehouse/) | Cross Keys Estates (agent) | Location unverified — check it's central Plymouth; Price not read — open listing |

### Recent events

- `2026-07-22` **NEW price n/a** — [Cremyll Street, Stonehouse](https://www.crosskeysestates.net/property/cremyll-street-stonehouse/) (Cross Keys Estates (agent))  ⚠ Location unverified — check it's central Plymouth; Price not read — open listing
- `2026-07-22` **NEW price n/a** — [Custom House Lane, The Hoe](https://www.crosskeysestates.net/property/custom-house-lane-the-hoe/) (Cross Keys Estates (agent))  ⚠ Location unverified — check it's central Plymouth; Price not read — open listing
- `2026-07-22` **NEW price n/a** — [Castle Street, The Barbican](https://www.crosskeysestates.net/property/castle-street-the-barbican/) (Cross Keys Estates (agent))  ⚠ Location unverified — check it's central Plymouth; Price not read — open listing
- `2026-07-22` **NEW £100,000** — [19176060](https://www.onthemarket.com/details/19176060/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £135,000** — [16293795](https://www.onthemarket.com/details/16293795/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £140,000** — [18816143](https://www.onthemarket.com/details/18816143/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £140,000** — [19007028](https://www.onthemarket.com/details/19007028/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £140,000** — [19593904](https://www.onthemarket.com/details/19593904/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £110,000** — [19516810](https://www.onthemarket.com/details/19516810/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £90,000** — [18063813](https://www.onthemarket.com/details/18063813/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £100,000** — [19839506](https://www.onthemarket.com/details/19839506/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £130,000** — [19895470](https://www.onthemarket.com/details/19895470/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £110,000** — [17455724](https://www.onthemarket.com/details/17455724/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £90,000** — [17751552](https://www.onthemarket.com/details/17751552/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £90,000** — [17879716](https://www.onthemarket.com/details/17879716/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £100,000** — [18011542](https://www.onthemarket.com/details/18011542/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £123,000** — [18743343](https://www.onthemarket.com/details/18743343/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £120,000** — [King Street, Plymouth](https://www.onthemarket.com/details/18878244/) (OnTheMarket (portal))  ⚠ Leasehold? — check tenure
- `2026-07-22` **NEW £110,000** — [Alexandra Road, Mutley, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18926524/) (OnTheMarket (portal))  ⚠ Leasehold? — check tenure
- `2026-07-22` **NEW £125,000** — [Clifton Place, Greenbank, Plymouth](https://www.onthemarket.com/details/18886681/) (OnTheMarket (portal))  ⚠ Leasehold? — check tenure
- `2026-07-22` **NEW £90,000** — [North Road West, Plymouth, Devon, PL1](https://www.onthemarket.com/details/18945835/) (OnTheMarket (portal))  ⚠ Leasehold? — check tenure
- `2026-07-22` **NEW £130,000** — [19008343](https://www.onthemarket.com/details/19008343/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £115,000** — [19013663](https://www.onthemarket.com/details/19013663/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £100,000** — [19065581](https://www.onthemarket.com/details/19065581/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
- `2026-07-22` **NEW £90,000** — [16705428](https://www.onthemarket.com/details/16705428/) (OnTheMarket (portal))  ⚠ Location unverified — check it's central Plymouth
<!--HUNT:END-->
