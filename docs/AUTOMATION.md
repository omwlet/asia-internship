# Automation Plan: Broken Link Checker

**Goal:** catch dead application links automatically instead of waiting for user reports.

## Approach (simplest → most robust)

### Phase 1 — Off-the-shelf link checker (current)

Use [`lycheeverse/lychee-action`](https://github.com/lycheeverse/lychee-action) on a weekly cron
(see [`.github/workflows/link-checker.yml`](../.github/workflows/link-checker.yml)).
It scans the README, follows redirects, and auto-opens a GitHub Issue listing failures.
Zero custom code to maintain.

### Phase 2 — Custom Python script (when Phase 1 isn't enough)

ATS pages often return HTTP 200 even when a job is closed (soft-404s). The script in
[`scripts/check_links.py`](../scripts/check_links.py) parses the README table, requests each link,
and additionally scans the response body for phrases like *"no longer accepting applications"*
or *"job not found"*. Run it from the same weekly workflow and pipe its output into the
auto-created issue.

## Key operational choices

- **Weekly, not on every PR** — hammering ATS domains on each push risks rate-limiting / IP blocks.
- **Retry with backoff and a browser-like User-Agent** — many career sites block default bot
  agents, causing false positives.
- **Report via Issues, never auto-delete rows** — a human confirms before a listing is removed.
