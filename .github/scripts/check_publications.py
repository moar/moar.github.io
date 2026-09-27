#!/usr/bin/env python3
"""
Monthly publications watcher.

Fetches the Mondragon research-portal profile page, parses the publication list,
and compares it against a stored snapshot of document IDs. For any new
publication it appends a *draft* BibTeX entry (enriched with the DOI from the
document's detail page) to the bibliography and records the new ID in the
snapshot.

Stdlib only (urllib + re) so the GitHub Action needs no pip install.

Exit code 0 always; whether a PR is opened is decided by the workflow based on
`git diff` (and on the value printed to $GITHUB_OUTPUT as new_count=N).
"""

from __future__ import annotations

import html as _html
import json
import os
import re
import sys
import time
import urllib.request

# --- Configuration ----------------------------------------------------------

PROFILE_ID = "738265"
BASE = "https://research.mondragon.edu"
PROFILE_URL = f"{BASE}/investigadores/{PROFILE_ID}/publicaciones"
DOC_URL = BASE + "/documentos/{id}"

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
SNAPSHOT_PATH = os.path.join(HERE, "..", "publications_snapshot.json")
BIB_PATH = os.path.join(REPO, "_bibliography", "papers.bib")

UA = "Mozilla/5.0 (compatible; moar-publications-watcher/1.0; +https://moar.github.io)"


# --- HTTP -------------------------------------------------------------------

def fetch(url: str, retries: int = 3) -> str:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001 - network best-effort
            last = e
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last}")


# --- Parsing ----------------------------------------------------------------

# Each publication is: <li class="investigador-docs__item c-doc"> ... </li>
# containing <a href="/documentos/{id}">, <span class="c-doc__titulo">TITLE</span>
# and <p class="c-doc__localizacion">VENUE</p>. Year groups are <h3>YYYY</h3>.

ITEM_RE = re.compile(r'<li class="investigador-docs__item c-doc">(.*?)</li>', re.S)
ID_RE = re.compile(r'/documentos/([0-9a-f]{12,})')
TITLE_RE = re.compile(r'class="c-doc__titulo"[^>]*>(.*?)</span>', re.S)
VENUE_RE = re.compile(r'class="c-doc__localizacion"[^>]*>(.*?)</p>', re.S)
YEAR_H3_RE = re.compile(r'<h3[^>]*>\s*(20\d\d)\s*</h3>')


def _clean(fragment: str) -> str:
    text = re.sub(r"<[^>]+>", " ", fragment)
    text = _html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def parse_publications(page: str) -> list[dict]:
    """Return list of {id, title, venue, year} in page order (newest first)."""
    pubs: list[dict] = []
    # Build a year lookup by tracking the last <h3>YEAR</h3> seen before each item.
    # Walk the document, remembering the current year as we encounter items.
    current_year = ""
    pos = 0
    for token in re.finditer(r'(<h3[^>]*>\s*20\d\d\s*</h3>)|(<li class="investigador-docs__item c-doc">.*?</li>)', page, re.S):
        chunk = token.group(0)
        ym = YEAR_H3_RE.search(chunk)
        if ym:
            current_year = ym.group(1)
            continue
        doc_id = (ID_RE.search(chunk) or [None, None])[1] if ID_RE.search(chunk) else None
        title_m = TITLE_RE.search(chunk)
        venue_m = VENUE_RE.search(chunk)
        if not doc_id or not title_m:
            continue
        pubs.append({
            "id": doc_id,
            "title": _clean(title_m.group(1)),
            "venue": _clean(venue_m.group(1)) if venue_m else "",
            "year": current_year,
        })
    return pubs


DOI_RE = re.compile(r'10\.\d{4,9}/[^\s"<>]+')


def fetch_doi(doc_id: str) -> str:
    try:
        page = fetch(DOC_URL.format(id=doc_id))
    except Exception:  # noqa: BLE001
        return ""
    m = DOI_RE.search(page)
    if not m:
        return ""
    return m.group(0).rstrip(".").lower()


# --- BibTeX generation ------------------------------------------------------

def make_key(pub: dict) -> str:
    year = pub.get("year") or "xxxx"
    title_words = re.findall(r"[A-Za-z]+", pub["title"].lower())
    slug = next((w for w in title_words if len(w) > 3), "paper")
    return f"aguirre{year}{slug}"


def make_bibtex(pub: dict, doi: str, key: str) -> str:
    title = pub["title"]
    venue = pub["venue"]
    lines = [
        f"@article{{{key},",
        "  bibtex_show={true},",
        "  % AUTO-GENERATED DRAFT from research.mondragon.edu - review authors, type (@article/@inproceedings/@inbook), and fields before merging.",
        f"  title={{{title}}},",
        "  author={Aguirre-Ortuzar, A. and others},",
        f"  journal={{{venue}}},",
    ]
    if pub.get("year"):
        lines.append(f"  year={{{pub['year']}}},")
    if doi:
        lines.append(f"  doi={{{doi}}},")
        lines.append(f"  html={{https://doi.org/{doi}}},")
    lines.append("}")
    return "\n".join(lines)


# --- Snapshot ---------------------------------------------------------------

def load_snapshot() -> dict:
    if os.path.exists(SNAPSHOT_PATH):
        with open(SNAPSHOT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"seen_ids": [], "publications": []}


def save_snapshot(snapshot: dict) -> None:
    os.makedirs(os.path.dirname(SNAPSHOT_PATH), exist_ok=True)
    with open(SNAPSHOT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
        f.write("\n")


def append_to_bib(entries: list[str]) -> None:
    block = "\n\n" + "\n\n".join(entries) + "\n"
    with open(BIB_PATH, "a", encoding="utf-8") as f:
        f.write(block)


# --- Main -------------------------------------------------------------------

def set_output(name: str, value: str) -> None:
    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        return
    with open(out, "a", encoding="utf-8") as f:
        if "\n" in value:
            delim = f"EOF_{time.time_ns()}"
            f.write(f"{name}<<{delim}\n{value}\n{delim}\n")
        else:
            f.write(f"{name}={value}\n")


def main() -> int:
    seed_only = "--seed" in sys.argv

    page = fetch(PROFILE_URL)
    pubs = parse_publications(page)
    if not pubs:
        print("ERROR: parsed 0 publications — page structure may have changed.", file=sys.stderr)
        return 0  # don't fail the workflow; nothing to PR
    print(f"Parsed {len(pubs)} publications from the portal.")

    snapshot = load_snapshot()
    seen = set(snapshot.get("seen_ids", []))

    if seed_only or not seen:
        # Seed mode (or first-ever run): record current state WITHOUT touching the
        # bibliography, so the existing papers.bib entries are not duplicated.
        snapshot["seen_ids"] = [p["id"] for p in pubs]
        snapshot["publications"] = pubs
        save_snapshot(snapshot)
        print(f"Seeded snapshot with {len(pubs)} publications (no bib changes).")
        set_output("new_count", "0")
        return 0

    new = [p for p in pubs if p["id"] not in seen]
    if not new:
        print("No new publications.")
        set_output("new_count", "0")
        return 0

    print(f"Found {len(new)} new publication(s):")
    entries = []
    for pub in new:
        doi = fetch_doi(pub["id"])
        key = make_key(pub)
        entries.append(make_bibtex(pub, doi, key))
        print(f"  + [{pub.get('year','????')}] {pub['title'][:80]} (doi={doi or 'n/a'})")

    append_to_bib(entries)
    snapshot["seen_ids"] = sorted(seen.union(p["id"] for p in pubs))
    snapshot["publications"] = pubs
    save_snapshot(snapshot)

    set_output("new_count", str(len(new)))
    titles = "\n".join(f"- {p['title']} ({p.get('year','')})" for p in new)
    set_output("new_titles", titles)
    return 0


if __name__ == "__main__":
    sys.exit(main())
