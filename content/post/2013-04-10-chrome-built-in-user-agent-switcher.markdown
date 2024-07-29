---
categories:
- Chrome
- User Agent
- Firefox
- Internet Explorer
- Opera
- Safari
- Browsers
comments: true
date: "2013-04-10T00:00:00Z"
title: Chrome Built-in User-Agent Switcher
---

You may need to quickly switch between user-agent strings on the fly - when
developing websites that need to work on both mobile browsers and desktop
browsers user-agent switcing is a must-have.

And some times you'll expirence some archaic site blocking you because you're
not using Netscape or Internet Explorer (in an ancient version e.g. version 6).

Chrome got a built-in user-agent switcher. All you need to do is to open the
developer tools panel (use `Ctrl+Shift+I` shortcut) and click the `wrench
button` (lower right corner) and click `Overrides`, and enable override user
agent and elect the browser or device you want to emulate and reload the page.

There is user-agent switchers and methods available for most browsers:

## Chrome

* Built-in user-agent switcher
* Using the `--user-agent` command line argument

## Safari

* [How to Activate User Agent Switcher in Safari](http://www.dummies.com/how-to/content/how-to-activate-user-agent-switcher-in-safari.html)

## Firefox

* Manipulate browser and OS identification in Firefox using ´about:config´

## Internet Explorer

* [UAPick User-Agent Switcher](http://www.enhanceie.com/ietoys/uapick.asp)

You can always check your current user agent string by visting e.g. [https://www.whatismybrowser.com/](https://www.whatismybrowser.com/detect/what-is-my-user-agent/)

My current user agent string is:
```
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31
```
