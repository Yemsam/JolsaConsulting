#!/usr/bin/env python3
"""
Weekly automated scholarship listing generator for Jolsa Consulting.

What this does:
  1. Asks Claude (with its web search tool switched on) to find UP TO 5
     scholarships that are CURRENTLY OPEN (or opening soon) for applications,
     each with a real, verifiable deadline and an official application link.
     Quality still comes before hitting the number 5 — Claude is told to
     return fewer rather than pad with weak/unverifiable entries.
  2. Has Claude draft a clear, scholarshipregion.com-style detail page for
     each one: overview, benefits, eligibility, timeline, how to apply,
     tips, and FAQs — so a reader fully understands what the opportunity
     is and how to act on it.
  3. Writes a new scholarship-<slug>.html detail page per scholarship
     (same template as every other scholarship on the site) and appends
     structured entries to scholarships.json, which drives the filterable
     Scholarships hub (scholarships.html) — this is a dedicated,
     SEO-optimized directory page, not a blog post.

What this deliberately does NOT do: publish anything. It's meant to run
inside a GitHub Action that commits the new files to a branch and opens a
pull request — a human still reviews each deadline/eligibility/link
against its official source before it goes live. Scholarship details are
exactly the kind of fact that's costly to get wrong (a reader could miss
a real deadline because of an error in an unreviewed auto-post), so this
script always leaves a clear "verify before merging" trail: every
generated page carries a visible notice linking to the official source,
and the PR description (built in the GitHub Action) lists every entry in
the batch so nothing gets missed in review.

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
BATCH_SIZE = int(os.environ.get("SCHOLARSHIP_POST_BATCH_SIZE", "5"))

SYSTEM_PROMPT = f"""You are a careful research assistant for Jolsa Consulting, a \
career/scholarship/study-abroad/visa-readiness consultancy serving Nigerian and \
other global applicants. You are adding new entries to their Scholarships \
directory page — a dedicated, filterable listing of real scholarship \
opportunities (not a blog post).

Hard rules:
- Cover UP TO {BATCH_SIZE} DIFFERENT scholarships in this run — but quality \
comes first. Return fewer than {BATCH_SIZE} (even just one, or in principle \
zero) rather than padding the batch with weak, uncertain, or hard-to-verify \
entries just to hit the number.
- Each scholarship must be currently open for applications OR opening within \
the next 60 days, with a deadline in the future relative to today's date.
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
for a new cycle) — in that case treat it as a new entry with a distinct slug. \
Also do not repeat a scholarship twice within this same batch.
- Prefer scholarships relevant to Nigerian/African applicants where possible, but \
broaden if nothing strong is open for that group right now. Prefer variety across \
the batch (mix of levels/countries) over several very similar entries.
- Write each body_html so a reader fully understands the opportunity without \
leaving the page: what it is, what it covers, who is eligible, the timeline, how \
to apply step by step, application tips, and 1-2 FAQs. This should read like a \
clear, complete explainer (similar in thoroughness to sites like \
scholarshipregion.com), not a short teaser.
- Tone: match Jolsa Consulting's existing voice — direct, practical, no hype, no \
promises of admission/funding outcomes. Short paragraphs, scannable structure.

Output format: respond with ONLY a single JSON object (no markdown fences, no \
commentary before or after), with exactly this shape:
{{
  "scholarships": [
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
    # ... up to {BATCH_SIZE} objects total, this exact shape each time
  ]
}}

body_html structure (per scholarship): valid HTML fragment using only these \
tags: <p>, <h2>, <ul>, <ol>, <li>, <strong>, <a>, and a closing \
<div class="source-callout"> block. Structure: <h2>What is [name]?</h2> \
overview paragraph(s); <h2>What does it cover?</h2> with a <ul>; <h2>Who is \
eligible?</h2> with a <ul>; <h2>Application timeline</h2> with a <ul> of dated \
milestones (or a single deadline paragraph if that's all that's confirmed); \
<h2>How to apply</h2> as an <ol> of steps; <h2>Application tips</h2> with a \
<ul>; <h2>FAQs</h2> with a couple of <p><strong>question</strong> answer</p> \
pairs; and finally a <div class="source-callout">Always verify current dates \
and eligibility directly on the official [Name] website: <a href="OFFICIAL_URL" \
target="_blank" rel="noopener noreferrer">official link text</a>.</div>. Do not \
use <h1> (the page template supplies its own)."""


def load_recent_titles(limit=25):
    data = json.loads(SCHOLARSHIPS_JSON.read_text(encoding="utf-8"))
    items = sorted(data["scholarships"], key=lambda s: s["date_posted"], reverse=True)
    return [s["title"] for s in items[:limit]]


def call_claude(today_str, recent_titles):
    import anthropic

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    user_prompt = (
        f"Today's date is {today_str}. Scholarships already on the site "
        f"(avoid duplicating these): {json.dumps(recent_titles)}\n\n"
        f"Search for up to {BATCH_SIZE} scholarships that are currently open "
        "(or opening within 60 days) for applications and draft the batch as "
        "specified in your instructions."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 20}],
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


REQUIRED_KEYS = {
    "title", "slug", "level", "country", "funding_type", "deadline",
    "status", "summary", "meta_description", "funder", "official_url",
    "sources", "body_html",
}


def validate_entry(raw, index, existing_slugs, used_titles):
    """Returns (ok, reason_or_none). Mutates existing_slugs/used_titles when ok."""
    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        return False, f"missing keys: {missing}"

    if not raw["sources"] or not raw["official_url"]:
        return False, "no source URL cited"

    bad_levels = [lvl for lvl in raw["level"] if lvl not in SCHOLARSHIP_LEVELS]
    if bad_levels or not raw["level"]:
        return False, f"invalid level(s): {raw.get('level')}"

    if raw["status"] not in ("open", "upcoming"):
        return False, f"invalid status: {raw.get('status')!r}"

    title_key = raw["title"].strip().lower()
    if title_key in used_titles:
        return False, "duplicate title within this batch"
    used_titles.add(title_key)

    return True, None


def main():
    today = date.today() if hasattr(date, "today") else None
    # NOTE: in CI this runs with a real system clock, so date.today() is fine
    # there. (Avoided only inside Claude-orchestrated workflow scripts.)
    today_str = today.isoformat() if today else datetime.now(timezone.utc).date().isoformat()

    recent_titles = load_recent_titles()
    raw = call_claude(today_str, recent_titles)
    result = extract_json(raw)

    candidates = result.get("scholarships")
    if not isinstance(candidates, list) or not candidates:
        raise SystemExit("ERROR: model output has no non-empty 'scholarships' list")

    existing_slugs = {
        p.stem[len("scholarship-"):]
        for p in ROOT.glob("scholarship-*.html")
    }
    used_titles = set()

    written = []  # list of (entry_dict, ) for successfully processed scholarships
    skipped = []  # list of (index, reason)

    for i, raw_entry in enumerate(candidates[:BATCH_SIZE]):
        ok, reason = validate_entry(raw_entry, i, existing_slugs, used_titles)
        if not ok:
            skipped.append((i, reason))
            print(f"SKIPPING entry {i}: {reason}")
            continue

        slug = raw_entry["slug"] or slugify_fallback(raw_entry["title"])
        slug = re.sub(r"^(blog-|scholarship-)+", "", slug)
        if slug in existing_slugs:
            slug = f"{slug}-{today_str}"
        existing_slugs.add(slug)
        detail_path = ROOT / f"scholarship-{slug}.html"

        entry = {
            "slug": slug,
            "title": raw_entry["title"],
            "level": raw_entry["level"],
            "country": raw_entry["country"],
            "funding_type": raw_entry["funding_type"],
            "deadline": raw_entry["deadline"],
            "date_posted": today_str,
            "status": raw_entry["status"],
            "summary": raw_entry["summary"],
            "meta_description": raw_entry["meta_description"],
            "official_url": raw_entry["official_url"],
            "funder": raw_entry["funder"],
            "source": "auto",
            "sources_cited": raw_entry["sources"],
        }

        html = render_scholarship_detail_page(entry, raw_entry["body_html"])
        detail_path.write_text(html, encoding="utf-8")
        print(f"Wrote {detail_path.name}")
        written.append(entry)

    if not written:
        raise SystemExit(
            "ERROR: no scholarship in this batch passed validation — nothing to publish. "
            f"Skipped: {skipped}"
        )

    # Append all successful entries to scholarships.json in one write.
    data = json.loads(SCHOLARSHIPS_JSON.read_text(encoding="utf-8"))
    data["scholarships"].extend(written)
    SCHOLARSHIPS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Updated scholarships.json with {len(written)} new entrie(s)")

    if skipped:
        print(f"NOTE: {len(skipped)} candidate(s) were skipped and not published: {skipped}")

    # Emit info for the GitHub Action to use in the PR title/body.
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        summary_lines = [
            f"- **{e['title']}** — deadline {e['deadline']} — source: {e['official_url']}"
            for e in written
        ]
        summary = "\n".join(summary_lines)
        with open(gh_output, "a", encoding="utf-8") as f:
            f.write(f"count={len(written)}\n")
            f.write(f"title={written[0]['title']}\n")
            f.write("summary<<GH_OUTPUT_EOF\n")
            f.write(summary + "\n")
            f.write("GH_OUTPUT_EOF\n")


if __name__ == "__main__":
    main()
