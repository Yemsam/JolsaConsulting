#!/usr/bin/env python3
"""
Rebuilds the blog archive listing in blog.html and the blog post entries
in sitemap.xml from posts.json.

Run manually with:  python3 scripts/build_blog_index.py
It's also run automatically by .github/workflows/rebuild-blog-index.yml
whenever posts.json (or any blog-*.html file) changes on main.

This script only ever touches the text between the POSTS:START/END and
BLOG-POSTS:START/END marker comments — everything else in blog.html and
sitemap.xml (hero copy, meta tags, other pages' sitemap entries) is left
exactly as-is.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from site_template import render_blog_card, DOMAIN  # noqa: E402

POSTS_JSON = ROOT / "posts.json"
BLOG_HTML = ROOT / "blog.html"
SITEMAP_XML = ROOT / "sitemap.xml"

POSTS_MARKER = re.compile(
    r"(<!-- POSTS:START.*?-->\n)(.*?)(\n\s*<!-- POSTS:END -->)", re.S
)
SITEMAP_MARKER = re.compile(
    r"(<!-- BLOG-POSTS:START.*?-->\n)(.*?)(\n\s*<!-- BLOG-POSTS:END -->)", re.S
)


def load_posts():
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts = data["posts"]
    # newest first
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def update_blog_html(posts):
    content = BLOG_HTML.read_text(encoding="utf-8")
    cards = "\n".join(render_blog_card(p) for p in posts)
    new_content, n = POSTS_MARKER.subn(lambda m: m.group(1) + cards + m.group(3), content)
    if n == 0:
        raise SystemExit("ERROR: POSTS:START/END markers not found in blog.html")
    if new_content != content:
        BLOG_HTML.write_text(new_content, encoding="utf-8")
        print(f"blog.html updated ({len(posts)} posts)")
    else:
        print("blog.html already up to date")


def update_sitemap(posts):
    content = SITEMAP_XML.read_text(encoding="utf-8")
    entries = []
    for p in posts:
        entries.append(
            f"  <url>\n"
            f"    <loc>{DOMAIN}/{p['slug']}.html</loc>\n"
            f"    <lastmod>{p['date']}</lastmod>\n"
            f"    <changefreq>yearly</changefreq>\n"
            f"    <priority>0.5</priority>\n"
            f"  </url>"
        )
    block = "\n".join(entries)
    new_content, n = SITEMAP_MARKER.subn(lambda m: m.group(1) + block + m.group(3), content)
    if n == 0:
        raise SystemExit("ERROR: BLOG-POSTS:START/END markers not found in sitemap.xml")
    if new_content != content:
        SITEMAP_XML.write_text(new_content, encoding="utf-8")
        print(f"sitemap.xml updated ({len(posts)} blog urls)")
    else:
        print("sitemap.xml already up to date")


def check_missing_files(posts):
    missing = [p["slug"] for p in posts if not (ROOT / f"{p['slug']}.html").exists()]
    if missing:
        raise SystemExit(
            "ERROR: posts.json references files that don't exist: "
            + ", ".join(f"{s}.html" for s in missing)
        )


if __name__ == "__main__":
    posts = load_posts()
    check_missing_files(posts)
    update_blog_html(posts)
    update_sitemap(posts)
