---
categories:
- Howto
- Ubuntu
- Debian
- Linux
comments: true
date: "2012-10-16T00:00:00Z"
title: 'Howto: Mount Bin/Cue in Linux'
---

Mounting a bin/cue image isn't possible straight away. It requires a simple convertion using `bchunk` to convert a bin/cue file set into an ISO file.

>binchunker converts a CD image in a ".bin / .cue" format (sometimes ".raw /
>.cue") to a set of .iso and .cdr tracks. The bin/cue format is used by some
>popular non-Unix cd-writing software, but is not supported on most other CD
>burning programs. A lot of CD/VCD images distributed on the Internet are in
>BIN/CUE format, I've been told.

Install bchunk on Ubuntu or Debian
    sudo apt-get install bchunk

Convert image.bin and image.cue into image.iso,
    bchunk image.bin image.cue image.iso

Then mount the ISO using the nautilus image mounter mechanism or do it manually on the command line:
    mount -o loop -t iso9660 image.iso /mnt

