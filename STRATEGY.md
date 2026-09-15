# Strategie — dvs-contentcheck

> **Status:** in uitvoering — fase 1
> **Laatst bijgewerkt:** 2026-09-15
> **Eigenaar:** `TODO: naam + rol`
> **Toetsingskader:** Dienstverleningsstrategie NederlandWereldwijd (DVS),
> vastgesteld 17-02-2025. Niet in deze repository opgenomen: dit is een openbare
> repository en de DVS is een intern document. De eisen eruit staan hieronder
> beschreven; de uitwerking in [`docs/dvs-meetlat.md`](docs/dvs-meetlat.md).
>
> Dit document beschrijft *waarom* dvs-contentcheck bestaat en *welke koers* we varen.
> Het beschrijft niet hoe je het installeert of gebruikt — dat hoort in de README
> en in `docs/`. Onderdelen met `TODO` zijn nog niet vastgesteld.

## 1. Doel

`dvs-contentcheck` maakt meetbaar of de content op www.nederlandwereldwijd.nl de
beloften waarmaakt die NederlandWereldwijd doet in zijn Dienstverleningsstrategie.

De DVS wijst de informatievoorziening — website en kennisbank — aan als
**basisinspanning en eerste prioriteit**, en stelt dat die altijd actueel en juist
moet zijn. Het doel voor 2030 is informatie die actueel, consistent en volledig is.
Reisdocumenten (paspoort en ID-kaart) staan er als **verbeterprioriteit 2**; dat is
niet toevallig de content waarmee dit project is begonnen.

Die belofte controleren we niet met de hand maar met regels, zodat de redactie ziet
waar de content afwijkt van wat is beloofd. Dat sluit aan op het DVS-uitgangspunt
*sturen op basis van feiten*: pas als er een getal is, valt er op te sturen.

**Succes betekent:** de redactie neemt bevindingen daadwerkelijk over, en de
website-eisen uit de DVS zijn geen intentie meer maar een cijfer dat periodiek
wordt gemeten. `TODO: welk cijfer is goed genoeg, en wie stelt dat vast?`

## 2. Probleem

Wat er nu misgaat, en voor wie:

- **De belofte is niet meetbaar.** De DVS belooft actuele en juiste informatie als
  eerste prioriteit, maar er is geen cijfer dat zegt hoe actueel of juist de
  website op enig moment is. Zonder meting is "het is actueel" een aanname.
- **De omvang past niet bij handwerk.** Alleen paspoort en ID-kaart telt al 741
  pagina's en 477.787 woorden. De DVS stelt zelf vast dat tijd, geld en capaciteit
  beperkt zijn; alles met de hand nalezen past daar niet in.
- **Sjabloontekst vergroot elke fout.** Ruim 200 landpagina's delen dezelfde
  zinnen: 156 zinnen staan op 100 of meer pagina's. Eén verouderde zin is daarmee
  meteen een fout op honderden pagina's — en één correctie lost er net zoveel op.
  Handmatig steekproeven nemen vindt precies dit patroon niet.

**Hoe het nu gaat (huidige situatie):** `TODO: het bestaande proces, ook als dat
"handmatig, per mail" is. Dit is de nulmeting waartegen we verbetering afmeten.`

## 3. Scope

### Wel

- **Content:** de publieke pagina's van www.nederlandwereldwijd.nl, opgehaald via
  de sitemap van de site zelf. Nu: 741 pagina's over paspoort en ID-kaart.
- **Checks:** taalgebruik (fase 1). Daarna feitelijke consistentie tussen
  landpagina's: bedragen, termijnen en voorwaarden die op de ene pagina zijn
  bijgewerkt en op de andere niet.
- **Waar het ingrijpt:** naast het redactieproces, niet erin. De uitkomst is een
  rapport dat de redactie raadpleegt; er wordt niets geblokkeerd of gepubliceerd.

`TODO: op termijn — moet dit in de publicatiepijplijn gaan draaien, en van wie
is die pijplijn?`

### Niet

Expliciet buiten scope houden is de helft van de strategie:

- **Zelf content genereren of herschrijven.** De tool stelt een alternatief voor;
  de tekst aanpassen blijft mensenwerk.
- **Eindredactioneel oordeel overnemen.** Bevindingen zijn advies, geen verdict.
- **Spellingcontrole.** Geen Nederlands woordenboek beschikbaar in deze omgeving;
  een eigen lijst zou vooral namen en vaktermen als fout markeren.
- **Andere kanalen dan de website.** Geen social media, brieven of formulieren.
- **Afgeschermde of interne content.** Alleen wat publiek op de site staat.

## 4. Gebruikers en belanghebbenden

| Wie | Wat ze nodig hebben | Hoe ze het gebruiken |
| --- | --- | --- |
| Redacteur NWW | Weten wélke pagina's aandacht nodig hebben, en waarom | Opent het rapport, filtert op zekere fouten, past de tekst aan |
| Contentregie / eindredactie | Zicht op patronen: welke sjabloonzin raakt honderden pagina's | Gebruikt de groepering om te prioriteren in plaats van pagina voor pagina |
| Beleid en keten (HDCV, CSO, posten) | Signalen over wat structureel misgaat | Via de signaalfunctie uit de DVS; nog niet ingericht |

`TODO: namen en rollen invullen — wie is de vaste gebruiker, en wie ontvangt de
signalen richting beleid?`

## 5. Aanpak

De uitgangspunten die keuzes in dit project sturen:

1. **Regels vóór modellen.** Wat met een deterministische regel te checken is,
   checken we met een regel: reproduceerbaar, uitlegbaar, goedkoop. Een taalmodel
   zetten we alleen in waar beoordeling nodig is. In de praktijk betekent dit dat
   de taalcheck uit gewone tekstregels bestaat die iedereen kan nalezen.
2. **De site is zijn eigen norm.** Meting vooraf liet zien dat deze content al in
   duidelijke taal is geschreven: mediaan 9 woorden per zin, 11 ambtelijke woorden
   in 477.787. Een externe regellijst levert hier vooral ruis op. We zoeken daarom
   naar plekken die afwijken van hoe de rest van de site het doet. Bij 741
   pagina's waarvan er ruim 200 op elkaar lijken, is de uitzondering de fout.
3. **Adviseren, niet blokkeren.** Bevindingen zijn voorstellen met bron en
   onderbouwing; de redactie houdt het laatste woord. We bouwen daarom geen
   blokkade in de publicatie en schrijven geen teksten automatisch om.
4. **Elke check is uitlegbaar.** Bij iedere bevinding staat het citaat in zijn
   zin, welke regel is geraakt, waarom dat een probleem is en wat een alternatief
   is. Zonder die onderbouwing wordt een melding niet vertrouwd en niet gebruikt.
5. **Klein beginnen op echte content.** Liever drie checks die op de werkelijke
   contentstroom draaien dan twintig die alleen op testmateriaal werken.

## 6. Architectuur op hoofdlijnen

Drie stappen, elk een los script dat je apart kunt draaien. De tussenresultaten
staan als bestand in de repository, zodat je bij elke stap kunt zien wat eruit kwam.

- **Invoer:** de sitemap van de site geeft de lijst met pagina's
  (`tools/sitemap_urls.py`); `tools/crawl.py` haalt ze op en bewaart per pagina de
  platte tekst uit het `<main>`-element, dus zonder menu en voettekst.
- **Checks:** `tools/taalcheck.py`. Elke controle is een tekstregel met een vaste
  vorm: wat het zoekt, hoe ernstig het is, waarom het een probleem is, en een
  voorstel. Een controle toevoegen is één regel toevoegen.
- **Uitvoer:** `rapport/taalcheck.csv` (alles, om op door te rekenen) en
  `docs/index.html` (om te lezen en te delen), gemaakt door `tools/rapport.py`.
  Gelijke bevindingen worden gegroepeerd: één sjabloonzin verbeteren verbetert
  soms honderden pagina's.
- **Technologie:** Python met alleen de standaardbibliotheek plus `requests`, en
  één HTML-bestand zonder externe scripts. Reden: op de werklaptops kan geen
  ontwikkelsoftware worden geïnstalleerd, dus alles moet draaien in een
  browsersessie en te bekijken zijn met alleen een browser. Publicatie via GitHub
  Pages; geen server, geen database, geen accounts.

`TODO: zodra het meer wordt dan dit — verplaats het detail naar docs/architecture.md.`

## 7. Fasering

| Fase | Doel | Klaar wanneer | Stand |
| --- | --- | --- | --- |
| 0 — Verkenning | Contentstroom in kaart | 741 pagina's opgehaald en gemeten | **klaar** (15-09-2026) |
| 1 — Eerste werkende versie | Taalcheck op echte content, zichtbaar voor collega's | rapport online, redactie heeft het gezien | **loopt** |
| 2 — Bruikbaar | Redactie neemt bevindingen daadwerkelijk over | precisie gemeten, eigenaar aangewezen | `TODO: termijn` |
| 3 — Verbreden | Feitcontrole tussen landpagina's, meer onderwerpen | `TODO` | `TODO: termijn` |

## 8. Meten

### De meetlat: zes eisen uit de DVS

De DVS stelt zes eisen aan de informatie op de website. Zo staat dit project ervoor:

| Eis uit de DVS | Gedekt door de check? |
| --- | --- |
| Consistent | **Ja** — dit is precies wat de taalcheck meet |
| Toegankelijk / begrijpelijk | **Deels** — lange zinnen en formele woorden; geen leesniveautoets |
| Actueel | **Nee** — eerste prioriteit in de DVS, nog niet gebouwd |
| Juist | **Nee** |
| Volledig | **Nee** |
| Correct doorverwijzen | **Nee** |

Eén van de zes volledig gedekt. Dat is geen falen van het gebouwde, maar het
plaatst het: de taalcheck raakt een echte DVS-eis, maar niet die welke de DVS zelf
als basisinspanning aanwijst. Zie [`docs/dvs-meetlat.md`](docs/dvs-meetlat.md)
voor de uitwerking en de eerste metingen op actualiteit.

### Wat we volgen om te weten of dit werkt

- **Aandeel bevindingen dat de redactie overneemt.** Dit is de maatstaf; zolang
  dit cijfer er niet is, is elke uitspraak over bruikbaarheid een gok.
  `TODO: meten zodra de redactie het rapport heeft bekeken.`
- **Gemist bij steekproef.** Hoeveel afwijkingen vindt een redacteur met de hand
  die de tool niet meldde? `TODO: nulmeting plannen.`
- **Klopt het citaat?** Bij oplevering: 10 van 10 steekproeven kwamen letterlijk
  terug op de live pagina.
- `TODO: doorlooptijd van controle per pagina — nulmeting van het handmatige
  proces ontbreekt nog.`

Valse alarmen zijn de grootste bedreiging voor gebruik: bij te veel ruis wordt de
tool weggeklikt. Precisie weegt daarom zwaarder dan dekking.

## 9. Risico's

| Risico | Gevolg | Wat we doen |
| --- | --- | --- |
| Te veel valse meldingen | Tool wordt weggeklikt en niet meer gebruikt | Ernst per bevinding; alleen 4 teksten staan als 'zeker fout' gemarkeerd, de rest is advies |
| Geen eigenaar | Niemand draait de crawl opnieuw; het rapport veroudert stil | Openstaande vraag 1 hieronder; eigenaar vastleggen in de kop van dit document |
| Rapport is een momentopname | Redactie werkt aan bevindingen die al opgelost zijn | Datum staat op de pagina; afspraak maken over herhaalfrequentie |
| Openbare publicatie van bevindingen | Publieke uiting over de kwaliteit van een ministeriesite | Vooraf afstemmen met de teamleider; alternatief is het bestand delen zonder te publiceren |
| Privacy/AVG | — | Speelt hier niet: alleen publieke webteksten, geen persoonsgegevens, geen gebruikersinvoer die wordt opgeslagen |

## 10. Open vragen

1. **Wie beheert dit na de training?** Zonder eigenaar draait niemand de crawl
   opnieuw. Dit is de eerste vraag, en geen technische.
2. **Hoe vaak halen we de content opnieuw op?** Bepaalt hoe actueel het rapport is.
3. **Welke bevindingen zijn blokkerend en welke zijn advies?** Dat is een
   redactiebeslissing, geen technische.
4. **Mag het rapport openbaar staan?** Nu gepubliceerd via GitHub Pages op een
   publieke repository. Af te stemmen met de teamleider.

## 11. Besluiten

Vastgestelde keuzes, met datum en reden. Zo blijft navolgbaar waarom iets zo is.

| Datum | Besluit | Reden |
| --- | --- | --- |
| 15-09-2026 | Content ophalen via de sitemap, niet door zelf door te linken | Het is de lijst die de site zelf als compleet beschouwt; beleefder en betrouwbaarder |
| 15-09-2026 | Beginnen met paspoort en ID-kaart (741 pagina's) | Grootste samenhangende blok, met ruim 200 landvarianten van dezelfde sjabloontekst |
| 15-09-2026 | Taal als eerste controle, niet feitelijke juistheid | Raakt alle pagina's tegelijk en is met regels te controleren |
| 15-09-2026 | De site geldt als zijn eigen norm | Meting liet zien dat een externe regellijst hier vooral ruis oplevert |
| 15-09-2026 | Rapport als statische pagina via GitHub Pages | Er hoeft niets te worden opgeslagen; zonder opslag is een backend puur extra risico en toestemming |
| 15-09-2026 | Ruwe HTML niet in de repository (±77 MB) | Opnieuw op te halen; de platte tekst is wat we controleren |
| 15-09-2026 | De DVS is het toetsingskader, niet een losse schrijfwijzer | Maakt expliciet waaraan content wordt getoetst en wie daarover gaat |
| 15-09-2026 | De DVS zelf niet in de repository opnemen | Dit is een openbare repository en de DVS is een intern document |
| 15-09-2026 | Actualiteit wordt de volgende controle | De DVS noemt actueel en juist de basisinspanning en eerste prioriteit |
