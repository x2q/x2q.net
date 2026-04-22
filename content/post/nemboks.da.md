+++
title = "nemboks.dk — få din digitale post (mit.dk, e-Boks) sendt direkte til din e-mail"
date = 2026-04-22
slug = "nemboks-dk-videresend-digital-post"
description = "Nemboks videresender digital post fra mit.dk og e-Boks direkte til den indbakke, du allerede læser. Uden MitID-login for hvert brev og uden en app."

[taxonomies]
tags = ["nemboks", "digital-post", "mit-dk", "e-boks", "danmark", "rails", "auth0", "stripe", "saas"]

[extra]
summary = "Digital post fra det offentlige lander i mit.dk og e-Boks. Nemboks sender den videre til den indbakke, du faktisk læser — uden MitID, uden app, uden bøvl."
+++

**TL;DR —** [nemboks.dk](https://nemboks.dk) **videresender digital post** (fra [mit.dk](https://mit.dk) og [e-Boks](https://www.e-boks.com/)) direkte til din e-mail. Problemet, det løser: digital post er i teorien "push", men i praksis "pull" — du skal stadig logge ind med MitID, åbne en app og klikke rundt for at læse et brev fra SKAT eller kommunen. Nemboks laver det til en e-mail, der lander i den indbakke, du i forvejen bor i — med PDF'en vedhæftet. Bygget til danske SMV'er, hvor samme `virksomhed` modtager post for flere selskaber eller medarbejdere, og hvor revisorer, bogholdere og ejendomsadministratorer vil have digital post samme sted som al anden e-mail. Gratis beta; efter beta koster det 39 kr/md på årlig betaling, 49 kr/md månedlig.

## Problemet med dansk digital post

Siden 2014 er kommunikation fra det offentlige digital som udgangspunkt. Det betyder, at hvis din kommune, SKAT, Udbetaling Danmark eller FerieKonto skal fat i dig, lægger de brevet i enten **[mit.dk](https://mit.dk)** (den offentlige portal) eller **[e-Boks](https://www.e-boks.com/)** (historisk set den mest brugte private portal, nu koblet til Digital Post).

I princippet er det fint: samlet, sporbart, ingen papir. I praksis er der en masse friktion:

- **Du skal logge ind med MitID hver gang.** Hvert skattebrev, hver p-afgift, hver feriepenge-besked ligger bag en MFA-flow.
- **Apps notificerer dig, men notifikationerne er tynde.** "Du har ny post" — ikke emnelinje, ikke afsender, ikke nok til at prioritere.
- **Der er ingen indbygget videresendelse.** Du kan ikke sige "send alt fra SKAT til min bogholder på `bogholder@firma.dk`".
- **Virksomheder får det værste af begge verdener.** En CVR-registreret virksomhed har sin egen mit.dk / e-Boks-indbakke. Hvis indehaveren ikke tjekker den, er der ingen, der gør.

E-mail er omvendt standard-indbakken for små virksomheder: delte postkasser, videresendelsesregler, arkivering, filtre, søgning. Nemboks bygger broen imellem.

## Hvad Nemboks gør

Når Nemboks er sat op, logger den på din mit.dk / e-Boks på dine vegne, tjekker for ny post og sender hvert nyt brev videre — **som en rigtig e-mail med PDF'en vedhæftet** — til den eller de adresser, du har konfigureret.

- **En e-mail pr. brev.** Emne = afsender + emne. Brødtekst = tekst-preview. Vedhæftning = PDF'en.
- **Flere selskaber pr. konto.** Hvis du er revisor for flere CVR'er, bor de alle under samme Nemboks-dashboard.
- **Flere destinationer pr. selskab.** Send f.eks. alt fra SKAT til bogholderen, resten til ejeren.
- **Originalen bliver liggende i mit.dk / e-Boks.** Intet slettes — Nemboks læser kun.
- **Logger hver videresendelse.** For revision og ro i maven.

Det praktiske resultat: revisoren eller bogholderen, der allerede bor i Outlook eller Gmail, holder op med at skifte kontekst til en portal en gang om ugen.

## Hvem det er til

Nemboks er bygget til danske SMV'er, især:

- **Revisorer og bogholdere.** Kunden giver adgang én gang; derefter bliver hvert SKAT-brev for hver kunde til en e-mail i den delte indbakke.
- **Ejendomsadministratorer.** En enkelt administrator kan sidde med post for dusinvis af ejendoms-A/S og -ApS.
- **Smv-indehavere.** Enkeltmandsvirksomheden eller to-mands-ApS, hvor ejeren hellere vil have brevet fra kommunen samme sted som sin kunde-mail.

## Stakken

For de nysgerrige:

- **Rails 8** på Ruby 3.4 med Hotwire (Turbo + Stimulus) og Tailwind til dashboardet.
- **PostgreSQL** til persistens.
- **[Auth0](https://auth0.com/)** til autentificering. Brugerne logger på med Google, Microsoft eller e-mail+kodeord — ingen separat Nemboks-kodeord at glemme.
- **[Stripe](https://stripe.com/)** til abonnementsstyring, inkl. deres hostede kundeportal til selv-betjent kortopdatering og opsigelse.
- **[Postmark](https://postmarkapp.com/)** til transaktionel e-mail — de er kategoriens standard for "e-mail der skal lande i indbakken", hvilket er hele pointen med en videresendelses-tjeneste.
- **Docker + Kamal** til deployment. Zero-downtime rollouts på en lille flåde; ingen Kubernetes at drifte.
- **Cloudflare Pages** til det statiske marketing-site på [nemboks.dk](https://nemboks.dk).

Opdelingen — Rails-app på Kamal, marketing-site på Pages — er bevidst. Marketing-sitet skal være billigt, hurtigt og tungt cached; Rails-appen skal have database og baggrundsjobs. At køre dem som to separate deployments holder hver af dem simpel.

## Pris

- **Gratis beta**, mens tjenesten stabiliseres.
- Efter beta: **39 kr/md** på årlig betaling, **49 kr/md** månedlig — excl. moms. Flad pris pr. selskab; ingen pris pr. brev.
- **60 dages gratis prøveperiode** til nye kunder efter beta.

## Ofte stillede spørgsmål

### Må Nemboks læse min mit.dk / e-Boks?

Ja — som indbakke-ejer giver du Nemboks lov til at læse på dine vegne. Nemboks læser kun; intet slettes, besvares eller markeres som læst uden at du har konfigureret det.

### Er det GDPR-compliant?

Nemboks behandler persondata på dine vegne. Som kunde er du dataansvarlig; Nemboks er databehandler, og der er en standard databehandleraftale (DPA) at underskrive. Alle data opbevares i EU.

### Hvad sker der med det originale brev i mit.dk / e-Boks?

Det bliver liggende. Nemboks er read-only.

### Kan jeg videresende til flere e-mailadresser?

Ja. Hvert selskab kan have flere modtagere, og du kan sende forskellige afsendere til forskellige adresser (f.eks. alt fra SKAT til bogholderen).

### Virker Nemboks for privatpersoner?

Det nuværende fokus er danske virksomheder (CVR). En privat-plan kommer måske senere.

### Hvad hvis Nemboks går ned?

Din post lander stadig i mit.dk / e-Boks som normalt; Nemboks videresender bare ikke, før tjenesten er tilbage. Intet går tabt.

### Hvordan opsiger jeg?

Via Stripes kundeportal inde fra dashboardet. Ingen e-mail, intet telefonopkald.

## Hvorfor bygge det

Digital post virker. Det er sikkert, sporbart, og jeg vil hellere have et SKAT-brev i mit.dk end en brun kuvert. Men brugerfladen er designet til en borger, der læser en håndfuld breve om året — ikke til en virksomhed, der får dusinvis om ugen på tværs af flere CVR'er. E-mail løser "dusinvis om ugen på tværs af flere postkasser" udmærket — filtre, regler, delte indbakker, søgning — så den mindst interessante, men mest nyttige bro er at få brevene ud af portalen og ind i e-mailen med PDF'en vedhæftet, uden at nogen skal logge ind hver gang.

Det er Nemboks.
