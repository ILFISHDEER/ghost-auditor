"""File ingestion for Ghost Auditor.

TODO (Week 2): parse uploaded orders/invoices files into pandas
DataFrames and validate required columns.

Responsibilities:
- Accept CSV and XLSX uploads; reject other formats with a clear error.
- Required orders columns: order_id, supplier, item, qty, unit_price,
  total, order_date.
- Required invoices columns: invoice_id, order_id, supplier, item, qty,
  unit_price, total, invoice_date, payment_status.
- On missing columns, report exactly which columns are missing.
- Provide a loader for the bundled synthetic sample data
  (backend/sample_data/) used by the no-upload demo path.

This module is a skeleton: functions below are placeholders and raise
NotImplementedError until implemented. Nothing here produces audit
results yet.
"""

import pandas as pd


def load_orders(path: str) -> pd.DataFrame:
    """TODO: load an orders CSV/XLSX file into a DataFrame."""
    raise NotImplementedError("ingest.load_orders is not implemented yet")


def load_invoices(path: str) -> pd.DataFrame:
    """TODO: load an invoices CSV/XLSX file into a DataFrame."""
    raise NotImplementedError("ingest.load_invoices is not implemented yet")


def load_sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """TODO: load the bundled synthetic sample data for the demo path."""
    raise NotImplementedError("ingest.load_sample_data is not implemented yet")
