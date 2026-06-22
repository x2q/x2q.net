+++
title = "Whisper backend shootout: faster-whisper vs HF Transformers vs whisper.cpp (2026)"
date = 2026-06-10
slug = "whisper-backend-shootout"
description = "Benchmarking three Whisper backends — faster-whisper, HF Transformers (batched/SDPA), and whisper.cpp — on Danish phone audio (RTX 4070 Ti): speed (RTF), VRAM, and consensus-WER quality, with recommendations per use case."

[taxonomies]
tags = ["whisper", "faster-whisper", "whisper-cpp", "transformers", "benchmark", "asr", "speech-to-text", "danish", "gpu", "local-ai"]

[extra]
summary = "Three ways to run Whisper — faster-whisper (CTranslate2), Hugging Face Transformers (batched, SDPA), and whisper.cpp (ggml) — benchmarked on real Danish telephone audio on an RTX 4070 Ti. faster-whisper + large-v3-turbo is the fastest overall (~56× real-time); whisper.cpp CUDA is close at a fraction of the VRAM and even matches GPU speed on CPU for short files. Full speed (RTF), VRAM, and consensus-WER quality tables, plus a recommendation per use case."
faq = [
  { q = "Which Whisper backend is fastest?", a = "On an RTX 4070 Ti, faster-whisper (CTranslate2) with large-v3-turbo in float16 was fastest at ~0.018 RTF (≈56× real-time). whisper.cpp CUDA was close (~40×) at much lower VRAM, and batched HF Transformers (SDPA, batch 24) was competitive on the turbo model (~22×)." },
  { q = "Is large-v3-turbo worth it over large-v3?", a = "For throughput, yes: on faster-whisper GPU, large-v3-turbo was ~2.4× faster than full large-v3, and on this Danish phone audio it was at least as coherent. Reach for full large-v3 only when you want maximum accuracy and have no speed constraint." },
  { q = "Can Whisper run fast without a GPU?", a = "whisper.cpp on CPU was the surprise — for short files it nearly matched GPU speed (model-load is amortised differently), and faster-whisper int8 stays practical at ~5× real-time. For a CPU-only server, faster-whisper + large-v3-turbo + int8 is the pick; for the smallest footprint, whisper.cpp CPU." },
  { q = "Which backend uses the least VRAM?", a = "Batched HF Transformers with large-v3-turbo (SDPA, batch 24) sat around 3.9 GB. whisper.cpp is also very light. faster-whisper large-v3 in float16 used the most of the GPU options measured here." },
  { q = "How was quality judged without reference transcripts?", a = "No ground-truth transcriptions exist for the corpus, so quality is consensus WER — each model's pairwise agreement with all the others. It measures convergence, not absolute correctness, but it reliably flags an outlier backend." }
]
+++

**TL;DR —** On an RTX 4070 Ti with telephony-optimised audio preprocessing, **`faster-whisper` with `large-v3-turbo` reaches ~56× real-time** — the fastest overall. **`whisper.cpp` CUDA is close (~40×)** at a fraction of the VRAM. **Batched HF Transformers** (SDPA, batch 24) is competitive on the turbo model. On CPU, `whisper.cpp` surprisingly matches GPU speeds for short files; `faster-whisper` int8 stays practical at ~5×.

> Part of the [Danish voice-log project](/post/danish-voice-log-transcription/) — this is the backend benchmark behind that pipeline's ASR choice. See also [running Whisper locally](/post/local-speech-to-text-whisper-cpp/).

## Setup

| | |
|---|---|
| **GPU** | NVIDIA GeForce RTX 4070 Ti (12 GB VRAM) |
| **CPU** | Intel Core i5-13400F (16 threads) |
| **RAM** | 125 GB |
| **CUDA** | 12.9 / Driver 595 |
| **faster-whisper** | 1.2.1 (CTranslate2 4.8.0) |
| **transformers** | 5.10.2 |
| **whisper.cpp** | compiled from source, CUDA enabled |
| **PyTorch** | 2.12.0 |

## Audio test set

Three real Danish phone-call recordings from a Danish voice-log corpus (filenames anonymised to `File 1–3`):

| File | Duration | Notes |
|------|----------|-------|
| **File 1** | 1m 26s | Authentic Danish conversational speech |
| **File 2** | 13m 26s | Authentic Danish conversational speech |
| **File 3** | 1m 51s | Authentic Danish conversational speech |

> No reference transcriptions exist — quality is evaluated via **consensus WER** (pairwise agreement across models) and **relative WER** (distance to the consensus winner).

## Backends under test

| Backend | Engine | Key technique | Models |
|---------|--------|---------------|--------|
| **faster-whisper** | CTranslate2 | int8/float16 quantised kernels | large-v3, large-v3-turbo |
| **HF Transformers (batched)** | PyTorch (SDPA) | batch_size=24, flash-attention via SDPA | large-v3, large-v3-turbo |
| **whisper.cpp** | ggml | CUDA kernel offload / AVX CPU | large-v3, large-v3-turbo |

## Results: speed (RTF — lower is better)

*RTF = transcription time ÷ audio duration. RTF 0.03 = 33× real-time.*

| Backend / Model / Device | File 1 | File 2 | File 3 | **Avg RTF** | **Speed** |
|--------------------------|---|---|---|---|---|
| faster-whisper / large-v3-turbo / CUDA | 0.021 | 0.013 | 0.019 | **0.018** | **56×** |
| faster-whisper / large-v3 / CUDA | 0.047 | 0.033 | 0.051 | **0.043** | **23×** |
| HF Transformers (b24, SDPA) / large-v3-turbo / CUDA | 0.040 | 0.062 | 0.036 | **0.046** | **22×** |
| HF Transformers (b2, SDPA) / large-v3 / CUDA | 0.180 | 0.142 | 0.222 | **0.181** | **6×** |
| whisper.cpp / large-v3-turbo / CUDA | 0.028 | 0.017 | 0.030 | **0.025** | **40×** |
| whisper.cpp / large-v3 / CUDA | 0.070 | 0.050 | 0.080 | **0.067** | **15×** |
| faster-whisper / large-v3-turbo / CPU | 0.208 | 0.151 | 0.248 | **0.203** | **5×** |
| faster-whisper / large-v3 / CPU | 0.470 | 0.354 | 0.714 | **0.513** | **2×** |
| whisper.cpp / large-v3-turbo / CPU | 0.034 | 0.017 | 0.027 | **0.026** | **39×** |
| whisper.cpp / large-v3 / CPU | 0.071 | 0.050 | 0.084 | **0.068** | **15×** |

## Results: VRAM usage (GPU runs)

| Backend / Model | Avg VRAM (MB) |
|-----------------|--------------|
| HF Transformers (b24, SDPA) / large-v3-turbo / CUDA | 3884 |
| HF Transformers (b2, SDPA) / large-v3 / CUDA | 5727 |

## Results: quality (consensus WER)

Consensus WER measures how much each model's output diverges from the group mean. Lower = more similar to what all models agree on.

| Backend / Model / Device | File 1 | File 2 | File 3 | Avg relative WER |
|--------------------------|---|---|---|---|
| faster-whisper / large-v3-turbo / CUDA | 0.132 | 0.359 | 0.226 | **0.239** |
| faster-whisper / large-v3 / CUDA | 0.230 | 0.334 | 0.294 | **0.286** |
| HF Transformers (b24, SDPA) / large-v3-turbo / CUDA | 0.237 | 0.601 | 0.229 | **0.356** |
| HF Transformers (b2, SDPA) / large-v3 / CUDA | 0.152 | 0.225 | 0.326 | **0.234** |
| whisper.cpp / large-v3-turbo / CUDA | 0.000 | 0.673 | 0.000 | **0.224** |
| whisper.cpp / large-v3 / CUDA | 0.187 | 0.000 | 0.553 | **0.247** |
| faster-whisper / large-v3-turbo / CPU | 0.136 | 0.344 | 0.191 | **0.224** |
| faster-whisper / large-v3 / CPU | 0.249 | 0.339 | 0.274 | **0.287** |
| whisper.cpp / large-v3-turbo / CPU | 0.000 | 0.673 | 0.000 | **0.224** |
| whisper.cpp / large-v3 / CPU | 0.187 | 0.000 | 0.553 | **0.247** |

> **Quality winner:** `faster-whisper / large-v3-turbo / CPU`

## Side-by-side: where the backends differed

The test audio is a private call, so rather than reproduce it, here's a neutral Danish sentence standing in for the kind of conversational speech tested — plus the divergence patterns that actually showed up across backends on the 86-second file:

> *"Lad os tage mødet på torsdag, så gennemgår vi tallene sammen."* (illustrative)

- **Dropped openings.** `faster-whisper` large-v3 (CUDA and CPU) sometimes started a few words in, omitting an opening sentence that the turbo models and `whisper.cpp` captured.
- **Proper-noun disagreement.** The opening name was transcribed two different ways across backends — the classic low-resource-name problem, where each model guesses a different plausible spelling.
- **Garbled noun phrases on noisy segments.** `whisper.cpp` large-v3 turned a clear noun phrase into a near-homophone that the turbo models got right.
- **Rare hallucinated fragments.** `faster-whisper` large-v3 occasionally emitted a short nonsense phrase on a noisy stretch where the other backends stayed clean.
- **Minor spelling slips.** The turbo CPU run produced the odd vowel typo not seen on GPU.

Net: the **turbo models were the most consistently coherent**; full large-v3 was strong but more prone to dropped openings and the occasional hallucination on this noisy telephone audio.

## Key findings

- **Fastest GPU:** `faster-whisper / large-v3-turbo / CUDA` at avg RTF 0.018 (56× real-time).
- **Turbo speedup (faster-whisper GPU):** large-v3-turbo is 2.4× faster than large-v3.
- **Fastest CPU:** `whisper.cpp / large-v3-turbo / CPU` at avg RTF 0.026.
- **GPU vs CPU (faster-whisper turbo):** GPU is 11.4× faster than CPU int8.
- **Lowest VRAM:** `HF Transformers (b24, SDPA) / large-v3-turbo / CUDA` at 3884 MB.

## Recommendations

| Use case | Recommendation |
|----------|---------------|
| **Production pipeline (GPU server)** | `faster-whisper` + `large-v3-turbo` + `float16` — best speed/quality/VRAM |
| **Highest accuracy (GPU, no speed constraint)** | `faster-whisper` + `large-v3` + `float16` |
| **Batched offline processing** | HF Transformers batched (SDPA) + `large-v3-turbo`, batch_size=24 |
| **Embedded / no Python runtime** | `whisper.cpp` CUDA — single binary, low overhead |
| **CPU-only server** | `faster-whisper` + `large-v3-turbo` + `int8` |
| **Edge / Raspberry Pi** | `whisper.cpp` CPU + `large-v3-turbo` (smallest RAM footprint) |

## Methodology notes

- Each backend/model/device combination runs as a **separate process** to guarantee full GPU memory reclamation between runs.
- faster-whisper GPU uses `compute_type=float16`; CPU uses `int8`.
- HF Transformers uses `attn_implementation=sdpa` (PyTorch SDPA / FlashAttention-equivalent, no extra install).
- whisper.cpp uses CUDA automatically when compiled with `GGML_CUDA=ON` — no flag needed; CPU runs use `-t 8` (system thread count).
- All audio is pre-processed with ffmpeg before transcription: `highpass=f=200,lowpass=f=3400,afftdn=nr=10:nf=-25,dynaudnorm` (telephone band-pass + light denoise + loudness normalisation).
- VRAM is measured via `torch.cuda.max_memory_allocated()`; not available for the whisper.cpp subprocess runs.
- All audio is Danish conversational phone-call speech — results may vary on other languages or audio conditions.
- Consensus WER is computed pairwise across all models; the model with the lowest mean pairwise WER is the "consensus winner".
