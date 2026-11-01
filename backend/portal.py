"""Playwright portal capture for Ghost Auditor.

TODO (Week 3): launch Playwright, load the bundled mock portal page
(mock_portal/index.html), and scrape its order/payment rows.

Rules:
- Capture ONLY the bundled mock portal in this repo. Never point this
  module at a real supplier portal.
- Captured rows are returned in canonical shape (see normalize.py).
- If the portal page cannot be loaded, raise a clear error so the
  caller can degrade to file-only matching.

This module is a skeleton: functions below are placeholders and raise
NotImplementedError until implemented.
"""

import pathlib

MOCK_PORTAL_PATH = pathlib.Path(__file__).resolve().parent.parent / "mock_portal" / "index.html"


def capture_portal_rows() -> list[dict]:
    """TODO: use Playwright (Chromium) to scrape the mock portal rows.

    Returns a list of dicts with keys: order_id, supplier, qty_received,
    amount_cents, payment_status.
    """
    raise NotImplementedError("portal.capture_portal_rows is not implemented yet")
