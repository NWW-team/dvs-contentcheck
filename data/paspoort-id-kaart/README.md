# Content: paspoort en ID-kaart

Opgehaald van **www.nederlandwereldwijd.nl** (Ministerie van Buitenlandse Zaken)
op **15 september 2026**. Dit is de ruwe grondstof voor de contentcheck, niet
het resultaat ervan.

## Wat er in zit

| Bestand | Inhoud |
| --- | --- |
| `urls.txt` | de 741 URL's, zoals gevonden in de sitemap van de site |
| `index.csv` | per pagina: URL, statuscode, titel, aantal woorden, bestandsnaam |
| `pages/*.txt` | per pagina de platte tekst (regel 1 = URL, regel 2 = titel) |

De ruwe HTML wordt niet meegeleverd (±77 MB). Die is opnieuw op te halen met
het commando onderaan.

## Omvang

- 741 pagina's, alle met statuscode 200 — geen fouten, geen dode links
- 477.787 woorden in totaal
- mediaan 715 woorden per pagina; kortste 31, langste 2.881

## Hoe de 741 pagina's zijn opgebouwd

| Deel | Aantal | Inhoud |
| --- | --- | --- |
| `/paspoort-id-kaart/nooddocument/…` | 220 | per land: nooddocument aanvragen |
| `/paspoort-id-kaart/buitenland/…` | 219 | per land: paspoort aanvragen vanuit dat land |
| `/paspoort-id-kaart/nederlandse-pasfotos-laten-maken/…` | 219 | per land: waar pasfoto's laten maken |
| `/reizen-paspoort-id-kaart/<land>` | 50 | per land: welk document nodig is om te reizen |
| `/paspoort-id-kaart/<onderwerp>` | 28 | algemeen: aanvragen, kosten, verlopen, kwijt/gestolen, pasfoto-eisen, kind, status |
| overig | 7 | BSN op paspoort, naamswijziging, DigiD met ID-kaart, visum |

De drie blokken van ruim 200 landvarianten zijn sjabloonteksten die per land
afwijken. Juist daar ontstaan verschillen die een contentcheck kan opsporen:
bedragen, termijnen en voorwaarden die op de ene landpagina zijn bijgewerkt en
op de andere niet.

## Opnieuw ophalen

```bash
python3 tools/sitemap_urls.py https://www.nederlandwereldwijd.nl \
    --filter paspoort id-kaart > data/paspoort-id-kaart/urls.txt

python3 tools/crawl.py https://www.nederlandwereldwijd.nl \
    --urls-file data/paspoort-id-kaart/urls.txt \
    --max-pages 800 --delay 0.4 --out data/paspoort-id-kaart
```

Duurt ongeveer 25 minuten: één pagina tegelijk, met pauze ertussen, omdat we
een site van een ander niet willen belasten. `robots.txt` van de site staat dit
toe; alleen `/zoeken` en `/api` zijn uitgesloten en die raken we niet.
