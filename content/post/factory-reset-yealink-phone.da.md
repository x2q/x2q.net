+++
title = "Nulstil en Yealink-telefon til fabriksindstillinger — også uden admin-adgangskoden (2026)"
date = 2026-06-10
slug = "nulstil-yealink-telefon-til-fabriksindstillinger"
description = "Sådan fabriksnulstiller du en Yealink SIP-telefon (T4x/T5x m.fl.), inklusive en hardware-nulstilling når du ikke har admin-adgangskoden. Plus standardadgangskoden i 2026 — admin/admin vs. den enheds-unikke label."

[taxonomies]
tags = ["yealink", "voip", "sip", "bordtelefon", "fabriksnulstilling", "admin-adgangskode", "netvaerk"]

[extra]
summary = "Du har fået fingre i en brugt Yealink-bordtelefon eller arvet en med ukendt admin-adgangskode. Her er, hvordan du fabriksnulstiller den på tre måder — fra tastaturet, fra web-UI'en og (den vigtige) med et hardware-tastetryk, der slet ikke kræver admin-adgangskoden. Plus hvad der ændrede sig ved Yealinks standardadgangskode: 'admin/admin' på ældre firmware, en enheds-unik adgangskode på nyere enheder."
faq = [
  { q = "Hvad er standard-admin-adgangskoden til Yealink?", a = "På ældre firmware er det admin / admin (brugernavn admin, adgangskode admin). Af sikkerhedshensyn leveres nyere Yealink-firmware med en unik tilfældig standardadgangskode trykt på et klistermærke på telefonen (eller tvinger dig til at sætte en ved første login) — så admin/admin virker ikke på nyere enheder. Hvis ingen af dem virker, så lav en hardware-fabriksnulstilling, der rydder adgangskoden." },
  { q = "Hvordan nulstiller jeg en Yealink-telefon uden admin-adgangskoden?", a = "Brug hardware-nulstillingen: med telefonen i hviletilstand, tryk og hold OK-tasten (den midterste runde tast) i cirka 10 sekunder, indtil den spørger 'Nulstil til fabriksindstillinger?', og bekræft så med OK. Dette sletter alle indstillinger inklusive admin-adgangskoden — intet login nødvendigt." },
  { q = "Sletter en fabriksnulstilling min SIP-konto og kontakter?", a = "Ja. En fuld fabriksnulstilling sletter SIP-/VoIP-kontoopsætningen, netværksindstillinger, kontakter og opkaldshistorik og bringer telefonen tilbage til ud-af-æsken-tilstand. Eksportér eller notér dine SIP-oplysninger først, hvis du skal genregistrere den." },
  { q = "Hvilke Yealink-modeller dækker dette?", a = "Samme fremgangsmåde virker på tværs af SIP-T2x-, T4x- og T5x-familierne (f.eks. T21, T27, T41, T42, T46, T48, T53, T54, T57) og de fleste andre Yealink-bordtelefoner — den nøjagtige tasteetiket kan variere lidt, men det er OK-/midtertasten holdt i hviletilstand." }
]
+++

**Kort fortalt —** For at fabriksnulstille en **Yealink** SIP-bordtelefon har du tre muligheder: **tastaturmenuen** (kræver admin-adgangskoden), **web-UI'en** (kræver admin-adgangskoden) eller et **hardware-tastetryk**, der slet **ikke kræver adgangskode** — hold **OK**-tasten i ~10 sekunder. Den sidste er den, du vil bruge til en brugt eller arvet telefon med ukendt admin-login. Dette dækker også standardadgangskode-situationen i 2026: gammel firmware er `admin`/`admin`, nyere enheder leveres med en **unik adgangskode på en label**.

## Standardadgangskoden, dengang → nu

Det her snubler folk over, så få det på plads først:

- **Ældre firmware:** brugernavn `admin`, adgangskode `admin`. Den klassiske standard.
- **Nyere firmware (sikkerhedshærdning, ~2021 og frem):** Yealink leverer hver telefon med en **unik tilfældig standardadgangskode** trykt på et klistermærke (typisk på undersiden eller æsken), eller tvinger dig til at sætte en ny adgangskode ved første web-login. Så `admin`/`admin` **virker ikke** på nyere enheder.

Hvis du har adgangskoden, så nulstil fra menuen eller web-UI'en. Hvis du ikke har den, så spring til **hardware-nulstillingen** — den rydder adgangskoden helt.

## Metode 1 — Hardware-nulstilling (ingen admin-adgangskode nødvendig)

Det er den, de fleste søger efter. Med telefonen **tændt og i hviletilstand** (ikke i et opkald, ikke i en menu):

1. Tryk og **hold OK-tasten** — den runde/midterste tast under skærmen — i cirka **10 sekunder**.
2. Skærmen viser **"Nulstil til fabriksindstillinger?"**
3. Tryk **OK** for at bekræfte.
4. Telefonen sletter alt og genstarter. Det tager et minut eller to; afbryd den ikke.

Intet login nødvendigt — dette nulstiller admin-adgangskoden sammen med alt andet. (På enkelte modeller udløses prompten ved at holde **X**-/annuller-tasten i stedet; hvis OK ikke gør det, så prøv den.)

## Metode 2 — Fra telefonens tastatur (kræver admin-adgangskode)

1. Tryk på **Menu**-softtasten.
2. Gå til **Indstillinger → Avancerede indstillinger**, og indtast admin-adgangskoden (`admin` på gammel firmware, eller label-adgangskoden).
3. Vælg **Nulstil til fabriksindstillinger** (nogle gange **Reset Config**), og bekræft.

## Metode 3 — Fra webgrænsefladen (kræver admin-adgangskode)

1. Find telefonens IP: **Menu → Status** (eller **Indstillinger → Status**).
2. Gå til `http://<telefon-ip>/`, og log ind som `admin`.
3. Gå til **Settings → Upgrade** (eller **Reset & Reboot**), og klik **Reset to Factory**.

## Efter nulstillingen

En fuld nulstilling sletter **SIP-kontoen, netværkskonfigurationen, kontakter og opkaldshistorik** — telefonen kommer tilbage som ny. Før du nulstiller (hvis du kan logge ind), så notér dine **SIP-oplysninger** (server/registrar, brugernavn, auth-ID, adgangskode), så du kan genregistrere den bagefter. På nyere firmware bliver du bedt om at sætte en frisk admin-adgangskode ved første login igen.

## Opsummering

- **Ingen admin-adgangskode?** Hold **OK**-tasten ~10 s i hviletilstand → bekræft → færdig. Intet login nødvendigt.
- **Har adgangskoden?** Nulstil fra **Menu → Indstillinger → Avanceret**, eller **web-UI'en** på `http://<telefon-ip>/`.
- **Standardadgangskode:** `admin`/`admin` på gammel firmware; en **unik label-adgangskode** på nyere enheder.
- En fabriksnulstilling **sletter SIP-kontoen og kontakter** — gem dine SIP-oplysninger først.
