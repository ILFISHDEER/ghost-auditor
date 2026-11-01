# Ghost Auditor — Design

## Architecture

Single FastAPI backend, sqlite run storage, a pandas matching pipeline,
a Playwright capture module, and one static frontend page. No heavy
frameworks, no separate services, no external APIs in the core flow.

```
  Upload CSV/XLSX ─┐
                   ▼
  Mock portal ──► portal.py (Playwright capture) ──► normalize.py
  (mock_portal/)                                     (canonical schema)
                                                            │
                                                  match.py (deterministic
                                                  rules, pandas)
                                                            │
                                                  evidence.py (evidence
                                                  chains + dossier)
                                                            │
  frontend/index.html ◄── main.py (FastAPI) ──► sqlite (runs)
```

## Data flow

1. **Ingest** (`ingest.py`): parse CSV/XLSX uploads into dataframes;
   validate required columns; fall back to bundled sample data when the
   user chooses the demo path.
2. **Capture** (`portal.py`): Playwright loads `mock_portal/index.html`
   and scrapes its order/payment rows into the same shape as an
   evidence source. Capture failure degrades to file-only matching.
3. **Normalize** (`normalize.py`): map every source (orders, invoices,
   portal rows) onto one canonical schema:
   `order_id, supplier, item, qty, unit_price, total, status, source`.
   Types are coerced (quantities to int, money to cents-int) so
   comparisons are exact, never float-fuzzy.
4. **Match** (`match.py`): deterministic rules over the canonical
   tables, in order: exact order-id join → quantity check → unit-price
   check → duplicate-paid-invoice check → missing-invoice check.
   Output: matched orders + typed exceptions. No LLM involvement in
   any verdict.
5. **Evidence** (`evidence.py`): attach to each exception its evidence
   chain (order line, invoice line, portal row) and render the dossier
   plus the one-sentence ghost narration of the worst exception.
6. **Storage**: each run (inputs summary, matches, exceptions, dossier)
   is stored in sqlite under a run id; `GET /report/{run_id}` returns
   the Markdown report.

## Four-agent crew concept (maps to modules, not services)

| Crew role   | Code module      | Responsibility                              |
| ----------- | ---------------- | ------------------------------------------- |
| Capture     | `portal.py`      | Possess the portal, scrape order/payment rows |
| Normalize   | `normalize.py`   | Canonical schema, type coercion             |
| Match       | `match.py`       | Deterministic matching rules                |
| Explain     | `evidence.py`    | Evidence chains, dossier, ghost narration   |

The "crew" is a narrative and code-organization device: four focused
modules with clear inputs and outputs. In a future step each could be
driven by a Kiro custom agent, but the matching verdicts stay
deterministic regardless.

## Frontend

One static page (`frontend/`): dark haunted theme, file-upload area,
"Summon Ghost" button, live run-progress area, dossier view, Markdown
export button. It calls the backend API; it contains no matching logic
of its own.

## Non-goals

- No real supplier portals, no real company data, no user accounts.
- No LLM-generated amounts or verdicts. Voice/TTS is stretch only.
