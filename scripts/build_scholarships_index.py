#!/usr/bin/env python3
"""
Rebuilds the scholarship card grid in scholarships.html and the
scholarship-detail-page entries in sitemap.xml from scholarships.json.

Run manually with:  python3 scripts/build_scholarships_index.py
It's also run automatically by .github/workflows/rebuild-scholarships-index.yml
whenever scholarships.json (or any scholarship-*.html file) changes on main.

This script only ever touches the text between the SCHOLARSHIPS:START/END
and SCHOLARSHIP-PAGES:START/END marker comments — everything else in
scholarships.html and sitemap.xml is left exactly as-is.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from site_template import render_scholarship_card, DOMAIN  # noqa: E402

SCHOLARSHIPS_JSON = ROOT / "scholarships.json"
SCHOLARSHIPS_HTML = ROOT / "scholarships.html"
SITEMAP_XML = ROOT / "sitemap.xml"

CARDS_MARKER = re.compile(
    r"(<!-- SCHOLARSHIPS:START.*?-->\n)(.*?)(\n\s*<!-- SCHOLARSHIPS:END -->)", re.S
)
SITEMAP_MARKER = re.compile(
    r"(<!-- SCHOLARSHIP-PAGES:START.*?-->\n)(.*?)(\n\s*<!-- SCHOLARSHIP-PAGES:END -->)", re.S
)


def load_scholarships():
    data = json.loads(SCHOLARSHIPS_JSON.read_text(encoding="utf-8"))
    items = data["scholarships"]
    # newest date_posted first
    items.sort(key=lambda s: s["date_posted"], reverse=True)
    return items


def update_scholarships_html(items):
    content = SCHOLARSHIPS_HTML.read_text(encoding="utf-8")
    cards = "\n".join(render_scholarship_card(s) for s in items)
    new_content, n = CARDS_MARKER.subn(lambda m: m.group(1) + cards + m.group(3), content)
    if n == 0:
        raise SystemExit("ERROR: SCHOLARSHIPS:START/END markers not found in scholarships.html")
    if new_content != content:
        SCHOLARSHIPS_HTML.write_text(new_content, encoding="utf-8")
        print(f"scholarships.html updated ({len(items)} scholarships)")
    else:
        print("scholarships.html already up to date")


def update_sitemap(items):
    content = SITEMAP_XML.read_text(encoding="utf-8")
    entries = []
    for s in items:
        entries.append(
            f"  <url>\n"
            f"    <loc>{DOMAIN}/scholarship-{s['slug']}.html</loc>\n"
            f"    <lastmod>{s['date_posted']}</lastmod>\n"
            f"    <changefreq>weekly</changefreq>\n"
            f"    <priority>0.7</priority>\n"
            f"  </url>"
        )
    block = "\n".join(entries)
    new_content, n = SITEMAP_MARKER.subn(lambda m: m.group(1) + block + m.group(3), content)
    if n == 0:
        raise SystemExit("ERROR: SCHOLARSHIP-PAGES:START/END markers not found in sitemap.xml")
    if new_content != content:
        SITEMAP_XML.write_text(new_content, encoding="utf-8")
        print(f"sitemap.xml updated ({len(items)} scholarship urls)")
    else:
        print("sitemap.xml already up to date")


def check_missing_files(items):
    missing = [s["slug"] for s in items if not (ROOT / f"scholarship-{s['slug']}.html").exists()]
    if missing:
        raise SystemExit(
            "ERROR: scholarships.json references detail pages that don't exist: "
            + ", ".join(f"scholarship-{s}.html" for s in missing)
        )


if __name__ == "__main__":
    items = load_scholarships()
    check_missing_files(items)
    update_scholarships_html(items)
    update_sitemap(items)
