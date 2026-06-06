+++
title = "Mount a remote filesystem over SSH with sshfs (2026)"
date = 2008-03-06
updated = 2026-06-06
slug = "mount-remote-filesystem-sshfs"
description = "Mount a remote server's files locally over SSH with sshfs — no server setup needed. Install, mount with the right uid/gid, keep it alive across drops, and unmount cleanly."

[taxonomies]
tags = ["sshfs", "ssh", "fuse", "linux", "macos", "filesystem"]

[extra]
summary = "sshfs mounts a remote directory on your local machine over plain SSH — nothing to install or configure on the server. Mount it with your own uid/gid for write access, add reconnect options so it survives flaky links, and unmount with fusermount."
+++

**TL;DR —** `sshfs user@host:/remote/path /mnt/point -o reconnect,uid=$(id -u),gid=$(id -g)` mounts a remote directory locally over SSH. Unmount with `fusermount -u /mnt/point`. The server needs nothing beyond OpenSSH, which it already has.

> A 2008 note that still holds up — if anything sshfs is more useful now that everything's a remote box. Pairs nicely with [SSH key login](/post/ssh-key-login-without-password/) so the mount comes up without a password prompt.

## Why sshfs

It's a FUSE filesystem that speaks the SSH **SFTP** protocol. Because every server running OpenSSH already supports SFTP, there is **nothing to set up on the server side** — if you can `ssh` in, you can `sshfs` in. Great for editing remote files with local tools, copying across, or poking at a server's filesystem without a full sync.

## Install

```
sudo apt install sshfs        # Debian / Ubuntu
sudo dnf install fuse-sshfs    # Fedora
brew install macfuse           # macOS: needs macFUSE + the sshfs cask
```

## Mount

```
mkdir -p ~/mnt/server
sshfs user@remote.host:/home/user ~/mnt/server -o reconnect,uid=$(id -u),gid=$(id -g)
```

- **`uid`/`gid`**: map remote file ownership to *your* local user so you have read/write access (otherwise files may show up owned by someone else and be read-only).
- **`reconnect`**: transparently re-establish the connection if SSH drops.

Now `~/mnt/server` is the remote directory — use `ls`, your editor, file manager, anything.

## Keep it alive on flaky links

Network blips otherwise leave the mount hung. Add keepalive + auto-reconnect options:

```
sshfs user@host:/path ~/mnt/server \
  -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3,follow_symlinks
```

`ServerAliveInterval`/`CountMax` make SSH notice a dead link in ~45 s; `follow_symlinks` resolves remote symlinks locally.

## Unmount

```
fusermount -u ~/mnt/server     # Linux
umount ~/mnt/server            # macOS
```

Use `fusermount -uz` (lazy) if it's stuck on a dead connection.

## Mount automatically via fstab

For a mount you want back after reboot (key-based auth required, since fstab can't type a password):

```
user@host:/path  /home/me/mnt/server  fuse.sshfs  noauto,x-systemd.automount,_netdev,reconnect,uid=1000,gid=1000,IdentityFile=/home/me/.ssh/id_ed25519  0 0
```

`x-systemd.automount` mounts it on first access rather than at boot, so a slow/absent server doesn't stall startup.

## Gotchas

- **Files owned by the wrong user / read-only** → you forgot `uid`/`gid`. Set them to your local `id -u`/`id -g`.
- **"Transport endpoint is not connected"** → the SSH link died. `fusermount -uz` then remount; add `reconnect` to avoid it.
- **Slow with many small files** → SFTP is chatty; add `-o cache=yes,kernel_cache,compression=no` and avoid running e.g. `grep -r` over huge remote trees.
- **macOS** → macFUSE needs a one-time approval in System Settings → Privacy & Security after install.

## FAQ

### Is sshfs secure?

Yes — all traffic rides inside the SSH connection, same encryption as a normal SSH session.

### Does the server admin need to install anything?

No. SFTP ships with OpenSSH. If you can SSH in, sshfs works.

### sshfs vs NFS/Samba?

NFS/Samba are faster for LAN file serving but need server-side setup and open ports. sshfs needs only SSH — ideal for ad-hoc access to a remote box you can already log into.

## Summary

- `sshfs user@host:/path /mnt -o reconnect,uid=$(id -u),gid=$(id -g)`.
- Set `uid`/`gid` for write access; add `ServerAliveInterval` + `reconnect` for stability.
- Unmount with `fusermount -u` (Linux) / `umount` (macOS).
- Combine with key auth for a password-free mount.
