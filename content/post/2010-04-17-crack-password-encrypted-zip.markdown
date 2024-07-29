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


[fcrackzip](https://www.kali.org/tools/fcrackzip/) is a [zip-file](https://en.wikipedia.org/wiki/ZIP_%28file_format%29) [encryption](https://en.wikipedia.org/wiki/Encryption) [cracker](https://en.wikipedia.org/wiki/Software_cracking), which can handle (recover / [crack](https://en.wikipedia.org/wiki/Password_cracking) / hack) any [password](https://en.wikipedia.org/wiki/Password) encrypted zipfile. Inside it uses a number of methods to accomplish the crack, but this happens nicely behind the scenes.

Install and fcrackzip on [Ubuntu](https://en.wikipedia.org/wiki/Ubuntu_%28operating_system%29) by typing:



    cc@zeus:~$ sudo aptitude install fcrackzip




Use the fcrackzip for [password cracking](https://en.wikipedia.org/wiki/Password_cracking) on Ubuntu by typing:



    cc@zeus:~/Desktop$ fcrackzip -v -b -p aaaa -u cuda_dxtc.pdf.zip
    found file 'cuda_dxtc.pdf', (size cp/uc 244965/294438, flags 9, chk a5d3)
    checking pw rUt~

    PASSWORD FOUND!!!!: pw == test
    cc@zeus:~/Desktop$




Happy zip-file cracking ;)

[FCrackZip website](https://www.kali.org/tools/fcrackzip/)
