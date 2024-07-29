---
categories:
- favicon
- Gimp
- Open Source
comments: true
date: "2013-01-13T00:00:00Z"
title: Howto create a real multi-resolution favicon
---

Most favicons are created in a single resolution only, which by default is 16x16 pixels. This is often fine, but low resolution 16x16 favicons look pixelated when seen in some browsers and when used for bookmarking and application icons in e.g. IOS. Some browsers expects favicons in different sizes e.g. 16x16, 32x32, 48x48, 64x64, and 128x128.

Most browsers can deal with favicons. GIF, JPG, PNG formats, and Microsoft Icon format (.ico). The ico format is the for some reason the most used.

The good thing regarding ico files is that they are able to contain multiple images within a single ico file. We'll now exploit this feature to make a favicon contain all for four favicon resolutions in a single favicon for maximum compability using [Gimp](https://www.gimp.org/).

1. Open Gimp
2. Load a large resolution of the image you are about to make into a favicon. Minimum 128x128 pixels.
3. Make the image squared with the same pixel width and height. This can be done using Image->Canvas Size in the menu.
4. Now scale and save the image in each resolution (16x16, 32x32, 48x48, 64x64, and 128x128) as png.
5. Open the largest image png image e.g. the 128x128 png image and open the rest of the images using File->Open as layers
6. Now it is time to save a image as a ico file. Click File->Save as and type favicon.ico as file name. And you are done.
