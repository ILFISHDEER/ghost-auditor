# Ghost Auditor — Repo Layout (Steering)

```
ghost-auditor/
├── README.md                  # pitch, architecture, quickstart, judge run guide
├── LICENSE                    # MIT
├── requirements.txt           # FastAPI, uvicorn, pandas, openpyxl, playwright
├── .gitignore                 # Python ignores; MUST NOT ignore .kiro/
├── .kiro/
│   ├── specs/ghost-auditor/   # requirements.md, design.md, tasks.md
│   ├── steering/              # product.md, tech.md, structure.md
│   └── hooks/hooks.json       # automation descriptions
├── backend/
│   ├── main.py                # FastAPI app + endpoints
│   ├── ingest.py              # CSV/XLSX parsing + validation
│   ├── normalize.py           # canonical schema + type coercion
│   ├── match.py               # deterministic matching rules
│   ├── evidence.py            # evidence chains + dossier + narration
│   ├── portal.py              # Playwright capture of the mock portal
│   └── sample_data/           # synthetic orders.csv, invoices.csv
├── mock_portal/
│   └── index.html             # static mock supplier portal page
└── frontend/
    ├── index.html             # single dark haunted page
    ├── style.css
    └── app.js                 # API calls, progress, dossier rendering
```

## Module responsibilities

- `main.py`: HTTP only. Parses requests, calls the pipeline modules,
  returns JSON. No matching logic here.
- `ingest.py`: file parsing and validation only. Returns dataframes
  or a precise column error.
- `normalize.py`: maps every source onto the canonical schema and
  coerces types (money → integer cents). No verdicts here.
- `match.py`: deterministic rules only. Returns matched orders and
  typed exceptions. No LLM calls, no guessing.
- `evidence.py`: attaches evidence chains, builds the dossier, and
  renders the one-sentence ghost narration from dossier facts.
- `portal.py`: Playwright only. Loads the mock portal, scrapes rows,
  returns them in canonical shape. Never touches real portals.
- `frontend/`: presentation only. No matching logic in JavaScript.

## Kiro directory rule

The `.kiro/` directory and everything under it MUST remain visible in
the repo. Never add `.kiro` or any `.kiro/**` path to `.gitignore`.
