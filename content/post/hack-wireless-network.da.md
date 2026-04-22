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

## Overblik

| År | Dominerende standard | Hovedangreb | Indsats for typisk netværk | Hurtigste dictionary / nøgle-rate dengang |
|------|---------------------|-------------|----------------------------|-------------------------------------------|
| 2002 | WEP (100%) | FMS statistisk IV | ~4M pakker / 2–10 t på aktivt AP | N/A — nøglen udledes af IV'er |
| 2007 | WEP 35%, WPA 25%, WPA2 20%, åben 20% | PTW + aircrack-ng | 40–85k pakker / <5 min (WEP) | ~50–100 PSK/s (CPU, cowpatty) |
| 2012 | WPA2 ~70% | Reaver (WPS) + GPU PSK dictionary | 11.000 WPS-PIN-forsøg / 2–10 t | ~75.000 PSK/s (GTX 580) |
| 2017 | WPA2 ~85% | KRACK; derefter PMKID (2018) | 1 pakke (PMKID) → offline dict | ~400.000 PSK/s (GTX 1080) |
| 2022 | WPA2 ~60%, WPA3 ~20%, mixed ~15% | Dragonblood downgrade | Tving WPA2-fallback, så GPU/cloud | ~1,2M PSK/s (RTX 3090), ~10M (8× A100) |
| 2027 | WPA3 ~40%, mixed ~35%, WPA2 ~20% | Klient-side + downgrade + chipset-FW | SAE intakt; legacy WPA2 på lånt tid | ~5–8M PSK/s (RTX 5090-klasse enkelt GPU) |

Globale udbredelses-andele er omtrentlige, afledt af offentlige Wi-Fi-målinger (WiGLE-trends + leverandør-rapporter); regn med ± 10 procentpoint.

## 2002 — WEP overalt, og trivielt brudt

**Standard:** IEEE 802.11b med **WEP** (Wired Equivalent Privacy). 40-bit eller 104-bit RC4-nøgle, 24-bit IV, CRC-32-integritet.

**Hvad er galt med den:** IV'en er for lille, nøglerne er statiske, og RC4's initial key schedule lækker bits af nøglen, når visse IV'er bruges. Det er **FMS-angrebet** (Fluhrer, Mantin, Shamir, 2001) og dets efterkommere.

**Hvad en angriber gjorde i 2002:** fangede trafik med en Prism-baseret USB-adapter, indsamlede et par millioner pakker (timer på et aktivt netværk) og udtrak nøglen med **AirSnort** eller **WEPCrack**. Angrebene var så pinlige, at Wi-Fi Alliance skubbede WPA som en midlertidig firmware-patchbar løsning i 2003.

**Tal (2002):**

- **Global Wi-Fi-udbredelse:** ~100% WEP (WPA blev først ratificeret marts 2003).
- **Nøglelængde:** 40 bit (eksport-grade) eller 104 bit. Irrelevant — angrebet er på IV'en, ikke på nøglen.
- **IV-space:** 24 bit → kun ~16,7 M mulige IV'er. Fødselsdags-kollision efter ~5.000 pakker.
- **FMS-angrebets pakke-antal:** ~500 k–4 M "interessante" IV-frames (få timers aktiv trafik).
- **Typisk crack-tid i ur-tid:** 2–10 t på et travlt SOHO-netværk.
- **Forbrugerhardware:** én laptop + én Prism2/Prism2.5 USB-dongle (~$40 brugt dengang).
- **Værktøjer:** AirSnort, WEPCrack, Kismet til capture.
- **CVE'er:** WEP er ikke i sig selv en CVE, men Borisov/Goldberg/Wagner (2001) og FMS-paperet (2001) er de kanoniske referencer.

**Hvad en forsvarer burde have gjort:** erkendt, at WEP ikke er en sikkerhedsfunktion, og behandle det trådløse LAN som ubetroet. Brug en VPN eller IPSec på lag 3.

## 2007 — WEP død, WPA overgangsvis, WPA2 på vej

**Standard:** WPA (2003), en nød-løsning med per-pakke-nøgler (TKIP). WPA2 (2004) med AES-CCMP begynder at dukke op i hjemme-routere.

**Hvad der er nyt for angribere:** **PTW-angrebet** på WEP (2007) reducerer pakke-antallet fra ~1 million til ~40.000 — WEP kan nu crackes på minutter. **aircrack-ng** bliver den kanoniske toolkit. Mod WPA-Personal bliver offline-dictionary-angreb på 4-way-handshake praktiske på CPU'er: fang en handshake, fodr PSK-afledningen gennem `cowpatty` eller `aircrack-ng`, prøv dictionary-indgange én ad gangen.

**Hvad angribere endnu ikke havde:** meningsfuld GPU-acceleration af WPA-PSK. Dictionary-angreb var langsomme.

**Tal (2007):**

- **Global udbredelse (WiGLE-målinger):** WEP ~35%, WPA ~25%, WPA2 ~20%, åben ~20%.
- **PTW-angrebets pakke-antal:** ~40.000–85.000 fangede frames for at gendanne en WEP-nøgle (ned fra millioner).
- **Crack-tid med aircrack-ng + pakke-injektion:** <5 minutter, ofte under 60 sekunder.
- **WPA-PSK dictionary-rate (CPU, cowpatty/aircrack-ng):** ~50–100 kandidater/sek pr. core.
- **Rockyou-ordliste** (lækket dec. 2009): 14,3 M indgange — blev de-facto engelsk PSK-ordliste.
- **WPA2 obligatorisk for Wi-Fi CERTIFIED:** marts 2006.
- **Aircrack-ng 1.0:** udgivet 2006, konsoliderede økosystemet.

**Hvad en forsvarer burde have gjort:** migrere til WPA2-AES-CCMP, vælg en PSK længere end nogen dictionary. Drop WEP-netværk helt.

## 2012 — WPA2 dominerer, GPU-cracking moden

**Standard:** WPA2 er default på stort set al consumer-gear. WPA2-Enterprise (802.1X / EAP) i corporate-netværk.

**Hvad der er nyt for angribere:** **hashcat** og **oclHashcat**, **pyrit** og **John the Ripper** gør WPA-PSK-dictionary-angrebet til et **GPU-problem**. En handshake-capture + en enkelt moderne GPU klarer titusindvis af kandidat-PSK'er pr. sekund; en lille lejet GPU-farm håndterer hundredtusinder. **airodump-ng** + **Reaver** (2011) udnytter en implementerings-fejl i **WPS-PIN** til at gendanne WPA-PSK'en helt uden en dictionary — en dødsdom for hjemme-routere med WPS-on-by-default.

**Tal (2012):**

- **Global udbredelse:** WPA2 ~70%, WEP ~10%, åben ~15%, WPA ~5%.
- **WPS-PIN-space på papir:** 10⁸ = 100 millioner. **Effektiv** angrebs-space efter Viehböck-splittet: 10⁴ + 10³ = ~11.000 forsøg.
- **Reaver ur-tid til at gendanne WPS-PIN → PSK:** 2–10 timer mod en upatched AP.
- **hashcat WPA-PSK throughput på GTX 580 (reference-GPU 2012):** ~75.000 kandidater/sek.
- **hashcat WPA-PSK på en lille 4-GPU-rig fra æraen:** ~300.000 kandidater/sek, dvs. `rockyou.txt` (14,3 M) på ~50 sekunder.
- **Virkelig PSK-gendannelsesrate med rockyou + almindelige regler:** ~20–25% på fangede handshakes i akademiske studier.
- **WPA2-PEAP/MSCHAPv2-hashrate (et Wi-Fi-tilstødende Enterprise-problem):** titusinder af millioner/sek på en enkelt GPU, fuldt 2²⁸-keyspace inden for et døgn.

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

**Tal (2017–2018):**

- **Global udbredelse:** WPA2 ~85%, WEP <3%, åben ~10%, WPA3 endnu ikke leveret.
- **KRACK CVE'er:** 10 i den koordinerede offentliggørelse (CVE-2017-13077 til CVE-2017-13088).
- **KRACK-berørte enheder:** alle WPA2-klienter og AP'er — **10+ milliarder** endpoints. Reel patching tog år for long-tail-IoT.
- **Patch-latency hos leverandører:** Microsoft / de fleste Linux-distroer inden for 1 uge fra disclosure; Android 2+ måneder afhængigt af OEM; mange embedded-enheder blev aldrig patchet.
- **PMKID-angrebets pakke-antal:** **1 enkelt frame** mod 4-way-handshakens 4 frames — ingen klient-association eller deauth nødvendig.
- **hashcat på GTX 1080 (reference-GPU 2017):** ~400.000 WPA-PSK-kandidater/sek — ~5× hurtigere end 2012.
- **En lejet 8× 1080 Ti-instans (~$4/t i 2017):** ~3M kandidater/sek — `rockyou.txt` på <5 sekunder.
- **Koordineret disclosure-forløbstid:** 4 måneder fra leverandør-notificering til offentlig release.

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

**Tal (2022):**

- **Global udbredelse:** WPA2-only ~60%, WPA3 ~20%, WPA2/3-transition-mode ~15%, WEP <1%.
- **WPA3-understøttelse på nye routere:** ~60% af forbruger-AP'er leveret i 2022 understøttede WPA3 (vs. ~10% i 2020).
- **Dragonblood CVE'er:** 5 (CVE-2019-9494 til CVE-2019-9499).
- **FragAttacks CVE'er:** 12 i 2021-bundlet.
- **hashcat WPA-PSK på RTX 3090:** ~1,2M kandidater/sek.
- **8× A100-cloud-instans:** ~10M kandidater/sek samlet. `rockyou.txt` på ~1,5 sekund; et 10 mia.-kandidats mask-angreb på ~17 minutter.
- **Pris pr. milliard PSK-forsøg på spot-cloud-GPU'er:** ~$3–5.
- **12-tegns fuldt tilfældig PSK-entropi:** 2⁷² ≈ 4,7 × 10²¹. Ved 10M H/s er udtømmende angreb = **~15.000 år**. Sikker.
- **8-tegns små-bogstav+ciffer PSK-entropi:** 2⁴¹ ≈ 2,2 × 10¹². Ved 10M H/s: **~2,5 døgn**. Ikke sikker.

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

**Tal (2027):**

- **Global udbredelse:** WPA3 ~40%, WPA2/3-transition ~35%, WPA2-only ~20%, WEP ~0,5% (lang hale af gammelt gear).
- **Enterprise-andel der kører WPA3-Enterprise 192-bit mode:** stadig <10%. De fleste corporate-netværk er stadig WPA2-Enterprise med PEAP.
- **Ny-enhed WPA3-certificering:** obligatorisk for Wi-Fi 6 siden 2020, Wi-Fi 6E (6 GHz) siden 2022, Wi-Fi 7 fra launch.
- **hashcat WPA-PSK på RTX 5090-klasse enkelt-GPU (2025+):** ~5–8M kandidater/sek.
- **8× H100-cloud-instans:** ~50M kandidater/sek samlet. `rockyou.txt` på ~0,3 sekund.
- **SAE (WPA3-Personal) offline-angreb:** ufremkommeligt ved enhver hash-rate — handshaken udleverer ikke en crackbar hash til en aflytter.
- **Pris for at brute-force en svag 8-tegns WPA2-PSK i 2027:** <$10 på spot-cloud-GPU'er.
- **Pris for at brute-force en 12-tegns tilfældig WPA2-PSK:** stadig ~$10⁹ (samme regnestykke som 2022, GPU'er 5× hurtigere → stadig årtusinder).
- **ESP32-S3 "Wi-Fi Nugget" / Flipper Zero-klasse lomme-værktøjer** i cirkulation i 2027: hundredtusinder af enheder. Opportunistisk handshake-capture er trivielt; PSK-cracking er stadig offline på en kraftig host.
- **Deauth-DoS-effektivitet:** nær-nul på PMF-required-netværk; virker stadig mod de ~30% af udrullede AP'er, hvor PMF er "capable", men ikke "required".

Bundlinje: mod **WPA3-Personal med SAE, PMF påkrævet og en tilfældig PSK** kommer intet af 2027-værktøjssættet ind via link-laget. Mod **en typisk 2019-vintage hjemme-router, der stadig kører WPA2 med en svag PSK og WPS valgfrit eksponeret**, er en weekend på en mellem-klasse-GPU rigeligt.

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
