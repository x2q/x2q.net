---
categories:
- Cracking
- Hacking
- Open Source
comments: true
date: "2010-04-17T21:06:29Z"
slug: crack-password-encrypted-zip
tags:
- Crack
- Debian
- Encryption
- Password cracking
- Ubuntu
- Unlock
- Windows
- Zip
title: 'How to: Crack Password Encrypted Zip Files'
wordpress_id: 182
---


[fcrackzip](http://www.goof.com/pcg/marc/fcrackzip.html) is a [zip-file](http://en.wikipedia.org/wiki/ZIP_%28file_format%29) [encryption](http://en.wikipedia.org/wiki/Encryption) [cracker](http://en.wikipedia.org/wiki/Software_cracking), which can handle (recover / [crack](http://en.wikipedia.org/wiki/Password_cracking) / hack) any [password](http://en.wikipedia.org/wiki/Password) encrypted zipfile. Inside it uses a number of methods to accomplish the crack, but this happens nicely behind the scenes.

Install and fcrackzip on [Ubuntu](http://en.wikipedia.org/wiki/Ubuntu_%28operating_system%29) by typing:

    
    
    cc@zeus:~$ sudo aptitude install fcrackzip
    



Use the fcrackzip for [password cracking](http://en.wikipedia.org/wiki/Password_cracking) on Ubuntu by typing:

    
    
    cc@zeus:~/Desktop$ fcrackzip -v -b -p aaaa -u cuda_dxtc.pdf.zip
    found file 'cuda_dxtc.pdf', (size cp/uc 244965/294438, flags 9, chk a5d3)
    checking pw rUt~ 
    
    PASSWORD FOUND!!!!: pw == test
    cc@zeus:~/Desktop$
    



Happy zip-file cracking ;)

[FCrackZip website](http://www.goof.com/pcg/marc/fcrackzip.html)
