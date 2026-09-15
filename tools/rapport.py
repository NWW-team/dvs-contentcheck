#!/usr/bin/env python3
"""Maakt van de bevindingen één webpagina.

    python3 tools/rapport.py --datum 2026-09-15

Leest de bevindingen van alle controles (`rapport/*.csv`) en schrijft
`docs/index.html`: één bestand zonder externe scripts, klaar om via GitHub
Pages te publiceren.

Bevindingen met dezelfde tekst worden samengevoegd. Dat is geen cosmetica:
ruim 200 landpagina's delen dezelfde sjabloontekst, dus één zin verbeteren
verbetert honderden pagina's tegelijk. Ongegroepeerd lijkt het werk vele
malen groter dan het is.
"""
import argparse
import csv
import html
import json
import os
from collections import Counter, defaultdict

ERNST_VOLGORDE = {"hoog": 0, "midden": 1, "advies": 2}
ERNST_LABEL = {
    "hoog": "Zeker fout",
    "midden": "Ter beoordeling",
    "advies": "Advies",
}
SOORT_LABEL = {
    # taalcheck
    "aanspreekvorm": "Aanspreekvorm",
    "schrijfwijze": "Schrijfwijze",
    "formeel-woord": "Formeel woord",
    "lijdende-vorm": "Lijdende vorm",
    "lange-zin": "Lange zin",
    # actualiteitscheck
    "doodlopende-verwijzing": "Doodlopende verwijzing",
    "langdurig-tijdelijk": "Te lang tijdelijk",
    "tijdelijk-zonder-datum": "Tijdelijk zonder datum",
    "verlopen-aankondiging": "Verlopen aankondiging",
    "verloopt-binnenkort": "Verloopt binnenkort",
}


def groepeer(rijen):
    """Voegt bevindingen met dezelfde tekst samen tot één item met paginalijst."""
    groepen = defaultdict(lambda: {"paginas": []})
    for r in rijen:
        sleutel = (r["soort"], r["ernst"], r["citaat"], r["voorstel"])
        g = groepen[sleutel]
        g["soort"], g["ernst"] = r["soort"], r["ernst"]
        g["citaat"], g["voorstel"], g["uitleg"] = r["citaat"], r["voorstel"], r["uitleg"]
        g["paginas"].append({"url": r["url"], "titel": r["titel"].split(" | ")[0],
                             "context": r.get("context") or r["citaat"]})
    uit = []
    for g in groepen.values():
        # Eén pagina kan dezelfde fout twee keer bevatten. Meldingen tellen alle
        # keren, de paginalijst noemt elke pagina één keer; samen tellen de
        # meldingen op tot precies het aantal regels in de bronbestanden.
        g["meldingen"] = len(g["paginas"])
        uniek = {p["url"]: p for p in g["paginas"]}
        g["paginas"] = sorted(uniek.values(), key=lambda p: p["titel"])
        # Het citaat is bij een los woord ('je', 'Email') niet te beoordelen;
        # toon daarom de zin waarin het staat.
        g["voorbeeld"] = g["paginas"][0]["context"]
        uit.append(g)
    uit.sort(key=lambda g: (ERNST_VOLGORDE[g["ernst"]], -g["meldingen"], g["citaat"]))
    return uit


def bouw(rijen, aantal_paginas, datum):
    groepen = groepeer(rijen)
    per_ernst = Counter(g["ernst"] for g in groepen)
    paginas_met = len({r["url"] for r in rijen})

    data = json.dumps(groepen, ensure_ascii=False)
    kaarten = "".join(
        '<button class="kaart" data-ernst="%s" aria-pressed="false">'
        '<span class="kaart-getal">%d</span>'
        '<span class="kaart-label">%s</span></button>'
        % (e, per_ernst.get(e, 0), ERNST_LABEL[e])
        for e in ("hoog", "midden", "advies"))

    return TEMPLATE % {
        "datum": html.escape(datum),
        "paginas": aantal_paginas,
        "bevindingen": len(rijen),
        "groepen": len(groepen),
        "paginas_met": paginas_met,
        "kaarten": kaarten,
        "data": data.replace("</", "<\\/"),
        "soort_labels": json.dumps(SOORT_LABEL, ensure_ascii=False),
        "ernst_labels": json.dumps(ERNST_LABEL, ensure_ascii=False),
    }


TEMPLATE = """<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Contentcheck paspoort en ID-kaart | NederlandWereldwijd</title>
<style>
  :root {
    --tekst: #15202b; --zacht: #5b6b7c; --lijn: #d6dce2; --vlak: #fff;
    --grond: #f4f6f8; --accent: #154273; --hoog: #a3140f; --midden: #8c5000;
    --advies: #3a6b35; --rand: 1px solid var(--lijn);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --tekst: #e8edf2; --zacht: #9fb0c0; --lijn: #2c3a48; --vlak: #17212b;
      --grond: #0e161e; --accent: #7aa7d9; --hoog: #ff8f88; --midden: #e3a955;
      --advies: #8fc98a;
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--grond); color: var(--tekst);
    font: 16px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  .wrap { max-width: 860px; margin: 0 auto; padding: 24px 16px 64px; }
  header { border-bottom: 3px solid var(--accent); padding-bottom: 20px; margin-bottom: 24px; }
  h1 { font-size: 1.6rem; line-height: 1.25; margin: 0 0 8px; }
  .onder { color: var(--zacht); margin: 0; font-size: .95rem; }
  .cijfers { display: flex; flex-wrap: wrap; gap: 8px; margin: 20px 0 8px; }
  .kaart {
    flex: 1 1 150px; text-align: left; background: var(--vlak); border: var(--rand);
    border-radius: 8px; padding: 12px 14px; cursor: pointer; color: inherit;
    font: inherit; display: flex; flex-direction: column; gap: 2px;
  }
  .kaart:hover { border-color: var(--accent); }
  .kaart[aria-pressed="true"] { border-color: var(--accent); box-shadow: inset 0 0 0 2px var(--accent); }
  .kaart-getal { font-size: 1.7rem; font-weight: 700; line-height: 1.1; }
  .kaart-label { color: var(--zacht); font-size: .85rem; }
  .kaart[data-ernst="hoog"] .kaart-getal { color: var(--hoog); }
  .kaart[data-ernst="midden"] .kaart-getal { color: var(--midden); }
  .kaart[data-ernst="advies"] .kaart-getal { color: var(--advies); }
  .zoek {
    width: 100%%; padding: 11px 13px; font: inherit; color: inherit;
    background: var(--vlak); border: var(--rand); border-radius: 8px; margin-top: 8px;
  }
  .status { color: var(--zacht); font-size: .9rem; margin: 14px 0 10px; }
  .item { background: var(--vlak); border: var(--rand); border-radius: 8px;
          padding: 14px 16px; margin-bottom: 10px; }
  .kop { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 8px; }
  .merk { font-size: .75rem; text-transform: uppercase; letter-spacing: .04em;
          font-weight: 700; padding: 2px 8px; border-radius: 99px; border: var(--rand); }
  .merk.hoog { color: var(--hoog); border-color: currentColor; }
  .merk.midden { color: var(--midden); border-color: currentColor; }
  .merk.advies { color: var(--advies); border-color: currentColor; }
  .soort { color: var(--zacht); font-size: .85rem; }
  .aantal { margin-left: auto; color: var(--zacht); font-size: .85rem; }
  blockquote {
    margin: 0 0 10px; padding: 9px 13px; border-left: 3px solid var(--accent);
    background: var(--grond); border-radius: 0 6px 6px 0; overflow-wrap: anywhere;
  }
  .uitleg { margin: 0 0 6px; color: var(--zacht); font-size: .92rem; }
  .voorstel { margin: 0; font-weight: 600; }
  details { margin-top: 10px; }
  summary { cursor: pointer; color: var(--accent); font-size: .9rem; }
  details ul { margin: 8px 0 0; padding-left: 20px; }
  details li { margin: 3px 0; font-size: .9rem; overflow-wrap: anywhere; }
  a { color: var(--accent); }
  footer { margin-top: 40px; padding-top: 20px; border-top: var(--rand);
           color: var(--zacht); font-size: .9rem; }
  footer h2 { font-size: 1.05rem; color: var(--tekst); margin: 0 0 8px; }
  footer ul { padding-left: 20px; }
  .leeg { text-align: center; padding: 36px 16px; color: var(--zacht); }
  mark { background: #ffe8a3; color: inherit; padding: 0 2px; border-radius: 3px; font-weight: 600; }
  @media (prefers-color-scheme: dark) { mark { background: #6b5415; color: #fff6dc; } }
  .ctx { display: block; color: var(--zacht); font-size: .85rem; margin-top: 2px; }
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1>Contentcheck: paspoort en ID-kaart</h1>
  <p class="onder">
    %(paginas)d pagina&#39;s van www.nederlandwereldwijd.nl gecontroleerd.
    Content opgehaald op %(datum)s.
  </p>
</header>

<p class="onder">
  <strong>%(bevindingen)d bevindingen</strong> op %(paginas_met)d pagina&#39;s, samen te
  vatten als <strong>%(groepen)d unieke teksten</strong>. Veel landpagina&#39;s delen
  dezelfde sjabloontekst: &eacute;&eacute;n zin verbeteren verbetert soms honderden
  pagina&#39;s tegelijk.
</p>
<p class="onder">
  Gecontroleerd op <strong>taalgebruik</strong> en op <strong>actualiteit en
  doorverwijzing</strong> &mdash; twee eisen die de Dienstverleningsstrategie aan de
  informatie op de website stelt.
</p>

<div class="cijfers">%(kaarten)s</div>
<input class="zoek" id="zoek" type="search" placeholder="Zoek in bevindingen, bijvoorbeeld: ID kaart">

<p class="status" id="status"></p>
<div id="lijst"></div>

<footer>
  <h2>Hoe dit is gecontroleerd</h2>
  <p>
    Deze content is al in duidelijke taal geschreven: mediaan 9 woorden per zin en
    nauwelijks ambtelijke woorden. Een algemene regellijst levert hier weinig op.
    Daarom geldt de site als zijn eigen norm en wordt gezocht naar plekken die
    afwijken van hoe de rest van de site het doet.
  </p>
  <ul>
    <li><strong>Aanspreekvorm</strong> &mdash; je, jij of jouw, terwijl de site 19.484 keer &#39;u&#39; gebruikt</li>
    <li><strong>Schrijfwijze</strong> &mdash; varianten van vaste termen: ID-kaart, e-mail, DigiD</li>
    <li><strong>Formeel woord</strong> &mdash; ambtelijk woord met een gewoner alternatief</li>
    <li><strong>Lijdende vorm</strong> &mdash; wordt of worden plus voltooid deelwoord</li>
    <li><strong>Lange zin</strong> &mdash; zinnen langer dan 20 woorden</li>
  </ul>
  <p>
    Daarnaast wordt gecontroleerd of informatie nog actueel is en of een klant die
    hier niet geholpen wordt, weet waar dan wel:
  </p>
  <ul>
    <li><strong>Doodlopende verwijzing</strong> &mdash; verwijst naar &#39;een omringend land&#39; zonder te zeggen welk</li>
    <li><strong>Te lang tijdelijk</strong> &mdash; een tijdelijke mededeling met de datum erbij; de duur staat erbij, de grens trekt de redactie</li>
    <li><strong>Tijdelijk zonder datum</strong> &mdash; niet te zien hoe lang het er al staat</li>
    <li><strong>Verlopen aankondiging</strong> &mdash; een datum die voorbij is</li>
    <li><strong>Verloopt binnenkort</strong> &mdash; een datum binnen 30 dagen</li>
  </ul>
  <h2>Wat hier niet in staat</h2>
  <p>
    Geen spellingcontrole, geen controle op feitelijke juistheid van bedragen en
    termijnen, en geen oordeel over de inhoud. Dit is een hulpmiddel voor de
    redactie, geen volledige toets: de tool stelt voor, de redactie beslist.
  </p>
  <p>
    Gemaakt met <a href="https://github.com/NWW-team/dvs-contentcheck">dvs-contentcheck</a>.
    Momentopname van %(datum)s; de site kan sindsdien zijn aangepast.
  </p>
</footer>

</div>
<script>
const GROEPEN = %(data)s;
const SOORT = %(soort_labels)s;
const ERNST = %(ernst_labels)s;

const lijst = document.getElementById('lijst');
const status = document.getElementById('status');
const zoek = document.getElementById('zoek');
const kaarten = [...document.querySelectorAll('.kaart')];
let ernstFilter = null;

function escape(s) {
  return String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function markeer(zin, term) {
  // Zonder reguliere expressie: de term kan leestekens bevatten.
  const veilig = escape(zin);
  if (!term || term === zin) return veilig;
  const t = escape(term);
  const i = veilig.toLowerCase().indexOf(t.toLowerCase());
  if (i < 0) return veilig;
  return veilig.slice(0, i) + '<mark>' + veilig.slice(i, i + t.length) + '</mark>'
       + veilig.slice(i + t.length);
}

function paginaLijst(g) {
  if (!g.paginas.length) return '';
  const toonContext = g.soort !== 'lange-zin';
  const items = g.paginas.map(p =>
    `<li><a href="${escape(p.url)}" target="_blank" rel="noopener">${escape(p.titel)}</a>` +
    (toonContext ? `<span class="ctx">${markeer(p.context, g.citaat)}</span>` : '') +
    `</li>`).join('');
  const n = g.paginas.length;
  const woord = n === 1 ? 'pagina' : "pagina's";
  return `<details><summary>Op ${n} ${woord}</summary><ul>${items}</ul></details>`;
}

function toon() {
  const term = zoek.value.trim().toLowerCase();
  const zichtbaar = GROEPEN.filter(g =>
    (!ernstFilter || g.ernst === ernstFilter) &&
    (!term || (g.citaat + ' ' + g.voorstel + ' ' + SOORT[g.soort]).toLowerCase().includes(term)));

  const meldingen = zichtbaar.reduce((n, g) => n + g.meldingen, 0);
  status.textContent = zichtbaar.length
    ? `${zichtbaar.length} unieke ${zichtbaar.length === 1 ? 'tekst' : 'teksten'}, samen ${meldingen} ${meldingen === 1 ? 'bevinding' : 'bevindingen'}.`
    : '';

  lijst.innerHTML = zichtbaar.length ? zichtbaar.map(g => `
    <article class="item">
      <div class="kop">
        <span class="merk ${g.ernst}">${escape(ERNST[g.ernst])}</span>
        <span class="soort">${escape(SOORT[g.soort])}</span>
        <span class="aantal">${g.meldingen}&times;</span>
      </div>
      <blockquote>${markeer(g.voorbeeld, g.citaat)}</blockquote>
      <p class="uitleg">${escape(g.uitleg)}</p>
      <p class="voorstel">${escape(g.voorstel)}</p>
      ${paginaLijst(g)}
    </article>`).join('')
    : '<p class="leeg">Niets gevonden. Pas het zoekwoord of het filter aan.</p>';
}

kaarten.forEach(k => k.addEventListener('click', () => {
  const e = k.dataset.ernst;
  ernstFilter = ernstFilter === e ? null : e;
  kaarten.forEach(x => x.setAttribute('aria-pressed', String(x.dataset.ernst === ernstFilter)));
  toon();
}));
zoek.addEventListener('input', toon);
toon();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Maak een webpagina van de bevindingen.")
    ap.add_argument("--bevindingen", nargs="+",
                    default=["rapport/taalcheck.csv", "rapport/actualiteitscheck.csv"],
                    help="een of meer CSV-bestanden met bevindingen")
    ap.add_argument("--crawl", default="data/paspoort-id-kaart/index.csv")
    ap.add_argument("--uit", default="docs/index.html")
    ap.add_argument("--datum", default="15 september 2026", help="datum van de crawl")
    args = ap.parse_args()

    rijen = []
    for pad in args.bevindingen:
        if not os.path.exists(pad):
            print("overgeslagen (bestaat niet): %s" % pad)
            continue
        rijen.extend(csv.DictReader(open(pad, encoding="utf-8")))
    aantal_paginas = sum(1 for _ in csv.DictReader(open(args.crawl, encoding="utf-8")))

    os.makedirs(os.path.dirname(args.uit), exist_ok=True)
    pagina = bouw(rijen, aantal_paginas, args.datum)
    open(args.uit, "w", encoding="utf-8").write(pagina)
    print("%s geschreven: %d bevindingen, %.0f kB"
          % (args.uit, len(rijen), len(pagina.encode("utf-8")) / 1024))


if __name__ == "__main__":
    main()
