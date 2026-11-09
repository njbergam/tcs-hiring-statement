#!/usr/bin/env python3
"""Rebuild the signatory list in index.html from signatories.csv.

Usage:  python3 update_signatories.py

Reads the Name and University columns (other columns are ignored), drops
duplicate names, sorts by last name, and rewrites everything between the
<!-- signatories:start --> and <!-- signatories:end --> markers in index.html.
"""
import csv
import html
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "signatories.csv"
HTML_PATH = HERE / "index.html"

# Names whose sort key isn't simply the last word.
SORT_AS = {
    "Ronald de Wolf": "Wolf",
    "François Le Gall": "Le Gall",
    "Bhaskar Ray Chaudhury": "Ray Chaudhury",
    "Shayan Oveis Gharan": "Oveis Gharan",
}


def sort_key(name):
    last = SORT_AS.get(name, name.split()[-1])
    plain = unicodedata.normalize("NFKD", f"{last} {name}")
    return "".join(c for c in plain if not unicodedata.combining(c)).casefold()


def main():
    seen, people = set(), []
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("Name") or "").strip()
            if not name or name.casefold() in seen:
                continue
            seen.add(name.casefold())
            people.append((name, (row.get("University") or "").strip()))
    people.sort(key=lambda p: sort_key(p[0]))

    items = "\n".join(
        f'      <li>{html.escape(n)} <span class="inst">{html.escape(u)}</span></li>'
        for n, u in people
    )
    page = HTML_PATH.read_text(encoding="utf-8")
    page, count = re.subn(
        r"(<!-- signatories:start -->).*?(<!-- signatories:end -->)",
        lambda m: m.group(1) + "\n" + items + "\n      " + m.group(2),
        page,
        flags=re.S,
    )
    if count != 1:
        raise SystemExit("Could not find the signatories markers in index.html")
    HTML_PATH.write_text(page, encoding="utf-8")
    print(f"Wrote {len(people)} signatories to {HTML_PATH.name}")


if __name__ == "__main__":
    main()
