+++
title = "Inspect and verify a TLS certificate with OpenSSL (2026)"
date = 2009-05-06
updated = 2026-06-06
slug = "inspect-verify-tls-certificate-openssl"
description = "View an X.509 certificate's details with OpenSSL, check the SANs and expiry, confirm a certificate matches its private key, and inspect what a live server is actually serving."

[taxonomies]
tags = ["openssl", "tls", "ssl", "x509", "certificates", "security", "linux"]

[extra]
summary = "OpenSSL reads X.509 certificates so you can check the subject, SANs, issuer, and expiry — and confirm a cert matches the private key it's paired with. Includes the s_client trick for inspecting what a live HTTPS server is really serving."
+++

**TL;DR —** `openssl x509 -in cert.crt -noout -text` dumps a certificate in readable form. Compare `-modulus | openssl md5` of the cert and the key to confirm they match. Use `openssl s_client -connect host:443` to see what a live server serves.

> Two short 2009 notes ("view x509 details" and "verify a cert matches a key"), merged and refreshed into one. Companion to [reading a CSR](/post/view-csr-contents-openssl/) and [removing a key passphrase](/post/openssl-remove-passphrase-private-key/).

## View a certificate

```
openssl x509 -in filename.crt -noout -text
```

`filename` is the X.509 file — typically `.crt`, `.cert`, `.pem`. `-noout` skips re-printing the encoded blob; `-text` gives the human-readable view: subject, issuer, validity dates, key, and extensions.

Pull out just the fields you care about:

```
openssl x509 -in cert.crt -noout -subject -issuer -dates
openssl x509 -in cert.crt -noout -ext subjectAltName     # the SANs
openssl x509 -in cert.crt -noout -fingerprint -sha256
```

The **SANs** are the part that matters most now — browsers ignore the CN and only trust the Subject Alternative Names, so confirm every hostname is listed.

## Verify a certificate matches a private key

The classic cutover failure: the cert and key don't belong together, and TLS refuses to start. The certificate, key (and CSR) share the same public modulus — compare hashes:

```
(openssl x509 -noout -modulus -in server.crt | openssl md5; \
 openssl rsa  -noout -modulus -in server.key | openssl md5) | uniq
```

**One line of output → they match. Two lines → they don't** (`uniq` collapses identical hashes). For an EC key, compare the public keys instead:

```
diff <(openssl x509 -in server.crt -noout -pubkey) \
     <(openssl ec   -in server.key -pubout)
```

No diff → they match.

## Inspect what a live server is serving

To see the certificate an HTTPS host actually presents (expiry, chain, SANs):

```
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
```

`-servername` sends SNI, so you get the right cert on a multi-site host. Quick expiry check:

```
echo | openssl s_client -connect example.com:443 -servername example.com 2>/dev/null \
  | openssl x509 -noout -enddate
```

## Other formats

```
openssl x509 -in cert.der -inform der -noout -text   # DER (binary)
openssl pkcs12 -in cert.pfx -info -nodes              # inspect a .pfx/.p12 bundle
```

## FAQ

### "No certificate matches private key" — what now?

The cert and key are from different keypairs. Run the modulus check above; if the hashes differ, find the key that was used to generate this cert's CSR (or reissue the cert from the key you have).

### How do I check the full chain?

`openssl verify -untrusted intermediate.crt server.crt`, or inspect what `s_client` returns with `-showcerts` to see every cert the server sends.

### When does this cert expire, across many hosts?

Script the `s_client … -enddate` one-liner over a host list — it's the no-dependencies way to monitor expiry.

## Summary

- View: `openssl x509 -in cert.crt -noout -text` (and `-subject -dates -ext subjectAltName`).
- Match cert↔key: compare `-modulus | openssl md5` — one line = match.
- Live server: `openssl s_client -connect host:443 -servername host`.
