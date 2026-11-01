# Ghost Auditor — Product Rules (Steering)

These rules apply to every change in this repo. They exist so the
product stays honest, auditable, and demo-safe.

## Deterministic matching first

- Matching verdicts come from deterministic rules only (exact joins,
  quantity comparison, price comparison, duplicate detection).
- A language model MUST NEVER guess, infer, or invent an amount, a
  quantity, a supplier, or a match verdict.
- If data is ambiguous, record an exception that says so — do not
  silently resolve it.

## Every exception must cite its evidence

- Every exception in the dossier MUST reference its evidence chain:
  the order line, the invoice line (if any), and the portal value (if
  captured).
- An exception without an evidence reference MUST NOT appear in the
  dossier or the exported report.
- The ghost narration MUST only restate dossier facts. It MUST NOT
  invent new amounts, suppliers, or causes.

## Synthetic demo data only

- All demo data in this repo is fictional. Supplier names and numbers
  are invented for demonstration.
- NEVER add real company data, real supplier names, real order numbers,
  or real credentials to this repo.
- The mock portal is a static page in this repo, not a real system.

## Demo honesty

- Stubs MUST be labeled as stubs. Never present a placeholder result
  as a real audit outcome.
- The demo path (sample data + mock portal) MUST run without any
  account, login, or external service.
