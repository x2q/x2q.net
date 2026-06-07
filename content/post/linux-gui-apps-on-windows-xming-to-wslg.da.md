+++
title = "Fra Xming på Windows XP til WSLg: 18 år med Linux-GUI-apps på Windows (2026)"
date = 2026-06-07
slug = "linux-gui-apps-paa-windows-xming-til-wslg"
description = "Et gammelt klip af Xming, der viser gedit på Windows XP, og hvad der er sket siden: VcXsrv, Wayland og WSLg kører nu Linux-GUI-apps på Windows indbygget — uden at installere en X-server."

[taxonomies]
tags = ["x11", "xming", "wsl", "wslg", "wayland", "ssh", "vcxsrv", "linux", "windows", "tilbageblik"]

[extra]
summary = "For år tilbage optog jeg Xming — en X11-server til Windows — der viste et fjernt Linux-gedit-vindue på et Windows XP-skrivebord over SSH. Det trick (installér en X-server, forward X11 over SSH) var sådan, man kørte Linux-GUI-apps på Windows i to årtier. I 2026 gør man det knap nok: WSLg leverer en Wayland-/X-server inde i Windows, så du bare `apt install`'er en Linux-app, og den åbner. Her er buen fra dengang til nu — og hvad du faktisk skal bruge i dag."
faq = [
  { q = "Virker SSH X11-forwarding stadig i 2026?", a = "Ja. `ssh -X user@host` (eller `-Y` til betroet forwarding) forwarder stadig X11 til en kørende X-server — Xming, VcXsrv, XQuartz på en Mac eller X-serveren inde i WSLg. Det er uændret i 20+ år. Det er bare langsomt over latency, fordi X11-protokollen er snakkesalig, hvilket er grunden til, at xpra, waypipe eller en remote-desktop-protokol som regel slår det i dag." },
  { q = "Vedligeholdes Xming stadig?", a = "På sin vis. Colin Harrison udgiver stadig builds (7.7.x i 2026), men de nuværende udgaver er donations-låst på straightrunning.com; den sidste frit tilgængelige offentlige version på SourceForge frøs ved 6.9.0.31 tilbage i 2007 — æraen for det originale Windows XP-klip. Vil du have en gratis, aktivt bygget X-server til Windows, er VcXsrv det normale valg nu." },
  { q = "Skal jeg stadig bruge en X-server som Xming eller VcXsrv?", a = "Kun til det klassiske tilfælde: at forwarde en GUI-app fra en fjern Linux-maskine til et Windows-skrivebord over SSH, eller at køre X-apps fra en ikke-WSLg-distro. Er dit Linux WSL2 på Windows 11 (eller Windows 10 21H2+), leverer WSLg allerede en Wayland- + X-server, så lokale Linux-GUI-apps åbner uden ekstra software." },
  { q = "Hvad er forskellen på X11 og Wayland her?", a = "X11 er den årtier gamle display-protokol med netværkstransparens indbygget — det var det, der gjorde `ssh -X` og Xming muligt. Wayland er dens moderne afløser på Linux; den er ikke netværkstransparent af design, så fjern-visning bruger waypipe eller RDP i stedet. WSLg kører Weston (en Wayland-compositor) med XWayland, så både Wayland- og gamle X11-apps virker." },
  { q = "Jeg vil bare redigere filer på en fjern maskine — skal jeg bruge noget af det her?", a = "Sandsynligvis ikke. At forwarde et helt editor-vindue gav mening i 2007; i dag ville du bruge VS Codes Remote-SSH, montere fjern-filsystemet med sshfs eller bare redigere over en almindelig SSH-session. At forwarde en GUI-app er nu undtagelsen, ikke standarden." }
]
+++

**TL;DR —** At køre en Linux-GUI-app på en Windows-maskine plejede at betyde, at man installerede en **X-server** (Xming, senere VcXsrv), pegede en SSH-session på den med `ssh -X` og så et fjernt `gedit`-vindue tegne sig selv op på Windows-skrivebordet. Jeg har [en gammel skærmoptagelse af præcis det](https://www.youtube.com/watch?v=P3hHsfdFusw) — Xming, der sætter gedit på **Windows XP**. Atten år senere gider man stort set ikke: **WSLg** leverer en Wayland- + X-server *inde i* Windows, så en Linux-app installeret i WSL2 bare åbner som ethvert andet vindue. Dette indlæg trækker buen op — X11-forwarding → VcXsrv → Wayland → WSLg — og hvad du faktisk skal bruge i 2026.

> Det her er en pendant til de andre "dengang vs. nu"-noter på bloggen — som [lokal tale-til-tekst, der afløser cloud-Speech-API'en](/post/local-speech-to-text-whisper-cpp/) og [25 års Wi-Fi-sikkerhed](/da/post/hack-traadloest-netvaerk/). Samme form: noget, der var fummelt i XP-æraen, er nu indbygget.

## Opsætningen, dengang

[Videoen](https://www.youtube.com/watch?v=P3hHsfdFusw) viser det kanoniske trick fra midten af 00'erne. Delene:

- **Xming** — en gratis X11-server til Windows (en port af X.Org-serveren). Den kørte i Windows' systembakke og leverede et *display*, som X-klienter kunne tegne til.
- **En SSH-klient** — som regel PuTTY med "Enable X11 forwarding" sat til, eller `ssh -X` fra Cygwin.
- **En fjern Linux-maskine**, der kørte selve appen (`gedit`, en editor) uden noget lokalt vindue af sin egen.

Flowet: SSH forbinder til Linux-værten, værten sætter `$DISPLAY` til at tunnelere X11 tilbage gennem den krypterede SSH-kanal, appen tegner til Xming, og et Linux-vindue dukker op på Windows XP. Applikationen kører udelukkende på fjern-maskinen; kun *pixels og input-events* rejser. Det virkede, fordi **X11 var netværkstransparent fra dag ét** — en designbeslutning fra 1984, der modnede til en reelt nyttig egenskab.

Det var smart, og det var også langsomt og skrøbeligt: hver menu og genoptegning var en round-trip, så over andet end et LAN føltes det som at vade gennem sirup.

## Et hurtigt overblik — 18 år med Linux-GUI på Windows

| Æra | Sådan gjorde du | Hvad drev displayet | Smertepunkter |
|-----|------------------|---------------------|---------------|
| **~2007 (XP)** | `ssh -X` / PuTTY → Xming | Xming X-server i bakken | Manuel install, snakkesalig X11, laggy over WAN |
| **~2012** | Samme, eller X over VNC | Xming / Xming-mesa, VcXsrv kommer (2011) | X-server stadig en separat bevægelig del |
| **~2017** | VcXsrv + WSL1 | VcXsrv, sæt `DISPLAY=localhost:0` | WSL1-finurligheder, font-/clipboard-fejl |
| **~2021** | WSL2 + manuel X-server, *eller* WSLg-preview | VcXsrv / X410, så WSLg | Overgang; manuel `DISPLAY`-eksport stadig normal |
| **2026 (i dag)** | WSLg, indbygget | Weston (Wayland) + XWayland, automatisk | Stort set ingen — `apt install`, appen åbner |

## Hvad der faktisk ændrede sig

**1. X-serveren holdt op med at være din at administrere.** I ~25 år var X-serveren noget, *du* installerede og passede på Windows. Med [WSLg](https://github.com/microsoft/wslg) — annonceret ved Microsoft Build 2021, nu standard på Windows 11 og Windows 10 21H2+ — bundter Microsoft en hel display-stak ind i en system-distro: en **Weston** Wayland-compositor, **XWayland** til gamle X11-apps, en PulseAudio-server til lyd og et RDP-link, der tegner vinduerne op på Windows-skrivebordet. Du installerer en Linux-GUI-app i WSL2, og den åbner. Ingen `DISPLAY`, intet bakke-ikon, ingen PuTTY-afkrydsning.

```bash
# Inde i WSL2 på Windows 11 — ingen X-server at installere:
sudo apt update && sudo apt install -y gedit
gedit            # et rigtigt Linux-gedit-vindue åbner på Windows
```

**2. Wayland afløste X11 på Linux-siden.** Protokollen, der gjorde det oprindelige trick muligt, er på vej ud. Moderne Linux-skriveborde defaulter til **Wayland**, som — i modsætning til X11 — *ikke* er netværkstransparent. Så "bare forward det over SSH"-reflekset passer ikke længere rent; det Wayland-native svar på fjern-visning er [`waypipe`](https://gitlab.freedesktop.org/mstoeckl/waypipe), og XWayland holder gamle X11-apps kørende i mellemtiden.

**3. Xming selv visnede til en betalt niche.** Xming lever stadig — Colin Harrison udgav 7.7.x-builds så sent som januar 2026 — men den frit tilgængelige offentlige udgave frøs ved **6.9.0.31 i 2007**; nyere versioner er donations-låst. Den gratis, aktivt vedligeholdte fakkel gik videre til **[VcXsrv](https://github.com/marchaesen/vcxsrv)**, en open source-X-server bygget fra nuværende X.Org-kilder. (Bemærk: VcXsrv droppede Windows XP-understøttelse for længst — den æra er reelt forbi.)

**4. Selve *grunden* fordampede stort set.** I 2007 forwardede man en editor, fordi det var smertefuldt at redigere fjern-filer på nogen anden måde. I 2026 ville du gribe efter **VS Codes Remote-SSH**, [montere fjern-filsystemet med sshfs](/post/mount-remote-filesystem-sshfs/) eller bare arbejde i en terminal over [nøglebaseret SSH](/post/ssh-key-login-without-password/). At forwarde et enkelt GUI-vindue er nu undtagelsen, ikke arbejdsgangen.

## Hvad du skal bruge i dag

**Du er på WSL2 (Windows 11 / Win10 21H2+):** gør ingenting. WSLg er der allerede. `apt install` appen og kør den. Tjek med:

```bash
echo $WAYLAND_DISPLAY     # wayland-0   → WSLg er aktiv
echo $DISPLAY             # :0          → XWayland til gamle X11-apps
```

**Du skal forwarde en GUI-app fra en fjern Linux-server til Windows:** installér **VcXsrv**, start den (multiple-windows-tilstand, slå adgangskontrol fra — kun på et betroet netværk), og:

```bash
ssh -X user@server        # -Y til betroet forwarding, hvis -X er blokeret
xterm                     # eller hvilken GUI-app som helst — den tegner til VcXsrv
```

Det er *præcis* den samme mekanisme som i Xming-klippet, bare med en moderne X-server. Det virker stadig. Det er stadig snakkesaligt over latency.

**Du vil have fjern-GUI, der ikke kravler over WAN:** drop rå X11. Brug [`xpra`](https://github.com/Xpra-org/xpra) ("screen for X" — apps overlever afbrydelser, og det komprimerer godt), `waypipe` til Wayland eller en rigtig remote-desktop-protokol (RDP via `xrdp`, eller NoMachine/NX) til et fuldt skrivebord.

## Pointen

XP-klippet er en lille tidskapsel: en bakke-ikon-X-server, en PuTTY-tunnel og en Linux-teksteditor, der materialiserer sig på et beige XP-skrivebord. *Idéen* — kør appen derovre, se den herovre — forsvandt aldrig. Det, der ændrede sig, er, at du ikke længere samler det i hånden. X-serveren flyttede ind i Windows, X11 gav plads til Wayland, og det almindelige tilfælde ("jeg vil bare røre filer på den maskine") fik bedre svar helt af sig selv. Atten års VVS, stille og roligt absorberet ind i `apt install`.

## FAQ

### Virker SSH X11-forwarding stadig i 2026?

Ja — `ssh -X` (eller `-Y` til betroet forwarding) er uændret. Det forwarder X11 til en hvilken som helst X-server: VcXsrv, Xming, XQuartz eller WSLg's. Det er bare snakkesaligt over latency, hvilket er grunden til, at xpra/waypipe/RDP som regel vinder til fjern-arbejde i dag.

### Vedligeholdes Xming stadig?

Builds dukker stadig op (7.7.x i 2026), men de er donations-låst; den sidste gratis offentlige udgave var 6.9.0.31 i 2007 — Windows XP-æraen for klippet. Vil du have en gratis, aktivt bygget X-server til Windows, så brug VcXsrv.

### Skal jeg overhovedet bruge en X-server?

Kun til at forwarde GUI-apps fra en fjern maskine over SSH, eller til at køre X-apps fra en ikke-WSLg-distro. På WSL2 med Windows 11 (eller Win10 21H2+) leverer WSLg allerede en — lokale Linux-GUI-apps åbner uden noget ekstra installeret.

### Hvorfor brød Wayland det gamle "forward det over SSH"-trick?

X11 var netværkstransparent af design, så forwarding var gratis. Wayland er det bevidst ikke — fjern-visning er et separat anliggende, der håndteres af waypipe eller RDP. WSLg dækker over det ved at køre Weston + XWayland, så begge slags app virker.

## Opsummering

- Den gamle måde: installér **Xming**, sæt X11-forwarding til i PuTTY, `ssh -X`, og en fjern Linux-app tegner op på Windows. [Videoen](https://www.youtube.com/watch?v=P3hHsfdFusw) er det, på Windows XP.
- I dag: **WSLg** leverer en Wayland- + X-server inde i Windows — `apt install` en Linux-app i WSL2, og den åbner bare.
- **VcXsrv** er den gratis, vedligeholdte afløser for Xming til det klassiske fjern-forwarding-tilfælde; **Xming** selv blev donations-kun efter 6.9.0.31 (2007).
- **Wayland** afløste X11's netværkstransparens; brug **waypipe**, **xpra** eller RDP til hurtig fjern-GUI.
- For den oprindelige motivation — at redigere på en fjern maskine — foretræk VS Codes Remote-SSH, [sshfs](/post/mount-remote-filesystem-sshfs/) eller almindelig [SSH](/post/ssh-key-login-without-password/).
