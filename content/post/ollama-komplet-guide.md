+++
title = "Ollama complete guide — run LLMs locally (2026)"
date = 2026-06-22
slug = "ollama-komplet-guide"
description = "Everything you need to run large language models locally with Ollama: installation on Mac and Linux, model selection, CLI commands, REST API, Python integration, Modelfile customisation, and performance tips. No API key, no cloud, no subscription."

[taxonomies]
tags = ["ollama", "local-ai", "llm", "guide", "linux", "apple-silicon", "python"]

[extra]
summary = "Ollama lets you run large language models locally with a single command. This guide covers installation on Mac and Linux, how to pick the right model (with a size table), a CLI cheat sheet, the REST API with curl and Python, customisation with Modelfile and system prompts, and performance tricks that halve VRAM usage."
faq = [
  { q = "What is Ollama?", a = "Ollama is an open-source tool that makes it easy to run large language models (LLMs) locally on your own machine. It wraps model download, quantisation, and an HTTP API into one simple command. No cloud, no API key, no subscription — the model runs on your GPU (or CPU)." },
  { q = "What GPU does Ollama require?", a = "None — Ollama runs on CPU, Apple Silicon (MPS), and NVIDIA GPU (CUDA). On CPU it's slow (2–5 tok/s for a 7B model), but usable for short tasks. With a GPU that has at least 8 GB VRAM (or 8 GB unified memory on M1/M2/M3), the popular 7B models run smoothly at 30–80 tok/s." },
  { q = "Is Ollama safe?", a = "Yes — by default Ollama only listens on localhost (127.0.0.1:11434), so no one outside can reach the API. If you expose it on the network (OLLAMA_HOST=0.0.0.0), you should either put a reverse proxy with auth in front of it or restrict access via firewall. Your models and prompts never leave your machine." },
  { q = "Which model should I start with?", a = "For most people, llama3.2:3b (2 GB) is a good starting point — it runs fast even on older hardware and is surprisingly capable. If you have 8+ GB VRAM or unified memory, qwen3.5 (6.6 GB, 9.7B parameters) is significantly better and handles contexts up to 262,000 tokens." },
  { q = "Can Ollama replace ChatGPT?", a = "For many everyday tasks — summarisation, code help, text generation — yes. The best 7–12B models in 2026 are very close to GPT-4o on common tasks. The upside: it costs nothing to run and your data stays on your machine. The downside: they're slower and make more mistakes on complex multi-step reasoning tasks." }
]
+++

**Ollama** lets you run large language models locally with a single command: `ollama run llama3.2`. No API key, no subscription, no data leaving your machine. This guide takes you from installation to a complete setup — including REST API, Python, and performance tricks.

## Installation

### Mac

```bash
brew install ollama
```

Start the server:

```bash
ollama serve
```

Or as a background service that starts at login:

```bash
brew services start ollama
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

The installer sets up Ollama as a `systemd` service that starts automatically. Check status with:

```bash
systemctl status ollama
```

### Windows

Download the installer from [ollama.com](https://ollama.com) — it sets up as a tray app and starts automatically at login.

---

## Your first model

Pull and run a model with one command:

```bash
ollama run llama3.2:3b
```

Ollama downloads the model on first run (~2 GB), caches it in `~/.ollama/models/`, and opens an interactive chat. `/bye` exits.

To download without opening a chat:

```bash
ollama pull qwen3.5
```

---

## Which model should you choose?

| Model | Size | RAM/VRAM | Best for |
|-------|:---:|:---:|---|
| `llama3.2:1b` | 1.3 GB | 2 GB | Fastest option — good for classification, short answers |
| `llama3.2:3b` | 2.0 GB | 3 GB | **Best starting point** — capable, runs anywhere |
| `llama3.1:8b` | 4.9 GB | 6 GB | Solid general-purpose model, good for code and text |
| `qwen3.5` | 6.6 GB | 8 GB | **Recommended** — 9.7B, 262k context window |
| `gemma4:12b` | 7.6 GB | 9 GB | Google's model — excellent at following instructions |
| `phi4:14b` | 9.1 GB | 11 GB | Microsoft's compact model, strong at reasoning |
| `llama3.1:70b` | 43 GB | 48 GB | Powerful — requires a server with lots of VRAM/RAM |
| `minicpm-v4.6` | 1.6 GB | 2 GB | Multimodal — can analyse images |

**Rule of thumb:** pick the largest model that fits in your GPU's VRAM. The model should ideally sit entirely in VRAM — if it overflows to RAM, speed drops dramatically.

Search available models:

```bash
ollama search llama
```

---

## CLI cheat sheet

```bash
# Interactive chat
ollama run qwen3.5

# One-shot prompt
ollama run llama3.2:3b "Explain TCP/IP in three sentences"

# Pipe input
cat article.txt | ollama run qwen3.5 "Summarise this"

# List downloaded models
ollama list

# Show model details (parameters, quantisation, context length)
ollama show qwen3.5

# Delete a model
ollama rm llama3.2:1b

# Copy and rename a model
ollama cp qwen3.5 my-project

# Show running models and VRAM usage
ollama ps
```

---

## REST API

Ollama exposes an HTTP API on `localhost:11434`. Use it directly from the terminal or from any programming language.

### Generate text

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5",
  "prompt": "What is the difference between TCP and UDP?",
  "stream": false
}'
```

Key fields in the response:

```json
{
  "response": "TCP is connection-oriented...",
  "eval_count": 142,
  "eval_duration": 1923000000,
  "prompt_eval_duration": 215000000
}
```

`eval_count / (eval_duration / 1e9)` gives tokens per second.

### Chat (with history)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3.5",
  "messages": [
    {"role": "system", "content": "You are a concise technical assistant."},
    {"role": "user", "content": "What is a hash table?"}
  ],
  "stream": false
}'
```

### Streaming

Set `"stream": true` (the default) to receive tokens as they are generated:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5",
  "prompt": "Write a poem about terminal programming",
  "stream": true
}' | while IFS= read -r line; do
  echo "$line" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response',''), end='', flush=True)"
done
```

### Useful options

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5",
  "prompt": "...",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_predict": 500,
    "num_ctx": 8192,
    "top_p": 0.9,
    "seed": 42
  }
}'
```

| Option | Default | What it does |
|--------|:---:|---|
| `temperature` | 0.8 | Creativity: 0 = deterministic, 1+ = more random |
| `num_predict` | -1 (unlimited) | Max tokens to generate |
| `num_ctx` | model's default | Context window (tokens) |
| `seed` | random | Fixed seed → reproducible responses |
| `top_p` | 0.9 | Nucleus sampling |

---

## Python

Ollama's API is simple enough to use with `urllib` — no extra packages needed:

```python
import urllib.request, json

def ollama(prompt, model="qwen3.5", system=None):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0}
    }).encode()

    req = urllib.request.Request(
        "http://localhost:11434/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)["message"]["content"]

# Usage
answer = ollama("Explain the difference between list and tuple in Python")
print(answer)
```

Or with the official package:

```bash
pip install ollama
```

```python
import ollama

response = ollama.chat(
    model="qwen3.5",
    messages=[{"role": "user", "content": "What is Rust?"}]
)
print(response["message"]["content"])
```

---

## Modelfile — customise a model

A `Modelfile` lets you create a new model based on an existing one — with a fixed system prompt, temperature, and parameters.

Create the file `Modelfile`:

```dockerfile
FROM qwen3.5

SYSTEM """
You are a precise technical assistant. Be concise.
Show code examples when relevant. Prefer simple over clever.
"""

PARAMETER temperature 0.3
PARAMETER num_ctx 16384
```

Build and use it:

```bash
ollama create my-assistant -f Modelfile
ollama run my-assistant "What is a hash table?"
```

List your custom models:

```bash
ollama list
```

You can share Modelfiles with colleagues — they pull the base model and run `ollama create`.

---

## Performance tips

### Flash Attention (recommended)

Reduces VRAM usage and increases speed on long contexts:

```bash
OLLAMA_FLASH_ATTENTION=1 ollama serve
```

On Mac via Homebrew, add to `~/.zshrc`:

```bash
export OLLAMA_FLASH_ATTENTION=1
```

### KV cache quantisation

Cuts context-cache VRAM roughly in half, with minimal quality loss:

```bash
OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve   # half VRAM, no visible difference
OLLAMA_KV_CACHE_TYPE=q4_0 ollama serve   # even smaller, slight quality loss
```

### Parallel requests

Ollama handles one request at a time by default. For server use:

```bash
OLLAMA_NUM_PARALLEL=4 ollama serve         # 4 concurrent requests
OLLAMA_MAX_LOADED_MODELS=2 ollama serve    # keep 2 models in VRAM
```

### Check what's running

```bash
ollama ps
# NAME            ID      SIZE    PROCESSOR    UNTIL
# qwen3.5:latest  ...   7.9 GB  100% GPU     4 minutes from now
```

Models unload automatically after 5 minutes of inactivity. Change the timeout:

```bash
OLLAMA_KEEP_ALIVE=30m ollama serve   # keep loaded for 30 min
OLLAMA_KEEP_ALIVE=-1 ollama serve    # keep loaded forever
```

---

## Network access

By default Ollama only listens on localhost. Open it for network access:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Use Tailscale** to expose your GPU server securely on your private network without opening it to the internet:

```bash
# On the GPU server:
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# From your laptop via Tailscale:
OLLAMA_HOST=gpu-box:11434 ollama run qwen3.5
# or directly via API:
curl http://gpu-box:11434/api/generate -d '{"model":"gemma4:12b","prompt":"..."}'
```

On Linux with systemd, add env vars to the service file:

```bash
sudo systemctl edit ollama
```

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_KV_CACHE_TYPE=q8_0"
```

```bash
sudo systemctl restart ollama
```

---

## OpenAI-compatible API

Ollama supports OpenAI's API format, so existing code that uses the `openai` package works without changes:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required by the client, ignored by Ollama
)

response = client.chat.completions.create(
    model="qwen3.5",
    messages=[{"role": "user", "content": "What is a linked list?"}]
)
print(response.choices[0].message.content)
```

---

## What does it cost to run?

Nothing — except electricity. A 7B model on an RTX 4070 Ti (200W under load) costs roughly:

| Use | Power | Cost (€0.30/kWh) |
|-----|:---:|:---:|
| 1 hour of chat (~50 requests) | ~0.1 kWh | ~€0.03 |
| 1 day of batch processing | ~0.5 kWh | ~€0.15 |
| GPT-4o via API (same volume) | — | ~€5–20 |

On an M1 Pro (25W), the electricity cost is near-zero.

---

## Useful links

- [ollama.com/library](https://ollama.com/library) — all available models
- [github.com/ollama/ollama](https://github.com/ollama/ollama) — source code and issues
- API reference: `http://localhost:11434` when Ollama is running

> See also [M1 Pro vs RTX 4070 Ti — GPU and LLM benchmarks](/post/m1-vs-rtx4070ti-ai-benchmark-2026/) for concrete numbers on what the two platforms deliver.
