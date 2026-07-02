+++
title = "Fine-tuning af Whisper til danske telefonopkald: en LoRA-obduktion (2026)"
date = 2026-07-02
slug = "dansk-whisper-lora-finetuning"
description = "Fine-tuning af whisper-large-v3 på CoRal-v3 til dansk telefonlyd: en trænings-loss-fejl, der lignede fundamental modelustabilitet, men var en fejl i warmup-skemaet, et benchmark, der næsten halverede WER, og en systematisk gennemgang, der viste, at benchmarket ikke var hele historien."

[taxonomies]
tags = ["tale-til-tekst", "whisper", "dansk", "asr", "lora", "fine-tuning", "peft", "huggingface", "coral", "claude-code"]

[extra]
summary = "Fine-tunede whisper-large-v3 på CoRal-project/coral-v3 (dansk tale, telefon-kodek-augmenteret) med LoRA. Træningstabet sad fast omkring 35-40 tre forsøg i træk — så ud som om large-v3 selv var ustabil under LoRA. Det var det ikke: warmup-skemaet var for langt i forhold til, hvor langt træningen rent faktisk kørte. Rettet, og modellen halverede næsten WER på tilbageholdt dansk tale sammenlignet med den utrænede base. Så fandt en systematisk gennemgang af 30 rigtige opkald en reel fabrikationsrate, som benchmark-tallet ikke viste — udgivet alligevel, med et ærligt modelkort."
faq = [
  { q = "Hvorfor sad LoRA-fine-tuningens træningstab fast?", a = "Tre separate træningsforsøg lagde sig alle fast omkring et tab på 35-40 i stedet for at konvergere til enkeltcifrede tal, og hver gang så det ud som en anden grundårsag — dårlige lydniveauer, et overflødigt præprocesseringsfilter, og derefter mistænkt læringsrate-ustabilitet på den fulde model. Den faktiske årsag var simplere: warmup-skemaet (100 skridt) var langt i forhold til, hvor langt hvert testkørsel rent faktisk nåede, så læringsraten nåede aldrig sin målværdi. En kontrolleret test med et proportionalt kortere warmup konvergerede rent i første forsøg." },
  { q = "Forbedrer fine-tuning på offentlig dansk taledata nøjagtigheden på rigtige telefonopkald?", a = "På et tilbageholdt benchmark med rigtig ground truth, ja betydeligt — word error rate på samtale-dansk blev næsten halveret sammenlignet med den utrænede basismodel. Men en separat kvalitativ gennemgang af rigtige (ikke benchmark-) telefonoptagelser fandt, at den fine-tunede model af og til fandt på indhold — et navn eller en detalje, der ikke var til stede i referencetransskriptionen — med en hyppighed på omkring 1 ud af 8 opkald. Benchmark-målingen og pålideligheden i den virkelige verden målte to forskellige ting." },
  { q = "Hvorfor fanger et WER-benchmark ikke hallucination/fabrikation?", a = "Word error rate måler, hvor mange ord der samlet set afviger fra en referencetransskription — det skelner ikke mellem en fejl, der forvansker et ord, og en fejl, der finder på en troværdigt lydende sætning. En model kan score bedre på WER, mens den af og til producerer selvsikkert, sammenhængende og helt forkert output. Den eneste måde at fange den fejltype på er en kvalitativ gennemlæsning af rigtige outputs, ikke en metrik." },
  { q = "Bør man udgive en fine-tunet model med kendte fejltilstande?", a = "Ja, hvis modelkortet siger det ærligt. En model med en dokumenteret ~13% fabrikationsrate og klar brugsvejledning (brug den ikke som eneste kilde til navne-/enhedsudtræk) er mere nyttig for fællesskabet end enten at skjule fejlen eller slet ikke udgive den — især når den utrænede basismodel har sin egen sammenlignelige fejlrate, der bare ser anderledes ud." }
]
+++

**Kort fortalt —** Fine-tunede [whisper-large-v3](https://huggingface.co/openai/whisper-large-v3)
på [CoRal-project/coral-v3](https://huggingface.co/datasets/CoRal-project/coral-v3) (rigtig,
menneske-transskriberet dansk tale) med en LoRA-adapter, telefon-kodek-augmenteret for at lukke
hullet til rigtig telefonlyd. Træningstabet sad fast på samme plateau **tre gange i træk**, og
hver gang så forklaringen anderledes ud — indtil det viste sig at være én kedelig
skemalægningsfejl. Rettet, og modellen **halverede næsten word error rate** på tilbageholdt
dansk tale. Så fandt en systematisk gennemgang af rigtige telefonoptagelser, at benchmark-tallet
ikke fortalte hele historien. Udgivet alligevel — [på Hugging Face](https://huggingface.co/x2q/whisper-large-v3-da-coral-lora),
med et ærligt modelkort.

> Fine-tuning-efterfølgeren til [transskribering af 33.000 danske voicelogs på hjemme-GPU'er](/post/dansk-voicelog-transkribering/).
> Det indlæg valgte basismodellerne; dette forsøger at gøre en af dem bedre.

## Tabet, der ikke ville bevæge sig

Opsætningen: [PEFT](https://github.com/huggingface/peft) LoRA (rank 32, alpha 64,
`q_proj`/`v_proj`) oven på whisper-large-v3, trænet på ~9.000 lydstykker fra coral-v3 —
tre fjerdedele kørt gennem en telefon-kodek-simulering (8kHz-båndbreddegrænse,
lav-bitrate-mp3-rundtur, let støj), så modellen ville se noget tættere på rigtig
opkaldslyd end coral-v3's rene studieoptagelser.

Krydsentropi-tab bør starte højt og falde til enkeltcifrede tal, efterhånden som
træningen konvergerer. I stedet gjorde tre separate forsøg det samme: et skarpt
indledende fald, derefter et hårdt plateau omkring 35-40, der aldrig bevægede sig,
uanset hvor længe træningen kørte. Hvert forsøg pegede på en anden synder — og hver
rettelse var reel, og ingen af dem løste det faktiske problem:

1. **Mistænkt: dårlig lyd.** Coral-v3's rå optagelser viste sig at have vildt
   uensartede lydstyrker — nogle stykker praktisk talt næsten stille (median-RMS en
   størrelsesorden under sund tale). Whispers feature-extractor er følsom over for
   absolut amplitude, så dette var en reel fejl. Rettet med lydstyrkenormalisering
   (EBU R128, -16 LUFS) på hvert stykke. **Tabet: sad stadig fast på 35-40.**
2. **Mistænkt: dobbeltbehandling.** Træningsscriptet genanvendte et støj-/EQ-filter
   beregnet til *rå, ubehandlet* produktionslyd på data, der allerede var fuldt
   forbehandlet — en rest fra genbrug af kode skrevet til en anden datakilde.
   Bekræftet ved direkte måling: det overflødige filter pressede nogle stykkers
   lydstyrke lige tilbage ned. Rettet. **Tabet: sad stadig fast på 35-40.**
3. **Mistænkt: modellen selv.** Med begge lydfejl rettet og plateauet uændret,
   skiftede arbejdsteorien til, at læringsraten var ustabil for den *fulde*
   whisper-large-v3 (32 decoder-lag) versus den mindre turbo-variant (4 lag), som en
   tidligere, vellykket fine-tuning havde brugt. En kontrolleret test — samme
   LoRA-konfiguration, samme kendt-gode data, kun basismodellen udskiftet —
   genskabte det identiske plateau. Test af en 5x lavere læringsrate gav et
   *identisk* resultat. Det var beviset: **to forskellige læringsrater, der
   konvergerer til præcis den samme "fastsiddende" værdi, er ikke et
   læringsrate-problem.**
4. **Den faktiske fejl.** Warmup-skemaet var 100 skridt, og hvert testkørsel —
   inklusive, viste det sig, de *rigtige* træningskørsler — blev kun nogensinde
   observeret midtvejs gennem den optrapning. Læringsrate-skemalæggeren klatrede
   stadig mod sin målværdi hele tiden, nogen havde kigget på den. Et kort,
   proportionalt warmup (40 af 548 samlede skridt) konvergerede rent i det allerførste
   efterfølgende forsøg: **98 → 83 → 68 → 54 → 39 → 26 → 16 → 13 → 11 → 9,5**, der
   fulgte næsten præcis banen for en tidligere, allerede bevist fine-tuning.

To af de tre rettelser var reelle fejl, det var værd at rette i sig selv. Ingen af dem
var *den* fejl. Lektionen generaliserer ud over dette ene projekt: **en metrik, der ser
"fastsiddende" ud, kan bare være et skema, der ikke er færdigt med at trappe op** —
tjek det, før du konkluderer, at noget grundlæggende er i stykker.

(En mindre, separat fejl undervejs: parallelisering af data-forberedelsestrinnet med en
trådpulje gav nondeterministiske nedbrud med en `PyGILState_Release`-fejl — et
C-udvidelses-trådproblem, ikke min kodes logik. En procespulje, som giver hver worker
sin egen uafhængige interpreter-tilstand, løste det fuldstændigt. **Foretræk
procespuljer frem for trådpuljer, når arbejdet er C-udvidelsestungt** (lydafkodning,
kodek-kald) frem for ren Python.)

## Benchmarket: en reel gevinst

Med træning, der rent faktisk konvergerede, den rigtige test: et tilbageholdt sæt
coral-v3-stykker (adskilt fra træningen — garanteret ved at springe det nøjagtige
antal stykker over, som træningen brugte, fra den samme deterministiske blanding) med
rigtig ground truth, så word error rate kan beregnes direkte i stedet for at blive
vurderet med øjemål.

| model | samtale-dansk WER | oplæsnings-dansk WER |
|---|---|---|
| whisper-large-v3 (utrænet) | 0,704 | 0,303 |
| **fine-tunet (dette indlæg)** | **0,367** | 0,220 |
| CoRals egen formålsbyggede danske model | 0,327 | 0,101 |

Næsten en **halvering** af samtale-WER fra en generisk basismodel, der lukker det
meste af hullet til en model bygget fra bunden til dansk. Oplæsningstallet forbedredes
mindre, fordi træningen kun brugte coral-v3's `conversation`-split — en klar, testbar
forudsigelse, der holdt stik (formel, skriptet tale er en anden fordeling end uformel
samtale, og modellen så kun den ene af dem).

## Men WER var ikke hele historien

Et WER-tal er en samlet størrelse: det fortæller dig *hvor meget* tekst der afviger fra
referencen, ikke *hvilken slags* fejl der er tale om. En model, der af og til erstatter
et rigtigt ord med et andet, forkert-men-plausibelt ord, og en model, der af og til
finder på en selvsikker, flydende, helt fabrikeret sætning, kan opnå den *samme* WER —
men kun den ene af dem er sikker at bruge uden opsyn.

Så: en systematisk kvalitativ gennemgang, på rigtige (ikke benchmark-) telefonoptagelser
— det faktiske måldomæne, ikke en stedfortræder for det. Hvert output fra den
fine-tunede model blev sammenlignet med fem andre modellers transskriptioner af den
samme lyd, specifikt på udkig efter indhold uden opbakning noget andet sted: et
opdigtet navn, en opdigtet detalje, en påstand der ikke blev sagt. (Intet
opkaldsindhold gengives her — optagelserne er private forretningsopkald; kun det
samlede resultat betyder noget for dette indlæg.)

Resultatet: **omtrent hvert ottende opkald viste en klar fabrikation** — indhold
sagt med selvsikkerhed, som ingen anden model, og formodentlig ingen på opkaldet,
rent faktisk sagde. Omkring halvdelen af opkaldene var i praksis ækvivalente med den
utrænede baseline, og det meste af resten adskilte sig kun i formulering eller
udeladelse, ikke opdigtning. Et genuint interessant sidespring: den utrænede
*basismodel* har sin egen velkendte fejltilstand på stille lyd (en specifik
hallucineret "falsk undertekst-credit"-linje, en dokumenteret Whisper-artefakt), der
dukkede op på en sammenlignelig andel af opkald — og den fine-tunede model genskabte
aldrig den specifikke fejl, hvilket tyder på, at fine-tuningen byttede én fejlklasse
ud med en anden i stedet for blot at lægge et nyt problem oven på en ren baseline.

**Samlet vurdering:** en reel, betydelig nøjagtighedsforbedring på den metrik, der er
let at måle, og et reelt, ikke-trivielt pålidelighedshul på den egenskab, der rent
faktisk betyder noget for brug uden opsyn — opdigtede navne og enheder er præcis det
forkerte at få galt i et system, der bruges til at spore, hvem der sagde hvad. Ingen
af de to kendsgerninger ophæver den anden.

## Udgivet alligevel

Adapteren er på Hugging Face: **[x2q/whisper-large-v3-da-coral-lora](https://huggingface.co/x2q/whisper-large-v3-da-coral-lora)**.
Modelkortet angiver WER-tallene, træningsdata og licens (coral-v3 er OpenRAIL-licenseret
og citeret direkte — ingen grund til at skjule et legitimt, statsstøttet dansk
tale-datasæt bag en vagere beskrivelse), fabrikationsrate-fundet, og en konkret
brugsadvarsel: brug den ikke som eneste kilde til automatisk navne-/enhedsudtræk uden
en anden model eller et menneske i løkken.

En mangelfuld model med et ærligt kort er mere værd for den, der finder den, end en
tavs én.

## Lektionerne, destilleret

1. **En fastsiddende metrik kan bare være et ufærdigt skema** — tre plausibelt
   lydende grundårsager (dårlig data, dobbeltbehandling, læringsrate-ustabilitet)
   var alle reelle fejl og alle forkerte om den faktiske årsag, som var en
   warmup-optrapning, ingen havde ladet færdiggøre, før de drog konklusioner.
2. **To forskellige værdier, der konvergerer til det identiske forkerte svar, er et
   stærkt signal** — hvis ændring af en hyperparameter ikke ændrer resultatet, er
   hyperparameteren sandsynligvis ikke årsagen.
3. **Procespuljer frem for trådpuljer til C-udvidelsestungt parallelt arbejde** — et
   nondeterministisk nedbrud på interpreter-niveau forsvandt fuldstændigt, da hver
   worker fik sin egen proces i stedet for at dele én interpreters GIL-tilstand.
4. **En enkelt samlet metrik kan ikke se fejltilstands-diversitet** — WER behandler
   et forvansket ord og en selvsikkert opdigtet sætning ens. Hvis de to betyder noget
   forskelligt for dit brug (det gør de næsten altid), har du brug for en kvalitativ
   gennemlæsning, ikke bare et bedre tal.
5. **Udgiv fejlen, ikke kun gevinsten** — en dokumenteret fejlrate med klar
   brugsvejledning er et mere nyttigt artefakt end et pænt udseende modelkort, der
   viser sig at skjule det samme problem, basismodellen allerede havde.
