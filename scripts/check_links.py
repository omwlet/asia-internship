"""Scan the README internship table for dead or soft-closed application links.

Usage: python scripts/check_links.py
Prints one line per suspicious listing; exits 0 regardless (reporting is
handled by the GitHub Actions workflow that consumes the output).
"""

import re

import requests

CLOSED_PHRASES = [
    "no longer accepting",
    "position has been filled",
    "job not found",
    "posting has closed",
]

TABLE_ROW = re.compile(
    r"^\|\s*(?P<company>[^|]+)\|[^|]+\|[^|]+\|.*?\((?P<url>https?://[^)]+)\)"
)


def main() -> None:
    with open("README.md", encoding="utf-8") as fh:
        for line in fh:
            m = TABLE_ROW.match(line)
            if not m:
                continue
            company, url = m["company"].strip(), m["url"]
            try:
                r = requests.get(
                    url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}
                )
                body = r.text.lower()
                if r.status_code >= 400 or any(p in body for p in CLOSED_PHRASES):
                    print(f"POSSIBLY CLOSED: {company} — {url} ({r.status_code})")
            except requests.RequestException as e:
                print(f"UNREACHABLE: {company} — {url} ({e})")


if __name__ == "__main__":
    main()
