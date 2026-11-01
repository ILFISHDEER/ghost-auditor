# Ghost Auditor — Tech Rules (Steering)

## Stack

- Language: Python 3.11+.
- Backend: FastAPI + uvicorn.
- Data: pandas (+ openpyxl for XLSX), sqlite for run storage.
- Browser automation: Playwright (Chromium) against the bundled mock
  portal only.
- Frontend: one static page (HTML + CSS + vanilla JS). No heavy
  frameworks, no build step, no npm dependencies.

## Rules

- Keep the frontend a single static page served by FastAPI. Do not
  introduce React, Next.js, or any frontend build tooling.
- Keep money as integer cents internally. Never compare float money
  values for equality.
- Keep modules small and single-purpose: ingest, normalize, match,
  evidence, portal — one job each (see `structure.md`).
- No external APIs in the core flow. The demo MUST work fully offline
  except for the initial `pip install` / `playwright install`.
- No secrets or credentials in code, data, or docs. Test credentials,
  if ever needed for judges, go in the Devpost submission form's
  judges-only field, never in the repo.
- Dependencies stay minimal: only what is listed in
  `requirements.txt`.
