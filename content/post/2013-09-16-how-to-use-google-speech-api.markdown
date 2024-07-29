---
comments: true
date: "2013-09-16T00:00:00Z"
published: true
categories:
- Speech recognition
tags:
- Google Speech API
title: How to use Google Speech API
---

I few years ago, Google embedded speech recognition into the [Google
Chrome][1] and the [Chromium browser][2]. Both implementation uses a
hidden API, but anyone is able to access and utilize the API as a
Speech To Text service.

The following is a short outline on how to use the Google Speech API.

## Requirements

* A [FLAC][3] file that stores the recorded speech or a mp3 file
* [Curl][4] installed (installed using e.g. `sudo apt-get install curl`)

## Prepare the FLAC

In case you got your audio stored in a mp3 file or another audio
format, then you'll need sox to convert the file to a FLAC file.

Here is the command line I used to convert the first 15 seconds of an
mp3 file into a FLAC file.

```
sox ~/speech.mp3 speech.flac trim 0 15
```

For some reason the Google Speech API only allows FLAC files upto 15
seconds.

## Query the Google Speech To Text API

```
curl -v -i -X POST -H "Content-Type:audio/x-flac; rate=16000" \
-T speech.flac \
"https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US&maxresults=10&pfilter=0&xjerr=1"
```

The result looks like this:

```json
{
  "status":0,
  "id":"f2661df1f2661df1f2661df1f2661df1124-2",
  "hypotheses": [
    { "utterance":"this is a test for speech recognition","confidence":0.7654833},
    { "utterance":"this is a fest for speech recognition"}
  ]
}
```

### Query Parameters

`-H "Content-Type:audio/x-flac; rate=16000"`
This tells the Speech API that we send a FLAC file with the bitrate of 16000 Hz.

`-T speech.flac`
This attaches the content of the speech.flac file to the HTTP POST

`client`
The client's name you're connecting from. For spoofing purposes,
let's use `chromium`

`lang`
Speech language, for example, `da-DK` for Danish, or `en-US`
for U.S. English

`maxresults`
Maximum results to return for the utterance.

`pfilter`
The porn filter ;-). Google (by default) censors the results, leading
to “Please search for ###” (pfilter!=0) instead of “Please search for
s e x” (pfilter=0).

`xjerr`
Tell speech recognition server to return errors as part of the JSON
response and not HTTP error codes


[1]: https://www.google.com/chrome
[2]: https://www.chromium.org/
[3]: https://xiph.org/flac/
[4]: https://curl.haxx.se/
