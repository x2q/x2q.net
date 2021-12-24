---
categories:
- Heroku
- Ruby
- Rack
- Thin
- SSL
comments: true
date: "2012-12-01T00:00:00Z"
title: Fast Static Sites with Ruby on Heroku/Cedar
---

Recently I needed a simple and fast way for serving a basic static website.

I ended up with a simple Ruby and Rack/Thin-based application, suitable for deploying to Heroku. Which means more or less no maintenance and it supports SSL - which is good in this case. For even simpler free HTML cloud hosting check out GitHub Pages.

For SSL support `Rack::SslEnforcer` is used.

{% gist 4181366 %}

## Run it locally

    $ rackup

