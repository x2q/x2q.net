+++
title = "Transcribing Danish voice logs on a home GPU — model review + a customer-service pipeline (2026)"
date = 2026-06-10
slug = "danish-voice-log-transcription"
description = "Experiments transcribing Danish call/voice logs locally on an RTX 4070 Ti: a review of the Danish speech-to-text models (Whisper, Hviske, Røst/CoRal, cloud APIs), what actually matters for phone audio, and a private pipeline that uses Claude to turn transcripts into customer-service data."

[taxonomies]
tags = ["speech-to-text", "whisper", "danish", "asr", "hviske", "coral", "customer-service", "claude", "tailscale", "local-ai", "privacy"]

[extra]
summary = "I've been transcribing Danish voice logs locally on an RTX 4070 Ti and using Claude to turn the raw transcripts into structured customer-service data — all reachable privately over Tailscale, so the audio never leaves my own machine. This post reviews the Danish speech-to-text options (vanilla Whisper vs the Danish fine-tunes Hviske and Røst, vs cloud APIs), what actually moves word-error-rate on real phone audio, and the end-to-end pipeline for a customer-service use case, with the GDPR angle that makes 'local' the point."
faq = [
  { q = "Which speech-to-text model is best for Danish?", a = "For local use, a Danish-fine-tuned Whisper-large model beats vanilla OpenAI Whisper on Danish — the two main options are Hviske (syvai/hviske-v2) and Røst-whisper-large from the CoRal / danish-foundation-models project. Vanilla Whisper large-v3 is a solid baseline if you want one model for many languages. For a turnkey API, ElevenLabs Scribe, Azure and Google Chirp all support Danish well." },
  { q = "Can it run on a 12 GB GPU?", a = "Yes. Whisper-large-class models (including the Danish fine-tunes) fit comfortably on a 12 GB card like an RTX 4070 Ti, especially via faster-whisper (CTranslate2) with int8/float16, which also gives you several-times-real-time throughput for batch transcription of call logs." },
  { q = "Why transcribe locally instead of using a cloud API?", a = "Privacy and GDPR. Customer-service voice logs are personal data (often with names, addresses, CPR numbers). Running the transcription on your own GPU — reachable only over a private Tailscale network — means the audio never leaves your control. You decide retention, redaction, and who can reach the service." },
  { q = "What does Claude do in the pipeline?", a = "Claude is the language layer after transcription: it cleans up the raw ASR text, labels who said what, and turns a call into structured data — a summary, the customer's intent, sentiment, action items, and a QA scorecard. The transcription (audio → text) stays on the GPU; Claude works on the text." },
  { q = "How accurate is it on real phone audio?", a = "Lower than the published benchmarks. Clean read-speech benchmarks land in the low single-digit error rates, but 8 kHz telephone audio with background noise, overlapping speakers, dialect and English code-switching pushes word-error-rate much higher. Treat benchmark numbers as a ceiling, not what you'll get on a noisy call." }
]
+++

**TL;DR —** I transcribe Danish voice logs **locally on an RTX 4070 Ti**, then use **Claude** to turn the raw transcript into structured customer-service data (summary, intent, sentiment, QA score). The whole thing is reachable only over a private **Tailscale** network, so the **audio never leaves my machine** — which is the entire point for GDPR-sensitive customer data. This post reviews the Danish speech-to-text models, what actually matters on real phone audio, and the end-to-end pipeline.

> Background: this is the grown-up version of [running Whisper locally instead of a cloud Speech API](/post/local-speech-to-text-whisper-cpp/). Same instinct — keep the audio on your own box — applied to Danish call logs.

## The setup

Nothing exotic, and that's the point:

- **GPU:** a single **RTX 4070 Ti (12 GB)** — enough to run Whisper-large-class models comfortably.
- **Access:** the transcription service listens on a port (`:5000`) and is reachable **only over Tailscale** (a private WireGuard mesh). There's no public endpoint — the box has a MagicDNS name like `gpu-box.tailnet.ts.net:5000` that only devices on my tailnet can resolve or reach.
- **Two layers:** the **GPU does audio → text** (Whisper / a Danish fine-tune); **Claude does text → structure** (the customer-service intelligence). The expensive, privacy-sensitive part — the raw audio — never leaves the local network.

## Why Danish is the hard part

English ASR is basically solved. Danish is harder, and customer-service audio makes it harder still:

- **Lower-resource language.** Far less training data than English, so generic models are weaker out of the box.
- **Compound words and reduced speech.** Danish runs words together and swallows endings; the boundary between words is genuinely ambiguous.
- **Dialects.** A model can be near-perfect on standard Copenhagen Danish and fall apart on **Sønderjysk** or strong **Nordjysk**.
- **English code-switching.** Danes drop English terms mid-sentence ("jeg *resetter* lige din *account*"), which trips language-locked models.
- **Phone audio.** Real call logs are **8 kHz narrowband**, compressed, with hold music, crosstalk and background noise. This is the single biggest accuracy killer.

## The models I compared

| Model | Type | Runs | Danish | Notes |
|---|---|---|---|---|
| **Whisper large-v3 / turbo** (OpenAI) | Whisper | local (faster-whisper) | good | strong multilingual baseline; turbo is much faster |
| **Hviske** (`syvai/hviske-v2`) | Whisper-large fine-tune | local | **better on Danish** | Danish-optimised ("hviske" = *whisper*) |
| **Røst-whisper-large** (CoRal / danish-foundation-models) | Whisper-large fine-tune | local | **best on Danish** | trained/evaluated on the Danish **CoRal** corpus |
| **Røst-wav2vec2** (315M / 1B) | wav2vec2 CTC | local | strong | lighter, fast; no built-in punctuation |
| **ElevenLabs Scribe** | cloud API | hosted | very good | ~3.1% WER FLEURS / 5.5% Common Voice (vendor) |
| **Azure / Google Chirp / Amazon** | cloud API | hosted | good | turnkey, diarization built in, but data leaves your control |

The shape of it: **the Danish fine-tunes (Hviske, Røst) clearly beat vanilla Whisper on Danish**, and they fit on the 4070 Ti. Cloud APIs are excellent and convenient, but for customer data the "hosted" column is exactly the problem.

## Performance — what actually matters for voice logs

Don't read a vendor's clean-audio number and expect it on a call recording.

- **CER vs WER — don't compare directly.** The CoRal benchmark reports **character** error rate: **Røst-whisper-large ≈ 4.3% CER** overall. Vendors like ElevenLabs report **word** error rate (≈3.1% WER FLEURS). CER is usually lower than WER; they're different metrics on different (clean) data.
- **Dialect variance is huge.** On CoRal, the same model ranges from **~1.6% (Nordjysk) to ~12.6% (Sønderjysk)**. Your accuracy depends on *who's calling*.
- **The phone-audio cliff.** Clean benchmarks sit under ~8%; add 8 kHz compression, noise and overlap and real-world WER can climb **past 30–35%**. Resample to 16 kHz mono and denoise before you transcribe — it matters more than the model choice.
- **Throughput.** With **faster-whisper** (CTranslate2, int8/float16) the 4070 Ti does batch transcription several times faster than real time, so a day of call logs processes overnight.
- **Diarization and punctuation.** Whisper gives punctuation/casing for free; wav2vec2 doesn't. For "who said what" (agent vs customer) you add a diarizer (pyannote / WhisperX).

**What I'd run:** **Røst-whisper-large** (or Hviske) on **faster-whisper**, audio pre-resampled to 16 kHz mono, with pyannote for diarization. Local, Danish-tuned, fits the GPU.

## Where Claude comes in — the customer-service application

Raw ASR text isn't useful on its own. The value is what you do with it, and that's the language layer — **Claude turns a transcript into structured, actionable data**:

- **Clean-up & speaker labels** — fix ASR slips, mark **agent** vs **customer** turns.
- **Summary** — a three-line "what the call was about and how it ended."
- **Intent / topic** — classify into your categories (billing, cancellation, technical…).
- **Sentiment & escalation risk** — was the customer angry? did they threaten to leave?
- **Action items** — what the agent promised, what's still open.
- **QA scorecard** — did the agent greet, verify identity, offer the right solution, close properly?
- **Knowledge mining** — recurring questions become FAQ/help-centre candidates.
- **PII redaction** — strip names, addresses, **CPR numbers** before anything is stored or analysed.

Feed Claude the diarized transcript and a schema, get back JSON you can store, search and dashboard. A week of calls becomes a queryable dataset: top intents, sentiment trend, agents who need coaching, the FAQ writing itself.

## The pipeline in practice

```sh
# 1. Normalise phone audio: 8 kHz stereo call -> 16 kHz mono, the model's native rate
ffmpeg -i call.wav -ac 1 -ar 16000 -af "highpass=f=80,lowpass=f=7500" call16.wav

# 2. Transcribe locally on the GPU (Danish fine-tune via faster-whisper)
#    model = a Røst/Hviske Whisper-large checkpoint, served on the tailnet at :5000
curl -s -F "file=@call16.wav" http://gpu-box.tailnet.ts.net:5000/transcribe > raw.json

# 3. Diarize (who spoke when) and merge with the transcript -> turns.json
#    (pyannote / WhisperX)

# 4. Structure it with Claude: turns.json + a JSON schema -> call record
#    summary, intent, sentiment, action items, QA score, PII redacted
```

Everything up to step 3 runs on the box and over the tailnet — the **audio never touches the internet**. Step 4 sends *text* to Claude; see the privacy note below.

## The privacy / GDPR angle (this is the selling point)

Customer-service voice logs are **personal data**. Doing the transcription locally, behind Tailscale, means:

- **Audio never leaves your control** — no third-party speech API, no upload of recordings.
- **You set retention and redaction** — transcribe, extract what you need, delete the audio.
- **Access is private by default** — the service has no public endpoint; only tailnet devices reach it.

Be honest about the one boundary: in step 4, **transcript text** goes to the Claude API. That's a data-processor relationship — use a DPA, redact PII *before* sending, and prefer zero-retention. If even that's too much, swap Claude for a local LLM and keep the whole pipeline on the 4070 Ti. The architecture is the same; only the language layer moves.

## Summary

- Transcribe Danish voice logs **locally** on a 12 GB GPU; the audio never leaves your machine.
- **Danish fine-tunes win:** **Røst-whisper-large** (CoRal) or **Hviske** beat vanilla Whisper on Danish, via **faster-whisper**.
- **Benchmarks are a ceiling** — CER ≈ 4.3% on clean CoRal, but phone audio + dialect + code-switching pushes real WER far higher. Resample and denoise first.
- **Claude is the language layer:** transcript → summary, intent, sentiment, action items, QA score, PII-redacted — the actual customer-service value.
- **Keep it private:** local transcription behind **Tailscale**; redact before any text leaves; or run the LLM locally too.
