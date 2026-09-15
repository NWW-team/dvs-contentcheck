# Strategie — dvs-contentcheck

> **Status:** concept — vastgesteld op hoofdlijnen, details open
> **Laatst bijgewerkt:** 2026-09-15
> **Eigenaar:** nog te bevestigen
>
> Dit document beschrijft *waarom* dvs-contentcheck bestaat en *welke koers* we varen.
> Installatie en gebruik horen in de README en in `docs/`.
>
> Regels gemarkeerd met **[aanname]** zijn niet bevestigd en moeten worden
> getoetst voordat er werk op wordt gebaseerd.

## 1. Doel

dvs-contentcheck toetst de content op **nederlandwereldwijd.nl** aan de
uitgangspunten van de DVS en geeft terug wat *niet* in lijn is.

De tool beoordeelt dus; hij herstelt niet. De uitkomst is een lijst afwijkingen
met vindplaats en onderbouwing, waar de redactie vervolgens zelf mee aan de slag
gaat.

**Succes betekent:** dat voor een gegeven pagina betrouwbaar is vast te stellen
welke DVS-uitgangspunten niet worden nageleefd, en dat de redactie die
bevindingen in de praktijk overneemt. Een concrete norm hiervoor is nog niet
vastgesteld — zie sectie 8.

## 2. Probleem

**Er is nu geen controle.** Content op nederlandwereldwijd.nl wordt niet
systematisch aan de DVS getoetst — niet geautomatiseerd en niet handmatig.

Daaruit volgt:

- Of de content in lijn is met de DVS is onbekend. Er is geen cijfer, geen
  steekproef, geen overzicht.
- Afwijkingen worden niet gevonden, dus ook niet hersteld. Ze blijven staan zo
  lang als ze er staan.
- De DVS werkt daardoor niet door in de content. Het document bestaat, maar
  raakt het publicatieproces niet.

**Gevolg voor de strategie:** er is geen nulmeting om verbetering tegen af te
meten, en geen bestaand menselijk oordeel om de tool tegen te kalibreren. Beide
moeten we zelf maken. Dat is geen bijzaak maar de eerste echte klus — zie
fase 0 en 1.

## 3. Scope

### Wel

- **Toetsingsobject:** alle content op nederlandwereldwijd.nl. De eerste focus
  is de content over **paspoort en ID-kaart**; daarna verbreden naar de rest.
- **Toetsingskader:** alle uitgangspunten van de DVS, niet een selectie ervan.
- **Uitkomst:** per stuk content de uitgangspunten die niet worden nageleefd,
  met vindplaats in de tekst en onderbouwing waarom het afwijkt.

### Niet

- **Content herschrijven of genereren.** De tool signaleert; formuleren blijft
  redactiewerk.
- **Het redactionele eindoordeel overnemen.** Een bevinding is een signaal, geen
  verplichting.
- **De DVS zelf herzien.** De DVS is hier het gegeven kader. Blijkt een
  uitgangspunt niet toetsbaar, dan is dat een signaal terug naar de eigenaar van
  de DVS, geen reden om het uitgangspunt aan te passen in de tool.
- **Andere websites en kanalen.** Alleen nederlandwereldwijd.nl.

## 4. Gebruikers en belanghebbenden

| Wie | Wat ze nodig hebben | Hoe ze het gebruiken |
| --- | --- | --- |
| Redactie nederlandwereldwijd.nl | Concrete, naar de bron herleidbare afwijkingen per pagina | Bevindingen doorlopen en content aanpassen |
| Eigenaar van de DVS | Zicht op waar content structureel afwijkt, en op welke uitgangspunten | Naleving volgen; signalen over niet-toetsbare uitgangspunten oppakken |
| Beheer / ontwikkeling | Onderhoudbare checks, herleidbare uitkomsten | Checks toevoegen en bijstellen als de DVS wijzigt |

De verdeling hierboven volgt uit het doel, maar de rollen zijn nog niet aan
personen of teams toegewezen. **[aanname]**

## 5. Uitgangspunten

1. **De DVS is de enige bron van waarheid.** Elke check hoort bij een
   genummerd uitgangspunt uit de DVS. Is er geen uitgangspunt dat een check
   dekt, dan is de check niet van ons.
2. **Elke bevinding is uitlegbaar en herleidbaar.** Bij een afwijking staat
   welk uitgangspunt geraakt wordt, waar in de tekst, en waarom het afwijkt.
   Een oordeel zonder onderbouwing wordt niet vertrouwd en dus niet gebruikt.
3. **Signaleren, niet blokkeren of herschrijven.** De tool publiceert niets,
   tegenhoudt niets en past niets aan.
4. **Deterministisch waar het kan, beoordeling waar het moet.** Een
   uitgangspunt dat mechanisch te toetsen is, toetsen we met een regel:
   reproduceerbaar en uitlegbaar. Uitgangspunten die om interpretatie vragen,
   vragen om een taalmodel — met de reproduceerbaarheidseisen uit sectie 6.
5. **Klein beginnen op echte content.** Liever de paspoort- en
   ID-kaartpagina's volledig en aantoonbaar goed getoetst dan alle content
   half.
6. **Het menselijk oordeel is de maatstaf.** De tool is goed zolang hij
   overeenkomt met wat een redacteur zou vinden. Daarom eerst een handmatige
   referentiemeting, dan automatiseren.

## 6. Architectuur op hoofdlijnen

Detail hoort in `docs/architecture.md`; dit zijn de contouren.

- **Invoer:** de content van nederlandwereldwijd.nl. Hoe we die ophalen is een
  open vraag: de site is openbaar en dus te crawlen, maar een CMS-export of API
  geeft schonere tekst en weet welke content bestaat. Zie sectie 10.
- **Toetsingskader:** de DVS-uitgangspunten, genummerd en apart vastgelegd,
  zodat een bevinding ernaar kan verwijzen en een wijziging in de DVS
  navolgbaar doorwerkt in de checks.
- **Checks:** per uitgangspunt één check, onafhankelijk toe te voegen en te
  wijzigen. Twee soorten, conform uitgangspunt 4: deterministische regels, en
  beoordeling door een taalmodel.
- **Uitvoer:** per stuk content de niet-nageleefde uitgangspunten, met
  vindplaats en onderbouwing. In welke vorm dat bij de redactie terechtkomt, is
  nog open.

**Over de taalmodel-checks.** Naar verwachting is een deel van de
DVS-uitgangspunten kwalitatief geformuleerd en niet met een regel te toetsen
**[aanname — te bevestigen zodra het DVS-document beschikbaar is]**. Voor die
checks geldt:

- het uitgangspunt en de beoordeling gaan als expliciet criterium mee, zodat
  het oordeel aan de bron hangt en niet aan een algemene indruk;
- het model geeft per bevinding een citaat uit de content, zodat de vindplaats
  controleerbaar is;
- dezelfde content moet bij herhaling tot hetzelfde oordeel leiden; variatie is
  een defect, niet een eigenschap. Dit wordt gemeten op de referentieset uit
  fase 1.

Modelkeuze en techniek (taal, runtime, hosting) zijn nog niet besloten en
worden pas ingevuld als fase 0 uitwijst hoeveel beoordelingswerk er is.

## 7. Fasering

| Fase | Doel | Klaar wanneer |
| --- | --- | --- |
| 0 — DVS toetsbaar maken | Uitgangspunten uit het DVS-document halen, nummeren, en per uitgangspunt bepalen of het met een regel of met beoordeling te toetsen is | Er ligt een genummerde lijst uitgangspunten met per stuk een toetsingsvorm — of de constatering dat het uitgangspunt niet toetsbaar is |
| 1 — Referentiemeting | De nulmeting maken die er niet is: handmatig de paspoort- en ID-kaartcontent tegen de uitgangspunten leggen | Er ligt een set beoordeelde pagina's die als maatstaf dient voor de tool |
| 2 — Eerste geautomatiseerde checks | Checks bouwen voor paspoort en ID-kaart en de uitkomst vergelijken met de referentiemeting | De tool komt op de referentieset aantoonbaar overeen met het handmatige oordeel |
| 3 — Verbreden | Uitrollen naar alle content op nederlandwereldwijd.nl | Alle content wordt periodiek getoetst |

Termijnen zijn nog niet vastgesteld. De omvang van fase 0 en 1 hangt af van het
aantal uitgangspunten en de hoeveelheid paspoort- en ID-kaartcontent; beide zijn
nog niet geteld.

## 8. Meten

Zolang fase 1 niet is gedaan, is er niets om tegen te meten. Daarna volgen we:

- **Overeenstemming met het handmatige oordeel** op de referentieset,
  uitgesplitst in onterechte meldingen en gemiste afwijkingen.
- **Overnamepercentage:** welk deel van de bevindingen leidt tot een aanpassing
  in de content.
- **Dekking:** hoeveel van de DVS-uitgangspunten daadwerkelijk getoetst worden,
  en hoeveel niet toetsbaar bleken.
- **Reproduceerbaarheid:** geeft dezelfde content bij herhaling hetzelfde
  oordeel.

Onterechte meldingen wegen zwaarder dan gemiste afwijkingen. Bij te veel ruis
verliest de redactie het vertrouwen en wordt de tool niet meer gebruikt — en
omdat er nu geen controle is, is niet-gebruiken terugvallen op nul.

## 9. Risico's

| Risico | Gevolg | Wat we doen |
| --- | --- | --- |
| DVS-uitgangspunten zijn te abstract om op contentniveau te toetsen | Checks meten iets anders dan het uitgangspunt bedoelt; schijnzekerheid | Fase 0 gaat hier expliciet over: per uitgangspunt vaststellen óf het toetsbaar is, en niet-toetsbare uitgangspunten als zodanig terugmelden |
| Geen nulmeting en geen bestaand menselijk oordeel | Niet vast te stellen of de tool goed werkt | Fase 1 maakt de referentiemeting vóór er geautomatiseerd wordt |
| Te veel onterechte meldingen | Redactie klikt bevindingen weg; tool raakt in onbruik | Precisie boven dekking; meten op de referentieset; liever minder checks die kloppen |
| Beoordeling door een taalmodel is niet reproduceerbaar | Wisselende uitkomsten op dezelfde content ondermijnen het vertrouwen | Reproduceerbaarheid is een meetpunt (sectie 8); bevindingen altijd met citaat, zodat ze te controleren zijn |
| Content verandert continu | Bevindingen verouderen; afwijkingen glippen er na publicatie in | Periodiek toetsen in plaats van eenmalig; frequentie nog te bepalen (sectie 10) |
| DVS wordt herzien | Checks toetsen aan een verouderd kader | Uitgangspunten genummerd en apart vastleggen; versie van de DVS vastleggen bij elke toetsing |

## 10. Open vragen

- **Waar staat het DVS-document, welke versie is leidend, en waar staat DVS
  voluit voor?** Zonder dit kan fase 0 niet beginnen — dit is de blokkerende
  vraag.
- **Hoe halen we de content op:** crawlen van de openbare site, of een export
  of API uit het CMS? Dit bepaalt of we weten welke content bestaat, en hoe
  schoon de tekst is die we toetsen.
- **Wie is eigenaar** van dvs-contentcheck, en wie van de DVS?
- **Hoe vaak toetsen we:** eenmalig, bij elke contentwijziging, of periodiek?
- **Hoe krijgt de redactie de bevindingen:** rapport, dashboard, of tickets in
  een bestaand werkproces?
- **Wat is de omvang:** hoeveel uitgangspunten heeft de DVS, en hoeveel
  paspoort- en ID-kaartcontent is er?

## 11. Besluiten

| Datum | Besluit | Reden |
| --- | --- | --- |
| 2026-09-15 | Toetsingsobject is nederlandwereldwijd.nl | Daar staat de content die aan de DVS moet voldoen |
| 2026-09-15 | Alle content in scope, eerste focus op paspoort en ID-kaart | Uiteindelijk moet alles in lijn zijn; beginnen bij één afgebakend onderwerp houdt fase 1 en 2 haalbaar |
| 2026-09-15 | Alle DVS-uitgangspunten toetsen, geen selectie | Doel is dat content in lijn is met de DVS als geheel |
| 2026-09-15 | De tool signaleert afwijkingen en herschrijft niet | Formuleren is redactiewerk; een signaleringstool is eerder bruikbaar en minder riskant |
