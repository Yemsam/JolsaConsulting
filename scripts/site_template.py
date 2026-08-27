"""
Shared HTML building blocks for Jolsa Consulting blog automation.

This module is the single source of truth for the header, footer, and
article page shape used by both:
  - build_blog_index.py   (regenerates blog.html + sitemap.xml)
  - generate_scholarship_post.py  (drafts new weekly posts)

Keeping this in one place means a future design tweak (e.g. a nav link
change) only needs to happen here, not in every generated file.
"""

DOMAIN = "https://jolsaconsulting.com"

HEADER = """    <header class="site-header">
  <a class="brand" href="index.html">
    <img src="img/logo.png" alt="Jolsa Consulting" />
  </a>
  <button
    class="menu-toggle"
    type="button"
    aria-label="Toggle menu"
    aria-expanded="false"
  >
    &#9776;
  </button>
  <nav class="nav-links" aria-label="Main navigation">
    <a href="services.html">Services</a>
    <a href="scholarships.html">Scholarships</a>
    <a href="digital-products.html">Products</a>
    <a href="study-abroad-assessment.html">Free Assessment</a>
    <a href="contact.html">Contact</a>
    <a href="booking.html" class="nav-cta">Book now</a>
  </nav>
</header>"""

NAV_SCHOLARSHIPS_LINK = '    <a href="scholarships.html">Scholarships</a>\n'

FOOTER = """    <footer class="site-footer">
  <div class="footer-main">
    <div>
        <a class="brand" href="index.html">
          <img src="img/logo.png" class="footer-logo" alt="Jolsa Consulting" />
        </a>
      <p>
        Career, scholarship, study abroad, and visa-readiness support for
        ambitious applicants.
      </p>
    </div>
    <div class="footer-links">
      <a href="study-abroad-assessment.html">Free Study-Abroad Assessment</a>
      <a href="contact.html">Contact</a>
      <a href="booking.html">Book consultation</a>
      <a href="privacy.html">Privacy policy</a>
    </div>
    <div class="footer-socials" aria-label="Social media links">
      <a class="footer-social-link" href="https://www.instagram.com/jolsaconsulting" aria-label="Instagram" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm0 2a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3H7zm5 3.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 0 1 12 7.5zm0 2A2.5 2.5 0 1 0 14.5 12 2.5 2.5 0 0 0 12 9.5zm5.75-3.1a1.05 1.05 0 1 1-1.05 1.05 1.05 1.05 0 0 1 1.05-1.05z"
          />
        </svg>
      </a>
      <a class="footer-social-link" href="https://www.facebook.com/JolsaConsulting" aria-label="Facebook" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M13.5 22v-8h2.7l.4-3h-3.1V9.1c0-.9.2-1.5 1.6-1.5h1.7V5c-.3 0-1.4-.1-2.6-.1-2.6 0-4.4 1.6-4.4 4.5V11H7v3h2.8v8h3.7z"
          />
        </svg>
      </a>
      <a class="footer-social-link" href="#" aria-label="LinkedIn" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M6.9 21H3.3V8.9h3.6V21zM5.1 7.3A2.1 2.1 0 1 1 5.1 3a2.1 2.1 0 0 1 0 4.3zM21 21h-3.6v-5.9c0-1.4 0-3.2-2-3.2s-2.3 1.5-2.3 3.1v6H9.5V8.9H13v1.7h.1c.5-.9 1.7-1.9 3.5-1.9 3.7 0 4.4 2.4 4.4 5.6V21z"
          />
        </svg>
      </a>
      <a class="footer-social-link" href="https://www.tiktok.com/@jolsa.consulting" aria-label="TikTok" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M16.6 3c.3 2.5 1.8 4.1 4.1 4.3v3.4a7.4 7.4 0 0 1-4-1.2v5.8c0 3.6-2.5 5.9-6 5.9a5.7 5.7 0 0 1-5.8-5.7c0-3.4 2.7-5.8 6.4-5.6v3.5c-1.7-.3-3 .6-3 2.1 0 1.3 1 2.2 2.3 2.2 1.5 0 2.4-.9 2.4-2.8V3h3.6z"
          />
        </svg>
      </a>
      <a class="footer-social-link" href="#" aria-label="YouTube" target="_blank" rel="noopener noreferrer">
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path
            d="M23 12c0 2.4-.3 4.1-.6 5.2-.2.8-.8 1.4-1.6 1.6-1.1.3-2.8.6-8.8.6s-7.7-.3-8.8-.6c-.8-.2-1.4-.8-1.6-1.6C1.3 16.1 1 14.4 1 12s.3-4.1.6-5.2c.2-.8.8-1.4 1.6-1.6C4.3 4.9 6 4.6 12 4.6s7.7.3 8.8.6c.8.2 1.4.8 1.6 1.6.3 1.1.6 2.8.6 5.2zM10 15.5l6-3.5-6-3.5v7z"
          />
        </svg>
      </a>
    </div>
  </div>
  <div class="footer-bottom">
    <span
      >&copy; <span data-current-year></span> Jolsa Consulting. All Rights
      Reserved.</span
    >
    <span>
      Designed by
      <a
        class="footer-designer"
        href="https://yemsam.github.io/WealthHubTech-new/"
        target="_blank"
        rel="noopener noreferrer"
        >Wealth Hub Tech</a
      >
    </span>
  </div>
</footer>"""

WHATSAPP_FLOAT = (
    '    <a class="whatsapp-float" href="https://wa.me/34604958276" '
    'aria-label="Chat with Jolsa Consulting on WhatsApp">WhatsApp</a>'
)


def organization_ld_json():
    return """{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Jolsa Consulting",
  "url": "https://jolsaconsulting.com/",
  "logo": "https://jolsaconsulting.com/img/logo.png",
  "description": "Career, scholarship, study abroad, and visa-readiness support for ambitious applicants.",
  "sameAs": [
    "https://www.instagram.com/jolsaconsulting",
    "https://www.facebook.com/JolsaConsulting",
    "https://www.tiktok.com/@jolsa.consulting"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "email": "info@jolsaconsulting.com",
    "contactType": "customer service"
  }
}"""


def render_post_page(post, body_html):
    """
    post: dict with keys slug, title, meta_description, category, read_time
    body_html: the <article> inner HTML (already built, including the
                leading <p class="post-meta">...</p>)
    Returns a full standalone HTML document string matching the site's
    existing blog post template exactly.
    """
    url = f"{DOMAIN}/{post['slug']}.html"
    og_image = f"{DOMAIN}/img/jolsa-consulting-banner.png"
    title_tag = f"{post['title']} | Jolsa Consulting"

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{post['meta_description']}" />
    <title>{title_tag}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet" />
    <link rel="icon" type="image/png" href="img/logo.png" />
    <link rel="stylesheet" href="css/styles.css" />
    <link rel="canonical" href="{url}" />
    <meta property="og:site_name" content="Jolsa Consulting" />
    <meta property="og:title" content="{title_tag}" />
    <meta property="og:description" content="{post['meta_description']}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{og_image}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title_tag}" />
    <meta name="twitter:description" content="{post['meta_description']}" />
    <meta name="twitter:image" content="{og_image}" />
    <script type="application/ld+json">
{organization_ld_json()}
    </script>
  </head>
  <body>
{HEADER}
    <main>
      <section class="page-hero">
        <p class="eyebrow">{post['category']}</p>
        <h1>{post['title']}</h1>
        <p>{post['meta_description']}</p>
      </section>
      <section class="section">
        <article class="article">
{body_html}
        </article>
      </section>
    </main>
{FOOTER}
{WHATSAPP_FLOAT}
    <script src="script.js" defer></script>
  </body>
</html>
"""


def render_blog_card(post):
    return f"""          <article class="mini-card post-card">
            <span class="post-meta">{post['category']}</span>
            <h2>{post['title']}</h2>
            <p>
              {post['excerpt']}
            </p>
            <a class="btn primary" href="{post['slug']}.html">Read post</a>
          </article>"""


# ---------------------------------------------------------------------------
# Scholarships hub (scholarships.html) + individual scholarship detail pages
# ---------------------------------------------------------------------------

SCHOLARSHIP_LEVELS = ["Undergraduate", "Masters", "PhD", "Fellowships"]


def _status_label(status):
    return {
        "open": ("Applications open", "tag-status-open"),
        "upcoming": ("Opens soon", "tag-status-closing"),
        "closing": ("Closing soon", "tag-status-closing"),
        "closed": ("Closed", "tag-status-closed"),
    }.get(status, ("Applications open", "tag-status-open"))


def render_scholarship_card(s):
    """
    s: dict with keys slug, title, level (list[str]), country, funding_type,
       deadline (YYYY-MM-DD), date_posted (YYYY-MM-DD), status, summary.
    Renders a fully static, pre-populated card. data-* attributes are what
    scholarships-filter.js reads to filter/sort client-side — the markup
    (and every word of text) is present in the raw HTML either way, so
    search engines see the full list regardless of JS.
    """
    status_text, status_class = _status_label(s.get("status", "open"))
    level_attr = " ".join(s["level"])
    return f"""          <article class="mini-card scholarship-card" data-level="{level_attr}" data-country="{s['country']}" data-deadline="{s['deadline']}" data-posted="{s['date_posted']}">
            <div class="tag-row">
              <span class="tag {status_class}">{status_text}</span>
              <span class="tag">{s['funding_type']}</span>
              <span class="tag">{'/'.join(s['level'])}</span>
              <span class="tag">{s['country']}</span>
            </div>
            <h2>{s['title']}</h2>
            <p>{s['summary']}</p>
            <p class="deadline-row">Deadline: <strong>{s['deadline']}</strong></p>
            <a class="btn primary" href="scholarship-{s['slug']}.html">View details &amp; how to apply</a>
          </article>"""


def scholarship_ld_json(s):
    url = f"{DOMAIN}/scholarship-{s['slug']}.html"
    return f"""{{
  "@context": "https://schema.org",
  "@type": "MonetaryGrant",
  "name": "{s['title']}",
  "description": "{s['meta_description']}",
  "url": "{url}",
  "funder": {{
    "@type": "Organization",
    "name": "{s.get('funder', s['title'])}"
  }},
  "amount": {{
    "@type": "MonetaryAmount",
    "currency": "USD",
    "description": "{s['funding_type']}"
  }},
  "datePosted": "{s['date_posted']}",
  "applicationDeadline": "{s['deadline']}"
}}"""


def render_scholarship_detail_page(s, body_html):
    """
    s: same dict shape as render_scholarship_card, plus meta_description
       and official_url.
    body_html: the article inner HTML (Overview, Benefits, Eligibility,
               Timeline, How to Apply, Tips, FAQs, source callout — already
               built by the caller).
    """
    url = f"{DOMAIN}/scholarship-{s['slug']}.html"
    og_image = f"{DOMAIN}/img/jolsa-consulting-banner.png"
    title_tag = f"{s['title']} | Jolsa Consulting"
    status_text, status_class = _status_label(s.get("status", "open"))

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="{s['meta_description']}" />
    <title>{title_tag}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet" />
    <link rel="icon" type="image/png" href="img/logo.png" />
    <link rel="stylesheet" href="css/styles.css" />
    <link rel="canonical" href="{url}" />
    <meta property="og:site_name" content="Jolsa Consulting" />
    <meta property="og:title" content="{title_tag}" />
    <meta property="og:description" content="{s['meta_description']}" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{og_image}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{title_tag}" />
    <meta name="twitter:description" content="{s['meta_description']}" />
    <meta name="twitter:image" content="{og_image}" />
    <script type="application/ld+json">
{scholarship_ld_json(s)}
    </script>
    <link rel="manifest" href="manifest.webmanifest" />
    <link rel="apple-touch-icon" href="img/icons/icon-192.png" />
    <meta name="theme-color" content="#071426" />
  </head>
  <body>
{HEADER}
    <main>
      <section class="page-hero">
        <p class="eyebrow">Scholarships</p>
        <h1>{s['title']}</h1>
        <p>{s['summary']}</p>
      </section>
      <section class="section">
        <div class="scholarship-meta-box">
          <div>
            <span class="label">Status</span>
            <span class="value"><span class="tag {status_class}">{status_text}</span></span>
          </div>
          <div>
            <span class="label">Level</span>
            <span class="value">{'/'.join(s['level'])}</span>
          </div>
          <div>
            <span class="label">Country / Host</span>
            <span class="value">{s['country']}</span>
          </div>
          <div>
            <span class="label">Funding</span>
            <span class="value">{s['funding_type']}</span>
          </div>
          <div>
            <span class="label">Application Deadline</span>
            <span class="value">{s['deadline']}</span>
          </div>
          <div>
            <span class="label">Date Posted</span>
            <span class="value">{s['date_posted']}</span>
          </div>
        </div>
        <article class="article">
{body_html}
        </article>
      </section>
      <section class="section cream">
        <div class="section-heading">
          <p class="eyebrow">Want expert help with this application?</p>
          <h2>Jolsa Consulting can help you build a stronger application</h2>
          <p>
            Our scholarship application support covers essays, personal
            statements, referee coordination, and full application review.
          </p>
        </div>
        <div class="button-row center">
          <a class="btn primary" href="scholarship.html">Get application support</a>
          <a class="btn secondary" href="scholarships.html">Browse more scholarships</a>
        </div>
      </section>
    </main>
{FOOTER}
{WHATSAPP_FLOAT}
    <script src="script.js" defer></script>
  </body>
</html>
"""
