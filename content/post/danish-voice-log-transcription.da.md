+++
title = "Transskribering af 33.000 danske voicelogs på hjemme-GPU'er — den lokale pipeline (2026)"
date = 2026-06-10
slug = "dansk-voicelog-transkribering"
description = "At bygge en lokal pipeline til at transskribere, diarisere og resumere ~33.000 danske telefonopkald på hjemme-GPU'er: modelbenchmark, dual-model-fusion, phone-first taleridentifikation, selvhelende infrastruktur og Claude Code-subagenter som resumélag — uden LLM-API. Plus hvordan det kan bruges i en kundeservicefunktion."

[taxonomies]
tags = ["tale-til-tekst", "whisper", "dansk", "asr", "hviske", "diarisering", "claude-code", "faster-whisper", "kundeservice", "lokal-ai", "privatliv"]

[extra]
summary = "Forretningstelefonsamtaler var blevet optaget i 13 måneder — ~33.000 danske mp3-filer, ~570 timer 32 kbps telefonlyd. Opgaven: transskribér alt, navngiv talerne, resumér pr. opkald/dag/uge, gør det browsbart på en hjemmeside, og gør det lokalt uden LLM-API. Dette er bygget: et benchmark af danske ASR-modeller, en dual-model + Claude-fusions-pipeline, 'phone-first' taleridentifikation fra metadata, selvhelende infrastruktur over to GPU'er, og Claude Code-subagenter som det (API-løse) resumélag. Plus hvad det lærer om at anvende den samme pipeline i en kundeservicefunktion."
faq = [
  { q = "Hvilken tale-til-tekst-model er bedst til dansk telefonlyd?", a = "I en direkte sammenligning på det rigtige korpus (RTX 4070 Ti) vandt faster-whisper large-v3-turbo på fart (~37× realtid, 1,8 GB VRAM), men den fulde large-v3 var mærkbart mere kohærent på støjende danske opkald, så pipelinen kører fuld large-v3 plus den danske fine-tune hviske-v3-conversation og fusionerer dem. Voxtral hallucinerede i løkker på støjende lyd og blev droppet; vibevoice var ~6× langsommere end realtid." },
  { q = "Hvorfor køre to ASR-modeller i stedet for én god?", a = "Fordi de fejler forskelligt. large-v3 har bedst grammatik og struktur; den danske hviske-fine-tune fanger danske navne og vendinger, som large-v3 forvansker. En Claude-subagent læser begge transskriptioner pr. opkald og fusionerer dem — tager struktur fra den ene og dansk ordvalg fra den anden. To middelmådige-men-forskellige spor plus en model, der fletter dem, slår ét stærkt spor." },
  { q = "Hvordan identificerer man talerne uden stemmetræning?", a = "Metadata først. Hver optagelses filnavn indeholder tidsstemplet og begge telefonnumre, og en lille telefonbog oversætter numre til navne — så man kender begge parter, før et sekund lyd er afkodet. Token-fri ECAPA-TDNN-klyngedeling deler så de to stemmer, og referencestemmeprofiler afgør, hvilken klynge der er den gennemgående part (det ene nummer, der er med på hvert opkald). Et telefonopkald er to-parts, så en 2-taler-prior retter det almindelige tilfælde, hvor klyngedeling kollapser til én." },
  { q = "Hvordan blev resuméerne lavet uden et LLM-API?", a = "Bindingen var ingen API-nøgle. Så Claude Code selv er resumélaget: én subagent pr. dag læser begge ASR-spor for hvert opkald, et fælles navneregister og gårsdagens resumé, og skriver så dagsresuméet direkte — ~50k–450k tokens pr. dag-agent, intet API-kald i pipelinen, ingen marginalomkostning. En uge-subagent syntetiserer de syv dagsresuméer." },
  { q = "Hjælper neural støjreduktion ASR?", a = "Kontraintuitivt nej — det skadede. Et let gammeldags ffmpeg-båndpas (200–3400 Hz) gjorde støjende opkald mere kohærente gratis, men DeepFilterNet (en SOTA neural denoiser) gav hallucinationer og tabt tale. Den er tunet til menneskeører, ikke til Whisper. SOTA er opgaveafhængigt." }
]
+++

**Kort fortalt —** Forretningstelefonsamtaler var blevet optaget i over et år: **~33.000 danske mp3-filer, ~570 timer, 32 kbps telefonkvalitet**. Opgaven var at transskribere det hele, navngive talerne, resumere pr. opkald / pr. dag / pr. uge, gøre det browsbart — og gøre det **lokalt, uden LLM-API**. Resultatet er en pipeline, der kører **to ASR-modeller og fusionerer dem med Claude**, identificerer talere **fra metadata før noget lyd afkodes**, heler sig selv over **to GPU'er**, og bruger **Claude Code-subagenter som resumélag** i stedet for et API. Her er hele bygget, og hvad det lærer om en kundeservicefunktion.

> Den voksne efterfølger til [at køre Whisper lokalt i stedet for et cloud-Speech-API](/post/local-speech-to-text-whisper-cpp/). Samme instinkt — hold lyden på din egen boks — i 33.000-fil-skala.

## Begynd med at analysere ligene

Mappen indeholdt allerede **ni halvfærdige forsøg** på problemet. Før der blev skrevet noget nyt, læste tre agenter alle ni. Tilsammen indeholdt de døde eksperimenter næsten alle de rigtige idéer, det endelige system havde brug for:

- Ét Python-forsøg (WhisperX + pyannote + Claude-dagsresuméer) var det mest komplette — men havde hardcodede API-nøgler, en engelsk-alignment-bug på dansk lyd og mock-diarisering i den "rigtige" pipeline.
- Ét havde opdaget nøgletricket: **phone-first taleridentifikation** (mere nedenfor) og havde allerede bygget stemmeprofiler.
- En Go-omskrivning havde en flot service-arkitektur og et SQLite-skema — men **alt var stubs**; nul segmenter blev nogensinde gemt. Lektion: byg aldrig skallen, før signalvejen virker.
- Et benchmark-harness havde allerede sammenlignet **seks ASR-modeller** på korpusset.

At syntetisere de ni var langt billigere end at opfinde fra bunden. **Lektion ét: analysér ligene først.**

## Modelbenchmarken

Det eksisterende benchmark (på RTX 4070 Ti) plus en frisk sammenligning afgjorde modelvalget:

| Model | Resultat |
|---|---|
| **faster-whisper large-v3-turbo** | Hurtigst — ~37× realtid, 1,8 GB VRAM. God, men glider på støjende dansk. |
| **faster-whisper large-v3 (fuld)** | Mest kohærent på rigtige opkald. ~18× realtid — hurtig nok. **Valgt.** |
| **hviske-v3-conversation** (dansk fine-tune) | Fanger danske navne/vendinger, de andre forvansker. **Valgt som andet spor.** |
| **Voxtral** | Hallucinerede i løkker (1.832 ord for et 117-sekunders opkald), sprog-bleed. **Droppet.** |
| **vibevoice** | ~6× langsommere end realtid. **Droppet.** |

Den ikke-oplagte beslutning: **kør to modeller, ikke én.** large-v3 og hviske **fejler forskelligt** — den ene har grammatikken, den anden har de danske navne — så at beholde begge og fusionere dem slår hver for sig.

## Pipelinen

```
mp3 → ffmpeg båndpas (200–3400 Hz + let denoise + dynaudnorm) → 16 kHz mono
    → [A] faster-whisper large-v3 (int8_float16, beam 5, VAD, anti-løkke-guards)
    → [B] hviske-v3-conversation (dansk fine-tune)              ← kun på opkald ≥45 s
    → ECAPA-TDNN-diarisering (token-fri klyngedeling, 2-taler-prior på lange opkald)
    → "phone-first" navngivning (filnavn + telefonbog forankrer identiteter;
       embeddings afgør hvilken klynge der er den gennemgående part; referenceprofiler matcher resten)
    → SQLite (idempotent: SHA-256-hash + status; dubletter arver tvillingens resultat)

pr. dag  → Claude-subagent læser BEGGE transskriptioner pr. opkald, fusionerer dem,
           retter diarisering ud fra kontekst, skriver dagsresuméet (dansk)
pr. uge  → Claude-subagent syntetiserer 7 dagsresuméer til tråde + en løftetabel
web      → Flask læser DB'en live (dage, uger, opkald m. audio, søgning, mønstre)
```

Et par beslutninger gjorde sig fortjent:

- **Phone-first taleridentifikation.** Filnavnet bærer tidsstemplet og begge numre; en lille telefonbog oversætter numre til navne. Man kender *begge* identiteter, før et ord afkodes — lyden skal kun afgøre *hvilken stemme der er hvem*, ikke *hvem de er*. **Metadata er guld.**
- **ffmpeg-båndpas hjælper; DeepFilterNet skader.** Målt: et 50 år gammelt båndpasfilter gjorde støjende opkald mere kohærente gratis; den neurale SOTA-denoiser gav hallucinationer og tabt tale. **SOTA er opgaveafhængigt.**
- **ECAPA frem for pyannote.** pyannote løb tør for hukommelse ved siden af Whisper på et 12 GB-kort og var for langsom på CPU til 33k filer. Token-fri ECAPA-klyngedeling på GPU'en, med en **2-taler-prior** (et telefonopkald *er* to-parts), reddede de 79% af lange opkald, der ellers kollapsede til én taler.
- **int8_float16 + udvidelige segmenter** lod **begge** modeller sameksistere i ~6–8 GB på 12 GB-kortet.

## Resumélaget: Claude Code-subagenter, intet API

Den hårde binding var **ingen LLM-API-nøgle**. Så harnesset selv er sprogmodellen: **én Claude Code-subagent pr. dag** får begge ASR-spor for hvert opkald, et fælles navneregister og gårsdagens resumé, og skriver dagsresuméet direkte — ~50k–450k tokens pr. dag-agent, **intet API-kald i pipelinen, ingen marginalomkostning.**

Tre små "institutioner" voksede op omkring det:

- **En fusions-instruksfil** — fletregler ([A]'s struktur, [B]'s danske ord), ret diarisering ud fra kontekst (en taler der nævner sit eget navn fastlægger, hvem der taler), spring voicemails over, **opfind aldrig indhold, rapportér usikkerhed ærligt.**
- **Et fælles, voksende navneregister** — agenterne læser det før skrivning og tilføjer nye afklaringer. Over 60+ dage forener det stavevarianter af samme kontakt til én bekræftet identitet og holder to ens-navngivne personer adskilt. Navnekonsistens over hele korpusset, lag på lag.
- **En ugentlig løftetabel** — hver uges agent fører en "løfter & leverancer"-tabel videre (✅/⏳/❌). En reelt nyttig primitiv (og, som vi skal se, broen til kundeservice).

## At køre det over to maskiner

Idempotens gjorde korpusset deleligt midt i kørslen:

- **Maskine 1 (RTX 4070 Ti, 12 GB):** hele dual-model-pipelinen, kronologisk fremad.
- **Maskine 2 (GTX 1060, 6 GB, Pascal):** deployeret over SSH/Tailscale med ét script; tog en senere partition. Kører kun [A]-sporet i int8 (nye CUDA-wheels droppede Pascal, så torch er på CPU mens CTranslate2 driver GPU'en direkte).
- **Merge:** workeren skriver sin egen SQLite; hovedmaskinen henter og merger hvert 15. minut (idempotent — `transcribed` kan opgraderes til `done`). Korpusset behandles **fra begge ender på én gang.**

Fordi hver fil er nøglet på **SHA-256-hash + status**, var det harmløst at flytte halvdelen af arbejdet til en anden maskine midt i kørslen. **Idempotens er friheden til at fejle.**

## Selvheling, lært på den hårde måde

Lange uovervågede kørsler fejler på kreative måder. Hver fejl fik et permanent modtræk:

1. **To transkriptionsprocesser på én GPU** (en forældreløs overlevede en genstart) → gensidig OOM-forgiftning, 756 fejlede rækker. Modtræk: en `flock`-singleton i supervisoren + auto-drab af forældreløse ved opstart.
2. **"Poison file"-myten** — en fil så ud til at crashe processen igen og igen; det var i virkeligheden dual-proces-konflikten. Den kørte fint ved retry. Supervisoren fik retry-én-gang-så-karantæne-logik alligevel.
3. **Tavse hæng** — en worker hang i en time på én fil (proces i live, ingen fremdrift). Modtræk: en watchdog der dræber inder-processen efter 20 min uden DB-aktivitet (DB-mtime som fremdriftssignal).
4. **En ydre watchdog hvert 10. minut** tjekker supervisoren, DB-fremdrift og webserver lokalt — og det hele på workeren over SSH — og genstarter automatisk.
5. **Falske "klar"-dage** — en max-dato-heuristik erklærede en dag færdig, mens 93 af dens 104 filer stadig manglede. Modtræk: **indbakken er ground truth** — en dag/uge er først klar, når *hver* fil har en afgjort DB-række. **Ground truth slår heuristik; max-dato-gættet løj to gange, indbakke-optællingen aldrig.**
6. **Anonyme opkald** — filer fra et hemmeligt nummer matchede ikke filnavnsmønsteret og blev usynlige for dag-gruppering. Parser udvidet, rækker repareret.
7. **En dublet-bug** — identisk lyd under nyt navn blev markeret `done` uden transskription (én hash delt af 103 tomme ring-ud-filer) og forurenede dag-dumps. Nu arver dubletter tvillingens status og indhold.
8. **Høstede baggrundsprocesser** — `nohup`-jobs blev høstet af miljøet og døde ubemærket i timevis. Modtræk: alt langkørende arbejde som harness-managede baggrundstasks, med watchdoggen som bagstopper.

**Selvheling skal være lagdelt:** proces-niveau (supervisor: crash / hæng / poison / orphan) *og* system-niveau (watchdog: supervisor død? web nede? worker væk?).

## Tallene (pr. skrivende stund)

| | |
|---|---|
| Korpus | ~33.000 mp3, ~570 audiotimer, 13 måneder |
| Behandlet | ~6.100 filer (19%), fra begge ender |
| Resuméer | 60 dags- + 7 ugeresuméer |
| Lokal hastighed | dual-model ~0,2 RTF; ~430 filer/time |
| Dag-agent-omkostning | ~50k–450k subagent-tokens/dag (gns. ~200k) |
| Diarisering | 2-taler-prior + kontekst-reparation reddede de 79% af lange opkald, der kollapsede til én stemme |

## Hvordan det kan bruges i en kundeservicefunktion

Den oprindelige use case er personlig opkalds-intelligens, men præcis den samme pipeline er et **kundeservice**-system:

- **To-spors-ASR + LLM-fusion** → præcise danske transskriptioner af supportopkald.
- **Resuméer pr. opkald / dag / uge** → QA uden at lytte til hvert opkald.
- **Løftetabellen** generaliserer direkte til **SLA-/løfte-tracking** — hvad en agent lovede en kunde, og om det blev leveret, ført videre uge for uge.
- **Det fælles navneregister** → et konsistent kunde-/kontaktkartotek bygget fra opkaldene selv.
- **Mønster-visningen** (volumen pr. time, retningsasymmetri, tilbagevendende emner) → bemandings- og eskaleringsindsigt, alt sammen fra metadata + resuméer.
- **PII-disciplin** er indbygget: "opfind aldrig, flag usikkerhed"-reglen og redigering før noget gemmes.

Og privatlivshistorien er salgsargumentet: alt kører **lokalt bag Tailscale** — lyden forlader aldrig bygningen, du sætter opbevaring og redigering, og der er intet offentligt endpoint. (Den ærlige grænse: hvis dit sproglag er et cloud-LLM-API frem for et lokalt harness, forlader den tekst stedet — så redigér først, eller hold LLM'en lokal også.)

## Lektionerne, destilleret

1. **Analysér ligene først** — ni døde eksperimenter rummede næsten alle de rigtige idéer. Syntese slår opfindelse.
2. **Metadata er guld** — filnavne alene gav taleridentitet, dagsstruktur og hele mønsteranalysen, før et sekund lyd var afkodet.
3. **To middelmådige, forskellige ASR-spor + en model der fletter dem slår ét godt spor.** Fejl-diversitet er pointen.
4. **SOTA er opgaveafhængigt** — neural denoise *skadede* ASR målbart; et 50 år gammelt båndpas hjalp.
5. **Idempotens er friheden til at fejle** — hash + status gjorde hvert crash, genstart og midt-i-kørslen-migrering harmløst.
6. **Selvheling i lag** — supervisor for processen, watchdog for systemet.
7. **Ground truth frem for heuristik** til fremdriftsgates — tæl indbakken, gæt ikke fra max-datoen.
8. **En LLM kan være pipelinens dyre trin uden et API** — når harnesset selv er modellen, er et "resumé-trin" en subagent med en god instruksfil, et fælles register og en ærlighedsnorm.
