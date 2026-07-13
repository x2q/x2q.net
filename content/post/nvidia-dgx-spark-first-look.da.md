+++
title = "Første kig på NVIDIA DGX Spark — hvad maskinen faktisk rapporterer (2026)"
date = 2026-07-13
slug = "nvidia-dgx-spark-foerste-kig"
description = "Udpakning af en NVIDIA DGX Spark (GB10 Grace Blackwell) og aflæsning af den fra kommandolinjen: lscpu, free -h, nvidia-smi, lspci, lsblk. En 20-kernes Arm-CPU, 128 GB unified memory, en Blackwell-GPU — og 120B-parameter-LLM'er kørende lokalt."

[taxonomies]
tags = ["nvidia", "dgx-spark", "gb10", "grace-blackwell", "lokal-ai", "arm", "llm", "ollama", "benchmark"]

[extra]
summary = "NVIDIA DGX Spark rapporterer sig selv som en 20-kernes Arm-maskine (10× Cortex-X925 + 10× Cortex-A725), 121 GiB unified LPDDR5x-hukommelse, en enkelt GB10 Blackwell-GPU på CUDA 13, og en 4 TB Samsung-NVMe — alt sammen i en guldfarvet kasse på størrelse med en tyk paperback. Dette første-kig-indlæg aflæser hele maskinen fra kommandolinjen (lscpu, free -h, nvidia-smi, lspci, lsblk) og viser den gøre det, ingen forbruger-GPU kan: holde en 67 GB llama4:scout og en 65 GB gpt-oss:120b i hukommelsen samtidig."
faq = [
  { q = "Hvad er NVIDIA DGX Spark?", a = "DGX Spark er en lille desktop-AI-computer bygget på NVIDIAs GB10 Grace Blackwell-superchip — en 20-kernes Arm-CPU og en Blackwell-generations-GPU der deler 128 GB unified LPDDR5x-hukommelse over et kohærent link (NVLink-C2C). Den er lavet til at køre og fine-tune store modeller lokalt: fordi CPU og GPU deler én hukommelsespulje, kan den holde modeller langt større end en 12–24 GB forbruger-GPU's VRAM tillader." },
  { q = "Hvilken CPU sidder i DGX Spark?", a = "GB10's CPU er et 20-kernes Arm-design i en big.LITTLE-opsætning: 10× Cortex-X925 performance-kerner (op til 3,9 GHz) og 10× Cortex-A725 efficiency-kerner (op til 2,8 GHz), rapporteret af lscpu som en enkelt NUMA-node med 24 MB L3-cache og fuld SVE2-understøttelse." },
  { q = "Hvor meget hukommelse har DGX Spark?", a = "128 GB unified LPDDR5x, hvoraf free -h rapporterer omkring 121 GiB brugbar. Afgørende er, at den deles kohærent mellem CPU og GPU, så en stor sprogmodel indlæst i den er synlig for GPU'en uden en kopi over PCIe — det er det, der lader kassen køre 100B+-parameter-modeller lokalt." },
  { q = "Kan DGX Spark køre store LLM'er lokalt?", a = "Ja — det er hele pointen. På enheden i dette indlæg holdt ollama llama4:scout (67 GB) og gpt-oss:120b (65 GB) — modeller der fysisk ikke kan passe på nogen enkelt forbruger-GPU. En hurtig llama4:scout-generering ramte ~15 tokens/sekund; et fuldt benchmark-indlæg følger." },
  { q = "Hvilken GPU og CUDA-version rapporterer DGX Spark?", a = "nvidia-smi rapporterer en enkelt 'NVIDIA GB10'-GPU på driver 580.159.03 med CUDA 13.0 og compute capability 12.1 (Blackwell). I tomgang ligger den omkring 52 °C og trækker ~13 W; under load i denne session ramte den 70 °C ved 46 W." }
]
+++

**Kort fortalt —** [NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/) er ankommet — en guldfarvet mursten på størrelse med en tyk paperback, bygget på **GB10 Grace Blackwell**-superchippen. Dette første-kig-indlæg gør én ting: aflæser hele maskinen fra kommandolinjen. Den korte version er en **20-kernes Arm-CPU** (10× Cortex-X925 + 10× Cortex-A725), **121 GiB unified LPDDR5x-hukommelse**, en enkelt **GB10 Blackwell-GPU** på **CUDA 13**, og en **4 TB Samsung-NVMe** — kørende Ubuntu 24.04 på en `6.17.0-nvidia`-kerne. Og den holder allerede to 100B-klasse-sprogmodeller i hukommelsen på én gang, hvilket er hele grunden til, at denne kasse findes.

> Ledsager til [Ollama — den komplette guide til lokal AI](/da/post/ollama-komplet-guide/) og [M1 Pro vs RTX 4070 Ti til lokal AI](/da/post/m1-vs-rtx4070ti-ai-benchmark-2026/). Et rigtigt benchmark-indlæg følger; dette handler bare om "hvad siger maskinen, at den er."

## Kassen

Den er lille og kompakt — en champagnefarvet aluminiumsskal med et karakteristisk metallisk skum-frontgitter (det er indsugningen). På bagsiden: en tænd-knap, tre USB-C-porte, HDMI, et 5 GbE RJ45, og de to QSFP-bure til det højhastigheds ConnectX-netværk. Min står oven på en ældre 1U-maskine i racket og trækker knap mere end en laptop-oplader i tomgang.

Nok med at kigge på den. Lad os spørge den, hvad den er.

## Hvad er det her? — `hostnamectl` / `uname`

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

Altså: **Ubuntu 24.04.4 LTS**, en **arm64**-maskine på NVIDIAs egen **`6.17.0-1026-nvidia`**-kerne, der identificerer sig rent som `NVIDIA_DGX_Spark`. Dette er ikke et Jetson-agtigt embedded-image — det er en normal Ubuntu Server-userland på en custom-kerne.

## CPU'en — `lscpu`

Det er den del, der overrasker folk, der kommer fra x86. GB10's CPU er et **20-kernes Arm big.LITTLE**-design, og `lscpu` rapporterer den som to kerne-klynger:

```
$ lscpu
Architecture:            aarch64
CPU(s):                  20
On-line CPU(s) list:     0-19

Model name:              Cortex-X925      <- 10 performance-kerner
  Core(s) per socket:    10
  CPU max MHz:           3900.0000
  CPU min MHz:           1378.0000

Model name:              Cortex-A725      <- 10 efficiency-kerner
  Core(s) per socket:    10
  CPU max MHz:           2808.0000
  CPU min MHz:           338.0000

L1d / L1i cache:         1.3 MiB (20 instances) hver
L2 cache:                25 MiB (20 instances)
L3 cache:                24 MiB (2 instances)
NUMA node(s):            1
NUMA node0 CPU(s):       0-19
Flags:                   ... sve sve2 sveaes svebf16 i8mm bf16 bti ...
```

Aflæst:

- **10× Arm Cortex-X925** performance-kerner, der booster til **3,9 GHz**.
- **10× Arm Cortex-A725** efficiency-kerner, op til **2,8 GHz**.
- **Én NUMA-node** — alle 20 kerner ser hukommelsen uniformt, hvilket holder tingene simple.
- **24 MB delt L3** (i 2 instanser, én per klynge) plus store 25 MB L2.
- Flags-linjen betyder noget for ML: **SVE2**, **BF16** og **I8MM** (int8-matrix) er alle til stede — CPU'en selv har moderne vektor/matrix-udvidelser, ikke kun GPU'en.

## Hukommelsen — `free -h`

Her er hovedfunktionen i hele arkitekturen:

```
$ free -h
               total        used        free      shared  buff/cache   available
Mem:           121Gi        78Gi        16Gi       612Mi        28Gi        43Gi
Swap:           15Gi       413Mi        15Gi
```

**121 GiB RAM** (128 GB nominelt LPDDR5x, minus firmware/carveout). Selve tallet er ubemærkelsesværdigt for en server — men på Spark er dette **unified memory**, delt kohærent mellem CPU og GPU over NVLink-C2C. Der er ingen separat "VRAM." En model indlæst i disse 121 GiB er direkte synlig for Blackwell-GPU'en uden en PCIe-kopi.

Det ene faktum er grunden til, at denne kasse findes. Et 12 GB RTX 4070 Ti topper omkring en 8B-model i fp16; selv et 24 GB-kort kæmper forbi ~30B. Spark behandler en 67 GB-model som ubemærkelsesværdig — se nedenfor.

## GPU'en — `nvidia-smi`

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

En enkelt **NVIDIA GB10**-GPU, **driver 580.159.03**, **CUDA 13.0**, **compute capability 12.1** (Blackwell). Bemærk at hukommelses-kolonnen viser `Not Supported` — fordi det er unified memory, rapporterer `nvidia-smi` ikke et dedikeret VRAM-tal, som den ville på et diskret kort. I stedet kan du se det faktiske fodaftryk i proceslisten: en `ollama` `llama-server`, der holder **67 GB** resident på GPU'en.

I tomgang er GPU'en ægte søvnig — omkring **52 °C ved ~13 W**. Under den load, der er fanget her, var den på **70 °C, 46 W, 94% util**. Dette er ikke en 300 W-varmeblæser.

## Lagring — `lsblk` / `df`

```
$ lsblk -d -o NAME,SIZE,MODEL
NAME      SIZE  MODEL
nvme0n1   3.7T  SAMSUNG MZALC4T0HBL1-00B07

$ df -h /
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p2  3.7T  215G  3.3T   7% /
```

En enkelt **4 TB Samsung-NVMe** (de `3.7T` er den sædvanlige base-2 vs base-10-forskel), 215 GB brugt indtil videre — det meste er de tre LLM'er, der ligger i `~/.ollama`. Masser af plads til datasæt og model-checkpoints.

## PCI-topologien — `lspci`

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

Alt hænger på NVIDIA-mærkede PCI-broer (GB10'ens eget root-complex). De interessante endpoints:

- **Samsung NVMe**-controller (4 TB-drevet).
- **Realtek 8127** — 5 GbE RJ45 på bagsiden (det blå kabel på billedet).
- **MediaTek 7925** — Wi-Fi 7.
- **NVIDIA device `2e12`** som "VGA compatible controller" — det er Blackwell-GPU'en.

## Netværk — `ip link`

```
$ ip -br link
enP7s7     UP     <BROADCAST,MULTICAST,UP,LOWER_UP>   # 5 GbE (Realtek)
wlP9s9     UP     <BROADCAST,MULTICAST,UP,LOWER_UP>   # Wi-Fi 7 (MediaTek)
tailscale0 UNKNOWN <POINTOPOINT,...>                  # Tailscale
docker0    DOWN   <NO-CARRIER,...>                    # Docker-bro
```

Jeg har den på det kablede 5 GbE og tilgængelig over Tailscale, hvilket er, hvordan jeg driver den headless. De to QSFP-bure på bagsiden — ConnectX-7 200 GbE-portene, der er beregnet til at klynge to Sparks sammen — er ikke konfigureret i denne opsætning; intet dukker op under `/sys/class/infiniband` endnu. Det er et projekt til en anden dag.

## Grunden til, at den findes — `ollama list`

```
$ ollama list
NAME            ID              SIZE     MODIFIED
llama4:scout    bf31604e25c2    67 GB    2 days ago
gpt-oss:120b    a951a23b46a1    65 GB    2 days ago
gemma4:26b      5571076f3d70    17 GB    2 days ago
```

Her er gevinsten. **En 67 GB-model og en 65 GB-model, begge residente, på én desktop-maskine.** Ingen af dem ville kunne indlæses på nogen forbruger-GPU på markedet — et 5090 har 32 GB. Her er de bare filer, der passer i unified-memory-puljen.

En hurtig, uvidenskabelig generering på `llama4:scout` (en 109B-parameter mixture-of-experts-model, 17B aktive) for at få en fornemmelse:

```
$ curl -s localhost:11434/api/generate -d '{"model":"llama4:scout", ...}' | ...
model:      llama4:scout
eval_count: 90 tokens
tok/s:      15.2
```

**~15 tokens/sekund** på en 100B-klasse-model, på en maskine der trækker under 100 W. Det er ægte brugbart til interaktivt arbejde — ikke RTX-hurtigt, men intet RTX kan holde denne model i første omgang. Et grundigt multi-model-benchmark (prompt-eval vs generering, batch-størrelser, de mindre modeller) er det næste indlæg.

## Første indtryk

- **Hukommelsen er produktet.** Alt andet — Arm-CPU'en, Blackwell-GPU'en, NVMe'en — er i tjeneste for én idé: sæt 128 GB, hvor både CPU og GPU kan nå dem kohærent, og pludselig er 100B-parameter-modeller en desktop-ting.
- **Det er en normal Ubuntu-kasse.** `apt`, `ollama`, Tailscale, Docker — intet eksotisk i userlandet. arm64-arkitekturen er det eneste, du skal huske på (tjek for `aarch64`-builds).
- **Den nipper til strømmen.** ~13 W GPU i tomgang, under 100 W under generering. Den lever i racket, og jeg glemmer, at den er tændt.
- **CUDA 13 / compute 12.1 / driver 580** er toolchain-baseline at sigte mod, hvis du bygger mod den.

Næste gang: et rigtigt benchmark — throughput på tværs af `gemma4:26b`, `llama4:scout` og `gpt-oss:120b`, prompt-eval vs genereringsrater, og hvordan unified-memory-modellen faktisk opfører sig, når man skubber mod toppen af de 121 GiB.

> Hvis du gør dette på en laptop eller en forbruger-GPU i stedet, dækker [Ollama-guiden](/da/post/ollama-komplet-guide/) og [M1 Pro vs RTX 4070 Ti-benchmarks](/da/post/m1-vs-rtx4070ti-ai-benchmark-2026/) det terræn.
