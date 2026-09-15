# Plan: actualiteitscheck

> **Status:** concept, nog niet gebouwd
> **Hoort bij:** de DVS-eisen *actueel* en *correct doorverwijzen*, zie
> [`dvs-meetlat.md`](dvs-meetlat.md)

## Waarom deze controle als tweede

De Dienstverleningsstrategie wijst de informatievoorziening aan als
basisinspanning en eerste prioriteit: die moet altijd actueel en juist zijn. De
taalcheck dekt die eis niet. Dit plan dicht het grootste gat.

## De meting vooraf

Net als bij de taalcheck eerst meten, dan pas ontwerpen. Gemeten op de 741
opgehaalde pagina's, peildatum 15 september 2026:

| Gemeten | Uitkomst |
| --- | --- |
| Volledige datums (dag maand jaar) in de content | 64 |
| Daarvan in het verleden | 16 |
| Daarvan vandaag of later | 48 |
| Pagina's met het woord "tijdelijk" | 228 |
| Pagina's die zeggen geen informatie te hebben | 130 |

Twee uitkomsten bepalen het ontwerp, en beide zijn waarschuwingen tegen de
voor de hand liggende regel:

**"Tijdelijk" is bijna altijd geen melding waard.** Van de 228 pagina's zijn er
210 met de definitiezin *"Een nooddocument is een tijdelijk reisdocument"*. Een
regel die op het woord zoekt, is voor 92% ruis. Wat overblijft is wél raak: op
één pagina staat dat een consulaat-generaal "tijdelijk" gesloten is — sinds
20 februari 2023, inmiddels 1.303 dagen.

**Een datum in het verleden is meestal geen fout.** De 16 oudste datums zijn
historische feiten: *"een ID-kaart afgegeven op of na 13 maart 2021"*,
*"paspoorten van voor 2014"*. Die horen er juist te staan. Het risico zit in de
48 datums in de toekomst: aankondigingen van bezoeken, spreekuren en
afspraakmomenten die morgen verlopen en die niemand weghaalt.

## De vier controles

| Controle | Wat het zoekt | Ernst | Gevonden bij de meting |
| --- | --- | --- | --- |
| `doodlopende-verwijzing` | "geen informatie over X" zonder dat er een concrete bestemming wordt genoemd | hoog | **83 pagina's** |
| `langdurig-tijdelijk` | "tijdelijk" met een begindatum langer dan een jaar geleden | hoog | 1 pagina (1.303 dagen) |
| `verlopen-aankondiging` | een aankondiging (bezoek, spreekuur, afspraak) met een datum die voorbij is | hoog | 0 nu, maar 48 gaan verlopen |
| `datum-verloopt-binnenkort` | datums die binnen 30 dagen passeren | advies | 48 pagina's |

### De belangrijkste: doodlopende verwijzingen

Van de 130 pagina's die zeggen geen informatie te hebben, noemen er **47**
concreet een ander land ("U kunt de informatie bekijken over fotografen in:
Pakistan, Verenigde Arabische Emiraten, India, Iran"). De andere **83** zeggen
alleen *"U kunt wel de informatie van een omringend land bekijken"* — zonder te
zeggen wélk land, en zonder link.

Dat is precies de klantbelofte uit de DVS: eerlijk zijn over wat NWW niet doet
mág, mits de klant weet waar hij dan wél moet zijn. Bij die 83 pagina's loopt de
klant dood. Met de hand gecontroleerd op Armenië, Bahrein en Benin: identieke
sjabloontekst, geen bestemming.

Omdat het sjabloontekst is, is het ook goed nieuws: één tekst aanpassen — of per
land de buurlanden invullen — lost 83 pagina's tegelijk op.

## Wat de controle bewust niet meldt

Uit de meting volgt wat er níet in moet, anders verzuipt het echte signaal:

- **De definitiezin over nooddocumenten** (210 pagina's). Dat is uitleg, geen
  tijdelijke mededeling.
- **Historische datumverwijzingen**: "afgegeven op of na", "van voor", "geboren
  na". Een datum in het verleden is daar het onderwerp, niet de veroudering.
- **Jaartallen zonder dag en maand** ("Fotomatrix model 2020"). Dat is een
  documentnaam, geen houdbaarheidsdatum.

## Wat het oplevert

Dezelfde vorm als de taalcheck, zodat het op dezelfde rapportpagina past:
`rapport/actualiteitscheck.csv` met per bevinding de URL, het citaat, hoe oud
iets is in dagen, de uitleg en een voorstel. Geen tweede app, geen tweede link.

## Hoe we weten of het werkt

Deze bevindingen zijn met de hand vastgesteld en moeten alle vier terugkomen:

| Verwacht | Waar |
| --- | --- |
| "tijdelijk gesloten" sinds 1.303 dagen | consulaat-generaal Sint-Petersburg |
| doodlopende verwijzing | pasfoto-armenie, pasfoto-bahrein, pasfoto-benin |
| géén melding op de definitiezin | de 210 nooddocument-pagina's |
| géén melding op "afgegeven op of na 13 maart 2021" | de ID-kaartpagina's |

Die laatste twee zijn even belangrijk als de eerste twee: een controle die ruis
produceert, wordt weggeklikt.

## Besloten: geen grens, wel de duur

Vanaf wanneer "tijdelijk" te lang is, is een keuze en geen feit. Daarom trekt de
controle die grens niet. Elke tijdelijke mededeling wordt gemeld met **hoeveel
dagen die er al staat**; de redactie ziet "1.303 dagen" en beslist zelf. Dat past
bij het uitgangspunt uit `STRATEGY.md`: de tool adviseert, de redactie beslist.

Een tijdelijke mededeling **zonder** datum is een bevinding op zichzelf: dan valt
niet te zien hoe lang die er al staat, en kan niemand beoordelen of hij weg mag.
