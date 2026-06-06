+++
title = "Find which process is using a port on Linux (ss, lsof, fuser) — 2026"
date = 2026-06-05
slug = "find-process-using-port-linux"
description = "‘Address already in use’? Find the PID listening on a port on Linux with ss, lsof, or fuser, then kill it — plus the modern ss replacement for netstat."

[taxonomies]
tags = ["linux", "networking", "ss", "lsof", "netstat", "debugging"]

[extra]
summary = "When a server won't start because the port is taken, you need the PID holding it. ss is the modern one-liner; lsof and fuser are the alternatives. Here's how to find the process and free the port."
+++

**TL;DR —** `sudo ss -ltnp | grep :8080` shows the process listening on port 8080. Then `kill <pid>`. `ss` is the modern replacement for the deprecated `netstat`; `lsof -i :8080` and `fuser 8080/tcp` do the same job.

## ss — the modern way

`ss` (from `iproute2`) ships on every current distro and replaced `netstat`. To see what's **listening**:

```
sudo ss -ltnp
```

- **`-l`** listening sockets
- **`-t`** TCP (use `-u` for UDP)
- **`-n`** numeric — don't resolve ports to names (faster, clearer)
- **`-p`** show the **p**rocess (needs root to see other users' processes)

Filter to one port with `ss`'s own expression (no grep needed):

```
sudo ss -ltnp 'sport = :8080'
```

```
State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process
LISTEN  0       511           0.0.0.0:8080       0.0.0.0:*      users:(("node",pid=4123,fd=18))
```

There's your PID: `4123`.

## lsof — the alternative

```
sudo lsof -i :8080            # anything using port 8080
sudo lsof -iTCP:8080 -sTCP:LISTEN   # only the listener
```

`lsof` prints the command, PID, and user per line. It isn't installed everywhere by default (`sudo apt install lsof`), but it's the most readable for "who has this port *and* in what state".

## fuser — the quick one

```
sudo fuser 8080/tcp
```

Prints just the PID(s). It can even kill in one shot:

```
sudo fuser -k 8080/tcp       # send SIGKILL to whatever holds 8080/tcp
```

Convenient, but blunt — it'll `kill -9` without asking, so know what you're terminating first.

## netstat — only if you're stuck on an old box

The classic `netstat -tulpn` still works where it's installed, but `netstat` is deprecated and missing from minimal modern images. Prefer `ss`; the flags are nearly identical.

## Free the port

Once you have the PID, stop it gracefully first, then escalate only if it ignores you:

```
kill 4123          # SIGTERM — lets it shut down cleanly
kill -9 4123       # SIGKILL — last resort, no cleanup
```

If it's a managed service, stop it properly so it doesn't just respawn:

```
sudo systemctl stop myapp
```

## Gotchas

- **No process shown?** You're not root. The `-p`/`-i` process columns are empty for sockets you don't own — re-run with `sudo`.
- **Port still "in use" after the process died.** A closed TCP socket lingers in `TIME_WAIT` for a couple of minutes. Either wait, or set `SO_REUSEADDR` in your server (most frameworks have a "reuse address" flag).
- **It came back immediately.** A supervisor (systemd, Docker, pm2) restarted it. Stop the supervisor unit, not the child PID.
- **IPv6 vs IPv4.** `0.0.0.0:8080` is IPv4; `[::]:8080` is IPv6. A process can hold both — `ss -ltnp` lists each separately.

## FAQ

### How do I see established connections, not just listeners?

Drop `-l`: `sudo ss -tnp` shows active connections. Add `state established` to filter.

### What's using a UDP port?

Swap `-t` for `-u`: `sudo ss -lunp 'sport = :53'` (e.g. to find what's on DNS).

### One-liner to kill whatever is on a port?

`sudo fuser -k 8080/tcp`, or `sudo kill $(sudo lsof -t -i:8080)`. Use with care.

## Summary

- Find it: `sudo ss -ltnp 'sport = :8080'` (modern), `sudo lsof -i :8080`, or `sudo fuser 8080/tcp`.
- Free it: `kill <pid>` first, `kill -9` only if needed, or stop the systemd unit.
- `ss` replaces `netstat` — same idea, fewer surprises on modern systems.
