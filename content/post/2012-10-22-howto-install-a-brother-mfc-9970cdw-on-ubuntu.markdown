---
categories:
- Ubuntu
- Brother
- MFC-9970CDW
- CUPS
- LPR
- Linux
- Debian
comments: true
date: "2012-10-22T00:00:00Z"
title: 'Howto: Install a Brother MFC-9970CDW on Ubuntu'
---

I got a [Brother MFC-9970CDW](https://www.brother-usa.com/mfc/modeldetail.aspx?PRODUCTID=MFC9970CDW) printer, a multifunction device with  wired/wireless network.

For unknown reasons the driver are not available in Ubuntu and as as user you are not able to find them using the printer configuration search tool.

Thereby you need to download the drivers yourself.

## Download Drivers

Go to [Brother Linux Driver Downloads](https://global.brother/en) and download the `LPR driver` and the `cupswrapper driver`.

## Install the Drivers

    sudo mkdir /var/spool/lpd
    sudo dpkg -i mfc9970cdwlpr-1.1.1-5.i386.deb
    sudo dpkg -i mfc9970cdwcupswrapper-1.1.1-5.i386.deb
