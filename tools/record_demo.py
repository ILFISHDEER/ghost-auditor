"""Record the Ghost Auditor demo video: drives the real app in a real
Chrome window (under Xvfb) while ffmpeg captures the virtual screen.

Usage (from the repo root):
  Xvfb :99 -screen 0 1280x720x24 &
  DISPLAY=:99 ffmpeg -y -f x11grab -video_size 1280x720 -framerate 25 \
      -i :99 -c:v libx264 -pix_fmt yuv420p /tmp/ghost-demo.mp4 &
  DISPLAY=:99 .venv/bin/python tools/record_demo.py
  pkill -INT -f x11grab   # finalize the mp4
"""

import glob
import time

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"


def pause(page, seconds, label):
    print(f"[{label}] pausing {seconds}s")
    page.wait_for_timeout(seconds * 1000)


def main():
    orders = sorted(glob.glob("sample_data/orders.*"))
    invoices = sorted(glob.glob("sample_data/invoices.*"))
    print("orders files:", orders)
    print("invoices files:", invoices)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/bin/google-chrome-stable",
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1280,720",
                "--window-position=0,0",
            ],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(BASE, wait_until="networkidle", timeout=30000)
        page.wait_for_selector("#summon-btn", timeout=15000)
        pause(page, 5, "header")

        # Shot 1: show the upload area, feed the ghost real sample files
        # (falls back to bundled sample data if the files are absent).
        page.locator("#upload-area").scroll_into_view_if_needed()
        if orders:
            page.set_input_files("#orders-file", orders[0])
        if invoices:
            page.set_input_files("#invoices-file", invoices[0])
        pause(page, 5, "upload area")

        # Shot 2: summon
        page.locator("#summon").scroll_into_view_if_needed()
        pause(page, 2, "before summon")
        page.click("#summon-btn")
        page.wait_for_selector("#dossier-list article.exception", timeout=30000)
        pause(page, 4, "dossier appeared")

        # Shot 3: walk the four exceptions, lingering on each evidence chain
        articles = page.locator("#dossier-list article.exception")
        count = articles.count()
        print(f"exceptions rendered: {count}")
        for i in range(count):
            articles.nth(i).scroll_into_view_if_needed()
            pause(page, 12, f"exception {i + 1}/{count}")

        # Shot 4: ghost narration + export
        page.locator("#ghost-narration").scroll_into_view_if_needed()
        pause(page, 5, "ghost narration")
        page.click("#export-btn")
        pause(page, 4, "export clicked")

        # Shot 5: close on the header
        page.evaluate("window.scrollTo(0, 0)")
        pause(page, 6, "closing header")
        browser.close()
    print("recording drive complete")


if __name__ == "__main__":
    main()
