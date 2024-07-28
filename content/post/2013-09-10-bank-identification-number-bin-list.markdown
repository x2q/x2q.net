---
categories:
- Visa
- MasterCard
- American Express (AMEX)
- JCB
- Payments
tags:
- BIN
- IIN
- Binlist
- Account Range Definition (ARDEF)
comments: true
date: "2013-09-10T00:00:00Z"
title: Bank Identification Number (BIN) List
---

The first 6 digits of a credit card number are known as the [Issuer
Identification Number (IIN)][1], previously known as [Bank Identification Number
(BIN)][1]. Merchants use the BIN or IIN information to identify the issuing
institution, country of origin, card type and other details.

For many year I've been wondering where to get the best Binlists, but they are
hard to get outside of the card scheme organizations, such as [Visa][8] or
[MasterCard][9]. Mostly beacuse BINs are generally considered sensitive information
and is normally provided by merchant service providers, who normally are able
to supply monthly updated BIN number range tables for all cards (Visa,
MasterCard etc.) except for AMEX, Diners, JCB and Discover.

There are a lot free available binlists around, and just to mention a few:

* [Wikipedia has a List of Bank Identification Numbers][2]
* [A combined CSV of Mars Banks Base, The now-defunct Dumpz.biz, and Wikipedia from 2009][3]
* [Google Fusion Table: Bank BIN List][5]
* [Pastebin with US Bin List][6]

Most of the freely available binlist are outdated and got low accuracy.

Recently I've started to use a free Binlist webservice called [binlist.net][4],
which is a simple webservice where I'm able to get BIN and
IIN-information using a single HTTP request. I made a few tests over the last few days with
[binlist.net][4] and it seems to be quite up to date and fairly good accuracy.

## Binlist.net code example

It is really easy to use the binlist.net webservice. They offer 3 return
formats; XML, JSON and CSV.

```
$ curl -s http://www.binlist.net/json/400115 | json_pp
{
   "card_category" : "ELECTRON",
   "card_type" : "",
   "bank" : "BARCLAYS BANK PLC",
   "country_name" : "UNITED KINGDOM",
   "bin" : "400115",
   "country_code" : "GB",
   "brand" : "VISA"
}
```

I'm usually very concerned regarding response times, but they seem to be quite good
according to this simple test.

```
$ ab -c 50 -n 100  http://www.binlist.net/json/400115
This is ApacheBench, Version 2.3 <$Revision: 655654 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking www.binlist.net (be patient).....done


Server Software:
Server Hostname:        www.binlist.net
Server Port:            80

Document Path:          /json/400115
Document Length:        152 bytes

Concurrency Level:      50
Time taken for tests:   0.261 seconds
Complete requests:      100
Failed requests:        0
Write errors:           0
Total transferred:      31200 bytes
HTML transferred:       15200 bytes
Requests per second:    382.60 [#/sec] (mean)
Time per request:       130.685 [ms] (mean)
Time per request:       2.614 [ms] (mean, across all concurrent requests)
Transfer rate:          116.57 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:       41   52   5.3     53      62
Processing:    44   66  10.5     68      81
Waiting:       44   65  10.4     68      81
Total:         89  118  13.4    122     139

Percentage of the requests served within a certain time (ms)
  50%    122
  66%    127
  75%    128
  80%    131
  90%    132
  95%    132
  98%    139
  99%    139
 100%    139 (longest request)
```


Unfortunately there is no [Ruby gem][7] or PHP library available as of today.


[1]: http://en.wikipedia.org/wiki/Credit_card_number
[2]: http://en.wikipedia.org/wiki/List_of_Issuer_Identification_Numbers
[3]: http://elliottback.com/wp/bank-identification-number-bin-list/
[4]: http://www.binlist.net/
[5]: https://www.google.com/fusiontables/DataSource?docid=1QQScVqT46tTQ18pyqls3WbwJ740ouzK_65C6cw
[6]: http://pastebin.com/qN3EeGZM
[7]: http://rubygems.org/
[8]: http://en.wikipedia.org/wiki/Visa_Inc.
[9]: http://en.wikipedia.org/wiki/MasterCard
