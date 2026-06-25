+++
title = "Google Coral Edge TPU Benchmarks & Experiments (2026)"
date = 2026-06-24
slug = "google-coral-edge-tpu-experiments-2026"
description = "Benchmark results for MobileNetV1, MobileNetV2, EfficientNet-M/L, and SSD object detection on the Google Coral USB Accelerator — plus a practical guide to what the Edge TPU is (and isn't) good for."

[taxonomies]
tags = ["linux", "ai", "benchmark", "hardware", "python"]

[extra]
summary = "Five models benchmarked on the Google Coral USB Accelerator: MobileNetV1 runs in 3.9 ms (5.3× faster than CPU), EfficientNet-L runs in 31 ms (9.7× faster), and SSD MobileNetV2 object detection runs in 12 ms (3.2× faster). Largest practical speedup comes from bigger models. This post shows the numbers and explains why."

faq = [
  { q = "What is the Coral Edge TPU TOPS number?", a = "Google rates it at 4 TOPS (tera-operations per second) for int8 operations. In practice, achievable throughput depends on model size relative to the 8 MB on-chip cache — models that fit entirely on-chip achieve the headline numbers, larger models incur CPU fallback." },
  { q = "Does the Coral Edge TPU work with PyTorch?", a = "No. The Edge TPU only runs TFLite int8 models that have been compiled with the edgetpu_compiler tool. You can export a PyTorch model → ONNX → TFLite (via tf.lite.TFLiteConverter) and then run the Edge TPU compiler, but the model must be fully quantized (post-training quantization or quantization-aware training)." },
  { q = "Can the Coral run LLMs?", a = "No. Even the smallest useful LLMs (Llama 3.2 1B ≈ 1 GB in int4) are orders of magnitude too large for the 8 MB on-chip cache. The Coral is designed for sub-10 MB inference models. For local LLMs, see the Ollama guide linked below." },
  { q = "Is the speedup consistent across model sizes?", a = "The speedup scales with model complexity. MobileNetV1/V2 (small, already fast on CPU) see 4–5× speedup. EfficientNet-L (a much heavier CPU workload at 300 ms) sees 9.7× speedup. The key insight: the Edge TPU removes a fixed per-layer overhead, so larger models benefit proportionally more." },
  { q = "What happens to models larger than 8 MB?", a = "The Edge TPU compiler partitions the model. Layers that fit on-chip run on the TPU; the remainder runs on CPU. Only the first 8 MB of parameters are cached — if a model exceeds that, you get partial acceleration. For the models tested here (4–13 MB), the compiler maps most ops onto the TPU." }
]
+++

**TL;DR:** The Google Coral USB Accelerator is a $30–60 USB dongle running a 4 TOPS ASIC. Benchmarked against an Intel i9-13900K: MobileNetV1 in **3.9 ms** (5×), EfficientNet-L in **31 ms** (10×), SSD object detection in **12 ms** (3.2×). Biggest gains come from models that would be slow on CPU. The chip is real — just narrow in scope.

---

## The hardware

The Coral USB Accelerator contains Google's Edge TPU ASIC, a chip designed exclusively for **int8 TensorFlow Lite inference**. Key specs:

| Spec | Value |
|---|---|
| Peak performance | 4 TOPS (int8) |
| On-chip SRAM (model cache) | 8 MB |
| Interface | USB 3.0 |
| Host OS support | Linux, macOS, Windows |
| Power draw | ~2 W (USB powered) |
| Price (2026) | ~$30–$60 |

The 8 MB on-chip cache is the defining constraint. Models smaller than 8 MB run entirely on-chip at full speed. Larger models are partitioned by the Edge TPU compiler — the first 8 MB worth of parameters go on-chip, the rest falls back to CPU.

---

## Setup

See [Setting Up the Google Coral Edge TPU on Ubuntu 24.04 (2026)](@/post/google-coral-edge-tpu-setup-ubuntu-2026.md) for the full setup guide, including the four `gasket-dkms` kernel patches required for Ubuntu 24.04 with kernel 6.8–6.17.

Test environment for these benchmarks:

| Component | Details |
|---|---|
| Host CPU | Intel Core i9-13900K |
| Host RAM | 64 GB DDR5 |
| OS | Ubuntu 24.04 LTS, kernel 6.17.0-35 |
| Edge TPU | Google Coral USB Accelerator (USB 3.0) |
| Runtime | libedgetpu1-std 16.0, python3-pycoral 2.0.0 |
| Container | ubuntu:20.04 via Docker (Python 3.8) |
| Runs per model | 50–100 (after 1 warm-up invocation) |

All Edge TPU timings are wall-clock `perf_counter()` around repeated `interpreter.invoke()` calls, averaged after warm-up. CPU timings use the identical setup without the delegate.

---

## Image classification benchmarks

Five models, all on a single 224×224 (or 300×300) BMP image:

| Model | Input | CPU (ms) | TPU (ms) | Speedup | Model size |
|---|---|---|---|---|---|
| MobileNetV1 1.0 224 | 224×224 | 20.9 | **3.9** | **5.3×** | 4.2 MB |
| MobileNetV2 1.0 224 | 224×224 | 17.0 | **4.3** | **3.9×** | 4.1 MB |
| EfficientNet-M | 240×240 | 119.2 | **12.5** | **9.5×** | 7.5 MB |
| EfficientNet-L | 300×300 | 301.5 | **31.2** | **9.7×** | 12 MB |

All four models correctly classified the test image (Grace Hopper portrait) as **"military uniform"** — the CPU and TPU outputs agree on the top label.

### Why does the speedup grow with model size?

MobileNetV1 takes 20.9 ms on CPU — it is already a lightweight model. The Coral compresses that to 3.9 ms. But EfficientNet-L takes 301 ms on CPU (a 14× larger workload), and the Coral handles it in 31 ms — a 9.7× improvement.

The Edge TPU eliminates per-operation dispatch overhead and runs int8 matrix operations in dedicated silicon. The more operations there are to run, the more overhead is eliminated. Small models that are already fast on CPU see modest absolute improvements; larger models see dramatic ones.

EfficientNet-L at 12 MB slightly exceeds the 8 MB on-chip cache, so the Edge TPU compiler partitions it — part runs on the ASIC, part falls back to CPU. That it still achieves 9.7× speedup despite partial fallback is a good sign.

---

## Object detection: SSD MobileNetV2 COCO

Beyond classification, the Edge TPU shines at **real-time object detection**. SSD MobileNetV2 (COCO, 300×300 input) is the canonical Coral detection model:

| | CPU | TPU | Speedup |
|---|---|---|---|
| SSD MobileNetV2 300×300 | 37.3 ms | **11.8 ms** | **3.2×** |
| Throughput | ~27 fps | **~85 fps** | — |

Detections on the Grace Hopper portrait (score threshold 0.4):

```
[person] score=0.80  box=[0.03, 0.00, 0.99, 1.00]
[tie]    score=0.77  box=[0.70, 0.44, 0.90, 0.56]
```

Both detections are correct — Grace Hopper is wearing a Navy uniform with a tie visible in the lower-right of the image. At **85 fps** on the TPU (vs 27 fps on CPU), this is comfortably real-time for a 30 fps camera feed with 2.8× headroom to spare.

---

## Latency summary

```
MobileNetV1 224  ████░░░░░░░░░░░░░░░░░░░░  3.9 ms  (5.3×)
MobileNetV2 224  ████░░░░░░░░░░░░░░░░░░░░  4.3 ms  (3.9×)
EfficientNet-M   ████████████░░░░░░░░░░░░ 12.5 ms  (9.5×)
SSD MobileNetV2  ████████████░░░░░░░░░░░░ 11.8 ms  (3.2×)
EfficientNet-L   ███████████████████████░ 31.2 ms  (9.7×)
```

For continuous inference (camera feed, audio classification loop), the MobileNet models at under 5 ms per frame are well within real-time territory even for 200 fps applications.

---

## Practical use cases

These numbers translate to specific real-world applications where the Coral is a good fit:

### Person detection / occupancy sensing

SSD MobileNetV2 at 11.8 ms (85 fps) means you can run person detection on a full 30 fps camera feed and still have ~65% CPU headroom for everything else — parsing frames, writing to disk, running application logic. This is the primary Coral use case in commercial products (smart doorbells, occupancy sensors, retail analytics).

### Edge audio classification

YAMNet and similar audio classifiers compile cleanly for the Edge TPU. At 3–5 ms per inference window, you can run audio classification on overlapping 25 ms windows in real time — useful for wake-word detection, sound event detection (glass breaking, baby crying), or industrial anomaly detection.

### Keyword spotting

Models like DS-CNN (depthwise separable CNN for keyword spotting) run at ~2–3 ms on the Edge TPU. A Raspberry Pi + Coral USB stick can do always-on keyword spotting at negligible power draw.

### What it is not good for

| Use case | Why it doesn't fit |
|---|---|
| LLM inference | Models are GB-scale; 8 MB cache is 100–1000× too small |
| FP32 / FP16 models | Edge TPU is int8-only; no floating point |
| Training | Inference-only chip |
| General-purpose compute | Not programmable; fixed hardware accelerator |
| Large vision transformers | ViT-B/16 is ~330 MB; will heavily spill to CPU |

---

## Benchmark code

The full benchmark script, running inside a Docker container:

```python
import time, numpy as np
from PIL import Image
from pycoral.utils import edgetpu
import tflite_runtime.interpreter as tflite

def bench(model_path, img, n=100, delegate=None):
    kwargs = {"experimental_delegates": [delegate]} if delegate else {}
    interp = tflite.Interpreter(model_path=model_path, **kwargs)
    interp.allocate_tensors()
    inp = interp.get_input_details()[0]
    out = interp.get_output_details()[0]
    x = np.expand_dims(np.array(img, dtype=np.uint8), 0)
    interp.set_tensor(inp["index"], x)
    interp.invoke()                          # warm up
    t0 = time.perf_counter()
    for _ in range(n):
        interp.set_tensor(inp["index"], x)
        interp.invoke()
    return (time.perf_counter() - t0) / n * 1000

print("Devices:", edgetpu.list_edge_tpus())

img = Image.open("grace_hopper.bmp").resize((224, 224))
delegate = tflite.load_delegate("libedgetpu.so.1")

cpu_ms = bench("mobilenet_v2_1.0_224_quant.tflite", img, n=50)
tpu_ms = bench("mobilenet_v2_1.0_224_quant_edgetpu.tflite", img, n=100, delegate=delegate)

print(f"CPU: {cpu_ms:.1f} ms   TPU: {tpu_ms:.1f} ms   ({cpu_ms/tpu_ms:.1f}×)")
```

Run it:

```bash
# Find device path
lsusb | grep '18d1:9302'
# Bus 002 Device 003: ID 18d1:9302 Google Inc.

docker run --rm \
  --device /dev/bus/usb/002/003 \
  -v $(pwd):/work \
  ubuntu:20.04 \
  bash -c "
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq gnupg curl python3 python3-numpy python3-pil
    curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
    echo 'deb https://packages.cloud.google.com/apt coral-edgetpu-stable main' \
        > /etc/apt/sources.list.d/coral.list
    apt-get update -qq
    apt-get install -y -qq libedgetpu1-std python3-pycoral
    cd /work && python3 bench.py
  "
```

---

## How it compares to other accelerators

For context, here is where the Coral sits in the broader landscape of inference accelerators available in 2026:

| Accelerator | Peak TOPS | Price | Form factor | Notes |
|---|---|---|---|---|
| Coral USB Accelerator | 4 (int8) | ~$40 | USB dongle | This post |
| NVIDIA Jetson Nano (2024) | 472 (int8) | ~$150 | Module/dev kit | Full GPU, much higher power |
| Hailo-8 | 26 (int8) | ~$50–100 | M.2 / HAT | Raspberry Pi compatible |
| Apple Neural Engine (M4) | 38 | — | Built into SoC | Not separately purchasable |
| Google TPU v4 (cloud) | 275,000 | per hour | Cloud | Training + inference |

The Coral is not the fastest or most capable accelerator — it is the cheapest USB-powered one that runs off a Raspberry Pi. Its niche is always-on, low-power, low-latency inference at the edge: door cameras, environmental sensors, robotics, industrial monitoring.

---

## Conclusion

The Google Coral USB Accelerator delivers real speedups for int8 TFLite models:

- **3–10× faster** inference across MobileNet and EfficientNet families
- **85 fps** object detection (SSD MobileNetV2, 300×300) vs 27 fps on CPU
- **Sub-5 ms latency** for MobileNet-class models — viable for any real-time application
- Biggest gains on models that are slow on CPU (EfficientNet-L: 301 ms → 31 ms, 9.7×)

The constraints are equally real: int8-only, 8 MB cache, TFLite-only. It will not run LLMs, FP16 models, or PyTorch models without a full quantized-TFLite conversion pipeline. But for the workloads it was designed for — lightweight vision and audio models at the edge — it is a capable and inexpensive piece of silicon.

For setup instructions (including the Ubuntu 24.04 kernel patches), see the [companion setup post](@/post/google-coral-edge-tpu-setup-ubuntu-2026.md).
