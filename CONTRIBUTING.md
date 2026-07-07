# Contributing Guide

Thank you for helping keep this list useful for students across Asia! 🎉
Please read these rules before opening a Pull Request.

---

## ✅ Listing Rules

1. **No duplicates.** Search the README (Ctrl+F the company name) before adding. If the same company has *multiple distinct roles*, separate rows are fine.
2. **Official links only.** The application link must point to the company's careers page or official ATS posting (Greenhouse, Lever, Workday, etc.). ❌ No referral links, ❌ no link shorteners (bit.ly etc.), ❌ no third-party aggregators (LinkedIn/Indeed links only if the company has no direct posting).
3. **Verify the link works** and the role is still accepting applications *at the time of your PR*.
4. **Scope:** the role must be a **tech internship for 2026** and either:
   - physically located in an **Asian country**, or
   - **fully remote** and open to applicants based in Asia (state time-zone restrictions in the Location column, e.g., `🌐 Remote (UTC+7 ±3h)`).
5. **Proper markdown links:** `[Apply](https://example.com/job/123)` — never paste a bare URL into the table.
6. **Formatting:**
   - One row per role, added at the **top** of the table.
   - Date format: `YYYY-MM-DD`.
   - Status emoji: 🟢 Open / 🟡 Closing soon / 🔴 Closed.
   - Keep the table's column count intact — 5 pipe-delimited columns, no more, no less.
7. **No spam or self-promotion.** Recruiters may list genuine roles at their own company but must disclose their affiliation in the PR description.

---

## 🔀 Step-by-Step: Fork → Branch → Commit → PR

### 1. Fork the repository
Click **Fork** (top-right of this repo) to create your own copy.

### 2. Clone your fork locally
```bash
git clone https://github.com/<your-username>/asia-internship.git
cd asia-internship
```

### 3. Create a branch
Use a descriptive branch name:
```bash
git checkout -b add-grab-backend-intern
```

### 4. Make your edit
Open `README.md`, add your row to the **top** of the table following the format in the Listing Rules above.

### 5. Commit your change
Write a clear commit message:
```bash
git add README.md
git commit -m "Add: Grab — Software Engineering Intern (Backend), Singapore"
```

### 6. Push and open a Pull Request
```bash
git push origin add-grab-backend-intern
```
Then go to your fork on GitHub and click **"Compare & pull request"**.

**PR title format:** `Add: <Company> — <Role>`
**PR description should include:**
- [ ] I searched the list and this role is not a duplicate
- [ ] The application link works and points to the official posting
- [ ] The row follows the required table format

> 💡 **Small edit? Skip the clone.** For a single-row addition you can edit `README.md` directly in the GitHub web UI (pencil icon) — GitHub will fork and create the PR for you automatically.

---

## 🧹 Marking roles as closed

If you notice a role is no longer accepting applications:
- Change its status emoji to 🔴 and replace the link text with `Closed`, **or**
- Open a "Broken / Expired Link" issue if you can't submit a PR.

Closed roles are pruned by maintainers monthly.

---

## 🚦 Review process

- A maintainer will review your PR, usually within a few days.
- The automated **link checker** (GitHub Actions) must pass — if it flags your link, double-check the URL.
- PRs that don't follow the table format will be asked to revise before merging.

Thanks for contributing! 🙌
