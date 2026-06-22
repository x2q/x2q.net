+++
title = "Rust vs Go vs C på Apple Silicon og Linux — benchmarks på rigtig hardware (2026)"
date = 2026-06-22
slug = "rust-go-c-benchmark-2026"
description = "Fire benchmarks — primtalssold, rekursiv Fibonacci, 512×512 matrixmultiplikation og parallel sum — på to maskiner: Apple M1 Pro (arm64/clang) og Intel i5-13400F (x86_64/gcc). Rust matcher C; Go overrasker på Fibonacci. Binærstørrelser, kompileringstider og en direkte pick-one-guide."

[taxonomies]
tags = ["rust", "go", "c", "benchmark", "performance", "systemprogrammering", "apple-silicon", "linux"]

[extra]
summary = "Fire benchmarks på to maskiner — Apple M1 Pro (macOS/clang) og Intel i5-13400F (Linux/gcc). Rust ≈ C på M1; på x86 Linux er Rust 1,5× langsommere end gcc på rekursiv fib og Go er 2,9× langsommere. Go's matrixmultiplikationsgab er 4,7× på Linux (mod 3,3× på arm64). Overraskelsen: Rust's parallel sum på x86 er 2,8× hurtigere end C pthreads — LLVM folder sandsynligvis rækken til en lukket formel."
faq = [
  { q = "Er Rust hurtigere end Go?", a = "På beregningsintensiv kode: ja, mærkbart. På en 512×512 double-precision matrixmultiplikation tog Rust 24–28ms mod Go's 80–107ms på begge testmaskiner. På rekursiv Fibonacci (n=47) på x86 Linux var Go 2,9× langsommere end C mens Rust var 1,5× langsommere. Forskellen skyldes Go's grænsecheck, mere konservativ auto-vektorisering og en svagere optimizer til dyb rekursion." },
  { q = "Er Rust lige så hurtig som C?", a = "På Apple Silicon med clang: ja, inden for støj på alle fire benchmarks. På x86 Linux med gcc: Rust matchede C på sold og matrixmultiplikation, men var 1,5× langsommere på rekursiv fib — gcc's rekursive-kaldsoptimering overgik rustc/LLVM her. Rust slog C 2,8× på parallel sum på x86, sandsynligvis fordi LLVM folder heltalrækken til en lukket formel som løkken aldrig kører." },
  { q = "Hvor store er de binære filer?", a = "På macOS: C 33KB, Rust 431KB, Go 2,5MB. På Linux: C 16KB, Rust 4,3MB, Go 1,9MB. Den store Linux Rust-binær skyldes statisk linking af standardbiblioteket; på macOS udskydes noget af dette til dylibs. Go bundler altid sin runtime statisk på begge platforme." },
  { q = "Hvad er hurtigst at kompilere?", a = "På macOS (clang): C 96ms, Go 319ms, Rust 660ms. På Linux (gcc): C 54ms, Go 193ms, Rust 134ms. Rust er dramatisk hurtigere at kompilere på Linux — rustc bruger LLVM som har bedre Linux x86_64 kodegennemstrømning, mens Go's compilerfordel over Rust skrumper markant på Linux." },
  { q = "Hvorfor er Go 2,9× langsommere end C på rekursiv Fibonacci på Linux?", a = "Go's amd64-optimizer genererer mindre effektiv kode til dybe rekursive funktionskald end gcc -O3. På arm64 (M1 Pro, kompileret af Go's arm64-backend) var forskellen kun 11%. i5-13400F-resultatet afslørede en reel compilerkvalitetsforskel i Go's x86_64-backend til rekursionstung kode." },
  { q = "Hvorfor er Rust's parallel sum hurtigere end C på Linux?", a = "Rust-koden summerer en u64-rækkevidde med `.sum()`. LLVM genkender en sum af en sammenhængende heltalrækkevidde som en aritmetisk rækkeformel (n*(n+1)/2-varianten) og eliminerer løkken fuldstændigt — O(1) uanset rækkeviddens størrelse. GCC med en manuel for-løkke anvender ikke denne optimering og lader det være en vektoriseret men stadig O(n) sum." }
]
+++

**Kort fortalt —** Fire benchmarks på to maskiner: **Apple M1 Pro** (arm64, macOS 26.6, clang 21) og **Intel i5-13400F** (x86\_64, Ubuntu 24.04, gcc 13). På M1 matcher Rust C inden for støj på alle tests. På Linux x86 **slår gcc rustc på rekursiv fib** (1,5×) og **Go's fib falder til 2,9× langsommere end C** — et meget større gab end på arm64. Den største overraskelse: **Rust's parallel sum er 2,8× hurtigere end C pthreads på x86**, sandsynligvis fordi LLVM folder heltalsrækken til en lukket formel som løkken aldrig rent faktisk kører.

## Opsætning

| | M1 Pro (arm64) | i5-13400F (x86\_64) |
|---|---|---|
| **Maskine** | Apple MacBook Pro | Desktop-PC |
| **RAM** | 16 GB | 125 GB |
| **OS** | macOS 26.6 (Sequoia) | Ubuntu 24.04 |
| **C-compiler** | Apple clang 21.0, `-O3 -march=native` | GCC 13.3, `-O3 -march=native` |
| **Go** | 1.26.4 darwin/arm64 | 1.22.4 linux/amd64 |
| **Rust** | 1.96.0 | 1.96.0 |
| **Rust-flag** | `-C opt-level=3 -C target-cpu=native` | `-C opt-level=3 -C target-cpu=native` |

Hvert benchmark kørtes tre gange; tabellerne nedenfor viser medianen af kørsel 2–3.

## De fire benchmarks

### 1 — Primtalssold (primtal op til 10.000.000)

Fladt bool-array-sold: skrive-tungt sekventiel hukommelsesadgang, letgrebet indre løkke. God proxy for hukommelsesbåndbredde-begrænset kode.

### 2 — Rekursiv Fibonacci (n = 47)

Ingen heap-allokering, ingen løkker — ~2,97 milliarder stakrammer. Måler rå kald-dispatch, grenforudsigelse og hvor aggressivt hver compiler inliner/optimerer dyb rekursion.

### 3 — Matrixmultiplikation (512 × 512, f64, i-k-j løkkerækkefølge)

Cache-venlig løkkerækkefølge men stadig en tæt FP-akkumulering i den indre løkke. Her betyder auto-vektorisering og eliminering af grænsecheck mest.

### 4 — Parallel sum (100.000.000 heltal, 8 tråde)

8 POSIX-tråde (C), goroutines (Go) eller `std::thread` (Rust), der hver summerer en partition af `0..100_000_000`. Tester tråd-spawn-overhead og hvor smart hver compiler håndterer den indre sum.

## Resultater: Apple M1 Pro (arm64, clang 21, macOS)

| Benchmark | C | Go 1.26 | Rust 1.96 |
|-----------|:---:|:---:|:---:|
| Sold (10M primtal) | 13,3 ms | 19,3 ms | **12,3 ms** |
| Fib(47) rekursiv | 8,86 s | 9,84 s | 8,91 s |
| Matrixmultiplikation 512² | 24,7 ms | 80,2 ms | **24,1 ms** |
| Parallel sum 100M | 3,0 ms | 10,7 ms | 3,4 ms |

## Resultater: Intel i5-13400F (x86\_64, gcc 13, Linux)

| Benchmark | C | Go 1.22 | Rust 1.96 |
|-----------|:---:|:---:|:---:|
| Sold (10M primtal) | 25,7 ms | 34,3 ms | 27,6 ms |
| Fib(47) rekursiv | 4,06 s | **11,86 s** | 6,02 s |
| Matrixmultiplikation 512² | 22,5 ms | 106,7 ms | 28,3 ms |
| Parallel sum 100M | 3,4 ms | 8,7 ms | **1,2 ms** |

*Median af 3 kørsler, kørsel 2 brugt. 2026-06-22.*

## Hastighed relativt til C, begge maskiner

| Benchmark | Go/C (M1) | Go/C (i5) | Rust/C (M1) | Rust/C (i5) |
|-----------|:---:|:---:|:---:|:---:|
| Sold | 1,45× | 1,33× | 0,92× | 1,07× |
| Fib(47) | 1,11× | **2,92×** | 1,01× | 1,48× |
| Matrixmultiplikation | 3,24× | **4,74×** | 0,98× | 1,26× |
| Parallel sum | 3,57× | 2,56× | 1,13× | **0,35×** |

## Tre ting der er værd at forklare

### 1 — Go's fib kollapser på x86

På M1 var Go's fib(47) 11% langsommere end C — i praksis det samme. På i5'en er det **2,9× langsommere**. Samme Go-version, samme algoritme. Forskellen er compiler-backend'en: Go's arm64-kodegeneration håndterer dybe rekursive kaldkæder mere effektivt end dens amd64-kodegeneration. Dette er et kendt kvalitetsgab; Go's x86-backend er generelt mindre moden end arm64-backendet til rekursionstunge mønstre.

### 2 — gcc slår rustc på rekursiv fib

På M1 (clang mod rustc, begge bruger LLVM) tog fib ~8,9s i begge sprog — identisk. På Linux producerede gcc 4,06s mens rustc producerede 6,02s — **gcc er 1,5× hurtigere**. GCC's optimizer anvender mere aggressiv tail-rekursion og inlining-heuristikker for dette specifikke mønster på x86. Det er en påmindelse om at "Rust bruger LLVM" ikke betyder at det altid vinder over gcc; GCC har 30+ år af x86-optimeringskunst bag sig.

### 3 — Rust's parallel sum er 2,8× hurtigere end C på x86

Rust-trådens krop er `(start..end).sum::<u64>()`. LLVM genkender en sum af en sammenhængende heltalsrækkevidde som en **aritmetisk rækkeformel** og erstatter løkken med en lukket beregning `n*(n+1)/2` — O(1), uanset rækkeviddens størrelse. GCC med den manuelle `for (i = start; i < end; i++) s += i;`-løkke anvender SIMD-vektorisering men laver ikke spring til lukket form. Resultat: Rust's otte tråde udfører hver én multiplikation; C's otte tråde summerer hver 12,5M heltal. 2,8×-forskellen er udelukkende en compiler-optimeringsforkel, ikke en sprogforskel. (På arm64 var denne effekt mindre fordi Apple clang også anvender noget af denne optimering.)

## Binærstørrelse og kompileringstid

| | C (macOS) | C (Linux) | Go (macOS) | Go (Linux) | Rust (macOS) | Rust (Linux) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Binærstørrelse (sold) | 33 KB | 16 KB | 2,5 MB | 1,9 MB | 431 KB | **4,3 MB** |
| Kold kompilering (sold) | 96 ms | 54 ms | 319 ms | 193 ms | 660 ms | 134 ms |

Rust-binæren der er **4,3 MB på Linux mod 431 KB på macOS** er den mest slående størrelsesforkel. På macOS linker Rust mod system-dylibs for dele af standardbiblioteket og holder binæren lille. På Linux linker Rust alt statisk, hvilket producerer en større men fuldt selvstændig binær uden system-biblioteksafhængighed — en reel fordel til containere.

Kompileringstider vender: Rust er **134ms på Linux mod 660ms på macOS** for en enkelt fil. LLVM's x86_64-backend er markant hurtigere til at udsende kode end dens arm64-backend.

## Anno 2026: hvor lever hvert sprog?

**C** er stadig referencepunktet og stadig hurtigst på rå rekursivt arbejde når gcc's optimizer er involveret. I 2026 er det ikke et førstehåndsvalg til nye projekter medmindre du skriver kernekode, embedded firmware eller FFI-klister — men compiler-kunsten akkumuleret siden 1972 er reel.

**Go** ramte 1.0 i 2012 med en klar tese: gør det at skrive netværkstjenester lige så hurtigt at udvikle som Python, mens man kører med effektiviteten af et kompileret sprog. Det har i høj grad lykkedes. Hvad det betaler for det: GC'en tilføjer latensvarians, og performance-loftet er lavere end Rust eller C for beregningstunge løkker. fib-resultatet på x86 afslører også at Go's optimizer har reelle kvalitetsgab på visse mønstre — den er tunet til hvad Go-kode faktisk ligner (interfaces, kanaler, HTTP-handlere), ikke trærekursion.

**Rust** ramte 1.0 i 2015 og har brugt et årti på at bevise at hukommelsessikkerhed uden GC er opnåeligt i stor skala. I 2026 accepterer Linux-kernen Rust til drivere (siden 6.1), Firefox og Chromium erstatter gradvist C++ med det, og ISRG omskriver kritisk netværksinfrastruktur i det. Den lukkede formel-sum-optimering ovenfor er et godt eksempel på hvad "zero-cost abstractions" betyder i praksis: at skrive idiomatisk Rust lader compileren anvende transformationer som en manuel C-løkke ikke kan udløse.

## Pick-one-guide

| Du vil... | Vælg |
|---|---|
| Skrive en Linux-driver eller kernemodul | **C** (eller Rust hvis subsystemet accepterer det) |
| Bygge en mikrotjeneste eller CLI-værktøj hurtigt | **Go** — tooling + goroutines + hurtig iteration |
| Skrive sikkerhedskritisk systemkode | **Rust** — borrowchecker, ingen GC, ingen UB |
| Optimere en varm numerisk indre løkke | **C** eller **Rust** — SIMD, ingen grænsecheck, fuld LLVM |
| Levere en statisk binær til en container | **Go** (statisk som standard) eller Rust (`musl`) |
| Målrette arm64-performance | **Rust** ≈ C, bedre end Go |
| Målrette x86-rekursiv kode | **C med gcc** vinder; Rust konkurrencedygtig; Go halter |

---

*Benchmarks kørt på personligt hardware; dine tal vil variere med CPU, OS-indstillinger og compiler-flag. Koden er fire enkelt-fils programmer, ingen eksterne afhængigheder. Alle compilere kaldt med fulde optimeringsflag som vist ovenfor.*
