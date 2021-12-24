---
categories:
- Ubuntu
- Debian
- pdf
- Cups
comments: true
date: "2013-01-30T00:00:00Z"
title: Howto Setup PDF Printer on Linux
---

Installing a pdf-printer on Windows is crap, but in Linux/Ubuntu/Debian it is quite easy.
    
    $ sudo apt-get install cups-pdf

Then restart your cups daemon

    $ sudo service cups restart

And you are ready to print to pdf files.
