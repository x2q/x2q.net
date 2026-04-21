+++
title = "elpriser.org — danske elpriser time for time"
date = 2026-04-20
slug = "elpriser-org-danske-elpriser-time-for-time"
description = "Danske elpriser time for time i DK1 og DK2 — inkl. nettariffer, elafgift og 25 % moms. Opdateres dagligt fra Energi Data Service."

[taxonomies]
tags = ["energi", "danmark", "nord-pool", "energi-data-service", "tariffer", "elpris", "dk1", "dk2"]

[extra]
summary = "Den reelle elpris i Danmark time for time — spotpris plus nettariffer, transmissionsgebyrer, elafgift og 25 % moms. DK1 og DK2, opdateret dagligt fra Energi Data Service."
faq = [
  { q = "Hvor ofte opdaterer elpriser.org?", a = "Én gang om dagen, efter at Nord Pools day-ahead-auktion offentliggør næste døgn omkring kl. 13 CET. Intradag-justeringer vises ikke; de fleste forbrugere afregnes alligevel efter day-ahead-prisen." },
  { q = "Er prisen med eller uden moms?", a = "Med. Headline-tallet på elpriser.org er all-in pr. kWh: spotpris + tariffer + afgift + 25 % moms. Du kan folde det ud og se opdelingen." },
  { q = "Hvorfor er priserne forskellige i DK1 og DK2?", a = "Danmark har to fysisk adskilte elprisområder, forbundet via Storebælt. Når forbindelsen er fuldt udnyttet, eller når vindproduktionen adskiller sig markant mellem øst og vest, clearer de to områder på forskellige Nord Pool-priser." },
  { q = "Kan jeg se opdelingen af hver komponent?", a = "Ja. Hver time-celle kan foldes ud for at vise spotpris, hver tarif-komponent, elafgift og moms." },
  { q = "Får jeg reelt negative priser, når engrosprisen bliver negativ?", a = "Det afhænger af din kontrakt. Rene spotpris-kontrakter videregiver Nord Pools råpris — tariffer og afgift gælder stadig, så all-in-prisen kan gå svagt negativ eller bare meget lav. Fastpris-kontrakter gør ikke." },
  { q = "Hvorfor kun dansk?", a = "Data, regulering, netselskabs-strukturen og målgruppen er alle danske. En engelsk version ville oversætte kontekst, ikke indhold." },
  { q = "Hvor kommer data fra?", a = "Energi Data Service (Nord Pool-spot) og Energinets tarifdata. Begge er officielle, offentlige datasæt fra den danske TSO." },
]
+++

**TL;DR —** [elpriser.org](https://elpriser.org) viser den **reelle elpris time for time i Danmark** — ikke kun spotprisen. Den samler Nord Pool-spotprisen, din lokale nettarif (`netselskab`), Energinets system- og transmissionstariffer, elafgiften og 25 % moms. Data kommer fra [Energi Data Service](https://www.energidataservice.dk/) og opdateres dagligt, når Nord Pool offentliggør de kommende 24 timer omkring kl. 13. DK1 (Vestdanmark) og DK2 (Østdanmark). Dansksproget, gratis, intet login.

## Hvad koster el faktisk i Danmark?

"Spotprisen", du ser på de fleste energidashboards, er kun én del af regningen. Den pris, du rent faktisk betaler pr. kWh, består af seks elementer:

1. **Spotpris** — sættes time for time på Nord Pool-markedet for det kommende døgn.
2. **Nettarif** — betales til dit lokale netselskab. Varierer efter selskab og tidspunkt (lav-, mellem- og spidslast).
3. **Systemtarif** — betales til Energinet, den danske TSO.
4. **Transmissionstarif** — betales også til Energinet.
5. **Elafgift** — statslig afgift på forbrug.
6. **Moms** — 25 % oven i alt det andet.

De fleste prissider viser kun det første tal. Nogle få viser ét eller to mere. Ingen, jeg kunne finde, viste alle seks time for time, for begge prisområder, med den rigtige nettarif automatisk valgt for brugerens netselskab. Det er præcis det, elpriser.org gør.

## De to prisområder: DK1 og DK2

Danmark er delt i to elprisområder geografisk — Storebælt skiller dem — og de har ofte forskellig pris i samme time:

- **DK1 — Vestdanmark.** Jylland og Fyn. Mere vind-domineret.
- **DK2 — Østdanmark.** Sjælland, Lolland, Falster, Møn og Bornholm. Tættere forbundet med Sverige (SE4) og Tyskland.

Når vinden blæser kraftigt i Jylland, kan DK1 være billig, mens DK2 er dyr. Når en forbindelse er nede, vokser forskellen yderligere. elpriser.org viser begge områder side om side.

## Hvilket netselskab har du?

Du kan ikke selv vælge dit netselskab — det afhænger af din adresse — men den nettarif, de opkræver, er en betydelig del af regningen, og den varierer med **15–25 øre/kWh i spidslast** mellem billigste og dyreste, hvilket svarer til **~500–1.000 kr/år** for en typisk husstand.

Groft rangeret spidslast-tariffer pr. 2025:

| Område | Netselskab | Spidslast-tarif (øre/kWh) |
| --- | --- | --- |
| DK1 | RAH Net | ~33 |
| DK1 | Trefor | ~37 |
| DK1 | N1 | ~46 |
| DK2 | Cerius | ~47 |
| DK2 | Radius | ~65 |

Mindre selskaber (Konstant, Nord Energi, Vores Elnet, El-net Kongerslev og andre) har egne tariffer. På elpriser.org vælger du dit eget, og den all-in time-for-time-pris tilpasser sig.

Du kan ikke skifte netselskab, men du **kan** flytte forbrug — vaskemaskine, opvaskemaskine, EV-ladning, varmepumpe — ned i lavsats-timerne. Time-grafen findes til lige præcis det.

## Historiske yderpunkter

- **Rekord-høj:** 16,69 kr/kWh (spotpris ex. moms) i DK2, kl. 19 den 5. september 2022 under energikrisen.
- **Rekord-lav:** −2,76 kr/kWh i DK1, kl. 14 den 2. juli 2023, hvor vindproduktionen overskød forbruget.

Negative priser er ikke en fejl: når produktionen er høj og forbruget lavt, betaler producenterne forbrugerne for at aftage strømmen. Moderne prisstyrede varmepumper og EV-ladere kan læne sig ind i det.

## Sådan er elpriser.org bygget

- **Statisk HTML**, genskabt én gang om dagen efter Nord Pools day-ahead-auktion omkring kl. 13 CET.
- **Datakilde**: [Energi Data Service](https://www.energidataservice.dk/), Energinets åbne data. Ingen API-nøgler nødvendige.
- **Strukturerede data**: `schema.org/WebApplication` og `FAQPage` udsendes på hver side, så Google kan vise priserne direkte i søgeresultater og AI-oversigter.
- **Hosting**: en lille origin bag Cloudflare. Cachebar hele døgnet; purges ved det daglige rebuild.
- **Sprog**: kun dansk. Domænenavnet burde have været et fingerpeg.

Det hele er et enkeltsporet værktøj: ingen tracking, intet login, ingen nyhedsbrev-popover, ingen "10 måder at spare på strømmen"-lister.

## Ofte stillede spørgsmål

### Hvor ofte opdaterer elpriser.org?

Én gang om dagen, efter at Nord Pools day-ahead-auktion offentliggør næste døgn omkring kl. 13 CET. Intradag-justeringer vises ikke; de fleste forbrugere afregnes alligevel efter day-ahead-prisen.

### Er prisen med eller uden moms?

Med. Headline-tallet på elpriser.org er all-in pr. kWh: spotpris + tariffer + afgift + 25 % moms. Du kan folde det ud og se opdelingen.

### Hvorfor er priserne forskellige i DK1 og DK2?

Danmark har to fysisk adskilte elprisområder, forbundet via Storebælt. Når forbindelsen er fuldt udnyttet, eller når vindproduktionen adskiller sig markant mellem øst og vest, clearer de to områder på forskellige Nord Pool-priser.

### Kan jeg se opdelingen af hver komponent?

Ja. Hver time-celle kan foldes ud for at vise spotpris, hver tarif-komponent, elafgift og moms.

### Får jeg reelt negative priser, når engrosprisen bliver negativ?

Det afhænger af din kontrakt. Rene spotpris-kontrakter videregiver Nord Pools råpris — tariffer og afgift gælder stadig, så all-in-prisen kan gå svagt negativ eller bare meget lav. Fastpris-kontrakter gør ikke.

### Hvorfor kun dansk?

Data, regulering, netselskabs-strukturen og målgruppen er alle danske. En engelsk version ville oversætte kontekst, ikke indhold.

### Hvor kommer data fra?

[Energi Data Service](https://www.energidataservice.dk/dataset/elspotprices) (Nord Pool-spot) og Energinets tarifdata. Begge er officielle, offentlige datasæt fra den danske TSO.

Lille, fokuseret, intet login, ingen tracking. Sådan bør forbruger-energiværktøjer se ud.
