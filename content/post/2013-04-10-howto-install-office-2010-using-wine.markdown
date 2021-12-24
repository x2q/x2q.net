---
categories:
- Ubuntu
- Debian
- Wine
- Microsoft
- Office
comments: true
date: "2013-04-10T00:00:00Z"
title: Howto Install Office 2010 using Wine
---

Microsoft Office 2010 is the most recent version of the Microsoft Office 
productivity suite. Formerly known as Office 14 in the initial stages of 
its beta cycle, it was released to customers in 2010.

This howto assume that you got an ISO image of the installation media.

If you are on Debian/Ubuntu you can install wine, winetricks, and winbind using
```
sudo apt-get install wine1.5 winetricks winbind
```

In order to install you'll need the following native Microsoft Windows libraries (dll files)
```
WINEARCH=win32 winetricks riched20 winhttp
```

Then mount and install
```
sudo mount -o loop -o unhide Microsoft-Office-2010.iso /mnt
WINEARCH=win32 wine /mnt/setup.exe
```

Test Excel
```
WINEARCH=win32 wine ~/.wine/drive_c/Program\ Files/Microsoft\ Office/Office14/EXCEL.EXE
```
