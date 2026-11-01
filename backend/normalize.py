"""Canonical schema normalization for Ghost Auditor.

TODO (Week 2): map every source (orders, invoices, portal rows) onto
one canonical schema so matching compares like with like.

Canonical schema:
    order_id (str), supplier (str), item (str),
    qty (int), unit_price_cents (int), total_cents (int),
    status (str), source (str: "orders" | "invoices" | "portal")

Rules:
- Money is stored as integer cents internally. Never compare float
  money values for equality.
- Quantities are coerced to int.
- Dates are normalized to ISO format (YYYY-MM-DD) strings.
- This module makes NO matching verdicts; it only normalizes.

This module is a skeleton: functions below are placeholders and raise
NotImplementedError until implemented.
"""

import pandas as pd


def normalize_orders(df: pd.DataFrame) -> pd.DataFrame:
    """TODO: normalize an orders DataFrame to the canonical schema."""
    raise NotImplementedError("normalize.normalize_orders is not implemented yet")


def normalize_invoices(df: pd.DataFrame) -> pd.DataFrame:
    """TODO: normalize an invoices DataFrame to the canonical schema."""
    raise NotImplementedError("normalize.normalize_invoices is not implemented yet")


def normalize_portal_rows(rows: list[dict]) -> pd.DataFrame:
    """TODO: normalize captured portal rows to the canonical schema."""
    raise NotImplementedError("normalize.normalize_portal_rows is not implemented yet")
