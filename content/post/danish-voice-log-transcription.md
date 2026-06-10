+++
title = "Transcribing 33,000 Danish voice logs on home GPUs — the local pipeline (2026)"
date = 2026-06-10
slug = "danish-voice-log-transcription"
description = "Building a local pipeline to transcribe, diarize and summarize ~33,000 Danish phone-call recordings on home GPUs: model benchmark, dual-model fusion, phone-first speaker ID, self-healing infra, and Claude Code subagents as the summary layer — with no LLM API. Plus how it maps to a customer-service function."

[taxonomies]
tags = ["speech-to-text", "whisper", "danish", "asr", "hviske", "diarization", "claude-code", "faster-whisper", "customer-service", "local-ai", "privacy"]

[extra]
summary = "Business phone calls had been recorded for 13 months — ~33,000 Danish mp3s, ~570 hours of 32 kbps phone audio. The job: transcribe everything, name the speakers, summarize per call/day/week, browsable on a site, and do it locally with no LLM API. This is the build: a benchmark of Danish ASR models, a dual-model + Claude-fusion transcription pipeline, 'phone-first' speaker identification from metadata, self-healing infrastructure across two GPUs, and Claude Code subagents as the (API-less) summary layer. Plus what it teaches about applying the same pipeline to a customer-service function."
faq = [
  { q = "Which speech-to-text model is best for Danish phone audio?", a = "In a head-to-head on the real corpus (RTX 4070 Ti), faster-whisper large-v3-turbo won on speed (~37× real-time, 1.8 GB VRAM) but the full large-v3 was noticeably more coherent on noisy Danish calls, so the pipeline runs full large-v3 plus the Danish fine-tune hviske-v3-conversation and fuses them. Voxtral hallucinated in loops on noisy audio and was dropped; vibevoice was ~6× slower than real-time." },
  { q = "Why run two ASR models instead of one good one?", a = "Because they fail differently. large-v3 has the better grammar and structure; the Danish hviske fine-tune catches Danish names and idioms large-v3 garbles. A Claude subagent reads both transcripts per call and fuses them — taking structure from one and Danish wording from the other. Two mediocre-but-diverse tracks plus a model that merges them beat a single strong track." },
  { q = "How do you identify the speakers without voice training?", a = "Metadata first. Every recording's filename carries the timestamp and both phone numbers, and a small phonebook maps numbers to names — so you know both parties before decoding a second of audio. Token-free ECAPA-TDNN clustering then splits the two voices, and reference voice profiles decide which cluster is the recurring party (the one number present on every call). A telephone call is two-party, so a 2-speaker prior fixes the common case where clustering collapses to one." },
  { q = "How were the summaries generated without an LLM API?", a = "The constraint was no API key. So Claude Code itself is the summary layer: one subagent per day reads both ASR tracks for every call, a shared name register and the previous day's summary, then writes the Danish day summary directly — ~50k–450k tokens per day-agent, no API call in the pipeline, no marginal cost. A weekly subagent synthesizes the seven day summaries." },
  { q = "Does neural denoising help ASR?", a = "Counter-intuitively, no — it hurt. A light old-school ffmpeg band-pass (200–3400 Hz) made noisy calls more coherent for free, but DeepFilterNet (a SOTA neural denoiser) caused hallucinations and dropped speech. It's tuned for human ears, not for Whisper. SOTA is task-dependent." }
]
+++

**TL;DR —** Business phone calls had been recorded for over a year: **~33,000 Danish mp3 files, ~570 hours, 32 kbps phone quality**. The brief was to transcribe all of it, name the speakers, summarize per call / per day / per week, make it browsable — and do it **locally, with no LLM API**. The result is a pipeline that runs **two ASR models and fuses them with Claude**, identifies speakers **from metadata before decoding any audio**, heals itself across **two GPUs**, and uses **Claude Code subagents as the summary layer** instead of an API. Here's the whole build, and what it teaches about a customer-service function.

> The grown-up sequel to [running Whisper locally instead of a cloud Speech API](/post/local-speech-to-text-whisper-cpp/). Same instinct — keep the audio on your own box — at 33,000-file scale.

## Start by analysing the corpses

The folder already held **nine half-finished attempts** at this problem. Before writing anything new, three agents read all nine. Between them, the dead experiments contained almost every good idea the final system needed:

- One Python attempt (WhisperX + pyannote + Claude day-summaries) was the most complete — but had hardcoded API keys, an English-alignment bug on Danish audio, and mock diarization in the "real" pipeline.
- One had discovered the key trick: **phone-first speaker identification** (more below), and had already built voice profiles.
- A Go rewrite had a beautiful service architecture and a SQLite schema — but **everything was stubs**; zero segments were ever stored. Lesson: never build the shell before the signal path works.
- A benchmark harness had already compared **six ASR models** on the corpus.

Synthesising the nine was far cheaper than inventing from scratch. **Lesson one: analyse the corpses first.**

## The model benchmark

The pre-existing benchmark (on the RTX 4070 Ti) plus a fresh side-by-side settled the model choice:

| Model | Result |
|---|---|
| **faster-whisper large-v3-turbo** | Fastest — ~37× real-time, 1.8 GB VRAM. Great, but slips on noisy Danish. |
| **faster-whisper large-v3 (full)** | Most coherent on real calls. ~18× real-time — fast enough. **Chosen.** |
| **hviske-v3-conversation** (Danish fine-tune) | Catches Danish names/idioms the others garble. **Chosen as the second track.** |
| **Voxtral** | Hallucinated in loops (1,832 words for a 117-second call), language-bleed. **Dropped.** |
| **vibevoice** | ~6× slower than real-time. **Dropped.** |

The non-obvious decision: **run two models, not one.** large-v3 and hviske **fail differently** — one has the grammar, the other has the Danish names — so keeping both and fusing them beats either alone.

## The pipeline

```
mp3 → ffmpeg band-pass (200–3400 Hz + light denoise + dynaudnorm) → 16 kHz mono
    → [A] faster-whisper large-v3 (int8_float16, beam 5, VAD, anti-loop guards)
    → [B] hviske-v3-conversation (Danish fine-tune)              ← only on calls ≥45 s
    → ECAPA-TDNN diarization (token-free clustering, 2-speaker prior on long calls)
    → "phone-first" naming (filename + phonebook anchor identities; embeddings
       decide which cluster is the recurring party; reference profiles match the rest)
    → SQLite (idempotent: SHA-256 hash + status; duplicates inherit their twin's result)

per day  → Claude subagent reads BOTH transcripts per call, fuses them, fixes
           diarization from context, writes the Danish day summary
per week → Claude subagent synthesises 7 day summaries into threads + a commitments table
web      → Flask reads the DB live (days, weeks, calls with audio, search, patterns)
```

A few decisions earned their place:

- **Phone-first speaker ID.** The filename carries the timestamp and both numbers; a small phonebook maps numbers to names. You know *both* identities before decoding a word — audio only has to decide *which voice is which*, not *who they are*. **Metadata is gold.**
- **ffmpeg band-pass helps; DeepFilterNet hurts.** Measured: a 50-year-old band-pass filter made noisy calls more coherent for free; the SOTA neural denoiser caused hallucinations and dropped speech. **SOTA is task-dependent.**
- **ECAPA over pyannote.** pyannote OOM'd next to Whisper on a 12 GB card and was too slow on CPU for 33k files. Token-free ECAPA clustering on the GPU, with a **2-speaker prior** (a phone call *is* two-party), fixed the 79% of long calls that otherwise collapsed to a single speaker.
- **int8_float16 + expandable segments** let **both** models coexist in ~6–8 GB on the 12 GB card.

## The summary layer: Claude Code subagents, no API

The hard constraint was **no LLM API key**. So the harness itself is the language model: **one Claude Code subagent per day** receives both ASR tracks for every call, a shared name register, and the previous day's summary, and writes the day summary directly — ~50k–450k tokens per day-agent, **no API call in the pipeline, no marginal cost.**

Three small "institutions" grew around it:

- **A fusion instruction file** — the merge rules ([A]'s structure, [B]'s Danish words), fix diarization from context (a caller stating their own name pins that speaker), skip voicemails, **never invent content, report uncertainty honestly.**
- **A shared, growing name register** — agents read it before writing and append new clarifications. Over 60+ days it reconciles spelling variants of the same contact into one confirmed identity and keeps two same-named people apart. Name consistency across the whole corpus, accreted one day at a time.
- **A weekly commitments table** — each week's agent carries a "promises & deliveries" table forward (✅/⏳/❌). A genuinely useful primitive (and, as we'll see, the bridge to customer service).

## Running it across two machines

Idempotency made the corpus splittable mid-run:

- **Machine 1 (RTX 4070 Ti, 12 GB):** the full dual-model pipeline, working chronologically forward.
- **Machine 2 (GTX 1060, 6 GB, Pascal):** deployed over SSH/Tailscale with one script; took a later partition. Runs only the [A] track in int8 (new CUDA wheels dropped Pascal, so torch is on CPU while CTranslate2 drives the GPU directly).
- **Merge:** the worker writes its own SQLite; the main box pulls and merges every 15 minutes (idempotent — `transcribed` can be upgraded to `done`). The corpus is processed **from both ends at once.**

Because every file is keyed by **SHA-256 hash + status**, moving half the work to another machine mid-run was harmless. **Idempotency is the freedom to fail.**

## Self-healing, learned the hard way

Long unattended runs fail in creative ways. Each failure got a permanent countermeasure:

1. **Two transcription processes on one GPU** (an orphan survived a restart) → mutual OOM poisoning, 756 failed rows. Fix: a `flock` singleton in the supervisor + auto-kill of orphans on startup.
2. **The "poison file" myth** — a file looked like it crashed the process repeatedly; it was actually the dual-process conflict. It ran fine on retry. The supervisor got retry-once-then-quarantine logic anyway.
3. **Silent hangs** — a worker hung for an hour on one file (process alive, no progress). Fix: a watchdog that kills the inner process after 20 minutes with no DB activity (DB mtime as the progress signal).
4. **An outer watchdog every 10 minutes** checks the supervisor, DB progress and web server locally — and all of it on the worker over SSH — and auto-restarts.
5. **False "ready" days** — a max-date heuristic declared a day finished while 93 of its 104 files were still missing. Fix: **the inbox is ground truth** — a day/week is ready only when *every* one of its files has a settled DB row. **Ground truth beats heuristics; the max-date guess lied twice, the inbox count never did.**
6. **Anonymous calls** — files from a withheld number didn't match the filename pattern and went invisible to day-grouping. Parser widened, rows repaired.
7. **A duplicate bug** — identical audio under a new name was marked `done` with no transcript (one hash shared by 103 empty ring-out files) and polluted the day dumps. Now duplicates inherit their twin's status and content.
8. **Reaped background processes** — `nohup` jobs were harvested by the environment and died unnoticed for hours. Fix: all long-running work as harness-managed background tasks, with the watchdog as backstop.

**Self-healing has to be layered:** process-level (supervisor: crash / hang / poison / orphan) *and* system-level (watchdog: supervisor dead? web down? worker gone?).

## The numbers (as of this writing)

| | |
|---|---|
| Corpus | ~33,000 mp3, ~570 audio hours, 13 months |
| Processed | ~6,100 files (19%), from both ends |
| Summaries | 60 daily + 7 weekly |
| Local speed | dual-model ~0.2 RTF; ~430 files/hour |
| Day-agent cost | ~50k–450k subagent tokens/day (avg ~200k) |
| Diarization | 2-speaker prior + context repair rescued the 79% of long calls that collapsed to one voice |

## How this maps to a customer-service function

The original use case is personal call intelligence, but the exact same pipeline is a **customer-service** system:

- **Two-track ASR + LLM fusion** → accurate Danish transcripts of support calls.
- **Per-call / per-day / per-week summaries** → QA without listening to every call.
- **The commitments table** generalises directly to **SLA / promise tracking** — what an agent promised a customer, and whether it was delivered, carried week to week.
- **The shared name register** → a consistent customer/contact directory built from the calls themselves.
- **The patterns view** (volume by hour, call-direction asymmetry, recurring topics) → staffing and escalation insight, all from metadata + summaries.
- **PII discipline** is built in: the "never invent, flag uncertainty" rule, and redaction before anything is stored.

And the privacy story is the selling point: everything runs **locally behind Tailscale** — audio never leaves the building, you set retention and redaction, and there's no public endpoint. (The honest boundary: if your language layer is a cloud LLM API rather than a local harness, that text leaves — so redact first or keep the LLM local too.)

## The lessons, distilled

1. **Analyse the corpses first** — nine dead experiments held almost every right idea. Synthesis beats invention.
2. **Metadata is gold** — filenames alone gave speaker identity, day structure and the whole pattern analysis before a second of audio was decoded.
3. **Two mediocre, diverse ASR tracks + a model that fuses them beat one good track.** Error diversity is the point.
4. **SOTA is task-dependent** — neural denoise *hurt* ASR measurably; a 50-year-old band-pass helped.
5. **Idempotency is the freedom to fail** — hash + status made every crash, restart and mid-run migration harmless.
6. **Self-healing in layers** — supervisor for the process, watchdog for the system.
7. **Ground truth over heuristics** for progress gates — count the inbox, don't guess from the max date.
8. **An LLM can be the pipeline's expensive step without an API** — when the harness itself is the model, a "summary stage" is a subagent with a good instruction file, a shared register, and an honesty norm.
