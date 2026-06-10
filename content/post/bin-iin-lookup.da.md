+++
title = "BIN/IIN-opslag: kort-præfiksernes intervaller og hvordan du slår et op (2026)"
date = 2026-06-10
slug = "bin-iin-opslag"
description = "Hvad et kort-BIN/IIN er, den fulde tabel over IIN-præfiksintervaller pr. netværk (Visa, Mastercard, Amex, Discover, JCB, UnionPay m.fl.), og hvordan du slår et BIN op — i hånden, på en side eller programmatisk med curl."

[taxonomies]
tags = ["bin", "iin", "binlist", "opslag", "betalinger", "kreditkort", "visa", "mastercard", "iso"]

[extra]
summary = "En praktisk reference til BIN/IIN-opslag: hvad issuer identification number er, tabellen over hvilke præfiksintervaller der hører til hvilket kortnetværk, og de tre måder at slå et BIN op på — læs det selv ud af intervallerne, brug en opslagsside/API som binlist.net, eller slå det op programmatisk. Inkluderer 6-vs-8-ciffer-forbeholdet og hvad du kan og ikke kan se ud fra et præfiks alene."
faq = [
  { q = "Hvad er et BIN / IIN?", a = "BIN (Bank Identification Number), formelt IIN (Issuer Identification Number) i ISO/IEC 7812, er de første cifre i et korts nummer (PAN), der identificerer den udstedende institution og kortnetværket. Det var 6 cifre og er nu 8 for de fleste netværk. 'BIN' er det daglige branchebegreb; 'IIN' er ISO-begrebet — det samme." },
  { q = "Kan jeg selv se banken ud fra et BIN?", a = "Kun netværket (Visa, Mastercard osv.) — det kan du læse ud af præfiksintervallerne nedenfor. Den specifikke udstedende bank, land, korttype (debit/kredit) og produkt kræver en BIN-database; der er ingen formel, der oversætter et præfiks til et banknavn. Brug en opslagsside/API eller en licenseret BIN-datafil til det." },
  { q = "Hvordan slår jeg et BIN op online?", a = "Indsæt de første 6-8 cifre i en BIN-opslagstjeneste. binlist.net tilbyder et gratis JSON-API (med rate limit) på https://lookup.binlist.net/<bin>; iinlist.com er en kommerciel database med 8-ciffers granularitet. Indsend aldrig et fuldt kortnummer til en tilfældig side — BIN'et (de første 6-8 cifre) er alt, et opslag behøver." },
  { q = "Er et 6-ciffers BIN stadig nok?", a = "Ikke altid. Netværkene udvidede IIN'et fra 6 til 8 cifre, så et 6-ciffers præfiks kan nu pege på flere udstedere eller produkter. Indfang og match på 8 cifre, hvor du har dem, og behandl 6-ciffers resultater som omtrentlige. Se det dedikerede indlæg om 8-ciffer-udvidelsen." }
]
+++

**Kort fortalt —** Et korts første cifre — **BIN** (Bank Identification Number) / **IIN** (Issuer Identification Number) — identificerer **netværket** og **udstederen**. Du kan læse *netværket* direkte ud af præfiksintervallerne (tabel nedenfor). *Udsteder/bank/land* kræver en **BIN-database** — der er ingen formel for det. Denne side giver dig **IIN-intervaltabellen**, **6-vs-8-ciffer-forbeholdet** og de **tre måder at slå et BIN op på** (i hånden, via side/API, programmatisk).

> Baggrundslæsning på bloggen: [hvorfor et 6-ciffers BIN nu er flertydigt](/post/8-digit-bin-iin-explained/) og [historien bag binlist.net og iinlist.com](/da/post/binlist-net-iinlist-com-historien/).

## Hvad et BIN/IIN er

Kortnummeret (PAN, primary account number) er struktureret: de **første cifre er IIN'et**, der identificerer den udstedende institution og netværket; resten er det individuelle kontonummer, med et afsluttende **Luhn-kontrolciffer**. "BIN" er det daglige branchebegreb; "IIN" er det formelle begreb i **ISO/IEC 7812**. IIN'et var **6 cifre** i årtier og er **udvidet til 8** for de fleste netværk — se [8-ciffer-indlægget](/post/8-digit-bin-iin-explained/).

## IIN-præfiksintervaller pr. netværk

Hvad du *kan* bestemme ud fra præfikset alene — hvilket netværk der udstedte kortet:

| Netværk | IIN-præfiksinterval(ler) | PAN-længde |
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

Bemærk: intervaller kan overlappe i kanterne (f.eks. nogle `62` UnionPay vs. `622126`–`622925` Discover-cobadging), og `50`/`56`–`69` for Maestro er bredt og kolliderer med andre — hvilket er præcis derfor, opløsning på udstederniveau kræver en database, ikke en præfiksregel.

## Hvad du *ikke* kan se ud fra præfikset

Der er **ingen formel**, der oversætter et præfiks til et banknavn, land eller debit/kredit-flag. Den kobling ligger i en vedligeholdt **BIN-database** bygget af netværksbulletiner og observerede kort. Så:

- **Netværk** → kan læses ud af tabellen ovenfor. ✅
- **Udstederbank, land, korttype, produkt, prepaid/debit/kredit** → kun databaseopslag. ❌ i hånden.

## Tre måder at slå et BIN op på

### 1. I hånden (kun netværk)

Tag de første cifre og match dem mod tabellen ovenfor. Godt nok, når alt du har brug for er "er det Visa eller Mastercard?".

### 2. På en opslagsside / gratis API

For detaljer på udstederniveau, brug en BIN-opslagstjeneste. Det velkendte gratis valg er **binlist.net**, som blotlægger et JSON-API:

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

Det er **rate-limited** (en håndfuld forespørgsler i timen) og bedst til lejlighedsvise opslag. Til volumen, 8-ciffers granularitet og pålidelighed vil du have en licenseret database — **iinlist.com** er det kommercielle valg bygget til netop dette. (Baggrund: [hvordan begge opstod](/da/post/binlist-net-iinlist-com-historien/).)

**Send kun BIN'et — de første 6-8 cifre — aldrig et fuldt kortnummer** til et tredjepartsopslag. Præfikset er alt, et opslag behøver, og fulde PAN'er er følsomme (PCI) data.

### 3. Programmatisk

Til mere end det lejlighedsvise tjek: validér og normalisér først, slå så op:

```sh
# normalisér: fjern mellemrum, tag de første 8 cifre som BIN
bin=$(echo "4571 7360 1234 5678" | tr -dc '0-9' | cut -c1-8)
curl -s "https://lookup.binlist.net/$bin"
```

Et hurtigt **Luhn**-gyldighedstjek, før du gemmer eller slår noget op (POSIX-shell):

```sh
luhn() {  # returnerer 0 hvis nummeret består Luhn-tjekket
  echo "$1" | tr -dc '0-9' | rev | awk '{
    s=0; for(i=1;i<=length;i++){d=substr($0,i,1);
      if(i%2==0){d*=2; if(d>9)d-=9}; s+=d}
    exit (s%10!=0)
  }'
}
luhn "4571736012345678" && echo gyldig || echo ugyldig
```

Til BIN-matching i produktion: indlæs en licenseret BIN-fil i din egen tabel, og key på **8 cifre** med fallback til 6 med et lav-tillids-flag.

## Opsummering

- **BIN/IIN'et** er kortnummerets første cifre — **netværk + udsteder**; 6 cifre historisk, **8 nu**.
- Du kan læse **netværket** ud af [præfiksintervallerne](#iin-praefiksintervaller-pr-netvaerk); **udsteder/bank/land kræver en database**.
- Slå op: **i hånden** (netværk), en **side/API** som binlist.net (gratis, rate-limited) eller **iinlist.com** (kommerciel, 8-ciffer), eller **programmatisk**.
- Send **kun de første 6-8 cifre**, aldrig et fuldt PAN, til noget tredjepartsopslag.
- Foretræk **8-ciffers** matching — se [hvorfor 6 cifre nu er flertydigt](/post/8-digit-bin-iin-explained/).
