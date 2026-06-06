+++
title = "Pretty-print XML on the command line with xmllint (2026)"
date = 2012-11-20
updated = 2026-06-06
slug = "pretty-print-xml-xmllint"
description = "Pretty-print, reformat, and validate XML from the terminal with xmllint — format a file or a stream, control indentation, and clean up minified or API XML responses."

[taxonomies]
tags = ["xmllint", "xml", "libxml2", "command-line", "linux", "payments", "3d-secure"]

[extra]
summary = "xmllint (part of libxml2, already on most systems) reformats ugly, minified, or single-line XML into something readable. Pipe an API response straight through it, control the indent width, and validate while you're at it."
+++

**TL;DR —** `xmllint --format file.xml` pretty-prints XML. Read from a pipe with `-`, control indentation with `XMLLINT_INDENT`, and write back with `--output`. It ships with **libxml2**, so it's almost certainly already installed.

> This one first went up here in 2012 — I was poking at a Visa **3-D Secure** test directory that answered in single-line XML and needed it readable. The tool hasn't changed; the flags below are the current, double-dash forms.

## The problem

API responses come back as one unreadable line. Here's the kind of thing a payment directory server hands you:

```
<?xml version="1.0" encoding="UTF-8"?><ThreeDSecure><Message><VERes><version>1.0.2</version><CH><enrolled>Y</enrolled></CH><url>https://acs.example/PIT/ACS</url></VERes></Message></ThreeDSecure>
```

## Format a file

```
xmllint --format response.xml
```

That writes the indented version to stdout. To overwrite (or write a new file):

```
xmllint --format response.xml --output response.pretty.xml
```

## Format a stream (the useful one)

Pass `-` as the filename to read stdin, so you can pretty-print straight from `curl`:

```
curl -s https://api.example/thing | xmllint --format -
```

```
<?xml version="1.0" encoding="UTF-8"?>
<ThreeDSecure>
  <Message>
    <VERes>
      <version>1.0.2</version>
      <CH>
        <enrolled>Y</enrolled>
      </CH>
      <url>https://acs.example/PIT/ACS</url>
    </VERes>
  </Message>
</ThreeDSecure>
```

## Control the indentation

By default `xmllint` indents with two spaces. Override it with the `XMLLINT_INDENT` environment variable — set it to spaces or a tab:

```
XMLLINT_INDENT="    " xmllint --format response.xml     # 4 spaces
XMLLINT_INDENT=$'\t'   xmllint --format response.xml     # tabs
```

## Recover broken XML

If the document is slightly malformed (a stray entity, a missing close tag from a truncated download), add `--recover` to format what it can instead of bailing:

```
xmllint --recover --format broken.xml
```

## While you're there: validate

`xmllint` isn't just a formatter. Check well-formedness (exit code 0 = OK), or validate against a schema:

```
xmllint --noout response.xml                       # well-formed?
xmllint --noout --schema schema.xsd response.xml   # valid against XSD?
xmllint --noout --dtdvalid doc.dtd response.xml    # valid against DTD?
```

## Install (if it's somehow missing)

```
sudo apt install libxml2-utils     # Debian / Ubuntu
sudo dnf install libxml2           # Fedora
brew install libxml2               # macOS (then use the keg's bin)
```

## FAQ

### How do I minify XML instead of pretty-printing it?

Use `--noblanks`: `xmllint --noblanks file.xml` strips the insignificant whitespace.

### Can I extract a single value instead of formatting the whole thing?

Yes — `xmllint --xpath '//url/text()' response.xml` pulls out a node with XPath. Handy for scripting against XML APIs.

### What about JSON?

`xmllint` is XML-only. For JSON, `jq .` is the equivalent ("`jq` for XML" is roughly `xmllint --format`).

## Summary

- `xmllint --format file.xml` — pretty-print a file.
- `… | xmllint --format -` — pretty-print a stream.
- `XMLLINT_INDENT` — set the indent.
- `--recover`, `--noout --schema`, `--xpath` — fix, validate, and query.
