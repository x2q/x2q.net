+++
title = "pdfcrack — gendan glemte PDF-kodeord på Linux og macOS (2026)"
date = 2026-04-22
slug = "gendan-pdf-kodeord-pdfcrack"
description = "Sådan bruger du pdfcrack til at gendanne et glemt kodeord på en beskyttet PDF. Installation, benchmark, dictionary vs brute-force og hvornår du skal skifte til pdf2john + hashcat til AES-256-PDF'er."

[taxonomies]
tags = ["pdfcrack", "pdf", "kodeord-gendannelse", "kodeord-cracking", "hashcat", "john-the-ripper", "linux", "macos", "sikkerhed"]

[extra]
summary = "pdfcrack er et lille, single-threaded CPU-værktøj til at gendanne glemte user- og owner-kodeord på PDF'er. Fin til 40-bit RC4 og små dictionary-angreb; til 128/256-bit AES-PDF'er skal du bruge pdf2john + hashcat på en GPU."
+++

**TL;DR —** **`pdfcrack`** er et kommandolinjeværktøj, der gendanner **user-kodeordet** eller **owner-kodeordet** på en krypteret PDF via brute-force eller dictionary-angreb. Det er lille, skrevet i C, kører på Linux/macOS/WSL og håndterer enhver krypterings-profil, PDF har leveret — 40-bit RC4, 128-bit RC4, 128-bit AES, 256-bit AES (PDF 1.7 + 2.0). Det er **single-threaded og kun CPU**, så det er hurtigt på den svage gamle RC4-40-kryptering, men stadig langsommere, efterhånden som PDF'er bliver moderne. Installeres med `apt install pdfcrack` (Debian/Ubuntu), `brew install pdfcrack` (macOS) eller bygges fra kilden. Når `pdfcrack` er for langsom, så skift til **`pdf2john` + `hashcat`** på en GPU.

Dette indlæg antager, at du **har autorisation til at gendanne kodeordet** på PDF'en — dit eget dokument, en kundes eller en lovligt anskaffet fil. Angrib ikke PDF'er, du ikke ejer.

## User-kodeord vs owner-kodeord

PDF har to kodeord:

- **User-kodeord** — kræves for at **åbne og læse** dokumentet.
- **Owner-kodeord** — kræves for at **fjerne begrænsninger** (print, kopi, rediger) på et dokument, der åbner uden et user-kodeord.

Mange "beskyttede" PDF'er er kun owner-kodeord-begrænsede: de åbner fint, men print og kopi er deaktiveret af læseren. Dem er trivielt at låse op — `qpdf --decrypt` eller et hvilket som helst `pdftk`-lignende værktøj fjerner owner-only-restriktioner uden at skulle gætte noget. `pdfcrack` er til det sværere tilfælde: en **user-kodeord-beskyttet PDF, du slet ikke kan åbne**.

Tjek hvilken du har med at gøre:

```
$ qpdf --show-encryption dokument.pdf
R = 6
P = -3904
User password = 
Supplied password is owner password
extract for accessibility: allowed
extract for any purpose: not allowed
print low resolution: allowed
print high resolution: not allowed
modify document assembly: not allowed
modify forms: not allowed
modify annotations: not allowed
modify other: not allowed
stream encryption method: AESv3
string encryption method: AESv3
file encryption method: AESv3
```

- **`R = ...`** fortæller dig revisionen/profilen. `R=2` = RC4-40, `R=3` = RC4-128, `R=4` = AES-128, `R=5/6` = AES-256.
- **"Supplied password is owner password"** + "User password = (tom)" betyder, du kan åbne den og bare skal fjerne restriktioner. Brug `qpdf --decrypt --password='' input.pdf output.pdf`, og du er færdig.

## Installation

```
# Debian / Ubuntu / Mint / Kali
sudo apt install pdfcrack

# macOS (Homebrew)
brew install pdfcrack

# Arch / Manjaro
sudo pacman -S pdfcrack

# Fedora / RHEL
sudo dnf install pdfcrack

# Fra kilden
wget https://sourceforge.net/projects/pdfcrack/files/latest/download -O pdfcrack.tar.gz
tar xf pdfcrack.tar.gz && cd pdfcrack-*
make
sudo cp pdfcrack /usr/local/bin/
```

## Benchmark

```
$ pdfcrack -b
Benchmark:	Average Speed (calls / second):
MD5:			1728972.6
MD5_50 (fast):		 97879.3
MD5_50 (slow):		 69167.0

RC4 (40, static):	606555.3
RC4 (40, no check):	598050.0
RC4 (128, no check):	590141.7

Benchmark:	Average Speed (passwords / second):
PDF (40, user):		453510.2
PDF (40, owner):	220250.0
PDF (40, owner, fast):	499995.0

PDF (128, user):	 22000.0
PDF (128, owner):	 10408.7
PDF (128, owner, fast):	 22220.0
```

Oversat:

- **RC4-40** (PDF 1.3, meget gammel) — ~450k kodeord/sek. Brute-force af et fuldt 8-tegns alfanumerisk space: ~1 uge på én core.
- **RC4-128 / AES-128** — ~22k kodeord/sek. Brute-force bliver urealistisk over længde 6 med et hvilket som helst charset.
- **AES-256 (R=5/6)** — endnu langsommere; `pdfcrack` understøtter det, men reelt kun til dictionary-angreb mod små ordlister.

Har du brug for mere fart end det, så vil du bruge `hashcat` på en GPU. Tal i bunden.

## Dictionary-angreb

```
pdfcrack -f dokument.pdf -w /usr/share/wordlists/rockyou.txt
```

- **`-f`** — målfil.
- **`-w <fil>`** — ordliste, én kandidat pr. linje.
- Valgfri **`-o`** — angrib kun owner-kodeord (ignorer user-kodeord). Default er at prøve user-kodeord først.
- Valgfri **`-u`** — angrib kun user-kodeord.

Har du kontekst — kodeordet er sandsynligvis et fornavn, et årstal, en projektkode — saml en mindre målrettet liste. Generiske lister er en lang skud, når du er forbi top ti tusind indgange.

## Brute-force-angreb

```
pdfcrack -f dokument.pdf -c 'abcdefghijklmnopqrstuvwxyz0123456789' -n 4 -m 8
```

- **`-c <charset>`** — tegnsæt at prøve. Default inkluderer et bredt ASCII-område.
- **`-n <min>`** — minimumslængde.
- **`-m <max>`** — maksimumslængde.

Juster `-c` aggressivt. Ved du, at kodeordet er alt-lowercase, så giv det ikke uppercase. Ved du, det har et ciffer til sidst, så brug et mask-angreb (hashcat-territorium, ikke pdfcrack).

## Genoptag et langt kørsel

```
pdfcrack -f dokument.pdf -w rockyou.txt -s /tmp/state.sav
```

`-s` skriver periodiske save-filer; hvis du stopper pdfcrack og genstarter, så giv `-l /tmp/state.sav` for at genoptage.

## Hvornår du skal skifte til hashcat

Til enhver moderne PDF (R=4, 5 eller 6 — altså AES-128 eller AES-256) bliver `pdfcrack`s single-core-fart flaskehalsen. `pdf2john` + `hashcat` giver dig to til tre størrelsesordener mere throughput på en GPU.

### Trin 1: træk hashen ud

```
$ /usr/share/john/pdf2john.pl dokument.pdf > hash.txt
```

(På Debian/Ubuntu: `apt install john` leverer `pdf2john.pl`.)

### Trin 2: identificér hash-mode

```
$ head -1 hash.txt
dokument.pdf:$pdf$5*6*256*-1028*1*16*...
```

Map de første to tal:

- `$pdf$1*2*...` → **mode 10400** (PDF 1.1–1.3, RC4-40, user)
- `$pdf$1*2*...` med owner-salt → **mode 10410 / 10420**
- `$pdf$2*3*...` → **mode 10500** (PDF 1.4–1.6, RC4-128 / AES-128)
- `$pdf$5*5*...` → **mode 10600** (PDF 1.7 r=5, AES-256)
- `$pdf$5*6*...` → **mode 10700** (PDF 1.7 r=6 / PDF 2.0, AES-256 med PBKDF2)

### Trin 3: kør hashcat

```
hashcat -m 10700 hash.txt /sti/til/ordliste.txt
```

På en enkelt moderne GPU (fx RTX 4090):

- **Mode 10400 (RC4-40):** ~10 milliarder H/s — ethvert praktisk kodeord gendannes øjeblikkeligt.
- **Mode 10500 (RC4-128 / AES-128):** ~100 millioner H/s.
- **Mode 10700 (AES-256, PBKDF2):** ~50.000 H/s. Det er ved design — PBKDF2-iterationerne gør brute-force dyrt.

For mode 10700 betyder din angrebsstrategi mere end rå fart. Dictionary + regler + mask-angreb målrettet mod sandsynlige kodeord-mønstre er størrelsesordener mere produktive end udtømmende brute-force.

## Almindelige faldgruber

### "Filen ser ud til at være krypteret, men jeg kan åbne den uden kodeord"

Du ser på owner-only-restriktioner. Brug `qpdf --decrypt input.pdf output.pdf` — ingen cracking nødvendigt.

### pdfcrack kører, men finder aldrig noget

Tre sandsynlige årsager:

1. **Kodeordet er længere / mere komplekst, end dit charset × længde dækker.** Øg `-m` og/eller udvid `-c`, eller skift til en dictionary.
2. **Kodeordet indeholder ikke-ASCII-tegn.** pdfcracks charset er ASCII som default; ikke-ASCII-user-kodeord i gamle PDF'er brugte varierende encodings (PDFDocEncoding, UTF-16). Prøv `pdf2john` + hashcat, som håndterer encoding'en korrekt.
3. **Det er AES-256 (R=6), og du er tålmodig.** Se hastighedsnoterne ovenfor — kun realistisk med en dictionary.

### "Only AES-256 is supported"-fejl eller lignende

Din `pdfcrack`-build er gammel. Ubuntu LTS leverer nogle gange en version, der ikke fuldt håndterer R=6. Byg fra kilden eller skift til `pdf2john` + `hashcat`.

### PDF'en åbner, men print/kopi er blokeret

Det er kun owner-kodeord-begrænset. `qpdf --decrypt` uden at behøve et kodeord virker som regel:

```
qpdf --decrypt --password='' input.pdf output.pdf
```

## Defensiv pointe

Til alt, du vil have til at forblive krypteret i 2026, brug **AES-256 med en PDF 2.0 (R=6) kodeord**. Det er profilen med PBKDF2-nøgle-afledning, der gør offline-angreb dyre på nuværende hardware.

Og som altid betyder kodeordets længde mere end noget andet. En 20-tegns tilfældig passphrase er brute-force-intraktabel mod enhver nuværende GPU. Et 6-tegns "smart substitutions"-kodeord er en kaffepause på en RTX 4090.

## Ofte stillede spørgsmål

### Er pdfcrack stadig vedligeholdt?

Opdateres langsomt. Kodebasen håndterer alle nuværende PDF-krypterings-profiler; det er bare ikke her, performance-arbejdet foregår længere (det er hashcat).

### Bruger pdfcrack GPU?

Nej. Kun CPU, single-threaded. Til GPU-arbejde, brug `pdf2john` + `hashcat`.

### Kan pdfcrack gendanne dokumentet, hvis skaberen ryddede user-kodeordet, men beholdt owner-kodeordet?

Ja — brug `qpdf --decrypt` først; hvis det ikke fuldt dekrypterer, angriber `pdfcrack -o` owner-kodeordet.

### Lækker pdfcrack min PDF nogle steder?

Nej. Den er lokal. Alt online-only ("crack min PDF på cloud-service-X.com") indebærer at uploade filen, hvilket du ikke skal gøre for fortroligt materiale.

### Hvad hvis jeg kun vagt husker kodeordet?

Skriv ned, hvad du husker — sandsynlige ord, sandsynlige cifre, sandsynlig længde — og byg en målrettet ordliste eller et `hashcat`-mask (`-a 3 ?l?l?l?l?l?d?d?d?d`). Det slår enhver generisk liste.

### Kan jeg gendanne tekst fra en AES-256-PDF uden kodeordet?

Nej. AES-256 med PBKDF2 (R=6) er, så vidt offentlig kryptanalyse går, ikke brudt. Hvis kodeordet er stærkt og tabt, er indholdet tabt.

## Opsummering

- **Kun owner-kodeord?** `qpdf --decrypt`, ingen cracking nødvendigt.
- **User-kodeord-beskyttet, gammel (R=2/3)?** `pdfcrack` med en dictionary virker fint.
- **Moderne (R=4/5/6)?** `pdf2john` + `hashcat` på en GPU, målrettet angreb.
- **Stærk 20-tegns tilfældig?** Accepter tabet.
