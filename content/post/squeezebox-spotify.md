+++
title = "How to play Spotify on a Logitech Squeezebox in 2026"
date = 2026-04-22
slug = "squeezebox-spotify-guide"
description = "Spotify on Squeezebox Classic, Touch, Boom and Radio in 2026 — via Logitech Media Server, the Spotty plugin, and spotifyd as a bridge. Works without the defunct official plugin."

[taxonomies]
tags = ["squeezebox", "spotify", "logitech-media-server", "lms", "spotty", "spotifyd", "audio", "homelab"]

[extra]
summary = "The official Squeezebox Spotify plugin has been broken for years. Here's what actually works in 2026: Logitech Media Server + the Spotty plugin, or spotifyd as a Spotify Connect bridge into LMS."
+++

**TL;DR —** The official Spotify plugin Logitech shipped with Squeezebox stopped working when Spotify retired the `libspotify` API in 2022. In 2026 there are two working paths to get **Spotify on a Squeezebox Classic, Touch, Boom, Radio, or Transporter**: (1) **Logitech Media Server + the [Spotty plugin](https://github.com/michaelherger/Spotty-Plugin)** (now renamed `Spotty` / sometimes `Spotty-XL`), which uses the Spotify Web API plus `librespot` under the hood, or (2) run **[spotifyd](https://github.com/Spotifyd/spotifyd)** on the same host as LMS and point LMS at it as a generic audio source. Path 1 is the one you want unless you have a reason otherwise. This post walks through it.

## What happened to the official plugin

Squeezebox hardware went end-of-life at Logitech in 2012, but the software — **Logitech Media Server (LMS)**, the thing that actually streams music to the devices — has been community-maintained ever since. For years it shipped an official "Spotify" plugin that used Spotify's now-discontinued `libspotify` C library. When Spotify shut `libspotify` down in 2022, that plugin stopped working, and Spotify has not shipped a replacement for third-party embedded devices.

The community filled the gap:

- **`librespot`** — an open-source, Rust reimplementation of the Spotify Connect client protocol. It's the basis of most modern third-party Spotify integrations.
- **Spotty plugin for LMS** — wraps `librespot` plus the Spotify Web API into an LMS plugin. Presents Spotify browsing, search, playlists, and playback inside the Squeezebox UI (both the device screen and the LMS web UI).
- **spotifyd** — a standalone `librespot`-based daemon that shows up as a Spotify Connect target. Your phone sees it as a speaker, you cast to it, and its audio output goes somewhere LMS can pick it up.

## Path 1 (recommended): Spotty plugin on LMS

This is the cleanest experience and the one that feels native on the Squeezebox. You search and browse from the Squeezebox remote or Touch screen, and it Just Works.

### 1. Get LMS running

If you're not already running LMS, install it on whatever always-on machine you have — a Raspberry Pi, a NAS with a Docker runtime, or a small Linux box is ideal.

```
# Debian/Ubuntu — grab the latest .deb from the community repo
wget https://downloads.slimdevices.com/LogitechMediaServer_v8.x/logitechmediaserver_<latest>_amd64.deb
sudo apt install ./logitechmediaserver_<latest>_amd64.deb
sudo systemctl enable --now logitechmediaserver
```

Or via Docker — `lmscommunity/logitechmediaserver` is a maintained image:

```
docker run -d --name lms \
  --network host \
  -v lms-config:/config \
  -v /path/to/music:/music:ro \
  lmscommunity/logitechmediaserver:latest
```

Open `http://<host>:9000/` and you should see the LMS web UI. Your Squeezebox devices on the same LAN should appear under **Players** automatically.

### 2. Install Spotty

In the LMS web UI: **Settings → Plugins → Install new plugins** and tick **Spotty** (author: Michael Herger). LMS downloads, installs, and restarts. On restart, you'll have a **Spotty** entry in **Settings → Advanced → Spotty**.

### 3. Authorise Spotty with your Spotify account

- In **Settings → Advanced → Spotty**, click **Add account**.
- Spotty kicks off an OAuth flow via Spotify's Web API — you log in once in a browser, approve the access, and the token is stored on the LMS server.
- You need **Spotify Premium** for playback. (This is a Spotify-side limit: `librespot` can authenticate with Free, but full-quality playback is Premium-only.)

### 4. Play something

On the Squeezebox device itself, **Home → My Music → Spotty** (or **Home → Music Library → Spotty**, depending on your LMS version) — browse playlists, search, start a track. On the Squeezebox Touch the on-screen artwork works. On the Classic the text UI works. On the Radio and Boom you drive it from the web UI or the [Squeeze Commander](https://squeeze-commander.com/) / [Squeezer](https://play.google.com/store/apps/details?id=uk.org.ngo.squeezer) apps.

Spotty also adds Squeezebox devices as **Spotify Connect targets** — meaning you can cast from your phone's Spotify app to "Living Room Squeezebox" natively, the same way you'd cast to a Sonos or a Google Home.

## Path 2: spotifyd as a Connect bridge

Use this if Spotty won't install (old LMS version, old Perl, weird OS) or you specifically want Spotify Connect behaviour without Spotty.

```
# Debian/Ubuntu
sudo apt install spotifyd
# or from source: cargo install spotifyd
```

Configure `/etc/spotifyd.conf` with your Spotify credentials, a backend (`alsa`, `pulseaudio`, or `pipe`), and a device name. Start the daemon:

```
sudo systemctl enable --now spotifyd
```

From your phone, cast to the `spotifyd`-named device. Audio comes out of the host.

To get that audio into a Squeezebox, pipe `spotifyd` to a FIFO and play the FIFO in LMS:

```
# spotifyd.conf
backend = "pipe"
device = "/var/run/spotifyd.pipe"
```

Then in LMS: add the FIFO as a **File system music folder** and play it as a live stream.

This is clunkier and has ~1 s of latency vs. Spotty's tight integration. Only use it if Path 1 doesn't work for you.

## Works on which Squeezebox?

Spotty works on every Squeezebox device that talks to LMS:

- **Squeezebox Classic / Squeezebox v3** (text display) — text-UI browsing and playback.
- **Squeezebox Touch** — colour touchscreen, artwork, the whole UI.
- **Squeezebox Boom** — text UI, same as Classic.
- **Squeezebox Radio** — text UI, built-in speaker.
- **Squeezebox Duet / Controller** — the controller's UI works; playback goes to the Receiver.
- **Transporter** — full support.
- **piCorePlayer / SqueezeLite on Pi** — yes, these are software Squeezeboxes and Spotty streams to them fine.

As long as the device can connect to LMS, Spotty can feed it.

## FAQ

### Do I need Spotify Premium?

Yes, for playback. `librespot` (and therefore Spotty) requires a Premium account to decode audio. Spotify Free accounts can authenticate but won't play.

### Does Spotify Connect "appear the Squeezebox as a speaker" work?

Yes, with Spotty installed. Each Squeezebox player shows up in the Spotify app's device picker as a Connect target.

### Does hi-res / lossless work?

Spotify itself doesn't offer lossless on standard plans (Hi-Fi has been "coming soon" for years). Spotty plays whatever Spotify serves — Ogg Vorbis 320 kbps on Premium — and the Squeezebox handles it natively.

### Gapless playback?

Yes, Spotty supports gapless.

### Does this break if Spotify's Web API changes?

Yes, occasionally — Spotify periodically rotates OAuth scopes or deprecates endpoints, and Spotty gets a patch release. Keep the plugin updated.

### Can I run LMS on the same box as my NAS?

Absolutely. LMS is lightweight (~200 MB RAM, minimal CPU except during library scans). Running it next to Samba or on a homelab SBC is the common setup.

### Is this the same as "piCorePlayer"?

piCorePlayer is a tiny Linux distribution that turns a Raspberry Pi into a Squeezebox-compatible player (via SqueezeLite). It does not replace LMS — you still need LMS as the server. piCorePlayer + LMS + Spotty is a very common 2026 stack for people whose original Squeezebox hardware finally died.

## What to do if your Squeezebox won't connect to LMS at all

Two things to check first:

1. **mDNS / multicast across your network.** Modern Wi-Fi routers often block multicast between SSIDs or to wired hosts. Put the Squeezebox and LMS on the same subnet/VLAN with multicast allowed.
2. **SlimProto port (3483/udp and 3483/tcp).** That's what the Squeezebox uses to find LMS. Not blocked by anything sensible, but worth checking if you run a strict firewall.

Beyond that, the Squeezebox community is still active — [forums.slimdevices.com](https://forums.slimdevices.com/) and the [LMS Community GitHub](https://github.com/LMS-Community) are where problems get solved.

Squeezebox hardware was discontinued fifteen years ago. Thanks to LMS, Spotty, and `librespot`, it still plays Spotify better than most "smart speakers" sold new in 2026.
