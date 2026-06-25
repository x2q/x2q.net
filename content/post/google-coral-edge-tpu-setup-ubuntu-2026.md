+++
title = "Setting Up the Google Coral Edge TPU on Ubuntu 24.04 (2026)"
date = 2026-06-24
slug = "google-coral-edge-tpu-setup-ubuntu-2026"
description = "How to fix gasket-dkms build failures on kernel 6.8–6.17, reload udev rules so the USB Coral gets proper permissions, and verify the hardware works with a Docker-based pycoral test."

[taxonomies]
tags = ["linux", "ai", "guide", "python", "hardware"]

[extra]
summary = "The Google Coral USB Accelerator is a $30–$60 inference chip that can run quantized TFLite models at 4 TOPS — but getting it working on Ubuntu 24.04 with kernel 6.8+ requires patching the gasket-dkms source for four kernel API breakages. This post walks through every step."
+++

**TL;DR:** Four kernel API changes break `gasket-dkms 1.0` on kernels ≥ 6.8. Patch the four lines in `/usr/src/gasket-1.0/`, rebuild with DKMS, reload udev rules so the device re-enumerates to `18d1:9302`, then test inference inside a Debian/Ubuntu container with `python3-pycoral`. The hardware runs fine once the plumbing is sorted.

---

## What is the Google Coral Edge TPU?

The [Google Coral](https://coral.ai/) USB Accelerator is a small USB 3.0 dongle containing Google's Edge TPU ASIC — a purpose-built chip for running quantized (int8) TensorFlow Lite models. At around $30–$60 it delivers **4 TOPS** (tera-operations per second) of inference throughput in a form factor smaller than a thumb drive.

It is not a general-purpose GPU. It only runs **TFLite int8 models that have been compiled with the Edge TPU compiler**, and each model must fit within its 8 MB of on-chip SRAM (larger models get partially cached — the "cold" portion runs on CPU). But for the right workloads — image classification, object detection, audio classification, person detection — it is genuinely fast.

The Coral product line also includes M.2 and mini-PCIe versions (which use the same `apex` PCIe driver), but this post focuses on the USB variant.

---

## The problem: gasket-dkms fails on modern kernels

When you install `gasket-dkms` (the kernel module package that ships the `apex` PCIe driver for Coral M.2 boards) on Ubuntu 24.04 running kernel 6.8–6.17, `apt` leaves the package in a broken state:

```
iF  gasket-dkms    1.0-18    all    DKMS source for the gasket driver
```

The `i` means the package is installed, `F` means it **failed to configure**. Running `sudo apt dist-upgrade` or `sudo dpkg --configure -a` loops forever trying and failing to build the kernel module.

Even if you only have the USB Coral and never plan to use the PCIe driver, `gasket-dkms` is a dependency of `libedgetpu1-std`, so fixing it unblocks the whole stack.

The build log at `/var/lib/dkms/gasket/1.0/build/make.log` shows four distinct errors:

```
gasket_interrupt.c:161: error: too many arguments to function 'eventfd_signal'
gasket_page_table.c:57: error: expected ',' or ';' before 'DMA_BUF'
gasket_core.c:1375: error: 'no_llseek' undeclared; did you mean 'noop_llseek'?
gasket_core.c:1841: error: too many arguments to function 'class_create'
```

These are all upstream kernel API changes that accumulated since the last time the `gasket-dkms` package was updated.

---

## Patching the source

The source lives at `/usr/src/gasket-1.0/`. DKMS re-reads this directory every time it builds, so patching it directly persists across kernel upgrades.

### 1. `eventfd_signal` lost its `n` argument (kernel ≥ 6.8)

```c
// gasket_interrupt.c:161 — before
eventfd_signal(ctx, 1);

// after
eventfd_signal(ctx);
```

```bash
sudo sed -i 's/eventfd_signal(ctx, 1);/eventfd_signal(ctx);/' \
    /usr/src/gasket-1.0/gasket_interrupt.c
```

### 2. `MODULE_IMPORT_NS` now takes a string literal (kernel ≥ 6.13)

Before kernel 6.13, `MODULE_IMPORT_NS(DMA_BUF)` worked because the macro called `__stringify()` internally. From 6.13 onward the macro expects a pre-quoted string. Kernels < 6.13 on the same machine break if you use the new form, so we need a version guard:

```c
// gasket_page_table.c — replace the bare macro with:
#include <linux/version.h>
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 13, 0)
MODULE_IMPORT_NS("DMA_BUF");
#else
MODULE_IMPORT_NS(DMA_BUF);
#endif
```

Apply with Python so the quotes survive the shell:

```bash
sudo python3 -c "
with open('/usr/src/gasket-1.0/gasket_page_table.c', 'r') as f:
    c = f.read()
old = 'MODULE_IMPORT_NS(\"DMA_BUF\");'
new = '''#include <linux/version.h>
#if LINUX_VERSION_CODE >= KERNEL_VERSION(6, 13, 0)
MODULE_IMPORT_NS(\"DMA_BUF\");
#else
MODULE_IMPORT_NS(DMA_BUF);
#endif'''
with open('/usr/src/gasket-1.0/gasket_page_table.c', 'w') as f:
    f.write(c.replace(old, new))
print('done')
"
```

> **Note:** You need to run this *after* the initial `sed` pass that changed `MODULE_IMPORT_NS(DMA_BUF)` to `MODULE_IMPORT_NS("DMA_BUF")`. If you are starting fresh, just insert the version-guarded block directly.

### 3. `no_llseek` renamed to `noop_llseek` (kernel ≥ 6.x)

```bash
sudo sed -i 's/\.llseek = no_llseek,/.llseek = noop_llseek,/' \
    /usr/src/gasket-1.0/gasket_core.c
```

### 4. `class_create` lost its `module` argument (kernel ≥ 6.4)

```c
// gasket_core.c:1841 — before
class_create(driver_desc->module, driver_desc->name);

// after
class_create(driver_desc->name);
```

```bash
sudo sed -i 's/class_create(driver_desc->module, driver_desc->name)/class_create(driver_desc->name)/' \
    /usr/src/gasket-1.0/gasket_core.c
```

---

## Rebuilding with DKMS

Remove the broken DKMS state and add the patched source back:

```bash
sudo dkms remove gasket/1.0 --all
sudo dkms add gasket/1.0
```

Build for the running kernel first (sanity check):

```bash
sudo dkms build gasket/1.0 -k $(uname -r)
```

If that succeeds, install it:

```bash
sudo dkms install gasket/1.0 -k $(uname -r)
```

Then let dpkg finish the configuration (it will build for all remaining kernels that have headers installed):

```bash
sudo dpkg --configure gasket-dkms
```

You should see all builds succeed and the final `dpkg -l gasket-dkms` output show `ii` (installed, configured):

```
ii  gasket-dkms    1.0-18    all    DKMS source for the gasket driver
```

---

## USB device: udev rules and re-enumeration

The Coral USB Accelerator ships in two USB states:

| VID:PID | Description |
|---|---|
| `1a6e:089a` | Uninitialized — appears at power-on before firmware is loaded |
| `18d1:9302` | Ready — device has received firmware from the host, inference-capable |

The Coral apt repo installs a udev rule at `/lib/udev/rules.d/60-libedgetpu1-std.rules`:

```
SUBSYSTEM=="usb",ATTRS{idVendor}=="1a6e",ATTRS{idProduct}=="089a",GROUP="plugdev"
SUBSYSTEM=="usb",ATTRS{idVendor}=="18d1",ATTRS{idProduct}=="9302",GROUP="plugdev"
```

If the device was plugged in before the rules were reloaded it will show `root:root` permissions. Reload and re-trigger:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=usb
```

After a second or two, check:

```bash
lsusb | grep -E '1a6e|18d1'
# Bus 002 Device 003: ID 18d1:9302 Google Inc.
```

The device should now show as `18d1:9302` (firmware loaded) with `root:plugdev` permissions:

```bash
ls -la /dev/bus/usb/002/003
# crw-rw---- 1 root plugdev 189, 130 Jun 24 09:28 /dev/bus/usb/002/003
```

Make sure your user is in the `plugdev` group:

```bash
sudo usermod -a -G plugdev $USER
# Log out and back in, or: newgrp plugdev
```

---

## Testing: why you need a container

Here is the annoying part. `libedgetpu1-std 16.0` (the current Coral apt package) was compiled against **TFLite ~2.5–2.13**. On Ubuntu 24.04 the only available Python is 3.12, and the Coral apt packages (`python3-pycoral`, `python3-tflite-runtime`) declare `Depends: python3 (< 3.10)`.

The `tflite-runtime` and `ai-edge-litert` packages on PyPI are versions 2.14+ — too new to be ABI-compatible with the old libedgetpu delegate interface at inference time. The delegate loads but fails with:

```
RuntimeError: Encountered an unresolved custom op.
Node number 1 (EdgeTpuDelegateForCustomOp) failed to invoke.
```

The cleanest workaround is a **Docker container running Ubuntu 20.04 (focal)**, which supports Python 3.8 and has working `python3-pycoral` packages. Pass your USB device into the container with `--device`:

```bash
# Find the USB device path first
lsusb | grep '18d1:9302'
# Bus 002 Device 003: ID 18d1:9302 Google Inc.
# → /dev/bus/usb/002/003

docker run --rm \
  --device /dev/bus/usb/002/003 \
  -v /tmp/coral_test:/coral_test \
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
    python3 /coral_test/your_test.py
  "
```

---

## A minimal classification test

Prepare test assets:

```bash
mkdir -p /tmp/coral_test && cd /tmp/coral_test

# Quantized MobileNetV2 compiled for Edge TPU
wget 'https://github.com/google-coral/test_data/raw/master/mobilenet_v2_1.0_224_quant_edgetpu.tflite'
# Same model without Edge TPU ops (CPU baseline)
wget 'https://github.com/google-coral/test_data/raw/master/mobilenet_v2_1.0_224_quant.tflite'
# ImageNet labels
wget 'https://raw.githubusercontent.com/google-coral/test_data/master/imagenet_labels.txt'
# Test image (Grace Hopper portrait)
wget 'https://github.com/google-coral/test_data/raw/master/grace_hopper.bmp'
```

Save this as `/tmp/coral_test/classify.py`:

```python
import time, numpy as np
from PIL import Image
from pycoral.utils import edgetpu
import tflite_runtime.interpreter as tflite

print("Coral devices:", edgetpu.list_edge_tpus())

with open("imagenet_labels.txt") as f:
    labels = [l.strip() for l in f]

img = Image.open("grace_hopper.bmp").resize((224, 224))
x = np.expand_dims(np.array(img, dtype=np.uint8), 0)

# CPU run
cpu = tflite.Interpreter(model_path="mobilenet_v2_1.0_224_quant.tflite")
cpu.allocate_tensors()
cpu.set_tensor(cpu.get_input_details()[0]["index"], x)
cpu.invoke()  # warm up
t0 = time.perf_counter()
for _ in range(50): cpu.invoke()
cpu_ms = (time.perf_counter() - t0) / 50 * 1000
cpu_out = cpu.get_tensor(cpu.get_output_details()[0]["index"])[0]

# Edge TPU run
delegate = tflite.load_delegate("libedgetpu.so.1")
tpu = tflite.Interpreter(
    model_path="mobilenet_v2_1.0_224_quant_edgetpu.tflite",
    experimental_delegates=[delegate]
)
tpu.allocate_tensors()
tpu.set_tensor(tpu.get_input_details()[0]["index"], x)
tpu.invoke()  # warm up — loads firmware + model onto TPU
t0 = time.perf_counter()
for _ in range(50): tpu.invoke()
tpu_ms = (time.perf_counter() - t0) / 50 * 1000
tpu_out = tpu.get_tensor(tpu.get_output_details()[0]["index"])[0]

top = lambda o: [(labels[i], int(o[i])) for i in np.argsort(o)[-3:][::-1]]
print(f"\nCPU  {cpu_ms:.1f} ms — {top(cpu_out)}")
print(f"TPU  {tpu_ms:.1f} ms — {top(tpu_out)}")
print(f"\nSpeedup: {cpu_ms/tpu_ms:.1f}×")
```

Run it inside the container:

```
Coral devices: [{'type': 'usb', 'path': '/sys/bus/usb/devices/2-6'}]

CPU  16.9 ms — [('military uniform', 234), ('suit, suit of clothes', 3), ('mortarboard', 2)]
TPU   4.2 ms — [('military uniform', 233), ('suit, suit of clothes', 3), ('mortarboard', 2)]

Speedup: 4.0×
```

The top-1 prediction (`military uniform`) is correct — Grace Hopper was a U.S. Navy admiral.

---

## Checklist summary

| Step | Command / check |
|---|---|
| Patch gasket source | 4 `sed` / `python3` edits to `/usr/src/gasket-1.0/` |
| Rebuild DKMS | `sudo dkms remove gasket/1.0 --all && sudo dkms add gasket/1.0 && sudo dpkg --configure gasket-dkms` |
| Verify package state | `dpkg -l gasket-dkms` shows `ii` |
| Reload udev | `sudo udevadm control --reload-rules && sudo udevadm trigger --subsystem-match=usb` |
| Verify device | `lsusb | grep 18d1:9302` |
| Check permissions | `/dev/bus/usb/00X/00Y` shows `root:plugdev` |
| Add user to group | `sudo usermod -a -G plugdev $USER` |
| Run inference test | Docker container with `--device /dev/bus/usb/00X/00Y` + `python3-pycoral` |

---

## FAQ

**Does this affect the PCIe / M.2 Coral too?**  
Yes. The `gasket` and `apex` kernel modules are used by both the USB and PCIe/M.2 variants. The USB Coral does *not* need the `apex` driver for normal use (it talks over USB), but `gasket-dkms` still needs to build cleanly or `dpkg` stays broken.

**Will future kernel upgrades break it again?**  
Only the `MODULE_IMPORT_NS` patch is kernel-version-sensitive and we handled it with a `#if LINUX_VERSION_CODE` guard. The other three changes (`eventfd_signal`, `noop_llseek`, `class_create`) are already the current API in 6.8+ — they will not regress. The version guard covers kernels < 6.13 and ≥ 6.13 simultaneously, so new kernel header packages will just work.

**Can I avoid Docker entirely?**  
If you install Python 3.10 (e.g. via the deadsnakes PPA) and create a virtualenv, `tflite-runtime 2.14` installs cleanly — but the ABI mismatch with `libedgetpu.so.1 16.0` causes `EdgeTpuDelegateForCustomOp` to fail at invoke time. Until Google releases a new `libedgetpu` built against a recent TFLite, Docker with Ubuntu 20.04 (Python 3.8 + `python3-pycoral 2.0.0`) is the most reliable path. Alternatively, compile `libedgetpu` from source against TFLite 2.14 — a significant undertaking.

**What is `libedgetpu1-max`?**  
`libedgetpu1-max` runs the Edge TPU ASIC at a higher clock speed for ~35% more throughput but produces more heat (the dongle gets warm). `libedgetpu1-std` is the conservative clocked version. They are mutually exclusive — install one or the other. Both are at version 16.0 in the Coral apt repo.

**The `gasket-dkms` package still shows errors after patching — what now?**  
Check whether kernel headers for all installed kernels are present: `ls /lib/modules/`. For kernels without matching headers, DKMS cannot build. Either install the headers (`sudo apt install linux-headers-$(uname -r)`) or remove the old kernel entirely (`sudo apt autoremove --purge linux-image-X.Y.Z-generic`).
