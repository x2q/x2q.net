+++
title = "apextowww.com — gratis apex-til-www-omdirigering (Let's Encrypt, IPv6, HTTP/3)"
date = 2026-04-18
slug = "apextowww-com-apex-til-www-omdirigering"
description = "Gratis apex-til-www-omdirigering. Peg dit nøgne domænes A/AAAA-records mod apextowww og få automatisk Let's Encrypt-TLS, IPv4 og IPv6, HTTP/3. Ingen oprettelse."

[taxonomies]
tags = ["dns", "http", "letsencrypt", "hetzner", "cloudflare-pages", "netlify", "vercel", "apex-domaene"]

[extra]
summary = "En gratis offentlig tjeneste, der 301-omdirigerer ethvert apex-domæne (nøgent domæne) til sit www-subdomæne — med automatisk Let's Encrypt-TLS, IPv4+IPv6 og HTTP/3. Bygget til hostingplatforme, der kræver CNAME på zoneapex."
+++

**TL;DR —** DNS tillader ikke `CNAME`-records på zoneapex ([RFC 1034 §3.6.2](https://www.rfc-editor.org/rfc/rfc1034#section-3.6.2)). Det er derfor hostingplatforme som Netlify, Vercel, Cloudflare Pages, Firebase og Heroku beder dig om at sætte `www.eksempel.dk` op med en `CNAME` og lader `eksempel.dk` (selve apex) være et problem, du selv løser. [apextowww.com](https://apextowww.com) løser det: peg to `A`-records og to `AAAA`-records mod tjenesten, og den udsteder et Let's Encrypt-certifikat til dit apex og `301`-omdirigerer hver forespørgsel til `https://www.ditdomæne.tld/` — med sti og querystring bevaret. Gratis, ingen oprettelse, ingen konto.

## Hvorfor du ikke kan sætte en CNAME på apex

DNS-specifikationen er entydig: en zoneapex (det "nøgne" domæne som `eksempel.dk`) skal have en `SOA`-record og som regel `NS`-records. `CNAME` er defineret som et alias, der skal stå alene — den må ikke sameksistere med de `SOA`- og `NS`-records, som apex er forpligtet til at have. Derfor kan du godt `CNAME www.eksempel.dk → mitsite.netlify.app`, men du **kan ikke** `CNAME eksempel.dk → mitsite.netlify.app`.

Der findes workarounds, og alle er en smule akavede:

- **ALIAS- / ANAME-records.** Leverandørspecifikke hos Cloudflare, Route 53, DNSimple, NS1 og andre. De virker ved at slå målet op bag kulisserne og returnere en `A`/`AAAA`. Fint, hvis din DNS-udbyder understøtter det; ubrugeligt, hvis ikke.
- **Fladning på udbyderniveau.** Cloudflares "CNAME flattening" er præcis det, gjort automatisk.
- **Din egen altid-tændte VPS med `301 → www`.** Det var det, jeg gjorde for flere domæner — både overkill og en lille vedligeholdelsesskat.

apextowww er den fjerde mulighed: en andens altid-tændte omdirigerer, driftet for dig.

## Hvad apextowww gør

Nøjagtig én ting: en `301 Moved Permanently` fra `https://ditdomæne.tld/noget?x=y` til `https://www.ditdomæne.tld/noget?x=y`.

- **TLS** udstedes automatisk ved første forespørgsel via Let's Encrypts HTTP-01-challenge. Ingen ACME-klient at køre selv.
- **IPv4 + IPv6** som dual-stack fra starten. Begge record-typer er påkrævet.
- **HTTP/1.1, HTTP/2 og HTTP/3** serveres. Selve omdirigeringen er lille, så protokolversion betyder mindre, men det hjælper first-paint, når omdirigeringen ligger i den kritiske sti.
- **Sti og querystring** bevares, så deep links stadig virker.
- **Ingen oprettelse, intet login, ingen konto.** Hvis DNS er peget korrekt, virker det bare.

## Sådan sætter du det op

1. Gå til [apextowww.com](https://apextowww.com) og kopiér de aktuelle IP-adresser (to IPv4, to IPv6).
2. I din DNS-udbyder: sæt `A`-records på dit apex, der peger på de to IPv4-adresser. Fjern eventuelle eksisterende `A`-records på apex.
3. Sæt `AAAA`-records på dit apex, der peger på de to IPv6-adresser.
4. Sørg for, at `www.ditdomæne.tld` stadig peger på din rigtige host (CNAME til Netlify / Vercel / Pages / osv.).
5. Vent på DNS-propagering. Besøg `http://ditdomæne.tld/` — den skal nu 301-omdirigere til `https://www.ditdomæne.tld/`.

apextowww-siden har platform-specifikke guides under `/netlify-apex-domain-redirect/`, `/vercel-apex-domain-redirect/`, `/cloudflare-pages-apex-redirect/`, `/firebase-hosting-apex-redirect/` og `/heroku-apex-domain-redirect/`.

## Stak

- **Hetzner ARM64**-servere for billig, strømbesparende compute. ARM64 er ~30 % billigere pr. vCPU hos Hetzner end x86 og kører omdirigereren uden at ryste på hånden.
- **Caddy-agtig automatisk TLS** med **Let's Encrypt** HTTP-01-challenges.
- Dual-stack **IPv4 + IPv6**.
- **HTTP/1.1, HTTP/2, HTTP/3**.
- Offentligt **statisk marketing-site** på Cloudflare Pages, med platform-guides i hver sin URL-sti, så de rangerer uafhængigt på Google for "netlify apex redirect", "vercel apex domain" osv.

## Ofte stillede spørgsmål

### Kan jeg bruge apextowww sammen med Cloudflare DNS?

Ja — men du skal have Cloudflares proxy (den orange sky) **slået fra** på apex'ens `A`/`AAAA`-records. Hvis proxien er slået til, opfanger Cloudflare forespørgslen, og Let's Encrypts HTTP-01-challenge når aldrig frem til apextowww. Når certifikatet er udstedt og forny­es, skal du ikke bøvle videre — bare lad det være slukket.

### Understøtter apextowww wildcards eller andre subdomæner end www?

Nej. Tjenesten omdirigerer kun apex til `www.`. Alt andet bliver liggende hos din rigtige host.

### Hvad sker der, hvis apextowww-IP'erne skifter?

Så skal du opdatere dine DNS `A`/`AAAA`-records. Operatøren offentliggør aktuelle IP'er på forsiden og giver varsel før ændringer. Det er fint for et privat domæne; for noget missionkritisk bør du køre din egen omdirigerer.

### Er der rate-limit?

Der er ingen publiceret hård grænse, men det er en gratis community-tjeneste. Hvis du serverer millioner af apex-omdirigeringer i døgnet, er det tid til at selv-hoste.

### Hvorfor ikke bare bruge Cloudflares gratis plan?

Cloudflares CNAME-flattening på apex er et fint alternativ, hvis hele din DNS er hos Cloudflare. apextowww er nyttig, når din DNS ikke er hos Cloudflare, eller når du vil have en host-agnostisk omdirigerer, der virker identisk på tværs af domæner.

### Er den virkelig gratis?

Ja. Marginalomkostningen pr. omdirigering på ARM64 er minimal. Ingen reklamer, ingen tracking ud over grundlæggende logs, ingen upsell.

## Hvorfor den findes

Hostingplatforme optimerer efter deres egen onboarding, ikke efter de DNS-selvfølgeligheder, der snubler enhver ny bruger. Det føltes værre at sende folk videre til en fremmeds VPS end selv at drifte én. Nu peger mine egne apex-domæner (inklusive [x2q.net](https://www.x2q.net)) på apextowww, og jeg har kunnet slukke for den sidste lille omdirigerer-VPS, jeg stadig kørte af historiske grunde.

Det er den slags projekt, der ikke virker interessant, før du har brug for det — og så er det lige præcis det, du skal bruge.
