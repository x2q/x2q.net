---
categories:
- Debian
- Ubuntu
- memcached
- Ruby
- Heroku
comments: true
date: "2013-04-16T00:00:00Z"
title: Howto install memcached gem on Ubuntu/Debian
---

Memcached is a general-purpose distributed memory caching system used by many
sites around. It is often used to speed up dynamic database-driven websites by
caching data and objects in RAM to reduce the number of times an external data
source (such as a database or API) must be read. Memcached runs on Unix, Linux,
Windows and Mac OS X.


The [memcached gem](https://rubygems.org/gems/memcached) requires the following
development libraries to be installed

```
sudo apt-get install libmemcached-dev libsasl2-dev
```

and then

```
sudo gem install memcached
```
