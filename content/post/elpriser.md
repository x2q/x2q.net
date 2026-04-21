+++
title = "elpriser.org — Danish hourly electricity prices"
date = 2026-04-20
slug = "elpriser-org-danish-electricity-prices"
description = "Hourly Danish electricity prices for DK1 + DK2, all-in: spot price, grid tariffs, electricity tax, 25% VAT. Updated daily from Energi Data Service."

[taxonomies]
tags = ["energy", "denmark", "nord-pool", "energi-data-service", "tariffs", "electricity", "dk1", "dk2"]

[extra]
summary = "The real hourly price of electricity in Denmark — spot price plus grid tariffs, transmission fees, electricity tax, and 25% VAT. DK1 and DK2, updated daily from Energi Data Service."
faq = [
  { q = "How often does elpriser.org update?", a = "Once a day, after the Nord Pool day-ahead auction publishes next-day prices around 13:00 CET. Intraday adjustments are not shown; most consumers are billed against the day-ahead price anyway." },
  { q = "Is the price shown with or without VAT?", a = "With. The headline number on elpriser.org is the all-in price per kWh: spot + tariffs + tax + 25% VAT. You can toggle to see the breakdown." },
  { q = "Why are prices in DK1 and DK2 different?", a = "Denmark has two physically separated electricity areas joined by the Great Belt interconnector. When the interconnector is fully used or wind production differs sharply between east and west, the two zones clear at different Nord Pool prices." },
  { q = "Can I see the breakdown of each component?", a = "Yes. Every hourly cell can be expanded to show spot price, each tariff component, elafgift, and VAT." },
  { q = "Do I really pay negative prices when the wholesale price goes negative?", a = "It depends on your contract. Pure spot-price contracts pass the raw Nord Pool price through — tariffs and tax still apply, so the all-in price can go slightly negative or just very low. Fixed-price contracts don't." },
  { q = "Why Danish only?", a = "The data, the regulatory rules, the netselskab structure, and the target audience are all Danish. An English version would be translating context, not content." },
  { q = "Where does the data come from?", a = "Energi Data Service (Nord Pool spot) and Energinet's tariff data. Both are official public data sets from the Danish TSO." },
]
+++

**TL;DR —** [elpriser.org](https://elpriser.org) shows the **real, all-in hourly price of electricity in Denmark** — not just the spot price. It combines the Nord Pool spot price, your local grid tariff (`netselskab`), Energinet's system and transmission tariffs, the state electricity tax (`elafgift`), and 25% VAT. Data comes from [Energi Data Service](https://www.energidataservice.dk/) and updates daily after Nord Pool publishes the next 24 hours around 13:00. DK1 (Vestdanmark) and DK2 (Østdanmark). Danish-language, free, no login.

## What does Danish electricity actually cost?

The "spot price" you see on most energy dashboards is only one component. The price you actually pay per kWh is made up of six parts:

1. **Spot price** — set hourly on the Nord Pool wholesale market for the following day.
2. **Grid tariff (nettarif)** — paid to your local grid operator (`netselskab`). Varies by company and by time-of-day (off-peak, shoulder, peak).
3. **System tariff (systemtarif)** — paid to Energinet, the Danish TSO.
4. **Transmission tariff (transmissionstarif)** — also paid to Energinet.
5. **Electricity tax (elafgift)** — a state tax on consumption.
6. **VAT (moms)** — 25% applied on top of everything else.

Most price sites show the first number. A few show one or two more. None that I could find showed all six, hour by hour, for both price zones, with the correct grid tariff automatically picked for the user's `netselskab`. That's what elpriser.org does.

## The two price zones: DK1 and DK2

Denmark is split into two electricity price zones by geography — the Great Belt separates them — and they often have different prices at the same hour:

- **DK1 — Vestdanmark.** Jylland and Fyn. More wind-dominated.
- **DK2 — Østdanmark.** Sjælland, Lolland, Falster, Møn, Bornholm. More interconnected with Sweden (SE4) and Germany.

When the wind blows hard in Jylland, DK1 can be cheap while DK2 is pricey. When an interconnector is down, the gap widens further. elpriser.org shows both zones side by side.

## Which netselskab are you on?

You cannot choose your `netselskab` — it depends on where you live — but the grid tariff they charge is a significant chunk of your bill, and it varies by **15–25 øre/kWh at peak** between the cheapest and the most expensive, which works out to **~500–1,000 kr/year** for a typical household.

Rough ranking of peak (spidslast) tariffs as of 2025:

| Zone | Netselskab | Peak tariff (øre/kWh) |
| --- | --- | --- |
| DK1 | RAH Net | ~33 |
| DK1 | Trefor | ~37 |
| DK1 | N1 | ~46 |
| DK2 | Cerius | ~47 |
| DK2 | Radius | ~65 |

Smaller operators (Konstant, Nord Energi, Vores Elnet, El-net Kongerslev, and others) each have their own tariffs. elpriser.org lets you pick yours; the all-in hourly price adjusts accordingly.

You can't switch `netselskab`, but you **can** shift consumption — laundry, dishwasher, EV charging, heat-pump heating — into the low-tariff hours. The hourly chart exists for exactly that.

## Historical extremes

- **Record high:** 16.69 kr/kWh (spot price, excl. VAT) in DK2, at 19:00 on 5 September 2022, during the European energy crisis.
- **Record low:** −2.76 kr/kWh in DK1, at 14:00 on 2 July 2023, when wind production overshot demand.

Negative prices are not a bug: when production is high and demand is low, producers pay consumers to absorb the surplus. Modern price-aware heat pumps and EV chargers can lean into this.

## How elpriser.org is built

- **Static HTML**, regenerated once per day after Nord Pool's next-day publication around 13:00 CET.
- **Data source**: [Energi Data Service](https://www.energidataservice.dk/), the open-data service from Energinet. No API keys required.
- **Structured data**: `schema.org/WebApplication` and `FAQPage` are emitted on every page so Google can surface the prices directly in search results and AI overviews.
- **Hosting**: a small origin behind Cloudflare. Cacheable for the full day; purged on the daily rebuild.
- **Language**: Danish only. The domain name should have been a hint.

The whole thing is a single-purpose tool: no tracking, no login, no newsletter popover, no "10 ways to save on your electricity bill" listicles.

## FAQ

### How often does elpriser.org update?

Once a day, after the Nord Pool day-ahead auction publishes next-day prices around 13:00 CET. Intraday adjustments are not shown; most consumers are billed against the day-ahead price anyway.

### Is the price shown with or without VAT?

With. The headline number on elpriser.org is the all-in price per kWh: spot + tariffs + tax + 25% VAT. You can toggle to see the breakdown.

### Why are prices in DK1 and DK2 different?

Denmark has two physically separated electricity areas joined by the Great Belt interconnector. When the interconnector is fully used or wind production differs sharply between east and west, the two zones clear at different Nord Pool prices.

### Can I see the breakdown of each component?

Yes. Every hourly cell can be expanded to show spot price, each tariff component, elafgift, and VAT.

### Do I really pay negative prices when the wholesale price goes negative?

It depends on your contract. Pure spot-price contracts pass the raw Nord Pool price through — tariffs and tax still apply, so the all-in price can go slightly negative or just very low. Fixed-price contracts don't.

### Why Danish only?

The data, the regulatory rules, the `netselskab` structure, and the target audience are all Danish. An English version would be translating context, not content.

### Where does the data come from?

[Energi Data Service](https://www.energidataservice.dk/en/dataset/elspotprices) (Nord Pool spot) and Energinet's tariff data. Both are official public data sets from the Danish TSO.

Small, focused, no login, no tracking. The way consumer energy tools should look.
