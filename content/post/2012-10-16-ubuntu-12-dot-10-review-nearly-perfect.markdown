---
categories:
- Ubuntu
- Linux
- Review
comments: true
date: "2012-10-16T00:00:00Z"
title: 'Ubuntu 12.10 Review: Nearly perfect'
---

When I last upgraded to [Ubuntu 12.04](http://www.ubuntu.com/), I was quite disappointed. Mostly because it was a LTS release and though you do not expect buggy and unpolished components.

Back to Ubuntu 12.10.


## Installation
The installation is simple and for the first time ever my girlfriend was able to install Ubuntu without my support. During the installation she even mentioned that is was incredible easy and straight forward.

The best thing about the installation is the fact that you don't waste time during the installation process. The installer simply starts the installation right after you've chosen the partition scheme and then while it installs you are asked for additional user details, username, password, timezone etc.

All in all quite efficient and almost as polished as the Mac installer. And a lot faster than the Windows installer.


## Bootup & Boot time
>Ubuntu 12.10 feels faster compared to Ubuntu 12.04. But in essence boot time
>shouldn't be more than 5 seconds and Ubuntu 12.10 is still far from this, when
>using a regular disk drive, but when {"tested on a modern SSD I ended up with a
>boot time of ~10 seconds"}.

Compared to Mac OS, Ubuntu still got a few flaws. For example random text messages occurs randomly during boot and shutdown from time to time. Not a problem as a such, but Mr. Jobs would never accepted a product release with this kind of unpolished user experience. Who said Apple Maps.


## The Desktop
The overall look and feel is simply great, but the new sponsored items in the dash is simply annoying and leaves the desktop area as a cluttered space. However with the annoying sponsored Amazon content uninstalled the Ubuntu desktop is a pleasure. It is fast and quite responsive, don't get me wrong there is still room for improvements.

The annoying shopping unity lens can be removed by:
    sudo apt-get install unity-lens-shopping

The Mac inspired reworked `System Settings` is really a step in the right direction. It is pleasant to use, however why aren't all configuration items shown, e.g. `Desktop Sharing`?


## Behind the Scenes
Looking into the machine room with `ps aux` and `top` was a mixed experience.

    RSS     COMMAND
    40m     /usr/bin/python /usr/lib/ubuntuone-client/ubuntuone-syncdaemon
    30m     /usr/bin/python3 /usr/lib/unity-lens-photos/unity-lens-photos
    19m     /usr/bin/python /usr/lib/unity-scope-video-remote/unity-scope-video-remote
    16m     /usr/bin/python /usr/lib/unity-lens-video/unity-lens-video
    13m     update-notifier
     8m     /usr/lib/evolution/evolution-source-registry
     7m     /usr/lib/gwibber/unity-gwibber-daemon
     4m     /usr/lib/x86_64-linux-gnu/deja-dup/deja-dup-monitor

All in all there is a lot processes - most of them are needed, but a significant number of the processes are simply not needed. The ubuntuone-syncdaemon is running even when it is not configured yet and the same for the deja-dup-monitor.

The update-notifier is running constantly. Personally, I think that the unity-lenses are consuming quite a bit memory, even though memory is cheap today.

## Conclusion
Ubuntu 12.10 is yet another step in the right direction. It is nearly perfect, when the cluttered sponsor content unity-lenses, misc memory hungry processes, and processes slowing bootup are uninstalled.
