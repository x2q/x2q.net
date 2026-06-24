+++
title = "Fem alternativer til pyannote: speaker diarization til telefonopkald (2026)"
date = 2026-06-24
slug = "diarization-fem-alternativer"
description = "Kan noget hurtigere end pyannote-audio 3.1 klare 2-part telefondiarization? Et benchmark af fem tilgange — spectral clustering, multi-scale embeddings, PLDA, Silero VAD og cross-call gallery — på 8 rigtige opkald. Vinder: Silero VAD + WeSpeaker ved 2,1 s og 76 % agreement. Taber: alle fem på mono-kald."

[taxonomies]
tags = ["diarization", "whisper", "tale-til-tekst", "lokal-ai", "python", "asr", "dansk", "benchmark"]

[extra]
summary = "Pyannote-audio 3.1 virker, men kræver en Hugging Face-token og tager 5 sekunder pr. opkald. Benchmark af fem alternativer på 8 rigtige 2-parts telefonopkald: WeSpeaker + spectral clustering (0,2 s), multi-scale AHC (0,6 s), PLDA + spectral (0,3 s), Silero VAD + spectral (2,1 s) og cross-call gallery nearest-neighbour (0,2 s). Silero VAD-tilgangen vandt med 76,1 % agreement og er 2,4× hurtigere. Overraskelse: alle fem kollapserede på mono-kald — pyannote forbliver i produktion."
faq = [
  { q = "Hvad er speaker diarization?", a = "Speaker diarization er opgaven med at besvare 'hvem talte hvornår' i en lydfil — altså at opdele og mærke et lydsegment med taler-identiteter. I et telefonopkald med to parter handler det om at afgøre, hvilke dele af transskriptionen der tilhører den ene part og hvilke der tilhører den anden." },
  { q = "Hvorfor ikke bare bruge pyannote?", a = "Pyannote-audio 3.1 virker godt, men kræver en Hugging Face-konto med accepterede modelvilkår, tager ~5 sekunder pr. opkald, og er en stor afhængighed. Til pipelines der skal køre hurtigt eller offline er det interessant at vide, om noget enklere kan klare opgaven." },
  { q = "Hvad er agreement i dette benchmark?", a = "Agreement er andelen af Whisper-segmenter, hvor metodens speaker-label matcher pyannotes output under den bedste globale label-mapping (swap A↔B tilladt). Det måler lighed med pyannote — ikke absolut korrekthed. En metode der afviger fra pyannote kan faktisk have ret; der er ingen menneskelig ground truth." },
  { q = "Hvilken metode vandt?", a = "EXP I — Silero VAD + WeSpeaker + Spectral Clustering — med 76,1 % agreement og ~2,1 sekunders behandlingstid (mod pyannotes 5,1 s). Den bruger Sileros akustiske tale-detektionsgrænser i stedet for Whispers semantiske segmentgrænser, hvilket giver renere embeddings." },
  { q = "Hvad er problemet med mono-kald?", a = "Alle fem tilgange tvinger to klynger — de kender ikke til scenariet 'der er kun én taler'. På opkald hvor kun én part taler (korte svar, mistede forbindelser, envejsopkald) splitter de alligevel lyden i to forkerte klynger og ender på 1–35 % agreement. En simpel 1-taler-detektor (cosine-varians under en grænseværdi → tildel alle segmenter til ejeropkaldet) ville løse det." }
]
+++

Speaker diarization — at afgøre "hvem talte hvornår" — lyder simpelt og viser sig at være svært. Dette indlæg dokumenterer et weekendeksperiment med fem alternative tilgange til min nuværende produktionspipeline.

## Baggrund

Jeg optager og transskriberer alle mine erhvervsopkald automatisk. Pipelinen er groft sagt:

1. Opkald ankommer, audio gemmes som MP3
2. [Whisper](https://github.com/openai/whisper) transskriberer til ordniveausegmenter
3. Et diarization-trin tildeler hvert segment en taler
4. Alt lander i en SQLite-database med et Markdown-resumé

Trin 3 er det interessante. Jeg landede på **pyannote/speaker-diarization-3.1** som produktionsbackend efter at tidligere eksperimenter udelukkede NeMo MSDD, reference-guided ECAPA og DiarizationLM. Pyannote virker pålideligt — men den bruger 4–5 sekunder pr. opkald og kræver en Hugging Face-token med accepterede modelvilkår. Jeg ville vide, om nyere forskning har produceret noget meningsfuldt bedre.

## Benchmark

**8 rigtige opkald, 288–592 sekunder, alle 2-partssamtaler.** Jeg kører hvert alternativ mod pyannotes output og måler *segment-level agreement*: andelen af Whisper-segmenter, hvor alternativet tildeler samme speaker-label som pyannote, under den bedste permutationsmapping.

Dette måler *lighed med pyannote*, ikke absolut korrekthed. En metode der afviger fra pyannote kan faktisk have *mere* ret — der er ingen human ground truth at sammenligne med. Husk det, når du læser tallene.

Alle fem bruger pyannotes interne **WeSpeaker ResNet34-LM** embedding-model (256-dim, cosine, trænet på VoxCeleb) — samme model pyannote bruger internt, så den er allerede indlæst.

---

## Baseline — EXP E (udgik tidligt)

Inden F–J prøvede jeg at bygge taler-referencer fra pyannotes egne labels i databasen og køre WeSpeaker nearest-neighbour mod dem. Den nåede 88 % agreement — men er cirkulær: den bruger pyannotes labels som input. Ubrugelig som erstatning.

---

## EXP F — WeSpeaker + Spectral Clustering

**Idé:** SpectralClustering med normaliseret cosine-affinitet slår AgglomerativeClustering på 2-taler-opgaver (Park et al. ICASSP 2022; Landini et al. IS 2022). Den globale grafstruktur slår grådige lokale sammensætninger.

**Flow:**
1. Gruppér Whisper-segmenter i turns (< 0,5 s pause = samme turn)
2. Embed hvert turn med WeSpeaker ResNet34 (256-dim, L2-normaliseret)
3. Byg cosine-affinitetsmatrix, kør `SpectralClustering(n_clusters=2)`
4. Map klyngerne til navne via opkaldsretning

**Tid:** ~0,2 s — 25× hurtigere end pyannote.

---

## EXP G — Multi-scale WeSpeaker + AHC

**Idé:** Korte turns giver ustabile embeddings. Løs det ved at embedde hvert turn i tre vinduesstørrelser — 0,5×, 1× og 2× turn-varighed centreret om turn-midten — og middel de tre embeddings. Inspireret af NeMos MSDD-arkitektur (Kwon et al. 2022).

**Flow:** Samme som F, men brug det middelte multi-scale embedding. Clustering med AgglomerativeClustering (`cosine`, `average` linkage).

**Tid:** ~0,6 s.

---

## EXP H — WeSpeaker + PLDA + Spectral Clustering

**Idé:** PLDA (Probabilistic Linear Discriminant Analysis) modellerer within- og between-speaker-kovarians og slår konsistent cosine-distance til speaker clustering (Snyder et al. 2018; dominerende i VoxSRC 2023-vindersystemer).

`pyannote-audio`-pakken medfølger et trænet PLDA-objekt med LDA-transformationen `_xvec_tf` og egenværdierne `phi`.

**Flow:**
1. LDA-projektion: `mat_lda = plda._xvec_tf(embeddings)` — reducerer 256 → 128 dim
2. Pairwise Simplified-PLDA log-likelihood ratio:
   - `φ` = PLDA-egenværdier (`plda.phi`, 128-dim)
   - `w_same = φ / (φ + 2)` — vægt for at x og y er samme taler
   - `w_diff = 1 / (φ + 1)` — straf for at de er forskellige
   - `LLR(x, y) = Σ [ w_same·(xᵢ+yᵢ)²/2 − w_diff·(xᵢ²+yᵢ²)/2 ]`
3. Konvertér til affinitet: `A = 1 / (1 + exp(−LLR))`
4. `SpectralClustering(n_clusters=2, affinity="precomputed")`

**Tid:** ~0,3 s.

---

## EXP I — Silero VAD + WeSpeaker + Spectral Clustering

**Idé:** Whisper-segmentgrænser er semantiske, ikke akustiske — de følger meningen, ikke mundens åbning. Bedre VAD-grænser giver renere embeddings. VBx-systemet (Landini et al. Odyssey 2022) viser, at nær-oracle VAD er kritisk for embedding-kvalitet. Silero VAD (Silero Team 2021) kører på CPU og bruger ~1 ms pr. sekund audio.

**Flow:**
1. Kør Silero VAD på rå audio (`threshold=0.4`, `min_speech=250 ms`, `min_silence=300 ms`)
2. Gruppér Silero-timestamps i turns (< 0,5 s pause)
3. Embed hvert Silero-turn med WeSpeaker
4. Map Whisper-segmenter til nærmeste Silero-turn via tidsoverlap
5. `SpectralClustering(n_clusters=2)`

**Tid:** ~2,1 s (domineret af Silero på CPU).

---

## EXP J — Cross-call speaker gallery (nearest-neighbour)

**Idé:** Ingen clustering overhovedet. Byg i stedet et galleri af kendte talere fra historiske kald i databasen, og klassificér nye turns med cosine nearest-neighbour — som i speaker-recognition-litteraturen (Ding et al. ICASSP 2020; x-vector NN-baseline i VoxSRC 2021–2023).

**Flow:**
1. Hent de seneste 40 færdigbehandlede kald fra DB
2. Sample op til 8 WeSpeaker-embeddings pr. taler pr. kald → `{taler: [emb, ...]}`
3. Beregn middelembedinget pr. taler, L2-normaliser
4. For hvert nyt turn: find galleri-taleren med højeste cosine-similaritet
5. Snap til linje-ejer eller modpart baseret på opkaldsretning

**Tid:** ~0,2 s ekskl. gallery-opbygning (12 s én gang ved opstart, derefter cached).

---

## Resultater — 8 opkald

| Opkald | Varighed | Pyannote-fordeling | F SC | G MS | H PLDA | I Silero | J Gallery |
|---|---|---|:---:|:---:|:---:|:---:|:---:|
| Kald A | 308 s | 68 / 34 seg. | 66,7 % | 65,7 % | **88,2 %** | **88,2 %** | 69,6 % |
| Kald B | 288 s | **mono** (10/0) | 80,0 % | 90,0 % | 80,0 % | 90,0 % | 80,0 % |
| Kald C | 320 s | 4 / 33 seg. | 75,7 % | **86,5 %** | 78,4 % | 81,1 % | 75,7 % |
| Kald D | 314 s | **mono** (99/0) | 35,4 % | 1,0 % | 35,4 % | 61,6 % | 47,5 % |
| Kald E | 384 s | 20 / 39 seg. | 62,7 % | 64,4 % | 66,1 % | **74,6 %** | 69,5 % |
| Kald F | 393 s | **mono** (84/0) | 40,5 % | 1,2 % | 10,7 % | 48,8 % | 47,6 % |
| Kald G | 401 s | 63 / 90 seg. | 58,8 % | 59,5 % | 57,5 % | **88,9 %** | 62,1 % |
| Kald H | 592 s | 43 / 64 seg. | 71,0 % | 58,9 % | 70,1 % | **75,7 %** | 64,5 % |
| **Gennemsnit** | | | 61,3 % ±15 % | 53,4 % ±32 % | 60,8 % ±24 % | **76,1 % ±14 %** | 64,6 % ±11 % |

Pyannote-referencetid: **5,1 s** gennemsnit pr. opkald.

*Kald B, D og F er "mono" — én part dominerer næsten 100 % af segmenterne. Disse er de sværeste cases.*

---

## Tre overraskelser

### 1. EXP G kollapsede fuldstændigt på mono-kald

1,0 % og 1,2 % agreement. Det er ikke bare dårligt — det er aktivt forkert. AHC med `n_clusters=2` tvinger to klynger uanset hvad: på mono-kald ender den med én kæmpe klynge og én med nærmest ingen segmenter, og den globale label-swap-permutation redder det ikke. Multi-scale hjalp intet.

Spectral Clustering (F, H, I) er lidt mere robust — 35–61 % på de samme kald — men kollapsede stadig. Ingen af de fem tilgange *ved* at der kun er én taler.

### 2. PLDA — 88 % på rigtige 2-taler-kald, 10 % på mono

PLDA-metoden (H) klarede sig bedst på kald med to tydeligt adskilte talere. Det er præcis hvad PLDA er designet til: at modellere forskellen i embedding-rummet mellem to taler-distributioner. Men på mono-kald splitter den alligevel, og ender med en worst-case på 10,7 %.

### 3. Gallery-metoden var den mest stabile (±11 %)

EXP J vandt ikke i gennemsnit, men havde langt laveste varians. Den "ved" hvem linje-ejeren er fra historiske kald og gætter rimeligt på modparten. Fejler systematisk på talere den aldrig har hørt — første gang en ny kontakt ringer er gallery-embeddinget tomt for den person.

---

## Konklusion

**Vandt: EXP I (Silero VAD + WeSpeaker + SC)** — 76,1 % agreement, 2,4× hurtigere end pyannote (2,1 s mod 5,1 s).

Forklaringen er at Sileros akustiske VAD-grænser giver renere turn-segmenter end Whispers semantiske grænser. Whisper skærer, hvor meningen stopper; Silero skærer, hvor munden stopper. Renere segmenter → renere embeddings → bedre clustering.

**Forblev på pyannote 3.1 i produktion.** Alle fem alternativer fejler på mono-kald, og mono-kald er et reelt scenarie i en produktionspipeline. Nær-ensidigt kald, mistet forbindelse, kort bekræftende svar — ingen af dem håndteres korrekt af klyngemetoder med fast `n_clusters=2`.

Den mest lovende sti fremad: **EXP I + 1-taler-detektor.** Beregn cosine-variansen inden for en turns embeddings; er variansen under en grænseværdi, er opkaldet sandsynligvis mono og alle segmenter tildeles linje-ejeren. Det ville sandsynligvis nå 85–90 % agreement ved ~2,5 s total — sammenlignelig med pyannote på rigtige 2-taler-kald og korrekt på mono-kald.

> Se [den fulde pipeline](/da/post/dansk-voicelog-transkribering/) og [Whisper backend-benchmarks](/da/post/whisper-backend-sammenligning/) for den bredere kontekst dette eksperiment lever i.
