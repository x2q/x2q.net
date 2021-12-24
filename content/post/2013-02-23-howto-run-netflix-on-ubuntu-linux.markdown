---
categories:
- Ubuntu
- Linux
- Netflix
- Wine
- Silverlight
- PlayReady
- DRM
- Debian
- Filmstriben
comments: true
date: "2013-02-23T00:00:00Z"
title: Howto run Netflix on Ubuntu Linux
---

Netflix is finally working on Linux - not native, but with a patched Wine build,
you can now use Netflix under Linux.

For those who are not familiar with Netflix, it is an American provider of
on-demand Internet streaming media available to both North and South America,
the Caribbean, United Kingdom, Ireland, Sweden, Denmark, Norway, Finland.

## How to install

      $ sudo apt-add-repository ppa:ehoover/compholio
      $ sudo apt-get update
      $ sudo apt-get install netflix-desktop

The Netflix Desktop package installs all of the components necessary to run Netflix
Watch Instantly under Wine, including the Windows version of Mozilla Firefox and
Microsoft Silverlight v4. The package also includes some convience
settings to integrate Netflix into Firefox in such a way that everything feels
like a native application.

## Run Netflix

You can launch the Netflix Desktop web app through desktop Dash menu.
The Netflix Desktop application runs in full screen, but you can exit full
screen mode by pressing F11 (just like any other browser).

## Use it for websites that require Silverlight / PlayReady DRM

Start the Netflix Desktop web app and then press F11 (to exit full screen mode),
then press ALT + v and then the menu occurs, now enable the Menu Bar and
Navigation Toolbar.

Now you are able to navigate to
[http://web.sldrm.video.msn.com/](http://web.sldrm.video.msn.com/) or
[http://www.filmstriben.dk/](http://www.filmstriben.dk/).
