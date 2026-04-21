+++
title = "apextowww.com — a free apex-to-www redirect service"
date = 2026-04-18
slug = "apextowww-com-apex-to-www-redirect"
description = "Free public apex-to-www redirect with automatic Let's Encrypt TLS, IPv4+IPv6, and HTTP/3. Point your naked domain at it — no signup required."

[taxonomies]
tags = ["dns", "http", "letsencrypt", "hetzner", "cloudflare-pages", "netlify", "vercel", "apex-domain"]

[extra]
summary = "A free public service that 301-redirects any apex (naked) domain to its www subdomain — with automatic Let's Encrypt TLS, IPv4+IPv6, and HTTP/3. Built for hosting platforms that require CNAME at the zone apex."
faq = [
  { q = "Can I use apextowww with Cloudflare DNS?", a = "Yes, but turn Cloudflare's orange-cloud proxy off on the apex A/AAAA records. If the proxy is on, Cloudflare intercepts the request and Let's Encrypt's HTTP-01 challenge won't reach apextowww. Once the certificate is issued and renewed, you don't need to toggle anything manually." },
  { q = "Does apextowww support wildcards or redirecting subdomains other than www?", a = "No. The service only redirects the apex to www. Everything else stays on your real host." },
  { q = "What happens if the apextowww IPs change?", a = "You'll need to update your DNS A/AAAA records. The operator publishes current IPs on the homepage and gives advance notice for changes. For a personal domain this is fine; for anything mission-critical, run your own redirector." },
  { q = "Is there a rate limit?", a = "There's no published hard limit, but this is a free community service. If you're serving millions of apex redirects a day, self-host." },
  { q = "Why not just use Cloudflare's free plan?", a = "Cloudflare's CNAME flattening at the apex is a perfectly reasonable alternative if your whole DNS is on Cloudflare. apextowww is useful when your DNS isn't on Cloudflare, or when you want a host-agnostic redirector that works identically across domains." },
  { q = "Is it really free?", a = "Yes. The marginal cost per redirect on ARM64 is negligible. No ads, no tracking beyond basic logs, no upsell." },
]
+++

**TL;DR —** DNS does not allow `CNAME` records at the zone apex ([RFC 1034 §3.6.2](https://www.rfc-editor.org/rfc/rfc1034#section-3.6.2)). That's why hosts like Netlify, Vercel, Cloudflare Pages, Firebase, and Heroku ask you to configure `www.example.com` with a `CNAME` and leave `example.com` (the apex) as a problem. [apextowww.com](https://apextowww.com) solves it: point two `A` records and two `AAAA` records at the service, and it issues a Let's Encrypt certificate for your apex and `301`-redirects every request to `https://www.yourdomain.tld/`, preserving path and query string. Free, no signup, no account.

## Why you can't put a CNAME on the apex

The DNS spec is unambiguous: a zone apex (the "bare" domain like `example.com`) must carry an `SOA` record and usually `NS` records. `CNAME` is defined as an alias that must be the only record at a name, and it is forbidden to coexist with the `SOA` and `NS` records that the apex is required to have. That's why you can `CNAME www.example.com → mysite.netlify.app` but you **cannot** `CNAME example.com → mysite.netlify.app`.

Workarounds exist, and all of them are a little awkward:

- **ALIAS / ANAME records.** Proprietary to each DNS provider (Cloudflare, Route 53, DNSimple, NS1). They work by resolving the target behind the scenes and returning an `A`/`AAAA`. Fine if your DNS provider supports it; useless if it doesn't.
- **Flattening at the provider level.** Cloudflare's "CNAME flattening" is this, done automatically for you.
- **Your own always-on VPS doing `301 → www`.** This is what I was doing for multiple domains, and it's both over-engineered and a small maintenance tax.

apextowww is the fourth option: somebody else's always-on redirector, managed for you.

## What apextowww does

Exactly one thing: a `301 Moved Permanently` from `https://yourdomain.tld/anything?x=y` to `https://www.yourdomain.tld/anything?x=y`.

- **TLS** is issued automatically on first request via the Let's Encrypt HTTP-01 challenge. No ACME client to run yourself.
- **IPv4 + IPv6** on dual-stack by design. Both apex records are required.
- **HTTP/1.1, HTTP/2, and HTTP/3** are all served. The redirect itself is trivially small, so protocol version matters less, but it helps the first-paint story when the redirect is on the critical path.
- **Path and query string** are preserved, so deep links keep working.
- **No signup, no login, no account.** If your DNS is pointed correctly, it just works.

## How to set it up

1. Go to [apextowww.com](https://apextowww.com) and copy the current IP addresses (two IPv4, two IPv6).
2. In your DNS provider, set `A` records on your apex pointing at the two IPv4 addresses. Remove any existing `A` record at the apex.
3. Set `AAAA` records on your apex pointing at the two IPv6 addresses.
4. Make sure `www.yourdomain.tld` still points at your real host (CNAME to Netlify/Vercel/Pages/etc).
5. Wait for DNS to propagate. Visit `http://yourdomain.tld/` — it should 301 to `https://www.yourdomain.tld/`.

The apextowww site has per-platform walkthroughs at `/netlify-apex-domain-redirect/`, `/vercel-apex-domain-redirect/`, `/cloudflare-pages-apex-redirect/`, `/firebase-hosting-apex-redirect/`, and `/heroku-apex-domain-redirect/`.

## Stack

- **Hetzner ARM64** servers, for cheap, low-power compute. ARM64 is ~30% cheaper per vCPU at Hetzner than x86 and runs the redirector fine.
- **Caddy-style automatic TLS** with **Let's Encrypt** HTTP-01 challenges.
- Dual-stack **IPv4 + IPv6**.
- **HTTP/1.1, HTTP/2, HTTP/3**.
- Public **static marketing site** on Cloudflare Pages, with per-platform guides in separate URL paths so they each rank independently on Google for "netlify apex redirect", "vercel apex domain", etc.

## FAQ

### Can I use apextowww with Cloudflare DNS?

Yes, but you'll want Cloudflare's proxy (orange cloud) **off** for the apex `A`/`AAAA` records. If the proxy is on, Cloudflare intercepts the request and Let's Encrypt's HTTP-01 challenge won't reach apextowww. Once the certificate is issued and renewed, you don't need to toggle anything manually; just keep it off.

### Does apextowww support wildcards or redirecting subdomains other than www?

No. The service only redirects the apex to `www.`. Everything else stays on your real host.

### What happens if the apextowww IPs change?

You'll need to update your DNS `A`/`AAAA` records. The operator publishes current IPs on the homepage and gives advance notice for changes. For a personal domain this is fine; for anything mission-critical, run your own redirector.

### Is there a rate limit?

There's no published hard limit, but this is a free community service. If you're serving millions of apex redirects a day, self-host.

### Why not just use Cloudflare's free plan?

Cloudflare's CNAME flattening at the apex is a perfectly reasonable alternative if your whole DNS is on Cloudflare. apextowww is useful when your DNS isn't on Cloudflare, or when you want a host-agnostic redirector that works identically across domains.

### Is it really free?

Yes. The marginal cost per redirect on ARM64 is negligible. No ads, no tracking beyond basic logs, no upsell.

## Why it exists

Hosting platforms optimise for their own onboarding, not for the DNS truisms that trip up every new user. Sending people to a stranger's VPS felt worse than running one myself. Now my own apex domains (including [x2q.net](https://www.x2q.net)) point at apextowww, which means I could tear down the last little redirector VPS I still had running for historical reasons.

It's the kind of project that isn't interesting until you need it, and then it's the only thing you need.
