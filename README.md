# Ghost Auditor

> A ghost that possesses your browser, cross-checks your orders, invoices, and payments, and hands you an auditable exception dossier — with evidence for every claim.

**Category:** Frankenstein, Kiroween 2026 (Devpost).

## The problem

Procurement reconciliation is manual drudgery: orders live in one system, invoices in spreadsheets, payment status in a supplier portal. People tab back and forth, exceptions surface late, and when something is wrong nobody can say exactly why. Ghost Auditor stitches together four technologies that don't usually live in one product — browser automation (Playwright), spreadsheet data pipelines (pandas), a multi-agent crew, and a ghost persona UI — into one audit desk.

## Core demo flow

1. Upload two files (purchase orders CSV + invoices XLSX), or press **Summon Ghost** to possess the built-in mock supplier portal.
2. Four agents work in sequence, visible live: **Capture** (portal data), **Normalize** (canonical schema), **Match** (deterministic rules), **Explain** (exception narration).
3. An exception dossier appears: quantity mismatches, price differences, missing invoices, duplicate payments — every exception cites its evidence chain (order line ↔ invoice line ↔ portal value).
4. Export the dossier as Markdown. The ghost narrates the worst exception in one sentence.

## Architecture (text diagram)

```
  Upload CSV/XLSX ─┐
                   ▼
  Mock portal ──► [Capture: Playwright] ──► [Normalize: canonical schema]
  (mock_portal/)        (backend/portal.py)        (backend/normalize.py)
                                                        │
                                              [Match: deterministic rules]
                                                  (backend/match.py)
                                                        │
                                              [Evidence: evidence chains]
                                                  (backend/evidence.py)
                                                        │
  Frontend (single page) ◄── FastAPI ──► Dossier + Markdown export
  (frontend/)              (backend/main.py, sqlite run storage)
```

The four-agent crew maps to code modules, not to separate services:
Capture → `portal.py`, Normalize → `normalize.py`, Match → `match.py`,
Explain → `evidence.py` + the ghost narration in the frontend.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn backend.main:app --reload
```

Then open http://127.0.0.1:8000/ — the API serves the frontend page.
Check the API is alive: `curl http://127.0.0.1:8000/health`.

## How judges can run the demo (synthetic data only)

1. Start the server as above.
2. On the page, press **Summon Ghost** without uploading anything: the app
   loads the bundled sample data (`backend/sample_data/orders.csv`,
   `backend/sample_data/invoices.csv`) and captures the mock portal
   (`mock_portal/index.html`).
3. The dossier shows four intentional exceptions: a quantity mismatch, a
   price difference, a missing invoice, and a duplicate payment.
4. Press **Export Markdown** to download the dossier.

No login is required for the demo. If a deployed demo ever needs
credentials, they are provided in the Devpost submission form's
judges-only field, never in this repo.

## Demo data notice

**All demo data in this repository is synthetic and fictional.**
Supplier names (Acme Widgets Co, Globex Supplies, Initech Parts, Umbrella
Components, Hooli Hardware, Stark Devices) are invented, and every number
is made up for demonstration. No real company data is included anywhere.

## Status

Scaffold state (see `backend/main.py`): the `/health` endpoint works.
`/upload`, `/audit`, and `/report/{run_id}` are clearly-marked stubs —
they return a `status: "stub"` response and do not pretend to produce
real audit results. Implementation order lives in
`.kiro/specs/ghost-auditor/tasks.md`.
