+++
title = "bchunk — konverter .bin/.cue-images til .iso og .wav på Linux og macOS"
date = 2026-04-22
slug = "bchunk-bin-cue-til-iso-wav"
description = "Sådan bruger du bchunk (binchunker) til at splitte et .bin/.cue-cd-image op i et rigtigt .iso-datasport og .wav-lydspor. Virker på Linux, macOS (Homebrew) og WSL."

[taxonomies]
tags = ["bchunk", "binchunker", "bin-cue", "iso", "cd-image", "linux", "macos", "homebrew", "audio-cd"]

[extra]
summary = "bchunk (binchunker) deler et .bin/.cue-cd-image op i .iso for datasporet og .wav-filer for hvert lydspor. Det kanoniske værktøj til at lave en mixed-mode BIN/CUE om til noget, du kan mounte eller brænde."
+++

**TL;DR —** **`bchunk`** — også kaldet **`binchunker`** — er et lille, gammelt Unix-kommandolinjeværktøj, der tager et `.bin`/`.cue`-par (et råt cd-image med et cue-sheet) og deler det op i en rigtig **`.iso`-fil til datasporet** og én **`.wav`-fil pr. lydspor**. Det er det rigtige værktøj, når et download eller arkiv har givet dig `game.bin` + `game.cue`, og du faktisk vil **mounte datasporet** eller **brænde lydsporene** igen. Installeres med `apt install bchunk` på Debian/Ubuntu, `brew install bchunk` på macOS eller bygges fra kilden på alt andet. Brug er `bchunk [options] image.bin image.cue basename` — du får `basename01.iso`, `basename02.wav`, `basename03.wav` osv.

## Hvad .bin/.cue er, og hvorfor du vil splitte det

Et `.bin`/`.cue`-par er et **råt, bit-nøjagtigt cd-image** plus et klartekst-sheet, der beskriver sporenes layout. `.bin` indeholder hver sektor af cd'en i rækkefølge — inklusive datasport (Mode 1 eller Mode 2), lydspor (rå Red Book PCM, 2352 bytes pr. sektor, intet filsystem) og pauserne imellem dem. `.cue` fortæller, hvor hvert spor begynder, og hvilken type det er.

Formatet er standard-output for cd-ripning-værktøjer som cdrdao og for gamle spil-arkiver, fordi det bevarer *alt* — pregaps, CD-TEXT, mixed-mode-cd'er, CD-DA-lyd. Det er også grunden til, at du ikke bare kan omdøbe `game.bin` til `game.iso` og mounte det: en mixed-mode-cd har **ikke-filsystem-sektorer** i starten, lydspor der slet ikke er filsystem, og per-sektor-headers, som ISO forventer fjernet.

`bchunk` laver konverteringen rigtigt:

- **Datasport** bliver til ISO 9660-filer (`.iso`) — 2352-byte cd-sektorer bliver trimmet til 2048-byte ISO-sektorer, headers smidt væk.
- **Lydspor** bliver til 16-bit stereo 44,1 kHz `.wav`-filer, hver med en ordentlig WAV-header.

Derefter kan du `mount -o loop` `.iso`'en, afspille `.wav`'erne eller fodre dem til en brænder.

## Installation

### Debian / Ubuntu / Mint

```
sudo apt install bchunk
```

### macOS (Homebrew)

```
brew install bchunk
```

### Arch / Manjaro

```
sudo pacman -S bchunk
# eller fra AUR: yay -S bchunk
```

### Fedora / RHEL / CentOS

`bchunk` er ikke i standard-repoet; hent det fra RPMFusion eller byg fra kilden:

```
git clone https://github.com/hessu/bchunk.git
cd bchunk
make
sudo cp bchunk /usr/local/bin/
```

### Windows

Brug WSL og `apt install bchunk`. Der findes en gammel native port, men WSL er nemmere.

## Grundlæggende brug

```
bchunk game.bin game.cue game
```

Output:

```
game01.iso    # datasport, mountbart som ISO 9660
game02.wav    # lydspor 1
game03.wav    # lydspor 2
...
```

`basename` (`game` i eksemplet) er præfikset for hver output-fil. Spornumre starter ved `01`.

## Nyttige options

`bchunk` har et lille, stabilt sæt flag — de fleste er der for at håndtere specifikke cd-særheder.

- **`-v`** — verbose. Printer hvert spor, efterhånden som det behandles. Brug den første gang, du kører det, for at bekræfte, at du får det sporlayout, du forventer.
- **`-w`** — skriv `.wav`-filer (default). Eksplicit form.
- **`-r`** — rå lydoutput i stedet for `.wav`. Nyttigt hvis du piper ind i `sox` eller `ffmpeg` og ikke vil have et ekstra header-skrællende skridt.
- **`-p`** — **Psx/PlayStation-mode**. Behandler Mode 2-sektorer mere løst — nødvendigt for mange PlayStation-cd-images, hvor cue-sheetet er upræcist.
- **`-s`** — byt byte-rækkefølge på lydspor. Nødvendigt hvis `.bin`'en er produceret af en ripper, der skrev little-endian-lyd, hvor `bchunk` forventer big-endian (eller omvendt). Symptom: output-`.wav` lyder som hvid støj.
- **`-W`** — skriv `.wav` med en verificeret (i stedet for beregnet) header-størrelse. Sjældent nødvendigt.
- **`-E`** — brug de nøjagtige spor-grænser fra cue-sheetet i stedet for at prøve sig frem. Brug dette hvis lydspor lyder klippet i starten eller slutningen.

## Mount af den resulterende .iso

På Linux:

```
sudo mkdir /mnt/cd
sudo mount -o loop game01.iso /mnt/cd
ls /mnt/cd
```

På macOS:

```
hdiutil attach game01.iso
```

## Almindelige faldgruber

### "Illegal or unsupported track type" eller tomt output

Dit cue-sheet er malformet eller refererer til en `.bin`-størrelse, der ikke matcher. Åbn `.cue`'en i en teksteditor — den er klartekst — og tjek:

- `FILE "..."`-linjen peger på det rigtige `.bin`-filnavn, case-sensitivt.
- `TRACK`-entries er nummereret sekventielt med typerne `MODE1/2352`, `MODE2/2352` eller `AUDIO`.
- Index-entries (`INDEX 00`, `INDEX 01`) er MM:SS:FF, hvor FF er frames (0–74).

### Lydspor lyder som statisk

Byte-rækkefølge-mismatch. Prøv igen med `-s`:

```
bchunk -s game.bin game.cue game
```

### Enkelt `.iso` er fin, men lydspor er stille eller afkortede

Prøv `-E` for at tvinge cue-sheet-eksakte grænser:

```
bchunk -E game.bin game.cue game
```

### PlayStation/PSX-image splitter ikke rent

Brug `-p`:

```
bchunk -p psx.bin psx.cue psx
```

Det er den mest almindelige klage på fora — PSX-cues er næsten altid Mode 2, og `bchunk` uden `-p` er streng overfor dem.

### Flere `.bin`-filer refereret i cue-sheetet

Nogle rippere producerer én `.bin` pr. spor plus et samlende cue-sheet. `bchunk` forventer én `.bin` for hele skiven. Concatener dem først med `cat track01.bin track02.bin ... > combined.bin` og peg et single-file-cue på `combined.bin`.

## Alternativer værd at kende

- **`cdemu`** — user-space cd-emulator til Linux. Kan mounte en `.bin`/`.cue` direkte uden at splitte. Nyttigt, hvis du bare vil *læse* datasporet midlertidigt.
- **`ecm-tools`** — andet format (`.ecm`), men samme problemområde. Værd at kende, hvis du støder på det.
- **`7z` / `p7zip`** — nyere 7-Zip-versioner kan liste og uddrage ISO 9660-datasport fra en rå `.bin`, men kan ikke redde lyd som `.wav`.
- **`ffmpeg`** — hvis du vil have MP3 / FLAC / Opus i stedet for `.wav`, pipe rå-outputtet: `bchunk -r game.bin game.cue game && ffmpeg -f s16be -ar 44100 -ac 2 -i game02.raw game02.flac`.

## Hvorfor det stadig er nyttigt i 2026

Optisk-medie-imaging har været et løst problem i årtier, men `.bin`/`.cue` er stadig default-output fra `cdrdao`, stadig det gamle arkiver er lagret som, og stadig det, der dukker op, når nogen rækker dig en cd-backup, der ikke er en ISO. `bchunk` er et ~1.000-liniers C-program, skrevet i sen-1990'erne, der gør ét job korrekt og knap har ændret sig i tyve år. Det er i alle store distributioner, det kompilerer rent på moderne systemer, og det er det rigtige værktøj.

Hvis du prøver at redde data fra et gammelt cd-image: start her.
