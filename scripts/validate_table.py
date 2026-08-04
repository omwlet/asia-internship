"""Validate the internship table in README.md (runs as a PR status check).

Usage: python scripts/validate_table.py
Prints one line per problem and exits 1 if any row breaks the format
rules described in CONTRIBUTING.md; exits 0 when the table is clean.
"""

import re
import sys

# Windows consoles default to cp1252 and would crash on the status emoji.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINK = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
STATUS_EMOJI = ("\U0001f7e2", "\U0001f7e1", "\U0001f534")  # green, yellow, red
CLOSED = "\U0001f534"
BANNED_HOSTS = ("bit.ly", "tinyurl.com", "goo.gl", "t.co/", "cutt.ly", "rb.gy")
HEADER = "| Company |"


def validate_row(lineno: int, row: str, errors: list[str]) -> None:
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    if len(cells) != 5:
        errors.append(f"line {lineno}: expected 5 columns, found {len(cells)}")
        return
    company, role, location, status, date = cells
    for name, value in (("Company", company), ("Role", role), ("Location", location)):
        if not value:
            errors.append(f"line {lineno}: {name} column must not be empty")
    if not any(e in status for e in STATUS_EMOJI):
        errors.append(f"line {lineno}: status cell needs one of \U0001f7e2 \U0001f7e1 \U0001f534")
    link = LINK.search(status)
    if link:
        url = link.group(1)
        if any(host in url for host in BANNED_HOSTS):
            errors.append(f"line {lineno}: link shorteners are not allowed ({url})")
    elif CLOSED not in status:
        # Open listings must link to the application page; closed rows may drop it.
        errors.append(f"line {lineno}: status cell needs a markdown link like [Apply](https://...)")
    if not DATE.match(date):
        errors.append(f"line {lineno}: Date Posted must be YYYY-MM-DD, got '{date}'")


def main() -> int:
    errors: list[str] = []
    rows = 0
    in_table = False
    with open("README.md", encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if line.startswith(HEADER):
                in_table = True
                continue
            if in_table and not line.startswith("|"):
                in_table = False
                continue
            if not in_table or set(line) <= set("|-: "):
                continue  # outside the table, or the |---| separator row
            rows += 1
            validate_row(lineno, line, errors)

    if not rows:
        errors.append("no internship table found in README.md")
    for e in errors:
        print(f"::error file=README.md::{e}")
    print(f"checked {rows} listing rows, {len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
