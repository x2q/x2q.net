+++
title = "Sådan afspiller du Spotify på en Logitech Squeezebox i 2026"
date = 2026-04-22
slug = "squeezebox-spotify-guide-dansk"
description = "Spotify på Squeezebox Classic, Touch, Boom og Radio i 2026 — via Logitech Media Server, Spotty-plugin'et og spotifyd som bro. Virker uden det nedlagte officielle plugin."

[taxonomies]
tags = ["squeezebox", "spotify", "logitech-media-server", "lms", "spotty", "spotifyd", "lyd", "hjemme-server"]

[extra]
summary = "Det officielle Spotify-plugin til Squeezebox har været i stykker i årevis. Her er det, der faktisk virker i 2026: Logitech Media Server + Spotty-plugin'et, eller spotifyd som Spotify Connect-bro ind i LMS."
+++

**TL;DR —** Det officielle Spotify-plugin, Logitech leverede med Squeezebox, holdt op med at virke, da Spotify lukkede `libspotify`-API'en i 2022. I 2026 er der to fungerende veje til at få **Spotify på en Squeezebox Classic, Touch, Boom, Radio eller Transporter**: (1) **Logitech Media Server + [Spotty-plugin'et](https://github.com/michaelherger/Spotty-Plugin)** (nu omdøbt `Spotty` / nogle gange `Spotty-XL`), der bruger Spotifys Web API plus `librespot` under motorhjelmen, eller (2) kør **[spotifyd](https://github.com/Spotifyd/spotifyd)** på samme host som LMS og peg LMS på den som generisk lydkilde. Vej 1 er den, du vil bruge, medmindre du har en grund til andet. Dette indlæg gennemgår den.

## Hvad skete der med det officielle plugin

Squeezebox-hardware gik end-of-life hos Logitech i 2012, men softwaren — **Logitech Media Server (LMS)**, det der faktisk streamer musik til enhederne — er blevet community-vedligeholdt siden. I årevis leverede den et officielt "Spotify"-plugin, der brugte Spotifys nu udfasede `libspotify` C-bibliotek. Da Spotify lukkede `libspotify` i 2022, holdt det plugin op med at virke, og Spotify har ikke leveret en erstatning til tredjeparts-indbyggede enheder.

Community'et udfyldte hullet:

- **`librespot`** — en open-source Rust-reimplementering af Spotify Connect-klientprotokollen. Grundlaget for de fleste moderne tredjeparts-Spotify-integrationer.
- **Spotty-plugin til LMS** — pakker `librespot` og Spotifys Web API ind i et LMS-plugin. Præsenterer Spotify-browsing, søgning, playlister og afspilning inde i Squeezebox-UI'et (både enheds-skærmen og LMS-web-UI'et).
- **spotifyd** — en selvstændig `librespot`-baseret dæmon, der fremstår som et Spotify Connect-mål. Din telefon ser den som en højttaler, du caster til den, og dens lydudgang går et sted hen, hvor LMS kan samle det op.

## Vej 1 (anbefalet): Spotty-plugin på LMS

Dette er den reneste oplevelse og den, der føles native på Squeezeboxen. Du søger og browser fra Squeezebox-fjernbetjeningen eller Touch-skærmen, og det Virker Bare.

### 1. Få LMS op at køre

Hvis du ikke allerede kører LMS, så installér det på en altid-tændt maskine — en Raspberry Pi, et NAS med Docker eller en lille Linux-boks er ideelt.

```
# Debian/Ubuntu — hent den nyeste .deb fra community-repoet
wget https://downloads.slimdevices.com/LogitechMediaServer_v8.x/logitechmediaserver_<latest>_amd64.deb
sudo apt install ./logitechmediaserver_<latest>_amd64.deb
sudo systemctl enable --now logitechmediaserver
```

Eller via Docker — `lmscommunity/logitechmediaserver` er et vedligeholdt image:

```
docker run -d --name lms \
  --network host \
  -v lms-config:/config \
  -v /sti/til/musik:/music:ro \
  lmscommunity/logitechmediaserver:latest
```

Åbn `http://<host>:9000/`, og du skulle se LMS-web-UI'et. Dine Squeezebox-enheder på samme LAN skal dukke op under **Players** automatisk.

### 2. Installér Spotty

I LMS-web-UI'et: **Settings → Plugins → Install new plugins** og kryds **Spotty** af (forfatter: Michael Herger). LMS henter, installerer og genstarter. Efter genstart har du et **Spotty**-punkt i **Settings → Advanced → Spotty**.

### 3. Autoriser Spotty med din Spotify-konto

- I **Settings → Advanced → Spotty** klik **Add account**.
- Spotty starter et OAuth-flow via Spotifys Web API — du logger ind én gang i en browser, godkender adgangen, og tokenet gemmes på LMS-serveren.
- Du skal bruge **Spotify Premium** til afspilning. (Det er en Spotify-side-grænse: `librespot` kan autentificere med Free, men fuld-kvalitets-afspilning er kun til Premium.)

### 4. Afspil noget

På selve Squeezebox-enheden: **Home → My Music → Spotty** (eller **Home → Music Library → Spotty**, afhængigt af din LMS-version) — browsing af playlister, søgning, start et nummer. På Squeezebox Touch virker artwork på skærmen. På Classic virker tekst-UI'et. På Radio og Boom styrer du det fra web-UI'et eller apps som [Squeeze Commander](https://squeeze-commander.com/) / [Squeezer](https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer).

Spotty tilføjer også Squeezebox-enheder som **Spotify Connect-mål** — det betyder, at du kan caste fra din telefon-Spotify-app til "Stue-Squeezeboxen" native, på samme måde som du ville caste til en Sonos eller en Google Home.

## Vej 2: spotifyd som Connect-bro

Brug denne, hvis Spotty ikke vil installere (gammel LMS-version, gammel Perl, mærkeligt OS) eller du specifikt vil have Spotify Connect-adfærd uden Spotty.

```
# Debian/Ubuntu
sudo apt install spotifyd
# eller fra kilden: cargo install spotifyd
```

Konfigurér `/etc/spotifyd.conf` med dine Spotify-credentials, en backend (`alsa`, `pulseaudio` eller `pipe`) og et enhedsnavn. Start dæmonen:

```
sudo systemctl enable --now spotifyd
```

Fra din telefon, cast til den `spotifyd`-navngivne enhed. Lyden kommer ud af hosten.

For at få den lyd ind i en Squeezebox, pipe `spotifyd` til en FIFO og afspil FIFO'en i LMS:

```
# spotifyd.conf
backend = "pipe"
device = "/var/run/spotifyd.pipe"
```

Tilføj derefter FIFO'en som en **File system music folder** i LMS og afspil den som en live-stream.

Det er klodset og har ~1 s forsinkelse i forhold til Spottys tætte integration. Brug det kun, hvis vej 1 ikke virker for dig.

## Virker på hvilke Squeezeboxe?

Spotty virker på alle Squeezebox-enheder, der taler med LMS:

- **Squeezebox Classic / Squeezebox v3** (tekstdisplay) — tekst-UI-browsing og afspilning.
- **Squeezebox Touch** — farvetouchskærm, artwork, hele UI'et.
- **Squeezebox Boom** — tekst-UI, samme som Classic.
- **Squeezebox Radio** — tekst-UI, indbygget højttaler.
- **Squeezebox Duet / Controller** — controllerens UI virker; afspilning går til Receiveren.
- **Transporter** — fuld understøttelse.
- **piCorePlayer / SqueezeLite på Pi** — ja, det er software-Squeezeboxe, og Spotty streamer fint til dem.

Så længe enheden kan forbinde til LMS, kan Spotty fodre den.

## Ofte stillede spørgsmål

### Skal jeg have Spotify Premium?

Ja, til afspilning. `librespot` (og dermed Spotty) kræver en Premium-konto for at afkode lyd. Spotify Free-konti kan autentificere, men kan ikke afspille.

### Virker "Squeezeboxen som Spotify Connect-højttaler"?

Ja, med Spotty installeret. Hver Squeezebox-player dukker op i Spotify-appens enhedsvælger som et Connect-mål.

### Virker hi-res / lossless?

Spotify tilbyder ikke selv lossless på standardplaner (Hi-Fi har været "kommer snart" i årevis). Spotty afspiller, hvad Spotify serverer — Ogg Vorbis 320 kbps på Premium — og Squeezeboxen håndterer det native.

### Gapless afspilning?

Ja, Spotty understøtter gapless.

### Går det i stykker, hvis Spotifys Web API ændrer sig?

Ja, lejlighedsvis — Spotify roterer jævnligt OAuth-scopes eller udfaser endpoints, og Spotty får en patch-release. Hold plugin'et opdateret.

### Kan jeg køre LMS på samme boks som mit NAS?

Absolut. LMS er let (~200 MB RAM, minimal CPU undtagen under bibliotek-scanninger). At køre det ved siden af Samba eller på en homelab-SBC er det almindelige setup.

### Er det det samme som "piCorePlayer"?

piCorePlayer er en lille Linux-distribution, der gør en Raspberry Pi til en Squeezebox-kompatibel player (via SqueezeLite). Den erstatter ikke LMS — du skal stadig bruge LMS som server. piCorePlayer + LMS + Spotty er en meget almindelig 2026-stak for folk, hvis oprindelige Squeezebox-hardware endelig døde.

## Hvad du gør, hvis din Squeezebox slet ikke vil forbinde til LMS

To ting at tjekke først:

1. **mDNS / multicast på tværs af dit netværk.** Moderne Wi-Fi-routere blokerer ofte multicast mellem SSID'er eller til kablede hosts. Sæt Squeezeboxen og LMS på samme subnet/VLAN med multicast tilladt.
2. **SlimProto-porten (3483/udp og 3483/tcp).** Det er det, Squeezeboxen bruger til at finde LMS. Ikke blokeret af noget fornuftigt, men værd at tjekke, hvis du kører en stram firewall.

Derudover er Squeezebox-community'et stadig aktivt — [forums.slimdevices.com](https://forums.slimdevices.com/) og [LMS Community GitHub](https://github.com/LMS-Community) er, hvor problemer bliver løst.

Squeezebox-hardware blev udfaset for femten år siden. Takket være LMS, Spotty og `librespot` afspiller den stadig Spotify bedre end de fleste "smarte højttalere", der sælges nye i 2026.
