"""Discover new Asia-based tech internships from public ATS job boards.

Polls the Greenhouse and Lever boards listed in scripts/sources.json, keeps
postings that are internships **and** tech **and** located in Asia (or remote),
drops anything already in the README, and prints the rest as table rows.

Usage:
  python scripts/discover_listings.py           # report candidates only
  python scripts/discover_listings.py --write   # also insert them into README.md

Nothing is published automatically: the workflow opens a pull request so a
maintainer confirms each listing before it reaches the table.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import requests

# Windows consoles default to cp1252 and would crash on flag emoji.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
SOURCES = Path(__file__).resolve().parent / "sources.json"
TIMEOUT = 25

# "Internship" but not "International" / "Internal" — word boundaries matter.
INTERN_RE = re.compile(r"\b(intern|interns|internship|internships)\b", re.I)

# Broad signals, trusted only in a job title where the wording is deliberate.
TECH_TITLE_RE = re.compile(
    r"\b(software|engineer\w*|developer|programming|data|analytics|backend|"
    r"back[- ]end|frontend|front[- ]end|full[- ]?stack|mobile|android|ios|web|"
    r"machine learning|ml|ai|artificial intelligence|devops|sre|infrastructure|"
    r"platform|cloud|security|cyber\w*|qa|quality assurance|test\w*|database|"
    r"network\w*|blockchain|computer science|it|technology|tech)\b",
    re.I,
)

# Department names are noisier: a logistics firm's "Quality Assurance" team
# inspects parcels, not code. Only unambiguous terms count here.
TECH_DEPT_RE = re.compile(
    r"\b(software|engineer\w*|developer|technology|it|data|infrastructure|"
    r"computer|cyber\w*)\b",
    re.I,
)

REMOTE_RE = re.compile(r"\bremote\b", re.I)

# Country name -> flag. Longest names are matched first so "South Korea" wins
# over a bare "Korea" substring.
COUNTRIES = {
    "singapore": "\U0001f1f8\U0001f1ec",
    "thailand": "\U0001f1f9\U0001f1ed",
    "indonesia": "\U0001f1ee\U0001f1e9",
    "malaysia": "\U0001f1f2\U0001f1fe",
    "philippines": "\U0001f1f5\U0001f1ed",
    "vietnam": "\U0001f1fb\U0001f1f3",
    "viet nam": "\U0001f1fb\U0001f1f3",
    "japan": "\U0001f1ef\U0001f1f5",
    "south korea": "\U0001f1f0\U0001f1f7",
    "korea": "\U0001f1f0\U0001f1f7",
    "china": "\U0001f1e8\U0001f1f3",
    "taiwan": "\U0001f1f9\U0001f1fc",
    "hong kong": "\U0001f1ed\U0001f1f0",
    "india": "\U0001f1ee\U0001f1f3",
    "bangladesh": "\U0001f1e7\U0001f1e9",
    "pakistan": "\U0001f1f5\U0001f1f0",
    "sri lanka": "\U0001f1f1\U0001f1f0",
    "cambodia": "\U0001f1f0\U0001f1ed",
    "myanmar": "\U0001f1f2\U0001f1f2",
    "laos": "\U0001f1f1\U0001f1e6",
    "brunei": "\U0001f1e7\U0001f1f3",
    "nepal": "\U0001f1f3\U0001f1f5",
    "mongolia": "\U0001f1f2\U0001f1f3",
}

# Cities that appear without a country in ATS location fields.
CITIES = {
    "singapore": "singapore",
    "jakarta": "indonesia",
    "bandung": "indonesia",
    "surabaya": "indonesia",
    "bangkok": "thailand",
    "chiang mai": "thailand",
    "tokyo": "japan",
    "osaka": "japan",
    "kyoto": "japan",
    "seoul": "south korea",
    "manila": "philippines",
    "taguig": "philippines",
    "makati": "philippines",
    "cebu": "philippines",
    "kuala lumpur": "malaysia",
    "petaling jaya": "malaysia",
    "subang jaya": "malaysia",
    "shah alam": "malaysia",
    "penang": "malaysia",
    "selangor": "malaysia",
    "cyberjaya": "malaysia",
    "johor": "malaysia",
    "ho chi minh": "vietnam",
    "hanoi": "vietnam",
    "da nang": "vietnam",
    "taipei": "taiwan",
    "hsinchu": "taiwan",
    "beijing": "china",
    "shanghai": "china",
    "shenzhen": "china",
    "guangzhou": "china",
    "hangzhou": "china",
    "bangalore": "india",
    "bengaluru": "india",
    "mumbai": "india",
    "delhi": "india",
    "gurgaon": "india",
    "gurugram": "india",
    "hyderabad": "india",
    "pune": "india",
    "chennai": "india",
    "noida": "india",
    "dhaka": "bangladesh",
    "colombo": "sri lanka",
    "phnom penh": "cambodia",
    "karachi": "pakistan",
    "lahore": "pakistan",
}


@dataclass(frozen=True)
class Listing:
    company: str
    role: str
    location: str
    url: str


def normalize_url(url: str) -> str:
    """Strip query strings, fragments and trailing slashes for comparison."""
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme, parts.netloc.lower(), path, "", "")).lower()


def escape_cell(text: str) -> str:
    """Pipes inside a cell would split the table column."""
    return text.replace("|", "\\|").strip()


def classify_location(raw: str) -> str | None:
    """Return a display location with flag, or None if not Asia/remote."""
    text = raw.lower()
    for name in sorted(COUNTRIES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(name)}\b", text):
            flag = COUNTRIES[name]
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            display = f"{parts[0]}, {parts[-1]}" if len(parts) > 2 else raw.strip()
            if REMOTE_RE.search(text):
                return f"{flag} {display} (remote)"
            return f"{flag} {display}"
    for city in sorted(CITIES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(city)}\b", text):
            country = CITIES[city]
            return f"{COUNTRIES[country]} {raw.strip()}, {country.title()}"
    if REMOTE_RE.search(text):
        return f"\U0001f310 Remote ({raw.strip()})"
    return None


def is_internship(title: str, commitment: str = "") -> bool:
    return bool(INTERN_RE.search(title) or INTERN_RE.search(commitment))


def is_tech(title: str, department: str = "") -> bool:
    return bool(TECH_TITLE_RE.search(title) or TECH_DEPT_RE.search(department))


def fetch_greenhouse(company: str, token: str) -> list[Listing]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    jobs = requests.get(url, timeout=TIMEOUT).json().get("jobs", [])
    out = []
    for j in jobs:
        title = j.get("title", "")
        location = (j.get("location") or {}).get("name", "")
        departments = " ".join(d.get("name", "") for d in j.get("departments", []))
        if not is_internship(title) or not is_tech(title, departments):
            continue
        display = classify_location(location)
        if display:
            out.append(Listing(company, title, display, j.get("absolute_url", "")))
    return out


def fetch_lever(company: str, token: str) -> list[Listing]:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    jobs = requests.get(url, timeout=TIMEOUT).json()
    out = []
    for j in jobs:
        title = j.get("text", "")
        cats = j.get("categories") or {}
        if not is_internship(title, cats.get("commitment", "")):
            continue
        if not is_tech(title, f"{cats.get('department', '')} {cats.get('team', '')}"):
            continue
        display = classify_location(cats.get("location", "") or "")
        if display:
            out.append(Listing(company, title, display, j.get("hostedUrl", "")))
    return out


def existing_keys(readme: str) -> tuple[set[str], set[tuple[str, str]]]:
    """URLs and (company, role) pairs already listed, to avoid duplicates."""
    urls = {normalize_url(u) for u in re.findall(r"\((https?://[^)\s]+)\)", readme)}
    pairs = set()
    for line in readme.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5:
            pairs.add((cells[0].lower(), cells[1].lower()))
    return urls, pairs


def insert_rows(readme: str, rows: list[str]) -> str:
    lines = readme.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if line.startswith("| Company |"):
            # Row after the header is the |---| separator; insert below it.
            lines[i + 2 : i + 2] = [r + "\n" for r in rows]
            return "".join(lines)
    raise SystemExit("could not find the internship table header in README.md")


def main() -> int:
    write = "--write" in sys.argv[1:]
    config = json.loads(SOURCES.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")
    known_urls, known_pairs = existing_keys(readme)

    found: list[Listing] = []
    for src in config["sources"]:
        fetcher = fetch_greenhouse if src["ats"] == "greenhouse" else fetch_lever
        try:
            found.extend(fetcher(src["company"], src["token"]))
        except (requests.RequestException, ValueError) as e:
            # A single unreachable board must not fail the whole sweep.
            print(f"WARN: {src['company']} ({src['ats']}) unavailable: {e}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    rows, seen = [], set()
    for lst in found:
        key = normalize_url(lst.url)
        pair = (lst.company.lower(), lst.role.lower())
        if not lst.url or key in known_urls or key in seen or pair in known_pairs:
            continue
        seen.add(key)
        rows.append(
            f"| {escape_cell(lst.company)} | {escape_cell(lst.role)} "
            f"| {escape_cell(lst.location)} | \U0001f7e2 [Apply]({lst.url}) | {today} |"
        )
        print(f"NEW: {lst.company} — {lst.role} — {lst.location}")

    print(f"scanned {len(config['sources'])} boards, {len(rows)} new listing(s)")
    if rows and write:
        README.write_text(insert_rows(readme, rows), encoding="utf-8", newline="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
