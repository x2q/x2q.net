+++
title = "Remove the passphrase from a private key with OpenSSL (2026)"
date = 2006-09-03
updated = 2026-06-06
slug = "openssl-remove-passphrase-private-key"
description = "Strip the passphrase from an encrypted TLS private key with OpenSSL so a server (Apache, nginx) starts without prompting — with the RSA, EC, and any-key commands and the security caveats."

[taxonomies]
tags = ["openssl", "tls", "ssl", "private-key", "nginx", "apache", "security", "linux"]

[extra]
summary = "An encrypted private key makes Apache/nginx prompt for a passphrase on every start — a problem for unattended reboots. OpenSSL can write an unencrypted copy. Here's how, for RSA/EC/any key, plus why you should lock the file down and what the safer alternatives are."
+++

**TL;DR —** `openssl rsa -in server.key -out server.key.nopass` writes a passphrase-free copy of an RSA key (use `openssl pkey` for any key type). Then `chmod 600` it. The server will start without prompting — at the cost of an unencrypted key on disk, so guard it.

> Refreshed from a 2006 note. The mechanism is unchanged; the commands below add the EC and modern any-key forms, and the security caveat it really deserves.

## The problem

If your TLS private key is passphrase-encrypted, the web server can't start unattended — it stops and waits for someone to type the passphrase. That breaks reboots, autoscaling, and config-management. The fix is an **unencrypted** copy of the key.

## Remove it

For a classic RSA key:

```
openssl rsa -in server.key -out server.key.nopass
```

For an EC (elliptic-curve) key:

```
openssl ec -in server.key -out server.key.nopass
```

Type-agnostic (works for RSA, EC, Ed25519 — the modern catch-all):

```
openssl pkey -in server.key -out server.key.nopass
```

OpenSSL prompts for the current passphrase, then writes the decrypted key. Point your server at the `.nopass` file and it'll start silently.

## Lock the file down

An unencrypted key is a plaintext credential. At minimum:

```
chmod 600 server.key.nopass
chown root:root server.key.nopass
```

Anyone who reads this file owns your certificate's identity until it's revoked. Treat it accordingly.

## Going the other way: add a passphrase

To *encrypt* a key (e.g. before moving it):

```
openssl rsa -aes256 -in plain.key -out encrypted.key
```

## Should you actually do this?

Removing the passphrase is convenient but trades away a layer of protection — a stolen disk image now hands over a working key. Consider the alternatives before reaching for `.nopass`:

- **systemd `ask-password` / a key-loading agent** can supply the passphrase at boot without baking it in.
- **A secrets manager** (Vault, cloud KMS, or the platform's secret store) hands the key to the process at runtime and never persists it in the clear.
- **Tight file permissions + full-disk encryption** mitigate the plaintext-on-disk risk if you must use an unencrypted key.

For a single hobby server, `.nopass` + `chmod 600` is a reasonable, honest trade. For anything sensitive, push the passphrase/secret out of the filesystem.

## FAQ

### Will the certificate still match after I do this?

Yes — you're only changing how the key is *stored*, not the key itself. The public key, certificate, and CSR all still match. (Verify with the modulus check in [inspecting & verifying certificates](/post/inspect-verify-tls-certificate-openssl/).)

### nginx/Apache still prompts after I switched files?

You're still pointing at the encrypted key. Check `ssl_certificate_key` (nginx) / `SSLCertificateKeyFile` (Apache) really points at the `.nopass` file, then reload.

### Can I tell whether a key is encrypted?

`head -1 server.key` — an encrypted PEM shows `Proc-Type: 4,ENCRYPTED` or a `BEGIN ENCRYPTED PRIVATE KEY` header.

## Summary

- RSA: `openssl rsa -in server.key -out server.key.nopass`; any key: `openssl pkey …`.
- `chmod 600` and restrict ownership — it's now a plaintext credential.
- Prefer a boot-time passphrase supplier or secrets manager for anything that matters.
