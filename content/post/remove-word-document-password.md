+++
title = "Remove the password / editing protection from a Word document (2026)"
date = 2008-07-28
updated = 2026-06-06
slug = "remove-word-document-password"
description = "Remove read-only / editing protection from a .docx by deleting one line of XML — and the real story on password-to-open encryption, which needs office2john + hashcat to recover."

[taxonomies]
tags = ["word", "docx", "office", "password-recovery", "hashcat", "john-the-ripper", "security"]

[extra]
summary = "There are two very different 'Word passwords'. Editing/read-only protection is trivial — a .docx is a ZIP, so you delete one XML element and it's gone. Password-to-open is real AES encryption and has to be cracked with office2john + hashcat. This post covers both, honestly."
+++

**TL;DR —** if a Word doc is **read-only / restricted from editing**, a `.docx` is just a ZIP — unzip it, delete the `<w:documentProtection>` element from `word/settings.xml`, re-zip. If it's **password-to-open** (encrypted), that's real crypto: extract a hash with `office2john` and recover it with `hashcat`.

> The 2008 version of this used Office XP's "Script Editor" — long gone. The modern `.docx` format makes editing-protection removal even easier (it's a ZIP), and the distinction between *editing protection* and *real encryption* is the thing to get right. Only do this on documents you own or are authorised to modify.

## First: which kind of "password" is it?

Two completely different protections get called "password" in Word:

1. **Editing / read-only protection ("Restrict Editing").** The document opens fine; you just can't edit it. This is **not encryption** — it's a flag in the file. Trivial to remove.
2. **Password to open ("Encrypt with Password").** The document won't open at all without the password. This **is** strong AES encryption. You can't "remove" it — you have to recover the password.

## Case 1 — remove editing / read-only protection

A modern `.docx` is a ZIP archive of XML. The protection lives in one element.

```
# work on a copy
cp protected.docx unlocked.docx
mkdir extracted && cd extracted
unzip ../unlocked.docx
```

Edit `word/settings.xml` and delete the whole `<w:documentProtection .../>` element. It looks like:

```
<w:documentProtection w:edit="readOnly" w:enforcement="1"
  w:cryptProviderType="rsaAES" w:cryptAlgorithmSid="14"
  w:hash="…" w:salt="…"/>
```

Remove that one self-closing tag, then repackage:

```
zip -r ../unlocked.docx .        # re-zip the contents
```

Open `unlocked.docx` — fully editable. (The `w:hash`/`w:salt` only protect *re-enabling* the restriction in the UI; deleting the element ignores them entirely, which is why this "protection" is cosmetic.)

### Even simpler: LibreOffice

Open the file in **LibreOffice Writer → Edit → Edit Mode** (or **Format → Sections** / **Tools → Protect Document** depending on the protection), turn the protection off, and save. For form/section protection, LibreOffice toggles it without any password.

## Case 2 — password to open (encrypted)

If Word demands a password just to *open* the file, the content is AES-encrypted and there's no shortcut — you recover the password with the same hash-then-crack flow as [archive passwords](/post/crack-rar-7z-zip-passwords-linux/).

```
# office2john ships with John the Ripper
office2john protected.docx > hash.txt

# hashcat mode depends on the Office version that saved it:
#   9400 = Office 2007, 9500 = 2010, 9600 = 2013+ (most modern files)
hashcat -m 9600 hash.txt /usr/share/wordlists/rockyou.txt
```

Modern Office encryption uses a heavy KDF, so it's **slow** — a good, targeted wordlist (and a mask built from what you remember) beats brute force. If it was a long random password, it may be genuinely unrecoverable, which is the encryption doing its job.

## Old .doc (binary format)

The pre-2007 `.doc` binary format isn't a ZIP. For *editing* protection, opening and re-saving in LibreOffice usually drops it; for password-to-open, `office2john` handles old `.doc` too (it autodetects the format) — same crack flow.

## FAQ

### Is read-only protection actually security?

No. As above, it's a removable flag, not encryption — useful to prevent *accidental* edits, useless against anyone who doesn't want to be stopped. If you need real protection, use **Encrypt with Password**.

### Excel / PowerPoint?

Same model. `.xlsx`/`.pptx` are ZIPs — sheet/workbook protection is an element you can delete; password-to-open is encryption, recoverable via `office2john` (mode 9600 etc.).

### Is this legal?

On your own documents, or ones you're authorised to edit — yes. Removing protection from someone else's confidential document without permission is not.

## Summary

- **Editing/read-only**: unzip the `.docx`, delete `<w:documentProtection>` from `word/settings.xml`, re-zip — or just toggle it off in LibreOffice.
- **Password-to-open**: real encryption — `office2john file.docx > hash.txt`, then `hashcat -m 9600 …`.
- Read-only protection is not security; use real encryption if you need it.
