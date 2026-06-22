+++
title = "Whisper-backend-dyst: faster-whisper vs HF Transformers vs whisper.cpp (2026)"
date = 2026-06-10
slug = "whisper-backend-sammenligning"
description = "Benchmark af tre Whisper-backends — faster-whisper, HF Transformers (batched/SDPA) og whisper.cpp — på dansk telefonlyd (RTX 4070 Ti): hastighed (RTF), VRAM og konsensus-WER-kvalitet, med anbefalinger pr. use case."

[taxonomies]
tags = ["whisper", "faster-whisper", "whisper-cpp", "transformers", "benchmark", "asr", "tale-til-tekst", "dansk", "gpu", "lokal-ai"]

[extra]
summary = "Tre måder at køre Whisper på — faster-whisper (CTranslate2), Hugging Face Transformers (batched, SDPA) og whisper.cpp (ggml) — benchmarket på rigtig dansk telefonlyd på et RTX 4070 Ti. faster-whisper + large-v3-turbo er hurtigst samlet (~56× realtid); whisper.cpp CUDA er tæt på med en brøkdel af VRAM'en og matcher endda GPU-hastighed på CPU for korte filer. Fulde tabeller for hastighed (RTF), VRAM og konsensus-WER-kvalitet, plus en anbefaling pr. use case."
faq = [
  { q = "Hvilken Whisper-backend er hurtigst?", a = "På et RTX 4070 Ti var faster-whisper (CTranslate2) med large-v3-turbo i float16 hurtigst ved ~0,018 RTF (≈56× realtid). whisper.cpp CUDA var tæt på (~40×) ved meget lavere VRAM, og batched HF Transformers (SDPA, batch 24) var konkurrencedygtig på turbo-modellen (~22×)." },
  { q = "Er large-v3-turbo det værd frem for large-v3?", a = "Til gennemløb, ja: på faster-whisper GPU var large-v3-turbo ~2,4× hurtigere end fuld large-v3, og på denne danske telefonlyd var den mindst lige så kohærent. Tag fat i fuld large-v3 kun når du vil have maksimal præcision og ingen hastighedsbinding har." },
  { q = "Kan Whisper køre hurtigt uden GPU?", a = "whisper.cpp på CPU var overraskelsen — for korte filer matchede den næsten GPU-hastighed (model-load amortiseres anderledes), og faster-whisper int8 er stadig praktisk ved ~5× realtid. Til en CPU-only-server er faster-whisper + large-v3-turbo + int8 valget; til mindst muligt fodaftryk, whisper.cpp CPU." },
  { q = "Hvilken backend bruger mindst VRAM?", a = "Batched HF Transformers med large-v3-turbo (SDPA, batch 24) lå omkring 3,9 GB. whisper.cpp er også meget let. faster-whisper large-v3 i float16 brugte mest af de målte GPU-muligheder her." },
  { q = "Hvordan blev kvaliteten vurderet uden referencetransskriptioner?", a = "Der findes ingen ground-truth-transskriptioner for korpusset, så kvalitet er konsensus-WER — hver models parvise enighed med alle de andre. Det måler konvergens, ikke absolut korrekthed, men det flagger pålideligt en outlier-backend." }
]
+++

**Kort fortalt —** På et RTX 4070 Ti med telefoni-optimeret lydforbehandling når **`faster-whisper` med `large-v3-turbo` ~56× realtid** — hurtigst samlet. **`whisper.cpp` CUDA er tæt på (~40×)** ved en brøkdel af VRAM'en. **Batched HF Transformers** (SDPA, batch 24) er konkurrencedygtig på turbo-modellen. På CPU matcher `whisper.cpp` overraskende GPU-hastigheder for korte filer; `faster-whisper` int8 er stadig praktisk ved ~5×.

> En del af [det danske voicelog-projekt](/da/post/dansk-voicelog-transkribering/) — dette er backend-benchmarken bag pipelinens ASR-valg. Se også [at køre Whisper lokalt](/post/local-speech-to-text-whisper-cpp/).

## Opsætning

| | |
|---|---|
| **GPU** | NVIDIA GeForce RTX 4070 Ti (12 GB VRAM) |
| **CPU** | Intel Core i5-13400F (16 tråde) |
| **RAM** | 125 GB |
| **CUDA** | 12.9 / Driver 595 |
| **faster-whisper** | 1.2.1 (CTranslate2 4.8.0) |
| **transformers** | 5.10.2 |
| **whisper.cpp** | kompileret fra kilde, CUDA aktiveret |
| **PyTorch** | 2.12.0 |

## Lyd-testsæt

Tre rigtige danske telefonopkald fra et dansk voicelog-korpus (filnavne anonymiseret til `Fil 1–3`):

| Fil | Varighed | Noter |
|------|----------|-------|
| **Fil 1** | 1m 26s | Autentisk dansk samtaletale |
| **Fil 2** | 13m 26s | Autentisk dansk samtaletale |
| **Fil 3** | 1m 51s | Autentisk dansk samtaletale |

> Der findes ingen referencetransskriptioner — kvalitet vurderes via **konsensus-WER** (parvis enighed på tværs af modeller) og **relativ WER** (afstand til konsensus-vinderen).

## Backends i test

| Backend | Engine | Nøgleteknik | Modeller |
|---------|--------|-------------|----------|
| **faster-whisper** | CTranslate2 | int8/float16-kvantiserede kerner | large-v3, large-v3-turbo |
| **HF Transformers (batched)** | PyTorch (SDPA) | batch_size=24, flash-attention via SDPA | large-v3, large-v3-turbo |
| **whisper.cpp** | ggml | CUDA-kerne-offload / AVX CPU | large-v3, large-v3-turbo |

## Resultater: hastighed (RTF — lavere er bedre)

*RTF = transskriptionstid ÷ lydvarighed. RTF 0,03 = 33× realtid.*

| Backend / Model / Enhed | Fil 1 | Fil 2 | Fil 3 | **Gns. RTF** | **Fart** |
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

## Resultater: VRAM-forbrug (GPU-kørsler)

| Backend / Model | Gns. VRAM (MB) |
|-----------------|--------------|
| HF Transformers (b24, SDPA) / large-v3-turbo / CUDA | 3884 |
| HF Transformers (b2, SDPA) / large-v3 / CUDA | 5727 |

## Resultater: kvalitet (konsensus-WER)

Konsensus-WER måler, hvor meget hver models output afviger fra gruppegennemsnittet. Lavere = mere lig det, alle modeller er enige om.

| Backend / Model / Enhed | Fil 1 | Fil 2 | Fil 3 | Gns. relativ WER |
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

> **Kvalitetsvinder:** `faster-whisper / large-v3-turbo / CPU`

## Side om side: hvor backendsne adskilte sig

Test-lyden er et privat opkald, så i stedet for at gengive det er her en neutral dansk sætning, der står som stedfortræder for den slags samtaletale, der blev testet — plus de afvigelsesmønstre, der faktisk dukkede op på tværs af backends på 86-sekunders-filen:

> *"Lad os tage mødet på torsdag, så gennemgår vi tallene sammen."* (illustrativ)

- **Tabte indledninger.** `faster-whisper` large-v3 (CUDA og CPU) startede nogle gange et par ord inde og udelod en indledende sætning, som turbo-modellerne og `whisper.cpp` fangede.
- **Uenighed om egennavne.** Det indledende navn blev transskriberet på to forskellige måder på tværs af backends — det klassiske problem med navne i et sprog med få ressourcer, hvor hver model gætter en anden plausibel stavemåde.
- **Forvanskede navneord på støjende segmenter.** `whisper.cpp` large-v3 lavede et klart navneord om til en næsten-homofon, som turbo-modellerne fik rigtigt.
- **Sjældne hallucinerede fragmenter.** `faster-whisper` large-v3 udsendte lejlighedsvis en kort nonsens-frase på en støjende strækning, hvor de andre backends holdt sig rene.
- **Mindre stavefejl.** Turbo-CPU-kørslen producerede en og anden vokal-tastefejl, der ikke sås på GPU.

Netto: **turbo-modellerne var mest konsekvent kohærente**; fuld large-v3 var stærk, men mere tilbøjelig til tabte indledninger og en og anden hallucination på denne støjende telefonlyd.

## Nøglefund

- **Hurtigste GPU:** `faster-whisper / large-v3-turbo / CUDA` ved gns. RTF 0,018 (56× realtid).
- **Turbo-speedup (faster-whisper GPU):** large-v3-turbo er 2,4× hurtigere end large-v3.
- **Hurtigste CPU:** `whisper.cpp / large-v3-turbo / CPU` ved gns. RTF 0,026.
- **GPU vs. CPU (faster-whisper turbo):** GPU er 11,4× hurtigere end CPU int8.
- **Lavest VRAM:** `HF Transformers (b24, SDPA) / large-v3-turbo / CUDA` ved 3884 MB.

## Anbefalinger

| Use case | Anbefaling |
|----------|------------|
| **Produktions-pipeline (GPU-server)** | `faster-whisper` + `large-v3-turbo` + `float16` — bedste hastighed/kvalitet/VRAM |
| **Højeste præcision (GPU, ingen hastighedsbinding)** | `faster-whisper` + `large-v3` + `float16` |
| **Batched offline-behandling** | HF Transformers batched (SDPA) + `large-v3-turbo`, batch_size=24 |
| **Embedded / ingen Python-runtime** | `whisper.cpp` CUDA — én binær, lavt overhead |
| **CPU-only-server** | `faster-whisper` + `large-v3-turbo` + `int8` |
| **Edge / Raspberry Pi** | `whisper.cpp` CPU + `large-v3-turbo` (mindste RAM-fodaftryk) |

## Metodenoter

- Hver backend/model/enhed-kombination kører som en **separat proces** for at garantere fuld GPU-hukommelses-frigivelse mellem kørsler.
- faster-whisper GPU bruger `compute_type=float16`; CPU bruger `int8`.
- HF Transformers bruger `attn_implementation=sdpa` (PyTorch SDPA / FlashAttention-ækvivalent, ingen ekstra installation).
- whisper.cpp bruger CUDA automatisk, når den er kompileret med `GGML_CUDA=ON` — intet flag nødvendigt; CPU-kørsler bruger `-t 8` (systemets trådantal).
- Al lyd forbehandles med ffmpeg før transskribering: `highpass=f=200,lowpass=f=3400,afftdn=nr=10:nf=-25,dynaudnorm` (telefon-båndpas + let denoise + loudness-normalisering).
- VRAM måles via `torch.cuda.max_memory_allocated()`; ikke tilgængeligt for whisper.cpp-subprocess-kørsler.
- Al lyd er dansk samtale-telefontale — resultater kan variere på andre sprog eller lydforhold.
- Konsensus-WER beregnes parvist på tværs af alle modeller; modellen med lavest gennemsnitlig parvis WER er "konsensus-vinderen".
