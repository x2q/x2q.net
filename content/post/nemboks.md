+++
title = "nemboks.dk — forward your Danish digital post (mit.dk, e-Boks) to your email inbox"
date = 2026-04-22
slug = "nemboks-dk-digital-post-forwarding"
description = "Nemboks forwards digital post from mit.dk and e-Boks straight to the email inbox you already read. No MitID login for every letter, no app to install."

[taxonomies]
tags = ["nemboks", "digital-post", "mit-dk", "e-boks", "denmark", "rails", "auth0", "stripe", "saas"]

[extra]
summary = "Digital post from Danish authorities lands in mit.dk and e-Boks. Nemboks forwards it to the email inbox you actually read — no MitID, no app, no surprises."
+++

**TL;DR —** [nemboks.dk](https://nemboks.dk) is a service that **forwards Danish digital post** (from [mit.dk](https://mit.dk) and [e-Boks](https://www.e-boks.com/)) straight to your email. The problem it solves: digital post is "push" in theory but pull in practice — you still have to log in with MitID, open an app, and click around to read a letter from SKAT or your kommune. Nemboks turns that into an email that lands in the inbox you already live in, attachments and all. Built for Danish SMBs where the same `virksomhed` receives post for multiple companies or employees, and where accountants, bookkeepers, and property managers want digital post in the same place as every other email. Free beta; after beta, 39 kr/md on annual billing, 49 kr/md monthly.

## The problem with Danish digital post

Since 2014, communication from the Danish public sector is digital by default. That means if your kommune, SKAT, Udbetaling Danmark, or FerieKonto needs to reach you, they drop a letter into either **[mit.dk](https://mit.dk)** (the public portal) or **[e-Boks](https://www.e-boks.com/)** (historically the most used private portal, now share-gated with Digital Post).

In principle this is great: centralised, auditable, no paper. In practice it's friction-heavy:

- **You need MitID to log in every time.** Every tax letter, parking ticket, or vacation-pay notice is gated behind an MFA flow.
- **The apps notify you, but the notifications are thin.** "You have new post" — not a subject line, not a sender, not enough to triage.
- **There's no native forwarding.** You can't say "send everything from SKAT to my accountant at `bogholder@firma.dk`."
- **Businesses inherit the worst of both worlds.** A CVR-registered company has its own mit.dk / e-Boks inbox. If the owner doesn't check it, nobody does.

Email, by contrast, is the default inbox for small businesses: shared mailboxes, forwarding rules, archiving, filters, search. Nemboks bridges the two.

## What Nemboks does

Once set up, Nemboks authenticates against your mit.dk / e-Boks on your behalf, polls your inbox for new post, and forwards each new letter — **as a real email with the PDF attached** — to the address(es) you configure.

- **One email per letter.** Subject = sender + subject. Body = plain-text preview. Attachment = the PDF.
- **Multiple companies per account.** If you're a revisor managing post for many CVRs, they all live under one Nemboks dashboard.
- **Multiple destinations per company.** Forward everything from SKAT to the bogholder, everything else to the owner, for example.
- **Keeps the original in mit.dk / e-Boks.** Nothing is deleted — Nemboks only reads.
- **Logs every forward.** For audit and peace of mind.

The practical outcome: the accountant or bookkeeper who already lives in Outlook or Gmail stops context-switching into a portal once a week.

## Who it's for

Nemboks is built for small- and medium-sized Danish businesses, especially:

- **Accountants and bookkeepers (`revisorer`, `bogholdere`).** Clients give them Nemboks access once; from then on, every SKAT letter for every client turns into an email in the shared inbox.
- **Property managers (`ejendomsadministratorer`).** A single administrator might manage post for dozens of property-owning A/S and ApS.
- **Small-company owners.** The `enkeltmandsvirksomhed` or two-person `ApS` whose owner would rather receive a letter from their municipality in the same place as their customer email.

## The stack

For the curious:

- **Rails 8** on Ruby 3.4, using Hotwire (Turbo + Stimulus) and Tailwind for the dashboard.
- **PostgreSQL** for persistence.
- **[Auth0](https://auth0.com/)** for authentication. Users sign in with Google, Microsoft, or email+password — no separate Nemboks password to forget.
- **[Stripe](https://stripe.com/)** for subscription management, including the hosted customer portal for self-service card updates and cancellations.
- **[Postmark](https://postmarkapp.com/)** for transactional email — it's the category leader for "email that must land in the inbox," which is the entire point of a forwarding service.
- **Docker + Kamal** for deployment. Zero-downtime rollouts on a small fleet; no Kubernetes to operate.
- **Cloudflare Pages** for the static marketing site at [nemboks.dk](https://nemboks.dk).

The split — Rails app on Kamal, marketing site on Pages — is deliberate. The marketing site needs to be cheap, fast, and heavily cached; the Rails app needs a database and background jobs. Running them as two separate deployments keeps each one simple.

## Pricing

- **Free beta** while the service is stabilising.
- After beta: **39 kr/md** on annual billing, **49 kr/md** monthly — VAT not included. Flat per-company pricing; no per-letter fees.
- **60-day free trial** for new customers after beta ends.

## FAQ

### Is Nemboks allowed to read my mit.dk / e-Boks?

Yes — as the inbox owner, you authorise Nemboks to read on your behalf. Nemboks only reads; it does not delete, reply, or mark as read anything you didn't configure.

### Is this GDPR-compliant?

Nemboks processes personal data on your behalf. As a customer you're the data controller; Nemboks is the data processor, and there's a standard databehandleraftale (DPA) to sign. All data is stored in the EU.

### What happens to the original letter in mit.dk / e-Boks?

It stays there. Nemboks is read-only.

### Can I forward to multiple email addresses?

Yes. Each company can have multiple forwarding destinations, and you can route different senders to different addresses (for example, everything from SKAT to the bookkeeper).

### Does Nemboks work for private individuals?

The current focus is Danish businesses (CVR). A private-individual plan may come later.

### What if Nemboks goes down?

Your post still arrives in mit.dk / e-Boks normally; Nemboks just won't forward it until the service is back. Nothing is lost.

### How do I cancel?

Through the Stripe customer portal from inside the dashboard. No email, no phone call.

## Why build it

Digital post works. It's secure, it's auditable, and I'd rather trust a SKAT letter in mit.dk than a brown envelope. But the user interface is designed for a citizen reading a handful of letters a year, not for a business receiving dozens a week across several CVRs. Email solves the "dozens a week across several mailboxes" problem well — filters, rules, shared inboxes, search — so the smallest useful bridge is to get the letters out of the portal and into email, with the PDF attached, without anyone having to log in every time.

That's Nemboks.
