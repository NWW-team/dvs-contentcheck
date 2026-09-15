# dvs-contentcheck

Controleert of de content van www.nederlandwereldwijd.nl de beloften waarmaakt uit
de Dienstverleningsstrategie van NederlandWereldwijd: informatie die actueel,
juist, consistent en begrijpelijk is. De tool adviseert; de redactie beslist.

Welke eisen dat precies zijn en hoeveel ervan al gedekt zijn (één van de zes),
staat in [`docs/dvs-meetlat.md`](docs/dvs-meetlat.md).

**Het rapport:** https://nww-team.github.io/dvs-contentcheck/

## Wat er nu werkt

741 pagina's over paspoort en ID-kaart zijn opgehaald en gecontroleerd op
taalgebruik. Dat leverde 1.651 bevindingen op, samen te vatten als 439 unieke
teksten — veel landpagina's delen dezelfde sjabloonzin, dus één zin verbeteren
verbetert soms honderden pagina's tegelijk.

Vier teksten zijn vrijwel zeker fout: een ontbrekend streepje in `ID kaart`, zes
keer `Email` in plaats van `E-mail`, en twee plekken waar de lezer met `je` wordt
aangesproken terwijl de site overal `u` gebruikt.

## Zelf draaien

Alles draait met Python, zonder installatie van extra pakketten.

```bash
# 1. welke pagina's bestaan er?
python3 tools/sitemap_urls.py https://www.nederlandwereldwijd.nl \
    --filter paspoort id-kaart > data/paspoort-id-kaart/urls.txt

# 2. de pagina's ophalen (duurt ±25 minuten; één pagina tegelijk, netjes)
python3 tools/crawl.py https://www.nederlandwereldwijd.nl \
    --urls-file data/paspoort-id-kaart/urls.txt \
    --max-pages 800 --delay 0.4 --out data/paspoort-id-kaart

# 3. controleren op taalgebruik
python3 tools/taalcheck.py data/paspoort-id-kaart --out rapport

# 4. er een webpagina van maken
python3 tools/rapport.py --datum "15 september 2026"
```

## Wegwijs

| Map | Inhoud |
| --- | --- |
| `tools/` | de scripts, met uitleg in `tools/README.md` |
| `data/` | de opgehaalde teksten per pagina |
| `rapport/` | alle bevindingen als CSV en als samenvatting |
| `docs/` | de webpagina die via GitHub Pages wordt gepubliceerd |

Waarom dit project bestaat en welke keuzes er zijn gemaakt, staat in
[`STRATEGY.md`](STRATEGY.md). Het plan voor de taalcheck staat in
[`docs/taalcheck-plan.md`](docs/taalcheck-plan.md).

## Let op

Het rapport is een momentopname van 15 september 2026. De site kan sindsdien zijn
aangepast; draai de stappen opnieuw voor een actueel beeld.
