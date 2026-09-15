#!/usr/bin/env python3
"""Haalt alle pagina-URL's uit de sitemap van een site.

    python3 sitemap_urls.py https://www.nederlandwereldwijd.nl > urls.txt
    python3 sitemap_urls.py https://www.nederlandwereldwijd.nl --filter paspoort id-kaart

Volgt een sitemapindex automatisch door naar de onderliggende sitemaps, zodat
je met één aanroep de volledige lijst krijgt. Betrouwbaarder en beleefder dan
zelf doorlinken: het is precies de lijst die de site zelf publiceert.
"""
import argparse
import os
import re
import sys
from urllib.parse import urljoin

import requests

UA = "dvs-contentcheck-crawler/0.1 (+https://github.com/NWW-team/dvs-contentcheck)"
LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.I)


def session():
    s = requests.Session()
    s.headers["User-Agent"] = UA
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        s.verify = ca
    return s


def locs(url, s, timeout):
    resp = s.get(url, timeout=timeout)
    resp.raise_for_status()
    return LOC.findall(resp.text), "<sitemapindex" in resp.text.lower()


def collect(start, s, timeout):
    """Alle URL's onder een sitemap of sitemapindex, één niveau diep gevolgd."""
    found, is_index = locs(start, s, timeout)
    if not is_index:
        return found
    urls = []
    for child in found:
        try:
            child_urls, _ = locs(child, s, timeout)
        except Exception as exc:
            print(f"overgeslagen {child}: {exc}", file=sys.stderr)
            continue
        print(f"{len(child_urls):>6} URL's uit {child}", file=sys.stderr)
        urls.extend(child_urls)
    return urls


def main():
    ap = argparse.ArgumentParser(description="Lees pagina-URL's uit een sitemap.")
    ap.add_argument("site", help="site-URL of directe sitemap-URL")
    ap.add_argument("--filter", nargs="*", default=[],
                    help="houd alleen URL's die één van deze woorden bevatten")
    ap.add_argument("--timeout", type=float, default=30.0)
    args = ap.parse_args()

    start = args.site if args.site.endswith(".xml") else urljoin(args.site, "/sitemap.xml")
    urls = sorted(set(collect(start, session(), args.timeout)))
    if args.filter:
        urls = [u for u in urls if any(w.lower() in u.lower() for w in args.filter)]
    print(f"{len(urls)} URL's", file=sys.stderr)
    print("\n".join(urls))


if __name__ == "__main__":
    sys.exit(main())
