---
categories:
- Hacking
comments: true
date: "2010-07-04T20:36:42Z"
slug: garmin-map-updates
tags:
- GPS
- Ubuntu
- Garmin
title: Garmin Map Updates And Linux
wordpress_id: 340
---

I have tried to update my [Garmin](http://en.wikipedia.org/wiki/Garmin) nüvi 760 GPS Navigator, however Garmin's updater mechanism, Garmin Map Updates doesn't work on [Linux](http://en.wikipedia.org/wiki/Linux).

However after some research on the net, I found two other ways to the maps on my device:

## Buy & Download
	
* Download MapSource from Garmin and then create a map-file named GMAPPROM.IMG containing the maps needed.
* Download or buy an unlocked map IMG.

## Upload to GPS Device

After creating or buying the map update, then the following procedure can be used to transfer the maps to the device

* GMAPPROM.IMG file to the Garmin folder on the Garmin device.
* If you are using a SD or [SDHC](http://en.wikipedia.org/wiki/Secure_Digital) card, then remember to  format it FAT or [FAT32](http://en.wikipedia.org/wiki/File_Allocation_Table).
* Rename GMAPPROM.IMG to GMAPSUPP.IMG.
* Copy GMAPSUPP.IMG to a folder named Garmin on the SD or SDHC card.
* Remember to copy the map unlock / key files as well. (not needed for an unlocked map IMG)
