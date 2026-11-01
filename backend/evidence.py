"""Evidence chains, dossier, and ghost narration for Ghost Auditor.

TODO (Week 3): attach evidence to every exception and build the
dossier + Markdown report.

Rules (see .kiro/steering/product.md):
- EVERY exception MUST cite its evidence chain: the order line, the
  invoice line (if any), and the portal value (if captured).
- An exception without an evidence reference MUST NOT appear in the
  dossier or the exported report.
- The ghost narration MUST only restate dossier facts. It MUST NOT
  invent new amounts, suppliers, or causes.

This module is a skeleton: functions below are placeholders and raise
NotImplementedError until implemented.
"""

import pandas as pd


def attach_evidence(
    exceptions: list[dict],
    orders: pd.DataFrame,
    invoices: pd.DataFrame,
    portal_rows: pd.DataFrame | None = None,
) -> list[dict]:
    """TODO: attach evidence chains to each exception.

    Drops any exception that ends up without an evidence reference.
    """
    raise NotImplementedError("evidence.attach_evidence is not implemented yet")


def build_dossier(exceptions: list[dict], matched: pd.DataFrame) -> dict:
    """TODO: build the dossier JSON (summary + exception list)."""
    raise NotImplementedError("evidence.build_dossier is not implemented yet")


def narrate_worst_exception(dossier: dict) -> str:
    """TODO: one-sentence ghost narration of the worst exception.

    Must restate dossier facts only.
    """
    raise NotImplementedError("evidence.narrate_worst_exception is not implemented yet")


def render_markdown_report(dossier: dict) -> str:
    """TODO: render the dossier as a Markdown report for download."""
    raise NotImplementedError("evidence.render_markdown_report is not implemented yet")
