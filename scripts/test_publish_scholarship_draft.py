import copy
import json
import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import publish_scholarship_draft as publisher


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.draft = {"id": "example-award-2099", "reviewed": True,
                      "discovery_url": "https://www.scholarshipregion.com/example/", "checked_at": "2026-10-21",
                      "listing": {"title": 'Example "Award" & Funding', "level": ["Masters"], "country": "Germany",
                                  "funding_type": "Partial Funding", "deadline": "2099-01-31", "status": "open",
                                  "summary": "Study & research support.", "meta_description": 'An "award" for study.',
                                  "funder": "Example University", "official_url": "https://example.edu/award",
                                  "body_html": '<h2>How to apply</h2><p>Visit the <a href="https://example.edu/award">provider</a>.</p>'}}

    def test_review_is_required(self):
        self.draft["reviewed"] = False
        with self.assertRaisesRegex(ValueError, "reviewed"):
            publisher.validate(self.draft, date(2026, 10, 21))

    def test_unconfirmed_fields_expired_dates_and_discovery_sources_rejected(self):
        for key, value in [("deadline", "2020-01-01"), ("country", None), ("official_url", "https://www.scholarshipregion.com/post/")]:
            draft = copy.deepcopy(self.draft)
            draft["listing"][key] = value
            with self.assertRaises(ValueError):
                publisher.validate(draft, date(2026, 10, 21))

    def test_unsafe_body_rejected(self):
        for body in ['<script>alert(1)</script>', '<a href="javascript:alert(1)">Apply</a>', '<p onclick="alert(1)">Text</p>']:
            draft = copy.deepcopy(self.draft)
            draft["listing"]["body_html"] = body
            with self.assertRaises(ValueError):
                publisher.validate(draft, date(2026, 10, 21))

    def test_reviewed_promotion_renders_page_and_rebuilds_hub_then_rejects_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            for name in ("build_scholarships_index.py", "site_template.py"):
                shutil.copy(Path(__file__).parent / name, root / "scripts" / name)
            (root / "scholarships.json").write_text('{"scholarships":[]}', encoding="utf-8")
            (root / "scholarships.html").write_text('<!-- SCHOLARSHIPS:START -->\n\n<!-- SCHOLARSHIPS:END -->', encoding="utf-8")
            (root / "sitemap.xml").write_text('<!-- SCHOLARSHIP-PAGES:START -->\n\n<!-- SCHOLARSHIP-PAGES:END -->', encoding="utf-8")
            draft_path = root / "automation" / "drafts" / "example.json"
            draft_path.parent.mkdir(parents=True)
            draft_path.write_text(json.dumps(self.draft), encoding="utf-8")
            with patch.object(publisher, "ROOT", root), patch.object(sys, "argv", ["publish", str(draft_path)]):
                publisher.main()
                with self.assertRaisesRegex(ValueError, "already exists"):
                    publisher.main()
            page = (root / "scholarship-example-award-2099.html").read_text(encoding="utf-8")
            self.assertIn('Example &quot;Award&quot; &amp; Funding', page)
            self.assertIn('Example &quot;Award&quot; &amp; Funding', (root / "scholarships.html").read_text(encoding="utf-8"))
            import re
            schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)[1])
            self.assertEqual(schema["name"], self.draft["listing"]["title"])
            self.assertIn('scholarship-example-award-2099.html', (root / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
