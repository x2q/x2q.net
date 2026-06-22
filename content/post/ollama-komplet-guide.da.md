+++
title = "Ollama — komplet guide til lokal AI (2026)"
date = 2026-06-22
slug = "ollama-komplet-guide"
description = "Kom i gang med Ollama fra nul: installation på Mac og Linux, model-valg, CLI-kommandoer, REST API, Python-integration, Modelfile og performance-tips. Kør LLM'er lokalt — ingen API-nøgle, ingen cloud, ingen abonnement."

[taxonomies]
tags = ["ollama", "lokal-ai", "llm", "guide", "linux", "apple-silicon", "python"]

[extra]
summary = "Ollama lader dig køre store sprogmodeller lokalt med én kommando. Guiden dækker installation på Mac og Linux, hvilken model du skal vælge (med størrelsestabel), CLI-cheat-sheet, REST API med curl og Python, tilpasning med Modelfile og system-prompts, samt performance-tricks der halverer VRAM-forbruget."
faq = [
  { q = "Hvad er Ollama?", a = "Ollama er et open source-program der gør det nemt at køre store sprogmodeller (LLM) lokalt på din egen maskine. Det pakker model-download, kvantisering og en HTTP-API ind i én simpel kommando. Ingen cloud, ingen API-nøgle, ingen abonnement — modellen kører på din GPU (eller CPU)." },
  { q = "Hvilken GPU kræver Ollama?", a = "Ingen — Ollama kører på CPU, Apple Silicon (MPS) og NVIDIA GPU (CUDA). På CPU er det langsomt (2–5 tok/s for en 7B-model), men brugbart for korte opgaver. Med en GPU der har mindst 8 GB VRAM (eller 8 GB unified memory på M1/M2/M3) kører de populære 7B-modeller flydende ved 30–80 tok/s." },
  { q = "Er Ollama sikkert?", a = "Ja — som standard lytter Ollama kun på localhost (127.0.0.1:11434), så ingen udefra kan ramme API'et. Hvis du åbner det på netværket (OLLAMA_HOST=0.0.0.0), bør du enten bruge en reverse proxy med auth eller begrænse adgang via firewall. Modellerne og dine prompts forlader aldrig din maskine." },
  { q = "Hvilken model skal jeg starte med?", a = "Til de fleste starter llama3.2:3b (2 GB) er et godt valg — den kører hurtigt selv på ældre hardware og er overraskende kompetent. Har du 8+ GB VRAM eller unified memory, er qwen3.5 (6.6 GB, 9.7B parametre) markant bedre og håndterer lange kontekster op til 262.000 tokens." },
  { q = "Kan Ollama bruges som ChatGPT-erstatning?", a = "For mange hverdagsopgaver — opsummering, kode-hjælp, tekstgenerering — ja. De bedste 7–12B-modeller i 2026 er meget tæt på GPT-4o på almindelige opgaver. Fordelen: det koster ingenting at køre, og dine data forlader ikke maskinen. Ulempen: de er langsommere og fejler mere på komplekse flertrin-ræsonneringsopgaver." }
]
+++

**Ollama** lader dig køre store sprogmodeller lokalt med én kommando: `ollama run llama3.2`. Ingen API-nøgle, ingen abonnement, ingen data der forlader din maskine. Denne guide tager dig fra installation til færdig opsætning — inkl. REST API, Python og performance-tricks.

## Installation

### Mac

```bash
brew install ollama
```

Start serveren:

```bash
ollama serve
```

Eller som baggrundstjeneste der starter automatisk ved login:

```bash
brew services start ollama
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Installationen sætter Ollama op som en `systemd`-service der starter automatisk. Tjek status med:

```bash
systemctl status ollama
```

### Windows

Download installationsfilen fra [ollama.com](https://ollama.com) — den sætter sig op som en bakke-app og starter automatisk ved login.

---

## Første model

Pull og kør en model med én kommando:

```bash
ollama run llama3.2:3b
```

Ollama downloader modellen første gang (~2 GB), cacher den i `~/.ollama/models/`, og åbner en interaktiv chat. `/bye` afslutter.

For at downloade uden at åbne chat:

```bash
ollama pull qwen3.5
```

---

## Hvilken model skal du vælge?

| Model | Størrelse | RAM/VRAM | Hvad den er god til |
|-------|:---:|:---:|---|
| `llama3.2:1b` | 1.3 GB | 2 GB | Hurtigste option — god til klassificering, korte svar |
| `llama3.2:3b` | 2.0 GB | 3 GB | **Bedste startpunkt** — kompetent, kører overalt |
| `llama3.1:8b` | 4.9 GB | 6 GB | Solid alsidig model, god til kode og tekst |
| `qwen3.5` | 6.6 GB | 8 GB | **Anbefalet** — 9.7B, 262k kontekst, stærk på dansk |
| `gemma4:12b` | 7.6 GB | 9 GB | Googles model — meget god til instruktioner |
| `phi4:14b` | 9.1 GB | 11 GB | Microsofts kompakte model, god til ræsonnering |
| `llama3.1:70b` | 43 GB | 48 GB | Kraftfuld — kræver server med meget VRAM/RAM |
| `minicpm-v4.6` | 1.6 GB | 2 GB | Multimodal — kan se billeder |

**Tommelfingerregel:** vælg den største model der passer i din GPU's VRAM. Modellen skal *helst* ligge helt i VRAM — flyder den over til RAM, falder hastigheden dramatisk.

Søg og find alle tilgængelige modeller:

```bash
ollama search llama
```

---

## CLI cheat sheet

```bash
# Kør interaktiv chat
ollama run qwen3.5

# Kør med system-prompt fra kommandolinjen
ollama run llama3.2:3b "Forklar TCP/IP i tre sætninger"

# Pipe input ind
cat artikel.txt | ollama run qwen3.5 "Opsummer dette"

# List downloadede modeller
ollama list

# Vis modeldetaljer (parametre, kvantisering, kontekstlængde)
ollama show qwen3.5

# Slet en model
ollama rm llama3.2:1b

# Kopiér og omdøb en model
ollama cp qwen3.5 mit-projekt

# Vis kørende modeller og VRAM-brug
ollama ps
```

---

## REST API

Ollama eksponerer en HTTP-API på `localhost:11434`. Du kan bruge den direkte fra terminalen eller fra ethvert programmeringssprog.

### Generér tekst

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5",
  "prompt": "Hvad er forskellen mellem TCP og UDP?",
  "stream": false
}'
```

Vigtige felter i svaret:

```json
{
  "response": "TCP er forbindelsesorienteret...",
  "eval_count": 142,
  "eval_duration": 1923000000,
  "prompt_eval_duration": 215000000
}
```

`eval_count / (eval_duration / 1e9)` giver tokens per sekund.

### Chat (med historik)

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "qwen3.5",
  "messages": [
    {"role": "system", "content": "Du er en hjælpsom dansk assistent."},
    {"role": "user", "content": "Hvad er hovedstaden i Danmark?"}
  ],
  "stream": false
}'
```

### Streaming

Sæt `"stream": true` (standard) for at få tokens løbende:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3.5",
  "prompt": "Skriv et digt om terminal-programmering",
  "stream": true
}' | while IFS= read -r line; do
  echo "$line" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('response',''), end='', flush=True)"
done
```

### Liste over downloadede modeller

```bash
curl http://localhost:11434/api/tags
```

### Nyttige options

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

| Option | Standard | Hvad det gør |
|--------|:---:|---|
| `temperature` | 0.8 | Kreativitet: 0 = deterministisk, 1+ = mere tilfældig |
| `num_predict` | -1 (ubegrænset) | Max tokens at generere |
| `num_ctx` | modelens standard | Kontekstvindue (tokens) |
| `seed` | tilfældig | Fast seed → reproducerbare svar |
| `top_p` | 0.9 | Nucleus sampling |

---

## Python

Ollama's API er simpel nok til at bruge med `urllib` — ingen ekstra pakker nødvendigt:

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

# Brug
svar = ollama("Forklar forskellen mellem list og tuple i Python")
print(svar)
```

Foretrækker du en dedikeret pakke:

```bash
pip install ollama
```

```python
import ollama

svar = ollama.chat(
    model="qwen3.5",
    messages=[{"role": "user", "content": "Hvad er Rust?"}]
)
print(svar["message"]["content"])
```

---

## Modelfile — tilpas en model

En `Modelfile` lader dig oprette en ny model baseret på en eksisterende — med fast system-prompt, temperatur og parametre.

Opret filen `Modelfile`:

```dockerfile
FROM qwen3.5

SYSTEM """
Du er en præcis dansk teknisk assistent. Svar altid på dansk.
Vær kortfattet. Vis kodeeksempler når relevant.
"""

PARAMETER temperature 0.3
PARAMETER num_ctx 16384
```

Byg og brug den:

```bash
ollama create dansk-assistent -f Modelfile
ollama run dansk-assistent "Hvad er en hash-tabel?"
```

List dine brugerdefinerede modeller:

```bash
ollama list
```

Du kan dele Modelfiles med kolleger — de puller bare base-modellen og kører `ollama create`.

---

## Performance-tips

### Flash Attention (anbefalet)

Reducerer VRAM-brug og øger hastighed på lange kontekster:

```bash
OLLAMA_FLASH_ATTENTION=1 ollama serve
```

På Mac via Homebrew, tilføj til `~/.zshrc`:

```bash
export OLLAMA_FLASH_ATTENTION=1
```

### KV-cache kvantisering

Halverer næsten VRAM-forbruget til kontekst-cachen, med minimal kvalitetstab:

```bash
OLLAMA_KV_CACHE_TYPE=q8_0 ollama serve   # halvt VRAM, ingen synlig forskel
OLLAMA_KV_CACHE_TYPE=q4_0 ollama serve   # endnu mindre, let kvalitetstab
```

### Parallelle requests

Ollama håndterer som standard én request ad gangen. Til serverbrug:

```bash
OLLAMA_NUM_PARALLEL=4 ollama serve         # 4 samtidige requests
OLLAMA_MAX_LOADED_MODELS=2 ollama serve    # hold 2 modeller i VRAM
```

### Se hvad der kører

```bash
ollama ps
# NAME          ID      SIZE    PROCESSOR    UNTIL
# qwen3.5:latest  ...   7.9 GB  100% GPU     4 minutes from now
```

Modeller unloades automatisk efter 5 minutters inaktivitet. Skift timeout:

```bash
OLLAMA_KEEP_ALIVE=30m ollama serve   # hold indlæst i 30 min
OLLAMA_KEEP_ALIVE=-1 ollama serve    # hold indlæst for evigt
```

---

## Som server på netværket

Som standard lytter Ollama kun på localhost. Åbn for netværksadgang:

```bash
OLLAMA_HOST=0.0.0.0:11434 ollama serve
```

**Brug Tailscale** til at eksponere din GPU-server sikkert på dit private netværk uden at åbne for internet:

```bash
# På serveren med RTX 4070 Ti:
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# Fra din Mac via Tailscale:
OLLAMA_HOST=gpu-box:11434 ollama run qwen3.5
# eller direkte via API:
curl http://gpu-box:11434/api/generate -d '{"model":"gemma4:12b","prompt":"..."}'
```

På Linux med systemd, tilføj env vars i service-filen:

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

## OpenAI-kompatibelt API

Ollama understøtter OpenAI's API-format, så eksisterende kode der bruger `openai`-pakken kører uden ændringer:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # kræves af klienten, ignoreres af Ollama
)

response = client.chat.completions.create(
    model="qwen3.5",
    messages=[{"role": "user", "content": "Hvad er en linked list?"}]
)
print(response.choices[0].message.content)
```

---

## Hvad koster det at køre?

Ingenting — bortset fra strøm. En 7B-model på en RTX 4070 Ti (200W under load) koster ca.:

| Brug | Strøm | Pris (3 kr/kWh) |
|------|:---:|:---:|
| 1 times chat (~50 req) | ~0,1 kWh | ~0,30 kr |
| 1 dags batch-transskription | ~0,5 kWh | ~1,50 kr |
| GPT-4o via API (samme mængde) | — | ~50–200 kr |

På M1 Pro (25W) er strømomkostningen nærmest symbolsk.

---

## Nyttige links

- [ollama.com/library](https://ollama.com/library) — alle tilgængelige modeller
- [github.com/ollama/ollama](https://github.com/ollama/ollama) — kildekode og issues
- API-reference: `http://localhost:11434` når Ollama kører

> Se også [M1 Pro vs RTX 4070 Ti — GPU og LLM benchmarks](/da/post/m1-vs-rtx4070ti-ai-benchmark-2026/) for konkrete tal på, hvad de to platforme leverer.
