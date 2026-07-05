+++
title = "We thought the model was the problem. It wasn't."
date = 2026-07-05
slug = "speaker-identification-five-rounds"
description = "Five rounds of speaker fingerprinting on phone calls: from a model that 'couldn't tell voices apart' to 87.2% accuracy — but only after discovering the model was never the problem. No names, method only."

[taxonomies]
tags = ["speaker-identification", "voice-fingerprint", "diarization", "machine-learning", "whisper", "data-science", "evaluation"]

[extra]
summary = "A speaker-identification experiment on phone calls went through five rounds — from a conclusion that 8kHz phone audio 'drowns speaker identity in noise' (EER 35-45%), to a methodology breakthrough (82-92% on a real gold set), to a reality check that crashed to 59.5% on blind calls. The fix wasn't a better model — it was discovering that 68% of 'single-speaker' clips actually contained two voices. Cleaned of those: 87.2% accuracy, AUC 0.856."
faq = [
  { q = "What is speaker fingerprinting?", a = "Speaker fingerprinting (also called speaker identification or speaker verification) is the task of determining whose voice a given audio segment belongs to — as opposed to speaker diarization, which only determines which segments belong to the same (unnamed) speaker. Typically an embedding model (e.g. ECAPA-TDNN) produces a numeric 'fingerprint' of a voice, which is then compared against known references." },
  { q = "Why did the model perform badly at first?", a = "Not because the model was bad at voice recognition — because the evaluation method was wrong. Training data came from the pipeline's own, partly-collapsed diarization labels (noise measured against noise), and the task being measured (cross-call verification) was harder and less relevant than the actual task (within one call, which cluster is the line owner?)." },
  { q = "What was the real cause of the poor results on real calls?", a = "Human verification of random audio clips showed that 68% of the clips the pipeline had labelled 'single speaker' actually contained audible traces of two different voices. The model was trying to identify one speaker in clips that genuinely contained two — that's not a model problem, it's a data-quality problem upstream in the diarization step." },
  { q = "What was the final accuracy?", a = "87.2% accuracy with an AUC of 0.856 — but only when measured on clips a human confirmed were clean (single-speaker only). On a completely random, unblinded sample of real calls, agreement with the existing labels was only 59.5%, because the majority of clips were genuinely mixed." },
  { q = "Why didn't channel fingerprinting work?", a = "The idea was to exploit the fact that the line owner's side of every call passes through the same phone equipment, producing a recognisable channel signature. But the calls are recorded as a single shared mono channel for both speakers at once — there is no separate 'owner channel' to fingerprint apart from the other party." }
]
+++

We run a pipeline that transcribes and summarises thousands of phone calls. One of the last unsolved problems was simple to state and infuriating to solve: **who is actually speaking in each call?**

Diarization (splitting audio into "speaker A" and "speaker B") works fine at the technical level — but knowing *who* speaker A and B *are* as people is an entirely different task. We tried five rounds. The fifth finally gave an answer — just not the one we expected.

> This is a follow-up to [five alternatives to pyannote](/post/diarization-five-alternatives/) and [the full voicelog pipeline](/post/danish-voice-log-transcription/). No names, phone numbers, or business details appear in this post — method and numbers only.

## The starting point: "the channel dominates identity"

The first three rounds of experiments landed on something depressing: on 8kHz phone audio, voice identity drowns in noise from the phone line and codec. A modern speaker-embedding model (ECAPA-TDNN) could barely distinguish two different people better than random guessing, measured at an Equal Error Rate of 35-45%.

The conclusion looked solid. It was wrong.

## Round 4: questioning our own method

We asked a different model to adversarially critique our own work — with no investment in the conclusion. It found two fatal methodology errors:

1. **Circular labels.** Our training data came from the pipeline's own speaker labels — the same pipeline we were trying to improve. 40% of calls had collapsed diarization (a single name on every segment). We were measuring noise against noise.
2. **The wrong task.** We measured cross-call verification (is voice A from call 1 the same person as voice B from call 2?), but the *actual* task is much easier: within a single call, which of the two clusters is the line owner? Here, the shared phone channel cancels out of the comparison — the exact confound we thought dominated everything.

We rebuilt a gold set from transcript self-introductions ("this is [name]") instead of pipeline labels, and re-scored the *same* embeddings on the *right* task. Result: **82-92% accuracy.** Same model. Same data. Just measured correctly this time.

## The reality check that didn't hold up

Before celebrating, we tested the method blind on the 100 most recent real calls — not the curated gold set, just ordinary conversations.

**59.5% agreement with the pipeline's existing labels.** Basically a coin flip.

And confidence was *inversely* calibrated: the more certain the model was, the more often it was wrong. That's not noise. That's a systematic problem.

## Five attempts to close the gap — none of them worked

We tried:

- **Text + behavioural fusion** (word choice, speaking-time share, turn-taking): 92% on the gold set, 100% on the one known hard confusion pair. Collapsed to an identical 62% on blind real calls — the same selection bias baked into the gold set itself.
- **Channel fingerprinting** (exploiting that the line owner's side of every call runs through the same equipment): near-random. Turned out the entire call — both speakers — shares one mono-recorded channel, so there's no separate "owner channel" signature to find.
- **Domain adaptation via Common Voice**: this delivered the first real breakthrough in *explanation*, not solution. We took a fully independent dataset with reliable ground truth, ran it through our phone-channel simulation, and tested the same model: **100% on clean speech, 98.7% on phone-simulated speech.** The model can handle phone audio just fine. Our foundational assumption since round 1 was wrong.
- **Formant/pitch landmarks** (Shazam-inspired): real signal, but underperformed the acoustic model.
- A trained meta-classifier over all signals at once: didn't beat the simple acoustic model alone.

## The manual labelling that solved it

We built a mobile-friendly page where a human could confirm: is this audio clip the line owner, or someone else? Random sample — no automated bias.

**68% of clips contained audible traces of BOTH speakers.**

We tested whether this was just an artefact of our clipping method: rebuilt it from scratch (fewer, longer segments, edge trimming, pauses between splices). Same rate, to the decimal: 68.2% before, 68.2% after.

## The chapter that closes the story

We scored only the clips a human had confirmed were *clean*, drawn from a completely random population.

**87.2% accuracy. AUC 0.856.**

The model was never the problem. The problem was that as many as 2 out of 3 "single-speaker" clusters actually contain two people's voices.

## The bonus findings along the way

Human verification surfaced three real errors in our contact register that no one had noticed — mismatched people conflated into one, a family member misregistered as a business contact, and a name mistyped years ago.

## What we're taking away

- **Distrust your own evaluation method**, especially if labels come from the system you're trying to improve.
- **Test on a population you didn't curate yourself.**
- **Separate confidence from correctness.** A well-calibrated system gets more accurate as it gets more confident — if the opposite happens, you're chasing the wrong problem.
- **Simple methods win until you have enough data to justify complexity.**
- **Human verification is still the cheapest path to the truth**, once you know exactly which question to ask.

> See also [five alternatives to diarization](/post/diarization-five-alternatives/) for the technical step that comes *before* this one — splitting audio into speakers before trying to identify them — and [the Whisper backend shootout](/post/whisper-backend-shootout/) for the transcription layer underneath all of it.
