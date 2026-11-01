"""Playwright portal capture for Ghost Auditor.

Launches Playwright (Chromium), loads ONLY the bundled mock portal page
(mock_portal/index.html), and scrapes its order/payment rows.

Rules:
- Capture ONLY the bundled mock portal in this repo. Never point this
  module at a real supplier portal.
- Captured rows are returned as plain dicts; normalize.py maps them
  onto the canonical schema.
- If Playwright or the browser is unavailable, or the page cannot be
  loaded, raise PortalCaptureError so the caller can degrade to
  file-only matching.
"""

import pathlib
from decimal import Decimal

MOCK_PORTAL_PATH = pathlib.Path(__file__).resolve().parent.parent / "mock_portal" / "index.html"


class PortalCaptureError(RuntimeError):
    """Raised when the mock portal cannot be captured."""


def _to_cents(text: str) -> int:
    return int((Decimal(text.strip().replace(",", "").replace("$", "")) * 100).quantize(Decimal("1")))


def capture_portal_rows() -> list[dict]:
    """Use Playwright (Chromium) to scrape the mock portal rows.

    Returns a list of dicts with keys: order_id, supplier,
    qty_received, amount_cents, payment_status.
    """
    if not MOCK_PORTAL_PATH.exists():
        raise PortalCaptureError(f"mock portal page not found: {MOCK_PORTAL_PATH}")
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise PortalCaptureError(
            "Playwright is not installed; portal capture is unavailable"
        ) from exc

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(MOCK_PORTAL_PATH.as_uri())
            page.wait_for_selector("#portal-orders tbody tr")
            rows = []
            for tr in page.query_selector_all("#portal-orders tbody tr"):
                cells = [td.inner_text().strip() for td in tr.query_selector_all("td")]
                if len(cells) != 5:
                    continue
                order_id, supplier, qty_received, amount, status = cells
                rows.append(
                    {
                        "order_id": order_id,
                        "supplier": supplier,
                        "qty_received": int(qty_received),
                        "amount_cents": _to_cents(amount),
                        "payment_status": status,
                    }
                )
            browser.close()
    except PortalCaptureError:
        raise
    except Exception as exc:
        raise PortalCaptureError(f"could not capture the mock portal: {exc}") from exc

    if not rows:
        raise PortalCaptureError("mock portal table had no rows to capture")
    return rows
