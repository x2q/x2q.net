---
categories:
- Amazon S3
- Amazon Glacier
- WD Live
- Debian
- Duplicity
- GPG
- My Book Live
- NAS
comments: true
date: "2013-02-24T00:00:00Z"
title: Howto Backup WD MyBook Live to Amazon S3 and Glacier
---

Recently I helped a [photographer](http://www.winniemethmann.com/) to backup a large photo collection (several
terabytes) from a [Western Digital (WD)](http://www.wdc.com/) personal NAS
MyBook Live.

The [My Book Live Edition
NAS](http://en.wikipedia.org/wiki/Western_Digital_My_Book) was released by
Western Digital in 2011. They range in storage capacity from 1 to 4 TB. My Book
Live features a 1 GHz ARM processor, 256 MB of RAM, and 1000 Mbit/s ethernet
connectivity. Contrary to previous My Book Live versions it now features a
fully fledged [Debian linux distribution](http://www.debian.org/), whichs makes
the My Book Live easy to customize and adapt to different needs.

## Backup your My Book Live to Amazon S3 and Glacier

This assumes that you got SSH access to your My Book Live. If you haven't got
SSH, then do the following to enable SSH access.

### Enable SSH via hidden menu on WD My Book Live

Go to _http://mybooklive/UI/ssh_ (case sensitive)
replace "mybooklive" if you have renamed your My Book Live to something else,
or replace it with its IP address. It's a hidden UI menu to enable SSH.

Now you are able to ssh to your My Book Live via
[putty](http://www.chiark.greenend.org.uk/~sgtatham/putty/) or another ssh
client.

### Install the backup tool Duplicity etc.

      $ apt-get install python-boto duplicity util-linux trickle

I used the following Bash script as a cron job. The script features:


* exclusive locking using flock - ensures that only instance is actice at the time. This is useful, when your backup might run for several days.
* bandwidth / upload limit using trickle.
* custom temp and cache folders - this is required on a WD My Book Live as it got limited space on the root file system


{% gist 5024054 %}

Now it is time to make the script run every night. Edit your crontab:

        $ crontab -e

Add the following line

        # m h  dom mon dow   command
        42  22  *   *   *    /root/wd-live-s3-backup.sh

Then be sure to check your log files and do restore to check that everything is
good.

### Adjust S3 lifecycle rule

Amazon supports archiving of Amazon S3 Data to Amazon Glacier using lifecycle rules.

I use the following lifecycle rule for Amazon S3 and Glacier.

![](/img/s3-glacier-lifecycle-rules.webp)
