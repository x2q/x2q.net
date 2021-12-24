---
categories:
- Howto
- Ubuntu
- Debian
- Linux
comments: true
date: "2012-10-22T00:00:00Z"
title: 'Howto: Install Adobe Air on Ubuntu'
---

For some reason Adobe only supported Linux until Adobe AIR 2.6.

## Download Adobe Air
Download Latest Version Air 2.6.0 For Linux [http://airdownload.adobe.com/air/lin/download/2.6/AdobeAIRInstaller.bin](http://airdownload.adobe.com/air/lin/download/2.6/AdobeAIRInstaller.bin) (16,1 MB)
    wget http://airdownload.adobe.com/air/lin/download/2.6/AdobeAIRInstaller.bin

## Install ia32-libs
The ia32-libs 32bit crap is needed if you want to run this in 64-bit Ubuntu.

    sudo apt-get install ia32-libs

## Install Adobe Air
    chmod +x AdobeAIRInstaller.bin
    sudo ./AdobeAIRInstaller.bin

You might get an error saying:

>"Sorry, an error has occured. Adobe AIR could not be installed. Install either
>Gnome Keyring or KDE KWallet before installing Adobe AIR.

Then you need to link a few files:

### Locate libgnome-keyring.so

    locate libgnome-keyring.so
    (my result, yours might differ)
    /usr/lib/i386-linux-gnu/libgnome-keyring.so.0
    /usr/lib/i386-linux-gnu/libgnome-keyring.so.0.2.0
    /usr/lib/x86_64-linux-gnu/libgnome-keyring.so.0
    /usr/lib/x86_64-linux-gnu/libgnome-keyring.so.0.2.0

### Create a symbolic link to your location you found using the locate command:

    sudo ln -s /usr/lib/x86_64-linux-gnu/libgnome-keyring.so.0 /usr/lib/libgnome-keyring.so.0

### Retry install

    chmod +x AdobeAIRInstaller.bin
    sudo ./AdobeAIRInstaller.bin

### Remove symbolic links after installation of Adobe AIR 2.6.0

    sudo rm /usr/lib/libgnome-keyring.so.0

