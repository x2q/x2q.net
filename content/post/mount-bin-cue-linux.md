+++
title = "Mount a BIN/CUE disc image on Linux (2026)"
date = 2012-10-16
updated = 2026-06-06
slug = "mount-bin-cue-linux"
description = "You can't loop-mount a BIN/CUE image directly on Linux. Convert it to ISO with bchunk and mount that, or mount the BIN/CUE as-is with a CD emulator like cdemu."

[taxonomies]
tags = ["bchunk", "bin-cue", "iso", "cd-image", "linux"]

[extra]
summary = "Linux can't loop-mount a raw BIN/CUE pair the way it mounts an ISO. The simple fix is to convert the BIN/CUE to ISO with bchunk and mount the ISO; for mixed-mode or audio discs, cdemu emulates a real optical drive instead."
+++

**TL;DR —** you can't `mount` a BIN/CUE pair straight away. Convert it: `bchunk image.bin image.cue out` produces an ISO you can loop-mount. For discs with audio tracks or copy protection, use **cdemu** to emulate a drive instead.

> A 2012 note, still accurate. BIN/CUE images are everywhere (old game/VCD rips), and the loop-mount confusion is perennial. See also the companion post on [bchunk itself](/post/bchunk-bin-cue-to-iso-wav/) if you just need the conversion.

## Why you can't just mount it

A `.bin` is a raw CD sector dump and the `.cue` is a text sheet describing its track layout. The kernel's loopback mounter understands filesystem images (ISO9660, etc.), not raw sector dumps with a separate cue sheet — so `mount image.bin` fails. You bridge the gap one of two ways.

## Option 1 — convert to ISO with bchunk (data discs)

`bchunk` (binchunker) converts a `.bin`/`.cue` set into `.iso` (data) and `.cdr` (audio) tracks.

```
sudo apt install bchunk          # Debian / Ubuntu
sudo dnf install bchunk          # Fedora
```

Convert — the last argument is the output *basename*, so this writes `out01.iso`:

```
bchunk image.bin image.cue out
```

Then loop-mount the ISO:

```
sudo mount -o loop,ro -t iso9660 out01.iso /mnt
ls /mnt
sudo umount /mnt
```

This is the right tool when the image is a single data track — most software/VCD rips.

## Option 2 — emulate a drive with cdemu (audio / mixed-mode)

If the disc has audio tracks, multiple sessions, or anything bchunk's flat conversion would mangle, emulate a real optical drive with **cdemu**. It loads the `.cue` directly and exposes a virtual `/dev/sr` device the desktop auto-mounts.

```
sudo apt install cdemu-client gcdemu      # Debian / Ubuntu (universe)

cdemu load 0 image.cue                     # load into virtual drive 0
cdemu status
# the virtual disc now appears like a real one; eject with:
cdemu unload 0
```

cdemu handles audio and mixed-mode discs that a straight ISO conversion can't represent.

## Option 3 — just extract the files

If you don't need a mounted volume, **7-Zip** can list and extract straight from many BIN/CUE data images:

```
7z l image.cue      # list contents
7z x image.cue      # extract here
```

## FAQ

### bchunk wrote a .iso and several .cdr files — what are those?

The `.cdr` files are the raw audio tracks. Convert one to WAV with `sox track.cdr track.wav` (it's headerless CD-DA), or ignore them if you only wanted the data track.

### mount says "wrong fs type" on the converted ISO

The image may not be ISO9660 (e.g. a UDF or game-console format). Drop the `-t iso9660` and let the kernel autodetect: `sudo mount -o loop,ro out01.iso /mnt`. Console images often need a dedicated emulator instead.

### Can I do this on macOS?

`bchunk` is in Homebrew (`brew install bchunk`); convert to ISO, then `hdiutil attach out01.iso`.

## Summary

- BIN/CUE won't loop-mount directly.
- Data disc → `bchunk image.bin image.cue out` then `mount -o loop out01.iso /mnt`.
- Audio/mixed-mode → load the `.cue` in **cdemu**.
- Just need the files → `7z x image.cue`.
