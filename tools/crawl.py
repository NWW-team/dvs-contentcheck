#!/usr/bin/env python3
"""Beleefde site-crawler voor dvs-contentcheck (alleen stdlib + requests).

Twee manieren van werken:

  # 1. zelf doorlinken vanaf een startpagina, binnen hetzelfde domein
  python3 crawl.py https://www.voorbeeld.nl --max-pages 50 --out ./crawl

  # 2. een vaste lijst URL's ophalen (bijv. uit de sitemap) - aanbevolen
  python3 crawl.py https://www.voorbeeld.nl --urls-file urls.txt --out ./crawl

Per pagina worden de HTML en de platte tekst weggeschreven; index.csv houdt
url, status, titel en aantal woorden bij en wordt na elke pagina bijgewerkt,
zodat een afgebroken run niets verliest.
"""
import argparse
import csv
import os
import re
import sys
import time
import urllib.robotparser
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urldefrag

import requests

UA = "dvs-contentcheck-crawler/0.1 (+https://github.com/NWW-team/dvs-contentcheck)"
SKIP_EXT = (".pdf", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico",
            ".zip", ".mp4", ".mp3", ".woff", ".woff2", ".ttf", ".css", ".js")
DROP_TAGS = {"script", "style", "noscript", "template", "svg"}
CHROME_TAGS = {"nav", "header", "footer", "aside"}
BREAK_TAGS = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6"}
FIELDS = ["url", "status", "titel", "woorden", "bestand"]


class Page(HTMLParser):
    """Haalt links, titel en zichtbare tekst uit een HTML-pagina.

    De tekst wordt twee keer verzameld: alles, en alleen wat binnen <main>
    staat. Voor een contentcheck is die tweede versie bruikbaarder, omdat
    menu, kruimelpad en voettekst er niet in zitten.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.text, self.main = [], [], []
        self.title = ""
        self._skip = 0          # binnen script/style e.d.
        self._chrome = 0        # binnen nav/header/footer/aside
        self._main = 0          # binnen <main>
        self._in_title = False
        self.has_main = False

    def _push(self, chunk):
        if self._skip:
            return
        self.text.append(chunk)
        if self._main and not self._chrome:
            self.main.append(chunk)

    def handle_starttag(self, tag, attrs):
        if tag in DROP_TAGS:
            self._skip += 1
            return
        if tag == "main":
            self._main += 1
            self.has_main = True
        elif tag in CHROME_TAGS:
            self._chrome += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
        if tag in BREAK_TAGS or tag in ("main",) or tag in CHROME_TAGS:
            self._push("\n")

    def handle_endtag(self, tag):
        if tag in DROP_TAGS:
            self._skip = max(0, self._skip - 1)
        elif tag == "main":
            self._main = max(0, self._main - 1)
        elif tag in CHROME_TAGS:
            self._chrome = max(0, self._chrome - 1)
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()
        else:
            self._push(data)

    @staticmethod
    def _tidy(chunks):
        raw = "".join(chunks)
        raw = re.sub(r"[ \t\r\f\v]+", " ", raw)
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        return "\n".join(line.strip() for line in raw.splitlines()).strip()

    def plain_text(self):
        """Tekst van de hoofdinhoud; valt terug op de hele pagina."""
        if self.has_main:
            body = self._tidy(self.main)
            if body:
                return body
        return self._tidy(self.text)


def normalise(url):
    """Fragment eraf, standaardpoort eraf, leeg pad wordt /."""
    url, _ = urldefrag(url)
    p = urlparse(url)
    netloc = p.netloc.replace(":443", "").replace(":80", "")
    return p._replace(netloc=netloc, path=p.path or "/", params="").geturl()


def slug(url, n):
    p = urlparse(url)
    name = (p.path + ("?" + p.query if p.query else "")).strip("/")
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name) or "index"
    return f"{n:04d}_{name[:80]}"


def write_index(out_dir, rows):
    with open(os.path.join(out_dir, "index.csv"), "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def load_robots(start, session):
    robots = urllib.robotparser.RobotFileParser()
    url = urljoin(start, "/robots.txt")
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        robots.parse(resp.text.splitlines())
        print(f"robots.txt gelezen van {url}")
        return robots
    except Exception as exc:
        print(f"robots.txt niet leesbaar ({exc}) - ga door zonder")
        return None


def crawl(start, max_pages, delay, out_dir, prefix, obey_robots, timeout, seed_urls=None):
    host = urlparse(start).netloc
    os.makedirs(os.path.join(out_dir, "pages"), exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = UA
    ca = "/root/.ccr/ca-bundle.crt"
    if os.path.exists(ca):
        session.verify = ca

    robots = load_robots(start, session) if obey_robots else None
    follow_links = seed_urls is None
    seeds = [normalise(u) for u in (seed_urls or [start])]
    queue, seen, rows = deque(seeds), set(seeds), []

    while queue and len(rows) < max_pages:
        url = queue.popleft()
        if robots and not robots.can_fetch(UA, url):
            print(f"overgeslagen (robots.txt): {url}")
            continue
        try:
            resp = session.get(url, timeout=timeout, allow_redirects=True)
        except Exception as exc:
            print(f"FOUT {url}: {exc}")
            rows.append({"url": url, "status": "error", "titel": str(exc)[:120],
                         "woorden": 0, "bestand": ""})
            write_index(out_dir, rows)
            time.sleep(delay)
            continue

        if "html" not in resp.headers.get("content-type", ""):
            print(f"overgeslagen (geen html): {url}")
            continue

        page = Page()
        page.feed(resp.text)
        text = page.plain_text()
        base = slug(url, len(rows) + 1)
        with open(os.path.join(out_dir, "pages", base + ".html"), "w", encoding="utf-8") as fh:
            fh.write(resp.text)
        with open(os.path.join(out_dir, "pages", base + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(f"{url}\n{page.title}\n{'-' * 60}\n{text}\n")
        rows.append({"url": url, "status": resp.status_code, "titel": page.title,
                     "woorden": len(text.split()), "bestand": base})
        write_index(out_dir, rows)
        print(f"[{len(rows):>4}/{max_pages}] {resp.status_code} {len(text.split()):>5}w  {url}", flush=True)

        if follow_links:
            for href in page.links:
                nxt = normalise(urljoin(resp.url, href))
                p = urlparse(nxt)
                if p.scheme not in ("http", "https") or p.netloc != host:
                    continue
                if p.path.lower().endswith(SKIP_EXT) or not p.path.startswith(prefix):
                    continue
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        time.sleep(delay)

    write_index(out_dir, rows)
    print(f"\nKlaar: {len(rows)} pagina's opgehaald, {len(queue)} niet bezocht. "
          f"Zie {out_dir}/index.csv")


def main():
    ap = argparse.ArgumentParser(description="Crawl een website binnen één domein.")
    ap.add_argument("url", help="start-URL, bijv. https://www.voorbeeld.nl")
    ap.add_argument("--urls-file", help="bestand met URL's (één per regel); dan wordt niet zelf doorgelinkt")
    ap.add_argument("--max-pages", type=int, default=50, help="maximaal aantal pagina's (standaard 50)")
    ap.add_argument("--delay", type=float, default=1.0, help="wachttijd in seconden tussen verzoeken")
    ap.add_argument("--out", default="./crawl", help="uitvoermap")
    ap.add_argument("--prefix", default="/", help="alleen paden die hiermee beginnen, bijv. /nieuws")
    ap.add_argument("--timeout", type=float, default=20.0, help="time-out per verzoek in seconden")
    ap.add_argument("--ignore-robots", action="store_true", help="robots.txt negeren (alleen met toestemming)")
    args = ap.parse_args()
    if not urlparse(args.url).scheme:
        args.url = "https://" + args.url

    seeds = None
    if args.urls_file:
        with open(args.urls_file, encoding="utf-8") as fh:
            seeds = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
        print(f"{len(seeds)} URL's geladen uit {args.urls_file}")
    crawl(args.url, args.max_pages, args.delay, args.out, args.prefix,
          not args.ignore_robots, args.timeout, seeds)


if __name__ == "__main__":
    sys.exit(main())
