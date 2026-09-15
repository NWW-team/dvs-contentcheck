#!/usr/bin/env python3
"""Taalcheck op opgehaalde content.

    python3 tools/taalcheck.py data/paspoort-id-kaart --out rapport

Controleert de teksten uit een crawl op taalgebruik en schrijft twee
bestanden: een volledig overzicht (`taalcheck.csv`) en een leesbare
samenvatting (`taalcheck.md`).

Uitgangspunt: de site is zijn eigen norm. Deze content is al in duidelijke
taal geschreven, dus een algemene lijst met moeilijke woorden levert weinig
op. Wat wél iets oplevert, is zoeken naar de plekken die afwijken van hoe de
rest van de site het doet. Dat zijn zeldzame, goed te controleren
bevindingen - en dat is precies wat een redactie kan gebruiken.

Elke bevinding vermeldt de regel die is geraakt, waarom dat een probleem is
en wat een alternatief is. Zonder die onderbouwing wordt een melding niet
vertrouwd en dus niet gebruikt.
"""
import argparse
import csv
import glob
import os
import re
import sys
from collections import Counter

SCHEIDING = "-" * 60

# Ernst bepaalt de volgorde in het rapport: 'hoog' is vrijwel zeker fout,
# 'advies' is een suggestie waar de redactie zelf over beslist.
HOOG, MIDDEN, ADVIES = "hoog", "midden", "advies"


class Bevinding:
    def __init__(self, regel_nr, soort, ernst, citaat, uitleg, voorstel, context=""):
        self.regel_nr = regel_nr
        self.soort = soort
        self.ernst = ernst
        self.citaat = citaat
        self.uitleg = uitleg
        self.voorstel = voorstel
        self.context = context


# --- regels ------------------------------------------------------------

AANSPREEKVORM = re.compile(r"\b(je|jij|jouw|jullie)\b")

SCHRIJFWIJZE = [
    # (afwijkende schrijfwijze, juiste schrijfwijze)
    (re.compile(r"\bID kaart\b"), "ID-kaart"),
    (re.compile(r"\bid-kaart\b"), "ID-kaart"),
    (re.compile(r"\bIDkaart\b"), "ID-kaart"),
    (re.compile(r"\bemail\b", re.I), "e-mail"),
    (re.compile(r"\bDigid\b"), "DigiD"),
    (re.compile(r"\bpas foto\b"), "pasfoto"),
    (re.compile(r"\bconsulaat generaal\b"), "consulaat-generaal"),
    (re.compile(r"\ba\.u\.b\.|\baub\b"), "alstublieft"),
]

FORMEEL = {
    "indien": "als", "dient u": "moet u", "dienen te": "moeten",
    "teneinde": "om", "alvorens": "voordat", "conform": "volgens",
    "inzake": "over", "derhalve": "daarom", "middels": "met",
    "betreffende": "over", "tevens": "ook", "voorts": "verder",
    "eveneens": "ook", "gaarne": "graag", "nagenoeg": "bijna",
    "verzoeken wij u": "vragen wij u", "in het bezit zijn van": "hebben",
}

LIJDEND = re.compile(
    r"\b(?:wordt|worden|werd|werden)\s+(?:\w+\s+){0,2}?"
    r"(ge\w{3,}|verstuurd|opgestuurd|verwerkt|verstrekt)\b")

# Een zin eindigt op leesteken + spatie + hoofdletter, of op het regeleinde.
ZINSEINDE = re.compile(r"(?<=[.!?])\s+")


def zinnen(regel):
    """Splitst een regel in zinnen; tabelrijen en kopjes blijven heel."""
    return [z.strip() for z in ZINSEINDE.split(regel) if z.strip()]


def omheen(regel, positie, marge=110):
    """De zin rond een treffer; valt terug op een stuk tekst eromheen."""
    for zin in zinnen(regel):
        start = regel.find(zin)
        if start <= positie < start + len(zin):
            return zin if len(zin) <= 300 else zin[:300] + "..."
    van, tot = max(0, positie - marge), min(len(regel), positie + marge)
    return ("..." if van else "") + regel[van:tot].strip() + ("..." if tot < len(regel) else "")


def check_regel(regel, nr, max_woorden):
    """Alle regels toepassen op één tekstregel."""
    gevonden = []

    for m in AANSPREEKVORM.finditer(regel):
        gevonden.append(Bevinding(
            nr, "aanspreekvorm", HOOG, m.group(0),
            "De site spreekt de lezer overal met 'u' aan; hier staat een je-vorm.",
            "Schrijf 'u', 'uw' of 'u heeft'.", omheen(regel, m.start())))

    for patroon, juist in SCHRIJFWIJZE:
        for m in patroon.finditer(regel):
            if m.group(0) == juist:
                continue
            gevonden.append(Bevinding(
                nr, "schrijfwijze", HOOG, m.group(0),
                "Afwijkende schrijfwijze van een term die elders op de site anders wordt geschreven.",
                "Schrijf '%s'." % juist, omheen(regel, m.start())))

    laag = regel.lower()
    for woord, alternatief in FORMEEL.items():
        m = re.search(r"\b%s\b" % re.escape(woord), laag)
        if m:
            gevonden.append(Bevinding(
                nr, "formeel-woord", MIDDEN, woord,
                "Formeel woord; in begrijpelijke taal (taalniveau B1) bestaat een gewoner alternatief.",
                "Overweeg '%s'." % alternatief, omheen(regel, m.start())))

    for m in LIJDEND.finditer(regel):
        gevonden.append(Bevinding(
            nr, "lijdende-vorm", ADVIES, m.group(0),
            "Lijdende vorm: de lezer ziet niet wie er iets doet.",
            "Schrijf actief, bijvoorbeeld 'wij sturen' of 'u ontvangt'.",
            omheen(regel, m.start())))

    for zin in zinnen(regel):
        # Alleen echte zinnen tellen: tabelrijen en kopjes eindigen niet op een punt.
        if not zin.endswith((".", "!", "?")):
            continue
        aantal = len(zin.split())
        if aantal > max_woorden:
            gevonden.append(Bevinding(
                nr, "lange-zin", ADVIES, zin[:120] + ("..." if len(zin) > 120 else ""),
                "Zin van %d woorden; boven de %d wordt een zin lastig te volgen." % (aantal, max_woorden),
                "Knip de zin in tweeën."))

    return gevonden


# --- doorlopen en rapporteren ------------------------------------------

def lees(pad):
    """Geeft (url, titel, inhoudsregels) van een tekstbestand uit de crawl."""
    regels = open(pad, encoding="utf-8").read().splitlines()
    url = regels[0] if regels else ""
    titel = regels[1] if len(regels) > 1 else ""
    try:
        start = regels.index(SCHEIDING) + 1
    except ValueError:
        start = 2
    return url, titel, regels[start:]


def controleer(map_pad, max_woorden):
    rijen = []
    bestanden = sorted(glob.glob(os.path.join(map_pad, "pages", "*.txt")))
    if not bestanden:
        sys.exit("Geen tekstbestanden gevonden in %s/pages/" % map_pad)
    for pad in bestanden:
        url, titel, inhoud = lees(pad)
        for i, regel in enumerate(inhoud, start=1):
            for b in check_regel(regel, i, max_woorden):
                rijen.append({
                    "bestand": os.path.basename(pad), "url": url, "titel": titel,
                    "regel": b.regel_nr, "soort": b.soort, "ernst": b.ernst,
                    "citaat": b.citaat, "context": b.context or b.citaat,
                    "uitleg": b.uitleg, "voorstel": b.voorstel,
                })
    return bestanden, rijen


def schrijf_csv(pad, rijen):
    velden = ["bestand", "url", "titel", "regel", "soort", "ernst", "citaat",
              "context", "uitleg", "voorstel"]
    with open(pad, "w", encoding="utf-8", newline="") as fh:
        schrijver = csv.DictWriter(fh, fieldnames=velden)
        schrijver.writeheader()
        schrijver.writerows(rijen)


def schrijf_samenvatting(pad, map_pad, bestanden, rijen, max_woorden):
    per_soort = Counter(r["soort"] for r in rijen)
    per_ernst = Counter(r["ernst"] for r in rijen)
    pagina_s = len({r["url"] for r in rijen})

    uit = ["# Taalcheck: %s" % map_pad, "",
           "%d pagina's gecontroleerd, %d bevindingen op %d pagina's."
           % (len(bestanden), len(rijen), pagina_s), "",
           "## Per soort", "", "| Soort | Ernst | Aantal |", "| --- | --- | --- |"]
    ernst_van = {r["soort"]: r["ernst"] for r in rijen}
    for soort, n in per_soort.most_common():
        uit.append("| %s | %s | %d |" % (soort, ernst_van[soort], n))

    uit += ["", "## Wat u eerst zou moeten bekijken", ""]
    hoog = [r for r in rijen if r["ernst"] == HOOG]
    if hoog:
        uit.append("%d bevindingen zijn vrijwel zeker fout. Ze staan hieronder volledig:"
                   % len(hoog))
        uit.append("")
        for r in hoog:
            uit += ["- **%s** (regel %s) - %s" % (r["citaat"], r["regel"], r["voorstel"]),
                    "  %s" % r["url"]]
    else:
        uit.append("Geen bevindingen met ernst 'hoog'.")

    advies = [r for r in rijen if r["ernst"] == ADVIES]
    if advies:
        top = Counter(r["url"] for r in advies).most_common(10)
        uit += ["", "## Pagina's met de meeste adviezen", "",
                "Adviezen (lange zinnen, lijdende vorm) zijn suggesties; de redactie beslist.",
                "", "| Aantal | Pagina |", "| --- | --- |"]
        uit += ["| %d | %s |" % (n, u) for u, n in top]

    uit += ["", "## Hoe dit is gecontroleerd", "",
            "- **aanspreekvorm** - je/jij/jouw/jullie, terwijl de site 'u' gebruikt",
            "- **schrijfwijze** - varianten van vaste termen (ID-kaart, e-mail, DigiD)",
            "- **formeel-woord** - ambtelijke woorden met een gewoner alternatief",
            "- **lijdende-vorm** - 'wordt/worden' plus voltooid deelwoord",
            "- **lange-zin** - zinnen langer dan %d woorden" % max_woorden, "",
            "Alle bevindingen met regelnummer en citaat staan in `taalcheck.csv`.",
            "", "Cijfers: %s." % ", ".join("%s %d" % (e, n) for e, n in per_ernst.most_common())]
    open(pad, "w", encoding="utf-8").write("\n".join(uit) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Controleer opgehaalde content op taalgebruik.")
    ap.add_argument("map", help="map met een crawl, bijv. data/paspoort-id-kaart")
    ap.add_argument("--out", default="rapport", help="map voor het rapport")
    ap.add_argument("--max-woorden", type=int, default=20,
                    help="een zin langer dan dit aantal woorden geldt als lang")
    args = ap.parse_args()

    bestanden, rijen = controleer(args.map, args.max_woorden)
    os.makedirs(args.out, exist_ok=True)
    schrijf_csv(os.path.join(args.out, "taalcheck.csv"), rijen)
    schrijf_samenvatting(os.path.join(args.out, "taalcheck.md"),
                         args.map, bestanden, rijen, args.max_woorden)

    per_ernst = Counter(r["ernst"] for r in rijen)
    print("%d pagina's gecontroleerd, %d bevindingen (%s)"
          % (len(bestanden), len(rijen),
             ", ".join("%s %d" % (e, n) for e, n in per_ernst.most_common())))
    print("Rapport: %s/taalcheck.md en %s/taalcheck.csv" % (args.out, args.out))


if __name__ == "__main__":
    sys.exit(main())
