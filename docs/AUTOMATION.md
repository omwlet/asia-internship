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

### Listing discovery — every Thursday

[`discover-listings.yml`](../.github/workflows/discover-listings.yml) runs
[`scripts/discover_listings.py`](../scripts/discover_listings.py), which polls the
public Greenhouse and Lever APIs for every board in
[`scripts/sources.json`](../scripts/sources.json) and opens a PR proposing rows
that pass all three filters:

| Filter | How it works |
|---|---|
| **Is an internship** | Word-boundary match, so *International* and *Internal Audit* are not mistaken for *Intern*. Lever's `commitment: Internship` field is used when present. |
| **Is tech** | Broad keywords in the job title; only unambiguous ones in the department, because a logistics firm's "Quality Assurance" team inspects parcels, not code. |
| **Is Asia or remote** | Country and city lookup that turns `Subang Jaya, Selangor, Malaysia` into `🇲🇾 Subang Jaya, Malaysia`. |

Rows already present (matched by normalized URL, or by company + role) are
skipped, so re-runs propose nothing new. The proposed table is passed through
`validate_table.py` before the PR opens, so a regex or API change can never
produce a malformed table.

**Adding a company:** find its public board token — Greenhouse boards answer at
`boards-api.greenhouse.io/v1/boards/<token>/jobs`, Lever at
`api.lever.co/v0/postings/<token>` — and append an entry to `sources.json`.
No code changes needed.

## Design rule

Every automation here **proposes; a human disposes.** Bots open issues and pull
requests, never commit to `main`. Discovered listings are unverified until a
maintainer reviews them, which is why they arrive as a PR rather than a commit.

## Key operational choices

- **Weekly, not on every PR** — hammering ATS domains on each push risks rate-limiting / IP blocks.
- **Retry with backoff and a browser-like User-Agent** — many career sites block default bot
  agents, causing false positives.
- **Report via Issues, never auto-delete rows** — a human confirms before a listing is removed.
