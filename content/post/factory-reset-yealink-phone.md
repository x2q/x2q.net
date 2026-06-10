+++
title = "Factory reset a Yealink phone — even without the admin password (2026)"
date = 2026-06-10
slug = "factory-reset-yealink-phone"
description = "How to factory reset a Yealink SIP phone (T4x/T5x and others), including a hardware reset when you don't have the admin password. Plus the default password situation in 2026 — admin/admin vs the per-device label."

[taxonomies]
tags = ["yealink", "voip", "sip", "desk-phone", "factory-reset", "admin-password", "networking"]

[extra]
summary = "You picked up a used Yealink desk phone, or inherited one with an unknown admin password. Here's how to factory reset it three ways — from the keypad, from the web UI, and (the important one) with a hardware key-hold that doesn't need the admin password at all. Plus what changed about Yealink's default password: 'admin/admin' on older firmware, a unique per-device password on newer units."
faq = [
  { q = "What is the default Yealink admin password?", a = "On older firmware it's admin / admin (username admin, password admin). For security, newer Yealink firmware ships with a unique random default password printed on a sticker on the phone (or forces you to set one on first login) — so admin/admin won't work on recent units. If neither works, do a hardware factory reset, which clears the password." },
  { q = "How do I reset a Yealink phone without the admin password?", a = "Use the hardware reset: with the phone idle, press and hold the OK key (the centre soft-key/round key) for about 10 seconds until it asks 'Reset to factory settings?', then confirm with OK. This wipes all settings including the admin password — no login required." },
  { q = "Will a factory reset delete my SIP account and contacts?", a = "Yes. A full factory reset erases the SIP/VoIP account configuration, network settings, contacts and call history, returning the phone to out-of-the-box state. Export or note your SIP credentials first if you'll need to re-register it." },
  { q = "Which Yealink models does this cover?", a = "The same approach works across the SIP-T2x, T4x and T5x families (e.g. T21, T27, T41, T42, T46, T48, T53, T54, T57) and most other Yealink desk phones — the exact key label may differ slightly, but it's the OK/centre key held while idle." }
]
+++

**TL;DR —** To factory reset a **Yealink** SIP desk phone you have three options: the **keypad menu** (needs the admin password), the **web UI** (needs the admin password), or a **hardware key-hold** that needs **no password at all** — hold the **OK** key for ~10 seconds. The last one is what you want for a used or inherited phone with an unknown admin login. This also covers the 2026 default-password situation: old firmware is `admin`/`admin`, newer units ship a **unique password on a label**.

## The default password, then → now

This trips people up, so get it straight first:

- **Older firmware:** username `admin`, password `admin`. The classic default.
- **Newer firmware (security hardening, ~2021 onward):** Yealink ships each phone with a **unique random default password** printed on a sticker (usually on the underside or the box), or forces you to set a new password on first web login. So `admin`/`admin` **will not work** on recent units.

If you have the password, reset from the menu or web UI. If you don't, skip to the **hardware reset** — it clears the password entirely.

## Method 1 — Hardware reset (no admin password needed)

This is the one most people are searching for. With the phone **powered on and idle** (not in a call, not in a menu):

1. Press and **hold the OK key** — the round/centre key below the screen — for about **10 seconds**.
2. The screen shows **"Reset to factory settings?"**
3. Press **OK** to confirm.
4. The phone wipes everything and reboots. This takes a minute or two; don't unplug it.

No login required — this resets the admin password along with everything else. (On a few models the prompt is triggered by holding the **X**/cancel key instead; if OK doesn't do it, try that.)

## Method 2 — From the phone's keypad (needs admin password)

1. Press the **Menu** soft key.
2. Go to **Settings → Advanced Settings** and enter the admin password (`admin` on old firmware, or the label password).
3. Choose **Reset to Factory** (sometimes **Reset Config**) and confirm.

## Method 3 — From the web interface (needs admin password)

1. Find the phone's IP: **Menu → Status** (or **Settings → Status**).
2. Browse to `http://<phone-ip>/` and log in as `admin`.
3. Go to **Settings → Upgrade** (or **Reset & Reboot**) and click **Reset to Factory**.

## After the reset

A full reset erases the **SIP account, network config, contacts and call history** — the phone comes back as if new. Before you reset (if you can log in), note your **SIP credentials** (server/registrar, username, auth ID, password) so you can re-register it afterward. On newer firmware you'll be asked to set a fresh admin password on first login again.

## Summary

- **No admin password?** Hold the **OK** key ~10 s while idle → confirm → done. No login needed.
- **Have the password?** Reset from **Menu → Settings → Advanced**, or the **web UI** at `http://<phone-ip>/`.
- **Default password:** `admin`/`admin` on old firmware; a **unique label password** on newer units.
- A factory reset **erases the SIP account and contacts** — save your SIP credentials first.
