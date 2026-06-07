+++
title = "Extending video clips with AI on a 12 GB GPU — six models compared"
date = 2026-06-07
slug = "video-extension-models-12gb-gpu"
description = "Wan2.2 (5B and 14B), Stable Video Diffusion, LTX-Video and CogVideoX — six image-to-video models for extending a short clip, run locally on a 12 GB RTX 4070 Ti. The real fight is the offload strategy that lets a 14B model — and 720p — fit in 12 GB."

[taxonomies]
tags = ["ai", "video", "image-to-video", "wan", "ltx-video", "cogvideox", "stable-video-diffusion", "diffusers", "gguf", "offloading", "nvidia"]

[extra]
summary = "You have a short machine/action clip and want it longer. 'Extending' a clip is really image-to-video: take the last frame and generate a plausible continuation. I fed the same shot to six models — Wan2.2-TI2V-5B, Wan2.2-I2V-A14B (GGUF), Stable Video Diffusion, LTX-Video and CogVideoX-5B — all on a single 12 GB RTX 4070 Ti. The interesting part isn't which looks best; it's the memory-offload tricks that make a 14B video model (and 720p) fit in 12 GB at all."
faq = [
  { q = "Can you really run a 14B video model on a 12 GB GPU?", a = "Yes — quantized to GGUF Q4 (~9 GB per expert) and with the right offloading. The official fp16 Wan2.2-14B wants ~24-35 GB and won't fit. The trick is to never keep the whole model resident: model-level CPU offload gets you 640-720p at short lengths, and group-offload (streaming the transformer block-by-block) drops the peak to under 2 GB so resolution becomes free and time becomes the limit." },
  { q = "Which model should I actually use on 12 GB?", a = "For short extensions, LTX-Video — it's the best speed/quality balance (~3 min, dynamic motion, prompt-guided). For genuine 720p, Wan2.2-I2V-14B with group-leaf offload (slow, ~20 min, but sharp). SVD is fastest but its motion is ambient (no prompt control). CogVideoX-5B gives the longest, smoothest clip but takes ~an hour per clip here." },
  { q = "Why did everything keep running out of memory?", a = "Two repeat offenders. First, the T5/umT5 text encoder is ~11 GB on its own and OOMs a 12 GB card the moment model-offload moves it to the GPU — fix by pre-encoding the prompt on CPU (in fp32; bf16-on-CPU is unusably slow) and evicting the encoder. Second, at higher resolutions the activation memory, not the weights, is what blows up — fewer frames or group-offload fixes that." },
  { q = "Does GGUF work with diffusers offloading?", a = "GGUF + model-level CPU offload: yes. GGUF + sequential offload: no — accelerate moves params via a meta device and the GGUF quant type gets dropped (KeyError). GGUF + group-offload: yes, and it's how you reach 720p. Plain (non-GGUF) models like LTX are happy with sequential offload." },
  { q = "Why does the AI continuation still look a bit fake?", a = "On 12 GB the binding constraint is resolution. The 5B at 640 px looks softest; the 14B at 720p is markedly sharper. The remaining gap — high resolution AND multi-second length together — is the one thing a 12 GB card can't give you; that needs a 24 GB+ GPU or cloud." },
  { q = "Do I need ComfyUI?", a = "No. Everything here runs through Hugging Face diffusers in a Python script, including the GGUF Wan experts via from_single_file. ComfyUI is fine too, but diffusers is far easier to drive headlessly and to batch." },
]
+++

**TL;DR —** "Extending" a video clip is really **image-to-video**: grab the last frame and let a model generate a believable continuation, then concatenate. I ran the same machine shot through **six** I2V models on one **12 GB RTX 4070 Ti**: Wan2.2-TI2V-5B, Wan2.2-I2V-A14B (GGUF Q4, at 640 px and at 720p), Stable Video Diffusion, LTX-Video and CogVideoX-5B. The headline isn't the winner — it's that a **14B** model and **720p** both fit in 12 GB once you get the **offload strategy** right.

## The task

I had a stack of short clips of forestry machines — an excavator digging, a wood chipper, a wheel loader — and wanted them a couple of seconds longer. There's no more footage; the only way to extend is to *invent* it. Modern image-to-video models do exactly this: condition on a starting image (here, the clip's final frame) and a text prompt, and hallucinate motion forward. Stitch the real tail to the generated continuation and you have a longer clip.

Everything below ran locally on a single 12 GB RTX 4070 Ti with 125 GB of system RAM (the RAM matters — it's where the offloaded weights live).

## The real problem: fitting big video models in 12 GB

Image diffusion is forgiving on VRAM. Video diffusion is not: you're denoising a 3D latent (frames × height × width), and the newest quality models are 5B-14B parameters. Three things kept biting:

1. **The text encoder is huge.** Wan and LTX and CogVideoX all use a T5-XXL / umT5-XXL encoder that's ~11 GB on its own. The instant model-level offload moves it onto a 12 GB card to encode the prompt, you OOM — before the video model even runs.
2. **Activations, not weights, blow up at higher resolution.** A 9 GB transformer can sit on the card fine; it's the attention activations over (frames × tokens) that overflow when you push past ~480p.
3. **Quantization helps disk and a bit of VRAM, but interacts badly with some offload modes.** GGUF Q4 shrinks a 14B expert to ~9 GB, but the way you offload it matters (see below).

The fixes that made it all work:

- **Pre-encode the prompt on CPU, then evict the encoder.** Compute the text embeddings with the T5 on the CPU *in fp32* (bf16 matmuls on CPU are pathologically slow — it looks hung), cast the result to bf16, set `text_encoder = None`, and only then start the video model. Now the 11 GB encoder never touches the GPU.
- **Pick the offload mode per model:**
  - `enable_model_cpu_offload()` — moves whole sub-models on/off the GPU. Fast, but one model must fit at a time (so it caps resolution/length).
  - `enable_sequential_cpu_offload()` — streams sub-modules. Lower peak VRAM, slower. Great for non-quantized models (LTX, CogVideoX), but **breaks GGUF** (accelerate's meta-device step drops the quant type).
  - `apply_group_offloading(..., offload_type="leaf_level", use_stream=True)` — streams the transformer leaf-by-leaf. This is the secret weapon.

## Wan2.2: from "fake" 5B to real 720p

I started with **Wan2.2-TI2V-5B** (the small, consumer-friendly one). It runs easily with model-offload and produces coherent motion, but at the ~640 px the card allows it looks soft — the classic "AI video" plasticky feel.

Stepping up to **Wan2.2-I2V-A14B** meant quantization. The official 14B is two experts (high-noise + low-noise) and wants 24-35 GB in fp16. The GGUF Q4 build is ~9 GB per expert, and diffusers can load each through `WanTransformer3DModel.from_single_file(..., quantization_config=GGUFQuantizationConfig(...))` — you just need the `gguf` package, or it fails to read the file. With model-offload + the CPU-prompt trick, the 14B runs at 640 px and the motion is visibly better (the wood chipper, a chaotic close-up that the 5B turned to mush, came out coherent).

Then the actual goal: **720p**. Model-offload at 1280×720 peaks at ~11.7 GB — it fits, but only ~13 frames before the activations overflow. The breakthrough was **group-leaf offloading**: stream the transformer one leaf module at a time, so almost nothing sits on the GPU. Peak VRAM at 1280×720: **1.9 GB**. The card is suddenly empty and resolution is free; the cost is speed (leaf streaming is slow, ~20 min a clip). But it's real, sharp 720p on a 12 GB card.

```python
from diffusers.hooks import apply_group_offloading
for t in (pipe.transformer, pipe.transformer_2):  # both noise experts
    apply_group_offloading(t, onload_device=torch.device("cuda"),
                           offload_device=torch.device("cpu"),
                           offload_type="leaf_level", use_stream=True)
pipe.vae.enable_tiling()
```

## The other three

- **LTX-Video** (2B). Fast and, for short extensions, the best of the lot — dynamic motion (the excavator throws dirt), prompt-guided, ~3 min a clip at 768×512. Needs `sentencepiece` for its T5 tokenizer, and `sequential` offload because that T5 is the same 11 GB OOM trap.
- **Stable Video Diffusion** (img2vid-xt). The veteran. Runs at 1024×576 with model-offload + `unet.enable_forward_chunking()`, and it's quick — but SVD has **no text prompt**, so its motion is *ambient* (a gentle drift, a breeze in the trees) rather than the directed action you asked for. Great for cinematic cutaways, wrong tool for "keep digging."
- **CogVideoX-5B-I2V**. The quality surprise: the longest and smoothest clip (6 s, 49 frames at 720×480), coherent throughout. The catch is speed — with sequential offload + VAE tiling it's roughly **an hour per clip** on 12 GB, which makes it impractical here even though the output is lovely.

## The scoreboard

| Model | Params | Fits 12 GB via | Output | Speed | Verdict |
|---|---|---|---|---|---|
| LTX-Video | 2B | sequential offload | 768×512 | ~3 min | **Best for short extensions** — fast, dynamic |
| Wan2.2-I2V-14B @ 720p | 14B (Q4) | **group-leaf offload (1.9 GB!)** | 1280×720 | ~20 min | **Real 720p on 12 GB** — sharpest |
| Wan2.2-I2V-14B | 14B (Q4) | model offload + CPU prompt | 640×384 | ~8 min | Good motion, esp. the hard cases |
| CogVideoX-5B-I2V | 5B | sequential + VAE tiling | 720×480 | ~1 hr | Longest/smoothest, but impractically slow here |
| Stable Video Diffusion | ~1.5B | model offload + chunking | 1024×576 | ~2 min | Fast & clean, but motion is ambient |
| Wan2.2-TI2V-5B | 5B | model offload | 640×384 | ~3 min | The soft, "fake"-looking baseline |

## What I'd actually do

On a 12 GB card: reach for **LTX-Video** for quick, directed extensions, and **Wan2.2-14B + group-offload** when you specifically need **720p** and can wait. SVD stays in the kit for ambient cutaways. CogVideoX is gorgeous but you'd want a bigger GPU to use it for real.

And the honest limitation: the thing that still reads as "AI" is mostly **resolution**. Group-offload buys you 720p *or* a 12 GB card buys you length — not both at once. High-res *and* multi-second is the one wall a 12 GB GPU won't climb; that's what a 24 GB+ card (or an hour of cloud) is for. Everything else — even a 14B model at 720p — turned out to be a question of offloading, not horsepower.
