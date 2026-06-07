+++
title = "From Xming on Windows XP to WSLg: 18 years of Linux GUI apps on Windows (2026)"
date = 2026-06-07
slug = "linux-gui-apps-on-windows-xming-to-wslg"
description = "An old clip of Xming forwarding gedit onto Windows XP, and what changed since: VcXsrv, Wayland, and WSLg now run Linux GUI apps on Windows natively — no X server to install."

[taxonomies]
tags = ["x11", "xming", "wsl", "wslg", "wayland", "ssh", "vcxsrv", "linux", "windows", "retrospective"]

[extra]
summary = "Years ago I recorded Xming — an X11 server for Windows — displaying a remote Linux gedit window on a Windows XP desktop over SSH. That trick (install an X server, forward X11 over SSH) was how you ran Linux GUI apps on Windows for two decades. In 2026 you barely do it anymore: WSLg ships a Wayland/X server inside Windows, so `apt install` a Linux app and it just opens. Here's the arc from then to now, and what to actually use today."
faq = [
  { q = "Does SSH X11 forwarding still work in 2026?", a = "Yes. `ssh -X user@host` (or `-Y` for trusted forwarding) still forwards X11 to any running X server — Xming, VcXsrv, XQuartz on a Mac, or the X server inside WSLg. It's unchanged for 20+ years. It's just slow over latency because the X11 protocol is chatty, which is why xpra, waypipe, or a remote-desktop protocol usually beat it today." },
  { q = "Is Xming still maintained?", a = "Sort of. Colin Harrison still ships builds (7.7.x in 2026), but the current releases are donation-gated on straightrunning.com; the last freely downloadable public version on SourceForge froze at 6.9.0.31 back in 2007 — the era of the original Windows XP clip. For a free, actively built X server on Windows, VcXsrv is the usual pick now." },
  { q = "Do I still need an X server like Xming or VcXsrv?", a = "Only for the classic case: forwarding a GUI app from a remote Linux box to a Windows desktop over SSH, or running X apps from inside a non-WSLg distro. If your Linux is WSL2 on Windows 11 (or Windows 10 21H2+), WSLg already bundles a Wayland + X server, so local Linux GUI apps open with no extra software." },
  { q = "What's the difference between X11 and Wayland here?", a = "X11 is the decades-old display protocol with network transparency built in — that's what made `ssh -X` and Xming possible. Wayland is its modern replacement on Linux; it isn't network-transparent by design, so remote display uses waypipe or RDP instead. WSLg runs Weston (a Wayland compositor) with XWayland so both Wayland and legacy X11 apps work." },
  { q = "I just want to edit files on a remote box — do I need any of this?", a = "Probably not. Forwarding a whole editor window made sense in 2007; today you'd use VS Code's Remote-SSH, mount the remote filesystem with sshfs, or just edit over a plain SSH session. Forwarding a GUI app is now the exception, not the default." }
]
+++

**TL;DR —** Running a Linux GUI app on a Windows machine used to mean installing an **X server** (Xming, later VcXsrv), pointing an SSH session at it with `ssh -X`, and watching a remote `gedit` window paint itself onto your Windows desktop. I have [an old screen recording of exactly that](https://www.youtube.com/watch?v=P3hHsfdFusw) — Xming putting gedit on **Windows XP**. Eighteen years later you mostly don't bother: **WSLg** ships a Wayland + X server *inside* Windows, so a Linux app installed in WSL2 just opens like any other window. This post traces the arc — X11 forwarding → VcXsrv → Wayland → WSLg — and what to actually use in 2026.

> This is a companion to the other "then vs now" notes on this blog — like [local speech-to-text replacing the cloud Speech API](/post/local-speech-to-text-whisper-cpp/) and [25 years of Wi-Fi security](/post/hack-wireless-network/). Same shape: a thing that was fiddly in the XP era is now built in.

## The setup, back then

The [video](https://www.youtube.com/watch?v=P3hHsfdFusw) shows the canonical mid-2000s trick. The pieces:

- **Xming** — a free X11 server for Windows (a port of the X.Org server). It ran in the Windows system tray and provided a *display* that X clients could draw to.
- **An SSH client** — usually PuTTY, with "Enable X11 forwarding" ticked, or `ssh -X` from Cygwin.
- **A remote Linux box** running the actual app (`gedit`, an editor) with no local window of its own.

The flow: SSH connects to the Linux host, the host sets `$DISPLAY` to tunnel X11 back through the encrypted SSH channel, the app draws to Xming, and a Linux window appears on Windows XP. The application runs entirely on the remote machine; only the *pixels and input events* travel. This worked because **X11 was network-transparent from day one** — a 1984 design decision that aged into a genuinely useful feature.

It was clever, and it was also slow and brittle: every menu and redraw was a round-trip, so over anything but a LAN it felt like wading through treacle.

## At a glance — 18 years of Linux GUI on Windows

| Era | How you did it | What ran the display | Pain points |
|-----|----------------|----------------------|-------------|
| **~2007 (XP)** | `ssh -X` / PuTTY → Xming | Xming X server in the tray | Manual install, chatty X11, laggy over WAN |
| **~2012** | Same, or X over VNC | Xming / Xming-mesa, VcXsrv arrives (2011) | X server still a separate moving part |
| **~2017** | VcXsrv + WSL1 | VcXsrv, set `DISPLAY=localhost:0` | WSL1 quirks, fonts/clipboard glitches |
| **~2021** | WSL2 + manual X server, *or* WSLg preview | VcXsrv / X410, then WSLg | Transitional; manual `DISPLAY` export still common |
| **2026 (today)** | WSLg, built in | Weston (Wayland) + XWayland, auto | Basically none — `apt install`, app opens |

## What actually changed

**1. The X server stopped being yours to manage.** For ~25 years the X server was a thing *you* installed and babysat on Windows. With [WSLg](https://github.com/microsoft/wslg) — announced at Microsoft Build 2021, now standard on Windows 11 and Windows 10 21H2+ — Microsoft bundles a whole display stack into a system distro: a **Weston** Wayland compositor, **XWayland** for legacy X11 apps, a PulseAudio server for sound, and an RDP link that paints the windows onto the Windows desktop. You install a Linux GUI app in WSL2 and it opens. No `DISPLAY`, no tray icon, no PuTTY checkbox.

```bash
# Inside WSL2 on Windows 11 — no X server to install:
sudo apt update && sudo apt install -y gedit
gedit            # a real Linux gedit window opens on Windows
```

**2. Wayland replaced X11 on the Linux side.** The protocol that made the original trick possible is on its way out. Modern Linux desktops default to **Wayland**, which — unlike X11 — is *not* network-transparent. So the "just forward it over SSH" reflex doesn't map cleanly anymore; the Wayland-native answer for remote display is [`waypipe`](https://gitlab.freedesktop.org/mstoeckl/waypipe), and XWayland keeps old X11 apps working in the meantime.

**3. Xming itself faded into a paid niche.** Xming is still alive — Colin Harrison shipped 7.7.x builds as recently as January 2026 — but the freely downloadable public release froze at **6.9.0.31 in 2007**; newer versions are donation-gated. The free, actively maintained torch passed to **[VcXsrv](https://github.com/marchaesen/vcxsrv)**, an open-source X server built from current X.Org sources. (Note: VcXsrv dropped Windows XP support long ago — that era is genuinely over.)

**4. The whole *reason* mostly evaporated.** In 2007 you forwarded an editor because editing remote files any other way was painful. In 2026 you'd reach for **VS Code Remote-SSH**, [mount the remote filesystem with sshfs](/post/mount-remote-filesystem-sshfs/), or just work in a terminal over [key-based SSH](/post/ssh-key-login-without-password/). Forwarding a single GUI window is now the exception, not the workflow.

## What to use today

**You're on WSL2 (Windows 11 / Win10 21H2+):** do nothing. WSLg is already there. `apt install` the app and run it. Check with:

```bash
echo $WAYLAND_DISPLAY     # wayland-0   → WSLg is active
echo $DISPLAY             # :0          → XWayland for legacy X11 apps
```

**You need to forward a GUI app from a remote Linux server to Windows:** install **VcXsrv**, start it (multiple-windows mode, disable access control on a trusted network only), and:

```bash
ssh -X user@server        # -Y for trusted forwarding if -X is blocked
xterm                     # or whatever GUI app — it paints to VcXsrv
```

This is the *exact* same mechanism as the Xming clip, just with a modern X server. It still works. It's still chatty over latency.

**You want remote GUI that doesn't crawl over WAN:** skip raw X11. Use [`xpra`](https://github.com/Xpra-org/xpra) ("screen for X" — apps survive disconnects and it compresses well), `waypipe` for Wayland, or a real remote-desktop protocol (RDP via `xrdp`, or NoMachine/NX) for a full desktop.

## The takeaway

The Windows XP clip is a little time capsule: a tray-icon X server, a PuTTY tunnel, and a Linux text editor materialising on a beige XP desktop. The *idea* — run the app over there, see it over here — never went away. What changed is that you no longer assemble it by hand. The X server moved inside Windows, X11 gave way to Wayland, and the common case ("I just want to touch files on that box") got better answers entirely. Eighteen years of plumbing, quietly absorbed into `apt install`.

## FAQ

### Does SSH X11 forwarding still work in 2026?

Yes — `ssh -X` (or `-Y` for trusted forwarding) is unchanged. It forwards X11 to any X server: VcXsrv, Xming, XQuartz, or WSLg's. It's just chatty over latency, which is why xpra/waypipe/RDP usually win for remote work today.

### Is Xming still maintained?

Builds still appear (7.7.x in 2026), but they're donation-gated; the last free public release was 6.9.0.31 in 2007 — the Windows XP era of the clip. For a free, actively built X server on Windows, use VcXsrv.

### Do I still need an X server at all?

Only to forward GUI apps from a remote box over SSH, or to run X apps from a non-WSLg distro. On WSL2 with Windows 11 (or Win10 21H2+), WSLg already bundles one — local Linux GUI apps open with nothing extra installed.

### Why did Wayland break the old "forward it over SSH" trick?

X11 was network-transparent by design, so forwarding came free. Wayland deliberately isn't — remote display is a separate concern handled by waypipe or RDP. WSLg papers over it by running Weston + XWayland, so both kinds of app work.

## Summary

- The old way: install **Xming**, tick X11 forwarding in PuTTY, `ssh -X`, and a remote Linux app paints onto Windows. The [video](https://www.youtube.com/watch?v=P3hHsfdFusw) is that, on Windows XP.
- Today: **WSLg** ships a Wayland + X server inside Windows — `apt install` a Linux app in WSL2 and it just opens.
- **VcXsrv** is the free, maintained successor to Xming for the classic remote-forwarding case; **Xming** itself went donation-only after 6.9.0.31 (2007).
- **Wayland** replaced X11's network transparency; use **waypipe**, **xpra**, or RDP for fast remote GUI.
- For the original motivation — editing on a remote box — prefer VS Code Remote-SSH, [sshfs](/post/mount-remote-filesystem-sshfs/), or plain [SSH](/post/ssh-key-login-without-password/).
