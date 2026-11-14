# 🏠 Plymouth House Hunt

Automated monitor for Sarah's Plymouth property search. Twice a day, a
GitHub Action fetches the sources below, applies her criteria, diffs
against the last run, and — when something changed (new listing, price
change, or delisting) — sends notifications and updates the
[RSS feed](docs/feed.xml), the README digest below, and the web digest
(if GitHub Pages is enabled).

**Criteria:** £50,000–£140,000 core budget, with a stretch band to
£160,000 (stretch listings are kept but flagged "Over budget") ·
central Plymouth (~1 mile of Buckwell Street / The Box) · freehold or
share of freehold preferred · excludes North Hill, Sydney Street,
Wyndham Street West and retirement homes · flags auctions, possible
sitting tenants, unknown tenure, and possible lettings.

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
_Last run: 2026-11-14T13:41:40Z — 23 active matches._

> ⚠ Sources that failed this run: Atwell Martin Plymouth (agent), Cross Keys Estates (agent)

| Price | Property | Source | Flags |
|---|---|---|---|
| £65,000 | [Arundel Crescent, Plymouth PL1](https://www.onthemarket.com/details/19274935/) | OnTheMarket (portal) | Leasehold? — check tenure; Shared ownership / share price |
| £70,000 | [Constantine Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/20447369/) | OnTheMarket (portal) | Auction |
| £90,000 | [Ebrington Street, Plymouth, Devon, PL4](https://www.onthemarket.com/details/20169397/) | OnTheMarket (portal) | May have sitting tenants; Might be a letting, not a sale (agent feeds mix both) |
| £90,000 | [Bayswater Road, Devon PL1](https://www.onthemarket.com/details/17863187/) | OnTheMarket (portal) | — |
| £90,000 | [Embankment Road, Plymouth. Stylish 2-Bedroom Top Floor Flat in Central Plymouth walking distance to City Center.](https://www.onthemarket.com/details/17879716/) | OnTheMarket (portal) | — |
| £90,000 | [41 Prince Maurice Road, Plymouth, Devon, PL4 7LJ](https://www.onthemarket.com/details/20695964/) | OnTheMarket (portal) | Auction |
| £100,000 | [Fully Managed Plymouth Flat, Plymouth City Centre](https://www.onthemarket.com/details/20425980/) | OnTheMarket (portal) | — |
| £105,000 | [Grenville Road, Plymouth, Devon, PL4](https://www.onthemarket.com/details/18945894/) | OnTheMarket (portal) | — |
| £110,000 | [Arundel Crescent, Devon PL1](https://www.onthemarket.com/details/20434701/) | OnTheMarket (portal) | — |
| £110,000 | [14 Francis Street, Plymouth, Devon PL1 5JZ](https://www.onthemarket.com/details/20577567/) | OnTheMarket (portal) | Auction |
| £110,000 | [Hands Off Plymouth Apartment, Plymouth](https://www.onthemarket.com/details/20627767/) | OnTheMarket (portal) | — |
| £120,000 | [Ladysmith Road, Plymouth](https://www.onthemarket.com/details/20381777/) | OnTheMarket (portal) | — |
| £125,000 | [FFF, 16 Bishops Place, The Hoe Plymouth. Contemporary coastal living close to Plymouth Hoe and the vibrant waterfront.](https://www.onthemarket.com/details/19932652/) | OnTheMarket (portal) | — |
| £130,000 | [Laira Street, St Judes, Plymouth. Prime City-Centre Project – Spacious 3 Double Bedroom Home Packed with Potential](https://www.onthemarket.com/details/19776211/) | OnTheMarket (portal) | — |
| £130,000 | [Hands Off Plymouth Apartment, Plymouth](https://www.onthemarket.com/details/20696474/) | OnTheMarket (portal) | — |
| £130,000 | [Wyndham Square, Stonehouse, Plymouth. Spacious 3 bedroom maisonette in a central location sold with no chain!!](https://www.onthemarket.com/details/20756660/) | OnTheMarket (portal) | — |
| £135,000 | [Hotham Place, Plymouth, Devon, PL1](https://www.onthemarket.com/details/20675025/) | OnTheMarket (portal) | Auction |
| £140,000 | [Exeter Street, Chain-Free|Two Double Bedrooms,  Balcony , Prime City Centre Location](https://www.onthemarket.com/details/17171237/) | OnTheMarket (portal) | — |
| £140,000 | [39 Alexandra Road, Mutley, Plymouth, Devon PL4 7EE](https://www.onthemarket.com/details/20707264/) | OnTheMarket (portal) | Auction |
| £145,000 | [The Barbican, Plymouth](https://www.onthemarket.com/details/20101752/) | OnTheMarket (portal) | Over budget — stretch (above £140,000) |
| £155,000 | [Bayswater Road, Plymouth PL1](https://www.onthemarket.com/details/19649536/) | OnTheMarket (portal) | Over budget — stretch (above £140,000) |
| £160,000 | [Victoria Avenue, Plymouth](https://www.onthemarket.com/details/20139475/) | OnTheMarket (portal) | Over budget — stretch (above £140,000) |
| £160,000 | [Victoria Avenue, Plymouth, Devon, PL1](https://www.onthemarket.com/details/20083635/) | OnTheMarket (portal) | Over budget — stretch (above £140,000) |

### Recent events

- `2026-11-13` **REMOVED** — [St. James Place West, The Hoe, Plymouth](https://www.langtownandcountry.com/property/st-james-place-west-the-hoe-plymouth/) (Lang Town & Country (agent))  ⚠ Over budget — stretch (above £140,000)
- `2026-11-13` **NEW £130,000** — [Wyndham Square, Stonehouse, Plymouth. Spacious 3 bedroom maisonette in a central location sold with no chain!!](https://www.onthemarket.com/details/20756660/) (OnTheMarket (portal))
- `2026-11-12` **REMOVED** — [Alexandra Road,Mutley,Plymouth,PL4 7EE](https://www.onthemarket.com/details/20738902/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-12` **PRICE £120,000 → £110,000** — [Arundel Crescent, Devon PL1](https://www.onthemarket.com/details/20434701/) (OnTheMarket (portal))
- `2026-11-11` **REMOVED** — [Gleaner Close, Plymouth](https://www.so-living.co.uk/find-a-home/our-developments/devon/homes-for-resale-devon/gleaner-close-plymouth/gleaner-close-plymouth/) (SO Living / Plymouth Community Homes (shared-ownership resales))  ⚠ Shared ownership / share price
- `2026-11-11` **NEW £140,000** — [Alexandra Road,Mutley,Plymouth,PL4 7EE](https://www.onthemarket.com/details/20738902/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-11` **REMOVED** — [Plymouth, Devon PL4](https://www.onthemarket.com/details/20673053/) (OnTheMarket (portal))
- `2026-11-11` **REMOVED** — [Hill Park Crescent, Mutley, Plymouth, Devon, PL4](https://www.onthemarket.com/details/20133952/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-10` **REMOVED** — [Embankment Road, Plymouth. Stylish 2-Bedroom Top Floor Flat in Central Plymouth walking distance to City Center.](https://www.onthemarket.com/details/17879716/) (OnTheMarket (portal))
- `2026-11-10` **NEW £150,000** — [St. James Place West, The Hoe, Plymouth](https://www.langtownandcountry.com/property/st-james-place-west-the-hoe-plymouth/) (Lang Town & Country (agent))  ⚠ Over budget — stretch (above £140,000)
- `2026-11-06` **REMOVED** — [Embankment Road, Plymouth. Stylish 2-Bedroom Top Floor Flat in Central Plymouth walking distance to City Center.](https://www.onthemarket.com/details/17879716/) (OnTheMarket (portal))
- `2026-11-06` **NEW £140,000** — [39 Alexandra Road, Mutley, Plymouth, Devon PL4 7EE](https://www.onthemarket.com/details/20707264/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-06` **PRICE £140,000 → £135,000** — [Hotham Place, Plymouth, Devon, PL1](https://www.onthemarket.com/details/20675025/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-06` **REMOVED** — [Torrington Court, North Road East, Plymouth PL4](https://www.onthemarket.com/details/20523746/) (OnTheMarket (portal))
- `2026-11-06` **PRICE £150,000 → £140,000** — [Hotham Place, Plymouth, Devon, PL1](https://www.onthemarket.com/details/20675025/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-05` **REMOVED** — [Arundel Crescent, Plymouth PL1](https://www.onthemarket.com/details/20676273/) (OnTheMarket (portal))
- `2026-11-05` **REMOVED** — [Hands Off Plymouth Apartment, Plymouth](https://www.onthemarket.com/details/20429563/) (OnTheMarket (portal))
- `2026-11-05` **NEW £90,000** — [41 Prince Maurice Road, Plymouth, Devon, PL4 7LJ](https://www.onthemarket.com/details/20695964/) (OnTheMarket (portal))  ⚠ Auction
- `2026-11-05` **NEW £130,000** — [Hands Off Plymouth Apartment, Plymouth](https://www.onthemarket.com/details/20696474/) (OnTheMarket (portal))
- `2026-11-04` **NEW £130,000** — [Arundel Crescent, Plymouth PL1](https://www.onthemarket.com/details/20676273/) (OnTheMarket (portal))
- `2026-11-04` **PRICE £160,000 → £155,000** — [Bayswater Road, Plymouth PL1](https://www.onthemarket.com/details/19649536/) (OnTheMarket (portal))  ⚠ Over budget — stretch (above £140,000)
- `2026-11-02` **NEW £150,000** — [Hotham Place, Plymouth, Devon, PL1](https://www.onthemarket.com/details/20675025/) (OnTheMarket (portal))  ⚠ Auction; Over budget — stretch (above £140,000)
- `2026-11-02` **NEW £130,000** — [Plymouth, Devon PL4](https://www.onthemarket.com/details/20673053/) (OnTheMarket (portal))
- `2026-11-01` **REMOVED** — [The Crescent, Plymouth PL1](https://www.onthemarket.com/details/20072342/) (OnTheMarket (portal))
- `2026-11-01` **REMOVED** — [Providence Street, Plymouth PL4](https://www.onthemarket.com/details/20071962/) (OnTheMarket (portal))  ⚠ Over budget — stretch (above £140,000)
<!--HUNT:END-->
