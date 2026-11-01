"""Evidence chains, dossier, and ghost narration for Ghost Auditor.

Rules (see .kiro/steering/product.md):
- EVERY exception MUST cite its evidence chain: the order line, the
  invoice line (if any), and the portal value (if captured).
- An exception without an evidence reference MUST NOT appear in the
  dossier or the exported report.
- The ghost narration MUST only restate dossier facts. It MUST NOT
  invent new amounts, suppliers, or causes.
"""

import pandas as pd


def _money(cents: int) -> str:
    """Format integer cents for display only (internal values stay ints)."""
    return f"${cents / 100:,.2f}"


def _order_evidence(order_row: pd.Series) -> dict:
    return {
        "source": "orders",
        "order_id": str(order_row["order_id"]),
        "supplier": str(order_row["supplier"]),
        "item": str(order_row["item"]),
        "quantity": int(order_row["quantity"]),
        "unit_price_cents": int(order_row["unit_price_cents"]),
        "amount_cents": int(order_row["amount_cents"]),
        "row": int(order_row["row"]),
    }


def _invoice_evidence(inv_row: pd.Series) -> dict:
    return {
        "source": "invoices",
        "invoice_id": str(inv_row["record_id"]),
        "order_id": str(inv_row["order_id"]),
        "supplier": str(inv_row["supplier"]),
        "item": str(inv_row["item"]),
        "quantity": int(inv_row["quantity"]),
        "unit_price_cents": int(inv_row["unit_price_cents"]),
        "amount_cents": int(inv_row["amount_cents"]),
        "payment_status": str(inv_row["status"]),
        "row": int(inv_row["row"]),
    }


def attach_evidence(
    exceptions: list[dict],
    orders: pd.DataFrame,
    invoices: pd.DataFrame,
    portal_rows: pd.DataFrame | None = None,
) -> list[dict]:
    """Attach evidence chains to each exception.

    Drops any exception that ends up without an evidence reference.
    Portal evidence is attached when a portal row exists for the same
    order_id; it is evidence only and never changes a verdict.
    """
    order_by_id = {str(r["order_id"]): r for _, r in orders.iterrows()}
    invoice_by_id = {str(r["record_id"]): r for _, r in invoices.iterrows()}
    portal_by_id: dict[str, pd.Series] = {}
    if portal_rows is not None and not portal_rows.empty:
        for _, r in portal_rows.iterrows():
            portal_by_id[str(r["order_id"])] = r

    evidenced: list[dict] = []
    for exc in exceptions:
        order_row = order_by_id.get(exc["order_id"])
        if order_row is None:
            continue  # no order evidence -> must not appear in the dossier
        chain: dict = {"order": _order_evidence(order_row), "invoices": []}
        for ref in exc.get("invoice_refs", []):
            inv_row = invoice_by_id.get(ref["record_id"])
            if inv_row is not None:
                chain["invoices"].append(_invoice_evidence(inv_row))
        portal_row = portal_by_id.get(exc["order_id"])
        chain["portal"] = (
            {
                "source": "portal",
                "order_id": str(portal_row["order_id"]),
                "supplier": str(portal_row["supplier"]),
                "qty_received": int(portal_row["quantity"]),
                "amount_cents": int(portal_row["amount_cents"]),
                "payment_status": str(portal_row["status"]),
                "row": int(portal_row["row"]),
            }
            if portal_row is not None
            else None
        )
        evidenced.append({**exc, "evidence": chain})
    return evidenced


def build_dossier(
    exceptions: list[dict], matched: pd.DataFrame, total_orders: int = 0
) -> dict:
    """Build the dossier JSON (summary + exception list + narration)."""
    by_type: dict[str, int] = {}
    for exc in exceptions:
        by_type[exc["type"]] = by_type.get(exc["type"], 0) + 1
    dossier = {
        "summary": {
            "total_orders": int(total_orders),
            "matched_count": int(len(matched)),
            "exception_count": len(exceptions),
            "exceptions_by_type": by_type,
        },
        "exceptions": exceptions,
        "matched_order_ids": (
            [str(r["order_id"]) for _, r in matched.iterrows()]
            if not matched.empty
            else []
        ),
        "narration": "",
    }
    dossier["narration"] = narrate_worst_exception(dossier)
    return dossier


def narrate_worst_exception(dossier: dict) -> str:
    """One-sentence ghost narration of the worst exception.

    Restates dossier facts only: order id, supplier, and the recorded
    values. Never invents amounts, suppliers, or causes.
    """
    exceptions = dossier.get("exceptions", [])
    if not exceptions:
        return "Boo! The ghost found nothing out of place — every order reconciled."
    worst = exceptions[0]  # match.py already sorts worst-first
    d = worst["details"]
    supplier = d.get("supplier", "an unknown supplier")
    order_id = worst["order_id"]
    if worst["type"] == "duplicate_payment":
        return (
            f"Boo! Order {order_id} from {supplier} was paid "
            f"{d['paid_invoice_count']} times — "
            f"{_money(d['extra_paid_cents'])} paid more than once — "
            "and the receipts are in the dossier."
        )
    if worst["type"] == "missing_invoice":
        return (
            f"Boo! Order {order_id} from {supplier} has no invoice at all — "
            f"{_money(d['order_total_cents'])} with nothing to match it against."
        )
    if worst["type"] == "quantity_mismatch":
        return (
            f"Boo! Order {order_id} from {supplier} ordered "
            f"{d['ordered_qty']} but was invoiced for {d['invoiced_qty']}."
        )
    if worst["type"] == "price_difference":
        return (
            f"Boo! Order {order_id} from {supplier} was priced at "
            f"{_money(d['ordered_unit_price_cents'])} per unit on the order "
            f"but {_money(d['invoiced_unit_price_cents'])} on the invoice."
        )
    return f"Boo! Order {order_id} from {supplier} has an exception: {worst['type']}."


def render_markdown_report(dossier: dict) -> str:
    """Render the dossier as a Markdown report for download."""
    summary = dossier["summary"]
    lines = [
        "# Ghost Auditor — Exception Dossier",
        "",
        "A ghost that possesses your browser, cross-checks your orders, "
        "invoices, and payments, and hands you an auditable exception "
        "dossier — with evidence for every claim.",
        "",
        "## Summary",
        "",
        f"- Orders audited: {summary['total_orders']}",
        f"- Orders matched: {summary['matched_count']}",
        f"- Exceptions found: {summary['exception_count']}",
    ]
    for exc_type, count in sorted(summary["exceptions_by_type"].items()):
        lines.append(f"- {exc_type}: {count}")
    lines += [
        "",
        f"> 👻 {dossier['narration']}",
        "",
        "## Exceptions",
        "",
    ]
    if not dossier["exceptions"]:
        lines.append("No exceptions. Every order reconciled.")
    for exc in dossier["exceptions"]:
        lines.append(f"### {exc['type']} — {exc['order_id']} (severity: {exc['severity']})")
        lines.append("")
        d = exc["details"]
        if exc["type"] == "quantity_mismatch":
            lines.append(
                f"- Ordered qty: {d['ordered_qty']}; invoiced qty: "
                f"{d['invoiced_qty']} (invoice {d['invoice_id']})."
            )
        elif exc["type"] == "price_difference":
            lines.append(
                f"- Ordered unit price: {_money(d['ordered_unit_price_cents'])}; "
                f"invoiced unit price: {_money(d['invoiced_unit_price_cents'])} "
                f"(invoice {d['invoice_id']})."
            )
        elif exc["type"] == "missing_invoice":
            lines.append(
                f"- No invoice found for this order; order total "
                f"{_money(d['order_total_cents'])}."
            )
        elif exc["type"] == "duplicate_payment":
            lines.append(
                f"- Paid invoices: {', '.join(d['paid_invoice_ids'])}; "
                f"extra amount paid more than once: "
                f"{_money(d['extra_paid_cents'])}."
            )
        ev = exc["evidence"]
        lines.append("")
        lines.append("Evidence chain:")
        order = ev["order"]
        lines.append(
            f"- Order line (orders file, row {order['row']}): "
            f"{order['order_id']}, {order['supplier']}, {order['item']}, "
            f"qty {order['quantity']}, unit price "
            f"{_money(order['unit_price_cents'])}, total "
            f"{_money(order['amount_cents'])}."
        )
        for inv in ev["invoices"]:
            lines.append(
                f"- Invoice line (invoices file, row {inv['row']}): "
                f"{inv['invoice_id']}, qty {inv['quantity']}, unit price "
                f"{_money(inv['unit_price_cents'])}, total "
                f"{_money(inv['amount_cents'])}, status {inv['payment_status']}."
            )
        if ev["portal"] is not None:
            portal = ev["portal"]
            lines.append(
                f"- Portal value (mock portal, row {portal['row']}): "
                f"qty received {portal['qty_received']}, amount "
                f"{_money(portal['amount_cents'])}, status "
                f"{portal['payment_status']}."
            )
        else:
            lines.append("- Portal value: not captured.")
        lines.append("")
    lines += [
        "## Matched orders",
        "",
        (
            ", ".join(dossier["matched_order_ids"])
            if dossier["matched_order_ids"]
            else "None."
        ),
        "",
        "---",
        "",
        "All demo data in this report is synthetic and fictional. "
        "Every exception above cites its source rows.",
        "",
    ]
    return "\n".join(lines)
