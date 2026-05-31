+++
title = "Sammensætning af drone-panoramaer: OpenCV vs Hugin, benchmarket"
date = 2026-05-31
slug = "drone-panorama-stitching-opencv-vs-hugin"
description = "63 DJI Phantom 4 Pro-billeder omdannet til panoramaer på to måder — OpenCVs automatiske Stitcher og Hugins kommandolinje-pipeline — og resultaterne benchmarket på kvalitet, hastighed og synsfelt."

[taxonomies]
tags = ["panorama", "drone", "dji", "hugin", "opencv", "enblend", "fotogrammetri", "exiftool", "imagemagick", "linux"]

[extra]
summary = "63 DJI Phantom 4 Pro-billeder over Randers, to pipelines. OpenCVs Stitcher er hurtig og automatisk, men giver bølget horisont og flossede kanter; Hugin + enblend er langsommere, men giver knivskarp lige horisont, sømløs overgang og et rent rektangel. Hugin vinder."
+++

**TL;DR —** Jeg havde en mappe med 63 DJI Phantom 4 Pro-billeder taget over Randers og ville lave panoramaer ud af dem. Jeg sammensatte de samme sweeps på to måder: **OpenCVs `Stitcher`** (fuldautomatisk, sfærisk) og **Hugins kommandolinje-pipeline** (`cpfind` → `autooptimiser` → `nona` → `enblend`). OpenCV er hurtig (få sekunder) og beholder det bredeste synsfelt, men horisonten bliver bølget, kanterne flossede, og eksponeringssømmene er synlige. Hugin tager ~30 s pr. panorama, men giver en **lige horisont, sømløs multi-band-overgang og et rent rektangulært beskåret billede**. Til alt, du vil printe eller udgive, vinder Hugin. Alle kommandoer og en benchmark-tabel nedenfor.

## Udgangspunktet

En mappe, 63 filer, `DJI_0029.jpeg` til `DJI_0091.jpeg`, ~15 MB hver, 5464 × 3070 px. Ingen flylog, ingen projektfil, og — som det viste sig — det meste af de brugbare metadata fjernet. Bare JPEG-filer og en enlig `result.jpg` fra et tidligere forsøg.

Første opgave: finde ud af *hvad disse billeder egentlig er*, før jeg beslutter, hvordan de skal sammensættes. Er det et nadir-kortlægningsgitter? Ét enkelt rotations-panorama? Flere separate sweeps? Hver af dem sammensætter man forskelligt.

## At regne optagelsen ud fra metadata

Ingen `exiftool` på maskinen, så:

```bash
sudo apt-get install -y libimage-exiftool-perl imagemagick
```

DJI skriver normalt gimbal-yaw/pitch/roll ind i et XMP-namespace, som ville fortælle mig præcis, hvordan kameraet pegede for hvert billede. Her var det fjernet — filerne var tydeligvis blevet re-eksporteret på et tidspunkt (hvilket også forklarer den root-ejede `result.jpg`). Det, der overlevede, var GPS og tidsstempler:

```bash
exiftool -n -T -FileName -GPSLatitude -GPSLongitude -GPSAltitude \
  -SubSecDateTimeOriginal DJI_*.jpeg
```

To ting sprang straks i øjnene.

**Der var to sessioner, 90 minutter fra hinanden:**

- `0029`–`0054`, taget 09:01–09:15
- `0055`–`0091`, taget 10:31–10:36

**Den anden session var en stak vandrette sweeps i stigende højde.** GPS-positionen flyttede sig næsten ikke, mens højden steg i tydelige bånd — 169 m, så 221 m, så 240 m, så 269 m. Det er signaturen på en drone, der svæver på stedet og panorerer kameraet hen over horisonten i hver højde. Hvert højdebånd er ét panorama.

Et hurtigt kontaktark bekræftede det:

```bash
ls DJI_*.jpeg | sed 's/.jpeg//' | xargs -P4 -I{} \
  convert {}.jpeg -resize 260x -gravity South -background black \
  -splice 0x16 -pointsize 13 -fill yellow -annotate +0+1 '{}' /tmp/thumbs/{}.png
montage /tmp/thumbs/DJI_00{55..91}.png -tile 6x -geometry +3+3 /tmp/sheet.png
```

Session ét viste sig at være blandet — billeder lige ned på en enkelt ejendom i forskellige højder (en lodret zoom-sekvens, ikke et panorama) plus nogle skrå nabolagsoptagelser. Så jeg fokuserede panoramaerne på session to's sweeps, som tydeligvis var det, dronen var der for at fange.

De grupper, jeg endte med:

| Gruppe | Billeder | Højde | Indhold |
|---|---|---|---|
| A | 0055–0065 | ~169 m | Villakvarter, lav panorering |
| B | 0066–0076 | ~221 m | By |
| C+D | 0077–0091 | 240–269 m | Høj skyline |

## Teknik 1 — OpenCV Stitcher

Vejen med mindst modstand. OpenCV leverer en `Stitcher` på højt niveau, der klarer feature-detektion, matchning, bundle adjustment, warping og blending i ét kald.

```bash
pip install opencv-contrib-python numpy
```

```python
import cv2, glob

imgs = [cv2.imread(f) for f in sorted(glob.glob("group_A/*.jpg"))]
stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)   # sfærisk model
status, pano = stitcher.stitch(imgs)
if status == cv2.Stitcher_OK:
    cv2.imwrite("A_opencv.jpg", pano)
```

To tilstande er vigtige:

- **`PANORAMA`** antager, at kameraet roterede om sit optiske centrum (sfærisk warp). Korrekt for disse svæv-og-panorer-sweeps.
- **`SCANS`** antager en affin/translatorisk model (flatbed-scanninger, nadir-kortlægning). Jeg prøvede den for fuldstændighedens skyld; den er den forkerte model her og reducerede de fleste sweeps til to-tre billeder. Brug den ikke til roterende luftoptagelser.

Jeg kørte alt på et 2400 px-arbejdssæt først — fuld opløsning er langsom at iterere på, og man vil gerne se, om en gruppe overhovedet hænger sammen, før man bruger minutter på den.

**Dom over OpenCV:** den bare virker, med nul parametre, på sekunder. Gruppe A — elleve billeder — blev til et 10433 × 1595-panorama på cirka 5 sekunder. Hagen er resultatet: en **bølget horisont**, **flossede revne kanter**, man selv skal beskære, og **svage eksponeringssømme**, hvor billeder mødes. Fint til et hurtigt kig; ikke noget, man printer.

## Teknik 2 — Hugin-pipelinen

[Hugin](https://hugin.sourceforge.io/) er open source-panoramaværktøjet, og afgørende er hele dets motor scriptbar fra kommandolinjen — ingen GUI nødvendig.

```bash
sudo apt-get install -y hugin-tools enblend enfuse
```

Pipelinen, trin for trin:

```bash
pto_gen      -o p.pto  DJI_0055.jpeg ... DJI_0065.jpeg   # 1. projekt fra EXIF
cpfind --multirow -o p.pto p.pto                          # 2. find kontrolpunkter
cpclean      -o p.pto p.pto                               # 3. fjern dårlige matches
autooptimiser -a -m -l -s -o p.pto p.pto                  # 4. optimér + ret horisont
pano_modify --canvas=AUTO --crop=AUTO --projection=2 \
             -o p.pto p.pto                               # 5. cylindrisk + auto-beskær
nona  -m TIFF_m -z LZW -o remap p.pto                     # 6. remap hvert billede
enblend -o pano.tif remap*.tif                            # 7. multi-band-overgang
```

Hvad hvert trin giver dig ud over OpenCV-onelineren:

- **`cpfind --multirow`** finder ordentlige kontrolpunkter på tværs af hele sættet — den rapporterede 250, 302 og 718 punkter for gruppe A, B og C+D.
- **`autooptimiser -l -s`** retter horisonten og opretter panoramaet. Det er den største synlige gevinst: bølgen forsvinder.
- **`--projection=2`** er cylindrisk, hvilket holder horisonten som en lige vandret linje — præcis hvad man vil have til et bredt luft-sweep.
- **`--crop=AUTO`** beskærer til det største rene rektangel, så ingen manuel beskæring.
- **`enblend`** laver multi-band (Burt–Adelson)-blending, som skjuler de eksponeringsforskelle mellem billeder, OpenCV efterlod synlige.

Samme gruppe, to pipelines, stablet — OpenCV øverst, Hugin nederst:

![OpenCV Stitcher vs Hugin på det samme by-sweep. OpenCV efterlader en bølget horisont og revne kanter; Hugin giver et lige, sømløst rektangel.](/img/drone-panorama/compare-cv-vs-hugin.avif)

Forskellen er ikke subtil.

## Benchmarken

Samme inputgrupper, begge pipelines. OpenCV-tallene er 2400 px-arbejdssættet; Hugin-tallene er de endelige kørsler i fuld opløsning på 5464 px.

| Gruppe | Billeder | Værktøj | Resultat | Tid | Horisont | Overgang | Beskæring |
|---|---|---|---|---|---|---|---|
| A · villakvarter | 11 | OpenCV PANORAMA | 10433 × 1595 | 5 s | bølget | sømme | flosset |
| A · villakvarter | 11 | **Hugin + enblend** | 11581 × 1827 | 31 s | **lige** | **sømløs** | **ren** |
| B · by | 11 | OpenCV PANORAMA | 10295 × 1838 | 11 s | bølget | sømme | flosset |
| B · by | 11 | **Hugin + enblend** | 8190 × 2547 | 30 s | **lige** | **sømløs** | **ren** |
| C+D · skyline | 15 | OpenCV PANORAMA | 8660 × 1975 | 2 s | bølget | sømme | flosset |
| C+D · skyline | 15 | **Hugin + enblend** | 22469 × 2391 | 60 s | **lige** | **sømløs** | **ren** |

OpenCV er 3–10× hurtigere og beholder typisk et bredere synsfelt (den warper og beholder de revne kanter i stedet for at beskære dem). Hugin er langsommere, men vinder på hver kvalitetsakse, der betyder noget for et færdigt billede.

## Op i fuld opløsning

Da Hugin var den klare vinder, kørte jeg den igen på de originale 5464 px-billeder. Pipelinen er identisk — peg bare `pto_gen` på de originale JPEG-filer i stedet for det nedskalerede sæt. `cpfind` og `enblend` er de langsomme trin ved fuld opløsning, men det lå stadig omkring 30 s pr. panorama, et minut for skyline-billedet med 15 frames.

De færdige panoramaer:

**Den høje skyline — femten billeder, 22469 × 2391, et næsten 180° sweep hen over hele byen:**

![Randers skyline-panorama, fuldt sweep, sammensat med Hugin og enblend.](/img/drone-panorama/skyline-hugin.avif)

**Villakvarter-sweepet i 169 m:**

![Villakvarter-panorama i 169 m, Hugin.](/img/drone-panorama/residential-hugin.avif)

**Byen i 221 m:**

![By-panorama i 221 m, Hugin.](/img/drone-panorama/town-hugin.avif)

Ved 22469 px bredde kan skyline-billedet uden problemer printes i storformat.

## FAQ

### Hvorfor betød metadataene så meget — hvorfor ikke bare smide alle 63 ind i stitcheren?

Det kan man godt, og OpenCV vil forsøge at finde sammenhængende komponenter. Men filerne var to urelaterede sessioner plus en blanding af nadir- og skråbilleder. At fodre det hele ind risikerer, at optimeringen forbinder billeder, der ikke bør hænge sammen, eller spilder minutter på at fejle. Fem minutter med `exiftool` til at gruppere billederne først sparede en masse gætteri — og fortalte mig, *hvilke* grupper der overhovedet var panoramaer.

### Hvorfor ikke bare bruge dronens indbyggede panorama-funktion?

Disse var ikke taget som in-camera-panoramaer — det er enkeltbilleder fra manuelle sweeps, og den indbyggede sammensætning (hvis den overhovedet kørte) er den lavopløselige `result.jpg`, jeg fandt i mappen. At sammensætte fra de originale fuldopløselige billeder giver langt mere detalje end in-camera-JPEG'en.

### Hvad med PTGui / Lightroom / Microsoft ICE?

Alle dygtige. PTGui er i bund og grund kommerciel Hugin og fremragende. Lightrooms Photo Merge er praktisk, hvis du allerede er derinde. Microsoft ICE var god, men er udgået. Jeg ville have en scriptbar, gratis, Linux-native pipeline, jeg kunne køre headless over en mappe — det er Hugin.

### Cylindrisk, sfærisk eller rektilineær?

Til et bredt vandret sweep holder **cylindrisk** (`--projection=2`) horisonten lige og håndterer >120° uden den ekstreme strækning, rektilineær giver i kanterne. Sfærisk (det OpenCVs `PANORAMA` bruger) er også fint, men har tendens til at bue horisonten, medmindre pitchen er godt estimeret — hvilket er sværere her, fordi gimbal-vinklerne var fjernet.

### Kan det køre uovervåget over en hel mappe?

Ja — hele Hugin-vejen er CLI, så den passer direkte ind i et shell-script eller en `Makefile`. Gruppér billederne (efter tidsstempel/højde, eller lad bare `cpfind` finde sammenhængende komponenter), og loop så de syv kommandoer pr. gruppe. Det er det egentlige argument for Hugin frem for et GUI-værktøj her.

## Dom

Vil du have et panorama *nu* og er ligeglad med en bølget horisont eller selv at trimme kanter, er OpenCVs `Stitcher` en fem-sekunders oneliner og oprigtigt imponerende for indsatsen.

Til alt, du beholder — print, udgivelse, på væggen — er **Hugins kommandolinje-pipeline** det ekstra halve minut værd. En lige horisont, en sømløs overgang og en automatisk ren beskæring er præcis de ting, der adskiller et snapshot fra et færdigt panorama, og Hugin leverer alle tre gratis. Det er nu mit standardvalg til at sammensætte alt fra dronen.

Det hele — fra installation til færdige fuldopløselige panoramaer — tog cirka en time, det meste brugt på at forstå billederne frem for at sammensætte dem. Hvilket som regel er sådan, det går.
