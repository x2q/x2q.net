+++
title = "Fra Launchy til Raycast: tastaturstarterens historie (2007 → 2026)"
date = 2026-06-07
slug = "historien-om-applikationsstartere-launchy-til-raycast"
description = "I 2007 demonstrerede jeg Launchy, en tastaturstyret app-starter til Windows. Historien om, hvor idéen kom fra — Quicksilver, LaunchBar — og hvor den endte: Alfred, Raycast, PowerToys og Cmd+K-kommandopaletten i hver eneste app."

[taxonomies]
tags = ["launchy", "quicksilver", "alfred", "raycast", "kommandopalette", "produktivitet", "windows", "macos", "linux", "tilbageblik"]

[extra]
summary = "Tilbage i 2007 optog jeg en kort demo af Launchy — en tastaturstyret applikationsstarter, der erstattede Windows' Start-menu med nogle få indtastede bogstaver. Den idé (tryk en genvejstast, skriv, fuzzy-match, start) begyndte på Mac'en med Quicksilver og LaunchBar, hoppede til Windows via Launchy, spredte sig til Linux og delte sig så i to: den voksede til produktivitetsplatforme som Alfred og Raycast, og den opløste sig i Cmd+K-kommandopaletten, der nu bor inde i næsten alle apps. Her er buen over 19 år."
faq = [
  { q = "Hvad var Launchy?", a = "En gratis, open source tastaturstyret applikationsstarter til Windows (senere på tværs af platforme), først udgivet af Josh Karlin omkring 2004. Du trykkede en genvejstast (Alt+Space), skrev nogle få bogstaver af et app- eller filnavn, og Launchy fuzzy-matchede og startede det — som erstatning for Start-menuen og skrivebordsikonerne. Den blev bredt beskrevet som 'Quicksilver til Windows'. Videoen fra 2007 viser den med 'Shiny'-skinnet." },
  { q = "Vedligeholdes Launchy stadig?", a = "Ikke rigtigt. Den aktive udvikling ebbede ud omkring 2010, og det oprindelige projekt er reelt gået i dvale (community-forks findes på GitHub). På Windows i 2026 ville du bruge PowerToys Command Palette, Flow Launcher eller Raycast i stedet — alle efterkommere af den samme idé." },
  { q = "Hvad er forskellen på en app-starter og en kommandopalette?", a = "Oprindelig ingen — begge er 'tryk en genvejstast, skriv, fuzzy-match, handl'. Starteren (Quicksilver, Launchy, Alfred, Raycast) er systemdækkende og starter apps/filer/handlinger. Kommandopaletten (VS Codes Ctrl+Shift+P, Cmd+K-baren i Slack/Linear/Notion/GitHub) er det samme mønster afgrænset til én app. Starteren kom først; kommandopaletten er den UX absorberet ind i alting." },
  { q = "Hvad skal jeg bruge i dag?", a = "macOS: Raycast (den moderne standard — udvidelser, udklipshistorik, vinduesstyring, AI) eller Alfred (engangskøb, lokal automatisering), med Spotlight indbygget. Windows: PowerToys Command Palette (officiel, gratis), Flow Launcher (open source) eller Raycast (Windows-beta kom sidst i 2025). Linux: Rofi, Ulauncher eller Albert. Terminal: fzf." }
]
+++

**TL;DR —** I 2007 lagde jeg en kort screencast op af **[Launchy](https://youtu.be/LBW1L2YOKks)** — en "tastaturstyret applikationsstarter", der lod dig fremkalde ethvert program på Windows ved at trykke en genvejstast og skrive nogle få bogstaver, i stedet for at lede i Start-menuen. Det mønster — **genvejstast → skriv → fuzzy-match → start** — blev født på Mac'en (Quicksilver, LaunchBar), kom til Windows med Launchy, spredte sig til Linux og gjorde så to ting på én gang: den modnedes til fulde produktivitetsplatforme (**Alfred**, så **Raycast**), og den opløste sig i **Cmd+K-kommandopaletten**, der nu bor inde i næsten alle apps, du bruger. Her er buen over 19 år.

> En pendant til de andre tidskapsel-indlæg her — som [Xming på Windows XP → WSLg](/da/post/linux-gui-apps-paa-windows-xming-til-wslg/) og [25 års Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/). En gammel screencast, og hvad idéen voksede til.

## Opsætningen, dengang

[Videoen](https://youtu.be/LBW1L2YOKks) ("Shiny Windows Application Launcher" — *Shiny* var et Launchy-skin) viser arbejdsgangen fra 2007. Du installerer **Launchy**, den indekserer din Start-menu, og fra da af:

1. Tryk **Alt+Space**. En lille gennemsigtig boks dukker op midt på skærmen.
2. Skriv nogle få bogstaver — `fir` for Firefox, `wor` for Word.
3. Launchy fuzzy-matcher mod alt, den har indekseret, og viser det bedste hit.
4. Tryk **Enter**. Appen starter. Boksen forsvinder.

Ingen mus, ingen Start-menu, ingen skrivebordsikoner. Efter en uge kendte dine fingre tre-bogstavs-præfikset for hver app, du brugte. Launchy — skrevet af Josh Karlin og open-sourcet — blev udtrykkeligt markedsført som **"Quicksilver til Windows"**, og den sammenligning er nøglen til hele historien.

## Hvor idéen faktisk kom fra

Launchy opfandt ikke tastaturstarteren — den bragte en **Mac**-idé til Windows:

- **LaunchBar** (Objective Development) — bedstefaderen, med rødder på **NeXTSTEP i 1990'erne**, genfødt på Mac OS X. Skriv en forkortelse, få tingen.
- **Quicksilver** (Nicholas Jitkoff / Blacktree, ~2003) — den legendariske, nærmest mystiske Mac-starter. Ikke bare "start en app", men en verbum-navneord-grammatik: vælg en *ting*, vælg en *handling*, vælg et *mål*. Den definerede genren og inspirerede en hel generation (den blev open-sourcet i 2007, da skaberen tog til Google).
- **Spotlight** (Mac OS X Tiger, 2005) — Apple bagte søgning ind i styresystemet, hvilket er der, de fleste almindelige brugere mødte "skriv bare for at finde ting"-idéen.

Launchy (2004→) var Windows-svaret på alt det, og videoen fra 2007 er et øjebliksbillede af den på toppen.

## Et hurtigt overblik — 19 år med startere

| Æra | macOS | Windows | Linux | Mønsteret |
|-----|-------|---------|-------|-----------|
| **~2003–05** | Quicksilver, LaunchBar, Spotlight | Start-menu (Vista får søgning, 2007) | — | Starteren er en Mac-power-user-ting |
| **2007 (videoen)** | Quicksilver på toppen | **Launchy** ("Quicksilver til Windows") | — | Tastaturstarteren krydser til Windows |
| **~2008–10** | Quicksilver stagnerer → **Alfred** (2010) | Launchy topper, så sløver | **GNOME Do**, Katapult | Starteren bliver mainstream-power-user |
| **~2011–15** | Alfred + Powerpack dominerer | Wox (2014) | Synapse, Albert | **Kommandopaletten** dukker op (Sublime, så VS Code) |
| **~2016–20** | **Raycast** grundlægges (2020) | **PowerToys Run** (2020), Flow Launcher | Rofi, Ulauncher | Cmd+K spreder sig til hver web-app |
| **2026 (i dag)** | Raycast dominerer; Spotlight + Apple Intelligence | PowerToys **Command Palette**; Raycast (beta) | Rofi / Ulauncher / Albert | Starteren = AI-drevet kommando-hub |

## Hvad der ændrede sig

**1. Starteren blev en platform.** Launchy startede apps og filer. **Alfred** (2010) tilføjede *workflows* — kæd handlinger sammen, kør scripts, udklipshistorik, snippets — og blev Mac-standarden i et årti. Så genopbyggede **Raycast** (2020) idéen som en native, udvidelig platform: en udvidelsesbutik, vinduesstyring, udklipshistorik, snippets, lommeregnere og nu indbygget **AI**. Den ydmyge start-boks blev til stedet, hvor power-brugere kører halvdelen af deres dag. Raycasts **Windows-beta kom sidst i 2025** og lukkede ringen tilbage til der, hvor Launchy startede.

**2. Windows blev ved med at genopfinde den.** Launchy ebbede ud efter ~2010. **Wox** (open source, 2014) bar faklen videre og affødte **Flow Launcher** (en Wox-fork med en plugin-markedsplads og AI-plugins). Microsoft selv udgav **PowerToys Run** (2020, `Alt+Space` — et vidende nik til Launchy), nu afløst af **PowerToys Command Palette**. Mønsteret er så åbenlyst godt, at OS-producenten adopterede det.

**3. Linux havde altid sin egen.** **GNOME Do** (2008) var den tidlige Quicksilver-lignende; i dag er det **Rofi** og **dmenu** (minimale, scriptbare, elskede af tiling-WM-brugere), **Ulauncher** og **Albert**. Samme muskelhukommelse, andet økosystem.

**4. Det største skift: starteren opløste sig i hver app.** Det definerende træk i det seneste årti er ikke en bedre starter — det er, at *kommandopaletten* blev en universel UX-primitiv. **Sublime Text** (~2011) og så **VS Code** (`Ctrl/Cmd+Shift+P`) gjorde "tryk en genvejstast, skriv en kommando" til måden, man styrer en editor på. Så dukkede **Cmd+K** op overalt: Slack, Linear, Notion, GitHub, Figma, Vercel, Stripe, din browser. Tastaturstarteren holdt op med at være en separat app, du installerer, og blev en kontrol indbygget i selve softwaren. I terminalen er **fzf** (2013) den samme idé destilleret til én fuzzy-finder-binær.

**5. Så åd AI'en kommandobaren.** Den nyeste drejning: boksen, du skriver i, taler nu med en model. **Raycast AI**, Flow Launchers AI-plugins, **Spotlight + Apple Intelligence**, Windows **Copilot**. "Genvejstast → skriv → fuzzy-match → handl" bliver til "genvejstast → spørg → starteren regner handlingen ud". Launchys lille gennemsigtige boks var larvestadiet for nutidens AI-kommandobar.

## Hvad du skal bruge i dag

**macOS** — **[Raycast](https://www.raycast.com/)** er den moderne standard: start, udklipshistorik, vinduesstyring, snippets, en udvidelsesbutik og AI i én genvejstast. **[Alfred](https://www.alfredapp.com/)** er alternativet, hvis du foretrækker et engangskøb og lokal automatisering. Spotlight er indbygget og efterhånden ret god.

**Windows** — **PowerToys Command Palette** (officiel, gratis, følger med [PowerToys](https://learn.microsoft.com/en-us/windows/powertoys/)), **[Flow Launcher](https://www.flowlauncher.com/)** (open source, plugin-markedsplads) eller **Raycast** (Windows-beta siden sidst i 2025). Par hvilken som helst af dem med **[Everything](https://www.voidtools.com/)** til lynhurtig filsøgning.

**Linux** — **Rofi** eller **dmenu** til den scriptbare/tiling-flok, **Ulauncher** eller **Albert** til en venligere GUI.

**Terminal** — **[fzf](https://github.com/junegunn/fzf)**. Pipe hvad som helst ind i den, fuzzy-find, handl. Starter-idéen i 30 linjers muskelhukommelse.

## Pointen

Launchy-klippet fra 2007 ser gammeldags ud — en gennemsigtig boks, et Shiny-skin, tre bogstaver og Enter. Men idéen i det vandt fuldstændigt. Den begyndte som en Mac-kuriositet, Launchy bragte den til Windows, Linux samlede den op, og derfra gik den i to retninger på én gang: *opad* til produktivitetsplatforme som Raycast, og *sidelæns* ind i hver app som Cmd+K-kommandopaletten. I dag bruger du den idé fra 2007 snesevis af gange om dagen — du installerer den bare ikke længere, for den er overalt. Og boksen er begyndt at tænke.

## FAQ

### Hvad var Launchy?

En gratis, open source tastaturstarter til Windows (senere på tværs af platforme), først udgivet af Josh Karlin omkring 2004. Genvejstast, skriv nogle få bogstaver, fuzzy-match, start — "Quicksilver til Windows". Videoen fra 2007 viser den på Shiny-skinnet.

### Vedligeholdes Launchy stadig?

Nej — udviklingen ebbede ud omkring 2010, og den er reelt gået i dvale. På Windows i dag: brug PowerToys Command Palette, Flow Launcher eller Raycast.

### App-starter vs. kommandopalette — hvad er forskellen?

Samme mønster, anden afgrænsning. En starter (Quicksilver, Launchy, Alfred, Raycast) er systemdækkende; en kommandopalette (VS Codes `Ctrl+Shift+P`, `Cmd+K`-baren i Slack/Linear/GitHub) er den samme UX inde i én app. Starteren kom først; paletten er den absorberet ind i alting.

### Hvad skal jeg bruge i 2026?

macOS: Raycast eller Alfred. Windows: PowerToys Command Palette, Flow Launcher eller Raycast. Linux: Rofi, Ulauncher eller Albert. Terminal: fzf.

## Opsummering

- Tastaturstarteren — **genvejstast → skriv → fuzzy-match → start** — begyndte på Mac'en (**LaunchBar**, **Quicksilver**) og nåede Windows via **Launchy**, som min [video fra 2007](https://youtu.be/LBW1L2YOKks) demonstrerer.
- Den voksede *opad* til platforme: **Alfred** (2010) → **Raycast** (2020), nu AI-drevet, med en **Windows-beta** fra sidst i 2025.
- Windows blev ved med at genopfinde den: **Wox** → **Flow Launcher**, og Microsofts **PowerToys Run → Command Palette**.
- Den spredte sig også *sidelæns* ind i hver app som **Cmd+K-kommandopaletten** (Sublime/VS Code → Slack, Linear, Notion, GitHub) og ind i terminalen som **fzf**.
- Idéen fra 2007 er nu overalt — og i stigende grad en AI-kommandobar.
