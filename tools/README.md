# tools

Hulpprogramma's om content op te halen die we willen controleren. Alleen de
Python-standaardbibliotheek plus `requests`; geen installatie nodig.

## `sitemap_urls.py` — welke pagina's bestaan er?

Leest de sitemap van een site (volgt een sitemapindex automatisch door) en
schrijft de URL's naar stdout. Betrouwbaarder dan zelf doorlinken: het is
precies de lijst die de site zelf publiceert.

```bash
python3 tools/sitemap_urls.py https://www.nederlandwereldwijd.nl \
    --filter paspoort id-kaart > urls.txt
```

## `crawl.py` — haal de pagina's op

```bash
# aanbevolen: de lijst uit de sitemap ophalen
python3 tools/crawl.py https://www.nederlandwereldwijd.nl \
    --urls-file urls.txt --max-pages 800 --delay 0.4 --out data/paspoort-id-kaart

# of: zelf doorlinken vanaf een startpagina, binnen hetzelfde domein
python3 tools/crawl.py https://www.voorbeeld.nl --max-pages 50 --prefix /nieuws
```

Levert per pagina twee bestanden in `<out>/pages/` — de ruwe HTML en de platte
tekst — plus `<out>/index.csv` met URL, statuscode, titel en aantal woorden.

De tekstversie bevat alleen wat binnen `<main>` staat, dus zonder menu,
kruimelpad en voettekst; staat er geen `<main>` in de pagina, dan valt hij
terug op de hele body.

### Uitgangspunten

- **`robots.txt` wordt gerespecteerd.** `--ignore-robots` bestaat, maar gebruik
  dat alleen met expliciete toestemming van de sitebeheerder.
- **Beleefd tempo.** Standaard 1 seconde tussen verzoeken (`--delay`), één
  verzoek tegelijk.
- **Herkenbare User-Agent**, met verwijzing naar deze repo.
- **Binnen één domein.** Externe links worden niet gevolgd.
- **Bestand tegen afbreken.** `index.csv` wordt na elke pagina bijgewerkt, dus
  een onderbroken run levert nog steeds bruikbaar materiaal op.

### Netwerk

Deze omgeving mag alleen naar domeinen die in het netwerkbeleid staan; andere
hosts geven een 403 van de proxy. `www.nederlandwereldwijd.nl` is toegestaan.
