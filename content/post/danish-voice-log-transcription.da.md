+++
title = "Transskribering af danske voicelogs på en hjemme-GPU — modelgennemgang + en kundeservice-pipeline (2026)"
date = 2026-06-10
slug = "dansk-voicelog-transkribering"
description = "Eksperimenter med at transskribere danske opkalds-/voicelogs lokalt på en RTX 4070 Ti: en gennemgang af de danske tale-til-tekst-modeller (Whisper, Hviske, Røst/CoRal, cloud-API'er), hvad der faktisk betyder noget for telefonlyd, og en privat pipeline, der bruger Claude til at gøre transskriptioner til kundeservicedata."

[taxonomies]
tags = ["tale-til-tekst", "whisper", "dansk", "asr", "hviske", "coral", "kundeservice", "claude", "tailscale", "lokal-ai", "privatliv"]

[extra]
summary = "Jeg har transskriberet danske voicelogs lokalt på en RTX 4070 Ti og brugt Claude til at gøre de rå transskriptioner til strukturerede kundeservicedata — alt sammen tilgængeligt privat over Tailscale, så lyden aldrig forlader min egen maskine. Dette indlæg gennemgår de danske tale-til-tekst-muligheder (almindelig Whisper vs. de danske fine-tunes Hviske og Røst, vs. cloud-API'er), hvad der faktisk rykker word-error-rate på rigtig telefonlyd, og hele pipelinen til en kundeservice-anvendelse — med GDPR-vinklen, der gør 'lokalt' til selve pointen."
faq = [
  { q = "Hvilken tale-til-tekst-model er bedst til dansk?", a = "Til lokal brug slår en dansk-fine-tunet Whisper-large-model almindelig OpenAI Whisper på dansk — de to vigtigste muligheder er Hviske (syvai/hviske-v2) og Røst-whisper-large fra CoRal / danish-foundation-models-projektet. Almindelig Whisper large-v3 er et solidt udgangspunkt, hvis du vil have én model til mange sprog. Til et færdigt API understøtter ElevenLabs Scribe, Azure og Google Chirp alle dansk godt." },
  { q = "Kan det køre på en 12 GB GPU?", a = "Ja. Whisper-large-klasse-modeller (inklusive de danske fine-tunes) passer fint på et 12 GB-kort som et RTX 4070 Ti, især via faster-whisper (CTranslate2) med int8/float16, hvilket også giver dig flere gange realtid til batch-transskribering af opkaldslogs." },
  { q = "Hvorfor transskribere lokalt i stedet for at bruge et cloud-API?", a = "Privatliv og GDPR. Kundeservice-voicelogs er personoplysninger (ofte med navne, adresser, CPR-numre). At køre transskriberingen på din egen GPU — kun tilgængelig over et privat Tailscale-netværk — betyder, at lyden aldrig forlader din kontrol. Du bestemmer opbevaring, redigering og hvem der kan nå tjenesten." },
  { q = "Hvad laver Claude i pipelinen?", a = "Claude er sproglaget efter transskriberingen: den rydder op i den rå ASR-tekst, markerer hvem der sagde hvad, og gør et opkald til strukturerede data — et resumé, kundens hensigt, stemning, handlingspunkter og et QA-scorekort. Selve transskriberingen (lyd → tekst) bliver på GPU'en; Claude arbejder på teksten." },
  { q = "Hvor præcist er det på rigtig telefonlyd?", a = "Lavere end de publicerede benchmarks. Rene oplæsnings-benchmarks lander i de lave encifrede fejlrater, men 8 kHz telefonlyd med baggrundsstøj, overlappende talere, dialekt og engelsk kodeskift skubber word-error-rate meget højere op. Behandl benchmark-tal som et loft, ikke som det, du får på et støjende opkald." }
]
+++

**Kort fortalt —** Jeg transskriberer danske voicelogs **lokalt på en RTX 4070 Ti** og bruger så **Claude** til at gøre den rå transskription til strukturerede kundeservicedata (resumé, hensigt, stemning, QA-score). Det hele er kun tilgængeligt over et privat **Tailscale**-netværk, så **lyden aldrig forlader min maskine** — hvilket er hele pointen for GDPR-følsomme kundedata. Dette indlæg gennemgår de danske tale-til-tekst-modeller, hvad der faktisk betyder noget på rigtig telefonlyd, og hele pipelinen.

> Baggrund: dette er den voksne udgave af [at køre Whisper lokalt i stedet for et cloud-Speech-API](/post/local-speech-to-text-whisper-cpp/). Samme instinkt — hold lyden på din egen boks — anvendt på danske opkaldslogs.

## Opsætningen

Intet eksotisk, og det er pointen:

- **GPU:** et enkelt **RTX 4070 Ti (12 GB)** — nok til at køre Whisper-large-klasse-modeller fint.
- **Adgang:** transskriberingstjenesten lytter på en port (`:5000`) og er kun tilgængelig **over Tailscale** (et privat WireGuard-mesh). Der er intet offentligt endpoint — boksen har et MagicDNS-navn som `gpu-box.tailnet.ts.net:5000`, som kun enheder på mit tailnet kan slå op eller nå.
- **To lag:** **GPU'en laver lyd → tekst** (Whisper / en dansk fine-tune); **Claude laver tekst → struktur** (kundeservice-intelligensen). Den dyre, privatlivsfølsomme del — den rå lyd — forlader aldrig det lokale netværk.

## Hvorfor dansk er den svære del

Engelsk ASR er stort set løst. Dansk er sværere, og kundeservicelyd gør det endnu sværere:

- **Sprog med færre ressourcer.** Langt mindre træningsdata end engelsk, så generiske modeller er svagere fra start.
- **Sammensatte ord og reduceret tale.** Dansk smelter ord sammen og sluger endelser; grænsen mellem ord er reelt flertydig.
- **Dialekter.** En model kan være næsten perfekt på standard-københavnsk og falde fra hinanden på **sønderjysk** eller stærk **nordjysk**.
- **Engelsk kodeskift.** Danskere smider engelske termer ind midt i en sætning ("jeg *resetter* lige din *account*"), hvilket spænder ben for sproglåste modeller.
- **Telefonlyd.** Rigtige opkaldslogs er **8 kHz smalbånd**, komprimeret, med ventemusik, krydstale og baggrundsstøj. Det er den enkeltstørste præcisionsdræber.

## Modellerne jeg sammenlignede

| Model | Type | Kører | Dansk | Noter |
|---|---|---|---|---|
| **Whisper large-v3 / turbo** (OpenAI) | Whisper | lokalt (faster-whisper) | god | stærk flersproget baseline; turbo er meget hurtigere |
| **Hviske** (`syvai/hviske-v2`) | Whisper-large fine-tune | lokalt | **bedre på dansk** | dansk-optimeret ("hviske" = *whisper*) |
| **Røst-whisper-large** (CoRal / danish-foundation-models) | Whisper-large fine-tune | lokalt | **bedst på dansk** | trænet/evalueret på det danske **CoRal**-korpus |
| **Røst-wav2vec2** (315M / 1B) | wav2vec2 CTC | lokalt | stærk | lettere, hurtig; ingen indbygget tegnsætning |
| **ElevenLabs Scribe** | cloud-API | hostet | meget god | ~3,1% WER FLEURS / 5,5% Common Voice (leverandør) |
| **Azure / Google Chirp / Amazon** | cloud-API | hostet | god | færdigt, diarisering indbygget, men data forlader din kontrol |

Formen på det: **de danske fine-tunes (Hviske, Røst) slår klart almindelig Whisper på dansk**, og de passer på 4070 Ti'en. Cloud-API'er er fremragende og bekvemme, men for kundedata er "hostet"-kolonnen netop problemet.

## Performance — hvad der faktisk betyder noget for voicelogs

Læs ikke en leverandørs rene-lyd-tal og forvent det på en opkaldsoptagelse.

- **CER vs. WER — sammenlign dem ikke direkte.** CoRal-benchmarken rapporterer **character** error rate: **Røst-whisper-large ≈ 4,3% CER** samlet. Leverandører som ElevenLabs rapporterer **word** error rate (≈3,1% WER FLEURS). CER er normalt lavere end WER; det er forskellige mål på forskellige (rene) data.
- **Dialektvariation er enorm.** På CoRal går den samme model fra **~1,6% (nordjysk) til ~12,6% (sønderjysk)**. Din præcision afhænger af *hvem der ringer*.
- **Telefonlyd-klippen.** Rene benchmarks ligger under ~8%; tilføj 8 kHz-komprimering, støj og overlap, og virkelig WER kan klatre **forbi 30-35%**. Resample til 16 kHz mono og fjern støj, før du transskriberer — det betyder mere end modelvalget.
- **Gennemløb.** Med **faster-whisper** (CTranslate2, int8/float16) laver 4070 Ti'en batch-transskribering flere gange hurtigere end realtid, så en dags opkaldslogs kører natten over.
- **Diarisering og tegnsætning.** Whisper giver tegnsætning/store bogstaver gratis; wav2vec2 gør ikke. Til "hvem sagde hvad" (agent vs. kunde) tilføjer du en diariser (pyannote / WhisperX).

**Hvad jeg ville køre:** **Røst-whisper-large** (eller Hviske) på **faster-whisper**, lyd præ-resamplet til 16 kHz mono, med pyannote til diarisering. Lokalt, dansk-tunet, passer på GPU'en.

## Hvor Claude kommer ind — kundeservice-anvendelsen

Rå ASR-tekst er ikke nyttig i sig selv. Værdien er, hvad du gør med den, og det er sproglaget — **Claude gør en transskription til strukturerede, handlingsbare data**:

- **Oprydning & talermærkning** — ret ASR-fejl, markér **agent**- vs. **kunde**-ture.
- **Resumé** — tre linjer "hvad opkaldet handlede om, og hvordan det endte".
- **Hensigt / emne** — klassificér i dine kategorier (fakturering, opsigelse, teknisk…).
- **Stemning & eskaleringsrisiko** — var kunden vred? truede de med at skifte?
- **Handlingspunkter** — hvad agenten lovede, hvad der stadig er åbent.
- **QA-scorekort** — hilste agenten, verificerede identitet, tilbød den rigtige løsning, lukkede ordentligt?
- **Vidensudvinding** — tilbagevendende spørgsmål bliver FAQ-/hjælpecenter-kandidater.
- **PII-redigering** — fjern navne, adresser, **CPR-numre**, før noget gemmes eller analyseres.

Giv Claude den diariserede transskription og et skema, og få JSON tilbage, som du kan gemme, søge i og lave dashboards på. En uges opkald bliver et datasæt, du kan forespørge: top-hensigter, stemningstendens, agenter der har brug for coaching, FAQ'en der skriver sig selv.

## Pipelinen i praksis

```sh
# 1. Normalisér telefonlyd: 8 kHz stereo-opkald -> 16 kHz mono, modellens native rate
ffmpeg -i opkald.wav -ac 1 -ar 16000 -af "highpass=f=80,lowpass=f=7500" opkald16.wav

# 2. Transskribér lokalt på GPU'en (dansk fine-tune via faster-whisper)
#    model = et Røst/Hviske Whisper-large-checkpoint, serveret på tailnet'et på :5000
curl -s -F "file=@opkald16.wav" http://gpu-box.tailnet.ts.net:5000/transcribe > raa.json

# 3. Diarisér (hvem talte hvornår) og flet med transskriptionen -> ture.json
#    (pyannote / WhisperX)

# 4. Strukturér det med Claude: ture.json + et JSON-skema -> opkaldsrecord
#    resumé, hensigt, stemning, handlingspunkter, QA-score, PII redigeret
```

Alt op til trin 3 kører på boksen og over tailnet'et — **lyden rører aldrig internettet**. Trin 4 sender *tekst* til Claude; se privatlivsnoten nedenfor.

## Privatlivs- / GDPR-vinklen (det er salgsargumentet)

Kundeservice-voicelogs er **personoplysninger**. At lave transskriberingen lokalt, bag Tailscale, betyder:

- **Lyden forlader aldrig din kontrol** — intet tredjeparts-speech-API, ingen upload af optagelser.
- **Du sætter opbevaring og redigering** — transskribér, udtræk det du har brug for, slet lyden.
- **Adgang er privat som standard** — tjenesten har intet offentligt endpoint; kun tailnet-enheder når den.

Vær ærlig om den ene grænse: i trin 4 går **transskriptionstekst** til Claude-API'et. Det er et databehandlerforhold — brug en databehandleraftale, redigér PII *før* afsendelse, og foretræk nul-opbevaring. Hvis selv det er for meget, så udskift Claude med en lokal LLM og hold hele pipelinen på 4070 Ti'en. Arkitekturen er den samme; kun sproglaget flytter.

## Opsummering

- Transskribér danske voicelogs **lokalt** på en 12 GB-GPU; lyden forlader aldrig din maskine.
- **Danske fine-tunes vinder:** **Røst-whisper-large** (CoRal) eller **Hviske** slår almindelig Whisper på dansk, via **faster-whisper**.
- **Benchmarks er et loft** — CER ≈ 4,3% på rent CoRal, men telefonlyd + dialekt + kodeskift skubber virkelig WER langt højere. Resample og fjern støj først.
- **Claude er sproglaget:** transskription → resumé, hensigt, stemning, handlingspunkter, QA-score, PII-redigeret — den egentlige kundeservice-værdi.
- **Hold det privat:** lokal transskribering bag **Tailscale**; redigér før noget tekst forlader; eller kør LLM'en lokalt også.
