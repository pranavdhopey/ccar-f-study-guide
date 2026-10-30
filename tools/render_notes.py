"""
Render a topic's handwritten notes: notes.html -> notes.png

    python tools/render_notes.py 1-agentic-architecture/1-1-agentic-loops

Needs:  pip install playwright && playwright install chromium
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

if len(sys.argv) != 2:
    sys.exit(__doc__)

topic = pathlib.Path(sys.argv[1]).resolve()
html = topic / "notes.html"
if not html.exists():
    sys.exit(f"No notes.html in {topic}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1500, "height": 1000}, device_scale_factor=1.5)
    page.goto(html.as_uri())
    page.wait_for_timeout(800)
    page.evaluate("document.fonts.ready")
    page.locator("#page").screenshot(path=str(topic / "notes.png"))
    browser.close()
print(f"wrote {topic / 'notes.png'}")
