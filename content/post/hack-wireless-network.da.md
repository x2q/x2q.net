+++
title = "Wi-Fi-hacking gennem 25 år — 2002, 2007, 2012, 2017, 2022, 2027"
date = 2026-04-22
slug = "hack-traadloest-netvaerk"
description = "Et tilbageblik på Wi-Fi-sikkerhed fra WEP i 2002 til WPA3 og 6 GHz i 2027. Hvad angribere gjorde ved hver milepæl, og hvad forsvarere bør gøre i dag."

[taxonomies]
tags = ["wifi", "wep", "wpa", "wpa2", "wpa3", "aircrack-ng", "hashcat", "krack", "pmkid", "netvaerkssikkerhed", "tilbageblik"]

[extra]
summary = "25 år Wi-Fi-sikkerhed i ét indlæg: WEP faldt i 2001, WPA2 dominerede i et årti, KRACK brød den i 2017, WPA3 overtog langsomt, og i 2027 er angrebsoverfladen 6 GHz, huller i management-frame-beskyttelse og social engineering. Defensiv vejledning inkluderet."
+++

**TL;DR —** Wi-Fi-sikkerhed har været gennem fire generationer — **WEP**, **WPA**, **WPA2**, **WPA3** — hver introduceret, fordi forgængeren var brudt. Dette indlæg går gennem seks snapshots af state of the art: **2002** (WEP, trivielt), **2007** (WEP død, WPA udbredt, offline-angreb kommer frem), **2012** (WPA2 dominerer, dictionary-angreb på GPU'er), **2017** (KRACK bryder WPA2 under de rette betingelser, PMKID-lækken i 2018), **2022** (WPA3 ruller ud, downgrade-angreb, cloud-skala-cracking), **2027** (dagens landskab: WPA3 næsten universel, 6 GHz åbner ny overflade, angreb flytter op i stakken). For hvert år opsummerer jeg angrebet, værktøjet og hvad en forsvarer burde have gjort. Kun autoriseret testning — den defensive vejledning i bunden er pointen.

## 2002 — WEP overalt, og trivielt brudt

**Standard:** IEEE 802.11b med **WEP** (Wired Equivalent Privacy). 40-bit eller 104-bit RC4-nøgle, 24-bit IV, CRC-32-integritet.

**Hvad er galt med den:** IV'en er for lille, nøglerne er statiske, og RC4's initial key schedule lækker bits af nøglen, når visse IV'er bruges. Det er **FMS-angrebet** (Fluhrer, Mantin, Shamir, 2001) og dets efterkommere.

**Hvad en angriber gjorde i 2002:** fangede trafik med en Prism-baseret USB-adapter, indsamlede et par millioner pakker (timer på et aktivt netværk) og udtrak nøglen med **AirSnort** eller **WEPCrack**. Angrebene var så pinlige, at Wi-Fi Alliance skubbede WPA som en midlertidig firmware-patchbar løsning i 2003.

**Hvad en forsvarer burde have gjort:** erkendt, at WEP ikke er en sikkerhedsfunktion, og behandle det trådløse LAN som ubetroet. Brug en VPN eller IPSec på lag 3.

## 2007 — WEP død, WPA overgangsvis, WPA2 på vej

**Standard:** WPA (2003), en nød-løsning med per-pakke-nøgler (TKIP). WPA2 (2004) med AES-CCMP begynder at dukke op i hjemme-routere.

**Hvad der er nyt for angribere:** **PTW-angrebet** på WEP (2007) reducerer pakke-antallet fra ~1 million til ~40.000 — WEP kan nu crackes på minutter. **aircrack-ng** bliver den kanoniske toolkit. Mod WPA-Personal bliver offline-dictionary-angreb på 4-way-handshake praktiske på CPU'er: fang en handshake, fodr PSK-afledningen gennem `cowpatty` eller `aircrack-ng`, prøv dictionary-indgange én ad gangen.

**Hvad angribere endnu ikke havde:** meningsfuld GPU-acceleration af WPA-PSK. Dictionary-angreb var langsomme.

**Hvad en forsvarer burde have gjort:** migrere til WPA2-AES-CCMP, vælg en PSK længere end nogen dictionary. Drop WEP-netværk helt.

## 2012 — WPA2 dominerer, GPU-cracking moden

**Standard:** WPA2 er default på stort set al consumer-gear. WPA2-Enterprise (802.1X / EAP) i corporate-netværk.

**Hvad der er nyt for angribere:** **hashcat** og **oclHashcat**, **pyrit** og **John the Ripper** gør WPA-PSK-dictionary-angrebet til et **GPU-problem**. En handshake-capture + en enkelt moderne GPU klarer titusindvis af kandidat-PSK'er pr. sekund; en lille lejet GPU-farm håndterer hundredtusinder. **airodump-ng** + **Reaver** (2011) udnytter en implementerings-fejl i **WPS-PIN** til at gendanne WPA-PSK'en helt uden en dictionary — en dødsdom for hjemme-routere med WPS-on-by-default.

**Hvad forsvarere burde have gjort:**
- **Slå WPS fra.** De fleste routere havde den tændt som default.
- **Brug lange tilfældige PSK'er**, ikke dictionary-ord.
- Til enterprise: **802.1X + EAP-TLS med klient-certifikater**, ikke PEAP-MSCHAPv2 (som i sig selv er et GPU-problem).

## 2017 — KRACK

**Standard:** WPA2 stadig overalt.

**Hvad der er nyt for angribere:** **KRACK** (Vanhoef, Piessens, 2017) — Key Reinstallation Attack. Det cracker ikke PSK'en. Det udnytter en subtil fejl i 4-way-handshaken, hvor, under visse betingelser (specifikt på Android 6+ og wpa_supplicant 2.4–2.6), genafspilning af handshake-meddelelse 3 får klienten til at geninstallere en **all-zero session-nøgle**. Derfra kan angriberen dekryptere udvalgt trafik og, afhængigt af cipher suite, injicere pakker.

**Hvad gjorde KRACK anderledes end tidligere angreb:** det ramte **protokollen, ikke nøglen**. En stærk PSK hjalp ikke. Hver WPA2-implementation havde brug for en patch. De fleste leverandører leverede en inden for uger; nogle tog år.

**Også i denne æra:**
- **PMKID hashcat-angrebet** (2018, Steube). Mange AP'er lækker PMKID'en i en enkelt besked; én pakke er nok til at starte et offline PSK-angreb. Sænkede capture-barren yderligere — ingen klient-association nødvendig.
- **Evil twin / captive portal-phishing.** Efterhånden som enheds-UI'er blev smukkere, blev falske captive portals alarmerende effektive mod mennesker.

**Hvad en forsvarer burde have gjort:** patch Android / wpa_supplicant straks, håndhæv HTTPS overalt, så dekrypteret Wi-Fi-trafik er mindre nyttig, begynd at planlægge WPA3-migration.

## 2022 — WPA3 ruller ud, downgrade-angreb

**Standard:** WPA3 (2018) påkrævet til Wi-Fi CERTIFIED-enheder siden 2020. Nøgle-opgraderinger:
- **SAE** (Simultaneous Authentication of Equals) erstatter 4-way-handshake-PSK'en — offline-dictionary-angreb bliver ufremkommelige.
- **192-bit mode** til Enterprise.
- **Forward secrecy**.
- **PMF** (Protected Management Frames) obligatorisk — neutraliserer deauth-baseret denial-of-service.

**Hvad der er nyt for angribere:** WPA3 er ikke brudt, men dens udrulning er for det meste ikke WPA3-**kun**. **WPA2/3-transition-mode** — default på de fleste AP'er — betyder, at en angriber kan tvinge en downgrade og angribe som WPA2. Det er **Dragonblood** (Vanhoef, Ronen, 2019 + opfølgninger): en familie af side-channel- og downgrade-angreb mod SAE. I 2022 lukkede patchede SAE-implementationer for det meste timing-side-channels; downgrade-angrebet virker stadig på mixed-mode-netværk.

**Også i denne æra:**
- **Cloud-skala-cracking**: at leje 8× H100 eller lignende på timebasis gør PMK-dictionary-angreb praktiske på en skala, ingen amatør havde i 2012.
- **Chipset-firmware-sårbarheder** (FragAttacks, 2021): fejl i selve Wi-Fi-stakken, under WPA-laget, lader angribere injicere frames uden at skulle bryde en handshake overhovedet.

**Hvad en forsvarer burde have gjort:** WPA3-Personal kun (ingen WPA2-transition) på netværk, hvor du kan håndhæve det; PMF påkrævet; lang tilfældig PSK selv med SAE; hold AP-firmware opdateret.

## 2027 — dagens landskab

**Standard:** Wi-Fi 6E (6 GHz) og tidlige Wi-Fi 7-udrulninger. WPA3 næsten universel på nyt gear; legacy WPA2 stadig almindelig i små virksomheder og længe-levende hjemme-netværk.

**State of the art i angreb:**

- **SAE holder.** Intet offentligt, praktisk angreb mod et velkonfigureret WPA3-Personal-netværk i 2027. Dictionary-angreb mod PSK'en er ikke fremkommelige — det er SAE's pointe.
- **Downgrade-angreb** er den primære ting. Ethvert netværk, der stadig annoncerer WPA2/3-transition, kan angribes som WPA2. Modstandere kigger efter mixed-mode-SSID'er først.
- **6 GHz åbner ny overflade.** 6 GHz-båndet kræver WPA3 til nye standarder; men legacy-klient-bridging, IoT-enheder uden 6 GHz-understøttelse og fejlkonfigureret co-broadcast-SSID'er skaber inkonsistenser, angribere udnytter.
- **Klient-side-angreb.** Når link-laget er sikkert, flytter angribere op. Rogue-captive-portals der snyder telefoner til at stole på et dårligt certifikat, QR-kode-tilslutning med falske SSID'er, deauth-under-roaming-angreb (sværere nu med PMF, men ikke elimineret).
- **Supply chain.** Firmware-indlejrede bagdøre og vendor-bugs i Wi-Fi-chipsets (FragAttacks-arven) er stadig en varig kilde til exploits.
- **Cloud-cracking er blevet commodity.** Et weekend-langt SAE-offline-angreb (i de tilfælde, hvor offline-angreb er muligt, altså målet kørte en upatched SAE) koster groft prisen på en pæn middag. Det betyder for det meste intet, fordi SAE ikke er reducerbart til offline-dictionary-angreb — men det skubber økonomien på legacy-WPA2-netværk, folk ikke har migreret.

**Værktøjer stadig i rotation i 2027:** aircrack-ng (ældre, stadig kanonisk til captures og WPA2), hashcat (cracking), bettercap (Wi-Fi MITM / rogue AP), airgeddon (workflow-lim) og en bølge af ESP32-baserede lomme-værktøjer til opportunistisk deauth og handshake-capture.

## Defensiv vejledning for 2027

Det er den del, der betyder mere end al historien.

- **WPA3-Personal SAE-only eller WPA3-Enterprise med EAP-TLS.** Ingen transition-mode på noget netværk, du kan kontrollere. Tjek eksplicit — mange AP'er default til transition.
- **PMF påkrævet, ikke valgfrit.** Protected Management Frames forhindrer deauth-drevne handshake-captures og basal denial-of-service.
- **PSK-længde: tilfældig, ≥ 20 tegn.** SAE gør korte PSK'er sikrere end de plejede at være, men ingen grund til at spille.
- **Slå WPS permanent fra.** Selvom WPS-PIN-angrebet er oldgammelt, leverer mange routere stadig med det aktiveret for "bekvemmelighed".
- **Gæste-SSID isoleret.** Klient-til-klient-isolation slået til og routet til et separat VLAN uden intern LAN-adgang.
- **IoT-SSID, separat og indelukket.** Billige Wi-Fi-termostater og legetøj er det svageste led på de fleste hjemme-netværk. De får deres eget SSID, deres eget VLAN og ingen rute til noget vigtigt.
- **Firmware-opdateringer på AP'er.** De fleste interessante 2020'er-Wi-Fi-sårbarheder var på chipset-niveau; rettelsen er altid en firmware-opdatering. Køb AP'er fra en leverandør, der leverer dem.
- **Antag at link-laget vil fejle og forsvar dig over det.** HTTPS overalt, klient-certs på alt, der betyder noget, VPN eller Tailscale til fjernadgang. Når (ikke hvis) nogen bryder din Wi-Fi, skal lag 4+ stadig holde.

## Hvad der forblev det samme gennem 25 år

Tre mønstre gentager sig ved hver generation:

1. **Kryptografien er næsten altid stærkere end udrulningerne.** WEP var en design-fejl; WPA2 og WPA3 er blevet brudt af implementerings-fejl, downgrade-stier og side-channels — ikke af rene krypto-svagheder.
2. **Defaults betyder mere end kapabiliteter.** WPS tændt som default, WPA2/3-transition-mode tændt som default, gæste-netværk uden isolation som default — det er det, angribere faktisk finder, i skala.
3. **Angriberen flytter altid op i stakken.** Når link-lags-sikkerheden forbedres, skifter angreb til captive portals, falske certs, klient-fejlkonfigurationer og phishing. Ingen mængde WPA3 retter brugeren, der klikker "Stol på" på evil-twin'ens falske certifikat.

## Coda

Hvis denne posts forfader på dette site, fra 2010, var "Hvordan man hacker et trådløst netværk" og fokuserede på WEP med `aircrack-ng`, er 2027-versionen tættere på "Hvordan man tænker om Wi-Fi-sikkerhed" og fokuserer på konfiguration, patching og realistisk trussels-modellering. Kryptografien har gjort sit arbejde. Lagene omkring den er den interessante front nu.

Test dine egne netværk — eller netværk, du er autoriseret til at teste — test ikke nogen andens. Samme lov, der gjaldt i 2002, gælder i 2027.
