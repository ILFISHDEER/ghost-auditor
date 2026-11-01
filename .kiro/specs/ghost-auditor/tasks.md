# Ghost Auditor — Implementation Tasks

Solo builder, ~4 weeks. Demo-critical path first: upload → match →
dossier → export. Everything else is polish or stretch.

## Week 1 — Skeleton (demo path must exist end-to-end, even stubbed)

- [ ] Create public repo, add MIT LICENSE, verify `.kiro/` is not ignored
- [ ] FastAPI skeleton: `GET /health` working; other endpoints stubbed
- [ ] Static frontend shell served by FastAPI: upload area, Summon Ghost
      button, progress area, dossier area
- [ ] Bundled synthetic sample data (orders + invoices with 4 built-in
      exceptions) and mock portal page
- [ ] Claim the 4,000 free Kiro credits (before Dec 1, 12:00 PM PT)

## Week 2 — Matching engine (the core)

- [ ] `ingest.py`: CSV/XLSX parsing + required-column validation
- [ ] `normalize.py`: canonical schema + money-to-cents coercion
- [ ] `match.py`: order-id join, quantity check, price check,
      duplicate-payment check, missing-invoice check
- [ ] Unit checks for the matching rules (run on every backend save)
- [ ] Wire `POST /upload` → `POST /audit` → dossier JSON

## Week 3 — Portal capture + dossier + export

- [ ] `portal.py`: Playwright capture of the mock portal rows
- [ ] `evidence.py`: evidence-chain attachment for every exception
- [ ] Dossier view in the frontend (exceptions with evidence chains)
- [ ] `GET /report/{run_id}`: Markdown export download
- [ ] Ghost narration: one sentence for the worst exception
- [ ] sqlite run storage

## Week 4 — Polish, video, submission

- [ ] Haunted UI polish (dark theme, ghost persona copy, progress states)
- [ ] README: architecture, quickstart, judge run instructions
- [ ] Demo video (under 3 minutes, YouTube public): pain → upload →
      possession → dossier → export
- [ ] Submission write-up: Inspiration / What it does / How we built it /
      How we used Kiro / Challenges / What we learned / What's next
- [ ] Submit at least 2 days before the Dec 4, 2:00 PM PT deadline

## Stretch (only if the core is done)

- [ ] Voice/TTS ghost narration (OPTIONAL — must not block the core flow)
- [ ] "Try it out" links and image gallery on the submission
- [ ] Property-based tests for matching invariants (amount conservation,
      no double counting)
