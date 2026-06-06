+++
title = "View the contents of a CSR with OpenSSL (2026)"
date = 2010-07-04
updated = 2026-06-06
slug = "view-csr-contents-openssl"
description = "Decode and verify a certificate signing request (CSR) from the command line with OpenSSL: read the subject and SANs, check the key, and confirm a CSR matches its private key."

[taxonomies]
tags = ["openssl", "csr", "tls", "certificates", "security", "linux"]

[extra]
summary = "OpenSSL can decode a CSR so you can confirm the subject, SANs, and key size before sending it to a CA. Here's the one command to read it, plus how to verify a CSR matches the private key it was generated from."
+++

**TL;DR —** `openssl req -in host.csr -noout -text -verify` decodes a certificate signing request into human-readable form and checks its signature. Use it to confirm the CN, the SANs, and the key before you hand the CSR to a CA.

> This is one of the oldest notes on this blog (2010). OpenSSL's CLI is famously sprawling, and "how do I just *read* a CSR" is a question that never goes away — so here's the refreshed version.

## What a CSR is

A **Certificate Signing Request (CSR)** is what you send to a Certificate Authority (CA) to be signed. It bundles your public key plus the identity you're requesting (the subject: common name, organisation, and — the part that actually matters now — the **Subject Alternative Names**), all signed by your private key. The CA signs it and hands back a certificate.

## Read it

```
openssl req -in host.csr -noout -text -verify
```

- **`-in host.csr`** — the request file.
- **`-noout`** — don't re-print the encoded CSR, just the decoded info.
- **`-text`** — human-readable output.
- **`-verify`** — check the CSR's self-signature (catches a corrupted or tampered request).

You'll get something like:

```
Certificate Request:
    Data:
        Version: 1 (0x0)
        Subject: C=DK, ST=Capital, L=Copenhagen, O=Example ApS, CN=example.com
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
        Requested Extensions:
            X509v3 Subject Alternative Name:
                DNS:example.com, DNS:www.example.com
    Signature Algorithm: sha256WithRSAEncryption
```

Check three things before sending it off: the **CN/subject** is right, the **SANs** list every hostname the cert must cover (modern browsers ignore the CN and only trust SANs), and the **key size/algorithm** meets the CA's minimum (2048-bit RSA or an EC key).

## Pull out just one field

When you only need the subject or the SANs (e.g. in a script):

```
openssl req -in host.csr -noout -subject
openssl req -in host.csr -noout -text | grep -A1 "Subject Alternative Name"
```

## Verify a CSR matches its private key

A common cutover mistake is generating the CSR from the wrong key. The modulus (RSA) of the CSR, the key, and the eventual certificate must all match. Compare hashes:

```
openssl req  -in host.csr      -noout -modulus | openssl md5
openssl rsa  -in host.key      -noout -modulus | openssl md5
openssl x509 -in host.crt      -noout -modulus | openssl md5
```

All three digests identical → they belong together. Any mismatch → you've got the wrong key (or wrong cert) and TLS will fail to start.

## Generate a CSR (for completeness)

```
openssl req -new -newkey rsa:2048 -nodes \
  -keyout host.key -out host.csr \
  -subj "/C=DK/O=Example ApS/CN=example.com" \
  -addext "subjectAltName=DNS:example.com,DNS:www.example.com"
```

`-addext subjectAltName=…` is the part people forget — without SANs the request is useless to a modern CA.

## FAQ

### How do I read a CSR that's in DER (binary), not PEM?

Add `-inform der`: `openssl req -in host.der -inform der -noout -text`.

### Can I paste a CSR online to decode it?

You can, but don't get in the habit — a CSR contains your public key and identity, and the paste site sees all of it. Decoding locally with OpenSSL leaks nothing.

### What's the difference between a CSR and a certificate?

The CSR is the *request* (your public key + identity, self-signed). The certificate is the CA's *signed answer*. Read a certificate with `openssl x509 -in host.crt -noout -text`.

## Summary

- Read: `openssl req -in host.csr -noout -text -verify`.
- Check the **SANs**, not just the CN — that's what browsers trust.
- Confirm key/CSR/cert belong together by comparing `-modulus | openssl md5`.
