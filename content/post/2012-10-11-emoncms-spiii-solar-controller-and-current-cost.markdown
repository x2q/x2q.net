---
Tags:
- CurrentCost
- Raspberry
- SPIII
- EMONCMS
categories:
- Linux
- Raspberry Pi
comments: true
date: "2012-10-11T00:00:00Z"
title: 'EMONCMS: SPIII Solar Controller &amp; Current Cost'
---

My father has got a solar water heater system with a SPIII Solar Water Heater Controller.
The controller itself is some crappy closed source with a bad interface (non-standard compliant HTML interface) - however it works.

In order to collect all environmental data from the house we decided to buy a [Raspberry PI](https://www.raspberrypi.org/) and a few [Arduino](https://www.arduino.cc/) devices.

So far we are able to collect data from the SPIII Solar Water Heater Controller using `curl` and from the [Current Cost](http://www.currentcost.com/) device (via cosm.com as proxy) using the following bash code:

{% gist 3872852 %}
