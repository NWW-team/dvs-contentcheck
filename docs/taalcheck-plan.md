# Plan: taalcheck

> **Status:** vastgesteld 15 september 2026, nog niet gebouwd
> **Hoort bij:** fase 1 uit `STRATEGY.md`

Dit is het plan voor de eerste werkende controle. Het beschrijft wát er wordt
gecontroleerd en waarom, zodat achteraf navolgbaar is waarom de tool meldt wat
hij meldt.

## Waarom taal als eerste

Taal raakt alle 741 pagina's tegelijk en is met regels te controleren: geen
taalmodel nodig, dus reproduceerbaar, uitlegbaar en goedkoop. Dat sluit aan op
het uitgangspunt *regels vóór modellen*.

## De meting vooraf

Voordat er iets is gebouwd, is de opgehaalde content gemeten. Dat leverde een
uitkomst op die het ontwerp bepaalt:

| Gemeten | Uitkomst |
| --- | --- |
| Zinslengte | mediaan 9 woorden, 90e percentiel 14, langste 38 |
| Zinnen langer dan 20 woorden | 2,9% |
| Ambtelijke woorden (`indien`, `teneinde`, `middels`, …) | 11 keer in 477.787 woorden |
| Aanspreekvorm | 19.484 keer `u`, 2 keer `je`/`jouw` |
| Schrijfwijze identiteitskaart | 9.689 keer `ID-kaart`, 1 keer `ID kaart` |

**Conclusie:** deze content is al in duidelijke taal geschreven. Een algemene
lijst met moeilijke woorden vindt hier vrijwel niets en levert vooral ruis op.

## Het uitgangspunt dat hieruit volgt

**De site is zijn eigen norm.** Bij 741 pagina's waarvan er ruim 200 op elkaar
lijken, is de afwijking de fout — niet het patroon. De controle zoekt daarom
naar plekken die afwijken van hoe de rest van de site het doet, in plaats van
naar overtredingen van een externe regellijst.

Dat past bij de afweging uit `STRATEGY.md`: precisie weegt zwaarder dan
dekking, omdat valse meldingen ertoe leiden dat de tool wordt weggeklikt.

## De vijf controles

| Controle | Wat het zoekt | Ernst | Verwacht |
| --- | --- | --- | --- |
| `aanspreekvorm` | `je`, `jij`, `jouw`, `jullie` terwijl de site `u` gebruikt | hoog | 2 |
| `schrijfwijze` | varianten van vaste termen: `ID kaart`, `id-kaart`, `email`, `Digid`, `pas foto` | hoog | 1 |
| `formeel-woord` | ambtelijk woord met een gewoner alternatief erbij | midden | ±12 |
| `lijdende-vorm` | `wordt`/`worden` plus voltooid deelwoord | advies | 44 |
| `lange-zin` | zinnen langer dan 20 woorden | advies | ±3% van de zinnen |

**Ernst** bepaalt de volgorde in het rapport:

- **hoog** — vrijwel zeker fout; de redactie hoeft alleen te bevestigen
- **midden** — waarschijnlijk beter anders, maar de context beslist
- **advies** — suggestie; de redactie beslist

## Wat het oplevert

- `rapport/taalcheck.md` — samenvatting, met de zekere fouten volledig uitgeschreven
- `rapport/taalcheck.csv` — alle bevindingen, met per regel: URL, regelnummer,
  citaat, soort, ernst, uitleg en een concreet voorstel

Elke bevinding vermeldt dus wat er is geraakt, waarom dat een probleem is en
wat een alternatief is. Zonder die onderbouwing wordt een melding niet
vertrouwd en dus niet gebruikt.

## Buiten scope

- **Spellingcontrole.** Er is in deze omgeving geen Nederlands woordenboek
  beschikbaar; een eigen lijst zou vooral namen en vaktermen als fout markeren.
- **Automatisch herschrijven.** De tool stelt voor, de redactie beslist.
- **Feitelijke juistheid.** Bedragen en termijnen vergelijken tussen
  landpagina's is een aparte controle, niet deze.

## Hoe we weten of het werkt

Deze drie afwijkingen zijn met de hand gevonden en moeten alle drie worden
teruggevonden. Vindt de controle ze niet, dan deugt de controle niet.

| Afwijking | Pagina |
| --- | --- |
| `Israëlische ID kaart` | `/paspoort-id-kaart/buitenland/paspoort-israel` |
| `Heeft u sommige vragen met je beantwoord?` | `/paspoort-id-kaart/langer-dan-2-jaar-verlopen-frankrijk` |
| `jouw volledige naam` | `/paspoort-id-kaart/nooddocument/myanmar` |

Daarna is de vraag niet "hoeveel vindt hij", maar "hoeveel bevindingen neemt de
redactie over". Dat is de maatstaf uit `STRATEGY.md`.
