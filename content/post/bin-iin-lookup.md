+++
title = "BIN/IIN lookup: the card prefix ranges and how to look one up (2026)"
date = 2026-06-10
slug = "bin-iin-lookup"
description = "What a card BIN/IIN is, the full table of IIN prefix ranges by network (Visa, Mastercard, Amex, Discover, JCB, UnionPay and more), and how to look up a BIN — by hand, on a site, or programmatically with curl."

[taxonomies]
tags = ["bin", "iin", "binlist", "lookup", "payments", "credit-card", "visa", "mastercard", "iso"]

[extra]
summary = "A practical reference for BIN/IIN lookups: what the issuer identification number is, the table of which prefix ranges belong to which card network, and the three ways to look a BIN up — read it off the ranges yourself, use a lookup site/API like binlist.net, or query it programmatically. Includes the 6-vs-8-digit caveat and what you can and can't tell from a prefix alone."
faq = [
  { q = "What is a BIN / IIN?", a = "The BIN (Bank Identification Number), formally the IIN (Issuer Identification Number) in ISO/IEC 7812, is the leading digits of a card's number (PAN) that identify the issuing institution and the card network. It was 6 digits and is now 8 for most networks. 'BIN' is the everyday industry term; 'IIN' is the ISO term — same thing." },
  { q = "Can I tell the bank from a BIN myself?", a = "Only the network (Visa, Mastercard, etc.) — that you can read off the prefix ranges below. The specific issuing bank, country, card type (debit/credit) and product require a BIN database; there's no formula that maps a prefix to a bank name. Use a lookup site/API or a licensed BIN data file for that." },
  { q = "How do I look up a BIN online?", a = "Paste the first 6-8 digits into a BIN lookup service. binlist.net offers a free JSON API (rate-limited) at https://lookup.binlist.net/<bin>; iinlist.com is a commercial database with 8-digit granularity. Never submit a full card number to a random site — the BIN (first 6-8 digits) is all a lookup needs." },
  { q = "Is a 6-digit BIN still enough?", a = "Not always. The networks expanded the IIN from 6 to 8 digits, so a 6-digit prefix can now map to several issuers or products. Capture and match on 8 digits where you have them, and treat 6-digit results as approximate. See the dedicated post on the 8-digit expansion." }
]
+++

**TL;DR —** A card's first digits — the **BIN** (Bank Identification Number) / **IIN** (Issuer Identification Number) — identify the **network** and the **issuer**. You can read the *network* straight off the prefix ranges (table below). The *issuer/bank/country* needs a **BIN database** — there's no formula for it. This page gives you the **IIN range table**, the **6-vs-8-digit caveat**, and the **three ways to look a BIN up** (by hand, by site/API, programmatically).

> Background reading on this blog: [why a 6-digit BIN is now ambiguous](/post/8-digit-bin-iin-explained/) and [the story behind binlist.net and iinlist.com](/post/binlist-net-iinlist-com-story/).

## What a BIN/IIN is

The card number (PAN, primary account number) is structured: the **leading digits are the IIN**, identifying the issuing institution and network; the rest is the individual account number, with a final **Luhn check digit**. "BIN" is the everyday industry word; "IIN" is the formal term in **ISO/IEC 7812**. The IIN was **6 digits** for decades and has been **expanded to 8** for most networks — see [the 8-digit post](/post/8-digit-bin-iin-explained/).

## IIN prefix ranges by network

What you *can* determine from the prefix alone — which network issued the card:

| Network | IIN prefix range(s) | PAN length |
|---|---|---|
| **Visa** | `4` | 13, 16, 19 |
| **Mastercard** | `51`–`55`, `2221`–`2720` | 16 |
| **American Express** | `34`, `37` | 15 |
| **Discover** | `6011`, `644`–`649`, `65`, `622126`–`622925` | 16–19 |
| **Diners Club Intl** | `36`, `300`–`305`, `3095`, `38`–`39` | 14–19 |
| **JCB** | `3528`–`3589` | 16–19 |
| **UnionPay** | `62`, `81` | 16–19 |
| **Maestro** | `50`, `56`–`69`, `6304`, `6759`, `676770`, `676774` | 12–19 |
| **RuPay** | `60`, `6521`, `6522` | 16 |
| **Mir** | `2200`–`2204` | 16 |
| **Troy** | `9792` | 16 |

Notes: ranges can overlap at the edges (e.g. some `62` UnionPay vs `622126`–`622925` Discover co-badging), and `50`/`56`–`69` for Maestro is broad and collides with others — which is exactly why issuer-level resolution needs a database, not a prefix rule.

## What you *cannot* tell from the prefix

There is **no formula** that turns a prefix into a bank name, country, or debit/credit flag. That mapping lives in a maintained **BIN database** built from network bulletins and observed cards. So:

- **Network** → readable from the table above. ✅
- **Issuer bank, country, card type, product, prepaid/debit/credit** → database lookup only. ❌ by hand.

## Three ways to look up a BIN

### 1. By hand (network only)

Take the first digits and match them against the table above. Good enough when all you need is "is this Visa or Mastercard?".

### 2. On a lookup site / free API

For issuer-level detail, use a BIN lookup service. The well-known free option is **binlist.net**, which exposes a JSON API:

```sh
curl https://lookup.binlist.net/45717360
```

```json
{
  "scheme": "visa",
  "type": "debit",
  "brand": "Visa Classic",
  "bank": { "name": "Example Bank", "country": "..." },
  "country": { "name": "United Kingdom", "alpha2": "GB" }
}
```

It's **rate-limited** (a handful of requests per hour) and best for occasional lookups. For volume, 8-digit granularity, and reliability you want a licensed database — **iinlist.com** is the commercial option built for exactly this. (Background: [how both came to exist](/post/binlist-net-iinlist-com-story/).)

**Only ever send the BIN — the first 6-8 digits — never a full card number** to a third-party lookup. The prefix is all a lookup needs, and full PANs are sensitive (PCI) data.

### 3. Programmatically

For more than the occasional check, validate and normalise first, then look up:

```sh
# normalise: strip spaces, take first 8 digits as the BIN
bin=$(echo "4571 7360 1234 5678" | tr -dc '0-9' | cut -c1-8)
curl -s "https://lookup.binlist.net/$bin"
```

A quick **Luhn** validity check before you store or look anything up (POSIX shell):

```sh
luhn() {  # returns 0 if the number passes the Luhn check
  echo "$1" | tr -dc '0-9' | rev | awk '{
    s=0; for(i=1;i<=length;i++){d=substr($0,i,1);
      if(i%2==0){d*=2; if(d>9)d-=9}; s+=d}
    exit (s%10!=0)
  }'
}
luhn "4571736012345678" && echo valid || echo invalid
```

For production BIN matching, load a licensed BIN file into your own table and key on **8 digits**, falling back to 6 with a low-confidence flag.

## Summary

- The **BIN/IIN** is the card number's leading digits — **network + issuer**; 6 digits historically, **8 now**.
- You can read the **network** off the [prefix ranges](#iin-prefix-ranges-by-network); **issuer/bank/country needs a database**.
- Look up: **by hand** (network), a **site/API** like binlist.net (free, rate-limited) or **iinlist.com** (commercial, 8-digit), or **programmatically**.
- Send **only the first 6-8 digits**, never a full PAN, to any third-party lookup.
- Prefer **8-digit** matching — see [why 6 digits is now ambiguous](/post/8-digit-bin-iin-explained/).
