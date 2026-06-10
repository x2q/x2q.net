+++
title = "Opdater Garmin-firmware og -kort i 2026 — fra WebUpdater til Garmin Express"
date = 2026-06-10
slug = "opdater-garmin-firmware-og-kort"
description = "Sådan opdaterer du firmware og kort på en Garmin-enhed i 2026 — også gamle nüvi-enheder. WebUpdater er for længst nedlagt; Garmin Express (kabel) og Garmin Connect (trådløst) har overtaget. Plus nüvi-debugmenuen."

[taxonomies]
tags = ["garmin", "garmin-express", "nuvi", "gps", "firmware", "kort", "navigation", "windows", "macos"]

[extra]
summary = "Den gamle måde at opdatere en Garmin på — WebUpdater — blev nedlagt for år tilbage. I 2026 bruger du Garmin Express (et skrivebordsprogram, kabelforbindelse) til firmware og kort på nüvi/DriveSmart-enheder, eller Garmin Connect til trådløse opdateringer på ure og nyere håndholdte. Her er den nuværende vej for hver, hvad du gør med meget gamle nüvi-enheder, og den skjulte nüvi-debugmenu."
faq = [
  { q = "Findes Garmin WebUpdater stadig?", a = "Nej. WebUpdater blev nedlagt omkring 2015 og erstattet af Garmin Express. Hvis du stadig har WebUpdater installeret, vil det fejle eller intet nyttigt gøre — afinstaller det og brug i stedet Garmin Express (skrivebord) eller Garmin Connect (mobil, trådløst)." },
  { q = "Hvordan opdaterer jeg en gammel Garmin nüvi?", a = "Installér Garmin Express på en Windows- eller Mac-computer, tilslut nüvi'en via USB, og lad Express finde den. Den viser tilgængelige firmware- og kortopdateringer. Bemærk, at mange ældre nüvi-enheder er uden for deres 'lifetime maps'-vindue eller helt udgået, så kortopdateringer tilbydes måske ikke længere, selvom firmwareopdateringer stadig gør." },
  { q = "Opdaterer jeg over Wi-Fi eller med kabel?", a = "Afhænger af enheden. nüvi og de fleste DriveSmart-navigatorer opdateres via USB-kabel gennem Garmin Express på en computer. Ure, cykelcomputere og nyere håndholdte opdateres trådløst gennem Garmin Connect på din telefon (Bluetooth/Wi-Fi). Nyere DriveSmart-modeller kan også opdatere over Wi-Fi uden computer." },
  { q = "Hvordan kommer jeg ind i nüvi-debug-/diagnosemenuen?", a = "Tænd enheden, og tryk og hold derefter nederste højre hjørne af berøringsskærmen i nogle sekunder. En diagnose-/testskærm dukker op (softwareversion, berøringsskærmstest, GPS-test osv.). Det er ufarligt at kigge på; lad være med at ændre kalibreringen, medmindre du ved, hvad du gør." }
]
+++

**Kort fortalt —** Hvis du søgte efter *Garmin WebUpdater* eller *hvordan opdaterer jeg Garmin-firmware*, er værktøjet, du husker, væk. **WebUpdater blev nedlagt (~2015)**; den nuværende vej er **Garmin Express** (et skrivebordsprogram, USB-kabel) til nüvi/DriveSmart-navigatorer, eller **Garmin Connect** (telefon, trådløst) til ure og nyere håndholdte. Dette indlæg dækker 2026-måden at opdatere **firmware og kort** på hver, hvad du gør med en gammel nüvi, og den skjulte **nüvi-debugmenu**.

## Dengang → nu: WebUpdater er død

I årevis opdaterede du en Garmin med **WebUpdater** — en lille skrivebordshjælper, der tjekkede for firmware. Garmin pensionerede den og samlede alt i to apps:

- **Garmin Express** — skrivebord (Windows/macOS), forbinder via **USB-kabel**. Det er det, der erstattede WebUpdater til navigatorer (nüvi, DriveSmart, Drive) og er også kabelvejen til ure/håndholdte og **kort**opdateringer.
- **Garmin Connect** — telefon-app (iOS/Android), opdaterer **trådløst** over Bluetooth/Wi-Fi. Det er vejen til ure (Forerunner, fēnix, Venu), cykelcomputere (Edge) og moderne håndholdte.

Hvis du stadig har WebUpdater installeret, så afinstallér det — det gør ikke længere noget nyttigt.

## Opdater en nüvi / DriveSmart-navigator (firmware + kort)

Det er tilfældet bag de fleste "opdater Garmin-firmware"-søgninger.

1. Hent **Garmin Express** fra [garmin.com/express](https://www.garmin.com/da-DK/software/express/) og installér det på en Windows- eller Mac-computer.
2. Tilslut enheden med et **USB-kabel** og tænd den. Vent på, at computeren genkender den som et drev.
3. Åbn Garmin Express. Den finder enheden og viser tilgængelige **software- (firmware)** og **kort**opdateringer.
4. Klik **Installér alle**, eller vælg enkelte opdateringer. Kortfiler er store (ofte flere GB) — lad den være tilsluttet, og afbryd ikke midt i.
5. Når den er færdig, så skub sikkert ud og frakobl. Enheden genstarter med den nye firmware.

**Kortopdateringer** vises også her. Hvis din enhed har **lifetime maps** ("LM"/"LMT" i modelnavnet), er opdateringer gratis i enhedens understøttede levetid. Ellers tilbyder Express et betalt kortkøb.

## Opdater et ur / Edge / nyere håndholdt (trådløst)

1. Installér **Garmin Connect** på din telefon, og parr enheden.
2. Connect henter opdateringer automatisk; du får en besked, når firmware er klar.
3. Hold enheden opladt og nær telefonen — den installerer og genstarter af sig selv.

For en kabelopdatering af disse enheder (eller hvis trådløst fejler) virker Garmin Express på en computer også.

## Meget gamle nüvi-enheder — hvad der stadig virker

Mange tidlige nüvi-modeller (2007–2012-æraen) er nu **udgået**: firmware kan måske stadig installeres via Garmin Express, men **kortopdateringer tilbydes ikke længere**, og lifetime-maps-dækningen er ophørt. Hvis Express viser "opdateret" med et gammelt kortår, er det som regel vejs ende — hardwaren understøttes simpelthen ikke med nye kortdata mere. Enheden virker fortsat med de kort, den har.

## Bonus: den skjulte nüvi-debugmenu

Et gammelt trick til at diagnosticere en ustabil nüvi: tænd den, og **tryk og hold nederste højre hjørne af berøringsskærmen** i nogle sekunder. En **diagnoseskærm** dukker op — softwareversion, kalibreringstest af berøringsskærm, GPS-signaltest, batteriinfo. Det er sikkert at se på; undgå at ændre berøringsskærmskalibrering, medmindre skærmen reelt er skæv.

## Opsummering

- **WebUpdater er nedlagt** — brug **Garmin Express** (skrivebord, USB) eller **Garmin Connect** (telefon, trådløst).
- **nüvi / DriveSmart**: Garmin Express over USB klarer både firmware og kort; "Installér alle".
- **Ure / Edge / håndholdte**: Garmin Connect opdaterer trådløst.
- **Lifetime maps** (LM/LMT-modeller) opdaterer gratis; meget gamle nüvi-enheder er udgået for nye kortdata.
- **nüvi-debugmenu**: hold nederste højre hjørne af skærmen efter opstart.
