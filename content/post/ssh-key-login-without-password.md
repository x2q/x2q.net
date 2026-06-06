+++
title = "SSH login without a password — set up key authentication (2026)"
date = 2007-06-09
updated = 2026-06-06
slug = "ssh-key-login-without-password"
description = "Log in over SSH without typing a password: generate an ed25519 key with ssh-keygen, copy it with ssh-copy-id, fix the permissions, and optionally disable password auth."

[taxonomies]
tags = ["ssh", "openssh", "ssh-keygen", "ed25519", "linux", "security"]

[extra]
summary = "Password-free SSH is key-pair authentication: a private key stays on your machine, the matching public key goes on the server. Generate an ed25519 key, copy it with ssh-copy-id, lock down the permissions — and, if you want, turn password logins off entirely."
+++

**TL;DR —** `ssh-keygen -t ed25519`, then `ssh-copy-id user@host`. Now `ssh user@host` logs you in with no password. Use a passphrase on the key plus `ssh-agent` so it stays both convenient *and* safe.

> One of the oldest how-tos from my blog (2007), back when `ssh-keygen -t rsa` was the answer. In 2026 you want **ed25519** keys, and `ssh-copy-id` does the fiddly part for you.

## How it works

Key authentication uses a **key pair**: a *private* key that never leaves your machine, and a matching *public* key you place on each server. The server challenges you with something only the private key can answer — so you prove who you are without ever sending a password.

## 1. Generate a key pair

```
ssh-keygen -t ed25519 -C "you@laptop"
```

- **`-t ed25519`** — modern, short, fast, secure. (Use `-t rsa -b 4096` only for ancient servers that don't support ed25519.)
- **`-C`** — a comment to identify the key later.

You'll be asked where to save it (default `~/.ssh/id_ed25519`) and for a **passphrase**. Use one — see the agent note below. This produces two files: `id_ed25519` (private — guard it) and `id_ed25519.pub` (public — safe to share).

## 2. Copy the public key to the server

The easy way:

```
ssh-copy-id user@remote.host
```

It appends your public key to `~/.ssh/authorized_keys` on the server and fixes the permissions. If `ssh-copy-id` isn't available, do it by hand:

```
cat ~/.ssh/id_ed25519.pub | ssh user@remote.host \
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

## 3. Log in

```
ssh user@remote.host
```

No password prompt (just your key's passphrase the first time, if you set one).

## Keep it convenient with ssh-agent

A passphrase-protected key would defeat the "no password" goal — except `ssh-agent` caches the unlocked key for your session, so you type the passphrase **once**:

```
eval "$(ssh-agent -s)"     # start the agent (often already running)
ssh-add ~/.ssh/id_ed25519  # unlock the key once
```

macOS stores it in the Keychain automatically with `ssh-add --apple-use-keychain`.

## Optionally: turn off password logins

Once keys work, disabling password auth shuts the door on brute-force attempts entirely. On the server, edit `/etc/ssh/sshd_config`:

```
PasswordAuthentication no
PubkeyAuthentication yes
```

Then reload: `sudo systemctl reload ssh` (or `sshd`). **Confirm key login works in a second session before you do this**, or you can lock yourself out.

## Permissions matter (the #1 reason it "doesn't work")

SSH refuses keys if the permissions are too loose:

```
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys      # on the server
chmod 600 ~/.ssh/id_ed25519           # your private key
```

## FAQ

### Still asks for a password?

Almost always permissions (above) or the wrong key. Debug with `ssh -v user@host` and watch which key it offers and whether the server rejects `authorized_keys` for being group/world-writable.

### Multiple keys / multiple servers?

Put them in `~/.ssh/config`:

```
Host prod
  HostName prod.example.com
  User deploy
  IdentityFile ~/.ssh/id_ed25519
```

Then just `ssh prod`.

### rsa or ed25519?

ed25519 by default — smaller, faster, and secure. Reach for `rsa -b 4096` only when talking to an old server that lacks ed25519 support.

## Summary

- `ssh-keygen -t ed25519` → `ssh-copy-id user@host` → `ssh user@host`.
- Use a passphrase + `ssh-agent` to stay convenient and safe.
- Fix `~/.ssh` permissions (700/600) if it won't take the key.
- Set `PasswordAuthentication no` once keys work — after testing.
