# Ghost Auditor — Requirements (EARS style)

## 1. File upload (CSV / XLSX)

- WHEN the user uploads an orders file, THE SYSTEM SHALL accept CSV and
  XLSX formats and reject other formats with a clear error message.
- WHEN the user uploads an invoices file, THE SYSTEM SHALL accept CSV and
  XLSX formats and reject other formats with a clear error message.
- WHEN either file is missing required columns, THE SYSTEM SHALL report
  exactly which columns are missing instead of failing silently.
- WHERE no files are uploaded, THE SYSTEM SHALL offer the bundled
  synthetic sample data as the demo path.

## 2. Deterministic matching engine

- WHEN matching runs, THE SYSTEM SHALL apply deterministic rules only:
  exact order-id joins, quantity comparison, unit-price comparison, and
  duplicate-payment detection. No amount, quantity, or match verdict SHALL
  be guessed by a language model.
- WHEN an order has no invoice, THE SYSTEM SHALL record a
  `missing_invoice` exception.
- WHEN invoice quantity differs from order quantity, THE SYSTEM SHALL
  record a `quantity_mismatch` exception with both values.
- WHEN invoice unit price differs from order unit price, THE SYSTEM SHALL
  record a `price_difference` exception with both values.
- WHEN two paid invoices reference the same order, THE SYSTEM SHALL record
  a `duplicate_payment` exception.
- WHEN all values agree, THE SYSTEM SHALL mark the order `matched` and
  record no exception.

## 3. Playwright portal capture (built-in mock portal)

- WHEN the user presses "Summon Ghost" with no uploads, THE SYSTEM SHALL
  launch Playwright, load the bundled mock portal page, and capture its
  order/payment rows.
- WHEN portal capture runs, THE SYSTEM SHALL store the captured rows as
  one evidence source, alongside the uploaded files.
- IF the portal page cannot be loaded, THE SYSTEM SHALL report the
  capture failure and continue with file-only matching.

## 4. Evidence-chain dossier

- WHEN the dossier is built, EVERY exception SHALL cite its evidence:
  the order line, the invoice line (if any), and the portal value (if
  captured). An exception without an evidence reference SHALL NOT be
  included in the dossier.
- THE SYSTEM SHALL present the dossier as a list of exceptions, each
  with type, severity, the conflicting values, and its evidence chain.
- THE SYSTEM SHALL store each audit run (inputs, matches, exceptions)
  in sqlite under a run id.

## 5. Report export (Markdown)

- WHEN the user requests an export, THE SYSTEM SHALL generate a Markdown
  report containing the run summary, the exception list with evidence
  chains, and the matched-order count.
- THE SYSTEM SHALL offer the report as a download; it SHALL NOT require
  any account or login for the demo.

## 6. Ghost-persona narration

- WHEN the dossier is ready, THE SYSTEM SHALL narrate the single most
  severe exception in one plain sentence, in the ghost persona.
- THE narration SHALL only restate dossier facts; it SHALL NOT invent
  new amounts, suppliers, or causes.
- Voice/TTS narration is OPTIONAL stretch and SHALL NOT block the core
  flow (upload → match → dossier → export).
