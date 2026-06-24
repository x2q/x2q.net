+++
title = "Five alternatives to pyannote: speaker diarization for phone calls (2026)"
date = 2026-06-24
slug = "diarization-fem-alternativer"
description = "Can anything faster than pyannote-audio 3.1 handle 2-party phone call diarization? A benchmark of five approaches — spectral clustering, multi-scale embeddings, PLDA, Silero VAD and a cross-call speaker gallery — on 8 real calls. Winner: Silero VAD + WeSpeaker at 2.1 s and 76% agreement. Loser: all five on mono calls."

[taxonomies]
tags = ["diarization", "whisper", "speech-to-text", "local-ai", "python", "asr", "benchmark"]

[extra]
summary = "pyannote-audio 3.1 works, but requires a Hugging Face token and takes 5 seconds per call. Benchmark of five alternatives on 8 real 2-party phone calls: WeSpeaker + spectral clustering (0.2 s), multi-scale AHC (0.6 s), PLDA + spectral (0.3 s), Silero VAD + spectral (2.1 s) and cross-call gallery nearest-neighbour (0.2 s). The Silero VAD approach won at 76.1% agreement and is 2.4× faster. Surprise: all five collapsed on mono calls — pyannote stays in production."
faq = [
  { q = "What is speaker diarization?", a = "Speaker diarization is the task of answering 'who spoke when' in an audio file — segmenting and labelling audio with speaker identities. In a 2-party phone call this means deciding which parts of the transcript belong to which party." },
  { q = "Why not just use pyannote?", a = "pyannote-audio 3.1 works well but requires a Hugging Face account with accepted model terms, takes ~5 seconds per call, and is a heavy dependency. For pipelines that need to run fast or offline, it's worth knowing whether something simpler can do the job." },
  { q = "What is agreement in this benchmark?", a = "Agreement is the fraction of Whisper segments where the method's speaker label matches pyannote's output under the best global label permutation (swap A↔B allowed). It measures similarity to pyannote — not absolute correctness. A method that diverges from pyannote may actually be more accurate; there is no human ground truth." },
  { q = "Which method won?", a = "EXP I — Silero VAD + WeSpeaker + Spectral Clustering — with 76.1% agreement and ~2.1 s processing time (vs pyannote's 5.1 s). It uses Silero's acoustic speech detection boundaries instead of Whisper's semantic segment boundaries, yielding cleaner embeddings." },
  { q = "What is the problem with mono calls?", a = "All five approaches force two clusters — they have no concept of the scenario 'there is only one speaker'. On calls where only one party speaks (short replies, dropped connections, one-sided calls) they still split the audio into two wrong clusters and end up at 1–35% agreement. A simple 1-speaker detector (cosine variance below a threshold → assign all segments to the line owner) would fix it." }
]
+++

Speaker diarization — deciding "who spoke when" — sounds simple and turns out to be hard. This post documents a weekend experiment with five alternative approaches to my current production pipeline.

## Background

I record and transcribe all my business calls automatically. The pipeline is roughly:

1. Call arrives, audio saved as MP3
2. [Whisper](https://github.com/openai/whisper) transcribes to word-level segments
3. A diarization step assigns each segment a speaker
4. Everything lands in a SQLite database with a Markdown summary

Step 3 is the interesting one. I landed on **pyannote/speaker-diarization-3.1** as the production backend after earlier experiments ruled out NeMo MSDD, reference-guided ECAPA and DiarizationLM. pyannote works reliably — but it takes 4–5 seconds per call and requires a Hugging Face token with accepted model terms. I wanted to know whether newer research has produced something meaningfully better.

## Benchmark

**8 real calls, 288–592 seconds, all 2-party conversations.** I run each alternative against pyannote's output and measure *segment-level agreement*: the fraction of Whisper segments where the alternative assigns the same speaker label as pyannote, under the best permutation mapping.

This measures *similarity to pyannote*, not absolute correctness. A method that diverges from pyannote may actually be *more* accurate — there is no human ground truth to compare against. Keep that in mind when reading the numbers.

All five use pyannote's internal **WeSpeaker ResNet34-LM** embedding model (256-dim, cosine, trained on VoxCeleb) — the same model pyannote uses internally, so it's already loaded.

---

## Baseline — EXP E (dropped early)

Before F–J I tried building speaker references from pyannote's own labels in the database and running WeSpeaker nearest-neighbour against them. It reached 88% agreement — but is circular: it uses pyannote's labels as input. Useless as a replacement.

---

## EXP F — WeSpeaker + Spectral Clustering

**Idea:** SpectralClustering with normalised cosine affinity beats AgglomerativeClustering on 2-speaker tasks (Park et al. ICASSP 2022; Landini et al. IS 2022). The global graph structure beats greedy local merging.

**Flow:**
1. Group Whisper segments into turns (< 0.5 s pause = same turn)
2. Embed each turn with WeSpeaker ResNet34 (256-dim, L2-normalised)
3. Build cosine affinity matrix, run `SpectralClustering(n_clusters=2)`
4. Map clusters to names via call direction

**Time:** ~0.2 s — 25× faster than pyannote.

---

## EXP G — Multi-scale WeSpeaker + AHC

**Idea:** Short turns yield unstable embeddings. Fix it by embedding each turn at three window sizes — 0.5×, 1× and 2× turn duration, centred on the turn midpoint — and averaging the three embeddings. Inspired by NeMo's MSDD architecture (Kwon et al. 2022).

**Flow:** Same as F, but use the averaged multi-scale embedding. Clustering with AgglomerativeClustering (`cosine`, `average` linkage).

**Time:** ~0.6 s.

---

## EXP H — WeSpeaker + PLDA + Spectral Clustering

**Idea:** PLDA (Probabilistic Linear Discriminant Analysis) models within- and between-speaker covariance and consistently beats cosine distance for speaker clustering (Snyder et al. 2018; dominant in VoxSRC 2023 winning systems).

The `pyannote-audio` package ships a trained PLDA object with LDA transform `_xvec_tf` and eigenvalues `phi`.

**Flow:**
1. LDA projection: `mat_lda = plda._xvec_tf(embeddings)` — reduces 256 → 128 dim
2. Pairwise Simplified-PLDA log-likelihood ratio:
   - `φ` = PLDA eigenvalues (`plda.phi`, 128-dim)
   - `w_same = φ / (φ + 2)` — weight for x and y being the same speaker
   - `w_diff = 1 / (φ + 1)` — penalty for being different speakers
   - `LLR(x, y) = Σ [ w_same·(xᵢ+yᵢ)²/2 − w_diff·(xᵢ²+yᵢ²)/2 ]`
3. Convert to affinity: `A = 1 / (1 + exp(−LLR))`
4. `SpectralClustering(n_clusters=2, affinity="precomputed")`

**Time:** ~0.3 s.

---

## EXP I — Silero VAD + WeSpeaker + Spectral Clustering

**Idea:** Whisper segment boundaries are semantic, not acoustic — they follow meaning, not the speaker's mouth. Better VAD boundaries yield cleaner embeddings. The VBx system (Landini et al. Odyssey 2022) shows that near-oracle VAD is critical for embedding quality. Silero VAD (Silero Team 2021) runs on CPU and uses ~1 ms per second of audio.

**Flow:**
1. Run Silero VAD on raw audio (`threshold=0.4`, `min_speech=250 ms`, `min_silence=300 ms`)
2. Group Silero timestamps into turns (< 0.5 s pause)
3. Embed each Silero turn with WeSpeaker
4. Map Whisper segments to nearest Silero turn by time overlap
5. `SpectralClustering(n_clusters=2)`

**Time:** ~2.1 s (dominated by Silero on CPU).

---

## EXP J — Cross-call speaker gallery (nearest-neighbour)

**Idea:** No clustering at all. Instead build a gallery of known speakers from historical calls in the database, and classify new turns with cosine nearest-neighbour — as in the speaker recognition literature (Ding et al. ICASSP 2020; x-vector NN-baseline in VoxSRC 2021–2023).

**Flow:**
1. Fetch the 40 most recently processed calls from DB
2. Sample up to 8 WeSpeaker embeddings per speaker per call → `{speaker_name: [emb, ...]}`
3. Compute mean embedding per speaker, L2-normalise
4. For each new turn: find the gallery speaker with highest cosine similarity
5. Snap to line owner or counterpart based on call direction

**Time:** ~0.2 s excluding gallery build (12 s once at startup, then cached).

---

## Results — 8 calls

| Call | Duration | Pyannote dist. | F SC | G MS | H PLDA | I Silero | J Gallery |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| Call A | 308 s | 68 / 34 seg. | 66.7 % | 65.7 % | **88.2 %** | **88.2 %** | 69.6 % |
| Call B | 288 s | **mono** (10/0) | 80.0 % | 90.0 % | 80.0 % | 90.0 % | 80.0 % |
| Call C | 320 s | 4 / 33 seg. | 75.7 % | **86.5 %** | 78.4 % | 81.1 % | 75.7 % |
| Call D | 314 s | **mono** (99/0) | 35.4 % | 1.0 % | 35.4 % | 61.6 % | 47.5 % |
| Call E | 384 s | 20 / 39 seg. | 62.7 % | 64.4 % | 66.1 % | **74.6 %** | 69.5 % |
| Call F | 393 s | **mono** (84/0) | 40.5 % | 1.2 % | 10.7 % | 48.8 % | 47.6 % |
| Call G | 401 s | 63 / 90 seg. | 58.8 % | 59.5 % | 57.5 % | **88.9 %** | 62.1 % |
| Call H | 592 s | 43 / 64 seg. | 71.0 % | 58.9 % | 70.1 % | **75.7 %** | 64.5 % |
| **Average** | | | 61.3 % ±15 % | 53.4 % ±32 % | 60.8 % ±24 % | **76.1 % ±14 %** | 64.6 % ±11 % |

pyannote reference time: **5.1 s** average per call.

*Calls B, D and F are "mono" — one party dominates nearly 100% of segments. These are the hardest cases.*

---

## Three surprises

### 1. EXP G completely collapsed on mono calls

1.0% and 1.2% agreement. That's not just bad — it's actively wrong. AHC with `n_clusters=2` forces two clusters regardless: on mono calls it ends up with one giant cluster and one with almost no segments, and the global label-swap permutation doesn't save it. Multi-scale helped nothing here.

Spectral Clustering (F, H, I) is slightly more robust — 35–61% on the same calls — but still collapsed. None of the five approaches *know* there is only one speaker.

### 2. PLDA — 88% on real 2-speaker calls, 10% on mono

The PLDA method (H) performed best on calls with two clearly separated speakers. That is exactly what PLDA is designed for: modelling the difference in embedding space between two speaker distributions. But on mono calls it still splits, ending at a worst-case 10.7%.

### 3. The gallery method was the most stable (±11%)

EXP J didn't win on average but had by far the lowest variance. It "knows" who the line owner is from historical calls and guesses reasonably on counterparts. It fails systematically on speakers it has never heard — the first time a new contact calls, the gallery embedding for that person is empty.

---

## Conclusion

**Winner: EXP I (Silero VAD + WeSpeaker + SC)** — 76.1% agreement, 2.4× faster than pyannote (2.1 s vs 5.1 s).

The explanation is that Silero's acoustic VAD boundaries give cleaner turn segments than Whisper's semantic boundaries. Whisper cuts where meaning stops; Silero cuts where the mouth stops. Cleaner segments → cleaner embeddings → better clustering.

**Stayed on pyannote 3.1 in production.** All five alternatives fail on mono calls, and mono calls are a real scenario in a production pipeline — one-sided calls, dropped connections, short confirmatory replies — none are handled correctly by clustering methods with a fixed `n_clusters=2`.

The most promising path forward: **EXP I + 1-speaker detector.** Compute cosine variance within a call's turn embeddings; if variance falls below a threshold, the call is likely mono and all segments get assigned to the line owner. That would likely reach 85–90% agreement at ~2.5 s total — comparable to pyannote on real 2-speaker calls and correct on mono calls.

> See [the full pipeline](/post/dansk-voicelog-transkribering/) and [Whisper backend benchmarks](/post/whisper-backend-sammenligning/) for the broader context this experiment lives in.
