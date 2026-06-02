+++
title = "Fem måder at skaffe b-roll fra én tur — alt på en lokal GPU"
date = 2026-06-02
slug = "ai-broll-fem-maader-lokal-gpu"
description = "Auto-mining, img2img, dybde-parallakse, Stable Video Diffusion og slowmotion med optisk flow — fem måder at lave filmisk b-roll ud af ét onboard-klip, sammenlignet, alt kørende lokalt på et 12 GB RTX 4070 Ti."

[taxonomies]
tags = ["ai", "video", "b-roll", "diffusers", "stable-diffusion", "sdxl", "stable-video-diffusion", "depth-anything", "controlnet", "ffmpeg", "opencv", "nvidia"]

[extra]
summary = "B-roll er de klip, der giver en redigering luft — og onboard-POV fra ét kamera har ingen. Jeg prøvede fem måder at fabrikere det ud af én ATV-tur: CV-auto-mining af det rigtige materiale, generative stills (SDXL-Turbo → RealVisXL img2img), AI Ken Burns via Depth-Anything-V2-parallakse, ægte genereret bevægelse via Stable Video Diffusion og slowmotion med optisk flow. Alt lokalt på et 12 GB-kort. Her er hvad hver især dur til — og faldgruberne."
faq = [
  { q = "Skal man have en stor GPU til det her?", a = "Nej. Alt kørte på ét 12 GB RTX 4070 Ti. SDXL og RealVisXL img2img er der rigeligt plads til; Stable Video Diffusion kræver CPU-offload + forward chunking + en lille VAE-decode-chunk for at holde sig under 12 GB; Depth-Anything-V2-Small er bittelille; CV-auto-mining og slowmotion med optisk flow er ren CPU/ffmpeg." },
  { q = "Hvilken metode ser mest ægte ud?", a = "Til at matche rigtigt materiale vinder RealVisXL img2img ved lav strength — den bevarer det rigtige POV og palette og rydder bare op. SDXL-Turbo ved høj strength hallucinerer og forvrænger ('AI-smelt'). Vil du have ægte materiale, slår slowmotion med optisk flow alt, for det ER det rigtige materiale." },
  { q = "Er Stable Video Diffusion det værd frem for et Ken Burns-/parallakse-move?", a = "Kun når du har brug for bevægelse, som et stillbillede ikke kan fake. SVD opfinder ægte bevægelse, men klippene er korte (~2–3 s), bevægelsen er kun løst styrbar, og det er det tungeste at køre. Dybdebaseret parallakse er langt billigere og læser ofte lige så godt for et langsomt dolly-move." },
  { q = "Hvorfor img2img frem for ren text-to-image?", a = "Ren text-to-image gav generiske 'stock-skov'-billeder, der ikke matchede selve turen — forkert lys, forkert køretøj, intet POV. At seede img2img fra et rigtigt frame låser kompositionen, køretøjet i forgrunden og farvepaletten, så outputtet klipper sammen med de rigtige klip." },
  { q = "Hvad med ControlNet?", a = "ControlNet-Canny låser de rigtige kanter, så geometrien ikke kan forvrænge — fint til at stoppe smeltet — men ved standardindstillinger komponerede den scenen grønnere og mere stiliseret end kilden. Nyttig når du vil have strukturtro, men udseende-fleksibelt output." },
  { q = "Kan jeg se materialet?", a = "Klippene ligger på et privat galleri; dette indlæg viser repræsentative stills og sammenlignings-grids. Pointen er teknikkerne og koden — de gælder for ethvert onboard- eller ét-kamera-materiale." },
]
+++

**Kort fortalt —** B-roll er de klip, der giver en redigering luft, og onboard-POV fra ét kamera har præcis ingen. Jeg tog én ATV-tur og prøvede **fem** måder at fabrikere b-roll ud af den: (1) **auto-mine** de bedste rigtige frames med OpenCV, (2) **generér stills** og seed dem fra rigtige frames med **SDXL-Turbo → RealVisXL img2img**, (3) fake et filmisk kamera-move med **Depth-Anything-V2**-parallakse i 2,5D, (4) generér *ægte bevægelse* med **Stable Video Diffusion**, og (5) lav et **slowmotion**-klip af det rigtige materiale med optisk flow-interpolation. Alt kørte lokalt på et 12 GB RTX 4070 Ti. De supplerer hinanden — her er sammenligningen og fælderne.

## Problemet

Onboard-materiale — et GoPro/DJI på styret af en gokart eller en ATV — er ét langt førstepersons-shot. Det er fremragende til action, men en redigering har brug for *cutaways*: etableringsbilledet, naturen, den langsomme detalje, der giver seeren et åndedrag mellem de intense passager. Med ét kamera og intet B-kamera har du ingen. Så: kan man fabrikere troværdig b-roll bagefter, lokalt og gratis?

Jeg prøvede fem tilgange på én 11-minutters ATV-tur gennem nordisk skov og grusspor. Hver laver et kort, gradet klip; det interessante er afvejningerne.

## 1. Auto-mine det rigtige materiale (OpenCV)

Den billigste b-roll er den, du allerede har filmet uden at lægge mærke til det. En lille OpenCV-rutine sampler ~1.400 frames hen over turen og giver hver en score for **skarphed** (variansen af Laplacian), **farverigdom** (Hasler–Süsstrunk-målet), **eksponering** (afstand fra en mellemtone) og **bevægelses-stabilitet** (forskel mellem frames — lavt er godt til en stabil cutaway). Non-maximum suppression spreder derefter valgene ud, så du ikke får otte næsten identiske frames fra de samme 20 sekunder.

```python
score = 1.1*z(skarphed) + 1.0*z(farverig) + 0.8*z(eksponering) - 0.9*rystelse - 6.0*klipning
```

Ikke glamourøst, men øjeblikkeligt, gratis og 100 % ægte. Outputtet er din egen tur — bare de mest b-roll-værdige tre sekunder, du havde glemt, du filmede.

## 2. Generative stills, matchet til den rigtige tur

Her blev det interessant — og her gik det først galt.

**Forsøg ét: ren text-to-image.** SDXL-Turbo med prompts som *"filmisk diset skov i gyldent lys"* lavede smukke billeder, der lignede selve turen i ingenting. Forkert lys (solnedgang vs. den rigtige overskyede himmel), ingen ATV i billedet, intet POV. Flot stock-materiale af *en* skov, ikke *denne*.

**Forsøg to: img2img, seedet fra rigtige frames.** Ved at fodre et rigtigt frame ind som init-billede ved moderat denoising-strength bevares den rigtige komposition — den sorte ATV's styr og spejle i forgrunden, det græs-og-jord-spor, den overskyede palette — og detaljen regenereres. Nu klipper det sammen med det rigtige materiale. Men SDXL-**Turbo** ved strength ≈0,5 *smeltede* stadig: den hallucinerede ekstra instrumenter på instrumentbrættet og forvrængede styret. Det klassiske "AI-look".

**Forsøg tre: bedre modeller, lavere strength.** Jeg sammenlignede tre mindre-smeltende metoder på de samme frames:

![Rigtigt frame (øverst til venstre) mod tre generative metoder: SDXL img2img ved lav strength, ControlNet-Canny og RealVisXL. SDXL ved lav strength og RealVisXL forbliver tro mod kilden; ControlNet komponerer grønnere.](/img/ai-broll/compare-methods.avif)

- **SDXL-base, lav strength (0,30), 30 steps** — tro mod kilden, ingen smelt, men en anelse blød.
- **ControlNet-Canny + SDXL** — låser de rigtige kanter, så intet forvrænger, men komponerede scenen grønnere og mere stiliseret end kilden.
- **RealVisXL** (en fotorealistisk SDXL-finetune), img2img — vinderen: skarp, fotorealistisk, bevarer det rigtige POV og palette, ingen smelt.

![Et rigtigt frame og dets RealVisXL-img2img-regeneration. Samme POV, spejle, bagagebærer og spor; renere og skarpere.](/img/ai-broll/realvis-match.avif)

Læren: til at matche materiale betyder *basismodellen* og *denoising-strength* langt mere end prompten. En fotorealistisk checkpoint ved lav strength slår en prangende destilleret model hver gang.

## 3. AI Ken Burns — dybde-parallakse

Et stillbillede behøver ikke stå stille. **Depth-Anything-V2** estimerer et dybdekort for et frame på et godt stykke under et sekund; med dybde i hånden kan du rendere et 2,5D-kamera-move, hvor nære pixels flytter sig mere end fjerne, plus et blidt skub mod sporets forsvindingspunkt. Det læser som at køre fremad.

![Et stillbillede og dets estimerede dybdekort fra Depth-Anything-V2. Nær = lys, fjern = mørk; sporet trækker sig rent tilbage.](/img/ai-broll/depth-parallax.avif)

Hele renderingen er en baglæns `cv2.remap` med dybdevægtet forskydning, så den er hulfri og hurtig. Én fælde værd at notere: OpenCV's `remap` vil have `float32`-maps, og en enkelt løs Python-skalar i regnestykket opgraderer dem stille til `float64`, hvorefter `remap` fejler. Cast dem eksplicit tilbage til `float32`.

Det er den bedste indsats-per-effekt af de syntetiske muligheder: rigtigt indhold, ægte-udseende bevægelse, en lillebitte model. Den eneste begrænsning er, at store skub begynder at afsløre forvrængning ved dybde-spring — hold bevægelsen diskret.

## 4. Generativ video — Stable Video Diffusion

Vil du have bevægelse, som et stillbillede *ikke* kan fake, animerer **Stable Video Diffusion** (image-to-video) et stillbillede til ægte bevægelse — kameraet driver og skubber gennem scenen, parallakse og det hele, opfundet af modellen frem for forvrænget geometrisk.

![Et frame fra et Stable Video Diffusion-klip genereret ud fra et RealVisXL-still — kameraet har bevæget sig gennem scenen, sammenhængende.](/img/ai-broll/svd-motion.avif)

At seede SVD fra RealVisXL-stillsene giver genereret bevægelse, der stadig ligner turen. De ærlige forbehold: klippene er korte (~2–3 sekunder ved 25 frames), bevægelsen er kun løst styrbar (du nudger den med en "motion bucket", ikke en bane), og der er let kant-forvrængning. Det er også det tungeste her — modellen fylder ~9 GB og passer på et 12 GB-kort kun med CPU-offload, UNet forward-chunking og en lille VAE-decode-chunk:

```python
pipe.enable_model_cpu_offload()
pipe.unet.enable_forward_chunking()
frames = pipe(image, num_frames=25, decode_chunk_size=2,
              motion_bucket_id=110, noise_aug_strength=0.04).frames[0]
```

## 5. Filmisk slowmotion — rigtigt materiale, ingen AI

Den femte mulighed bruger slet ingen generativ model. Tag de auto-minede øjeblikke, sæt dem ned til 50 % fart med **bevægelseskompenseret optisk-flow-interpolation** (så slowmotion bliver glat, ikke hakkende duplikerede frames), stabilisér let, og læg en filmisk grade på. ffmpeg klarer det i én filterkæde:

```
minterpolate=mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:fps=60,setpts=2.0*PTS
```

Det er 100 % ægte, ser dyrt ud og er det mest "broadcast" af det hele. Interpolation kan udtvære meget hurtige kanter, men på naturklip er det rent.

## Hvilken vinder?

Ingen — de supplerer hinanden, og en rigtig redigering blander flere:

| Metode | Ægthed | Kontrol | Omkostning | Bedst til |
|---|---|---|---|---|
| 1 · Auto-mine (CV) | Ægte | Begrænset til det filmede | Øjeblikkelig | Ægte cutaways, gratis |
| 2 · Generative stills (RealVisXL) | Syntetisk | Høj (enhver scene) | Mellem (GPU) | Shots du aldrig filmede |
| 3 · Dybde-parallakse | Ægte + fake bevægelse | Kun bevægelse | Billig | At gøre et godt frame levende |
| 4 · SVD-video | Syntetisk | Løs bevægelse | Tungest (~9 GB) | Levende bevægelse uden materiale |
| 5 · Slowmotion (ægte) | 100 % ægte | Fart/grade | Mellem | Et dyrt klip af ægte øjeblikke |

Hvis jeg skulle levere ét b-roll-lag til den slags materiale, blev det **slowmotion (5) for den ægte, dyre følelse**, med **dybde-parallakse (3)** til at lægge bevægelse på fremtrædende frames, og **RealVisXL-stills (2)** kun dér, hvor jeg har brug for et etableringsbillede, der aldrig kunne filmes.

## Stak

- **GPU:** ét **RTX 4070 Ti, 12 GB**. Alt nedenstående passer.
- **Diffusion:** `diffusers` 0.38 — SDXL-base, **RealVisXL V4.0**, ControlNet-Canny-SDXL, **Stable Video Diffusion XT**.
- **Dybde:** `transformers` + **Depth-Anything-V2-Small**.
- **CV / samling:** OpenCV, NumPy og **ffmpeg** (`minterpolate`, `deshake`, AV1 NVENC, AVIF-stills).
- Et par fælder værd at huske: en distro-Python markeret **PEP 668 externally-managed** vil *stille* nægte `pip install` — brug et rigtigt virtualenv. Og `pgrep -f build.sh` matcher glad og gerne den *watcher-kommando*, der indeholder strengen, så stol ikke på den til at fortælle dig, at en rendering er færdig; tjek efter en levende `ffmpeg` i stedet.

## Hvorfor det findes

Det startede som "onboard-klippene mangler cutaways, og jeg har ét kamera". Det ærlige svar viste sig at være, at du ikke behøver et andet kamera — du skal *finde* den b-roll, du allerede har filmet (1, 5), og *fabrikere* resten med den mindste model, der gør arbejdet (3 før 2 før 4). Den mest prangende mulighed (generativ video) er den, jeg ville gribe til sidst. Den mindst prangende (at score frames med en Laplacian) er den, jeg ville gribe først.

Alt lokalt, alt på et kort, der koster mindre end en weekend med cloud-GPU. Ikke interessant før du har brug for det — og så er det præcis det, du har brug for.
