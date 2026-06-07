+++
title = "From Launchy to Raycast: the history of the keystroke launcher (2007 → 2026)"
date = 2026-06-07
slug = "history-of-application-launchers-launchy-to-raycast"
description = "In 2007 I demoed Launchy, a keystroke app launcher for Windows. The story of where that idea came from — Quicksilver, LaunchBar — and where it went: Alfred, Raycast, PowerToys, and the Cmd+K command palette in every app."

[taxonomies]
tags = ["launchy", "quicksilver", "alfred", "raycast", "command-palette", "productivity", "windows", "macos", "linux", "retrospective"]

[extra]
summary = "Back in 2007 I recorded a short demo of Launchy — a keystroke application launcher that replaced the Windows Start menu with a few typed letters. That idea (hit a hotkey, type, fuzzy-match, launch) started on the Mac with Quicksilver and LaunchBar, jumped to Windows via Launchy, spread to Linux, then split in two: it grew into productivity platforms like Alfred and Raycast, and it dissolved into the Cmd+K command palette that now lives inside nearly every app. Here's the 19-year arc."
faq = [
  { q = "What was Launchy?", a = "A free, open-source keystroke application launcher for Windows (later cross-platform), first released by Josh Karlin around 2004. You'd hit a hotkey (Alt+Space), type a few letters of an app or file name, and Launchy fuzzy-matched and launched it — replacing the Start menu and desktop icons. It was widely described as 'Quicksilver for Windows'. The 2007 video shows it running the 'Shiny' skin." },
  { q = "Is Launchy still maintained?", a = "Not really. Active development tapered off around 2010 and the original project is effectively dormant (community forks exist on GitHub). On Windows in 2026 you'd use PowerToys Command Palette, Flow Launcher, or Raycast instead — all descendants of the same idea." },
  { q = "What's the difference between an app launcher and a command palette?", a = "Originally none — both are 'hit a hotkey, type, fuzzy-match, act'. The launcher (Quicksilver, Launchy, Alfred, Raycast) is system-wide and launches apps/files/actions. The command palette (VS Code's Ctrl+Shift+P, the Cmd+K bar in Slack/Linear/Notion/GitHub) is the same pattern scoped inside a single app. The launcher came first; the command palette is that UX absorbed into everything." },
  { q = "What should I use today?", a = "macOS: Raycast (the modern default — extensions, clipboard history, window management, AI) or Alfred (one-time purchase, local automation), with Spotlight built in. Windows: PowerToys Command Palette (official, free), Flow Launcher (open source), or Raycast (Windows beta arrived late 2025). Linux: Rofi, Ulauncher, or Albert. Terminal: fzf." }
]
+++

**TL;DR —** In 2007 I posted a short screencast of **[Launchy](https://youtu.be/LBW1L2YOKks)** — a "keystroke application launcher" that let you summon any program on Windows by hitting a hotkey and typing a few letters, instead of hunting through the Start menu. That pattern — **hotkey → type → fuzzy-match → launch** — was born on the Mac (Quicksilver, LaunchBar), crossed to Windows with Launchy, spread to Linux, and then did two things at once: it matured into full productivity platforms (**Alfred**, then **Raycast**), and it dissolved into the **Cmd+K command palette** that now lives inside nearly every app you use. Here's the 19-year arc.

> A companion to the other time-capsule posts here — like [Xming on Windows XP → WSLg](/post/linux-gui-apps-on-windows-xming-to-wslg/) and [25 years of Wi-Fi security](/post/hack-wireless-network/). An old screencast, and what the idea grew into.

## The setup, back then

The [video](https://youtu.be/LBW1L2YOKks) ("Shiny Windows Application Launcher" — *Shiny* was a Launchy skin) shows the 2007 workflow. You install **Launchy**, it indexes your Start menu, and from then on:

1. Press **Alt+Space**. A small translucent box appears in the middle of the screen.
2. Type a few letters — `fir` for Firefox, `wor` for Word.
3. Launchy fuzzy-matches against everything it indexed and shows the best hit.
4. Hit **Enter**. The app launches. The box vanishes.

No mouse, no Start menu, no desktop icons. After a week your fingers knew the three-letter prefix for every app you used. Launchy — written by Josh Karlin and open-sourced — was explicitly pitched as **"Quicksilver for Windows"**, and that comparison is the key to the whole story.

## Where the idea actually came from

Launchy didn't invent the keystroke launcher — it brought a **Mac** idea to Windows:

- **LaunchBar** (Objective Development) — the granddaddy, with roots on **NeXTSTEP in the 1990s**, reborn on Mac OS X. Type an abbreviation, get the thing.
- **Quicksilver** (Nicholas Jitkoff / Blacktree, ~2003) — the legendary, almost mystical Mac launcher. Not just "launch an app" but a verb-noun grammar: select a *thing*, choose an *action*, pick a *target*. It defined the genre and inspired a generation (it was open-sourced in 2007 when its creator left for Google).
- **Spotlight** (Mac OS X Tiger, 2005) — Apple baked search into the OS, which is where most casual users met the "just type to find things" idea.

Launchy (2004→) was the Windows answer to all that, and the 2007 video is a snapshot of it in its prime.

## At a glance — 19 years of launchers

| Era | macOS | Windows | Linux | The pattern |
|-----|-------|---------|-------|-------------|
| **~2003–05** | Quicksilver, LaunchBar, Spotlight | Start menu (Vista adds search, 2007) | — | Launcher is a Mac power-user thing |
| **2007 (the video)** | Quicksilver peak | **Launchy** ("Quicksilver for Windows") | — | Keystroke launcher crosses to Windows |
| **~2008–10** | Quicksilver stalls → **Alfred** (2010) | Launchy peaks, then slows | **GNOME Do**, Katapult | Launcher goes mainstream-power-user |
| **~2011–15** | Alfred + Powerpack dominates | Wox (2014) | Synapse, Albert | **Command palette** appears (Sublime, then VS Code) |
| **~2016–20** | **Raycast** founded (2020) | **PowerToys Run** (2020), Flow Launcher | Rofi, Ulauncher | Cmd+K spreads into every web app |
| **2026 (today)** | Raycast dominant; Spotlight + Apple Intelligence | PowerToys **Command Palette**; Raycast (beta) | Rofi / Ulauncher / Albert | Launcher = AI-powered command hub |

## What changed

**1. The launcher became a platform.** Launchy launched apps and files. **Alfred** (2010) added *workflows* — chain actions, run scripts, clipboard history, snippets — and became the Mac standard for a decade. Then **Raycast** (2020) rebuilt the idea as a native, extensible platform: an extension store, window management, clipboard history, snippets, calculators, and now built-in **AI**. The humble launch box turned into the place power users run half their day. Raycast's **Windows beta arrived in late 2025**, closing the loop back to where Launchy started.

**2. Windows kept reinventing it.** Launchy faded after ~2010. **Wox** (open source, 2014) carried the torch and spawned **Flow Launcher** (a Wox fork with a plugin marketplace and AI plugins). Microsoft itself shipped **PowerToys Run** (2020, `Alt+Space` — a knowing nod to Launchy), now succeeded by the **PowerToys Command Palette**. The pattern is so obviously good that the OS vendor adopted it.

**3. Linux always had its own.** **GNOME Do** (2008) was the early Quicksilver-alike; today it's **Rofi** and **dmenu** (minimal, scriptable, beloved by tiling-WM users), **Ulauncher**, and **Albert**. Same muscle memory, different ecosystem.

**4. The biggest shift: the launcher dissolved into every app.** The defining move of the last decade isn't a better launcher — it's that the *command palette* became a universal UX primitive. **Sublime Text** (~2011) and then **VS Code** (`Ctrl/Cmd+Shift+P`) made "hit a hotkey, type a command" the way you drive an editor. Then **Cmd+K** showed up everywhere: Slack, Linear, Notion, GitHub, Figma, Vercel, Stripe, your browser. The keystroke launcher stopped being a separate app you install and became a control built into the software itself. On the terminal, **fzf** (2013) is the same idea distilled to one fuzzy-finder binary.

**5. Then AI ate the command bar.** The newest turn: the box you type into now talks to a model. **Raycast AI**, Flow Launcher's AI plugins, **Spotlight + Apple Intelligence**, Windows **Copilot**. "Hotkey → type → fuzzy-match → act" is becoming "hotkey → ask → the launcher figures out the action." Launchy's little translucent box was the larval form of today's AI command bar.

## What to use today

**macOS** — **[Raycast](https://www.raycast.com/)** is the modern default: launching, clipboard history, window management, snippets, an extension store, and AI in one hotkey. **[Alfred](https://www.alfredapp.com/)** is the alternative if you prefer a one-time purchase and local automation. Spotlight is built in and now quite good.

**Windows** — **PowerToys Command Palette** (official, free, ships in [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/)), **[Flow Launcher](https://www.flowlauncher.com/)** (open source, plugin marketplace), or **Raycast** (Windows beta since late 2025). Pair any of them with **[Everything](https://www.voidtools.com/)** for instant file search.

**Linux** — **Rofi** or **dmenu** for the scriptable/tiling crowd, **Ulauncher** or **Albert** for a friendlier GUI.

**Terminal** — **[fzf](https://github.com/junegunn/fzf)**. Pipe anything into it, fuzzy-find, act. The launcher idea in 30 lines of muscle memory.

## The takeaway

The 2007 Launchy clip looks quaint — a translucent box, a Shiny skin, three letters and Enter. But the idea in it won completely. It started as a Mac curiosity, Launchy brought it to Windows, Linux picked it up, and from there it went two directions at once: *up* into productivity platforms like Raycast, and *sideways* into every app as the Cmd+K command palette. Today you use that 2007 idea dozens of times a day — you just don't install it anymore, because it's everywhere. And the box is starting to think.

## FAQ

### What was Launchy?

A free, open-source keystroke launcher for Windows (later cross-platform), first released by Josh Karlin around 2004. Hotkey, type a few letters, fuzzy-match, launch — "Quicksilver for Windows". The 2007 video shows it on the Shiny skin.

### Is Launchy still maintained?

No — development tapered off around 2010 and it's effectively dormant. On Windows today use PowerToys Command Palette, Flow Launcher, or Raycast.

### App launcher vs command palette — what's the difference?

Same pattern, different scope. A launcher (Quicksilver, Launchy, Alfred, Raycast) is system-wide; a command palette (VS Code's `Ctrl+Shift+P`, the `Cmd+K` bar in Slack/Linear/GitHub) is that same UX inside one app. The launcher came first; the palette is it absorbed into everything.

### What should I use in 2026?

macOS: Raycast or Alfred. Windows: PowerToys Command Palette, Flow Launcher, or Raycast. Linux: Rofi, Ulauncher, or Albert. Terminal: fzf.

## Summary

- The keystroke launcher — **hotkey → type → fuzzy-match → launch** — started on the Mac (**LaunchBar**, **Quicksilver**) and reached Windows via **Launchy**, which my [2007 video](https://youtu.be/LBW1L2YOKks) demos.
- It grew *up* into platforms: **Alfred** (2010) → **Raycast** (2020), now AI-powered, with a **Windows beta** as of late 2025.
- Windows kept reinventing it: **Wox** → **Flow Launcher**, and Microsoft's **PowerToys Run → Command Palette**.
- It also spread *sideways* into every app as the **Cmd+K command palette** (Sublime/VS Code → Slack, Linear, Notion, GitHub), and into the terminal as **fzf**.
- The 2007 idea is now everywhere — and increasingly an AI command bar.
