"""Deterministic matching engine for Ghost Auditor.

TODO (Week 2): implement the matching rules over canonical tables.

Rules, applied in order:
1. Exact order-id join between orders and invoices.
2. Quantity check: invoice qty vs order qty -> `quantity_mismatch`.
3. Unit-price check: invoice unit_price_cents vs order unit_price_cents
   -> `price_difference`.
4. Duplicate-payment check: two paid invoices referencing the same
   order -> `duplicate_payment`.
5. Missing-invoice check: order with no invoice at all
   -> `missing_invoice`.
6. Otherwise the order is `matched` and produces no exception.

Hard rule: verdicts are deterministic only. No language model may
guess, infer, or invent an amount, quantity, supplier, or verdict.
Ambiguous data becomes an exception that says so; it is never silently
resolved.

This module is a skeleton: functions below are placeholders and raise
NotImplementedError until implemented.
"""

import pandas as pd


def match(
    orders: pd.DataFrame, invoices: pd.DataFrame
) -> tuple[pd.DataFrame, list[dict]]:
    """TODO: run deterministic matching.

    Returns (matched_orders, exceptions). Each exception is a dict with
    at least: type, order_id, severity, and the conflicting values.
    """
    raise NotImplementedError("match.match is not implemented yet")
