"""
generate_site.py — Generates static HTML website from digest JSON.
No framework needed — pure HTML/CSS/JS output.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).parent.parent / "site"
DATA_DIR = Path(__file__).parent.parent / "data"


def format_date_vi(iso_str: str) -> str:
    """Format ISO date string to Vietnamese date."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        days_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
        day_name = days_vi[dt.weekday()]
        return f"{day_name}, {dt.day:02d}/{dt.month:02d}/{dt.year}"
    except Exception:
        return iso_str[:10] if iso_str else ""


def render_category_card(cat_data: dict) -> str:
    """Render one category section."""
    emoji = cat_data.get("emoji", "📰")
    label = cat_data.get("label", "")
    themes = cat_data.get("themes", [])
    highlight = cat_data.get("highlight", "")
    article_count = cat_data.get("article_count", 0)

    if not themes:
        return ""

    themes_html = ""
    for theme in themes:
        sources_html = ""
        for art in theme.get("source_articles", [])[:4]:
            sources_html += f'<a href="{art["url"]}" target="_blank" rel="noopener" class="source-link">{art["source"]}: {art["title"][:60]}{"…" if len(art["title"]) > 60 else ""}</a>'

        themes_html += f"""
        <div class="theme">
          <h3 class="theme-title">{theme["title"]}</h3>
          <p class="theme-summary">{theme["summary"]}</p>
          {f'<div class="theme-sources">{sources_html}</div>' if sources_html else ""}
        </div>"""

    highlight_html = f'<div class="highlight-box"><span class="highlight-label">⚡ Điểm nhấn</span><p>{highlight}</p></div>' if highlight else ""

    return f"""
  <section class="category-section" id="cat-{cat_data.get('key', '')}">
    <div class="category-header">
      <span class="category-emoji">{emoji}</span>
      <h2 class="category-title">{label}</h2>
      <span class="article-count">{article_count} bài</span>
    </div>
    {highlight_html}
    <div class="themes-grid">
      {themes_html}
    </div>
  </section>"""


def generate_html(digest: dict) -> str:
    """Generate complete HTML page from digest data."""
    date_str = format_date_vi(digest.get("summarized_at", digest.get("scraped_at", "")))
    total_articles = digest.get("total_articles", 0)
    categories = digest.get("categories", {})

    # Nav links
    nav_links = ""
    for cat_data in categories.values():
        if cat_data.get("themes"):
            nav_links += f'<a href="#cat-{cat_data["key"]}" class="nav-link">{cat_data["emoji"]} {cat_data["label"]}</a>'

    # Category sections
    sections_html = ""
    for cat_data in categories.values():
        sections_html += render_category_card(cat_data)

    # Archive links (last 7 days would be here)
    now_utc = datetime.now(timezone.utc)
    generated_at = now_utc.strftime("%H:%M UTC")

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Tóm tắt tin tức hàng ngày — {date_str}">
  <meta property="og:title" content="Daily News Digest — {date_str}">
  <meta property="og:description" content="{total_articles} bài viết được tóm tắt bởi AI">
  <title>Daily News Digest · {date_str}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Merriweather:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #fafaf9;
      --surface: #ffffff;
      --border: #e5e7eb;
      --text: #111827;
      --muted: #6b7280;
      --accent: #2563eb;
      --accent-light: #eff6ff;
      --green: #059669;
      --yellow: #d97706;
      --radius: 12px;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0f1117;
        --surface: #1a1d27;
        --border: #2e3347;
        --text: #e2e8f0;
        --muted: #94a3b8;
        --accent: #60a5fa;
        --accent-light: #1e293b;
      }}
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Inter', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}

    /* Header */
    header {{ background: var(--surface); border-bottom: 1px solid var(--border); padding: 0; position: sticky; top: 0; z-index: 100; backdrop-filter: blur(8px); }}
    .header-inner {{ max-width: 900px; margin: 0 auto; padding: 14px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }}
    .site-title {{ font-size: 18px; font-weight: 600; color: var(--text); text-decoration: none; display: flex; align-items: center; gap: 8px; }}
    .site-date {{ font-size: 13px; color: var(--muted); }}
    .header-meta {{ font-size: 12px; color: var(--muted); }}

    /* Nav */
    nav {{ background: var(--bg); border-bottom: 1px solid var(--border); overflow-x: auto; }}
    .nav-inner {{ max-width: 900px; margin: 0 auto; padding: 8px 20px; display: flex; gap: 4px; }}
    .nav-link {{ white-space: nowrap; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 500; color: var(--muted); text-decoration: none; transition: all 0.15s; border: 1px solid transparent; }}
    .nav-link:hover {{ color: var(--accent); background: var(--accent-light); border-color: var(--accent); }}

    /* Main */
    main {{ max-width: 900px; margin: 0 auto; padding: 32px 20px 64px; }}

    /* Stats bar */
    .stats-bar {{ display: flex; gap: 24px; padding: 16px 20px; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); margin-bottom: 32px; flex-wrap: wrap; }}
    .stat {{ text-align: center; }}
    .stat-n {{ font-size: 22px; font-weight: 600; color: var(--accent); }}
    .stat-l {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px; }}

    /* Category sections */
    .category-section {{ margin-bottom: 48px; scroll-margin-top: 100px; }}
    .category-header {{ display: flex; align-items: center; gap: 12px; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid var(--border); }}
    .category-emoji {{ font-size: 22px; }}
    .category-title {{ font-size: 20px; font-weight: 600; }}
    .article-count {{ margin-left: auto; font-size: 12px; color: var(--muted); background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 2px 10px; }}

    /* Highlight */
    .highlight-box {{ background: var(--accent-light); border-left: 3px solid var(--accent); border-radius: 0 8px 8px 0; padding: 12px 16px; margin-bottom: 20px; }}
    .highlight-label {{ font-size: 11px; font-weight: 600; color: var(--accent); text-transform: uppercase; letter-spacing: 0.06em; display: block; margin-bottom: 4px; }}
    .highlight-box p {{ font-size: 14px; color: var(--text); font-style: italic; }}

    /* Themes grid */
    .themes-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }}
    @media (max-width: 600px) {{ .themes-grid {{ grid-template-columns: 1fr; }} }}

    .theme {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px 20px; transition: border-color 0.15s; }}
    .theme:hover {{ border-color: var(--accent); }}
    .theme-title {{ font-size: 15px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; }}
    .theme-summary {{ font-size: 14px; color: var(--muted); line-height: 1.7; margin-bottom: 12px; }}
    .theme-sources {{ border-top: 1px solid var(--border); padding-top: 10px; display: flex; flex-direction: column; gap: 4px; }}
    .source-link {{ font-size: 12px; color: var(--accent); text-decoration: none; line-height: 1.4; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .source-link:hover {{ text-decoration: underline; }}

    /* Footer */
    footer {{ background: var(--surface); border-top: 1px solid var(--border); padding: 24px 20px; text-align: center; font-size: 12px; color: var(--muted); }}
    footer a {{ color: var(--accent); text-decoration: none; }}
    footer a:hover {{ text-decoration: underline; }}

    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
  </style>
</head>
<body>

<header>
  <div class="header-inner">
    <a href="/" class="site-title">📡 Daily News Digest</a>
    <div class="site-date">{date_str}</div>
    <div class="header-meta">Cập nhật lúc {generated_at}</div>
  </div>
</header>

<nav>
  <div class="nav-inner">
    {nav_links}
  </div>
</nav>

<main>
  <div class="stats-bar">
    <div class="stat"><div class="stat-n">{total_articles}</div><div class="stat-l">Bài viết</div></div>
    <div class="stat"><div class="stat-n">{len([c for c in categories.values() if c.get("themes")])}</div><div class="stat-l">Chuyên mục</div></div>
    <div class="stat"><div class="stat-n">{sum(len(c.get("themes", [])) for c in categories.values())}</div><div class="stat-l">Chủ đề</div></div>
    <div class="stat"><div class="stat-n">AI</div><div class="stat-l">Tóm tắt bởi</div></div>
  </div>

  {sections_html}
</main>

<footer>
  <p>Tổng hợp tự động · Tóm tắt bởi Claude AI · Cập nhật hàng ngày lúc 06:00 ICT</p>
  <p style="margin-top:6px;">
    <a href="https://github.com/ngthnam/daily-news-digest" target="_blank">GitHub</a> ·
    Dữ liệu từ nguồn công khai · Không lưu trữ nội dung gốc
  </p>
</footer>

</body>
</html>"""


def generate_site(digest: dict):
    """Build the full static site from digest data."""
    SITE_DIR.mkdir(exist_ok=True)

    # Write main index.html
    html = generate_html(digest)
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Generated site/index.html")

    # Copy latest digest JSON for optional API access
    shutil.copy2(DATA_DIR / "latest_digest.json", SITE_DIR / "digest.json")
    print(f"✓ Copied digest.json to site/")

    # Write a simple .nojekyll file for GitHub Pages
    (SITE_DIR / ".nojekyll").touch()

    print(f"✓ Site generation complete → {SITE_DIR}")


if __name__ == "__main__":
    digest_path = DATA_DIR / "latest_digest.json"
    if not digest_path.exists():
        print("No digest found. Run scraper.py then summarizer.py first.")
        exit(1)

    digest = json.loads(digest_path.read_text())
    generate_site(digest)
