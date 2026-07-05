+++
title = "Vi troede modellen var problemet. Den var ikke."
date = 2026-07-05
slug = "speaker-identifikation-fem-forsoegsrunder"
description = "Fem forsøgsrunder med speaker fingerprinting på telefonopkald: fra en model der 'ikke kunne skelne stemmer' til 87,2% nøjagtighed — men først efter vi fandt ud af, at problemet aldrig var modellen. Ingen navne, kun metoden."

[taxonomies]
tags = ["speaker-identification", "stemme-fingeraftryk", "diarization", "maskinlaering", "whisper", "data-science", "evaluering", "dansk"]

[extra]
summary = "Et speaker-identification-eksperiment på telefonopkald gik gennem fem runder — fra en konklusion om at 8kHz-telefonlyd 'drukner stemmeidentitet' (EER 35-45%), over et metodegennembrud (82-92% på et rigtigt guldsæt), til et realitetstjek der styrtdykkede til 59,5% på blinde opkald. Løsningen var ikke en bedre model — det var at opdage, at 68% af de 'enkelt-taler'-klip faktisk indeholdt to stemmer. Renset for det: 87,2% nøjagtighed, AUC 0,856."
faq = [
  { q = "Hvad er speaker fingerprinting?", a = "Speaker fingerprinting (også kaldet speaker identification eller speaker verification) er opgaven at afgøre, hvem en given stemme tilhører som en konkret, kendt person — modsat speaker diarization, som blot afgør, hvilke lydsegmenter der hører til samme (unavngivne) taler. Typisk bruges en embedding-model (fx ECAPA-TDNN) til at lave et numerisk 'fingeraftryk' af en stemme, som derefter sammenlignes med kendte referencer." },
  { q = "Hvorfor virkede modellen dårligt i starten?", a = "Ikke fordi modellen var dårlig til stemmegenkendelse — men fordi evalueringsmetoden var forkert. Træningsdata kom fra pipelinens egne, delvist kollapsede diarization-labels (støj mod støj), og den målte opgave (cross-call-verifikation) var sværere og mindre relevant end den faktiske opgave (inden for ét opkald, hvilken klynge er ejeren?)." },
  { q = "Hvad var den egentlige årsag til de dårlige resultater på rigtige opkald?", a = "Menneskelig verifikation af tilfældige lydklip viste, at 68% af de klip, pipelinen havde mærket som 'énkelt taler', faktisk indeholdt hørbare spor af to forskellige stemmer. Modellen forsøgte at identificere én taler i klip, der reelt indeholdt to — det er ikke et modelproblem, det er et datakvalitetsproblem opstrøms i diarization-trinnet." },
  { q = "Hvad var nøjagtigheden til sidst?", a = "87,2% nøjagtighed med en AUC på 0,856 — men kun når man måler på klip, et menneske har bekræftet er rene (kun én taler). På en helt tilfældig, ublindet population af rigtige opkald var enigheden med de eksisterende labels kun 59,5%, fordi størstedelen af klippene reelt var blandede." },
  { q = "Hvorfor virkede kanal-fingeraftryk ikke?", a = "Ideen var at udnytte, at ejerens side af hvert opkald går gennem samme telefonudstyr og dermed har en genkendelig kanalsignatur. Men opkaldene er optaget som én delt mono-kanal for begge talere samtidig — der findes ingen adskilt 'ejer-kanal' at fingeraftrykke separat fra modpartens." }
]
+++

Vi har en pipeline, der transskriberer og opsummerer tusindvis af telefonopkald. Et af de sidste, uløste problemer var enkelt at formulere og forbandet svært at løse: **hvem taler egentlig i hvert opkald?**

Diarization (at splitte lyd op i "taler A" og "taler B") virker fint på det tekniske plan — men at vide *hvem* taler A og B *er* som mennesker, er en helt anden opgave. Vi prøvede i fem runder. Den femte gav endelig svaret — men ikke det svar, vi forventede.

> Dette er et opfølgende indlæg til [fem alternativer til pyannote](/da/post/diarization-fem-alternativer/) og [den fulde voicelog-pipeline](/da/post/dansk-voicelog-transkribering/). Ingen navne, telefonnumre eller virksomhedsdetaljer optræder i dette indlæg — kun metoden og tallene.

## Udgangspunktet: "kanalen dominerer identiteten"

De første tre forsøgsrunder konkluderede noget deprimerende: på 8kHz-telefonlyd drukner stemmeidentitet i støj fra telefonlinjen og codec'et. En moderne speaker-embedding-model (ECAPA-TDNN) kunne knap skelne to forskellige mennesker fra hinanden bedre end tilfældigt gæt, målt ved en Equal Error Rate på 35-45%.

Konklusionen virkede solid. Den var forkert.

## Runde 4: at stille spørgsmålstegn ved sin egen metode

Vi bad en anden model om at kritisere vores eget arbejde adversarielt — uden at være investeret i konklusionen. Den fandt to fatale metodefejl:

1. **Cirkulære labels.** Vores træningsdata kom fra pipelinens egne speaker-labels — den samme pipeline, vi prøvede at forbedre. 40% af kaldene havde kollapset diarization (ét navn på hvert segment). Vi målte støj mod støj.
2. **Forkert opgave.** Vi målte cross-call-verifikation (er stemme A fra kald 1 samme person som stemme B fra kald 2?), men den *rigtige* opgave er meget lettere: inden for ét opkald, hvilken af de to klynger er linjeejeren? Her går den delte telefonkanal ud i differencen — den nøjagtige confound, vi troede dominerede alt.

Vi genopbyggede et guldsæt fra transskript-selvintroduktioner ("det er [navn]") i stedet for pipeline-labels, og re-scorede de *samme* embeddings på den *rigtige* opgave. Resultat: **82-92% nøjagtighed.** Samme model. Samme data. Bare målt rigtigt denne gang.

## Realitetstjekket der ikke stemte

Før vi fejrede, testede vi metoden blindt på de 100 seneste rigtige opkald — ikke det kuraterede guldsæt, bare almindelige samtaler.

**59,5% enighed med pipelinens eksisterende labels.** Stort set møntkast.

Og konfidensen var *omvendt* kalibreret: jo mere sikker modellen var, jo oftere tog den fejl. Det er ikke støj. Det er et systematisk problem.

## Fem forsøg til at lukke gabet — ingen af dem virkede

Vi prøvede:

- **Tekst + adfærdsfusion** (ordvalg, taletidsandel, turtagning): 92% på guldsættet, 100% på det ene kendte svære forvekslingspar. Kollapsede til identisk 62% på blinde rigtige kald — samme selektionsbias som guldsættet selv.
- **Kanal-fingeraftryk** (udnytte at linjeejerens side af hvert opkald går gennem samme udstyr): tæt på tilfældigt. Viste sig at hele opkaldet — begge talere — deles om én mono-optaget kanal, så der findes ikke en separat "ejer-kanal"-signatur at finde.
- **Domænetilpasning via Common Voice**: her kom det første rigtige gennembrud i *forklaringen*, ikke løsningen. Vi tog en helt uafhængig dataset med pålidelig ground truth, kørte den gennem vores telefonsimulering, og testede den samme model: **100% på ren tale, 98,7% på telefonsimuleret tale.** Modellen kan sagtens håndtere telefonlyd. Vores grundantagelse siden runde 1 var forkert.
- **Formant/pitch-landmarks** (Shazam-inspireret): reelt signal, men underpræsterede akustik.
- En trænet meta-klassifikator over alle sensorer samtidig: slog ikke den simple akustiske model alene.

## Den manuelle mærkning der løste det

Vi byggede en mobilvenlig side, hvor et menneske kunne bekræfte: er dette lydklip linjeejeren, eller en anden? Tilfældig stikprøve — ingen automatisk forudindtagethed.

**68% af klippene indeholdt hørbare spor af BEGGE talere.**

Vi testede, om det bare var vores klip-metode: byggede den om fra bunden (færre, længere segmenter, kanttrimning, pauser mellem sammensplejsninger). Samme rate, til decimalen: 68,2% før, 68,2% efter.

## Kapitlet der lukker historien

Vi scorede kun de klip, et menneske havde bekræftet var *rene*, fra en helt tilfældig population.

**87,2% nøjagtighed. AUC 0,856.**

Modellen har aldrig været problemet. Problemet var, at op mod 2 ud af 3 "enkelt-taler"-klynger faktisk indeholder to personers stemmer.

## Bonusfundene undervejs

Menneskelig verifikation afslørede tre reelle fejl i vores kontaktregister, som ingen havde opdaget — fejlagtigt sammenblandede personer, et familiemedlem forkert registreret som forretningskontakt, og et navn indtastet forkert for år siden.

## Det vi tager med os

- **Mistro din egen evalueringsmetode**, især hvis labels stammer fra det system, du prøver at forbedre.
- **Test på en population, du ikke selv har kurateret.**
- **Split confidence fra korrekthed.** Et velkalibreret system bliver mere præcist, når det er mere sikkert — sker det modsatte, leder du efter det forkerte problem.
- **Simple metoder vinder, indtil du har data nok til at retfærdiggøre kompleksitet.**
- **Menneskelig verifikation er stadig den billigste vej til sandheden**, når du ved præcis, hvilket spørgsmål du skal stille.

> Se også [fem alternativer til diarization](/da/post/diarization-fem-alternativer/) for det tekniske trin, der kommer *før* dette — at splitte lyd op i talere, inden man forsøger at identificere dem — og [Whisper-backend-sammenligningen](/da/post/whisper-backend-sammenligning/) for transskriptionslaget under det hele.
