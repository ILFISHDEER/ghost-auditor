# Ghost Auditor — demo video script (under 3 minutes)

Target: one continuous screen recording of the real app working end to end.
No stock footage, no AI-generated app footage — every frame must be the
actual app. Narration in English (judges are international); keep sentences
short and slow.

## Shot list

### Shot 1 — The pain (0:00–0:20)
- Show: the two sample files (orders.csv, invoices.csv) and the mock portal
  page side by side.
- Narration: "Procurement reconciliation is manual drudgery. Orders live in
  one system, invoices in spreadsheets, payment status in a portal. When
  something doesn't match, nobody can say whose number is wrong."

### Shot 2 — Summon (0:20–0:40)
- Show: open the app, upload orders.csv and invoices.csv (or press Summon
  Ghost with no files to use the built-in sample data), click Summon Ghost.
- Narration: "Ghost Auditor takes the files, and a crew of four agents —
  capture, normalize, match, explain — goes to work."

### Shot 3 — The haunting, live (0:40–1:40)
- Show: the crew progress area updating, then the dossier appearing with
  4 exceptions. Linger on each exception type for a few seconds.
- Narration: "Four exceptions. A quantity mismatch. A price difference.
  A missing invoice. And one order paid twice. Every single one carries
  its evidence — the exact order line, the exact invoice line."

### Shot 4 — Evidence + export (1:40–2:30)
- Show: click into the duplicate-payment exception (PO-1004), show the
  evidence chain (order row + both invoices), then click Export and show
  the Markdown report downloading.
- Narration: "Here is the duplicate payment: one order, two paid invoices,
  2,400 dollars paid more than once. And the receipts are in the dossier.
  One click exports the whole audit as a report."

### Shot 5 — Close (2:30–3:00)
- Show: the app's front page with the ghost persona line, then the GitHub
  repo page (ILFISHDEER/ghost-auditor) for one second.
- Narration: "Ghost Auditor. A ghost that possesses your browser,
  cross-checks your numbers, and proves every claim. Built with Kiro."

## Recording checklist (for whoever records)

- Use the hosted demo URL (or localhost if recording before deploy).
- Use the built-in sample data — it guarantees all 4 exception types.
- Record at 1080p, no background music, no third-party logos on screen.
- Do one full rehearsal before recording; the whole flow takes ~2 minutes
  when it works.
- Upload to YouTube as public or unlisted, no password. Only the first
  3 minutes are reviewed, so keep it under 3:00.

## What is NOT in the video (deliberately)

- Voice narration by the ghost (stretch feature, not built).
- Live portal capture (needs a machine with a Chromium browser; the app
  falls back to file data and marks portal evidence as not captured).
