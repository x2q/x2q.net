+++
title = "Java cacerts default password — and how to use the truststore (2026)"
date = 2006-08-29
updated = 2026-06-06
slug = "java-keystore-default-password-cacerts"
description = "The default password for Java's cacerts truststore is 'changeit'. Where cacerts lives in a modern JDK, how to list it, import a certificate, and change the password with keytool."

[taxonomies]
tags = ["java", "keytool", "cacerts", "tls", "certificates", "security"]

[extra]
summary = "Java's default truststore (cacerts) password is 'changeit' — and has been forever. Here's where the file lives in a modern JDK, plus the keytool commands to list trusted CAs, import a self-signed/internal certificate, and actually change that password."
+++

**TL;DR —** the default password for Java's `cacerts` truststore is **`changeit`**. The file lives at `$JAVA_HOME/lib/security/cacerts` in any modern (Java 9+) JDK. Use `keytool` to list, import, and change the password.

> This was a two-line note in 2006 (the password and the path). Both are still right — Java never changed the default — but the path moved in Java 9, and the useful part is what you *do* with the truststore, below.

## The default password

```
changeit
```

That's it. It's the same on every JDK, every OS, and has been for the entire history of Java. (Some Linux distros that manage the system truststore set it to `changeme` — if `changeit` is rejected, try that.)

## Where cacerts lives

In a modern JDK (Java 9 and later, after the JRE/JDK merge):

```
$JAVA_HOME/lib/security/cacerts
```

On older Java 8 and earlier it was under `$JAVA_HOME/jre/lib/security/cacerts`. Find it if unsure:

```
find "$JAVA_HOME" -name cacerts
```

## List the trusted CAs

```
keytool -list -keystore "$JAVA_HOME/lib/security/cacerts" -storepass changeit
```

Add `-v` for full detail, or grep for a specific alias.

## Import a certificate (internal CA / self-signed)

The common reason you're here: a Java app throws `PKIX path building failed` / `unable to find valid certification path` because it doesn't trust an internal or self-signed cert. Import it into the truststore:

```
keytool -importcert \
  -alias my-internal-ca \
  -file internal-ca.crt \
  -keystore "$JAVA_HOME/lib/security/cacerts" \
  -storepass changeit
```

Grab the cert a server is presenting first if you don't have the file — see [inspecting a TLS certificate](/post/inspect-verify-tls-certificate-openssl/) (`openssl s_client … -showcerts`). Prefer importing the **CA** that signed the cert over the leaf cert itself, so it keeps working after renewal.

## Remove or replace an entry

```
keytool -delete -alias my-internal-ca \
  -keystore "$JAVA_HOME/lib/security/cacerts" -storepass changeit
```

## Actually change the password

The alias is literally "changeit" for a reason:

```
keytool -storepasswd \
  -keystore "$JAVA_HOME/lib/security/cacerts" \
  -storepass changeit -new <new-password>
```

In practice most setups leave the global `cacerts` at the default and instead point apps at a **separate truststore** they control (`-Djavax.net.ssl.trustStore=…`), which is cleaner than editing the JDK's own file.

## FAQ

### Should I edit the JDK's cacerts directly?

For a quick fix, sure. Better practice: keep a project-specific truststore and pass `-Djavax.net.ssl.trustStore=/path/to/store -Djavax.net.ssl.trustStorePassword=…`, so a JDK upgrade doesn't wipe your changes.

### keytool says "keystore was tampered with, or password was incorrect"

Wrong password — try `changeit`, then `changeme` (distro-managed JDKs). Confirm you're pointing at the right `cacerts` if you have multiple JDKs installed.

### Truststore vs keystore — what's the difference?

A **truststore** holds the CA certs you trust (cacerts). A **keystore** holds *your* private keys + certs (what a server presents). Same file format, opposite roles.

## Summary

- Default `cacerts` password: **`changeit`** (sometimes `changeme` on distro JDKs).
- Path (Java 9+): `$JAVA_HOME/lib/security/cacerts`.
- `keytool -list` to view, `-importcert` to trust an internal CA, `-storepasswd` to change it.
- Prefer a separate app-managed truststore over editing the JDK's own.
