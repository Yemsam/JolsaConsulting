#!/usr/bin/env python3
"""
Weekly automated scholarship listing generator for Jolsa Consulting.

What this does:
  1. Asks Claude (with its web search tool switched on) to find ONE
     scholarship that is CURRENTLY OPEN (or opening soon) for applications,
     with a real, verifiable deadline and an official application link.
  2. Has Claude draft a clear, scholarshipregion.com-style detail page
     about it: overview, benefits, eligibility, timeline, how to apply,
     tips, and FAQs — so a reader fully understands what the opportunity
     is and how to act on it.
  3. Writes a new scholarship-<slug>.html detail page (same template as
     every other scholarship on the site) and appends a structured entry
     to scholarships.json, which drives the filterable Scholarships hub
     (scholarships.html) — this is a dedicated, SEO-optimized directory
     page, not a blog post.

What this deliberately does NOT do: publish anything. It's meant to run
inside a GitHub Action that commits the new files to a branch and opens a
pull request — a human still reviews the deadline/eligibility/link
against the official source before it goes live. Scholarship details are
exactly the kind of fact that's costly to get wrong (a reader could miss
a real deadline because of an error in an unreviewed auto-post), so this
script always leaves a clear "verify before merging" trail: every
generated page carries a visible notice linking to the official source,
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
from site_template import render_scholarship_detail_page, SCHOLARSHIP_LEVELS  # noqa: E402

SCHOLARSHIPS_JSON = ROOT / "scholarships.json"

MODEL = os.environ.get("SCHOLARSHIP_POST_MODEL", "claude-sonnet-4-5")

SYSTEM_PROMPT = f"""You are a careful research assistant for Jolsa Consulting, a \
career/scholarship/study-abroad/visa-readiness consultancy serving Nigerian and \
other global applicants. You are adding ONE new entry to their Scholarships \
directory page — a dedicated, filterable listing of real scholarship \
opportunities (not a blog post).

Hard rules:
- Cover exactly ONE scholarship per run, currently open for applications OR \
opening within the next 60 days, with a deadline in the future relative to \
today's date.
- You may use scholarship aggregator/roundup sites (e.g. scholarshipregion.com, \
opportunitydesk.org, and similar) purely to discover WHICH scholarships are \
currently being talked about — they are a lead, not a source. Every fact you \
publish (deadline, amount, eligibility, how to apply) MUST come from, and be \
cited to, the scholarship's own official page (the provider's own site, a \
university, a government/embassy program) — never copy or closely paraphrase \
an aggregator site's wording or structure. If you cannot find the official page \
for a scholarship you noticed on an aggregator, skip it rather than writing from \
the aggregator alone.
- Do not invent, estimate, or guess at deadlines, amounts, or eligibility \
criteria. If you are not confident of a detail from your search results, leave it \
out rather than filling it in.
- Do not repeat any scholarship already on the site (a list of recent titles is \
provided below) unless there is a genuinely new detail (e.g. deadline extended \
for a new cycle) — in that case treat it as a new entry with a distinct slug.
- Prefer scholarships relevant to Nigerian/African applicants where possible, but \
broaden if nothing strong is open for that group right now.
- Write body_html so a reader fully understands the opportunity without leaving \
the page: what it is, what it covers, who is eligible, the timeline, how to \
apply step by step, application tips, and 1-2 FAQs. This should read like a \
clear, complete explainer (similar in thoroughness to sites like \
scholarshipregion.com), not a short teaser.
- Tone: match Jolsa Consulting's existing voice — direct, practical, no hype, no \
promises of admission/funding outcomes. Short paragraphs, scannable structure.

Output format: respond with ONLY a single JSON object (no markdown fences, no \
commentary before or after), with exactly these keys:
{{
  "title": "...",                 # e.g. "DAAD Scholarship 2027 (Germany, Fully Funded Master's)"
  "slug": "...",                  # lowercase-hyphenated, no "blog-"/"scholarship-" prefix, e.g. "daad-scholarship-2027"
  "level": ["..."],               # subset of {SCHOLARSHIP_LEVELS!r}
  "country": "...",               # host country, or "Global" if multiple/not location-specific
  "funding_type": "...",          # e.g. "Fully Funded" or "Partial Funding"
  "deadline": "YYYY-MM-DD",       # application deadline
  "status": "...",                # "open" if applications are open now, "upcoming" if opening later
  "summary": "...",               # 1-2 sentence plain summary for the card, no HTML
  "meta_description": "...",      # <160 chars, plain description for SEO
  "funder": "...",                # the organization funding/running it
  "official_url": "https://...",  # the single best official page to link as the source
  "sources": ["https://...", "..."],   # all official URL(s) you verified facts against
  "body_html": "..."              # inner HTML for the detail page body — see structure below
}}

body_html structure: valid HTML fragment using only these tags: <p>, <h2>, <ul>, \
<ol>, <li>, <strong>, <a>, and a closing <div class="source-callout"> block. \
Structure: <h2>What is [name]?</h2> overview paragraph(s); <h2>What does it \
cover?</h2> with a <ul>; <h2>Who is eligible?</h2> with a <ul>; <h2>Application \
timeline</h2> with a <ul> of dated milestones (or a single deadline paragraph if \
that's all that's confirmed); <h2>How to apply</h2> as an <ol> of steps; \
<h2>Application tips</h2> with a <ul>; <h2>FAQs</h2> with a couple of <p><strong> \
question</strong> answer</p> pairs; and finally a \
<div class="source-callout">Always verify current dates and eligibility directly \
on the official [Name] website: <a href="OFFICIAL_URL" target="_blank" \
rel="noopener noreferrer">official link text</a>.</div>. Do not use <h1> (the page \
template supplies its own)."""


def load_recent_titles(limit=15):
    data = json.loads(SCHOLARSHIPS_JSON.read_text(encoding="utf-8"))
    items = sorted(data["scholarships"], key=lambda s: s["date_posted"], reverse=True)
    return [s["title"] for s in items[:limit]]


def call_claude(today_str, recent_titles):
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    user_prompt = (
        f"Today's date is {today_str}. Scholarships already on the site "
        f"(avoid duplicating these): {json.dumps(recent_titles)}\n\n"
        "Search for one scholarship that is currently open (or opening within "
        "60 days) for applications and draft the entry as specified in your "
        "instructions."
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
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60]


def main():
    today = date.today() if hasattr(date, "today") else None
    # NOTE: in CI this runs with a real system clock, so date.today() is fine
    # there. (Avoided only inside Claude-orchestrated workflow scripts.)
    today_str = today.isoformat() if today else datetime.now(timezone.utc).date().isoformat()

    recent_titles = load_recent_titles()
    raw = call_claude(today_str, recent_titles)
    result = extract_json(raw)

    required = {
        "title", "slug", "level", "country", "funding_type", "deadline",
        "status", "summary", "meta_description", "funder", "official_url",
        "sources", "body_html",
    }
    missing = required - result.keys()
    if missing:
        raise SystemExit(f"ERROR: model output missing keys: {missing}")

    if not result["sources"] or not result["official_url"]:
        raise SystemExit("ERROR: model returned no source URL — refusing to publish an entry with no citation.")

    bad_levels = [lvl for lvl in result["level"] if lvl not in SCHOLARSHIP_LEVELS]
    if bad_levels or not result["level"]:
        raise SystemExit(f"ERROR: model returned invalid level(s): {result.get('level')}")

    if result["status"] not in ("open", "upcoming"):
        raise SystemExit(f"ERROR: model returned invalid status: {result.get('status')!r} (expected 'open' or 'upcoming')")

    slug = result["slug"] or slugify_fallback(result["title"])
    slug = re.sub(r"^(blog-|scholarship-)+", "", slug)
    detail_path = ROOT / f"scholarship-{slug}.html"
    if detail_path.exists():
        slug = f"{slug}-{today_str}"
        detail_path = ROOT / f"scholarship-{slug}.html"

    entry = {
        "slug": slug,
        "title": result["title"],
        "level": result["level"],
        "country": result["country"],
        "funding_type": result["funding_type"],
        "deadline": result["deadline"],
        "date_posted": today_str,
        "status": result["status"],
        "summary": result["summary"],
        "meta_description": result["meta_description"],
        "official_url": result["official_url"],
        "funder": result["funder"],
        "source": "auto",
        "sources_cited": result["sources"],
    }

    html = render_scholarship_detail_page(entry, result["body_html"])
    detail_path.write_text(html, encoding="utf-8")
    print(f"Wrote {detail_path.name}")

    # Append to scholarships.json
    data = json.loads(SCHOLARSHIPS_JSON.read_text(encoding="utf-8"))
    data["scholarships"].append(entry)
    SCHOLARSHIPS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print("Updated scholarships.json")

    # Emit info for the GitHub Action to use in the PR title/body.
    sources_line = "\n".join(f"- {u}" for u in result["sources"])
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"slug={slug}\n")
            f.write(f"title={result['title']}\n")
            f.write(f"deadline={result['deadline']}\n")


if __name__ == "__main__":
    main()
