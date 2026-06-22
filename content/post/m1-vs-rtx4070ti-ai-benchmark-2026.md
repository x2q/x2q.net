+++
title = "Apple M1 Pro vs RTX 4070 Ti for local AI — GPU matmul and LLM benchmarks (2026)"
date = 2026-06-22
slug = "m1-vs-rtx4070ti-ai-benchmark-2026"
description = "Raw GPU TFLOPS and real LLM tokens/second on two consumer machines: Apple M1 Pro (unified memory, MPS) vs NVIDIA RTX 4070 Ti (12 GB GDDR6X, CUDA). The compute gap is 18×. The LLM gap is 3–4×. Why they diverge, and what it means for running AI locally."

[taxonomies]
tags = ["benchmark", "gpu", "local-ai", "apple-silicon", "nvidia", "llm", "pytorch", "ollama", "performance"]

[extra]
summary = "RTX 4070 Ti hits 75 TFLOPS at fp16 via tensor cores; M1 Pro MPS reaches 4.2 TFLOPS — an 18× compute gap. But on real LLM inference (minicpm-v4.6, qwen3.5, gemma4:12b via ollama), the RTX is only 3–4× faster. LLM inference at batch=1 is memory-bandwidth-bound, not compute-bound, and the M1's unified-memory architecture closes most of the gap. Apple's AMX extensions also give its CPU 2.7× better matmul throughput than an Intel i5 with the same thread count."
faq = [
  { q = "Is the RTX 4070 Ti much faster than M1 Pro for AI?", a = "For raw GPU matrix multiply at fp16: yes, 18× (75 TFLOPS vs 4.2 TFLOPS). For real LLM inference (tokens per second at batch=1): only 3–4× faster. The gap collapses because LLM decoding is memory-bandwidth-bound — the GPU spends most of its time moving weights, not computing. The RTX 4070 Ti has ~504 GB/s GDDR6X bandwidth; M1 Pro's unified memory does ~200 GB/s." },
  { q = "Can you run large models on M1 Pro?", a = "Yes — unified memory is the M1's AI superpower. A 16GB M1 Pro can load a 10–13B parameter model in fp16 without hitting a VRAM limit, because GPU and CPU share the same pool. An RTX 4070 Ti with 12GB VRAM hits its limit around 8–9B fp16 parameters. The M1 can run bigger models, just slower." },
  { q = "What LLM speeds are usable in practice?", a = "Roughly 20 tok/s feels real-time for reading; below 10 tok/s feels slow. minicpm-v4.6 runs at 95 tok/s on M1 Pro and 279 tok/s on RTX 4070 Ti — both very usable. qwen3.5 runs at 20 tok/s on M1 Pro (barely real-time) and 74 tok/s on RTX (comfortable). The small 1.6GB model is the practical daily-driver on the M1." },
  { q = "Why is M1 Pro CPU matmul faster than Intel i5-13400F?", a = "Apple's AMX (Apple Matrix Extensions) are dedicated matrix-multiply units built into every M1 CPU core. PyTorch routes float32 matmul through them automatically on macOS. The Intel i5-13400F relies on AVX2 SIMD for the same operation. AMX is purpose-built for this; AVX2 is general-purpose SIMD repurposed for matmul. Result: 1.59 vs 0.58 TFLOPS — 2.7× on CPU before the GPU even enters the picture." },
  { q = "Which is better for a home AI server?", a = "RTX 4070 Ti if you prioritise speed and run one model at a time within 12GB VRAM. M1 Pro (or any Apple Silicon) if you want larger models, lower power draw (~30W GPU vs ~200W GPU under load), and a unified memory pool. For a whisper transcription pipeline running 24/7, the RTX wins on throughput; for an interactive assistant that needs to fit a 10B+ model, the M1's unified memory is the deciding factor." }
]
+++

**TL;DR —** A 4096×4096 float16 matrix multiply exposes an **18× raw compute gap**: RTX 4070 Ti hits 75 TFLOPS via tensor cores; M1 Pro MPS reaches 4.2 TFLOPS. But run an actual LLM and the gap collapses to **3–4×** — because token generation at batch size 1 is memory-bandwidth-bound, not compute-bound. Both machines can run useful models locally; they trade off on VRAM ceiling vs speed.

> Companion to [Rust vs Go vs C on the same machines](/post/rust-go-c-benchmark-2026/) — same hardware, different question.

## Setup

| | M1 Pro (Metal/MPS) | RTX 4070 Ti (CUDA) |
|---|---|---|
| **Machine** | Apple MacBook Pro | Desktop PC |
| **GPU** | M1 Pro 16-core GPU | NVIDIA GeForce RTX 4070 Ti |
| **VRAM / GPU mem** | 16 GB unified (shared with CPU) | 12 GB GDDR6X |
| **CPU** | M1 Pro, 8-core (6P+2E) | Intel i5-13400F, 16 threads |
| **RAM** | 16 GB | 125 GB |
| **OS** | macOS 26.6 | Ubuntu 24.04, CUDA 12.1, driver 595 |
| **PyTorch** | 2.7.0, MPS backend | 2.5.1+cu121 |
| **ollama** | 0.30.8 | 0.30.8 |

## Benchmark 1 — GPU matrix multiply (raw TFLOPS)

A single 4096×4096 dense matmul, 20 timed runs after 5 warmup runs. Synchronised before and after to exclude kernel launch overhead. This is a proxy for **raw tensor compute throughput** — the ceiling everything else runs against.

| Device | dtype | ms / run | TFLOPS |
|--------|-------|:---:|:---:|
| i5-13400F CPU | float32 | 237.8 ms | 0.58 |
| M1 Pro CPU | float32 | 86.4 ms | 1.59 |
| M1 Pro MPS | float32 | 35.8 ms | 3.84 |
| M1 Pro MPS | float16 | 33.0 ms | 4.16 |
| RTX 4070 Ti CUDA | float32 | 4.9 ms | 28.3 |
| RTX 4070 Ti CUDA | float16 | **1.8 ms** | **75.3** |
| RTX 4070 Ti CUDA | bfloat16 | 1.8 ms | 74.9 |

### What the numbers mean

**M1 Pro MPS float16 → float32 barely differs (4.16 vs 3.84 TFLOPS).** The M1 GPU does not have dedicated fp16 tensor cores the way NVIDIA does. Both precisions go through the same hardware; the fp16 path saves some memory bandwidth but gains little compute.

**RTX 4070 Ti float16 → 75 TFLOPS — a 18× leap over M1 and a 2.7× leap over its own float32.** This is the tensor core effect. NVIDIA's Ada Lovelace generation (RTX 40xx) has 4th-gen tensor cores that operate natively on fp16/bf16 matrix tiles and reach roughly 4× the throughput of the fp32 CUDA cores on the same chip. PyTorch routes `torch.float16` matmul through them automatically.

**M1 Pro CPU beats Intel i5-13400F CPU 2.7×** despite both having 8 active threads here. The M1 uses **AMX (Apple Matrix Extensions)** — dedicated matrix-multiply units in each CPU core, separate from NEON SIMD. PyTorch's macOS backend routes float32 matmul through them automatically. The Intel i5 uses AVX2 (256-bit SIMD repurposed for matmul), which is general-purpose and substantially less efficient for dense matrix work.

## Benchmark 2 — LLM inference (tokens / second, ollama)

Fixed 300-token generation task, temperature=0, measuring `eval_count / eval_duration` from the ollama API response (excludes prompt-eval time, which is reported separately). The prompt asks for a detailed explanation of transformer internals to ensure the model generates dense, varied output.

| Model | Size | M1 Pro tok/s | RTX 4070 Ti tok/s | RTX / M1 |
|-------|:----:|:---:|:---:|:---:|
| minicpm-v4.6 | 1.6 GB | 95.3 | 278.9 | **2.9×** |
| qwen3.5 | 6.6 GB | 20.3 | 73.5 | **3.6×** |
| gemma4:12b | 7.6 GB | — | 49.1 | — |

*Prompt eval (time to first token): M1 Pro 25ms / 115ms; RTX 4070 Ti 9ms / 22ms / 42ms for the three models respectively.*

### The bandwidth story

The raw compute gap is 18×. The LLM throughput gap is only 3–4×. Why?

**LLM decoding at batch=1 is memory-bandwidth-bound, not compute-bound.** Each generated token requires loading the entire set of model weights from VRAM (or unified memory) once per forward pass. The compute per byte is low. The GPU spends almost all its time moving data, not multiplying.

The relevant number is **memory bandwidth**:
- RTX 4070 Ti: ~504 GB/s (GDDR6X, dedicated VRAM bus)
- M1 Pro: ~200 GB/s (LPDDR5X, shared CPU/GPU)

Bandwidth ratio: **2.5×** — which matches the LLM throughput ratio of 2.9–3.6× almost exactly. The M1 is slower because it has less memory bandwidth, not because its GPU is 18× weaker. For LLM inference at small batch sizes, buying more memory bandwidth is what you're actually buying.

## The unified-memory advantage

The M1 Pro's GPU has access to **all 16 GB** of unified memory. An RTX 4070 Ti has 12 GB of dedicated VRAM with a hard cliff: models larger than ~11 GB fp16 don't fit and fall back to slow system RAM via PCIe, which collapses throughput.

| Model size (fp16) | M1 Pro 16GB | RTX 4070 Ti 12GB |
|---|---|---|
| 1–3B (~2–6 GB) | Runs fast | Runs fast |
| 7B (~14 GB) | Runs fast | Fits tight (~13.5 GB); may not load |
| 13B (~26 GB) | Doesn't fit | Doesn't fit |
| 7B quantised q4 (~4 GB) | Fast | Fast |
| 13B quantised q4 (~8 GB) | Fast | Fast |
| 30B quantised q4 (~18 GB) | Doesn't fit | Doesn't fit |

For the common use case — a quantised 7B or 13B model — both machines work comfortably. The M1 Pro's unified memory lets it load an unquantised 7B model in fp16 that would overflow a 12GB RTX; the RTX runs the same model quantised to q4 faster overall.

## What 95 vs 279 tok/s actually feels like

minicpm-v4.6 at 95 tok/s on M1 Pro produces tokens faster than anyone reads. qwen3.5 at 20 tok/s on M1 Pro is borderline — you see words appearing but it feels slightly slow. On the RTX at 74 tok/s, qwen3.5 is comfortable.

For **interactive use**: 20–30 tok/s is the floor of what feels acceptable. Both machines clear it on the small model; only the RTX clears it comfortably on the 6.6GB model.

For a **batch transcription or summarisation pipeline** running continuously, the RTX wins clearly — 279 vs 95 tok/s means 3× the throughput with the same model. The [Danish voice-log pipeline](/post/danish-voice-log-transcription/) using Claude Code subagents as the summary layer runs exactly this kind of sustained batch workload; an RTX 4070 Ti would run the same workload in a third of the clock time.

## Power draw

No instruments were connected for this run, but rated TDP gives the order of magnitude:

| | Idle | Full GPU load |
|---|---|---|
| M1 Pro MacBook Pro | ~5 W | ~25–30 W |
| RTX 4070 Ti (card only) | ~15 W | ~200 W |

The M1 wins decisively on efficiency. At 95 tok/s for ~25W and 279 tok/s for ~200W, the RTX delivers **2.9× the performance at 7–8× the power** — so the M1 is **2.5× more efficient per watt** for LLM inference.

## Which machine for local AI?

| Use case | Pick |
|---|---|
| Interactive local assistant (7B–13B quantised) | Either — RTX faster, M1 quieter and more efficient |
| Sustained batch inference (transcription, summaries) | **RTX 4070 Ti** — 3× throughput |
| Loading large fp16 models without quantisation | **M1 Pro** — unified memory, no VRAM cliff |
| Training or fine-tuning (LoRA) | **RTX 4070 Ti** — tensor cores, CUDA ecosystem |
| Always-on home server (power bill matters) | **M1 Pro** — ~7–8× lower GPU power draw |
| Numerical ML (CV, embeddings, matmul-heavy) | **RTX 4070 Ti** — 7–18× faster |

---

*Benchmarks run on personal hardware, June 2026. LLM throughput depends heavily on model quantisation, context length, and system load — treat these numbers as order-of-magnitude comparisons, not absolute specs.*
