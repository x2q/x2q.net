---
categories:
- Hacking
comments: true
date: "2010-08-29T12:45:14Z"
slug: howto-install-squeezecenter-debian-ubuntu
tags:
- Debian
- SqueezeCenter
- Ubuntu
title: 'Howto: Install SqueezeCenter on Debian / Ubuntu'
wordpress_id: 638
---

A [Debian](http://www.debian.org/) [SqueezeCenter](/index.php/SqueezeCenter) (formerly known as [SlimServer](http://www.mysqueezebox.com/download)) package distributed by [Slim Devices](http://www.slimdevices.com) now exists. This package also should work with most Debian-based [Linux distributions](http://en.wikipedia.org/wiki/Linux_distribution) such as [Ubuntu](http://www.ubuntu.com), [Mepis](http://www.mepis.org) or [Knoppix](http://www.knoppix.net). See below for installation instructions for [SqueezeCenter](/index.php/SqueezeCenter).

## Add Debian and Ubuntu Repository

To install the latest stable release update your /etc/apt/ configuration using:
    sudo sh -c "echo \"# SqueezeCenter Repository\" >> /etc/apt/[sources.list](http://wiki.debian.org/Apt).d/squeezecenter.list"
    sudo sh -c "echo \"deb http://debian.slimdevices.com stable main\" >> /etc/apt/sources.list.d/squeezecenter.list"

## Install squeezeboxserver using aptitude

Ubuntu users may need to add Universe to their sources.list file. There will be two lines near the top of your existing sources.list ending in "universe" that will need to be uncommented. You will also need to run the previous two statements using the "sudo" command to gain root privileges.

    x2q@x2q.net:~$ sudo aptitude install squeezeboxserver
    Reading package lists... Done
    Building dependency tree
    Reading state information... Done
    Reading extended state information
    Initializing package states... Done
    Reading task descriptions... Done
    The following NEW packages will be installed:
    libmysqlclient15-dev{a} squeezeboxserver zlib1g-dev{a}
    0 packages upgraded, 3 newly installed, 0 to remove and 0 not upgraded.
    Need to get 41.5MB of archives. After unpacking 117MB will be used.
    Do you want to continue? [Y/n/?]
    WARNING: untrusted versions of the following packages will be installed!`

    Untrusted packages could compromise your system's security.
    You should only proceed with the installation if you are certain that
    this is what you want to do.
    
    squeezeboxserver
    
    Do you want to ignore this warning and proceed anyway?
    To continue, enter "Yes"; to abort, enter "No": Yes
    Writing extended state information... Done
    Get:1 http://http.us.debian.org stable/main zlib1g-dev 1:1.2.3.3.dfsg-12 [163kB]
    Get:2 http://debian.slimdevices.com stable/main squeezeboxserver 7.5.1 [33.7MB]
    Get:3 http://http.us.debian.org stable/main libmysqlclient15-dev 5.0.51a-24+lenny4 [7586kB]
    Fetched 41.5MB in 1s (35.5MB/s)
    Selecting previously deselected package zlib1g-dev.
    (Reading database ... 20471 files and directories currently installed.)
    Unpacking zlib1g-dev (from .../zlib1g-dev_1%3a1.2.3.3.dfsg-12_amd64.deb) ...
    Selecting previously deselected package libmysqlclient15-dev.
    Unpacking libmysqlclient15-dev (from .../libmysqlclient15-dev_5.0.51a-24+lenny4_amd64.deb) ...
    Selecting previously deselected package squeezeboxserver.
    Unpacking squeezeboxserver (from .../squeezeboxserver_7.5.1_all.deb) ...
    Processing triggers for man-db ...
    Setting up zlib1g-dev (1:1.2.3.3.dfsg-12) ...
    Setting up libmysqlclient15-dev (5.0.51a-24+lenny4) ...
    Setting up squeezeboxserver (7.5.1) ...
    Adding system user 'squeezeboxserver' (UID 104) ...
    Adding new user 'squeezeboxserver' (UID 104) with group `nogroup' ...
    Not creating home directory `/usr/share/squeezeboxserver'.
    Making sure that Squeezebox Server is not running first: No process in pidfile '/var/run/squeezeboxserver.pid' found running; none killed.
    Starting Squeezebox Server.
    Reading package lists... Done
    Building dependency tree
    Reading state information... Done
    Reading extended state information
    Initializing package states... Done
    Writing extended state information... Done
    Reading task descriptions... Done
    x2q@x2q.net:~$
