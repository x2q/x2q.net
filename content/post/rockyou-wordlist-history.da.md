+++
title = "rockyou.txt: historien om verdens mest berømte ordliste (2026)"
date = 2026-07-03
slug = "rockyou-ordliste-historie"
description = "Hvor rockyou.txt egentlig kommer fra, hvorfor den blev standard-ordlisten til password cracking, og hvad der har overhalet den. Et kig på weakpass.com's aktuelle ordliste-rangering — rockyou2021, rockyou2024, og hashmob.net's 'found'-lister i toppen i 2026."

[taxonomies]
tags = ["ordlister", "rockyou", "password-cracking", "hashcat", "weakpass", "sikkerhed", "password-sikkerhed"]

[extra]
summary = "rockyou.txt opstod fra et brud i 2009, hvor 32 millioner kodeord lå i klartekst. Den blev standard-ordlisten til pentest i et årti — men weakpass.com's 2026-rangering viser, at den ikke længere er topklasse. Mindre, kuraterede udsnit (rockyou-65.txt) og løbende opdaterede 'fundet i naturen'-lister fra hashmob.net rangerer nu højere end originalen og dens milliard-linjers efterfølgere rockyou2021.txt og rockyou2024.txt."
faq = [
  { q = "Hvad er rockyou.txt?", a = "rockyou.txt er en klartekstliste med omkring 14,3 millioner rigtige kodeord, udtrukket fra et databrud hos RockYou Inc. i december 2009 — en virksomhed der lavede sociale-netværks-widgets. Bruddet eksponerede omkring 32 millioner brugerkonti, fordi RockYou opbevarede kodeord fuldstændig uhashede — i klartekst i databasen. Efter fjernelse af dubletter blev den lækkede kodeord-kolonne til ordlisten kendt som rockyou.txt." },
  { q = "Er rockyou.txt stadig nyttig i 2026?", a = "Ja, men den er ikke længere det bedste valg. På weakpass.com's effektivitetsrangering ligger den originale rockyou.txt i mellemklassen (C), overhalet af både langt mindre kuraterede udsnit (rockyou-65.txt, 30K linjer) og langt større, løbende opdaterede 'fundne kodeord'-lister fra tjenester som hashmob.net. Den er stadig et rimeligt udgangspunkt, men ikke længere loftet." },
  { q = "Er rockyou2021.txt og rockyou2024.txt fra nye RockYou-brud?", a = "Nej. Trods navnet er ingen af dem nyt bruddata fra RockYou Inc. Begge er community-sammensatte megalister — milliarder af linjer flettet og dedupliceret fra mange tidligere brud, ordlister og algoritmisk genererede permutationer — udgivet på hacker-fora og givet navnet 'rockyou' som et brand for 'den største sammensatte cracking-ordliste', ikke fordi de stammer fra den oprindelige virksomhed." },
  { q = "Hvad er weakpass.com?", a = "weakpass.com er et ordliste-repository og community-hub for password cracking. Det hoster hundredvis af ordlister (fra få kilobyte til 145+ GB) med størrelse, antal linjer og en bogstavkarakter for effektivitet (S til F) baseret på cracking-hitrate snarere end rå størrelse, plus torrent-downloads og et API." },
  { q = "Hvilken ordliste skal jeg egentlig bruge i 2026?", a = "Start småt og målrettet, ikke stort. weakpass.com's S-klasse-valg i 2026 er for det meste små kuraterede lister (rockyou-65.txt) eller løbende opdaterede 'fundne'-lister fra virkeligheden (hashmob.net_2025.*.found) frem for de største filer. Kombinér en beskeden liste med et stærkt regelsæt (best64.rule, OneRuleToRuleThemAll) før du griber efter en 100+ GB megaliste — regler på en god lille liste slår ofte rå størrelse." }
]
+++

**Kort fortalt —** `rockyou.txt` er 14,3 millioner rigtige kodeord lækket i klartekst fra ét firmas databrud i 2009. Den blev standard-ordlisten for en hel generation af password cracking — bundlet i Kali Linux, citeret i hver eneste hashcat-tutorial, udødeliggjort som `/usr/share/wordlists/rockyou.txt.gz`. I 2026 findes den stadig, men den er ikke længere det bedste værktøj til opgaven: weakpass.com's aktuelle rangering placerer små kuraterede udsnit og løbende opdaterede 'fundne kodeord fra virkeligheden'-lister over den. Dette indlæg dækker, hvor den kom fra, hvorfor den vandt, og hvad der reelt vinder nu.

## December 2009: et firma der ikke hashede sine kodeord

**RockYou Inc.** lavede Flash-baserede sociale-netværks-widgets — SuperWall, sjove foto-apps — til MySpace og Facebook, på højdepunktet af platform-app-boomet. I december 2009 eksponerede en **SQL-injection**-sårbarhed på RockYous side hele deres brugerdatabase: omkring **32 millioner konti**.

Bruddet ville have været en fodnote, hvis ikke for én detalje: RockYou opbevarede kontoadgangskoder som **klartekst**. Ingen hashing, ingen salting — bare kodeordet, ordret, ved siden af e-mailadressen. Da dumpet cirkulerede, havde sikkerhedsforskere noget nærmest uhørt: **millioner af rigtige kodeord, i klartekst**, uden behov for cracking for at se, hvad folk faktisk valgte.

Efter fjernelse af dubletter endte den unikke kodeord-kolonne på **~14,3–14,4 millioner linjer**, og den begyndte at cirkulere som en almindelig `.txt`-fil under navnet på det brudte firma: `rockyou.txt`.

## Hvorfor den blev standarden

Der skete masser af lækager før og efter 2009. `rockyou.txt` blev specifikt standarden for pentest/CTF/red-team af nogle konkrete grunde:

- **Det var rigtige, uhashede, menneskevalgte data.** Ikke en ordbog af engelske ord, ikke et genereret permutationssæt — rigtige kodeord rigtige mennesker skrev, med bias mod præcis den slags forudsigelige mønstre (`iloveyou`, `password1`, fødselsdatoer, tastatur-walks), som rigtige konti kompromitteres med.
- **Størrelsen passede til hardwaren fra tiden.** 14,3M kandidater kørte til ende på en enkelt CPU eller tidlig GPU på rimelig tid — nyttig, ikke bare symbolsk.
- **Den var gratis og overalt.** Ingen konto-mur, ingen nedtagning der holdt. Den blev bundlet i **SecLists** og leveret som standard i **BackTrack**, derefter **Kali Linux**, på `/usr/share/wordlists/rockyou.txt.gz` — hvilket satte den på hver eneste pentesters maskine, uanset om de ledte efter den eller ej.
- **Engelsk-flertals-bias matchede flertallet af tidlige 2010'er-mål.** Efterhånden som cracking-værktøjer blev globale, blev dette en begrænsning, ikke bare en fordel — men på det tidspunkt var det en hitrate-fordel.

I begyndelsen af 2010'erne var "kør rockyou.txt mod det" standardtrækket i næsten hvert eneste WPA-håndtryk, hashet database-dump eller CTF-udfordring med et kodeord-hash.

## Navnet overlevede bruddet

Her er den del, der overrasker folk: **rockyou2021.txt** og **rockyou2024.txt**, de kæmpestore efterfølger-navngivne lister du finder i dag, er **ikke** nye brud på RockYou Inc.

- **rockyou2021.txt** dukkede op på et hacker-forum i juni 2021: omkring **8,46 milliarder linjer**, sammensat ved at flette dusinvis af tidligere lækager, ordlister og algoritmisk genererede permutationer (case-varianter, leetspeak-substitutioner, tal-suffikser) — ikke friskstjålne credentials.
- **rockyou2024.txt** fulgte samme mønster i 2024: omkring **9,95 milliarder linjer**, endnu en community-megasammensætning.

Navnet "rockyou" blev genbrugt som et **brand for "den største sammensatte cracking-ordbog lige nu"**, løsrevet fra sin oprindelige betydning. Begge er rigtige, begge er enorme, og begge er værd at have — men ingen af dem fortæller dig noget om RockYou Inc.'s faktiske 2009-brugere. Behandl navnet som en genre-etiket, ikke en oprindelsespåstand.

## Hvad weakpass.com's rangering faktisk viser i 2026

[weakpass.com](https://weakpass.com/wordlists) er det tætteste, cracking-communityet har på et live ordliste-leaderboard: hundredvis af lister, hver med størrelse, antal linjer og en bogstavkarakter for **effektivitet (S til F)** — baseret på reel cracking-hitrate, ikke rå størrelse. At trække den aktuelle top af tavlen er mere interessant end noget enkelt tal:

| Ordliste | Rang | Størrelse | Linjer |
|---|:---:|---:|---:|
| `weakpass_4.merged.txt` | S | 37,72 GB | 3,58 mia. |
| `all-h.txt` | S | 28,51 GB | 2,72 mia. |
| `all-h.latin.txt` | S | 28,35 GB | 2,71 mia. |
| `triple-h.txt` | S | 21,82 GB | 2,13 mia. |
| `SAWL.txt` | S | 17,02 GB | 1,49 mia. |
| `cyclone.hashesorg.hashkiller.combined.txt` | S | 15,02 GB | 1,47 mia. |
| `hashpwn.txt` | S | 14,11 GB | 1,35 mia. |
| `Hashes.org` | S | 13,99 GB | 1,40 mia. |
| `dictionary_private.dic` | S | 2,66 GB | 206,28 mio. |
| `hashmob.net_2025.user.found` | S | 979,96 MB | 84,29 mio. |
| `rockyou-65.txt` | S | 238,80 KB | 30,29 K |
| `weakpass_4a.txt` | A | 81,37 GB | 8,44 mia. |
| `clatsdictionary.txt` | A | 71,55 GB | 7,87 mia. |
| `rockyou2024.txt` | B | 145,27 GB | 9,95 mia. |
| `rockyou2021.txt` | B | 91,62 GB | 8,46 mia. |
| **`rockyou.txt` (originalen)** | **C** | **133,44 MB** | **14,34 mio.** |

Den sidste række er den interessante. Den originale `rockyou.txt` — filen der definerede et årti af tutorials — rangerer **under** både et 238-kilobyte kuraterede udsnit af sig selv og de milliard-linjers megasammensætninger, der lånte dens navn. Tre ting sker på samme tid:

### 1. Rang måler hitrate, ikke størrelse

weakpass bedømmer efter **cracking-effektivitet**, ikke rå antal linjer. En lille, omhyggeligt kurateret liste, der rammer en høj procentdel af rigtige kodeord pr. forsøgt kandidat, rangerer over en vidtstrakt liste polstret med permutationsstøj. Derfor sidder `rockyou-65.txt` — et udsnit på **30.290 linjer, 238 KB** — i **S-klasse**, samme kategori som 30+ GB megalister, mens originalen med 14,34 millioner linjer sidder tre klasser lavere.

### 2. Procentvis udsnit af rockyou er en reel teknik

weakpass udgiver en hel familie af `rockyou-XX.txt`-filer — `rockyou-5.txt` op til `rockyou-75.txt` — hver et sandsynlighedsvægtet udsnit af originalen, holdt i faldende rækkefølge efter observeret hyppighed. `rockyou-5.txt` er 13 linjer; `rockyou-75.txt` er 59.190. Ideen: til en hurtig første gennemgang mod et stort sæt hashes udgør de øverste 5–15% af `rockyou.txt` efter observeret hyppighed ofte en uforholdsmæssig stor andel af de crackbare konti. Prøv det lille udsnit først; grib kun til den fulde 14,3M-linjers liste, eller efterfølgerne på milliarder af linjer, hvis det hurtige gennemløb kommer tomhændet tilbage.

| Udsnit | Størrelse | Linjer |
|---|---:|---:|
| `rockyou-5.txt` | 104 Bytes | 13 |
| `rockyou-25.txt` | 7,06 KB | 929 |
| `rockyou-50.txt` | 74,13 KB | 9,44 K |
| `rockyou-65.txt` | 238,80 KB | 30,29 K |
| `rockyou-75.txt` | 467,72 KB | 59,19 K |
| `rockyou.txt` (fuld) | 133,44 MB | 14,34 mio. |

### 3. "Fundet i naturen, i år" slår "lækket engang, for et årti siden"

Det andet mønster i toppen af S-klassen: **`hashmob.net_2025.*.found`**-listerne. [hashmob.net](https://hashmob.net) er et levende community-hub for hash-cracking — kodeord-hashes bliver indsendt, communityet cracker hvad det kan, og de succesfuldt crackede klartekster udgives tilbage som ordlister, løbende opdateret. Fordi de repræsenterer **kodeord folk vælger lige nu**, ikke kodeord folk valgte i 2009, har de en aktualitetsfordel, ingen statisk lækage kan matche, uanset størrelse.

## Hvad det betyder i praksis

Hvis du vælger en ordliste i 2026, er "største fil" den forkerte tommelfingerregel:

1. **Start småt og målrettet.** Et kurateret udsnit (`rockyou-65.txt`) eller en frisk "fundet"-liste slår en 100 GB megafil til en første gennemgang — det er færdigt på sekunder og rydder ofte en meningsfuld del af de svage konti.
2. **Tilføj regler før størrelse.** `hashcat -a 0 -r best64.rule` (eller den langt større `OneRuleToRuleThemAll.rule`) mod en beskeden basisliste genererer størrelsesordener flere effektive kandidater end den samme liste kørt rå — og slår normalt en større umuteret liste for samme tidsbudget.
3. **Grib til megalisterne til sidst.** `rockyou2021.txt`, `rockyou2024.txt`, `weakpass_4.merged.txt` og lignende er værd at have til udtømmende offline-arbejde mod et hash-sæt, du har råd til timer eller dage imod — ikke som det første, du prøver.
4. **Den originale `rockyou.txt` er stadig en fin baseline** — gratis, lille nok til hurtig iteration, velforstået — bare ikke længere loftet.

> Se [hashcat WiFi-cracking i 2026](/da/post/crack-wifi-med-hashcat-2026/) for disse ordlister i aktion mod et rigtigt WPA-håndtryk, og [25 år med Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/) for den bredere angrebs- og forsvarshistorie.
