# Automation: How This Repo Maintains Itself

**Goal:** keep the list accurate with minimal manual work, while a human always
approves changes before they land.

## What runs today

### PR format validation — on every pull request

[`validate-pr.yml`](../.github/workflows/validate-pr.yml) runs
[`scripts/validate_table.py`](../scripts/validate_table.py) whenever a PR touches
the README. It rejects rows with the wrong column count, bad dates, missing
status emoji, missing application links, or link shorteners — so maintainers
only review substance, not formatting.

### Weekly link check — every Monday

[`link-checker.yml`](../.github/workflows/link-checker.yml) runs two jobs:

1. **lychee** scans every link in the README and opens an issue listing any
   that fail outright (404s, DNS errors).
2. **autoClose** runs [`scripts/check_links.py`](../scripts/check_links.py) `--fix`,
   which also catches **soft-404s** — ATS pages that return HTTP 200 but say
   *"no longer accepting applications"*. Dead rows are rewritten to 🔴 Closed
   and submitted as a **pull request** for a maintainer to review and merge.

> ⚙️ One-time setup: the autoClose job needs
> **Settings → Actions → General → Workflow permissions →
> ✅ "Allow GitHub Actions to create and approve pull requests"**.

## Possible next phase — auto-discovering new listings

Companies on Greenhouse or Lever expose public JSON APIs
(e.g. `https://boards-api.greenhouse.io/v1/boards/agoda/jobs`,
`https://api.lever.co/v0/postings/GoToGroup`). A weekly script could filter
those for "intern" roles not yet in the table and open a PR proposing them.
API-based, so no scraping or bot-blocking issues — but only covers companies
on those ATS platforms.

## Key operational choices

- **Weekly, not on every PR** — hammering ATS domains on each push risks rate-limiting / IP blocks.
- **Retry with backoff and a browser-like User-Agent** — many career sites block default bot
  agents, causing false positives.
- **Report via Issues, never auto-delete rows** — a human confirms before a listing is removed.
