"""Deterministic matching engine for Ghost Auditor.

Rules, applied in order:
1. Exact order-id join between orders and invoices.
2. Quantity check: invoice qty vs order qty -> `quantity_mismatch`.
3. Unit-price check: invoice unit_price_cents vs order unit_price_cents
   -> `price_difference`.
4. Duplicate-payment check: two or more paid invoices referencing the
   same order -> `duplicate_payment`.
5. Missing-invoice check: order with no invoice at all
   -> `missing_invoice`.
6. Otherwise the order is `matched` and produces no exception.

Hard rule: verdicts are deterministic only. No language model may
guess, infer, or invent an amount, quantity, supplier, or verdict.
Ambiguous data becomes an exception that says so; it is never silently
resolved.

Each exception records the order row and invoice row(s) it came from
so evidence.py can cite them, plus an impact in integer cents used
only to rank exceptions for narration (largest impact first).
"""

import pandas as pd

SEVERITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _row_ref(row: pd.Series) -> dict:
    return {
        "source": row["source"],
        "record_id": row["record_id"],
        "order_id": row["order_id"],
        "row": int(row["row"]),
    }


def match(
    orders: pd.DataFrame, invoices: pd.DataFrame
) -> tuple[pd.DataFrame, list[dict]]:
    """Run deterministic matching.

    Returns (matched_orders, exceptions). Each exception is a dict with
    type, order_id, severity, conflicting values, impact_cents, and
    the order/invoice row references it came from.
    """
    invoices_by_order: dict[str, list[pd.Series]] = {}
    for _, inv in invoices.iterrows():
        invoices_by_order.setdefault(str(inv["order_id"]), []).append(inv)

    matched_rows: list[pd.Series] = []
    exceptions: list[dict] = []

    for _, order in orders.iterrows():
        order_id = str(order["order_id"])
        order_ref = _row_ref(order)
        invs = invoices_by_order.get(order_id, [])
        order_exceptions: list[dict] = []

        if not invs:
            order_exceptions.append(
                {
                    "type": "missing_invoice",
                    "order_id": order_id,
                    "severity": "high",
                    "details": {
                        "order_total_cents": int(order["amount_cents"]),
                        "supplier": str(order["supplier"]),
                        "item": str(order["item"]),
                    },
                    "impact_cents": int(order["amount_cents"]),
                    "order_ref": order_ref,
                    "invoice_refs": [],
                }
            )
        else:
            paid = [inv for inv in invs if str(inv["status"]).lower() == "paid"]
            if len(paid) >= 2:
                extra = paid[1:]
                order_exceptions.append(
                    {
                        "type": "duplicate_payment",
                        "order_id": order_id,
                        "severity": "high",
                        "details": {
                            "paid_invoice_count": len(paid),
                            "paid_invoice_ids": [str(i["record_id"]) for i in paid],
                            "extra_paid_cents": sum(int(i["amount_cents"]) for i in extra),
                            "supplier": str(order["supplier"]),
                        },
                        "impact_cents": sum(int(i["amount_cents"]) for i in extra),
                        "order_ref": order_ref,
                        "invoice_refs": [_row_ref(i) for i in paid],
                    }
                )
            for inv in invs:
                inv_ref = _row_ref(inv)
                if int(inv["quantity"]) != int(order["quantity"]):
                    order_exceptions.append(
                        {
                            "type": "quantity_mismatch",
                            "order_id": order_id,
                            "severity": "medium",
                            "details": {
                                "invoice_id": str(inv["record_id"]),
                                "ordered_qty": int(order["quantity"]),
                                "invoiced_qty": int(inv["quantity"]),
                                "supplier": str(order["supplier"]),
                            },
                            "impact_cents": abs(
                                int(inv["quantity"]) - int(order["quantity"])
                            )
                            * int(order["unit_price_cents"]),
                            "order_ref": order_ref,
                            "invoice_refs": [inv_ref],
                        }
                    )
                if int(inv["unit_price_cents"]) != int(order["unit_price_cents"]):
                    order_exceptions.append(
                        {
                            "type": "price_difference",
                            "order_id": order_id,
                            "severity": "medium",
                            "details": {
                                "invoice_id": str(inv["record_id"]),
                                "ordered_unit_price_cents": int(order["unit_price_cents"]),
                                "invoiced_unit_price_cents": int(inv["unit_price_cents"]),
                                "supplier": str(order["supplier"]),
                            },
                            "impact_cents": abs(
                                int(inv["unit_price_cents"])
                                - int(order["unit_price_cents"])
                            )
                            * int(inv["quantity"]),
                            "order_ref": order_ref,
                            "invoice_refs": [inv_ref],
                        }
                    )

        if order_exceptions:
            exceptions.extend(order_exceptions)
        else:
            matched_rows.append(order)

    matched = pd.DataFrame(matched_rows) if matched_rows else pd.DataFrame()
    # Deterministic order: severity rank, then largest impact, then order_id.
    exceptions.sort(
        key=lambda e: (
            SEVERITY_RANK[e["severity"]],
            -e["impact_cents"],
            e["order_id"],
            e["type"],
        )
    )
    return matched, exceptions
