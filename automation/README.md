# Weekly scholarship drafts

The Monday 08:00 UTC GitHub Action discovers opportunities **only through
Scholarship Region's RSS feed**. It reads up to 20 matching articles and prepares
up to five new review drafts. No AI service, API key, or package installation is
required. Node.js 22 runs the collector; Python 3.11 runs the existing page tools.

## Run and check

Run `node scripts/collect-scholarships.mjs --dry-run` to check live sources without
writing files, or omit `--dry-run` to create drafts. GitHub Actions also supports
**Weekly scholarship listing draft → Run workflow**. Source failures appear in
the Actions summary and downloadable report artifact, even when the job fails.
A run with source errors and no drafts fails visibly; no new opportunities is
a successful no-op and does not open an empty pull request.

The collector respects robots.txt, waits at least two seconds between requests
to each host, limits downloads and redirects, and never bypasses blocked pages.
Application/official links are candidates, not automatically trusted providers.
When a Scholarship Region application link points to its ScholarsRegion version,
the collector follows that intermediary to the provider; it is never used as an
official source or as an independent discovery feed.
PDFs, inaccessible pages, and uncertain details need manual research. Extracted
date mentions are not automatically classified as application deadlines.

## Review and publish

1. Open a new `automation/drafts/<id>.md` and its companion JSON in the PR.
2. Confirm official provider identity, current application cycle, eligibility,
   funding, and deadline. Check that applications are open or opening within
   60 days and that the opportunity is not already listed.
3. Complete `listing` using official information. Use levels supported by
   `scripts/site_template.py`, a future `YYYY-MM-DD` deadline, and `open` or
   `upcoming` status. Write original summary, meta description, and body HTML.
   Do not copy Scholarship Region's article or fill gaps by guessing.
4. Set `reviewed` to `true`, then run:

   ```sh
   python scripts/publish_scholarship_draft.py automation/drafts/<id>.json
   ```

5. Review and commit the generated detail page, scholarships.json, hub, and sitemap
   to the PR. Merge the reviewed changes to publish through the normal deploy.

JSON drafts remain as discovery history after merging, preventing repeat
collection. Merging raw drafts alone does not publish a listing. Compare newer
batches with still-unmerged batches before promotion; promotion also checks
source and slug duplicates.

## Setup and limits

Repository settings must allow Actions to create pull requests. The workflow
declares contents and pull-request write permissions. No Anthropic secret is
used. GitHub Actions usage remains subject to the account's allowances.

This is a bounded feed check, not an archive crawl. The feed may hold fewer than
a week's posts. Broader coverage can later use the same site's category feeds
or archives. Article layout changes may require parser maintenance. Unknown
provider layouts produce a source-linked research draft with fields left blank.

Tests: `node --test scripts/collect-scholarships.test.mjs`.
