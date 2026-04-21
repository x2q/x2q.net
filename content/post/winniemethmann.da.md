+++
title = "winniemethmann.com — fra WordPress til Astro for en madfotograf"
date = 2026-04-19
slug = "winniemethmann-com-astro-portfolio"
description = "Flyt af winniemethmann.com fra WordPress til Astro. Tosproget portfolio (dansk/engelsk) med content collections, Sharp + AVIF-billedpipeline og 70 % mindre build."

[taxonomies]
tags = ["astro", "wordpress-migration", "static-site", "sharp", "avif", "i18n", "madfotografi", "portfolio"]

[extra]
summary = "En 10 år gammel WordPress-portfolio bygget om i Astro: content collections i stedet for et CMS, Sharp-drevne AVIF-billeder, tosproget i18n og et 70 % mindre build."
+++

**TL;DR —** [winniemethmann.com](https://winniemethmann.com) er portfolien for en dansk madfotograf og opskriftsudvikler. I et årti var det et WordPress-site. Jeg byggede det om oven på [Astro](https://astro.build) med **content collections** (typet Markdown) i stedet for et CMS, **Sharp + AVIF** til billedpipelinen og **Astros i18n-routing** (dansk som standard, engelsk på `/en/`). Build-tid: ~30 sekunder. Output: ~70 % mindre. Intet admin-panel, ingen plugin-opdateringer, ingen bot-prøvet login-endpoint.

## Hvorfor væk fra WordPress

For en portfolio, der opdateres et par gange om måneden, lavede WordPress for meget:

- **PHP-runtime og MySQL** for et site, der i praksis er statisk.
- **Titusindvis af plugins** til billedgallerier, kontaktformularer, SEO og caching — hver med sin egen opdaterings­kadence og sikkerhedshuller.
- **Et halvt-forket tema** med patches, ingen huskede hvorfor var der.
- **Et admin-login-endpoint**, der blev prøvet flere tusind gange i døgnet af bots.
- **Gentagne cache-kvaler**, hver gang CDN og plugins var uenige.

Konkret betød det at droppe WordPress:

- **Ingen admin-panel at holde patchet.** WordPress-core, plugin-opdateringer, tema-opdateringer — væk.
- **Ingen database.** Indholdet ligger som Markdown i repoet.
- **Ingen login-flade, bots kan prøve.** Der findes ikke en `/wp-admin/` længere.
- **~10× hurtigere sideindlæsning** uden cache-lag.
- **~70 % mindre samlet build-størrelse** — vi skiftede håndeksporterede JPEG'er ud med AVIF med fornuftige `srcset`-breakpoints.

Til gengæld mister du den ikke-tekniske redigering. I praksis betød det ingenting: ejeren var gladere for at redigere Markdown end for at kæmpe med WordPress' blok-editor.

## Hvorfor Astro

Jeg overvejede Hugo, 11ty, Next.js static export og SvelteKit. Astro vandt på tre konkrete punkter:

1. **Content collections.** En typet, skema-kontrolleret måde at beskrive et portfolio-projekt som en mappe med fotos plus lidt front-matter. Buildet fejler højlydt, hvis noget ikke overholder skemaet. Intet CMS nødvendigt.
2. **`<Image>`-komponenten.** Astros indbyggede billedpipeline håndterer AVIF + JPEG-fallback + `srcset` + `width`/`height` med en one-liner. Sharp er motoren under.
3. **Islands-arkitektur — ikke relevant her.** Siden har ingen interaktive komponenter, så den sender stort set ingen JavaScript.

## Content collections, ikke et CMS

Hvert portfolio-projekt er en mappe under `src/content/portfolio/` med et front-matter-skema:

```
src/content/portfolio/
├── 2024-kogebogs-editorial/
│   ├── index.mdx
│   ├── cover.jpg
│   ├── 01.jpg, 02.jpg, …
└── 2023-forarets-katalog/
    ├── index.mdx
    ├── cover.jpg
    └── 01.jpg …
```

`index.mdx`'s front-matter deklarerer titel, kategori, år og forsidebillede. Astro håndhæver skemaet ved build-tid via [`defineCollection`](https://docs.astro.build/en/guides/content-collections/) med et Zod-skema. Hvis et projekt mangler et forsidebillede eller har en dårlig kategori, fejler buildet.

Kategorier: **madfotografi, opskriftsudvikling, interiør- og haveproduktion, editorial, kogebøger og mode**. At tilføje et nyt projekt er `mkdir` + `cp *.jpg` + en kort YAML-front-matter-blok. Ingen admin-UI, ingen database-migration, ingen cache at invalidere.

## Billedpipeline: Sharp + AVIF

Madfotografi står og falder med billedkvalitet. Astros `<Image>`-komponent — drevet af [Sharp](https://sharp.pixelplumbing.com/) — genererer:

- **AVIF** som primært format. Stort set alle moderne browsere understøtter det nu (se [caniuse](https://caniuse.com/avif)).
- **JPEG**-fallback med matchende `srcset`-breakpoints (320, 640, 960, 1280, 1920 px).
- Eksplicitte `width`- og `height`-attributter, så der er nul layout shift, mens billederne loader.
- `loading="lazy"` til billeder under folden og `fetchpriority="high"` til heroet.

**Tal**: en typisk portfolio-side gik fra ~4,8 MB håndeksporterede JPEG'er til ~1,4 MB AVIF — omkring 70 % reduktion — uden synligt kvalitetstab i de viste størrelser.

## i18n — dansk som standard, engelsk på /en/

Astros i18n-routing sidder i `astro.config.mjs`:

```js
export default defineConfig({
  i18n: {
    defaultLocale: "da",
    locales: ["da", "en"],
    routing: { prefixDefaultLocale: false },
  },
});
```

Det giver:

- `/` for dansk (standard, uden præfiks).
- `/en/` for engelsk.
- Hvert indholds-entry deklarerer sit sprog via sin collection og filnavn.
- `<link rel="alternate" hreflang>` og sitemap genereres fra samme kilde.

Indlæg og portfolio-entries uden oversættelse dukker simpelthen ikke op i det andet sprogs routing — der er ingen forkert-sprog-404.

## Deployment og build

- **Output**: fuldt statisk, udgivet som almindelige filer bag Cloudflare.
- **Build-tid**: ~30 sekunder fra koldt cache, ~6 sekunder inkrementelt.
- **Ingen server, ingen database, ingen løbende kørselstid.**

## Målbare forbedringer

| Mål | WordPress (før) | Astro (efter) |
| --- | --- | --- |
| Build / deploy-tid | ikke relevant | ~30 s koldt, ~6 s varmt |
| Typisk sidestørrelse (portfolio-side) | ~4,8 MB | ~1,4 MB |
| Largest Contentful Paint | ~2,8 s | ~0,9 s |
| Time to Interactive | ~3,5 s | ~1,1 s |
| JS sendt til klienten | ~220 KB | ~0 KB |
| Plugins at holde patchet | 14 | 0 |

## Ofte stillede spørgsmål

### Kan en ikke-teknisk ejer stadig redigere siden?

Ja, til tekstændringer. At redigere Markdown i GitHubs web-editor er i praksis lettere end WordPress' blok-editor. For nye portfolio-projekter er workflowet: træk billeder ind i en mappe, skriv en lille front-matter-blok, commit. Er det for teknisk, kan man bolte en minimal admin på (Decap CMS, Sveltia CMS eller Keystatic).

### Hvad med SEO efter flytningen?

URL'er blev bevaret, hvor det var muligt. Manglende gamle stier omdirigeres via Cloudflare-regler. Sitemap genereres ved hvert build, og strukturerede data (`Person`, `ImageGallery`, `Article`) udsendes pr. side.

### Hvorfor Astro og ikke Hugo?

Hugo er hurtigere og simplere til ren blogging, men Astros typede content collections og førsteklasses `<Image>`-komponent vandt i det her tilfælde. Til [x2q.net](https://www.x2q.net) selv endte jeg senere med Zola — men til en portfolio med tung billedpipeline var Astro det rigtige valg.

### Hvordan holdes billederne organiseret?

Hvert portfolio-projekt har sin egen mappe. Git-repoet er CMS'et. `git log` fortæller, hvornår et billede blev tilføjet, og hvorfor.

### Er buildet deterministisk?

Ja. Samme input giver bit-for-bit identisk output. Sharp er pinned i `package.json`; det samme er Astro. CI kører på Node LTS.

Hvis du sidder med et WordPress-site, der laver langt mindre, end dets infrastruktur antyder, er Astro en eftermiddag værd.
