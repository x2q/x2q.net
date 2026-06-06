+++
title = "sudo without a password on Ubuntu/Debian — safely (2026)"
date = 2012-10-11
updated = 2026-06-06
slug = "sudo-without-password"
description = "Configure passwordless sudo on Ubuntu or Debian the right way: a drop-in file in /etc/sudoers.d via visudo, scoped to a user, group, or a single command — with the security caveats."

[taxonomies]
tags = ["sudo", "sudoers", "ubuntu", "debian", "linux", "security"]

[extra]
summary = "Passwordless sudo is convenient for automation and lab boxes — and a foot-gun if you do it carelessly. Here's the modern, safe way: a validated drop-in under /etc/sudoers.d, scoped as narrowly as you can get away with."
+++

**TL;DR —** don't edit `/etc/sudoers` directly. Create a validated drop-in: `sudo visudo -f /etc/sudoers.d/nopasswd` and add `youruser ALL=(ALL) NOPASSWD: ALL`. Better yet, scope it to the *specific commands* you actually need to run unattended.

> A 2012 note, refreshed. The mechanism is unchanged, but in 2026 the right move is a drop-in file under `/etc/sudoers.d/` (not editing the main file), and scoping the rule rather than handing out blanket root.

## Always use visudo

`sudo` reads `/etc/sudoers` and every file in `/etc/sudoers.d/`. **`visudo` syntax-checks before saving** — a typo in `sudoers` can lock you out of `sudo` entirely, so never edit these files with a plain editor.

Edit a dedicated drop-in (keeps your change out of the distro-managed main file):

```
sudo visudo -f /etc/sudoers.d/nopasswd
```

## Single user

Add this line (swap in your username):

```
alice ALL=(ALL) NOPASSWD: ALL
```

## A group instead

On Ubuntu, members of the `sudo` group get admin rights (it's `wheel` on Fedora/RHEL). Make the whole group passwordless:

```
%sudo ALL=(ALL) NOPASSWD: ALL
```

## The version you should actually use: scope it

Blanket `NOPASSWD: ALL` means anything that can run as that user can now become root with no further check — a real escalation risk. For automation, grant only the commands the job needs:

```
# deploy user may restart one service and nothing else, no password
deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart myapp, /usr/bin/systemctl status myapp
```

This is the difference between "convenient" and "convenient *and* defensible".

## Apply and test

Files in `/etc/sudoers.d/` are picked up immediately — no reload needed. Validate the whole config and test in a way that won't strand you:

```
sudo visudo -c                 # syntax-check every sudoers file
sudo -k                        # clear the cached credential
sudo -n true && echo "passwordless works"
```

Keep your current root shell open until you've confirmed it works in a *second* terminal.

## Gotchas

- **Filenames matter.** `sudo` ignores files in `/etc/sudoers.d/` with a `.` or `~` in the name (so `nopasswd.conf` is silently skipped). Use a plain name like `nopasswd`.
- **Permissions matter.** The file must be `0440` and owned by root; `visudo -f` sets this for you. A wrong mode makes sudo refuse to start.
- **Order matters.** Later rules win. A broad `NOPASSWD: ALL` after a narrow rule re-opens everything.

## FAQ

### Is passwordless sudo a security risk?

Blanket `NOPASSWD: ALL` removes the last speed-bump between a compromised user account and root. Fine on a throwaway lab VM; scope it (or skip it) on anything that matters. Command-scoped rules are the compromise.

### How do I require a password again?

Delete the drop-in (`sudo rm /etc/sudoers.d/nopasswd`) or remove the `NOPASSWD:` keyword from the line.

### Why does it still ask for a password?

Another rule later in the chain overrides yours, the filename contains a `.`/`~` (so it's ignored), or you edited `/etc/sudoers` but a drop-in re-requires it. Run `sudo visudo -c` and check `/etc/sudoers.d/` for conflicting files.

## Summary

- Edit a drop-in with `sudo visudo -f /etc/sudoers.d/nopasswd` — never the main file by hand.
- `user ALL=(ALL) NOPASSWD: ALL` for a user, `%sudo …` for a group.
- Scope to specific commands for anything beyond a lab box. Validate with `visudo -c`.
