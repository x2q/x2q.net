+++
title = "Local speech-to-text with whisper.cpp — a self-hosted Google Speech API alternative (2026)"
date = 2026-06-04
slug = "local-speech-to-text-whisper-cpp"
description = "Transcribe audio locally with whisper.cpp — no API keys, no per-minute billing, no audio leaving your machine. Build it, grab a model, convert audio with ffmpeg, and transcribe."

[taxonomies]
tags = ["whisper", "speech-to-text", "ai", "local-ai", "ffmpeg", "macos", "linux"]

[extra]
summary = "Years ago I ran transcription through the Google Speech API. In 2026 you don't need a cloud API for that — whisper.cpp runs OpenAI's Whisper models locally on a laptop, CPU or GPU, with no keys and nothing leaving the machine. Here's the full path from clone to transcript."
+++

**TL;DR —** `whisper.cpp` runs OpenAI's Whisper speech-to-text models locally. Build it, download a model, convert your audio to 16 kHz mono WAV with `ffmpeg`, and run `whisper-cli -m models/ggml-base.en.bin -f audio.wav`. No API key, no upload, no per-minute charge.

> This blog has a history of [speech-to-text experiments](/) — the old ones leaned on the Google Speech API. The local-model story is dramatically better now: same quality tier, zero cloud dependency.

## Why local

A hosted speech API means keys, per-minute billing, and shipping (often sensitive) audio to a third party. `whisper.cpp` is a small, dependency-light C/C++ port of Whisper that runs the same models offline — on CPU, or accelerated with Metal (Mac) / CUDA (NVIDIA). For batch transcription, private recordings, or just avoiding a metered API, it's the obvious default in 2026.

## Build it

```
git clone https://github.com/ggml-org/whisper.cpp
cd whisper.cpp
cmake -B build
cmake --build build -j --config Release
```

The CLI lands at `build/bin/whisper-cli`. (Older checkouts called this binary `./main` — if a guide references `main`, it's the same tool under the previous name.)

On a Mac, Metal acceleration is on by default. For an NVIDIA GPU, configure with CUDA:

```
cmake -B build -DGGML_CUDA=1
cmake --build build -j --config Release
```

## Get a model

Models are GGML/GGUF files you download once. The helper script fetches them into `models/`:

```
sh ./models/download-ggml-model.sh base.en
```

Pick the size for your accuracy/speed trade-off:

- **`tiny.en` / `base.en`** — fast, fine for clean English; great on a laptop CPU.
- **`small.en`** — a noticeable accuracy step up, still quick.
- **`medium`** — strong, multilingual.
- **`large-v3`** — best quality, wants a GPU and a few GB of RAM.

Drop the `.en` suffix for the multilingual variants. Quantized builds (e.g. `base.en-q5_0`) cut memory with minimal quality loss.

## Convert your audio

Whisper expects **16 kHz mono PCM WAV**. Convert anything to that with `ffmpeg`:

```
ffmpeg -i recording.mp3 -ar 16000 -ac 1 -c:a pcm_s16le recording.wav
```

- `-ar 16000` — 16 kHz sample rate
- `-ac 1` — mono
- `-c:a pcm_s16le` — 16-bit PCM

## Transcribe

```
./build/bin/whisper-cli -m models/ggml-base.en.bin -f recording.wav
```

It prints the transcript with timestamps. Write it to files instead:

```
./build/bin/whisper-cli -m models/ggml-base.en.bin -f recording.wav \
  -otxt -osrt -ovtt -oj
```

- `-otxt` plain text · `-osrt` SRT subtitles · `-ovtt` WebVTT · `-oj` JSON (with word timing).

For non-English audio, use a multilingual model and set the language (or let it auto-detect):

```
./build/bin/whisper-cli -m models/ggml-medium.bin -l da -f optagelse.wav
# -l auto  to detect automatically; add --translate to render English
```

## Speed notes

- `tiny`/`base` transcribe faster than real time on a modern laptop CPU. `large-v3` wants a GPU to be comfortable.
- Long file? Whisper chunks internally, but you can pre-split with `ffmpeg -f segment` for parallelism across cores.
- `--threads N` tunes CPU usage; Metal/CUDA builds offload the heavy matmuls automatically.

## FAQ

### Is this the same model as OpenAI's Whisper?

Yes — `whisper.cpp` runs the released Whisper weights (converted to GGML/GGUF). The output quality matches the corresponding model size; only the runtime differs.

### Do I need a GPU?

No. `tiny`/`base`/`small` are perfectly usable on CPU. A GPU mainly helps with `medium`/`large` and long batches.

### How accurate is it versus a cloud speech API?

For clean audio, `small.en` and up is competitive with the major hosted APIs, and `large-v3` generally beats them — with the bonus that nothing leaves your machine.

### Can it do live/streaming transcription?

There's a `stream` example in the repo that does near-real-time from a microphone. It's rougher than batch mode but works for live captions.

## Summary

- Build `whisper.cpp`, download a model with `download-ggml-model.sh`.
- Convert audio to 16 kHz mono WAV with `ffmpeg`.
- `whisper-cli -m models/ggml-base.en.bin -f audio.wav` — local, key-free transcription.
- Scale the model size to your hardware; use `-l`/`--translate` for other languages.
