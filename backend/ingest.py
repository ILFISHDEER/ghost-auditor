"""File ingestion for Ghost Auditor.

Parses uploaded orders/invoices files into pandas DataFrames and
validates required columns. Accepts CSV and XLSX only; anything else,
and any file missing required columns, is rejected with a clear error
message. Also loads the bundled synthetic sample data used by the
no-upload demo path.

No audit verdicts are produced here — parsing and validation only.
"""

import io
import pathlib

import pandas as pd

ORDERS_REQUIRED_COLUMNS = [
    "order_id",
    "supplier",
    "item",
    "qty",
    "unit_price",
    "total",
    "order_date",
]

INVOICES_REQUIRED_COLUMNS = [
    "invoice_id",
    "order_id",
    "supplier",
    "item",
    "qty",
    "unit_price",
    "total",
    "invoice_date",
    "payment_status",
]

SAMPLE_DATA_DIR = pathlib.Path(__file__).resolve().parent / "sample_data"


class IngestError(ValueError):
    """Raised when an uploaded file cannot be parsed or validated."""


def _read_bytes(filename: str, data: bytes) -> pd.DataFrame:
    """Parse file bytes as CSV or XLSX based on the file extension."""
    suffix = pathlib.Path(filename).suffix.lower()
    try:
        if suffix == ".csv":
            return pd.read_csv(io.BytesIO(data))
        if suffix == ".xlsx":
            return pd.read_excel(io.BytesIO(data), engine="openpyxl")
    except Exception as exc:  # unreadable file, bad encoding, bad workbook
        raise IngestError(f"could not read {filename!r}: {exc}") from exc
    raise IngestError(
        f"unsupported file format for {filename!r}: only .csv and .xlsx "
        "are accepted"
    )


def _validate(df: pd.DataFrame, required: list[str], kind: str) -> pd.DataFrame:
    """Check required columns; report exactly which ones are missing."""
    df = df.copy()
    # Tolerate stray whitespace in header names.
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise IngestError(
            f"{kind} file is missing required column(s): "
            f"{', '.join(missing)}"
        )
    if df.empty:
        raise IngestError(f"{kind} file has no data rows")
    return df


def parse_upload(filename: str, data: bytes, kind: str) -> pd.DataFrame:
    """Parse one uploaded file (``kind`` is "orders" or "invoices")."""
    required = (
        ORDERS_REQUIRED_COLUMNS if kind == "orders" else INVOICES_REQUIRED_COLUMNS
    )
    df = _read_bytes(filename, data)
    return _validate(df, required, kind)


def _load_path(path: str | pathlib.Path, kind: str) -> pd.DataFrame:
    path = pathlib.Path(path)
    if not path.exists():
        raise IngestError(f"{kind} file not found: {path}")
    return parse_upload(path.name, path.read_bytes(), kind)


def load_orders(path: str) -> pd.DataFrame:
    """Load an orders CSV/XLSX file from disk into a DataFrame."""
    return _load_path(path, "orders")


def load_invoices(path: str) -> pd.DataFrame:
    """Load an invoices CSV/XLSX file from disk into a DataFrame."""
    return _load_path(path, "invoices")


def load_sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the bundled synthetic sample data for the demo path."""
    orders = _load_path(SAMPLE_DATA_DIR / "orders.csv", "orders")
    invoices = _load_path(SAMPLE_DATA_DIR / "invoices.csv", "invoices")
    return orders, invoices
