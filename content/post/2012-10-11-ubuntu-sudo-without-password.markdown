---
categories:
- Open Source
comments: true
date: "2012-10-11T00:00:00Z"
tags:
- Ubuntu
- Linux
- Debian
- Sudo
title: 'Ubuntu: Sudo without password'
---

Sudo is a program that allows users to run programs with the security privileges of another user 
(normally the superuser, or root).

The `/etc/sudoers` file allows listed users access to execute a subset of commands while having the privileges of the root user.

Use `visudo` to edit `/etc/sudoers`. It can be edited manually, but it is recommended to use `visudo` to encure that the syntax is correct.

    sudo visudo

## Add Single User

Add this line at the end (change `x2q` to your username):

    x2q ALL=(ALL) NOPASSWD: ALL

## Add Group

Add this line at the end (change `%sudo` to your group name):

    %sudo ALL=NOPASSWD: ALL


Press Ctrl-X to save your changes, and exit.
