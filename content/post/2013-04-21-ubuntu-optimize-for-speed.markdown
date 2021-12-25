---
categories:
- Ubuntu
- Debian
- Optimize
- Boot time
- Memory
- tmpfs
- SSD
- Firefox
- Google Chrome
- tmpfs
- zRam
comments: true
date: "2013-04-21T00:00:00Z"
title: 'Ubuntu: Optimize for speed'
---

This easy little guide will help you with simple optimization tips for speeding
up Ubuntu (12.04, 12.10, and 13.04) and other Ubuntu-based systems such as Linux
Mint. The tips come in very handy for those using older computers with low RAM
who need to boost their computer for better speed and performance and if you are
just want a really fast and snappy computer on some regular hardware.

## Removing Ubuntu One client

Saves >100 MB ram.

The following steps can be followed to completely remove the Ubuntu One client
software.

```
killall ubuntuone-login ubuntuone-preferences ubuntuone-syncdaemon
sudo rm -rf ~/.local/share/ubuntuone
rm -rf ~/.cache/ubuntuone
rm -rf ~/.config/ubuntuone
rm ~/Ubuntu\ One
```

```
sudo apt-get purge ubuntuone-client python-ubuntuone-storage*
```

## Remove unused Unity lenses

```
sudo apt-get purge \
unity-lens-friends \
unity-lens-music \
unity-lens-photos \
unity-lens-shopping \
unity-lens-video \
unity-lens-radios
```

## Optimize mount options

Ubuntu use the relatime flag for updating file metadata when files are accessed.
All these updates involve writes to the disk. We can avoid this with the
`noatime` and `nodiratime` parameters. This means that access time to files and
directories won't be tracked at all.


## Use tmpfs for /tmp and /var etc.

Add a section like this tmpfs section to `/etc/fstab`

{% gist 5459544 %}


## Move browser cache to tmpfs

```
rm -rf ~/.cache/google-chrome
ln -s /tmp ~/.cache/google-chrome
```

## Move browser profile to memory using Profile-sync-daemon

[Profile-sync-daemon
(psd)](https://wiki.archlinux.org/index.php/Profile-sync-daemon) is a diminutive
pseudo-daemon designed to manage your browser's profile in tmpfs and to
periodically sync it back to your physical disc (HDD/SSD). This is accomplished
via a symlinking step and an innovative use of rsync to maintain back-up and
synchronization between the two. One of the major design goals of psd is a
completely transparent user experience.

Running this daemon is beneficial for two reasons:
* Reduced wear to physical discs
* Speed

```
sudo add-apt-repository ppa:graysky/utils
sudo apt-get update
sudo apt-get install profile-sync-daemon
```

Adjust `/etc/psd.conf` to match your setup and then restart the
Profile-sync-daemon. Your browser(s) needs to be closed before restart of the
Profile-sync-daemon.

```
sudo /etc/init.d/psd restart
```


## Remove orphaned libraries

Over time most Ubuntu/Debian installations acquire packages which are no longer
required - they've just been pulled in to satisfy dependencies of software
you've since removed - deborphan package is probably the simplest way to get rid
of orphaned and unused packages.

```
sudo apt-get install deborphan
sudo apt-get remove --purge `deborphan`; sudo apt-get autoremove
```

## Clean browsers cache etc and vacuum browser databases.

```
sudo apt-get install bleachbit
bleachbit -c `bleachbit -l | grep cache`
bleachbit -c `bleachbit -l | grep tmp`
bleachbit -c `bleachbit -l | grep vacuum`
```

## Clean rotated log files

```
sudo bleachbit -c system.rotated_logs
```

## Clean temp and backup files

First do a dry-run and check that everything is good to go.
```
bleachbit -p deepscan.*
```

and then do the real one
```
bleachbit -c deepscan.*
```


## Disable unnecessary services and applications

Use BUM, which is a runlevel configuration tool with GUI that allows Ubuntu
users to edit and configure init services that are started when the system is
booting up or restarting. With this tool, you will be displayed with all
running and disabled services in which you can turn them on/off.

```
sudo apt-get install bum
sudo bum
```


To remove applications from startup go to `Dash` > and type `Startup Applications`.

![](/ubuntu-startup-application-preferences.webp)

Disable automatic startup of any services that are not needed (or even remove
the package completely).



## Increases performance using zRam

[zRam](https://code.google.com/p/compcache/) is a module of the Linux kernel. It
was previously called “compcache”. zRam increases performance by avoiding paging
on disk and instead uses a compressed block device in RAM in which paging takes
place until it is necessary to use the swap space on the hard disk drive. Since
using RAM is faster than using disks, zRam allows Linux to make more use of RAM
when swapping/paging is required, especially on older computers with less RAM
installed.

FYI: [Google uses zRAM for Chrome OS](http://www.chromestory.com/2013/03/google-enabling-zram-for-chrome-os-by-default/)

Enable zRam on Ubuntu:

```
sudo apt-get install zram-config
```
