#!/usr/bin/env python3
"""Promote a reviewed discovery draft; never called by the discovery job."""
import html
import json
import re
import subprocess
import sys
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from site_template import SCHOLARSHIP_LEVELS, render_scholarship_detail_page

ROOT = Path(__file__).resolve().parent.parent


class BodyValidator(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag not in {"p", "h2", "ul", "ol", "li", "strong", "a", "div"}:
            raise ValueError(f"Unsupported body tag: {tag}")
        for key, value in attrs:
            if key not in {"href", "target", "rel", "class"} or (key == "href" and urlparse(value or "").scheme != "https"):
                raise ValueError(f"Unsupported or unsafe HTML attribute: {key}")


def validate(draft, today):
    if draft.get("reviewed") is not True:
        raise ValueError("Review the official source and set reviewed to true first")
    entry = draft["listing"].copy()
    for key in ("title", "country", "funding_type", "deadline", "status", "summary", "meta_description", "funder", "official_url", "body_html"):
        if not isinstance(entry.get(key), str) or not entry[key].strip():
            raise ValueError(f"Complete listing.{key} from the official source")
    if not isinstance(entry.get("level"), list) or not entry["level"] or any(level not in SCHOLARSHIP_LEVELS for level in entry["level"]):
        raise ValueError("Choose valid scholarship levels")
    if entry["status"] not in {"open", "upcoming"} or date.fromisoformat(entry["deadline"]) <= today:
        raise ValueError("Require open/upcoming status and a future confirmed deadline")
    official = urlparse(entry["official_url"])
    if official.scheme != "https" or not official.hostname or official.username or official.password:
        raise ValueError("Require an official HTTPS URL")
    if any(official.hostname == domain or official.hostname.endswith("." + domain) for domain in ("scholarshipregion.com", "scholarsregion.com")):
        raise ValueError("Use the provider's official source, not the discovery article")
    BodyValidator().feed(entry["body_html"])
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", draft["id"]):
        raise ValueError("Invalid draft id")
    return entry


def main():
    draft_path = Path(sys.argv[1]).resolve()
    if not draft_path.is_relative_to(ROOT / "automation" / "drafts"):
        raise ValueError("Choose a JSON draft under automation/drafts")
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    entry = validate(draft, date.today())
    body = entry.pop("body_html")
    slug = draft["id"]
    listing_path = ROOT / f"scholarship-{slug}.html"
    data_path = ROOT / "scholarships.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    if listing_path.exists() or any(s["slug"] == slug or s.get("official_url") == entry["official_url"] or s.get("discovery_url") == draft["discovery_url"] for s in data["scholarships"]):
        raise ValueError("This source or listing already exists; update it manually instead")
    entry.update(slug=slug, date_posted=date.today().isoformat(), source="scholarshipregion-discovery",
                 discovery_url=draft["discovery_url"], sources_cited=[entry["official_url"]], checked_at=draft["checked_at"])
    safe = {key: html.escape(value, quote=True) if isinstance(value, str) else [html.escape(v, quote=True) for v in value] if isinstance(value, list) else value for key, value in entry.items()}
    page = render_scholarship_detail_page(safe, body)
    schema = {"@context": "https://schema.org", "@type": "MonetaryGrant", "name": entry["title"],
              "description": entry["meta_description"], "url": f"https://jolsaconsulting.com/scholarship-{slug}.html",
              "funder": {"@type": "Organization", "name": entry["funder"]}, "datePosted": entry["date_posted"], "applicationDeadline": entry["deadline"]}
    schema_text = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
    page = re.sub(r'(<script type="application/ld\+json">)[\s\S]*?(</script>)', lambda m: m[1] + "\n" + schema_text + "\n" + m[2], page, count=1)
    data["scholarships"].append(entry)
    listing_path.write_text(page, encoding="utf-8")
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_scholarships_index.py")], check=True)
    print(f"Prepared {listing_path.name}; review and merge the page, hub, JSON, and sitemap changes.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, IndexError) as error:
        raise SystemExit(f"ERROR: {error}")
