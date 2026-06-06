+++
title = "8-digit BINs explained: what the IIN expansion means for card BIN lookups (2026)"
date = 2026-06-06
slug = "8-digit-bin-iin-explained"
description = "Card BINs/IINs expanded from 6 to 8 digits. What changed, why the networks did it, and why a 6-digit BIN lookup is now ambiguous — with how to handle it in practice."

[taxonomies]
tags = ["bin", "iin", "binlist", "payments", "credit-card", "visa", "mastercard", "iso"]

[extra]
summary = "The card networks expanded the issuer identifier on a payment card from 6 to 8 digits. For anyone doing BIN/IIN lookups it means a 6-digit prefix is no longer guaranteed to identify a single issuer — you often need 8 digits to disambiguate. Here's the what, the why, and the practical fallout."
+++

**TL;DR —** the **IIN** (issuer identification number) on a payment card grew from **6 digits to 8**. A 6-digit prefix can now map to *several* issuers or products, so BIN lookups that key on 6 digits return ambiguous results. The card number's overall length didn't change — the account portion just got two digits shorter.

This is the structural background behind [binlist.net and iinlist.com](/post/binlist-net-iinlist-com-story/) — if you do anything with card numbers, it's worth understanding.

## What a BIN/IIN actually is

The first digits of a card's PAN (primary account number) identify who issued it. Two terms for the same thing:

- **BIN** — *Bank Identification Number*, the older industry term.
- **IIN** — *Issuer Identification Number*, the term ISO/IEC 7812 uses.

They're used interchangeably. The very first digit is the **MII** (Major Industry Identifier) — `4` = Visa, `5`/`2` = Mastercard, `3` = Amex/Diners/JCB, and so on. The PAN as a whole is structured as:

```
   IIN (issuer)        account identifier        check digit (Luhn)
┌────────────────┐ ┌───────────────────────┐ ┌──┐
4 5 3 9 1 4 8 8   0 3 4 5 6 7 8             9
└─ 8 digits now ─┘
```

## What changed

Historically the IIN was the **first 6 digits**. ISO/IEC 7812 was updated to define it as **8 digits**, and the card networks moved the ecosystem onto 8-digit BINs — **Visa and Mastercard set April 2022** as the point by which issuers, acquirers, and processors had to support the longer identifier.

Crucially, the **PAN length didn't change** (still up to 19 digits, 16 for most cards). The issuer identifier took two more digits, so the **account-identifier portion got two digits shorter**.

## Why they did it

They were running out of room. A 6-digit space is one million possible IINs, and between new fintechs, BIN sponsorship, and ever-finer product segmentation (each card product often wants its own range) the 6-digit pool was being exhausted. Going to 8 digits multiplies the available ranges by a hundred.

## The practical fallout for lookups

This is the part that bites if you maintain or consume a BIN database:

1. **A 6-digit prefix is no longer unique.** Within one old 6-digit block, the two extra digits can now belong to *different* issuers or *different* products. Looking up only 6 digits can return the wrong bank, country, or card type.
2. **You need at least 8 digits to be confident.** If your input only has 6 (common with masked/truncated data), treat the result as a best-effort guess, not ground truth.
3. **Your data source has to be 8-digit aware.** A BIN list that only carries 6-digit granularity silently collapses distinct 8-digit issuers into one row.

```
# Same 6-digit prefix, two different 8-digit issuers (illustrative):
4539 14 ..  -> 45391488 = Issuer A, debit,  country X
4539 14 ..  -> 45391499 = Issuer B, credit, country Y
```

## What to do in practice

- **Capture and key on 8 digits** wherever you legitimately have them.
- **Degrade gracefully** when you only have 6 — return the prefix-level info and flag it as low-confidence rather than asserting a single issuer.
- **Mind PCI scope.** The first 6 *and* the first 8 are both allowed to be stored/displayed under PCI DSS truncation rules (BIN + last 4), but check your acquirer's current guidance before widening what you persist.
- **Don't hardcode "6".** If you have regexes or schema columns that assume a 6-digit BIN, they're now wrong.

## FAQ

### Did my card number get longer?

No. The total PAN length is unchanged. Only the *split* between issuer-identifier and account-identifier moved — issuer up by two digits, account down by two.

### Is it "BIN" or "IIN"?

Same thing. "BIN" is the everyday industry word; "IIN" is the formal ISO term. Expect to see both, often in the same document.

### Can I still do a 6-digit lookup?

You can, and for many ranges it's still fine — but it's no longer *guaranteed* to identify a single issuer. Treat 6-digit results as approximate and prefer 8 when you have them.

### Where do I get 8-digit BIN data?

A maintained BIN/IIN database that carries 8-digit granularity. The free [binlist.net](/post/binlist-net-iinlist-com-story/) and the commercial iinlist.com exist precisely for this.

## Summary

- The issuer identifier on a card went from **6 to 8 digits** (networks: support required by ~April 2022).
- Total card-number length is unchanged; the account portion shrank by two digits.
- **6-digit BIN lookups are now ambiguous** — capture and match on 8 digits where you can, and flag 6-digit results as low-confidence.
