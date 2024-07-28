---
categories:
- Open Source
comments: true
date: "2010-07-08T17:30:38Z"
slug: git-daily-usage-branching-model
tags:
- Git
- Linux
title: Git Daily Usage and Branching Model
wordpress_id: 381
---

## What is [Git](http://git-scm.com/)


Git is a distributed [revision control](http://en.wikipedia.org/wiki/Revision_control) system with an emphasis on speed. Git was initially designed and developed by Linus Torvalds for [Linux kernel](http://www.kernel.org/) development.
Every Git working directory is a full-fledged repository with complete history and full revision tracking capabilities, not dependent on network access or a central server.

The central repository holds two main branches and a number of feature branches:


* **master**: The main branch where the source code of HEAD always reflects a state with the latest delivered development changes for the next release. Some would call this the “integration branch”. This is where any automatic nightly builds are built from.
* **stable**: When the source code in the master branch reaches a stable point and is ready to be released, all of the changes should be merged into the stable branch and then tagged with a release number.
* **feature_x: Feature X**
* **feature_y: Feature Y**
* **feature_z: Feature Z**

The feature branches are used to develop new features for the upcoming or a distant future release. When starting development of a feature, the target release in which this feature will be incorporated may well be unknown at that point. The essence of a feature branch is that it exists as long as the feature is in development, but will eventually be merged back into the master branch in order to add the new feature to the upcoming release or discarded in case of a failed experiment.


## Creating a feature branch


When starting work on a new feature, branch off from the **master** branch.


    git checkout -b feature_x master




## Push feature branch to central repository for sharing




    git checkout feature_x
    git push origin feature_x




## Merge feature into master


Finished features may be merged into the master branch to definitely add them to the upcoming release:


    git checkout master
    git merge --no-ff --log feature_x
    git branch -d feature_x
    git push origin master


The --no-ff and --log flags cause the merge to always create a new commit object, even if the merge could be performed with a fast-forward. This avoids losing information about the historical existence of a feature branch and groups together all commits that together added the feature.


## Merge features into stable




    git checkout -b stable --track origin/stable #only needed once
    git pull
    git merge --no-ff --log master
    git push
