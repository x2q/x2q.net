+++
title = "bchunk — convert .bin/.cue images to .iso and .wav on Linux and macOS"
date = 2026-04-22
slug = "bchunk-bin-cue-to-iso-wav"
description = "How to use bchunk (binchunker) to split a .bin/.cue CD image into a proper .iso data track plus .wav audio tracks. Works on Linux, macOS (Homebrew), and WSL."

[taxonomies]
tags = ["bchunk", "binchunker", "bin-cue", "iso", "cd-image", "linux", "macos", "homebrew", "audio-cd"]

[extra]
summary = "bchunk (binchunker) splits a .bin/.cue CD image into .iso for the data track and .wav files for each audio track. The canonical tool for turning a mixed-mode BIN/CUE into something you can mount or burn."
+++

**TL;DR —** **`bchunk`** — sometimes called **`binchunker`** — is a small, old, Unix command-line tool that takes a `.bin`/`.cue` pair (a raw CD image with a cue sheet) and splits it into a proper **`.iso` file for the data track** and one **`.wav` file per audio track**. It's the right tool when a download or archive gave you `game.bin` + `game.cue` and you actually want to **mount the data track** or **re-burn the audio tracks**. Install with `apt install bchunk` on Debian/Ubuntu, `brew install bchunk` on macOS, or build from source on anything else. Usage is `bchunk [options] image.bin image.cue basename` — you get `basename01.iso`, `basename02.wav`, `basename03.wav`, and so on.

## What .bin/.cue is, and why you'd want to split it

A `.bin`/`.cue` pair is a **raw, bit-accurate CD image** plus a plain-text sheet that describes the track layout. The `.bin` contains every sector of the CD back-to-back — including data tracks (Mode 1 or Mode 2), audio tracks (raw Red Book PCM, 2352 bytes per sector, no filesystem), and the gaps between them. The `.cue` tells you where each track starts and what type it is.

This format is the standard output of CD-ripping tools like cdrdao and of old game-preservation scrapes, because it preserves *everything* — pregaps, CD-TEXT, mixed-mode CDs, CD-DA audio. That's also why you can't just rename `game.bin` to `game.iso` and mount it: a mixed-mode CD has **non-filesystem sectors** at the beginning, audio tracks that aren't a filesystem at all, and per-sector headers that ISO expects stripped.

`bchunk` does the conversion properly:

- **Data tracks** become ISO 9660 files (`.iso`) — the 2352-byte CD sectors are trimmed to 2048-byte ISO sectors, headers discarded.
- **Audio tracks** become 16-bit stereo 44.1 kHz `.wav` files, each with a proper WAV header.

After that you can `mount -o loop` the `.iso`, play the `.wav`s, or feed them to a burner.

## Installing

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
# or from AUR: yay -S bchunk
```

### Fedora / RHEL / CentOS

`bchunk` isn't in the default repos; get it from RPMFusion or build from source:

```
git clone https://github.com/hessu/bchunk.git
cd bchunk
make
sudo cp bchunk /usr/local/bin/
```

### Windows

Use WSL and `apt install bchunk`. There's an old native port but WSL is easier.

## Basic usage

```
bchunk game.bin game.cue game
```

Output:

```
game01.iso    # data track, mountable as ISO 9660
game02.wav    # audio track 1
game03.wav    # audio track 2
...
```

The `basename` (`game` in the example) is the prefix for every output file. Track numbers start at `01`.

## Useful options

`bchunk` has a small, stable set of flags — most of them are there to handle specific CD quirks.

- **`-v`** — verbose. Prints each track as it's processed. Use this the first time you run it to confirm you're getting the track layout you expect.
- **`-w`** — write `.wav` files (default). Explicit form.
- **`-r`** — raw audio output instead of `.wav`. Useful if you're piping into `sox` or `ffmpeg` and don't want a second header-stripping step.
- **`-p`** — **Psx/PlayStation mode**. Treats Mode 2 sectors more loosely — needed for many PlayStation CD images where the cue sheet is imprecise.
- **`-s`** — swap byte order on audio tracks. Needed if the `.bin` was produced by a ripper that wrote little-endian audio where `bchunk` expects big-endian (or vice versa). Symptom: output `.wav` sounds like white noise.
- **`-W`** — write `.wav` with a verified (rather than computed) header size. Rarely needed.
- **`-E`** — use the exact track boundaries from the cue sheet rather than probing. Use this if audio tracks sound clipped at the beginning or end.

## Mounting the resulting .iso

On Linux:

```
sudo mkdir /mnt/cd
sudo mount -o loop game01.iso /mnt/cd
ls /mnt/cd
```

On macOS:

```
hdiutil attach game01.iso
```

## Common gotchas

### "Illegal or unsupported track type" or empty output

Your cue sheet is malformed or references a `.bin` size that doesn't match. Open the `.cue` in a text editor — it's plain text — and check:

- The `FILE "..."` line points at the right `.bin` filename, case-sensitive.
- `TRACK` entries are numbered sequentially with types `MODE1/2352`, `MODE2/2352`, or `AUDIO`.
- Index entries (`INDEX 00`, `INDEX 01`) are MM:SS:FF, with FF being frames (0–74).

### Audio tracks sound like static

Byte order mismatch. Retry with `-s`:

```
bchunk -s game.bin game.cue game
```

### Single `.iso` is fine, but audio tracks are silent or truncated

Try `-E` to force cue-sheet-exact boundaries:

```
bchunk -E game.bin game.cue game
```

### PlayStation/PSX image won't split cleanly

Use `-p`:

```
bchunk -p psx.bin psx.cue psx
```

This is the most common complaint on forums — PSX cues are almost always Mode 2 and `bchunk` without `-p` is strict about them.

### Multiple `.bin` files referenced in the cue

Some rippers produce one `.bin` per track plus a combining cue sheet. `bchunk` expects one `.bin` for the whole disc. Concatenate them first with `cat track01.bin track02.bin ... > combined.bin` and point a single-file cue at `combined.bin`.

## Alternatives worth knowing

- **`cdemu`** — user-space CD emulator for Linux. Can mount a `.bin`/`.cue` directly without splitting. Useful if you just want to *read* the data track temporarily.
- **`ecm-tools`** — different format (`.ecm`), but same problem space. Worth knowing if you encounter it.
- **`7z` / `p7zip`** — newer 7-Zip versions can list and extract ISO 9660 data tracks from a raw `.bin`, but can't recover audio as `.wav`.
- **`ffmpeg`** — if you want MP3 / FLAC / Opus instead of `.wav`, pipe the raw output: `bchunk -r game.bin game.cue game && ffmpeg -f s16be -ar 44100 -ac 2 -i game02.raw game02.flac`.

## Why it's still useful in 2026

Optical-media imaging has been a solved problem for decades, but `.bin`/`.cue` is still the default output of `cdrdao`, still what old archives are stored as, and still what shows up when someone hands you a CD backup that isn't an ISO. `bchunk` is a ~1,000-line C program, written in the late 1990s, that does one job correctly and has barely changed in twenty years. It's in every major distribution, it compiles cleanly on modern systems, and it's the right tool.

If you're trying to recover data from an old CD image: start here.
