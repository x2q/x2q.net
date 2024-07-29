---
categories:
- Hacking
- Open Source
comments: true
date: "2010-08-31T18:00:29Z"
slug: squeezebox-spotify
tags:
- Debian
- Linux
- Spotify
- Squeezebox
- Ubuntu
title: Squeezebox and Spotify
wordpress_id: 846
---

## What is Spotify?

[Spotify](https://en.wikipedia.org/wiki/Spotify) is an ingenious solution to stream music, so it would be great if it could be used with the [Squeezebox](https://en.wikipedia.org/wiki/Squeezebox_(network_music_player)) - and it is actually possible using the Spotify Premium Plugin for Squeezebox Server.
Spotify offers you legal and free access to a huge library of music. All you need to do is create an account and download our streaming music player.

## Scope

* For Spotify users with a Premium account
* Plays back 320k or 160k streams
* Requires a running Squeezebox Server ([Linux](https://www.kernel.org/), [Windows](https://www.microsoft.com/WINDOWS) or Mac, could be cloud-based e.g. at [Amazon EC2](https://amazon.com))
* Will play back via Squeezebox 2 and later hardware players only


## The Install Procedure

1. Make sure you have a running >7.5.x Squeezebox server
2. Select the Spotify plugin from the recommended 3rd party plugin list and then click apply as per normal plugin installation
3. Ensure the server has restarted
4. Go to the Plugin, Settings page for "Spotify" either via the advanced menu or from the plugin page
5. Read and agree the Spotify restrictions, then add your username and password to the settings page.
6. If you refresh the settings page a couple of times you should see that a "helper app" is running and it is logged into Spotify. If not there may be an error to help...
7. Go to the "radio" menu on one of your hardware players and you should be able to browse and play tracks from Spotify.


## Spotify / Linux Adjustment

The binary files included in the plugin include the Spotify library libspotify and a closed source application built around this. This is 32-bit only so on 64-bit linux you'll need ia32-libs installed. For both 32-bit and 64-bit machines you will need libFLAC.so.8 installed (usually in flac or libflac packages of your distro) and libogg.so.0 (usually in libogg packages of your distro).

I experienced a few problems on Debian lenny, so I copied the shared objects from my Ubuntu). Using ldd to reveal any problems:

    x2q@x2q:/var/lib/squeezeboxserver/cache/InstalledPlugins/Plugins/Spotify/Bin/i386-linux$ ldd spotifyd
    	linux-gate.so.1 =>  (0xffffe000)
    	libspotify.so.4 => /var/lib/squeezeboxserver/cache/InstalledPlugins/Plugins/Spotify/Bin/i386-linux/libspotify.so.4 (0xf7cc5000)
    	libFLAC.so.8 => /var/lib/squeezeboxserver/cache/InstalledPlugins/Plugins/Spotify/Bin/i386-linux/libFLAC.so.8 (0xf7c75000)
    	libc.so.6 => /lib32/libc.so.6 (0xf7b1b000)
    	librt.so.1 => /lib32/librt.so.1 (0xf7b11000)
    	libm.so.6 => /lib32/libm.so.6 (0xf7aed000)
    	libpthread.so.0 => /lib32/libpthread.so.0 (0xf7ad6000)
    	libogg.so.0 => /var/lib/squeezeboxserver/cache/InstalledPlugins/Plugins/Spotify/Bin/i386-linux/libogg.so.0 (0xf7acf000)
    	/lib/ld-linux.so.2 (0xf7fdf000)
