+++
title = "First look at the NVIDIA DGX Spark — what the box actually reports (2026)"
date = 2026-07-13
slug = "nvidia-dgx-spark-first-look"
description = "Unboxing an NVIDIA DGX Spark (GB10 Grace Blackwell) and reading it back from the command line: lscpu, free -h, nvidia-smi, lspci, lsblk. A 20-core Arm CPU, 128 GB unified memory, a Blackwell GPU — and 120B-parameter LLMs running locally."

[taxonomies]
tags = ["nvidia", "dgx-spark", "gb10", "grace-blackwell", "local-ai", "arm", "llm", "ollama", "benchmark"]

[extra]
summary = "The NVIDIA DGX Spark reports itself as a 20-core Arm machine (10× Cortex-X925 + 10× Cortex-A725), 121 GiB of unified LPDDR5x memory, a single GB10 Blackwell GPU on CUDA 13, and a 4 TB Samsung NVMe — all in a gold box the size of a thick paperback. This first-look post reads the whole machine back from the command line (lscpu, free -h, nvidia-smi, lspci, lsblk) and shows it doing the one thing no consumer GPU can: holding a 67 GB llama4:scout and a 65 GB gpt-oss:120b model in memory at the same time."
faq = [
  { q = "What is the NVIDIA DGX Spark?", a = "The DGX Spark is a small desktop AI computer built on NVIDIA's GB10 Grace Blackwell superchip — a 20-core Arm CPU and a Blackwell-generation GPU sharing 128 GB of unified LPDDR5x memory over a coherent link (NVLink-C2C). It's aimed at running and fine-tuning large models locally: because CPU and GPU share one memory pool, it can hold models far larger than a 12–24 GB consumer GPU's VRAM allows." },
  { q = "What CPU is in the DGX Spark?", a = "The GB10's CPU is a 20-core Arm design in a big.LITTLE arrangement: 10× Cortex-X925 performance cores (up to 3.9 GHz) and 10× Cortex-A725 efficiency cores (up to 2.8 GHz), reported by lscpu as a single NUMA node with 24 MB of L3 cache and full SVE2 support." },
  { q = "How much memory does the DGX Spark have?", a = "128 GB of unified LPDDR5x, of which free -h reports about 121 GiB usable. Crucially it's shared coherently between the CPU and GPU, so a large language model loaded into it is visible to the GPU without a copy across PCIe — that's what lets the box run 100B+ parameter models locally." },
  { q = "Can the DGX Spark run large LLMs locally?", a = "Yes — that's its whole point. On the unit in this post, ollama was holding llama4:scout (67 GB) and gpt-oss:120b (65 GB) — models that physically cannot fit on any single consumer GPU. A quick llama4:scout generation clocked ~15 tokens/second; a full benchmark post will follow." },
  { q = "What GPU and CUDA version does the DGX Spark report?", a = "nvidia-smi reports a single 'NVIDIA GB10' GPU on driver 580.159.03 with CUDA 13.0 and compute capability 12.1 (Blackwell). Idle it sits around 52 °C drawing ~13 W; under load in this session it hit 70 °C at 46 W." }
]
+++

**TL;DR —** The [NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) arrived — a gold brick the size of a thick paperback, built on the **GB10 Grace Blackwell** superchip. This first-look post does one thing: reads the whole machine back from the command line. The short version is a **20-core Arm CPU** (10× Cortex-X925 + 10× Cortex-A725), **121 GiB of unified LPDDR5x memory**, a single **GB10 Blackwell GPU** on **CUDA 13**, and a **4 TB Samsung NVMe** — running Ubuntu 24.04 on a `6.17.0-nvidia` kernel. And it's already holding two 100B-class language models in memory at once, which is the entire reason this box exists.

> Companion to [Ollama — the complete local-LLM guide](/post/ollama-komplet-guide/) and [M1 Pro vs RTX 4070 Ti for local AI](/post/m1-vs-rtx4070ti-ai-benchmark-2026/). A proper benchmark post will follow; this one is just "what does the machine say it is."

## The box

It's small and dense — a champagne-gold aluminium shell with a distinctive metallic-foam front grille (that's the intake). On the back: a power button, three USB-C ports, HDMI, a 5 GbE RJ45, and the two QSFP cages for the high-speed ConnectX networking. Mine sits on top of an older 1U machine in the rack and draws barely more than a laptop charger at idle.

Enough looking at it. Let's ask it what it is.

## What is this thing? — `hostnamectl` / `uname`

```
$ uname -a
Linux spark 6.17.0-1026-nvidia #26-Ubuntu SMP PREEMPT_DYNAMIC ... aarch64 aarch64 aarch64 GNU/Linux

$ hostnamectl
   Operating System: Ubuntu 24.04.4 LTS
             Kernel: Linux 6.17.0-1026-nvidia
       Architecture: arm64
    Hardware Vendor: NVIDIA
     Hardware Model: NVIDIA_DGX_Spark
   Firmware Version: 5.36_0ACUM023
      Firmware Date: Thu 2026-04-02
```

So: **Ubuntu 24.04.4 LTS**, an **arm64** machine on NVIDIA's own **`6.17.0-1026-nvidia`** kernel, identifying itself cleanly as `NVIDIA_DGX_Spark`. This isn't a Jetson-style embedded image — it's a normal Ubuntu Server userland on a custom kernel.

## The CPU — `lscpu`

This is the part that surprises people coming from x86. The GB10's CPU is a **20-core Arm big.LITTLE** design, and `lscpu` reports it as two core clusters:

```
$ lscpu
Architecture:            aarch64
CPU(s):                  20
On-line CPU(s) list:     0-19

Model name:              Cortex-X925      <- 10 performance cores
  Core(s) per socket:    10
  CPU max MHz:           3900.0000
  CPU min MHz:           1378.0000

Model name:              Cortex-A725      <- 10 efficiency cores
  Core(s) per socket:    10
  CPU max MHz:           2808.0000
  CPU min MHz:           338.0000

L1d / L1i cache:         1.3 MiB (20 instances) each
L2 cache:                25 MiB (20 instances)
L3 cache:                24 MiB (2 instances)
NUMA node(s):            1
NUMA node0 CPU(s):       0-19
Flags:                   ... sve sve2 sveaes svebf16 i8mm bf16 bti ...
```

Reading that back:

- **10× Arm Cortex-X925** performance cores, boosting to **3.9 GHz**.
- **10× Arm Cortex-A725** efficiency cores, up to **2.8 GHz**.
- **One NUMA node** — all 20 cores see memory uniformly, which keeps things simple.
- **24 MB of shared L3** (in 2 instances, one per cluster) plus a big 25 MB of L2.
- The flags line matters for ML: **SVE2**, **BF16**, and **I8MM** (int8 matrix) are all present — the CPU itself has modern vector/matrix extensions, not just the GPU.

## The memory — `free -h`

Here's the headline feature of the whole architecture:

```
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           121Gi        78Gi        16Gi       612Mi        28Gi        43Gi
Swap:           15Gi       413Mi        15Gi
```

**121 GiB of RAM** (128 GB nominal LPDDR5x, minus firmware/carveout). The number itself is unremarkable for a server — but on the Spark this is **unified memory**, shared coherently between the CPU and the GPU over NVLink-C2C. There is no separate "VRAM." A model loaded into these 121 GiB is directly visible to the Blackwell GPU with no PCIe copy.

That single fact is why this box exists. A 12 GB RTX 4070 Ti tops out around an 8B model in fp16; even a 24 GB card struggles past ~30B. The Spark treats a 67 GB model as unremarkable — see below.

## The GPU — `nvidia-smi`

```
$ nvidia-smi
NVIDIA-SMI 580.159.03   Driver Version: 580.159.03   CUDA Version: 13.0
+-----------------------------------------+------------------------+----------------------+
|   0  NVIDIA GB10               On       |   0000000F:01:00.0 Off |                  N/A |
| N/A   70C    P0    46W /  N/A           | Not Supported          |     94%      Default |
+-----------------------------------------+------------------------+----------------------+
| Processes:                                                                              |
|    0   ...   1784176   C   ...ollama/llama-server              67012MiB                 |
+-----------------------------------------------------------------------------------------+

$ nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader
NVIDIA GB10, 12.1
```

A single **NVIDIA GB10** GPU, **driver 580.159.03**, **CUDA 13.0**, **compute capability 12.1** (Blackwell). Note the memory-usage column reads `Not Supported` — because it's unified memory, `nvidia-smi` doesn't report a dedicated VRAM figure the way it would on a discrete card. Instead you can see the actual footprint in the process list: an `ollama` `llama-server` holding **67 GB** resident on the GPU.

Idle, the GPU is genuinely sleepy — around **52 °C at ~13 W**. Under the load captured here it was at **70 °C, 46 W, 94% util**. This is not a 300 W space heater.

## Storage — `lsblk` / `df`

```
$ lsblk -d -o NAME,SIZE,MODEL
NAME      SIZE  MODEL
nvme0n1   3.7T  SAMSUNG MZALC4T0HBL1-00B07

$ df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  3.7T  215G  3.3T   7% /
```

A single **4 TB Samsung NVMe** (the `3.7T` is the usual base-2 vs base-10 discrepancy), 215 GB used so far — most of that is the three LLMs sitting in `~/.ollama`. Plenty of room for datasets and model checkpoints.

## The PCI topology — `lspci`

```
$ lspci
0000:00:00.0 PCI bridge: NVIDIA Corporation Device 22ce (rev 01)
0002:00:00.0 PCI bridge: NVIDIA Corporation Device 22ce (rev 01)
0004:00:00.0 PCI bridge: NVIDIA Corporation Device 22ce (rev 01)
0004:01:00.0 Non-Volatile memory controller: Samsung Electronics Co Ltd Device a810
0007:00:00.0 PCI bridge: NVIDIA Corporation Device 22d0 (rev 01)
0007:01:00.0 Ethernet controller: Realtek Semiconductor Co., Ltd. Device 8127 (rev 05)
0009:00:00.0 PCI bridge: NVIDIA Corporation Device 22d0 (rev 01)
0009:01:00.0 Network controller: MEDIATEK Corp. Device 7925
000f:00:00.0 PCI bridge: NVIDIA Corporation Device 22d1
000f:01:00.0 VGA compatible controller: NVIDIA Corporation Device 2e12 (rev a1)
```

Everything hangs off NVIDIA-branded PCI bridges (the GB10's own root complex). The interesting endpoints:

- **Samsung NVMe** controller (the 4 TB drive).
- **Realtek 8127** — the 5 GbE RJ45 on the back (the blue cable in the photo).
- **MediaTek 7925** — Wi-Fi 7.
- **NVIDIA device `2e12`** as the "VGA compatible controller" — that's the Blackwell GPU.

## Networking — `ip link`

```
$ ip -br link
enP7s7     UP     <BROADCAST,MULTICAST,UP,LOWER_UP>   # 5 GbE (Realtek)
wlP9s9     UP     <BROADCAST,MULTICAST,UP,LOWER_UP>   # Wi-Fi 7 (MediaTek)
tailscale0 UNKNOWN <POINTOPOINT,...>                  # Tailscale
docker0    DOWN   <NO-CARRIER,...>                    # Docker bridge
```

I've got it on the wired 5 GbE and reachable over Tailscale, which is how I'm driving it headless. The two QSFP cages on the back — the ConnectX-7 200 GbE ports meant for clustering two Sparks together — aren't configured in this setup; nothing shows up under `/sys/class/infiniband` yet. That's a project for another day.

## The reason it exists — `ollama list`

```
$ ollama list
NAME            ID              SIZE     MODIFIED
llama4:scout    bf31604e25c2    67 GB    2 days ago
gpt-oss:120b    a951a23b46a1    65 GB    2 days ago
gemma4:26b      5571076f3d70    17 GB    2 days ago
```

This is the payoff. **A 67 GB model and a 65 GB model, both resident, on one desktop machine.** Neither would load onto any consumer GPU on the market — a 5090 has 32 GB. Here they're just files that fit in the unified memory pool.

A quick, unscientific generation on `llama4:scout` (a 109B-parameter mixture-of-experts model, 17B active) to get a feel for it:

```
$ curl -s localhost:11434/api/generate -d '{"model":"llama4:scout", ...}' | ...
model:      llama4:scout
eval_count: 90 tokens
tok/s:      15.2
```

**~15 tokens/second** on a 100B-class model, on a machine pulling under 100 W. That's genuinely usable for interactive work — not RTX-fast, but no RTX can hold this model in the first place. A rigorous multi-model benchmark (prompt-eval vs generation, batch sizes, the smaller models) is the next post.

## First impressions

- **The memory is the product.** Everything else — the Arm CPU, the Blackwell GPU, the NVMe — is in service of one idea: put 128 GB where both the CPU and GPU can reach it coherently, and suddenly 100B-parameter models are a desktop thing.
- **It's a normal Ubuntu box.** `apt`, `ollama`, Tailscale, Docker — nothing exotic in the userland. The arm64 architecture is the only thing you have to keep in mind (check for `aarch64` builds).
- **It sips power.** ~13 W idle GPU, under 100 W generating. It lives in the rack and I forget it's on.
- **CUDA 13 / compute 12.1 / driver 580** is the toolchain baseline to target if you're building against it.

Next up: a real benchmark — throughput across `gemma4:26b`, `llama4:scout`, and `gpt-oss:120b`, prompt-eval vs generation rates, and how the unified-memory model actually behaves as you push toward the top of the 121 GiB.

> If you're doing this on a laptop or a consumer GPU instead, [the Ollama guide](/post/ollama-komplet-guide/) and the [M1 Pro vs RTX 4070 Ti benchmarks](/post/m1-vs-rtx4070ti-ai-benchmark-2026/) cover that ground.
