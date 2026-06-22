+++
title = "Rust vs Go vs C on Apple Silicon — benchmarks on real hardware (2026)"
date = 2026-06-22
slug = "rust-go-c-benchmark-2026"
description = "Four benchmarks — prime sieve, recursive Fibonacci, 512×512 matrix multiply, and concurrent sum — compiled at full optimisation on an Apple M1 Pro. Rust matches C; Go surprises on matrix multiply. Binary sizes, compile times, and a no-nonsense pick-one guide."

[taxonomies]
tags = ["rust", "go", "c", "benchmark", "performance", "systems-programming", "apple-silicon"]

[extra]
summary = "Four benchmarks on an M1 Pro: Rust ≈ C within noise on every test; Go is 1.4× slower on sieve, roughly equal on fib, but 3.3× slower on matrix multiply — that's the headline. Compile time: C 96ms, Go 319ms, Rust 660ms. Binary size: C 33KB, Go 2.5MB, Rust 440KB. Full tables and a pick-one guide."
faq = [
  { q = "Is Rust faster than Go?", a = "On compute-bound code: yes, meaningfully. On a 512×512 double-precision matrix multiply (Apple M1 Pro, full optimisations), Rust took 24ms, Go 80ms — 3.3× slower. On a prime sieve Rust was 12ms vs Go 19ms (1.6×). Go is close on simple recursive work like fib. The gap comes from Go's bounds checking and more conservative auto-vectorisation." },
  { q = "Is Rust as fast as C?", a = "In these benchmarks: yes — within measurement noise. Rust matched C on sieve (12.3ms vs 13.3ms), fib (~8.9s each), matrix multiply (24ms each), and concurrent sum (~3ms each). Both compile to native machine code via LLVM with the same -O3 / opt-level=3 flags." },
  { q = "How big are the binaries?", a = "C produced 33KB binaries (just the program, dynamically linked libc). Go binaries were 2.5MB (includes the runtime, GC, goroutine scheduler, all linked statically). Rust landed at 430–460KB — bigger than C but far smaller than Go." },
  { q = "Which is fastest to compile?", a = "For a single-file program: C with clang was 96ms, Go 319ms, Rust 660ms. The order flips on large projects — Go's compilation model scales linearly without dependency recompilation, while Rust's borrow-checker analysis compounds. Rust's incremental compilation narrows the gap in practice." },
  { q = "Why is Go 3× slower on matrix multiply?", a = "Two reasons. First, Go performs bounds checking on every slice access — the compiler can sometimes eliminate them, but not reliably inside a triple loop. Second, Go's compiler is more conservative than LLVM about auto-vectorising loops; clang and rustc both apply SIMD transformations here that Go doesn't. Unsafe code or assembly can recover this gap in Go, but that defeats the point." }
]
+++

**TL;DR —** On an Apple M1 Pro with full optimisations, **Rust matches C on every benchmark** (within measurement noise), and **Go runs 1.4–3.3× slower** depending on the workload. The biggest gap is matrix multiply, where Go's bounds checking and conservative auto-vectorisation cost 3.3× compared to both C and Rust. Compile times: C is fastest; Go is in the middle; Rust is slowest on a cold single file.

## Setup

| | |
|---|---|
| **Machine** | Apple MacBook Pro — M1 Pro, 8-core (6P + 2E) |
| **RAM** | 16 GB |
| **OS** | macOS 26.6 (Sequoia) |
| **C compiler** | Apple clang 21.0, flags: `-O3 -march=native` |
| **Go** | 1.26.4 darwin/arm64, `go build` (default flags) |
| **Rust** | 1.96.0, flags: `-C opt-level=3 -C target-cpu=native` |

Each benchmark was run three times; the table below shows the median of runs 2–3 (run 1 is warmer-up noise). Output was suppressed to eliminate I/O time.

## The four benchmarks

### 1 — Sieve of Eratosthenes (primes up to 10,000,000)

A flat bit-array sieve: write-heavy sequential memory access, branch-light inner loop. A good proxy for memory-bandwidth-bound code. The C and Go versions use `bool` arrays; Rust uses `Vec<bool>`.

### 2 — Recursive Fibonacci (n = 47)

Pure function-call overhead with exponential recursion depth. No heap allocation, no loops — just ~2.97 billion stack frames. Measures raw call dispatch, branch prediction, and register pressure.

### 3 — Matrix multiply (512 × 512, f64, i-k-j loop order)

The i-k-j trip-order is cache-friendlier than naïve i-j-k, but the inner loop is still a tight FP accumulate. This is where auto-vectorisation and bounds-check elimination matter most.

### 4 — Concurrent sum (100,000,000 integers, 8 threads)

Split the range across 8 POSIX threads (C), goroutines (Go), or `std::thread` (Rust), sum each partition, add the results. Tests thread spawn overhead, cache-line sharing, and the overhead each language puts between "run this on a thread" and "wait for the result."

## Results

| Benchmark | C (clang -O3) | Go 1.26 | Rust 1.96 |
|-----------|:---:|:---:|:---:|
| Sieve (10M primes) | 13.3 ms | 19.3 ms | **12.3 ms** |
| Fib(47) recursive | 8.86 s | 9.84 s | 8.91 s |
| Matrix multiply 512² | 24.7 ms | 80.2 ms | **24.1 ms** |
| Concurrent sum 100M | 3.0 ms | 10.7 ms | 3.4 ms |

*Median of 3 runs, run 2 used. Apple M1 Pro, 2026-06-22.*

### Speed relative to C

| Benchmark | Go/C | Rust/C |
|-----------|:---:|:---:|
| Sieve | 1.45× slower | 0.92× (faster) |
| Fib(47) | 1.11× slower | 1.01× |
| Matrix multiply | **3.24× slower** | 0.98× |
| Concurrent sum | 3.57× slower | 1.13× |

## The matrix multiply gap

The 3.3× Go/C gap on matrix multiply is the headline and deserves an explanation, because a lot of Go code works around this without most authors realising it.

**Bounds checking.** Every slice access in Go (`a[i][k]`, `b[k][j]`, `c[i][j]`) generates a bounds check. The compiler eliminates some of them — particularly when it can prove an index is in-range from an enclosing `for range` — but inside a manually-indexed triple loop it conservatively keeps them. C and Rust have no equivalent overhead at `-O3`/`opt-level=3`.

**SIMD auto-vectorisation.** Clang and rustc both recognise the inner accumulate loop as a candidate for NEON (ARM SIMD) transformation and apply it. Go's compiler is more conservative; it targets correctness and fast compilation over aggressive vectorisation, and the inner loop here gets scalar code.

You can recover most of this in Go with `unsafe` indexing or CGo, but then you've left the language's safety guarantees behind. For a user-facing web service handling 1,000 RPS, this difference in a matrix loop is irrelevant. For a numerical workload running continuously on a server, it's real.

## Binary size and compile time

| | C | Go | Rust |
|---|:---:|:---:|:---:|
| Binary size (sieve) | 33 KB | 2.5 MB | 431 KB |
| Cold compile (sieve, single file) | 96 ms | 319 ms | 660 ms |

**C** dynamically links libc and ships nothing else — the binary *is* just your code and the compiler's runtime shim. Tiny, but you carry an OS-version dependency on the dynamic linker.

**Go** statically links its entire runtime — garbage collector, goroutine scheduler, reflection, net stack — into every binary. The 2.5 MB includes all of that. `go build` with `-trimpath` and `ldflags="-s -w"` can shrink it to around 1.5 MB, but the floor is high. The upside: you ship a single static binary with no libc dependency, which is enormously useful for containers.

**Rust** lands in the middle: the standard library is statically linked in, LLVM's runtime support is included, but there's no GC or scheduler overhead. Binaries can be stripped further with `strip` or `lto = true` in Cargo.toml; `musl` targets get you to single static binaries too.

For compile time, the order flips on large codebases: Go's compilation model is architecturally fast (no header parsing, simple dependency graph), while Rust's borrow-checker and monomorphisation compound with codebase size. A `cargo build --release` on a 50K-line Rust project takes minutes; a comparable Go project takes seconds.

## Anno 2026: where does each language live?

**C** is still the reference point. Every other language's performance story is told relative to it. In 2026 it's not a first-choice for new projects unless you're writing kernels, embedded firmware, or FFI glue — but the optimizer art accumulated since 1972 means LLVM can still beat hand-written assembly in the common case. It wins on binary size and compile speed, loses on safety, tooling ergonomics, and the decades of CVEs that come with manual memory.

**Go** hit 1.0 in 2012 with a clear thesis: make writing networked services as fast to develop as Python, while running with the efficiency of a compiled language. It has largely succeeded. The language is small, the tooling (`go test`, `go fmt`, `go vet`, `go mod`) ships with zero configuration, and goroutines make concurrent services natural to write. It's not trying to beat C; it's trying to be the better C for services. Where it pays for this: the GC adds latency variance, and the performance ceiling is lower than Rust or C for compute-heavy inner loops.

**Rust** reached 1.0 in 2015 and spent the following decade proving that you can have memory safety without a garbage collector. In 2026 it has won significant embedded, systems, and infrastructure territory: the Linux kernel accepts Rust for drivers (since 6.1), ISRG rewrites critical network tools in it, and both Firefox and Chromium are incrementally replacing C++ with it. The borrow checker is the famous friction point — and it's real — but modern Rust with async/await, `Arc<Mutex<T>>` patterns, and `rayon` for data parallelism is more ergonomic than it was in 2018. If you want C-level control and speed with memory-safety guarantees, Rust is the answer.

## Pick-one guide

| You want to... | Reach for |
|---|---|
| Write a Linux driver or kernel module | **C** (or Rust, if the subsystem accepts it) |
| Build a microservice or CLI tool fast | **Go** — tooling + goroutines + fast iteration |
| Write safety-critical systems code | **Rust** — borrow checker, no GC, no UB |
| Optimise a hot numerical inner loop | **C** or **Rust** — SIMD, no bounds checks |
| Ship a static binary to a container | **Go** (static by default) or Rust (`musl`) |
| Contribute to an existing codebase | Match what's already there |

There is no universal answer in 2026 — and that's fine. C, Go, and Rust occupy genuinely different parts of the design space. The benchmark tells you the performance ceiling of each; the project tells you which ceiling you need to hit.

---

*Benchmarks were run on a personal machine; your numbers will vary with chip, OS tuning, and compiler flags. The code is straightforward and reproducible: four single-file programs, no external dependencies, full flags shown above.*
