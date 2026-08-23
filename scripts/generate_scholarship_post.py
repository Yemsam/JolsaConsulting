#!/usr/bin/env python3
"""
Weekly automated scholarship post generator for Jolsa Consulting.

What this does:
  1. Asks Claude (with its web search tool switched on) to find 1-3
     scholarships that are CURRENTLY OPEN for applications, with a real,
     verifiable deadline and an official application link.
  2. Has Claude draft a blog post about them in the site's existing tone
     and format.
  3. Writes the new post as blog-<slug>.html (same template as every
     other post on the site), and appends an entry to posts.json.

What this deliberately does NOT do: publish anything. It's meant to run
inside a GitHub Action that commits the new file to a branch and opens a
pull request — a human still reviews the deadline/eligibility/link
against the official source before it goes live. Scholarship details are
exactly the kind of fact that's costly to get wrong (a reader could miss
a real deadline because of an error in an unreviewed auto-post), so this
script always leaves a clear "verify before merging" trail: every
generated post carries a visible notice linking to the official source,
and the PR description (built in the GitHub Action) says the same thing.

Requires:
  pip install anthropic
  env var ANTHROPIC_API_KEY set (GitHub Actions secret in production)

Run manually to test:
  python3 scripts/generate_scholarship_post.py
"""
import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from site_template import render_post_page  # noqa: E402

POSTS_JSON = ROOT / "posts.json"

MODEL = os.environ.get("SCHOLARSHIP_POST_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = """You are a careful research assistant for Jolsa Consulting, a \
career/scholarship/study-abroad/visa-readiness consultancy serving Nigerian and \
other global applicants. You are drafting ONE new blog post for their site about \
currently open scholarships.

Hard rules:
- Only include scholarships whose application deadline is in the future relative \
to today's date, and that you found described on what looks like an official or \
highly reputable source (the scholarship provider's own site, a university, a \
government/embassy program, or a well-established scholarship database). Cite the \
official application URL for each one.
- Do not invent, estimate, or guess at deadlines, amounts, or eligibility \
criteria. If you are not confident of a detail from your search results, leave it \
out rather than filling it in.
- Cover 1 to 3 scholarships (quality over quantity). Prefer scholarships relevant \
to Nigerian/African applicants where possible, but broaden if nothing strong is \
open for that group right now.
- Do not repeat any scholarship already covered in the site's recent posts (a list \
of recent post titles is provided below) unless there is a genuinely new detail \
(e.g. deadline extended).
- Tone: match Jolsa Consulting's existing voice — direct, practical, no hype, no \
promises of admission/funding outcomes. Short paragraphs, scannable structure.

Output format: respond with ONLY a single JSON object (no markdown fences, no \
commentary before or after), with exactly these keys:
{
  "title": "...",                # Post title, specific (mentions the scholarship name/theme), not generic
  "slug": "...",                 # lowercase-hyphenated, starts with "blog-", e.g. "blog-daad-2027-deadline"
  "category": "...",             # short label e.g. "Scholarships"
  "meta_description": "...",     # <160 chars, plain description
  "read_time_minutes": 0,        # integer estimate
  "body_html": "...",            # inner HTML for the article body — see structure below
  "sources": ["https://...", "..."]   # the official URL(s) for each scholarship mentioned
}

body_html structure: valid HTML fragment using only these tags: <p>, <h2>, <ul>, \
<li>, <strong>, <a>. Start with a <p class="post-meta"> line stating the category \
and read time, like existing posts do. For each scholarship covered, use an <h2> \
with the scholarship name, then a <p> summary, then a <ul> with <li> items for \
Deadline, Eligibility, Funding covers, and How to apply (with an <a \
href="OFFICIAL_URL" target="_blank" rel="noopener noreferrer"> link to the \
official page). End with a <p> reminding readers to confirm every detail on the \
official page before applying, since deadlines can move. Do not use <h1> (the \
page template supplies its own)."""


def load_recent_titles(limit=15):
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    posts = sorted(data["posts"], key=lambda p: p["date"], reverse=True)
    return [p["title"] for p in posts[:limit]]


def call_claude(today_str, recent_titles):
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    user_prompt = (
        f"Today's date is {today_str}. Recent post titles already on the site "
        f"(avoid duplicating these): {json.dumps(recent_titles)}\n\n"
        "Search for scholarships that are currently open for applications and "
        "draft the post as specified in your instructions."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": user_prompt}],
    )

    # The final assistant text block should contain the JSON. Concatenate all
    # text blocks (tool-use turns may interleave text + tool_use blocks).
    text_parts = [block.text for block in response.content if block.type == "text"]
    return "\n".join(text_parts)


def extract_json(raw_text):
    # Claude was told to return only JSON, but be defensive: grab the first
    # {...} block in case any stray commentary slipped in.
    match = re.search(r"\{.*\}", raw_text, re.S)
    if not match:
        raise ValueError("No JSON object found in model output:\n" + raw_text[:2000])
    return json.loads(match.group(0))


def slugify_fallback(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"blog-{slug[:60]}"


def main():
    today = date.today() if hasattr(date, "today") else None
    # NOTE: in CI this runs with a real system clock, so date.today() is fine
    # there. (Avoided only inside Claude-orchestrated workflow scripts.)
    today_str = today.isoformat() if today else datetime.now(timezone.utc).date().isoformat()

    recent_titles = load_recent_titles()
    raw = call_claude(today_str, recent_titles)
    result = extract_json(raw)

    required = {"title", "slug", "category", "meta_description", "body_html", "sources"}
    missing = required - result.keys()
    if missing:
        raise SystemExit(f"ERROR: model output missing keys: {missing}")

    if not result["sources"]:
        raise SystemExit("ERROR: model returned no source URLs — refusing to publish a draft with no citations.")

    slug = result["slug"] or slugify_fallback(result["title"])
    if not slug.startswith("blog-"):
        slug = "blog-" + slug
    out_path = ROOT / f"{slug}.html"
    if out_path.exists():
        slug = f"{slug}-{today_str}"
        out_path = ROOT / f"{slug}.html"

    post_meta = {
        "slug": slug,
        "title": result["title"],
        "category": result["category"],
        "meta_description": result["meta_description"],
    }
    html = render_post_page(post_meta, result["body_html"])
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path.name}")

    # Append to posts.json
    data = json.loads(POSTS_JSON.read_text(encoding="utf-8"))
    data["posts"].append(
        {
            "slug": slug,
            "title": result["title"],
            "category": result["category"],
            "meta_description": result["meta_description"],
            "excerpt": result["meta_description"],
            "date": today_str,
            "source": "auto",
            "sources_cited": result["sources"],
        }
    )
    POSTS_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Updated posts.json")

    # Emit info for the GitHub Action to use in the PR title/body.
    print(f"::set-output name=slug::{slug}")
    print(f"::set-output name=title::{result['title']}")
    sources_line = "\n".join(f"- {u}" for u in result["sources"])
    summary = (
        f"POST_TITLE={result['title']}\n"
        f"POST_SLUG={slug}\n"
        f"POST_SOURCES<<EOF\n{sources_line}\nEOF\n"
    )
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"slug={slug}\n")
            f.write(f"title={result['title']}\n")


if __name__ == "__main__":
    main()
