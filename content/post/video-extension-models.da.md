+++
title = "Forlæng videoklip med AI på en 12 GB GPU — seks modeller sammenlignet"
date = 2026-06-07
slug = "video-forlaengelse-modeller-12gb-gpu"
description = "Wan2.2 (5B og 14B), Stable Video Diffusion, LTX-Video og CogVideoX — seks billede-til-video-modeller til at forlænge et kort klip, kørt lokalt på et 12 GB RTX 4070 Ti. Den egentlige kamp er den offload-strategi, der får en 14B-model — og 720p — til at passe i 12 GB."

[taxonomies]
tags = ["ai", "video", "image-to-video", "wan", "ltx-video", "cogvideox", "stable-video-diffusion", "diffusers", "gguf", "offloading", "nvidia"]

[extra]
summary = "Du har et kort maskine-/action-klip og vil have det længere. At 'forlænge' et klip er i virkeligheden billede-til-video: tag sidste frame og generér en troværdig fortsættelse. Jeg gav det samme klip til seks modeller — Wan2.2-TI2V-5B, Wan2.2-I2V-A14B (GGUF), Stable Video Diffusion, LTX-Video og CogVideoX-5B — alt på ét 12 GB RTX 4070 Ti. Det interessante er ikke hvilken der ser bedst ud, men de hukommelses-tricks der overhovedet får en 14B-videomodel (og 720p) til at passe i 12 GB."
faq = [
  { q = "Kan man virkelig køre en 14B-videomodel på en 12 GB GPU?", a = "Ja — kvantiseret til GGUF Q4 (~9 GB pr. ekspert) og med den rette offloading. Den officielle fp16 Wan2.2-14B vil have ~24-35 GB og passer ikke. Tricket er aldrig at holde hele modellen residerende: model-niveau CPU-offload giver 640-720p i korte længder, og group-offload (der streamer transformeren blok for blok) sænker toppen til under 2 GB, så opløsning bliver gratis og tid bliver grænsen." },
  { q = "Hvilken model bør jeg faktisk bruge på 12 GB?", a = "Til korte forlængelser: LTX-Video — bedste balance mellem hastighed og kvalitet (~3 min, dynamisk bevægelse, prompt-styret). Til ægte 720p: Wan2.2-I2V-14B med group-leaf-offload (langsom, ~20 min, men skarp). SVD er hurtigst, men dens bevægelse er ambient (ingen prompt-kontrol). CogVideoX-5B giver det længste og blødeste klip, men tager ~en time pr. klip her." },
  { q = "Hvorfor løb alt tør for hukommelse?", a = "To gengangere. For det første fylder T5/umT5-tekstenkoderen ~11 GB alene og OOM'er et 12 GB-kort i det øjeblik model-offload flytter den til GPU'en — løs det ved at præ-enkode prompten på CPU (i fp32; bf16 på CPU er ubrugeligt langsomt) og smide enkoderen ud. For det andet er det ved højere opløsninger aktiverings-hukommelsen, ikke vægtene, der eksploderer — færre frames eller group-offload løser det." },
  { q = "Virker GGUF med diffusers-offloading?", a = "GGUF + model-niveau CPU-offload: ja. GGUF + sequential offload: nej — accelerate flytter parametre via en meta-enhed og GGUF-kvant-typen mistes (KeyError). GGUF + group-offload: ja, og det er sådan man når 720p. Almindelige (ikke-GGUF) modeller som LTX er glade for sequential offload." },
  { q = "Hvorfor ser AI-fortsættelsen stadig lidt fake ud?", a = "På 12 GB er den bindende begrænsning opløsning. 5B'en ved 640 px ser blødest ud; 14B'en ved 720p er markant skarpere. Det resterende gab — høj opløsning OG flere sekunders længde samtidig — er det ene et 12 GB-kort ikke kan give; det kræver en 24 GB+ GPU eller cloud." },
  { q = "Skal jeg bruge ComfyUI?", a = "Nej. Alt her kører via Hugging Face diffusers i et Python-script, inklusive GGUF Wan-eksperterne via from_single_file. ComfyUI dur også, men diffusers er langt nemmere at styre headless og at batche." },
]
+++

**Kort fortalt —** At "forlænge" et videoklip er i virkeligheden **billede-til-video**: tag sidste frame, lad en model generere en troværdig fortsættelse, og sæt dem sammen. Jeg kørte det samme maskine-klip gennem **seks** I2V-modeller på ét **12 GB RTX 4070 Ti**: Wan2.2-TI2V-5B, Wan2.2-I2V-A14B (GGUF Q4, ved 640 px og ved 720p), Stable Video Diffusion, LTX-Video og CogVideoX-5B. Pointen er ikke vinderen — men at en **14B**-model og **720p** begge passer i 12 GB, når man får **offload-strategien** rigtig.

## Opgaven

Jeg havde en stak korte klip af skovmaskiner — en gravemaskine, en flishugger, en gummiged — og ville have dem et par sekunder længere. Der er ikke mere materiale; den eneste måde at forlænge på er at *opfinde* det. Moderne billede-til-video-modeller gør netop det: de betinges på et startbillede (her klippets sidste frame) og en tekst-prompt og hallucinerer bevægelse fremad. Sæt den ægte hale sammen med den genererede fortsættelse, og du har et længere klip.

Alt nedenfor kørte lokalt på ét 12 GB RTX 4070 Ti med 125 GB system-RAM (RAM'en betyder noget — det er der de offloadede vægte bor).

## Det egentlige problem: at få store videomodeller ned i 12 GB

Billed-diffusion er tilgivende på VRAM. Video-diffusion er ikke: man denoiser et 3D-latent (frames × højde × bredde), og de nyeste kvalitetsmodeller er 5B-14B parametre. Tre ting bed hele tiden:

1. **Tekstenkoderen er enorm.** Wan, LTX og CogVideoX bruger alle en T5-XXL / umT5-XXL-enkoder på ~11 GB alene. I det øjeblik model-offload flytter den til et 12 GB-kort for at enkode prompten, OOM'er du — før videomodellen overhovedet kører.
2. **Aktiveringer, ikke vægte, eksploderer ved højere opløsning.** En 9 GB-transformer kan sidde på kortet fint; det er attention-aktiveringerne over (frames × tokens), der løber over, når man presser forbi ~480p.
3. **Kvantisering hjælper på disk og lidt på VRAM, men spiller dårligt sammen med visse offload-tilstande.** GGUF Q4 skrumper en 14B-ekspert til ~9 GB, men hvordan man offloader den betyder noget.

Det der fik det hele til at virke:

- **Præ-enkod prompten på CPU, og smid så enkoderen ud.** Beregn tekst-embeddings med T5 på CPU'en *i fp32* (bf16-matmuls på CPU er ulideligt langsomme — det ligner at den hænger), cast resultatet til bf16, sæt `text_encoder = None`, og start så først videomodellen. Nu rører de 11 GB enkoder aldrig GPU'en.
- **Vælg offload-tilstand pr. model:**
  - `enable_model_cpu_offload()` — flytter hele del-modeller ind/ud af GPU'en. Hurtig, men én model skal kunne være der ad gangen (så den begrænser opløsning/længde).
  - `enable_sequential_cpu_offload()` — streamer del-moduler. Lavere top-VRAM, langsommere. Glimrende til ikke-kvantiserede modeller (LTX, CogVideoX), men **bryder GGUF** (accelerates meta-enhed-trin mister kvant-typen).
  - `apply_group_offloading(..., offload_type="leaf_level", use_stream=True)` — streamer transformeren blad for blad. Det er hemmelige våben.

## Wan2.2: fra "fake" 5B til ægte 720p

Jeg startede med **Wan2.2-TI2V-5B** (den lille, forbrugervenlige). Den kører nemt med model-offload og laver sammenhængende bevægelse, men ved de ~640 px kortet tillader, ser den blød ud — den klassiske plastik-agtige "AI-video"-fornemmelse.

At gå op til **Wan2.2-I2V-A14B** krævede kvantisering. Den officielle 14B er to eksperter (high-noise + low-noise) og vil have 24-35 GB i fp16. GGUF Q4-versionen er ~9 GB pr. ekspert, og diffusers kan loade hver via `WanTransformer3DModel.from_single_file(..., quantization_config=GGUFQuantizationConfig(...))` — man skal bare have `gguf`-pakken, ellers kan filen ikke læses. Med model-offload + CPU-prompt-tricket kører 14B'en ved 640 px, og bevægelsen er synligt bedre (flishuggeren, et kaotisk nærbillede som 5B'en lavede til grød, kom ud sammenhængende).

Så det egentlige mål: **720p**. Model-offload ved 1280×720 topper ved ~11,7 GB — den passer, men kun ~13 frames før aktiveringerne løber over. Gennembruddet var **group-leaf-offloading**: stream transformeren ét bladmodul ad gangen, så næsten intet sidder på GPU'en. Top-VRAM ved 1280×720: **1,9 GB**. Kortet er pludselig tomt og opløsning er gratis; prisen er hastighed (blad-streaming er langsomt, ~20 min pr. klip). Men det er ægte, skarp 720p på et 12 GB-kort.

```python
from diffusers.hooks import apply_group_offloading
for t in (pipe.transformer, pipe.transformer_2):  # begge støj-eksperter
    apply_group_offloading(t, onload_device=torch.device("cuda"),
                           offload_device=torch.device("cpu"),
                           offload_type="leaf_level", use_stream=True)
pipe.vae.enable_tiling()
```

## De andre tre

- **LTX-Video** (2B). Hurtig og, til korte forlængelser, den bedste af bundtet — dynamisk bevægelse (gravemaskinen kaster jord), prompt-styret, ~3 min pr. klip ved 768×512. Kræver `sentencepiece` til sin T5-tokenizer, og `sequential` offload, fordi den T5 er den samme 11 GB OOM-fælde.
- **Stable Video Diffusion** (img2vid-xt). Veteranen. Kører ved 1024×576 med model-offload + `unet.enable_forward_chunking()`, og den er hurtig — men SVD har **ingen tekst-prompt**, så dens bevægelse er *ambient* (en blid glidning, vind i træerne) frem for den styrede action du bad om. God til filmiske cutaways, forkert værktøj til "bliv ved med at grave".
- **CogVideoX-5B-I2V**. Kvalitets-overraskelsen: det længste og blødeste klip (6 s, 49 frames ved 720×480), sammenhængende hele vejen. Hagen er hastigheden — med sequential offload + VAE-tiling tager det groft sagt **en time pr. klip** på 12 GB, hvilket gør den upraktisk her, selvom outputtet er smukt.

## Resultattavlen

| Model | Parametre | Passer i 12 GB via | Output | Hastighed | Dom |
|---|---|---|---|---|---|
| LTX-Video | 2B | sequential offload | 768×512 | ~3 min | **Bedst til korte forlængelser** — hurtig, dynamisk |
| Wan2.2-I2V-14B @ 720p | 14B (Q4) | **group-leaf-offload (1,9 GB!)** | 1280×720 | ~20 min | **Ægte 720p på 12 GB** — skarpest |
| Wan2.2-I2V-14B | 14B (Q4) | model-offload + CPU-prompt | 640×384 | ~8 min | God bevægelse, især de svære tilfælde |
| CogVideoX-5B-I2V | 5B | sequential + VAE-tiling | 720×480 | ~1 time | Længst/blødest, men upraktisk langsom her |
| Stable Video Diffusion | ~1,5B | model-offload + chunking | 1024×576 | ~2 min | Hurtig og ren, men bevægelsen er ambient |
| Wan2.2-TI2V-5B | 5B | model-offload | 640×384 | ~3 min | Den bløde, "fake"-agtige baseline |

## Hvad jeg faktisk ville gøre

På et 12 GB-kort: grib **LTX-Video** til hurtige, styrede forlængelser, og **Wan2.2-14B + group-offload** når du specifikt har brug for **720p** og kan vente. SVD bliver i kassen til ambient cutaways. CogVideoX er smuk, men man ville ønske sig en større GPU for at bruge den i praksis.

Og den ærlige begrænsning: det der stadig læses som "AI" er mest **opløsning**. Group-offload køber dig 720p *eller* et 12 GB-kort køber dig længde — ikke begge på én gang. Høj opløsning *og* flere sekunder er den ene mur et 12 GB-kort ikke kan bestige; det er hvad et 24 GB+ kort (eller en time i skyen) er til. Alt andet — selv en 14B-model ved 720p — viste sig at være et spørgsmål om offloading, ikke hestekræfter.
