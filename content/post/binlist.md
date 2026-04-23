+++
title = "binlist.net — how a Fuerteventura holiday side-project became iinlist.com"
date = 2026-04-22
slug = "binlist-net-iinlist-com-story"
description = "The story of binlist.net, a free BIN/IIN lookup service I started on holiday in 2013, and iinlist.com, the commercial variant I co-founded afterwards. BIN/IIN primer included."

[taxonomies]
tags = ["binlist", "iinlist", "bin", "iin", "payments", "credit-card", "ardef", "visa", "mastercard", "side-project"]

[extra]
summary = "In 2013, sitting on a hotel balcony in Corralejo, I built binlist.net — a free HTTP API for looking up the issuer of a credit card from its first six digits. Thirteen years later it's still free, and its commercial sibling iinlist.com is the one we run the business on."
+++

**TL;DR —** [binlist.net](https://binlist.net) is a **free HTTP API** that takes the first 6–8 digits of a credit card number (the **BIN** or **IIN**) and returns the issuing bank, country, card scheme (Visa, Mastercard, etc.), card type (debit/credit/prepaid), and category. I started it in **August 2013 on a holiday in Fuerteventura**, because I needed a BIN lookup for another project and everything that existed was either paywalled, stale, or behind a sketchy scraper. It was my **first ever Go project**, hit **100,000 queries/day** within weeks, and crossed **1 million queries/day in 2015**. It is still online, still free, still `curl`-friendly. The commercial variant, [iinlist.com](https://iinlist.com), is what I co-founded after binlist.net's success; it's the same idea with **payment-industry-grade accuracy**, **8-digit IIN support** (mandated by ISO/IEC 7812 since 2022), **ARDEF-backed ranges**, and an SLA — built for banks, PSPs, fraud teams, and issuers who need to treat BIN data as production data.

## BIN vs IIN — a one-paragraph primer

The first six (historically) or eight (since 2017, mandatory 2022) digits of a card number are the **Issuer Identification Number** (IIN). The old name, still widely used, is **Bank Identification Number** (BIN). Given a BIN/IIN, you can determine:

- **Scheme / network** — Visa, Mastercard, Amex, Discover, JCB, UnionPay, Diners.
- **Issuer** — the bank or fintech that issued the card.
- **Country** — country of the issuer, which is not necessarily the cardholder's country but is a useful proxy for risk scoring, tax logic (EU/EEA VAT MOSS), and user experience (preferred language, local payment methods).
- **Type** — debit, credit, prepaid, deferred debit, charge.
- **Category / product** — Classic, Gold, Platinum, Business, Corporate, etc. Useful for acceptance cost routing (commercial cards cost more to accept).

All of this is "sensitive" in the sense that issuers don't publish full BIN tables and card schemes consider them proprietary. In practice, BIN ranges leak constantly — every authorisation the scheme routes, every chargeback dispute — and there's a whole cottage industry around keeping reasonably accurate BIN tables.

## Why I built binlist.net on holiday

Summer 2013. **Playitas, southern Fuerteventura** — the resort on the Atlantic side down by Gran Tarajal. Rented apartment, small balcony, Canary wind doing its thing. I had an idea for a side-project that needed to look up cards by BIN and I did not want to pay a payments vendor €200/month for it. The existing free options were:

- **Wikipedia's IIN list** — reasonably accurate for well-known schemes, woefully incomplete for niche issuers, updated by volunteers who don't work in payments.
- **Pasted CSVs on forums** — decent coverage for US issuers, always outdated.
- **Google Fusion Tables** — deprecated by Google that same year.
- **Scrapers of merchant-bank lookup forms** — ToS-violating, brittle.

What I wanted was `curl http://example.com/40012345` returning clean JSON. So I built it.

### The stack (then)

This was **my first ever Go project**. I'd been reading about Go for a while and wanted a small, well-scoped excuse to try it; a single-endpoint JSON API over an in-memory BIN table was perfect. Ruby/Sinatra would have been faster for me to type, but I wanted to learn something, and the memory and latency characteristics of a Go binary turned out to be exactly what a free-tier public API needed.

- **Go** — a single binary, `net/http`, no framework. The whole server was a few hundred lines.
- **In-memory BIN range table**, built at boot from a ~300 MB source file. Lookups were O(log n) over a sorted slice.
- **Deployed on a single Hetzner VM** from day one (I briefly considered Heroku but Heroku's free dyno memory limits didn't fit a fully-loaded BIN table).
- **JSON + XML + CSV** response formats, because 2013.
- **Data seed** from a combination of public Wikipedia scrapes, the old "Mars Base" CSV from 2009, and a set of ranges I'd been accumulating at work.

Total build time on that balcony: a weekend — about half of which was me figuring out `go build`, `GOPATH` (Go modules didn't exist yet), and how interfaces worked. I bought the domain on the Monday, deployed the binary, and tweeted about it.

### Traffic curve

- **Week 1:** a few hundred queries/day, mostly me testing.
- **Month 1:** ~**100,000 queries/day** after developers on Stack Overflow and a couple of e-commerce forums found it.
- **By early 2015:** crossed **1 million queries/day** sustained, with spikes above 2M during flash-sale events on merchants that called it on every checkout page-load.

Scaling to that point cost almost nothing because Go's single-binary footprint meant a ~€5/month VPS handled the whole thing; the bottleneck for a long time was the NIC, not CPU or memory.

### 13 years later

binlist.net still runs. It has migrated infrastructure a few times — Hetzner VM → Hetzner fleet → a small fleet behind Cloudflare — and the data seed has been continuously updated, but the API surface (and most of the original Go code) is the same. Today it serves **tens of millions of lookups per month**, free, no API key required, with a soft rate limit on anonymous callers to keep it honest.

It has **~2,000 Google impressions/month** for queries like "binlist", "bin list bank identification number", "list of bank identification numbers" — still picking up the long tail of developers who type the same question I typed into Google in 2013.

## Why iinlist.com exists

binlist.net's data is good enough for "what country is this card from" decisions — risk scoring, currency presentation, analytics. It is **not** good enough for:

- **Acceptance-cost routing** where you route commercial-card transactions through a different processor.
- **Interchange++ modelling** where the margin difference between Classic and Platinum Mastercard is real money.
- **Scheme compliance** — the ISO/IEC 7812 migration from 6-digit BINs to 8-digit IINs, mandated 2022, broke a lot of "I'll just use the first six digits" logic.
- **Co-badged cards** (e.g. Dankort + Visa Debit) where two networks both claim the card and the routing decision is business-critical.
- **ARDEF-grade accuracy** — Visa's Account Range Definition File is the source of truth; you really do want data derived from ARDEF for anything production-grade.

iinlist.com solves these, commercially. I co-founded it with a small team of people who know payments data professionally. It's the product binlist.net is the free-tier advertisement for. Some of our customers are names you'd recognise; most are not. All of them eventually reach the same conclusion: **BIN data that's "mostly right" costs more in wrong decisions than accurate data costs in licence fees**.

### What iinlist.com is, specifically

- **8-digit IIN support** across all schemes.
- **Daily updates**, derived from ARDEF + scheme feeds + issuer announcements + internal verification.
- **Richer enrichment**: card type, product category, issuing country, issuer branding, regulatory classifications (commercial vs consumer, prepaid flag, etc.).
- **SLA and support**. You can file a ticket and it will actually reach a human.
- **On-prem / self-hosted option** for customers whose compliance doesn't allow "BIN lookup as a third-party API call in the authorisation path".
- **Pricing** that makes sense for both a scrappy fintech (monthly plan) and an established acquirer (annual, unlimited).

## Can I just use binlist.net commercially?

You can use binlist.net however you want; there's no gate. But:

- There's no SLA, no uptime guarantee, and no contract. It's a side project that happens to have stayed up for 13 years.
- Rate limits on anonymous traffic will kick in at production volume. Buy a licence from iinlist.com and the problem is solved.
- If your regulator asks where your BIN data comes from, "a free API my developer found" is not the answer you want to give.

For anything hobby, demo, or prototype: binlist.net is perfect. For anything where wrong BIN data becomes someone's KPI: iinlist.com.

## Using binlist.net today

```
$ curl -sH "Accept-Version: 3" https://lookup.binlist.net/45717360
{
  "number": { "length": 16, "luhn": true },
  "scheme": "visa",
  "type": "debit",
  "brand": "Visa/Dankort",
  "country": {
    "numeric": "208",
    "alpha2": "DK",
    "name": "Denmark",
    "emoji": "🇩🇰",
    "currency": "DKK",
    "latitude": 56,
    "longitude": 10
  },
  "bank": {
    "name": "Jyske Bank A/S",
    "url": "www.jyskebank.dk",
    "phone": "+4589893300",
    "city": "Silkeborg"
  }
}
```

- **`Accept-Version: 3`** — pins to API v3.
- **Anonymous rate limit** — documented on the site, plenty for casual use.
- **Zero warranties** — if the response is wrong, submit a correction on the GitHub repo. For commercial guarantees, see iinlist.com.

## FAQ

### Is BIN / IIN data regulated?

BIN ranges themselves are not personal data under GDPR — a BIN identifies an issuer, not a person. Combining a BIN with a full card number is a different story and falls under PCI-DSS.

### What changed with the 8-digit IIN migration?

ISO/IEC 7812 formalised 8-digit IINs in 2017 with a hard migration deadline in April 2022 for the major networks. If your code still treats only the first six digits as the issuer identifier, you're silently misrouting a growing share of traffic — modern Visa and Mastercard issuer ranges are defined at 8 digits.

### Why not just look it up client-side?

You can, with a static list in the browser. But you'll accept a trade-off: freshness (the static list will be out of date within weeks) or bundle size (the current BIN table is megabytes uncompressed). A server-side API is the conventional answer.

### Does binlist.net log the BINs I query?

Aggregate analytics only — enough to detect abuse and rate-limit. Individual queries are not associated with a user. iinlist.com has a stricter no-logging posture for customers where that matters.

### Is the source code open?

The API surface of binlist.net is on GitHub, with contribution guidelines for data corrections. The data ingestion pipeline is not open-source; it relies on scheme feeds that require licences.

### Are binlist.net and iinlist.com the same company?

Separate projects, overlapping origins, same operator on my side. binlist.net is a personal free service; iinlist.com is a commercial company with co-founders and employees. The two are operationally independent but share institutional knowledge about BIN data that is not easy to accumulate from scratch.

## Thirteen years in

The thing I find most interesting about binlist.net is not the traffic — it's the **kind of questions** developers are still typing into Google in 2026: "what is a bin list", "bin number example", "list of issuer identification numbers". These are the exact queries I was typing in 2013 on that balcony in Playitas. Payments as an industry keeps adding layers, but the foundational questions don't change.

If you're sitting on a beach with a laptop and you have an itch for a side-project that scratches your own back, go build it — and while you're at it, try the language you've been meaning to learn. Sometimes it turns out a lot of people have the same itch, and thirteen years later you have a useful thing to point them at and a working knowledge of Go.
