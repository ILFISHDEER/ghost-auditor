"""Canonical schema normalization for Ghost Auditor.

Maps every source (orders, invoices, portal rows) onto one canonical
schema so matching compares like with like:

    order_id (str), supplier (str), item (str),
    quantity (int), unit_price_cents (int), amount_cents (int),
    status (str), source (str: "orders" | "invoices" | "portal"),
    record_id (str), date (ISO YYYY-MM-DD str), row (int, 1-based data
    row number in the source file/table, for evidence citations)

Rules:
- Money is stored as integer cents internally, converted with
  Decimal so no float arithmetic ever touches an amount. Never
  compare float money values for equality.
- Quantities are coerced to int; a non-integral quantity is an error.
- Portal rows have no unit price, so their unit_price_cents is None
  (they are evidence only, never matching input).
- This module makes NO matching verdicts; it only normalizes.
"""

from decimal import Decimal, InvalidOperation

import pandas as pd


class NormalizeError(ValueError):
    """Raised when a value cannot be coerced into the canonical schema."""


def to_cents(value: object, *, field: str, row: int) -> int:
    """Convert a money value to integer cents via Decimal (no floats)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise NormalizeError(f"row {row}: {field} is missing")
    text = str(value).strip().replace(",", "").replace("$", "")
    try:
        cents = (Decimal(text) * 100).quantize(Decimal("1"))
    except (InvalidOperation, ValueError) as exc:
        raise NormalizeError(
            f"row {row}: {field} value {value!r} is not a valid amount"
        ) from exc
    return int(cents)


def to_int(value: object, *, field: str, row: int) -> int:
    """Coerce a quantity to int; non-integral values are errors."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise NormalizeError(f"row {row}: {field} is missing")
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise NormalizeError(
            f"row {row}: {field} value {value!r} is not a valid number"
        ) from exc
    if number != number.to_integral_value():
        raise NormalizeError(
            f"row {row}: {field} value {value!r} is not a whole number"
        )
    return int(number)


def _text(value: object, *, field: str, row: int) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise NormalizeError(f"row {row}: {field} is missing")
    text = str(value).strip()
    if not text:
        raise NormalizeError(f"row {row}: {field} is empty")
    return text


def _date(value: object, *, field: str, row: int) -> str:
    """Normalize a date to an ISO YYYY-MM-DD string (best effort)."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        raise NormalizeError(f"row {row}: {field} is missing")
    stamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(stamp):
        raise NormalizeError(f"row {row}: {field} value {value!r} is not a date")
    return stamp.strftime("%Y-%m-%d")


def normalize_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize an orders DataFrame to the canonical schema."""
    records = []
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        records.append(
            {
                "order_id": _text(r["order_id"], field="order_id", row=i),
                "supplier": _text(r["supplier"], field="supplier", row=i),
                "item": _text(r["item"], field="item", row=i),
                "quantity": to_int(r["qty"], field="qty", row=i),
                "unit_price_cents": to_cents(r["unit_price"], field="unit_price", row=i),
                "amount_cents": to_cents(r["total"], field="total", row=i),
                "status": "ordered",
                "source": "orders",
                "record_id": _text(r["order_id"], field="order_id", row=i),
                "date": _date(r["order_date"], field="order_date", row=i),
                "row": i,
            }
        )
    return pd.DataFrame.from_records(records)


def normalize_invoices(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize an invoices DataFrame to the canonical schema."""
    records = []
    for i, (_, r) in enumerate(df.iterrows(), start=1):
        records.append(
            {
                "order_id": _text(r["order_id"], field="order_id", row=i),
                "supplier": _text(r["supplier"], field="supplier", row=i),
                "item": _text(r["item"], field="item", row=i),
                "quantity": to_int(r["qty"], field="qty", row=i),
                "unit_price_cents": to_cents(r["unit_price"], field="unit_price", row=i),
                "amount_cents": to_cents(r["total"], field="total", row=i),
                "status": _text(r["payment_status"], field="payment_status", row=i).lower(),
                "source": "invoices",
                "record_id": _text(r["invoice_id"], field="invoice_id", row=i),
                "date": _date(r["invoice_date"], field="invoice_date", row=i),
                "row": i,
            }
        )
    return pd.DataFrame.from_records(records)


def normalize_portal_rows(rows: list[dict]) -> pd.DataFrame:
    """Normalize captured portal rows to the canonical schema.

    Portal rows carry no unit price, so unit_price_cents is None for
    them. They are evidence only and are never used as matching
    input, so the missing unit price is safe.
    """
    records = []
    for i, r in enumerate(rows, start=1):
        records.append(
            {
                "order_id": str(r["order_id"]),
                "supplier": str(r["supplier"]),
                "item": "",
                "quantity": int(r["qty_received"]),
                "unit_price_cents": None,
                "amount_cents": int(r["amount_cents"]),
                "status": str(r["payment_status"]),
                "source": "portal",
                "record_id": str(r["order_id"]),
                "date": "",
                "row": i,
            }
        )
    return pd.DataFrame.from_records(records)
