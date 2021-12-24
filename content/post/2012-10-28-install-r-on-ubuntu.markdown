---
categories:
- Ubuntu
- R
- Debian
- Big Data
comments: true
date: "2012-10-28T00:00:00Z"
title: Install R on Ubuntu
---

The statistical analysis and data mining package R is given its single 
letter name quite difficult to find help for in Google.

## What is R
R is an open source programming language and software environment for 
statistical computing and graphics. The R language is widely used among 
statisticians for developing statistical software and data analysis.

## How to Install R
    sudo apt-get install r-base

## How to use R
You can start R simply typing R (case sensitive) on your command line
    x2q@x2q:~$ R

### Examples
    > 2+2
    [1] 4
    > x <- c(1,2,3,4,5,6)
    > print(x)
    [1] 1 2 3 4 5 6
    > y <- x^2
    > print(y)
    [1]  1  4  9 16 25 36
    > mean(y)
    [1] 15.16667
    > summary(x)
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
       1.00    2.25    3.50    3.50    4.75    6.00
    > summary(y)
       Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
       1.00    5.25   12.50   15.17   22.75   36.00
