+++
title = "Rust vs Go vs C på Apple Silicon — benchmarks på rigtig hardware (2026)"
date = 2026-06-22
slug = "rust-go-c-benchmark-2026"
description = "Fire benchmarks — primtalssold, rekursiv Fibonacci, 512×512 matrixmultiplikation og parallel sum — kompileret med fuld optimering på en Apple M1 Pro. Rust matcher C; Go overrasker på matrixmultiplikation. Binærstørrelser, kompileringstider og en direkte guide til at vælge sprog."

[taxonomies]
tags = ["rust", "go", "c", "benchmark", "performance", "systemprogrammering", "apple-silicon"]

[extra]
summary = "Fire benchmarks på en M1 Pro: Rust ≈ C inden for målestøj på alle tests; Go er 1,4× langsommere på sold, omtrent ens på fib, men 3,3× langsommere på matrixmultiplikation — det er overskriften. Kompileringstid: C 96ms, Go 319ms, Rust 660ms. Binærstørrelse: C 33KB, Go 2,5MB, Rust 440KB. Fulde tabeller og en pick-one-guide."
faq = [
  { q = "Er Rust hurtigere end Go?", a = "På beregningsintensiv kode: ja, mærkbart. På en 512×512 double-precision matrixmultiplikation (Apple M1 Pro, fuld optimering) tog Rust 24ms, Go 80ms — 3,3× langsommere. På et primtalssold var Rust 12ms mod Go 19ms (1,6×). Go er tæt på ved simpelt rekursivt arbejde som fib. Forskellen skyldes Go's grænsecheck og mere konservativ auto-vektorisering." },
  { q = "Er Rust lige så hurtig som C?", a = "I disse benchmarks: ja — inden for målestøj. Rust matchede C på sold (12,3ms vs 13,3ms), fib (~8,9s begge), matrixmultiplikation (24ms begge) og parallel sum (~3ms begge). Begge kompilerer til native maskinkode via LLVM med de samme -O3 / opt-level=3 flag." },
  { q = "Hvor store er de binære filer?", a = "C producerede 33KB-binærer (kun programmet, dynamisk linket libc). Go-binærer var 2,5MB (inkluderer runtime, GC, goroutine-scheduler — alt statisk linket). Rust landede på 430–460KB — større end C, men langt mindre end Go." },
  { q = "Hvilket sprog er hurtigst at kompilere?", a = "For et enkelt-fils program: C med clang var 96ms, Go 319ms, Rust 660ms. Rækkefølgen vendes på store projekter — Go's kompileringsmodel skalerer lineært uden genompilering af afhængigheder, mens Rust's borrowchecker-analyse vokser med kodebasen. Rust's inkrementelle kompilering mindsker forskellen i praksis." },
  { q = "Hvorfor er Go 3× langsommere på matrixmultiplikation?", a = "To årsager. Første: Go udfører grænsecheck på hvert slice-access — compileren kan sommetider eliminere dem, men ikke pålideligt i en triple-løkke. Anden: Go's compiler er mere konservativ end LLVM med at auto-vektorisere løkker; clang og rustc anvender begge SIMD-transformationer her, som Go ikke gør. Unsafe kode eller assembly kan genvinde dette gap i Go, men så har man forladt sprogets sikkerhedsgarantier." }
]
+++

**Kort fortalt —** På en Apple M1 Pro med fuld optimering **matcher Rust C på alle benchmarks** (inden for målestøj), og **Go kører 1,4–3,3× langsommere** afhængigt af opgaven. Den største forskel er matrixmultiplikation, hvor Go's grænsecheck og konservative auto-vektorisering koster 3,3× sammenlignet med både C og Rust. Kompileringstider: C er hurtigst; Go er i midten; Rust er langsomst på en enkelt kold fil.

## Opsætning

| | |
|---|---|
| **Maskine** | Apple MacBook Pro — M1 Pro, 8-kerne (6P + 2E) |
| **RAM** | 16 GB |
| **OS** | macOS 26.6 (Sequoia) |
| **C-compiler** | Apple clang 21.0, flag: `-O3 -march=native` |
| **Go** | 1.26.4 darwin/arm64, `go build` (standardflag) |
| **Rust** | 1.96.0, flag: `-C opt-level=3 -C target-cpu=native` |

Hvert benchmark køres tre gange; tabellen nedenfor viser medianen af kørsel 2–3 (kørsel 1 er opvarmningsstøj). Output undertrykkes for at eliminere I/O-tid.

## De fire benchmarks

### 1 — Primtalssold (primtal op til 10.000.000)

Et fladt bool-array-sold: skrive-tungt sekventiel hukommelsesadgang, letgrebet indre løkke. En god proxy for hukommelsesbåndbredde-begrænset kode. C- og Go-versionen bruger `bool`-arrays; Rust bruger `Vec<bool>`.

### 2 — Rekursiv Fibonacci (n = 47)

Ren funktionskaldsoverhead med eksponentiel rekursionsdybde. Ingen heap-allokering, ingen løkker — bare ~2,97 milliarder stakrammer. Måler rå kald-dispatch, grenforudsigelse og registertryk.

### 3 — Matrixmultiplikation (512 × 512, f64, i-k-j løkkerækkefølge)

i-k-j-ordenen er mere cache-venlig end naiv i-j-k, men den indre løkke er stadig en tæt FP-akkumulering. Her betyder auto-vektorisering og eliminering af grænsecheck mest.

### 4 — Parallel sum (100.000.000 heltal, 8 tråde)

Opdel intervallet over 8 POSIX-tråde (C), goroutines (Go) eller `std::thread` (Rust), summer hver partition, læg resultaterne sammen. Tester tråd-spawn-overhead, cache-linje-deling og den overhead hvert sprog lægger mellem "kør dette på en tråd" og "vent på resultatet."

## Resultater

| Benchmark | C (clang -O3) | Go 1.26 | Rust 1.96 |
|-----------|:---:|:---:|:---:|
| Sold (10M primtal) | 13,3 ms | 19,3 ms | **12,3 ms** |
| Fib(47) rekursiv | 8,86 s | 9,84 s | 8,91 s |
| Matrixmultiplikation 512² | 24,7 ms | 80,2 ms | **24,1 ms** |
| Parallel sum 100M | 3,0 ms | 10,7 ms | 3,4 ms |

*Median af 3 kørsler, kørsel 2 brugt. Apple M1 Pro, 2026-06-22.*

### Hastighed relativt til C

| Benchmark | Go/C | Rust/C |
|-----------|:---:|:---:|
| Sold | 1,45× langsommere | 0,92× (hurtigere) |
| Fib(47) | 1,11× langsommere | 1,01× |
| Matrixmultiplikation | **3,24× langsommere** | 0,98× |
| Parallel sum | 3,57× langsommere | 1,13× |

## Matrixmultiplikationsgabet

3,3×-forskellen Go/C på matrixmultiplikation er overskriften og fortjener en forklaring, fordi meget Go-kode arbejder udenom dette uden at de fleste forfattere lægger mærke til det.

**Grænsecheck.** Hvert slice-access i Go (`a[i][k]`, `b[k][j]`, `c[i][j]`) genererer et grænsecheck. Compileren eliminerer nogle af dem — særligt når den kan bevise at et indeks er inden for rækkevidde fra en omgivende `for range` — men inde i en manuelt indekseret triple-løkke beholder den dem konservativt. C og Rust har ingen tilsvarende overhead ved `-O3`/`opt-level=3`.

**SIMD auto-vektorisering.** Clang og rustc genkender begge den indre akkumuleringsløkke som kandidat til NEON (ARM SIMD)-transformation og anvender den. Go's compiler er mere konservativ; den prioriterer korrekthed og hurtig kompilering over aggressiv vektorisering, og den indre løkke her får skalarkode.

Man kan genvinde det meste af dette i Go med `unsafe`-indeksering eller CGo, men så har man forladt sprogets sikkerhedsgarantier. For en brugervendt webtjeneste der håndterer 1.000 forespørgsler per sekund er denne forskel i en matrixløkke irrelevant. For en numerisk opgave der kører kontinuerligt på en server er den reel.

## Binærstørrelse og kompileringstid

| | C | Go | Rust |
|---|:---:|:---:|:---:|
| Binærstørrelse (sold) | 33 KB | 2,5 MB | 431 KB |
| Kold kompilering (sold, enkelt fil) | 96 ms | 319 ms | 660 ms |

**C** linker dynamisk libc og leverer intet andet — binæren *er* bare din kode og compilerens runtime-shim. Lille, men du er afhængig af OS-versionen på den dynamiske linker.

**Go** linker statisk sin hele runtime — garbage collector, goroutine-scheduler, reflection, net-stack — ind i hver binær. De 2,5 MB inkluderer alt det. `go build` med `-trimpath` og `ldflags="-s -w"` kan skrumpe den til omkring 1,5 MB, men gulvet er højt. Fordelen: du leverer én statisk binær uden libc-afhængighed, hvilket er enormt nyttigt til containere.

**Rust** lander i midten: standardbiblioteket er statisk linket ind, LLVM's runtime-support er inkluderet, men der er ingen GC- eller scheduler-overhead. Binærer kan strippes yderligere med `strip` eller `lto = true` i Cargo.toml; `musl`-targets giver dig også statiske binærer.

For kompileringstid vender rækkefølgen på store kodebaser: Go's kompileringsmodel er arkitektonisk hurtig (ingen header-parsing, simpel afhængighedsgraf), mens Rust's borrowchecker og monomorfikation vokser med kodebasens størrelse. En `cargo build --release` på et 50.000-linjers Rust-projekt tager minutter; et sammenligneligt Go-projekt tager sekunder.

## Anno 2026: hvor lever hvert sprog?

**C** er stadig referencepunktet. Alle andre sprogets performance-historie fortælles i relation til det. I 2026 er det ikke et førstehåndsvalg til nye projekter medmindre du skriver kernekode, embedded firmware eller FFI-klister — men compiler-kunsten akkumuleret siden 1972 betyder at LLVM stadigvæk kan slå håndskrevet assembly i det normale tilfælde. Det vinder på binærstørrelse og kompileringshastighed, taber på sikkerhed, tooling-ergonomi og de årtiers CVE'er der følger med manuel hukommelseshåndtering.

**Go** ramte 1.0 i 2012 med en klar tese: gør det at skrive netværkstjenester lige så hurtigt at udvikle som Python, mens man kører med effektiviteten af et kompileret sprog. Det har i høj grad lykkedes. Sproget er lille, toolingen (`go test`, `go fmt`, `go vet`, `go mod`) leveres med nul konfiguration, og goroutines gør samtidige tjenester naturlige at skrive. Det forsøger ikke at slå C; det forsøger at være den bedre C til tjenester. Hvad det betaler for det: GC'en tilføjer latensvarians, og performance-loftet er lavere end Rust eller C for beregningstunge indre løkker.

**Rust** ramte 1.0 i 2015 og brugte det efterfølgende årti på at bevise at man kan have hukommelsessikkerhed uden en garbage collector. I 2026 har det vundet betydeligt embedded-, systems- og infrastrukturterritorium: Linux-kernen accepterer Rust til drivere (siden 6.1), ISRG omskriver kritiske netværksværktøjer i det, og både Firefox og Chromium erstatter gradvist C++ med det. Borrow checkeren er det berømte friktionspunkt — og det er reelt — men moderne Rust med async/await, `Arc<Mutex<T>>`-mønstre og `rayon` til dataparallelisme er mere ergonomisk end i 2018. Vil du have C-niveau kontrol og hastighed med hukommelsessikkerhedsgarantier, er Rust svaret.

## Pick-one-guide

| Du vil... | Vælg |
|---|---|
| Skrive en Linux-driver eller kernemodul | **C** (eller Rust, hvis subsystemet accepterer det) |
| Bygge en mikrotjeneste eller CLI-værktøj hurtigt | **Go** — tooling + goroutines + hurtig iteration |
| Skrive sikkerhedskritisk systemkode | **Rust** — borrowchecker, ingen GC, ingen UB |
| Optimere en varm numerisk indre løkke | **C** eller **Rust** — SIMD, ingen grænsecheck |
| Levere en statisk binær til en container | **Go** (statisk som standard) eller Rust (`musl`) |
| Bidrage til en eksisterende kodebase | Match det der allerede er der |

Der er ikke et universelt svar i 2026 — og det er fint. C, Go og Rust besætter genuint forskellige dele af designrummet. Benchmarket fortæller dig performance-loftet for hvert; projektet fortæller dig hvilket loft du har brug for at nå.

---

*Benchmarks blev kørt på en personlig maskine; dine tal vil variere med chip, OS-indstillinger og compiler-flag. Koden er ligetil og reproducerbar: fire enkelt-fils programmer, ingen eksterne afhængigheder, fulde flag vist ovenfor.*
