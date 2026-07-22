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
_No runs yet — trigger the workflow from the Actions tab._
<!--HUNT:END-->
