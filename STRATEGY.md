# Strategie — dvs-contentcheck

> **Status:** concept / in te vullen
> **Laatst bijgewerkt:** 2026-09-15
> **Eigenaar:** `TODO: naam + rol`
>
> Dit document beschrijft *waarom* dvs-contentcheck bestaat en *welke koers* we varen.
> Het beschrijft niet hoe je het installeert of gebruikt — dat hoort in de README
> en in `docs/`. Onderdelen met `TODO` zijn nog niet vastgesteld.

## 1. Doel

`TODO: één alinea. Wat moet dvs-contentcheck bereiken, in de taal van de
opdrachtgever — niet in techniek. Bijvoorbeeld: "content vóór publicatie
automatisch toetsen aan de DVS-richtlijnen, zodat redacteuren minder handmatig
nakijken en fouten niet live gaan."`

**Succes betekent:** `TODO: het meetbare gevolg. Bijv. "90% van de checks die
redactie nu handmatig doet, gebeurt automatisch."`

## 2. Probleem

Wat er nu misgaat, en voor wie:

- `TODO: probleem 1 — wie loopt hier tegenaan en wat kost het?`
- `TODO: probleem 2`
- `TODO: probleem 3`

**Hoe het nu gaat (huidige situatie):** `TODO: het bestaande proces, ook als dat
"handmatig, per mail" is. Dit is de nulmeting waartegen we verbetering afmeten.`

## 3. Scope

### Wel

- `TODO: welke content wordt gecontroleerd? (bron, formaat, volume)`
- `TODO: welke soorten checks? (bijv. taal/spelling, richtlijnen, structuur,
  toegankelijkheid, feitelijke actualiteit, merk/tone-of-voice)`
- `TODO: waar grijpt de tool in? (redactieproces, CI, publicatiepijplijn)`

### Niet

Expliciet buiten scope houden is de helft van de strategie:

- `TODO: bijv. zelf content genereren of herschrijven`
- `TODO: bijv. eindredactioneel oordeel overnemen — de tool adviseert, mens beslist`
- `TODO: bijv. andere kanalen/systemen`

## 4. Gebruikers en belanghebbenden

| Wie | Wat ze nodig hebben | Hoe ze het gebruiken |
| --- | --- | --- |
| `TODO: bijv. redacteur` | `TODO` | `TODO` |
| `TODO: bijv. eindredactie` | `TODO` | `TODO` |
| `TODO: bijv. beheer/IT` | `TODO` | `TODO` |

## 5. Aanpak

De uitgangspunten die keuzes in dit project sturen:

1. **`TODO: principe`** — `TODO: wat het betekent in de praktijk, en wat we
   daardoor níet doen.`
2. **`TODO: principe`** — `TODO`
3. **`TODO: principe`** — `TODO`

Suggesties om uit te kiezen of te vervangen — schrap wat niet past:

- *Regels vóór modellen.* Wat met een deterministische regel te checken is, checken
  we met een regel: reproduceerbaar, uitlegbaar, goedkoop. Een taalmodel zetten we
  alleen in waar beoordeling nodig is.
- *Adviseren, niet blokkeren.* Bevindingen zijn voorstellen met bron en
  onderbouwing; de redactie houdt het laatste woord.
- *Elke check is uitlegbaar.* Bij iedere bevinding staat welke richtlijn is
  geraakt en waarom, anders wordt de uitkomst niet vertrouwd en niet gebruikt.
- *Klein beginnen op echte content.* Liever drie checks die op de werkelijke
  contentstroom draaien dan twintig die alleen op testmateriaal werken.

## 6. Architectuur op hoofdlijnen

`TODO: kort — in/uitgangen en de stappen ertussen. Vul in zodra de aanpak staat;
detail hoort in docs/architecture.md, niet hier.`

- **Invoer:** `TODO`
- **Checks:** `TODO: hoe worden regels/checks gedefinieerd en toegevoegd?`
- **Uitvoer:** `TODO: rapport, PR-commentaar, dashboard, API?`
- **Technologie:** `TODO: taal, runtime, hosting. Noteer ook waarom.`

## 7. Fasering

| Fase | Doel | Klaar wanneer | Termijn |
| --- | --- | --- | --- |
| 0 — Verkenning | Richtlijnen en contentstroom in kaart | `TODO` | `TODO` |
| 1 — Eerste werkende versie | Een handvol checks op echte content | `TODO` | `TODO` |
| 2 — In het proces | Draait mee in de publicatiepijplijn | `TODO` | `TODO` |
| 3 — Verbreden | Meer checks, meer contentsoorten | `TODO` | `TODO` |

## 8. Meten

Wat we volgen om te weten of dit werkt:

- `TODO: bijv. aandeel bevindingen dat de redactie overneemt (precisie in de praktijk)`
- `TODO: bijv. gemist bij steekproef (recall)`
- `TODO: bijv. doorlooptijd van controle per artikel`
- `TODO: bijv. aantal fouten dat alsnog live gaat`

Valse alarmen zijn de grootste bedreiging voor gebruik: bij te veel ruis wordt de
tool weggeklikt. Precisie weegt daarom zwaarder dan dekking.

## 9. Risico's

| Risico | Gevolg | Wat we doen |
| --- | --- | --- |
| `TODO: bijv. richtlijnen zijn niet eenduidig vastgelegd` | `TODO` | `TODO` |
| `TODO: bijv. te veel valse meldingen` | `TODO` | `TODO` |
| `TODO: bijv. geen aansluiting op het redactiesysteem` | `TODO` | `TODO` |
| `TODO: bijv. privacy/AVG bij verwerken van content` | `TODO` | `TODO` |

## 10. Open vragen

- `TODO: vraag — wie beslist, en wanneer moet het antwoord er zijn?`
- `TODO`

## 11. Besluiten

Vastgestelde keuzes, met datum en reden. Zo blijft navolgbaar waarom iets zo is.

| Datum | Besluit | Reden |
| --- | --- | --- |
| `TODO` | `TODO` | `TODO` |
