+++
title = "Fine-tuning Whisper for Danish phone calls: a LoRA post-mortem (2026)"
date = 2026-07-02
slug = "danish-whisper-lora-finetune"
description = "Fine-tuning whisper-large-v3 on CoRal-v3 for Danish phone audio: a training-loss bug that looked like fundamental model instability but was a warmup-schedule mistake, a benchmark that nearly halved WER, and a systematic audit that found the benchmark wasn't the whole story."

[taxonomies]
tags = ["speech-to-text", "whisper", "danish", "asr", "lora", "fine-tuning", "peft", "huggingface", "coral", "claude-code"]

[extra]
summary = "Fine-tuned whisper-large-v3 on CoRal-project/coral-v3 (Danish speech, telephone-codec augmented) with LoRA. Training loss got stuck at ~35-40 for three attempts running — looked like large-v3 itself was unstable under LoRA. It wasn't: the warmup schedule was too long relative to how far training actually ran. Fixed, the model nearly halved WER on held-out Danish speech versus the untrained base. Then a systematic 30-call audit on real phone audio found a real fabrication rate the benchmark number didn't show — published anyway, with an honest model card."
faq = [
  { q = "Why did the LoRA fine-tune's training loss get stuck?", a = "Three separate training attempts all plateaued around a loss of 35-40 instead of converging to single digits, and each time it looked like a different root cause — bad audio levels, a redundant preprocessing filter, then suspected learning-rate instability on the full model. The actual cause was simpler: the warmup schedule (100 steps) was long relative to how far each test run actually got, so the learning rate never reached its target value. A controlled test with a proportionally shorter warmup converged cleanly on the first try." },
  { q = "Does fine-tuning on public Danish speech data improve accuracy on real phone calls?", a = "On a held-out benchmark with real ground truth, yes substantially — word error rate on conversational Danish nearly halved versus the untrained base model. But a separate qualitative audit on real (not benchmark) phone recordings found the fine-tuned model would occasionally invent content — a name or detail not present in the reference transcription — at a rate around 1 in 8 calls. The benchmark metric and real-world reliability measured two different things." },
  { q = "Why does a WER benchmark not catch hallucination/fabrication?", a = "Word error rate measures how many words differ from a reference transcript in aggregate — it doesn't distinguish between an error that garbles a word and an error that invents a plausible-sounding sentence. A model can score better on WER while occasionally producing confident, coherent, and entirely wrong output. The only way to catch that class of error is a qualitative read of real outputs, not a metric." },
  { q = "Should you publish a fine-tuned model with known failure modes?", a = "Yes, if the model card says so honestly. A model with a documented ~13% fabrication rate and clear usage guidance (don't use it as a sole source for name/entity extraction) is more useful to the community than either hiding the flaw or not publishing at all — especially when the untrained base model has a comparable failure rate of its own that just looks different." }
]
+++

**TL;DR —** Fine-tuned [whisper-large-v3](https://huggingface.co/openai/whisper-large-v3) on
[CoRal-project/coral-v3](https://huggingface.co/datasets/CoRal-project/coral-v3) (real,
human-transcribed Danish speech) with a LoRA adapter, telephone-codec-augmented to close
the gap to real phone audio. Training loss got stuck at the same plateau **three times in a
row**, and each time the explanation looked different — until it turned out to be a single,
boring scheduling mistake. Fixed, the model **nearly halved word error rate** on held-out
Danish speech. Then a systematic audit on real phone recordings found the benchmark number
didn't tell the whole story. Published anyway — [on Hugging Face](https://huggingface.co/x2q/whisper-large-v3-da-coral-lora),
with an honest model card.

> The fine-tuning sequel to [transcribing 33,000 Danish voice logs on home GPUs](/post/danish-voice-log-transcription/).
> That post picked the base models; this one tries to make one of them better.

## The loss that wouldn't move

The setup: [PEFT](https://github.com/huggingface/peft) LoRA (rank 32, alpha 64,
`q_proj`/`v_proj`) on top of whisper-large-v3, trained on ~9,000 chunks of coral-v3
audio — three quarters of it run through a telephone-codec simulation (8kHz bandwidth
limit, low-bitrate mp3 round-trip, light noise) so the model would see something closer
to real call audio than coral-v3's clean studio recordings.

Cross-entropy loss should start high and drop into the single digits as training
converges. Instead, three separate attempts all did the same thing: a sharp initial
drop, then a hard plateau around 35–40 that never moved, no matter how far training ran.
Each attempt suggested a different culprit — and each fix was real, and none of them
fixed the actual problem:

1. **Suspect: bad audio.** Coral-v3's raw recordings turned out to have wildly
   inconsistent volume — some samples effectively near-silent (median RMS an order of
   magnitude below healthy speech). Whisper's feature extractor is sensitive to absolute
   amplitude, so this was a real bug. Fixed with loudness normalization (EBU R128,
   -16 LUFS) on every sample. **Loss: still stuck at 35-40.**
2. **Suspect: double-processing.** The training script was re-applying a noise/EQ
   filter meant for *raw, unprocessed* production audio onto data that had already been
   fully preprocessed — a leftover from reusing code written for a different data
   source. Confirmed via direct measurement: the redundant filter was crushing some
   samples' volume right back down. Fixed. **Loss: still stuck at 35-40.**
3. **Suspect: the model itself.** With both audio bugs fixed and the plateau
   unchanged, the working theory shifted to the learning rate being unstable for the
   *full* whisper-large-v3 (32 decoder layers) versus the smaller turbo variant (4
   layers) an earlier, successful fine-tune had used. A controlled test — same LoRA
   config, same known-good data, only the base model swapped — reproduced the identical
   plateau. Testing a 5x lower learning rate produced an *identical* result. That was
   the tell: **two different learning rates converging to the exact same "stuck" value
   isn't a learning-rate problem.**
4. **The actual bug.** The warmup schedule was 100 steps, and every test run —
   including, it turned out, the *real* training runs — only ever got observed partway
   through that ramp. The learning rate scheduler was still climbing toward its target
   value the entire time anyone had looked at it. A short, proportional warmup (40 of
   548 total steps) converged cleanly on the very next attempt: **98 → 83 → 68 → 54 →
   39 → 26 → 16 → 13 → 11 → 9.5**, tracking almost exactly the trajectory of an earlier,
   already-proven fine-tune.

Two of the three fixes were real bugs worth fixing on their own merits. None of them
were *the* bug. The lesson generalizes past this one project: **a metric that looks
"stuck" can just be a schedule that hasn't finished ramping** — check that before
concluding something fundamental is broken.

(A smaller, separate bug along the way: parallelizing the data-prep step with a thread
pool crashed nondeterministically with a `PyGILState_Release` fault — a C-extension
threading issue, not my code's logic. A process pool, which gives every worker its own
independent interpreter state, fixed it outright. **Prefer process pools over thread
pools when the work is C-extension-heavy** (audio decode, codec calls) rather than pure
Python.)

## The benchmark: a real win

With training actually converging, the real test: a held-out set of coral-v3 samples
(disjoint from training — guaranteed by skipping the exact number of samples training
consumed, from the same deterministic shuffle) with real ground truth, so word error
rate is directly computable rather than eyeballed.

| model | conversational Danish WER | read-aloud Danish WER |
|---|---|---|
| whisper-large-v3 (untrained) | 0.704 | 0.303 |
| **fine-tuned (this post)** | **0.367** | 0.220 |
| CoRal's own purpose-built Danish model | 0.327 | 0.101 |

Nearly **halving** conversational WER from a generic base model, closing most of the
gap to a model built from scratch for Danish. The read-aloud number improved less,
because training only used coral-v3's `conversation` split — a clean, testable
prediction that held up (formal, scripted speech is a different distribution from
informal conversation, and the model only saw one of them).

## But WER wasn't the whole story

A WER number is an aggregate: it tells you *how much* text differs from the reference,
not *what kind* of error it is. A model that occasionally replaces a real word with
a different, wrong-but-plausible word, and a model that occasionally invents a
confident, fluent, entirely fabricated sentence can post the *same* WER — but only one
of those is safe to use unsupervised.

So: a systematic qualitative audit, on real (not benchmark) phone recordings — the
actual target domain, not a proxy for it. Every output from the fine-tuned model was
compared against five other models' transcriptions of the same audio, specifically
looking for content with no support anywhere else: an invented name, an invented
detail, a claim that wasn't said. (No call content is reproduced here — the recordings
are private business calls; only the aggregate finding matters for this writeup.)

The result: **roughly one call in eight showed a clear fabrication** — content
confidently stated that no other model, and presumably no one on the call, actually
said. About half the calls were effectively equivalent to the untrained baseline, and
most of the rest differed only in phrasing or omission, not invention. One genuinely
interesting wrinkle: the untrained *base* model has its own well-known failure mode on
quiet audio (a specific hallucinated "fake subtitle credit" line, a documented Whisper
artifact) that showed up on a comparable share of calls — and the fine-tuned model
never reproduced that specific failure, suggesting the fine-tune traded one class of
error for a different one rather than simply adding a new problem on top of a clean
baseline.

**Net read:** a real, substantial accuracy improvement on the metric that's easy to
measure, and a real, non-trivial reliability gap on the property that actually matters
for unsupervised use — invented names and entities are exactly the wrong thing to get
wrong in a system used for tracking who said what. Neither fact cancels the other out.

## Publishing it anyway

The adapter is on Hugging Face: **[x2q/whisper-large-v3-da-coral-lora](https://huggingface.co/x2q/whisper-large-v3-da-coral-lora)**.
The model card states the WER numbers, the training data and license (coral-v3 is
OpenRAIL-licensed and cited directly — no reason to obscure a legitimate, state-funded
Danish speech dataset behind a vaguer description), the fabrication-rate finding, and a
concrete usage warning: don't use it as a sole source for automated name/entity
extraction without a second model or human in the loop.

A flawed model with an honest card is worth more to whoever finds it than a silent one.

## Lessons, distilled

1. **A stuck metric might just be an unfinished schedule** — three plausible-sounding
   root causes (bad data, double-processing, learning-rate instability) were all real
   bugs and all wrong about the actual cause, which was a warmup ramp nobody had let
   finish before drawing conclusions.
2. **Two different values converging to the identical wrong answer is a strong
   signal** — if changing a hyperparameter doesn't change the outcome, the
   hyperparameter probably isn't the cause.
3. **Process pools over thread pools for C-extension-heavy parallel work** — a
   nondeterministic interpreter-level crash disappeared entirely once every worker got
   its own process instead of sharing one interpreter's GIL state.
4. **A single aggregate metric can't see failure-mode diversity** — WER treats a
   garbled word and a confidently invented sentence the same way. If the two matter
   differently for your use case (they almost always do), you need a qualitative read,
   not just a better number.
5. **Publish the flaw, not just the win** — a documented failure rate with clear usage
   guidance is a more useful artifact than a clean-looking model card that turns out to
   hide the same problem the base model already had.
