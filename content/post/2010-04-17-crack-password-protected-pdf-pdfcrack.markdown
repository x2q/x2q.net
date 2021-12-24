---
categories:
- Cracking
comments: true
date: "2010-04-17T21:01:36Z"
slug: crack-password-protected-pdf-pdfcrack
tags:
- Cracking
- Debian
- Fedora
- Password
- PDF
- pdfcrack
- Security
- Ubuntu
- Unlock
title: Crack Password Protected PDF With pdfcrack
wordpress_id: 176
---


PDFCrack is a [GNU/Linux](http://en.wikipedia.org/wiki/Linux) application (or any other [POSIX](http://en.wikipedia.org/wiki/POSIX)-compatible system) tool for recovering [passwords](http://en.wikipedia.org/wiki/Password) and content from [PDF](http://en.wikipedia.org/wiki/Portable_Document_Format)-files. It is small, [command line](http://en.wikipedia.org/wiki/Command-line_interface) driven without external dependencies. PDFCrack is released under [GPL](http://www.gnu.org/copyleft/gpl.html).

Install and pdfcrack on Ubuntu by typing:

    
    cc@zeus:~$ sudo aptitude install pdfcrack
    


Run a quick cracking power benchmark:

    
    cc@zeus:~/Desktop$ pdfcrack -b
    Benchmark:      Average Speed (calls / second):
    MD5:                    1728972.6
    MD5_50 (fast):          97879.3
    MD5_50 (slow):          69167.0
    
    RC4 (40, static):       606555.3
    RC4 (40, no check):     598050.0
    RC4 (128, no check):    590141.7
    
    Benchmark:      Average Speed (passwords / second):
    PDF (40, user):         453510.2
    PDF (40, owner):        220250.0
    PDF (40, owner, fast):  499995.0
    
    PDF (128, user):        22000.0
    PDF (128, owner):       10408.7
    PDF (128, owner, fast): 22220.0
    cc@zeus:~/Desktop$
    


Use the pdfcrack to crack an encrypted pdf-file by typing:

    
    cc@zeus:~/Desktop$ pdfcrack test.pdf
    


Happy pdf-hacking and cracking
