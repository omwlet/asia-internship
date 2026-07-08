"""Scan the README internship table for dead or soft-closed application links.

Usage:
  python scripts/check_links.py          # report suspicious listings only
  python scripts/check_links.py --fix    # also mark them CLOSED in README.md

Prints one line per dead listing; exits 0 regardless (the GitHub Actions
workflow consumes the output and opens a pull request for a human to review).
Bot-blocked responses (401/403/407/429/503) are treated as inconclusive and
never marked, since many career sites block automated requests.
"""

import re
import sys

import requests

CLOSED_PHRASES = [
    "no longer accepting",
    "position has been filled",
    "job not found",
    "posting has closed",
    "this job is no longer available",
    "vacancy has expired",
]

INCONCLUSIVE_STATUSES = {401, 403, 407, 429, 503}

OPEN_EMOJI = ("\U0001f7e2", "\U0001f7e1")  # green, yellow
CLOSED_EMOJI = "\U0001f534"  # red

TABLE_ROW = re.compile(
    r"^\|\s*(?P<company>[^|]+)\|[^|]+\|[^|]+\|(?P<status>[^|]*\((?P<url>https?://[^)]+)\)[^|]*)\|"
)


def dead_reason(url: str) -> str | None:
    """Return why the listing looks dead, or None if it seems alive."""
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as e:
        return f"unreachable ({e.__class__.__name__})"
    if r.status_code in INCONCLUSIVE_STATUSES:
        return None
    if r.status_code >= 400:
        return f"HTTP {r.status_code}"
    body = r.text.lower()
    for phrase in CLOSED_PHRASES:
        if phrase in body:
            return f'page says "{phrase}"'
    return None


def close_row(status: str) -> str:
    """Rewrite a status cell as closed, keeping the link for reference."""
    for emoji in OPEN_EMOJI:
        status = status.replace(emoji, CLOSED_EMOJI)
    return re.sub(r"\[[^\]]*\]", "[Closed]", status, count=1)


def main() -> None:
    fix = "--fix" in sys.argv[1:]
    with open("README.md", encoding="utf-8") as fh:
        lines = fh.readlines()

    changed = False
    for i, line in enumerate(lines):
        m = TABLE_ROW.match(line)
        if not m or CLOSED_EMOJI in m["status"]:
            continue
        reason = dead_reason(m["url"])
        if reason is None:
            continue
        print(f"{m['company'].strip()} — {m['url']} — {reason}")
        if fix:
            lines[i] = line.replace(m["status"], close_row(m["status"]))
            changed = True

    if fix and changed:
        with open("README.md", "w", encoding="utf-8", newline="") as fh:
            fh.writelines(lines)


if __name__ == "__main__":
    main()
