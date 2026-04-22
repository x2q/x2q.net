+++
title = "fcrackzip — gendan glemte zip-kodeord på Linux, macOS og Windows (2026)"
date = 2026-04-22
slug = "gendan-zip-kodeord-fcrackzip"
description = "Sådan bruger du fcrackzip til at gendanne et glemt kodeord på en krypteret .zip-fil. Installation, brute-force, dictionary og hvornår du skal skifte til zip2john + hashcat."

[taxonomies]
tags = ["fcrackzip", "zip", "kodeord-gendannelse", "kodeord-cracking", "hashcat", "john-the-ripper", "linux", "macos", "sikkerhed"]

[extra]
summary = "fcrackzip er et lille, gammelt kommandolinjeværktøj, der gendanner kodeord på klassisk-ZipCrypto-krypterede .zip-filer. Brute-force eller dictionary, kører overalt, stadig nyttigt i 2026 — med hashcat/john som moderne opfølger, når det ikke er hurtigt nok."
+++

**TL;DR —** **`fcrackzip`** er et gratis, open-source kommandolinjeværktøj til at gendanne kodeordet på en krypteret `.zip`-fil. Det understøtter **brute-force** (over et bruger-defineret charset og længde) og **dictionary**-angreb, virker på Linux/macOS/WSL, og er det rigtige første værktøj, når du skal gendanne et glemt kodeord på en zip, du lovligt ejer. Det er kun hurtigt mod **klassisk ZipCrypto**-kryptering; til den nyere **AES-256**-zip-profil virker `fcrackzip` ikke — så skal du bruge `zip2john` + `hashcat` i stedet. Installeres med `apt install fcrackzip` (Debian/Ubuntu), `brew install fcrackzip` (macOS) eller bygges fra kilden.

Dette indlæg går gennem de praktiske tilfælde. Det antager, at du **har autorisation til at gendanne kodeordet** — dine egne filer, en kundes, en CTF. Brug det ikke på zips, du ikke ejer.

## Installation

```
# Debian / Ubuntu / Mint / Kali
sudo apt install fcrackzip

# macOS (Homebrew)
brew install fcrackzip

# Arch / Manjaro
sudo pacman -S fcrackzip

# Windows
# Brug WSL2 + Ubuntu og `apt install fcrackzip`.
# En native .exe findes, men er gammel — WSL er simplere.

# Fra kilden
git clone https://github.com/hyc/fcrackzip.git
cd fcrackzip && ./configure && make
sudo cp fcrackzip /usr/local/bin/
```

## Tjek først, hvilken kryptering din zip bruger

`fcrackzip` håndterer kun **klassisk ZipCrypto** (den originale, svage PKZIP-kryptering). Til moderne **AES-128 / AES-256**-zips (introduceret af WinZip 9 i 2003, nu default i nogle værktøjer) vil `fcrackzip` lydløst fejle i at finde kodeordet, uanset hvor længe du lader det køre.

Hurtigste tjek med `zipinfo`:

```
$ zipinfo -v arkiv.zip | head -40
```

Led efter `WinZip AES encryption, strength 3` (= AES-256). Ser du det, så spring til hashcat-sektionen.

Eller med `7z`:

```
$ 7z l -slt arkiv.zip | grep -i 'method\|encrypted'
Method = ZipCrypto Store          ← fcrackzip virker
Method = AES-256 Deflate          ← fcrackzip virker IKKE
```

## Grundlæggende brute-force

```
fcrackzip -v -b -c 'a1' -p aaaa -u arkiv.zip
```

- **`-v`** — verbose.
- **`-b`** — brute-force-mode.
- **`-c 'a1'`** — charset. `a` = små bogstaver `a–z`, `A` = store, `1` = cifre, `!` = printbare symboler. Kombiner: `'aA1!'` = alt printbart ASCII (94 tegn).
- **`-p aaaa`** — start-kodeord (definerer minimum-længde = 4 her).
- **`-u`** — rapporterer kun, hvis den dekrypterede fil "unzipper" rent (filtrerer falske positive — ZipCrypto har en lille CRC, som mange tilfældige kodeord passerer).

Længde: `-p aaaaa` starter ved 5 tegn. `fcrackzip` har ikke et `--max-length`-flag; det inkrementerer start-kodeordet gennem charsettet uendeligt, så **at lade det køre til "færdigt" ved længde 8 på det fulde printbare ASCII-charset er ca. 94⁸ ≈ 6×10¹⁵ kandidater** — ikke realistisk. Du afgrænser angrebet ved at vælge et rimeligt max charset + længde eller ved at bruge en dictionary.

## Dictionary-angreb

```
fcrackzip -v -D -u -p /usr/share/wordlists/rockyou.txt arkiv.zip
```

- **`-D`** — dictionary-mode.
- **`-p <fil>`** — ordliste-fil, én kandidat pr. linje.
- **`-u`** — verificér via unzip, som før.

`rockyou.txt` er den standard 14 M-indgange-ordliste, der leveres med Kali og er tilgængelig overalt. Har du kontekst om kodeordet (det er nogens navn + årstal, det er et projektkodenavn), så saml en mindre målrettet ordliste — hit-raterne er som regel meget højere end med en generisk liste.

## Hastighed og hvad du kan forvente

`fcrackzip` er single-threaded og CPU-bundet. På en moderne laptop ser du groft:

- **10–30 millioner ZipCrypto-forsøg pr. sekund pr. core** for et dictionary-angreb mod en typisk zip.
- Brute-force en anelse hurtigere pga. mindre streng-I/O.

Det gør den fin til:

- **Dictionary-angreb** mod en hvilken som helst rimelig ordliste.
- **Kort brute-force** (4–6 tegn alfanumerisk).

Det gør den uegnet til:

- **Længde 8+ med symboler** — du når aldrig i mål.
- **AES-256-zips** — forkert værktøj.

## Hvornår du skal skifte til hashcat

Hvis `fcrackzip` er for langsom, eller zip'en er AES-krypteret, så gå over til `hashcat`. Det er det general-purpose kodeord-cracking-værktøj, GPU-accelereret, og håndterer både ZipCrypto og AES-WinZip-hashes.

### Trin 1: træk hashen ud med `zip2john`

`zip2john` er en del af John the Ripper. Ubuntu: `apt install john`.

```
$ zip2john arkiv.zip > hash.txt
$ cat hash.txt
arkiv.zip:$zip2$*0*3*0*...*$/zip2$::arkiv.zip:hemmelig.pdf:/sti/til/arkiv.zip
```

### Trin 2: fodr den til hashcat

```
# ZipCrypto (mode 17200, 17210, 17220, 17225 afhængigt af komprimering)
hashcat -m 17200 hash.txt /sti/til/ordliste.txt

# AES-krypteret WinZip (mode 13600)
hashcat -m 13600 hash.txt /sti/til/ordliste.txt
```

På en enkelt moderne diskret GPU (fx RTX 4090) ser du:

- **ZipCrypto: ~5–10 milliarder H/s**
- **WinZip AES-256: ~10–50 millioner H/s** (meget langsommere, fordi AES er dyrt, og der er PBKDF2-iterationer involveret)

hashcats rule-engine, mask-angreb (`-a 3`) og combinator-mode (`-a 1`) gør den massivt mere fleksibel end `fcrackzip`. Til alt ikke-trivielt er den det rigtige værktøj.

## Almindelige faldgruber

### "PASSWORD FOUND!!!!: pw == abc", men `unzip` beder stadig om et kodeord

Du brugte ikke `-u`. fcrackzips CRC-tjek har falske positive. Kør igen med `-u` for at verificere kandidater mod et rigtigt dekomprimerings-forsøg.

### Forskellige filer i samme zip har forskellige kodeord

Klassisk PKZIP understøtter per-fil-kodeord. `fcrackzip` angriber én fil ad gangen; giv `-l <filnavn>` (eller lad den vælge den første krypterede) hvis du skal være specifik.

### fcrackzip finder kodeordet, men jeg kan stadig ikke unzippe

Charset/locale-problem. Hvis kodeordet indeholder ikke-ASCII-tegn, har zip'ens skaber måske brugt en anden encoding end din terminal. Prøv `unzip -P "$(echo -n 'passwd' | iconv -t cp437)" arkiv.zip`.

### AES-krypteret, og dictionary finder det ikke

hashcat + regler + en målrettet ordliste er løsningen. Se migrations-trinnene ovenfor.

## Defensiv pointe

Hvis du laver zip-filer, der skal forblive krypterede: brug **AES-256**, ikke ZipCrypto. De fleste moderne værktøjer (`7z`, `zip` fra InfoZIP med `-e`, WinZip, Keka) giver dig AES, hvis du beder om det. Default på `zip` er desværre stadig ZipCrypto på mange systemer. Tjek med `7z l -slt arkiv.zip` før du sender den afsted.

Og vælg et kodeord med længde, ikke smarthed. `hashcat` er ligeglad med, hvor mærkeligt dit substitutions-mønster er; det handler kun om entropi. En fire-ords passphrase (`correct-horse-battery-staple`-stil, ~44 bit) er fin mod offline ZipCrypto-angreb; et tilfældigt 12-tegns blandet kodeord (~78 bit) er fint mod GPU-AES-angreb. Alt kortere er genvindbart.

## Ofte stillede spørgsmål

### Er fcrackzip lovligt?

At gendanne kodeord på filer du ejer eller har autorisation til at tilgå, er lovligt i alle jurisdiktioner, jeg kender. At gøre det på en andens fil uden autorisation er uautoriseret adgang — samme lov som for enhver anden computer-indtrængen.

### Er fcrackzip vedligeholdt?

Kun lige. Kodebasen har været stabil i femten-plus år. Til moderne arbejde har kombinationen af `zip2john` + `hashcat` overtaget.

### Kan fcrackzip bruge en GPU?

Nej. `fcrackzip` er kun CPU. Hvis GPU er det, du har, så gå direkte til hashcat.

### Håndterer fcrackzip .7z, .rar, .gpg-filer?

Nej — kun klassisk PKZIP `.zip`. Til `.7z`, brug `7z2john` + hashcat (mode 11600). Til `.rar`, `rar2john` + hashcat (mode 12500 / 13000). Til `.gpg`, `gpg2john` + hashcat (mode 17010+).

### Hvordan genererer jeg en målrettet ordliste?

`hashcat`s maskprocessor (`mp64`), `crunch` og `cewl` (crawler et site for kandidat-ord) er alle værd at kende. Til at gendanne et specifikt glemt kodeord er den højeste-yield-tilgang at skrive ned, hvad du husker om det — længde, sandsynlige ord, sandsynlige tal — og bygge et mask-angreb fra det.

## Opsummering

- `fcrackzip` + `-D` + en ordliste er det rigtige første forsøg.
- Virker det ikke, og det er ZipCrypto: `fcrackzip` + `-b` med et snævert charset og kort længde.
- Virker det ikke, eller det er AES: `zip2john` + `hashcat` på en GPU.
- Virker det ikke: dit kodeord var stærkt nok. Det er systemet, der virker som tiltænkt.
