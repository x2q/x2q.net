---
categories:
- Debian
- MySQL
- MariaDB
- Howto
- Tutorial
- libmysql
comments: true
date: "2013-05-05T00:00:00Z"
title: 'Howto: Install MariaDB on Debian 7/Wheezy'
---

[MariaDB][1] is a fork of [MySQL][2], which is true open source and community
maintained. MariaDB is a binary drop in [replacement][3] for MySQL. It includes
the XtraDB storage engine as a replacement for InnoDB. Its lead developer is
[Michael Widenius][4] (also known as "Monty"), the founder of MySQL.

Recently, many popular Linux distributions replaced MySQL with MariaDB as
default database server. Fedora [version => 19][5], [Archlinux][6] and
[OpenSuse][7]. Moreover Wikipedia [moved][8] to MariaDB and Mozilla [also uses][9] MariaDB.

Famous distributions often used in server environments such as Debian and
Centos have not replaced MySQL with MariaDB yet, but they'll probaly soon
migrate as well.

## Why switch to MariaDB

Well, MySQL development has basically stopped, since Oracle acquired MySQL,
whereas the MariaDB development is progessing at full speed.

Performance and licensing are the often the most predominant reasons to make a
switch from MySQL to MariaDB.

Regarding performance - here is what Wikipedia experienced, when they compared
MariaDB to the [Facebook fork of MySQL 5.1][10].

http://blog.wikimedia.org/2013/04/22/wikipedia-adopts-mariadb/ Wikipedia Adopts MariaDB

>Many query types were 4-15% faster with MariaDB 5.5.30
>under production load, a few were 5% slower, and nothing
>appeared aberrant beyond those bounds.

## Install MariaDB on Debian Wheezy

MariaDB packages are not yet available in official Debian repositories. MariaDB
provides repositories for almost every popular os here:

[https://downloads.mariadb.org/mariadb/repositories/][11]

Add the following to your `/etc/apt/sources.list`

```
deb http://ftp.osuosl.org/pub/mariadb/repo/5.5/debian wheezy main
```

and then

```
sudo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
sudo apt-get update
sudo apt-get install mariadb-server-5.5 libmysqlclient18=5.5.30-mariadb1~wheezy
```

The **libmysqlclient18=5.5.30-mariadb1~wheezy** is needed as a work-around to this
[bug][12].

This should result is something like this...

```
Reading package lists... Done
Building dependency tree
Reading state information... Done
The following extra packages will be installed:
  libaio1 libdbd-mysql-perl libdbi-perl libhtml-template-perl libmariadbclient18 libnet-daemon-perl libplrpc-perl mariadb-client-5.5
  mariadb-client-core-5.5 mariadb-common mariadb-server-core-5.5 mysql-common psmisc
Suggested packages:
  libipc-sharedcache-perl tinyca mailx mariadb-test
The following NEW packages will be installed:
  libaio1 libdbd-mysql-perl libdbi-perl libhtml-template-perl libmariadbclient18 libmysqlclient18 libnet-daemon-perl libplrpc-perl
  mariadb-client-5.5 mariadb-client-core-5.5 mariadb-common mariadb-server-5.5 mariadb-server-core-5.5 mysql-common psmisc
0 upgraded, 15 newly installed, 0 to remove and 0 not upgraded.
Need to get 32.3 MB of archives.
After this operation, 111 MB of additional disk space will be used.
Do you want to continue [Y/n]?
```

You are now ready to use MariaDB.

[1]: http://www.mariadb.org
[2]: http://www.mysql.com
[3]: https://kb.askmonty.org/en/mariadb-versus-mysql-compatibility/
[4]: http://askmonty.org/
[5]: http://fedoraproject.org/wiki/Features/ReplaceMySQLwithMariaDB
[6]: https://www.archlinux.org/news/mariadb-replaces-mysql-in-repositories/
[7]: http://www.zdnet.com/oracle-who-fedora-and-opensuse-will-replace-mysql-with-mariadb-7000010640/
[8]: http://www.zdnet.com/wikipedia-moving-from-mysql-to-mariadb-7000008912/
[9]: http://blog.mozilla.org/it/2013/01/17/mysql-5-1-vs-mysql-5-5-floats-doubles-and-scientific-notation/
[10]: https://launchpad.net/mysqlatfacebook/51
[11]: https://downloads.mariadb.org/mariadb/repositories
[12]: https://mariadb.atlassian.net/browse/MDEV-3882
