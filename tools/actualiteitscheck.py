#!/usr/bin/env python3
"""Controleert opgehaalde content op actualiteit en doorverwijzingen.

    python3 tools/actualiteitscheck.py data/paspoort-id-kaart --out rapport

Toetst twee eisen uit de Dienstverleningsstrategie die de taalcheck niet dekt:
informatie moet actueel zijn, en wie hier niet geholpen wordt moet weten waar
dan wel. Zie docs/actualiteitscheck-plan.md.

Wat er niet gemeld wordt is net zo bepalend als wat wel: de meting vooraf liet
zien dat zoeken op het woord "tijdelijk" voor 92% ruis oplevert (de definitiezin
over nooddocumenten), en dat een datum in het verleden meestal een historisch
feit is en geen veroudering.
"""
import argparse
import datetime
import os
import re
import unicodedata
import sys
from collections import Counter

from taalcheck import HOOG, MIDDEN, ADVIES, lees, zinnen

MAANDEN = {m: i for i, m in enumerate(
    "januari februari maart april mei juni juli augustus september oktober "
    "november december".split(), 1)}
DATUM = re.compile(r'\b(\d{1,2})\s+(%s)\s+(\d{4})\b' % "|".join(MAANDEN), re.I)

# Een datum is hier het onderwerp, niet de houdbaarheid: "afgegeven op of na
# 13 maart 2021" hoort er juist te staan.
HISTORISCH = re.compile(
    r'\b(?:afgegeven|afgiftedatum|geboren|uitgegeven|van voor|van vóór|op of na|'
    r'verlopen op|verstreken|overgangsperiode|model)\b', re.I)
# Aankondigingen verlopen wél: na de datum hoort de mededeling weg.
AANKONDIGING = re.compile(
    r'\b(?:bezoek|bezoekt|pop-?up|spreekuur|zittingsdag|afspraak|afspraken|'
    r'inloop|aanwezig|houdt zitting)\b', re.I)
TIJDELIJK = re.compile(r'\btijdelijk\b', re.I)
# "Tijdelijk" telt alleen als het over de dienstverlening gaat. In "Bent u
# tijdelijk in Nederland?" beschrijft het de situatie van de lezer, en in
# "bewijs van tijdelijk legaal verblijf" is het een documentnaam - dat zijn
# geen mededelingen die ooit verlopen.
DIENSTVERLENING = re.compile(
    r'\b(?:aanvragen|aanvraag|ophalen|opgehaald|gesloten|dicht|geopend|open|'
    r'beschikbaar|bereikbaar|verstrekt|uitgereikt|stilgelegd|opgeschort)\b', re.I)
# De definitiezin over nooddocumenten is uitleg, geen tijdelijke mededeling.
DEFINITIE = re.compile(r'nooddocument\s+is\s+een\s+tijdelijk|tijdelijk\s+reisdocument', re.I)

GEEN_INFO = re.compile(r'\bgeen informatie over\b[^.\n]*', re.I)
VAAG = re.compile(r'\b(?:een omringend land|een ander land|een land in de buurt|'
                  r'omringende landen|andere landen)\b', re.I)
EINDE_BLOK = re.compile(r'\bOok nuttig\b', re.I)
# Een concrete bestemming is een eigennaam die niet het land van de pagina zelf is.
EIGENNAAM = re.compile(r'\b[A-Z][a-zéëïöü]{2,}(?:[- ][A-Z][a-z]{2,})*\b')
NIET_BESTEMMING = {"Nederland", "Nederlandse", "Nederlands", "Ook", "Eisen", "Paspoort",
                   "Schengenvisum", "Mvv", "De", "Het", "Een", "Bent", "Ga", "Download",
                   "Neem", "In", "Als", "Wij", "We", "Deze", "Dit", "Wilt", "Kunt", "Voor",
                   "Meer", "Bekijk", "Lees", "Vraag", "Maak", "Let", "Waarschuwing", "Contact"}


def datum_van(m):
    return datetime.date(int(m.group(3)), MAANDEN[m.group(2).lower()], int(m.group(1)))


def dagen_woord(n):
    return "%d dag" % n if n == 1 else "%d dagen" % n


def vergelijkbaar(naam):
    """Naam zonder accenten en scheidingstekens, zodat 'Armenië' en 'armenie'
    hetzelfde worden — de URL van een pagina kent die tekens niet."""
    plat = unicodedata.normalize("NFKD", naam)
    plat = "".join(c for c in plat if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", plat.lower())


def bestemming_genoemd(staart, eigen_land):
    """Staat er een concreet land in de tekst na 'geen informatie over'?"""
    blok = EINDE_BLOK.split(staart)[0]
    eigen = vergelijkbaar(eigen_land)
    for m in EIGENNAAM.finditer(blok):
        naam = m.group(0)
        if naam in NIET_BESTEMMING or vergelijkbaar(naam) in eigen:
            continue
        # Een hoofdletter direct na een punt is een zinsbegin, geen opsomming.
        voor = blok[max(0, m.start() - 2):m.start()]
        if voor.endswith(". ") or m.start() == 0:
            continue
        return naam
    return None


def land_van(url):
    return url.rstrip("/").rsplit("/", 1)[-1].replace("pasfoto-", "").replace("-", " ")


def controleer_pagina(url, titel, inhoud, peildatum):
    """Alle controles op één pagina; geeft bevindingen terug."""
    tekst = "\n".join(inhoud)
    gevonden = []

    # 1. Doorverwijzing die nergens heen wijst.
    for m in GEEN_INFO.finditer(tekst):
        staart = tekst[m.start():m.start() + 500]
        if not VAAG.search(staart):
            continue
        if bestemming_genoemd(staart, land_van(url)):
            continue
        zin = next((z for z in zinnen(staart) if VAAG.search(z)), staart[:200])
        gevonden.append({
            "soort": "doodlopende-verwijzing", "ernst": HOOG,
            "citaat": "geen informatie over ...", "context": zin.strip()[:300],
            "ouderdom": "",
            "uitleg": "De pagina verwijst door naar 'een omringend land' zonder te "
                      "zeggen welk land. De klant weet niet waar hij verder moet zoeken.",
            "voorstel": "Noem de landen waar wél informatie over is, zoals op de "
                        "pagina over Afghanistan gebeurt."})

    # 2. Tijdelijke mededelingen: hoe lang staan ze er al?
    for regel in inhoud:
        for zin in zinnen(regel):
            if not TIJDELIJK.search(zin) or DEFINITIE.search(zin):
                continue
            if not DIENSTVERLENING.search(zin):
                continue
            m = DATUM.search(zin)
            if m:
                dagen = (peildatum - datum_van(m)).days
                if dagen < 0:
                    continue
                gevonden.append({
                    "soort": "langdurig-tijdelijk", "ernst": HOOG,
                    "citaat": "tijdelijk sinds %s" % m.group(0),
                    "context": zin.strip()[:300], "ouderdom": dagen,
                    "uitleg": "Deze mededeling staat er %s en heet nog steeds tijdelijk."
                              % dagen_woord(dagen),
                    "voorstel": "Controleer of dit nog klopt; zo ja, schrijf op tot "
                                "wanneer het geldt."})
            else:
                gevonden.append({
                    "soort": "tijdelijk-zonder-datum", "ernst": MIDDEN,
                    "citaat": "tijdelijk", "context": zin.strip()[:300], "ouderdom": "",
                    "uitleg": "Tijdelijke mededeling zonder datum: niet te zien hoe "
                              "lang dit er al staat of wanneer het afloopt.",
                    "voorstel": "Zet erbij sinds wanneer dit geldt, of tot wanneer."})

    # 3 en 4. Datums in aankondigingen: verlopen, of bijna.
    for regel in inhoud:
        for zin in zinnen(regel):
            if HISTORISCH.search(zin) or TIJDELIJK.search(zin):
                continue
            for m in DATUM.finditer(zin):
                d = datum_van(m)
                dagen = (d - peildatum).days
                if dagen < 0 and AANKONDIGING.search(zin):
                    gevonden.append({
                        "soort": "verlopen-aankondiging", "ernst": HOOG,
                        "citaat": m.group(0), "context": zin.strip()[:300],
                        "ouderdom": -dagen,
                        "uitleg": "Aankondiging voor een datum die %s geleden is "
                                  "gepasseerd." % dagen_woord(-dagen),
                        "voorstel": "Haal de mededeling weg of vervang hem door de "
                                    "eerstvolgende datum."})
                elif 0 <= dagen <= 30:
                    gevonden.append({
                        "soort": "verloopt-binnenkort", "ernst": ADVIES,
                        "citaat": m.group(0), "context": zin.strip()[:300],
                        "ouderdom": dagen,
                        "uitleg": "Deze datum is over %s voorbij; daarna klopt de "
                                  "tekst niet meer." % dagen_woord(dagen),
                        "voorstel": "Zet een herinnering om dit na die datum bij te werken."})
    return gevonden


def controleer(map_pad, peildatum):
    import glob
    rijen = []
    bestanden = sorted(glob.glob(os.path.join(map_pad, "pages", "*.txt")))
    if not bestanden:
        sys.exit("Geen tekstbestanden gevonden in %s/pages/" % map_pad)
    for pad in bestanden:
        url, titel, inhoud = lees(pad)
        for b in controleer_pagina(url, titel, inhoud, peildatum):
            b.update({"bestand": os.path.basename(pad), "url": url, "titel": titel,
                      "regel": ""})
            rijen.append(b)
    return bestanden, rijen


def schrijf_samenvatting(pad, bestanden, rijen, peildatum):
    per_soort = Counter(r["soort"] for r in rijen)
    uit = ["# Actualiteitscheck", "",
           "%d pagina's gecontroleerd op peildatum %s; %d bevindingen."
           % (len(bestanden), peildatum, len(rijen)), "",
           "| Soort | Aantal |", "| --- | --- |"]
    uit += ["| %s | %d |" % (s, n) for s, n in per_soort.most_common()]
    hoog = [r for r in rijen if r["ernst"] == HOOG and r["soort"] != "doodlopende-verwijzing"]
    if hoog:
        uit += ["", "## Verlopen of te lang tijdelijk", ""]
        for r in sorted(hoog, key=lambda r: -(r["ouderdom"] or 0)):
            uit += ["- **%s** (%s) — %s" % (r["citaat"], dagen_woord(r["ouderdom"]), r["url"]),
                    "  > %s" % r["context"]]
    dood = [r for r in rijen if r["soort"] == "doodlopende-verwijzing"]
    if dood:
        uit += ["", "## Doodlopende verwijzingen", "",
                "%d pagina's verwijzen naar 'een omringend land' zonder te zeggen welk. "
                "Het is sjabloontekst, dus één aanpassing helpt ze allemaal." % len(dood), ""]
        uit += ["- %s" % r["url"] for r in dood[:10]]
        if len(dood) > 10:
            uit.append("- ... en nog %d" % (len(dood) - 10))
    open(pad, "w", encoding="utf-8").write("\n".join(uit) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Controleer content op actualiteit.")
    ap.add_argument("map", help="map met een crawl, bijv. data/paspoort-id-kaart")
    ap.add_argument("--out", default="rapport")
    ap.add_argument("--peildatum", default=datetime.date.today().isoformat(),
                    help="datum waartegen wordt gerekend (JJJJ-MM-DD)")
    args = ap.parse_args()
    peildatum = datetime.date.fromisoformat(args.peildatum)

    bestanden, rijen = controleer(args.map, peildatum)
    os.makedirs(args.out, exist_ok=True)
    velden = ["bestand", "url", "titel", "regel", "soort", "ernst", "citaat",
              "context", "ouderdom", "uitleg", "voorstel"]
    import csv
    with open(os.path.join(args.out, "actualiteitscheck.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=velden)
        w.writeheader()
        w.writerows(rijen)
    schrijf_samenvatting(os.path.join(args.out, "actualiteitscheck.md"),
                         bestanden, rijen, peildatum)

    per = Counter("%s/%s" % (r["ernst"], r["soort"]) for r in rijen)
    print("%d pagina's gecontroleerd, %d bevindingen" % (len(bestanden), len(rijen)))
    for k, n in per.most_common():
        print("  %-40s %d" % (k, n))


if __name__ == "__main__":
    sys.exit(main())
