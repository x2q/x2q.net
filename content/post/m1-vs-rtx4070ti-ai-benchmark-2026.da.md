+++
title = "Apple M1 Pro vs RTX 4070 Ti til lokal AI — GPU-matmul og LLM-benchmarks (2026)"
date = 2026-06-22
slug = "m1-vs-rtx4070ti-ai-benchmark-2026"
description = "Rå GPU-TFLOPS og rigtige LLM-token/s på to forbrugermaskiner: Apple M1 Pro (unified memory, MPS) vs NVIDIA RTX 4070 Ti (12 GB GDDR6X, CUDA). Beregningsgabet er 18×. LLM-gabet er 3–4×. Hvorfor de divergerer, og hvad det betyder for at køre AI lokalt."

[taxonomies]
tags = ["benchmark", "gpu", "lokal-ai", "apple-silicon", "nvidia", "llm", "pytorch", "ollama", "performance"]

[extra]
summary = "RTX 4070 Ti rammer 75 TFLOPS ved fp16 via tensor cores; M1 Pro MPS når 4,2 TFLOPS — et 18× beregningsgab. Men på rigtig LLM-inferens (minicpm-v4.6, qwen3.5, gemma4:12b via ollama) er RTX kun 3–4× hurtigere. LLM-inferens ved batch=1 er hukommelsesbåndbredde-begrænset, ikke beregnings-begrænset, og M1's unified-memory-arkitektur lukker det meste af gabet. Apple's AMX-udvidelser giver også dens CPU 2,7× bedre matmul-gennemstrømning end en Intel i5 med samme tråd-antal."
faq = [
  { q = "Er RTX 4070 Ti meget hurtigere end M1 Pro til AI?", a = "Til rå GPU-matrixmultiplikation ved fp16: ja, 18× (75 TFLOPS vs 4,2 TFLOPS). Til rigtig LLM-inferens (tokens per sekund ved batch=1): kun 3–4× hurtigere. Gabet kollapser fordi LLM-dekodning er hukommelsesbåndbredde-begrænset — GPU'en bruger det meste af sin tid på at flytte vægte, ikke beregne. RTX 4070 Ti har ~504 GB/s GDDR6X-båndbredde; M1 Pro's unified memory klarer ~200 GB/s." },
  { q = "Kan man køre store modeller på M1 Pro?", a = "Ja — unified memory er M1's AI-superpower. En 16GB M1 Pro kan indlæse en 10–13B-parameter-model i fp16 uden at ramme en VRAM-grænse, fordi GPU og CPU deler den samme hukommelsespulje. En RTX 4070 Ti med 12GB VRAM rammer sin grænse ved ca. 8–9B fp16-parametre. M1 kan køre større modeller, bare langsommere." },
  { q = "Hvad er brugbare LLM-hastigheder i praksis?", a = "Cirka 20 tok/s føles realtid til læsning; under 10 tok/s føles langsomt. minicpm-v4.6 kører ved 95 tok/s på M1 Pro og 279 tok/s på RTX 4070 Ti — begge meget brugbare. qwen3.5 kører ved 20 tok/s på M1 Pro (knapt realtid) og 74 tok/s på RTX (komfortabelt). Den lille 1,6GB-model er den praktiske daglige driver på M1." },
  { q = "Hvorfor er M1 Pro CPU-matmul hurtigere end Intel i5-13400F?", a = "Apple's AMX (Apple Matrix Extensions) er dedikerede matrix-multiplikationsenheder indbygget i hvert M1 CPU-kerne. PyTorch router float32-matmul automatisk igennem dem på macOS. Intel i5-13400F bruger AVX2 (256-bit SIMD ombrugt til matmul), som er generel brug og markant mindre effektivt til tæt matrixarbejde. Resultat: 1,59 vs 0,58 TFLOPS — 2,7× på CPU." },
  { q = "Hvad er bedst til en hjemme-AI-server?", a = "RTX 4070 Ti hvis du prioriterer hastighed og kører én model ad gangen inden for 12GB VRAM. M1 Pro (eller enhver Apple Silicon) hvis du vil have større modeller, lavere strømforbrug (~30W GPU vs ~200W GPU under load), og en unified memory-pulje. Til en Whisper-transskriptionspipeline der kører 24/7 vinder RTX på gennemstrømning; til en interaktiv assistent der skal passe en 10B+-model er M1's unified memory den afgørende faktor." }
]
+++

**Kort fortalt —** En 4096×4096 float16 matrixmultiplikation afslører et **18× rå beregningsgab**: RTX 4070 Ti rammer 75 TFLOPS via tensor cores; M1 Pro MPS når 4,2 TFLOPS. Men kør en rigtig LLM, og gabet kollapser til **3–4×** — fordi tokengenerering ved batch størrelse 1 er hukommelsesbåndbredde-begrænset, ikke beregnings-begrænset. Begge maskiner kan køre nyttige modeller lokalt; de bytter på VRAM-loft vs hastighed.

> Ledsager til [Rust vs Go vs C på de samme maskiner](/da/post/rust-go-c-benchmark-2026/) — samme hardware, anderledes spørgsmål.

## Opsætning

| | M1 Pro (Metal/MPS) | RTX 4070 Ti (CUDA) |
|---|---|---|
| **Maskine** | Apple MacBook Pro | Desktop-PC |
| **GPU** | M1 Pro 16-kerne GPU | NVIDIA GeForce RTX 4070 Ti |
| **VRAM / GPU-mem** | 16 GB unified (delt med CPU) | 12 GB GDDR6X |
| **CPU** | M1 Pro, 8-kerne (6P+2E) | Intel i5-13400F, 16 tråde |
| **RAM** | 16 GB | 125 GB |
| **OS** | macOS 26.6 | Ubuntu 24.04, CUDA 12.1, driver 595 |
| **PyTorch** | 2.7.0, MPS-backend | 2.5.1+cu121 |
| **ollama** | 0.30.8 | 0.30.8 |

## Benchmark 1 — GPU-matrixmultiplikation (rå TFLOPS)

En enkelt 4096×4096 tæt matmul, 20 tids-kørsler efter 5 opvarmningskørsler. Synkroniseret før og efter for at ekskludere kernel launch overhead. Dette er en proxy for **rå tensor-beregningsgennemstrømning** — loftet alt andet løber imod.

| Enhed | dtype | ms / kørsel | TFLOPS |
|-------|-------|:---:|:---:|
| i5-13400F CPU | float32 | 237,8 ms | 0,58 |
| M1 Pro CPU | float32 | 86,4 ms | 1,59 |
| M1 Pro MPS | float32 | 35,8 ms | 3,84 |
| M1 Pro MPS | float16 | 33,0 ms | 4,16 |
| RTX 4070 Ti CUDA | float32 | 4,9 ms | 28,3 |
| RTX 4070 Ti CUDA | float16 | **1,8 ms** | **75,3** |
| RTX 4070 Ti CUDA | bfloat16 | 1,8 ms | 74,9 |

### Hvad tallene betyder

**M1 Pro MPS float16 → float32 adskiller sig knap (4,16 vs 3,84 TFLOPS).** M1 GPU'en har ikke dedikerede fp16 tensor cores som NVIDIA. Begge præcisioner kører igennem den samme hardware; fp16-stien sparer noget hukommelsesbåndbredde men vinder lidt beregning.

**RTX 4070 Ti float16 → 75 TFLOPS — et 18× spring over M1 og et 2,7× spring over sin egen float32.** Dette er tensor core-effekten. NVIDIAs Ada Lovelace-generation (RTX 40xx) har 4. generation tensor cores der opererer nativt på fp16/bf16 matrix-felter og når ca. 4× gennemstrømningen af fp32 CUDA-kernerne på den samme chip. PyTorch router `torch.float16` matmul igennem dem automatisk.

**M1 Pro CPU slår Intel i5-13400F CPU med 2,7×** trods begge med 8 aktive tråde. M1 bruger **AMX (Apple Matrix Extensions)** — dedikerede matrix-multiplikationsenheder i hver CPU-kerne, separate fra NEON SIMD. PyTorches macOS-backend router float32-matmul igennem dem automatisk. Intel i5'en bruger AVX2 (256-bit SIMD ombrugt til matmul), som er generel brug og markant mindre effektivt til tæt matrixarbejde.

## Benchmark 2 — LLM-inferens (tokens / sekund, ollama)

Fast 300-token genereringsopgave, temperatur=0, målt som `eval_count / eval_duration` fra ollama API-svaret (ekskluderer prompt-eval-tid, som rapporteres separat). Prompten beder om en detaljeret forklaring af transformer-internals for at sikre at modellen genererer tæt, varieret output.

| Model | Størrelse | M1 Pro tok/s | RTX 4070 Ti tok/s | RTX / M1 |
|-------|:----:|:---:|:---:|:---:|
| minicpm-v4.6 | 1,6 GB | 95,3 | 278,9 | **2,9×** |
| qwen3.5 | 6,6 GB | 20,3 | 73,5 | **3,6×** |
| gemma4:12b | 7,6 GB | — | 49,1 | — |

*Prompt-eval (tid til første token): M1 Pro 25ms / 115ms; RTX 4070 Ti 9ms / 22ms / 42ms for de tre modeller.*

### Båndbredde-historien

Rå beregningsgabet er 18×. LLM-gennemstrømningsgabet er kun 3–4×. Hvorfor?

**LLM-dekodning ved batch=1 er hukommelsesbåndbredde-begrænset, ikke beregnings-begrænset.** Hvert genereret token kræver at indlæse hele sættet af modelvægte fra VRAM (eller unified memory) én gang per forward pass. Beregningen per byte er lav. GPU'en bruger næsten al sin tid på at flytte data, ikke multiplicere.

Det relevante tal er **hukommelsesbåndbredde**:
- RTX 4070 Ti: ~504 GB/s (GDDR6X, dedikeret VRAM-bus)
- M1 Pro: ~200 GB/s (LPDDR5X, delt CPU/GPU)

Båndbredde-forhold: **2,5×** — som matcher LLM-gennemstrømningsforholdet på 2,9–3,6× næsten præcist. M1 er langsommere fordi den har mindre hukommelsesbåndbredde, ikke fordi dens GPU er 18× svagere. Til LLM-inferens ved små batch-størrelser er det hukommelsesbåndbredde du reelt køber.

## Unified memory-fordelen

M1 Pro's GPU har adgang til **alle 16 GB** unified memory. En RTX 4070 Ti med 12 GB dedikeret VRAM rammer en hård grænse: modeller større end ~11 GB fp16 passer ikke og falder tilbage til langsomt system-RAM via PCIe, hvilket kollapser gennemstrømningen.

| Modelstørrelse (fp16) | M1 Pro 16GB | RTX 4070 Ti 12GB |
|---|---|---|
| 1–3B (~2–6 GB) | Kører hurtigt | Kører hurtigt |
| 7B (~14 GB) | Kører hurtigt | Passer stramt; passer måske ikke |
| 7B kvantiseret q4 (~4 GB) | Hurtigt | Hurtigt |
| 13B kvantiseret q4 (~8 GB) | Hurtigt | Hurtigt |
| 30B kvantiseret q4 (~18 GB) | Passer ikke | Passer ikke |

For det almindelige use case — en kvantiseret 7B- eller 13B-model — fungerer begge maskiner komfortabelt. M1 Pro's unified memory lader den indlæse en ukvantiseret 7B-model i fp16 der ville overløbe en 12GB RTX; RTX kører den samme model kvantiseret til q4 hurtigere samlet set.

## Hvad 95 vs 279 tok/s faktisk føles som

minicpm-v4.6 ved 95 tok/s på M1 Pro producerer tokens hurtigere end nogen læser. qwen3.5 ved 20 tok/s på M1 Pro er grænsen — man ser ord dukke op men det føles lidt langsomt. På RTX ved 74 tok/s er qwen3.5 komfortabelt.

Til **interaktiv brug**: 20–30 tok/s er gulvet for hvad der føles acceptabelt. Begge maskiner klarer det på den lille model; kun RTX klarer det komfortabelt på 6,6GB-modellen.

Til en **batch-transskriptions- eller resumé-pipeline** der kører kontinuerligt vinder RTX klart — 279 vs 95 tok/s betyder 3× gennemstrømningen med den samme model. Den [danske voicelog-pipeline](/da/post/dansk-voicelog-transkribering/) der bruger Claude Code-subagenter som resumélag kører præcis denne slags vedvarende batch-arbejdsbyrde; en RTX 4070 Ti ville køre den samme arbejdsbyrde på en tredjedel af clock-tiden.

## Strømforbrug

Ingen instrumenter var tilkoblet for denne kørsel, men nominel TDP giver størrelsesordenen:

| | Tomgang | Fuld GPU-belastning |
|---|---|---|
| M1 Pro MacBook Pro | ~5 W | ~25–30 W |
| RTX 4070 Ti (kort alene) | ~15 W | ~200 W |

M1 vinder afgørende på effektivitet. Ved 95 tok/s for ~25W og 279 tok/s for ~200W leverer RTX **2,9× ydelsen til 7–8× strømmen** — så M1 er **2,5× mere effektiv per watt** til LLM-inferens.

## Hvilken maskine til lokal AI?

| Use case | Vælg |
|---|---|
| Interaktiv lokal assistent (7B–13B kvantiseret) | Begge — RTX hurtigere, M1 roligere og mere effektiv |
| Vedvarende batch-inferens (transskribering, resuméer) | **RTX 4070 Ti** — 3× gennemstrømning |
| Indlæsning af store fp16-modeller uden kvantisering | **M1 Pro** — unified memory, ingen VRAM-grænse |
| Træning eller fine-tuning (LoRA) | **RTX 4070 Ti** — tensor cores, CUDA-økosystem |
| Always-on hjemmeserver (elregning betyder noget) | **M1 Pro** — ~7–8× lavere GPU-strømforbrug |
| Numerisk ML (CV, embeddings, matmul-tungt) | **RTX 4070 Ti** — 7–18× hurtigere |

---

*Benchmarks kørt på personligt hardware, juni 2026. LLM-gennemstrømning afhænger kraftigt af modelkvantisering, kontekstlængde og systembelastning — behandl disse tal som størrelsesordenssammenligninger, ikke absolutte specifikationer.*
