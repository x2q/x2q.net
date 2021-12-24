---
categories:
- Hacking
comments: true
date: "2011-02-10T10:46:45Z"
published: false
slug: upgrade-debian-lenny-squeeze
tags:
- Debian
- Linux
title: How to upgrade Debian Lenny to Squeeze
wordpress_id: 1882
---

As with the post of How to upgrade Debian Etch to Lenny, I actually know this may be know by a lot of people already, but here is how I did it, and if you ever forget can come here and remember it.

Debian Squeeze is going to be released on February 5th or 6th this 2011, so I am updating this how-to a little bit

How to upgrade Debian from Lenny to Squeeze

First edit your sources.list
    sudo vim /etc/apt/sources.list

Now change there, any word lenny to squeeze,(or from stable to testing -This will not work after the release date, so use squeeze, or stable after that date-) and save it, it could be a good idea to backup your original file before, just in case.

Updating and upgrading

    sudo apt-get update
    sudo apt-get install apt dpkg apt-get
    sudo apt-get dist-upgrade

And that is it, now you are running Debian Squeeze, it is better to use squeeze instead of testing, so when it change from testing to stable, you can decide when to go to testing again.

Remember to read the Squeeze release notes

One of the most important thing I have read is about back up.

