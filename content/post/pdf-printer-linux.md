+++
title = "Print to PDF on Linux — set up a system-wide PDF printer with cups-pdf (2026)"
date = 2013-01-30
updated = 2026-06-06
slug = "print-to-pdf-on-linux"
description = "Set up a system-wide print-to-PDF printer on Linux with cups-pdf: install on Debian, Ubuntu, Fedora, or Arch, find your output folder, and print from any app or the command line."

[taxonomies]
tags = ["cups-pdf", "cups", "pdf", "printing", "linux", "ubuntu", "debian", "fedora", "arch-linux"]

[extra]
summary = "cups-pdf gives you a virtual printer that writes a PDF instead of printing to paper — available system-wide to every application, from the command line, and over the network from a headless box. Install it, restart CUPS, and your PDFs land in ~/PDF."
+++

**TL;DR —** install **`cups-pdf`**, restart CUPS, and you get a virtual **"PDF" printer** that any application can print to. The files land in **`~/PDF`** by default. On Debian/Ubuntu that's `sudo apt install printer-driver-cups-pdf && sudo systemctl restart cups`.

> This post first went up here in 2013 as a two-line note — `apt-get install cups-pdf`, restart CUPS, done. The tool is still the right answer in 2026, so here is the current, fuller version.

## Do you even need this?

Most Linux desktop apps already print to PDF on their own. GTK and KDE print dialogs (so Firefox, Chrome, LibreOffice, GNOME apps, etc.) have a built-in **"Print to File → PDF"** option. If that covers you, you're done.

`cups-pdf` earns its place when you want a **real, system-wide printer queue** rather than a per-app export:

- Available to *every* application, including ones that have no PDF export of their own.
- Usable from the **command line** and scripts.
- Shareable **over the network** from a headless server, so other machines can "print to PDF" to a central spool.

## Install

`cups-pdf` is packaged on every mainstream distro:

```
# Debian / Ubuntu / Mint / Kali
sudo apt install printer-driver-cups-pdf      # older name: cups-pdf

# Fedora
sudo dnf install cups-pdf

# Arch / Manjaro
sudo pacman -S cups-pdf
```

Then (re)start the CUPS daemon so it picks up the new backend:

```
sudo systemctl restart cups        # systemd
sudo service cups restart          # older sysvinit
```

The package's post-install step normally registers the queue for you. That's it — you can print to PDF now.

## Verify the printer exists

```
$ lpstat -p -d
printer PDF is idle.  enabled since ...
```

You're looking for a queue named **`PDF`** (sometimes `Virtual_PDF_Printer`). If it isn't there, add it by hand — first find the exact model string CUPS registered:

```
$ lpinfo -m | grep -i pdf
CUPS-PDF_opt.ppd  Generic CUPS-PDF Printer (w/ options)
```

…then create the queue with that model:

```
sudo lpadmin -p PDF -E -v cups-pdf:/ -m CUPS-PDF_opt.ppd
```

Or do it in the GUI: **Settings → Printers → Add**, pick the *Generic CUPS-PDF* printer.

## Where the files go

By default, output lands in **`~/PDF/`** for the user who submitted the job. The location is set in `/etc/cups/cups-pdf.conf`:

```
$ grep -i '^Out\|^AnonDirName' /etc/cups/cups-pdf.conf
Out ${HOME}/PDF
AnonDirName /var/spool/cups-pdf/ANONYMOUS
```

Change the `Out` directive and `sudo systemctl restart cups` to send PDFs somewhere else. Jobs that arrive without a resolvable home directory (e.g. from a shared network queue) collect under `/var/spool/cups-pdf/`.

## Print from the command line

Once the queue exists, it's a normal CUPS printer:

```
lp -d PDF report.txt          # any printable file
lpr -P PDF document.ps
```

The resulting PDF shows up in `~/PDF`. Set a default page size if the wrong one keeps appearing:

```
lpoptions -p PDF -o media=A4   # or media=Letter
```

## Headless / network "print to PDF"

On a server with no desktop you can still run the whole thing: install `cups` + `cups-pdf`, enable the daemon, and share the queue.

```
sudo systemctl enable --now cups
sudo lpadmin -p PDF -o printer-is-shared=true
```

With CUPS configured to listen on the network (`Listen`/`Allow` in `/etc/cups/cupsd.conf`), other machines can add this IPP printer and "print to PDF" remotely — the PDFs collect in the spool on the server. Handy for appliances and apps that only know how to talk to a network printer.

## Gotchas

### Nothing appears in ~/PDF

Check the job actually completed and read the CUPS log:

```
lpstat -W completed -o
sudo tail -n 50 /var/log/cups/error_log
```

Then confirm the `Out` path in `/etc/cups/cups-pdf.conf` is what you expect.

### Permission denied writing the PDF

`~/PDF` has to be writable by the CUPS spool. If you print across a shared queue as another user, output lands under `/var/spool/cups-pdf/<user>` or `…/ANONYMOUS` instead of your home directory.

### Fedora: SELinux blocks the write

If a job silently disappears on Fedora, check for an SELinux denial (`sudo ausearch -m avc -ts recent`) — the `cups-pdf` backend writing to a non-default directory is the usual trigger.

## FAQ

### Do I need cups-pdf if I use GNOME, Firefox, or Chrome?

Probably not — those export PDF directly from their print dialog. Reach for `cups-pdf` when you want one system-wide queue, command-line/scripted output, or a network print-to-PDF server.

### How do I print to PDF on Windows or macOS?

You don't need `cups-pdf`. Windows has a built-in **"Microsoft Print to PDF"** printer; macOS has a **PDF** dropdown in every print dialog. This post is Linux-only — and, as the 2013 original put it, setting this up on Linux is the easy case.

### What's the difference between this and "Print to File"?

"Print to File → PDF" in an app's dialog is per-application and exports a single file. `cups-pdf` is a genuine CUPS print queue: shared across apps, scriptable, and shareable over the network.

### Which package name — cups-pdf or printer-driver-cups-pdf?

On current Debian/Ubuntu the package is `printer-driver-cups-pdf`; `cups-pdf` is kept as a transitional name and still works. Fedora and Arch call it `cups-pdf`.

## Summary

- `sudo apt install printer-driver-cups-pdf` (or your distro's equivalent), then `sudo systemctl restart cups`.
- A virtual **PDF** printer appears; verify with `lpstat -p -d`.
- Output defaults to **`~/PDF`**, configurable via `Out` in `/etc/cups/cups-pdf.conf`.
- Print from any app's dialog, from the CLI with `lp -d PDF file`, or over the network from a headless box.
