+++
title = "binlist.net — hvordan et ferie-sideprojekt fra Fuerteventura blev til iinlist.com"
date = 2026-04-22
slug = "binlist-net-iinlist-com-historien"
description = "Historien om binlist.net, en gratis BIN/IIN-opslagstjeneste jeg startede på ferie i 2013, og iinlist.com — den kommercielle variant jeg medstiftede bagefter. BIN/IIN-grundkursus inkluderet."

[taxonomies]
tags = ["binlist", "iinlist", "bin", "iin", "betalinger", "kreditkort", "ardef", "visa", "mastercard", "sideprojekt"]

[extra]
summary = "I 2013, på en balkon i Playitas på Fuerteventura, byggede jeg binlist.net som mit første Go-projekt nogensinde — en gratis HTTP-API til at slå kortudstederen op ud fra de første seks cifre. Den ramte 1 million queries/dag i 2015. Tretten år senere er den stadig gratis, og dens kommercielle søster iinlist.com er den, vi driver forretning på."
+++

**TL;DR —** [binlist.net](https://binlist.net) er en **gratis HTTP-API**, der tager de første 6–8 cifre af et kortnummer (**BIN** eller **IIN**) og returnerer udsteder-bank, land, kort-netværk (Visa, Mastercard osv.), korttype (debit/credit/prepaid) og kategori. Jeg startede den **i august 2013 på ferie på Fuerteventura**, fordi jeg skulle bruge BIN-opslag til et andet projekt, og alt der fandtes var enten betalingspligtigt, forældet eller bag en tvivlsom scraper. Det var mit **første Go-projekt nogensinde**, ramte **100.000 queries/dag** inden for uger og krydsede **1 million queries/dag i 2015**. Den er stadig online, stadig gratis, stadig `curl`-venlig. Den kommercielle variant, [iinlist.com](https://iinlist.com), er den, jeg medstiftede efter binlist.nets succes; det er samme idé med **betalingsindustri-præcision**, **8-cifret IIN-understøttelse** (påkrævet af ISO/IEC 7812 siden 2022), **ARDEF-baserede ranges** og en SLA — bygget til banker, PSP'er, fraud-teams og issuere, der har brug for at behandle BIN-data som produktions-data.

## BIN vs IIN — et grundkursus på én paragraf

De første seks (historisk) eller otte (siden 2017, obligatorisk fra 2022) cifre af et kortnummer er **Issuer Identification Number** (IIN). Det gamle navn, stadig vidt brugt, er **Bank Identification Number** (BIN). Givet en BIN/IIN kan du afgøre:

- **Netværk** — Visa, Mastercard, Amex, Discover, JCB, UnionPay, Diners.
- **Udsteder** — banken eller fintech'en, der udstedte kortet.
- **Land** — udstederens land, ikke nødvendigvis kortholderens, men en nyttig proxy for risiko-scoring, skatte-logik (EU/EØS moms-OSS) og brugeroplevelse (foretrukket sprog, lokale betalingsmetoder).
- **Type** — debit, credit, prepaid, deferred debit, charge.
- **Kategori / produkt** — Classic, Gold, Platinum, Business, Corporate osv. Nyttigt til acceptance-cost-routing (erhvervskort koster mere at modtage).

Alt dette er "følsomt" i den forstand, at udstedere ikke offentliggør fulde BIN-tabeller, og kort-netværkene betragter dem som proprietære. I praksis lækker BIN-ranges konstant — hver autorisation, netværket router, hver chargeback-dispute — og der er en hel bibranche omkring at holde rimeligt præcise BIN-tabeller.

## Hvorfor jeg byggede binlist.net på ferie

Sommer 2013. **Playitas, sydlige Fuerteventura** — resortet på Atlanterhavs-siden nede ved Gran Tarajal. Lejet lejlighed, lille balkon, kanariefuglevinden gør sit. Jeg havde en idé til et sideprojekt, der skulle slå kort op via BIN, og jeg ville ikke betale en betalings-leverandør €200/md for det. De eksisterende gratis muligheder var:

- **Wikipedias IIN-liste** — rimelig præcis for velkendte netværk, elendig dækning for niche-udstedere, opdateret af frivillige, der ikke arbejder i payments.
- **Indsatte CSV'er på fora** — anstændig dækning for US-udstedere, altid forældet.
- **Google Fusion Tables** — udfaset af Google samme år.
- **Scrapere af merchant-bankers opslagsformer** — ToS-overtrædende, skrøbelige.

Det jeg ville have, var `curl http://example.com/40012345` der returnerer ren JSON. Så jeg byggede det.

### Stakken (dengang)

Det var **mit første Go-projekt nogensinde**. Jeg havde læst om Go et stykke tid og ville have en lille, velafgrænset undskyldning for at prøve det; en single-endpoint JSON-API over en in-memory BIN-tabel var perfekt. Ruby/Sinatra ville have været hurtigere at taste for mig, men jeg ville lære noget, og memory- og latency-karakteristikken af en Go-binary viste sig at være præcis det, en gratis-tier offentlig API havde brug for.

- **Go** — en enkelt binary, `net/http`, ingen framework. Hele serveren fyldte nogle hundrede linjer.
- **In-memory BIN-range-tabel**, bygget ved boot fra en ~300 MB kilde-fil. Opslag var O(log n) over et sorteret slice.
- **Deployet på én Hetzner-VM** fra dag ét (jeg overvejede kortvarigt Heroku, men Heroku's gratis dyno-memory-grænser kunne ikke rumme en fuldt indlæst BIN-tabel).
- **JSON + XML + CSV**-svarformater, fordi 2013.
- **Dataseed** fra en kombination af offentlige Wikipedia-scrapes, den gamle "Mars Base"-CSV fra 2009 og et sæt ranges, jeg havde akkumuleret på arbejde.

Samlet build-tid på den balkon: en weekend — hvoraf cirka halvdelen var mig, der fandt ud af `go build`, `GOPATH` (Go-moduler fandtes ikke endnu) og hvordan interfaces virkede. Jeg købte domænet mandag morgen, deployede binaryen og tweetede om det.

### Trafik-kurven

- **Uge 1:** et par hundrede queries/dag, mest mig, der testede.
- **Måned 1:** ~**100.000 queries/dag**, efter udviklere på Stack Overflow og et par e-handels-fora fandt den.
- **I begyndelsen af 2015:** krydsede **1 million queries/dag** vedholdende, med spikes over 2M under flash-sale-events hos merchants, der kaldte den på hver checkout-page-load.

At skalere til det punkt kostede næsten ingenting, fordi Go's single-binary-fodaftryk betød, at en ~€5/md VPS klarede det hele; flaskehalsen var længe NIC'en, ikke CPU eller memory.

### 13 år senere

binlist.net kører stadig. Den er blevet flyttet infrastruktur nogle gange — Hetzner-VM → Hetzner-flåde → en lille flåde bag Cloudflare — og dataseed'et er blevet opdateret løbende, men API-overfladen (og det meste af den oprindelige Go-kode) er den samme. I dag serverer den **titusinder af millioner opslag pr. måned**, gratis, uden API-nøgle, med en soft-rate-limit på anonyme kaldere for at holde den ærlig.

Den har **~2.000 Google-visninger/md** for queries som "binlist", "bin list bank identification number", "list of bank identification numbers" — den samler stadig den lange hale af udviklere op, der skriver samme spørgsmål, jeg skrev i Google i 2013.

## Hvorfor iinlist.com findes

binlist.nets data er god nok til "hvilket land er dette kort fra"-beslutninger — risiko-scoring, valuta-præsentation, analytics. Den er **ikke** god nok til:

- **Acceptance-cost-routing**, hvor du router erhvervskorts-transaktioner gennem en anden processor.
- **Interchange++-modellering**, hvor margin-forskellen mellem Classic og Platinum Mastercard er rigtige penge.
- **Compliance** — ISO/IEC 7812-migrationen fra 6-cifrede BIN'er til 8-cifrede IIN'er, obligatorisk fra 2022, brød en masse "jeg bruger bare de første seks cifre"-logik.
- **Co-badged kort** (f.eks. Dankort + Visa Debit), hvor to netværk begge hævder kortet, og routing-beslutningen er forretningskritisk.
- **ARDEF-præcision** — Visas Account Range Definition File er sandhedskilden; du vil virkelig have data afledt af ARDEF til noget, der kører i produktion.

iinlist.com løser det, kommercielt. Jeg medstiftede den med et lille team af folk, der kender payments-data professionelt. Det er produktet, som binlist.net er gratis-tier-annoncen for. Nogle af vores kunder er navne, du ville genkende; de fleste er ikke. De kommer alle til samme konklusion: **BIN-data der er "stort set rigtige" koster mere i forkerte beslutninger, end præcise data koster i licens-gebyr**.

### Hvad iinlist.com specifikt er

- **8-cifret IIN-understøttelse** på tværs af alle netværk.
- **Daglige opdateringer** afledt af ARDEF + netværks-feeds + udsteder-annonceringer + intern verificering.
- **Rigere enrichment**: korttype, produkt-kategori, udsteder-land, udsteder-branding, regulatoriske klassifikationer (commercial vs consumer, prepaid-flag osv.).
- **SLA og support**. Du kan oprette en ticket, og den når faktisk et menneske.
- **On-prem / self-hosted**-mulighed for kunder, hvis compliance ikke tillader "BIN-opslag som tredjeparts-API-kald i autorisations-stien".
- **Prissætning** der giver mening for både en startende fintech (månedlig plan) og en etableret acquirer (årlig, ubegrænset).

## Kan jeg bare bruge binlist.net kommercielt?

Du kan bruge binlist.net, som du vil; der er ingen gate. Men:

- Ingen SLA, ingen oppetidsgaranti, ingen kontrakt. Det er et sideprojekt, der er blevet oppe i 13 år.
- Rate-limits på anonym trafik træder i kraft ved produktions-volumen. Køb en licens fra iinlist.com, og problemet er løst.
- Hvis din regulator spørger, hvor dine BIN-data kommer fra, er "en gratis API, min udvikler fandt" ikke det svar, du vil give.

Til hobby, demo eller prototype: binlist.net er perfekt. Til alt, hvor forkerte BIN-data bliver en KPI: iinlist.com.

## Brug af binlist.net i dag

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

- **`Accept-Version: 3`** — pin'er til API v3.
- **Anonym rate-limit** — dokumenteret på siden, rigeligt til almindelig brug.
- **Ingen garantier** — hvis svaret er forkert, indsend en rettelse på GitHub-repoet. Til kommercielle garantier: se iinlist.com.

## Ofte stillede spørgsmål

### Er BIN-/IIN-data reguleret?

BIN-ranges i sig selv er ikke persondata under GDPR — en BIN identificerer en udsteder, ikke en person. Kombination af en BIN med et fuldt kortnummer er en anden historie og falder under PCI-DSS.

### Hvad ændrede sig med 8-cifret IIN-migrationen?

ISO/IEC 7812 formaliserede 8-cifrede IIN'er i 2017 med en hård migrations-deadline i april 2022 for de store netværk. Hvis din kode stadig behandler kun de første seks cifre som udsteder-identifikatoren, fejlrouter du lydløst en voksende del af din trafik — moderne Visa- og Mastercard-udsteder-ranges er defineret ved 8 cifre.

### Hvorfor ikke bare slå op på klient-siden?

Det kan du, med en statisk liste i browseren. Men du accepterer et trade-off: friskhed (den statiske liste er forældet inden for uger) eller bundle-størrelse (den nuværende BIN-tabel er megabytes ukomprimeret). En server-side-API er det konventionelle svar.

### Logger binlist.net de BIN'er, jeg slår op?

Kun aggregeret analytics — nok til at opdage misbrug og rate-limite. Enkelte opslag er ikke knyttet til en bruger. iinlist.com har en strammere no-logging-holdning til kunder, hvor det betyder noget.

### Er kildekoden open source?

API-overfladen af binlist.net er på GitHub med retningslinjer for data-rettelser. Data-ingestion-pipelinen er ikke open source; den afhænger af netværks-feeds, der kræver licenser.

### Er binlist.net og iinlist.com samme firma?

Adskilte projekter, overlappende oprindelse, samme operatør på min side. binlist.net er en personlig gratis-tjeneste; iinlist.com er et kommercielt selskab med medstiftere og medarbejdere. De to er driftsmæssigt uafhængige, men deler institutionel viden om BIN-data, som ikke er nem at akkumulere fra bunden.

## Tretten år inde

Det, jeg finder mest interessant ved binlist.net, er ikke trafikken — det er **den slags spørgsmål**, udviklere stadig skriver ind i Google i 2026: "what is a bin list", "bin number example", "list of issuer identification numbers". Det er nøjagtig de queries, jeg skrev i 2013 på balkonen i Playitas. Payments som industri fortsætter med at tilføje lag, men de grundlæggende spørgsmål ændrer sig ikke.

Hvis du sidder på en strand med en laptop, og du har en kløe til et sideprojekt, der klør din egen ryg: byg det — og prøv imens det sprog, du har haft lyst til at lære. Nogle gange viser det sig, at mange har samme kløe, og tretten år senere har du en nyttig ting at pege dem på og et arbejdende kendskab til Go.
