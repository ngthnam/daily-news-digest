"""
scraper.py — Fetches articles from RSS feeds.
Uses feedparser (free, no API keys needed).
"""

import os
import json
import logging
import time
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import feedparser
import requests
from bs4 import BeautifulSoup

from sources import SOURCES, DEFAULT_CATEGORIES

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# How many hours back to look
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "25"))
# Max articles per feed
MAX_PER_FEED = int(os.getenv("MAX_PER_FEED", "10"))
# Max workers for parallel fetching
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "8"))
# Request timeout seconds
TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; NewsDigestBot/1.0; "
        "+https://github.com/ngthnam/daily-news-digest)"
    )
}


def fetch_feed(feed_info: dict, cutoff: datetime) -> list[dict]:
    """Fetch and parse a single RSS/Atom feed."""
    name = feed_info["name"]
    url = feed_info["url"]
    articles = []

    try:
        # feedparser handles RSS, Atom, and RDF
        d = feedparser.parse(url, request_headers=HEADERS, agent=HEADERS["User-Agent"])

        if d.bozo and not d.entries:
            log.warning(f"  ⚠ {name}: feed parse error — {d.bozo_exception}")
            return []

        for entry in d.entries[:MAX_PER_FEED]:
            # Parse publish date
            pub = None
            for date_field in ("published_parsed", "updated_parsed", "created_parsed"):
                if hasattr(entry, date_field) and getattr(entry, date_field):
                    try:
                        t = getattr(entry, date_field)
                        pub = datetime(*t[:6], tzinfo=timezone.utc)
                        break
                    except Exception:
                        pass

            # Skip if older than cutoff (allow None — include if date unknown)
            if pub and pub < cutoff:
                continue

            # Extract content
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            summary = ""

            # Try summary/content fields
            if hasattr(entry, "content") and entry.content:
                raw = entry.content[0].get("value", "")
                summary = BeautifulSoup(raw, "html.parser").get_text(" ", strip=True)[:800]
            elif hasattr(entry, "summary"):
                summary = BeautifulSoup(entry.summary, "html.parser").get_text(" ", strip=True)[:800]
            elif hasattr(entry, "description"):
                summary = BeautifulSoup(entry.description, "html.parser").get_text(" ", strip=True)[:800]

            if not title or not link:
                continue

            article_id = hashlib.md5(link.encode()).hexdigest()[:12]

            articles.append({
                "id": article_id,
                "title": title,
                "url": link,
                "source": name,
                "summary": summary,
                "published_at": pub.isoformat() if pub else None,
            })

        log.info(f"  ✓ {name}: {len(articles)} articles")

    except Exception as e:
        log.error(f"  ✗ {name}: {e}")

    return articles


def scrape_category(cat_key: str, cat_info: dict, cutoff: datetime) -> dict:
    """Scrape all feeds in a category in parallel."""
    feeds = cat_info["feeds"]
    all_articles = []

    log.info(f"\n{cat_info['emoji']} Scraping {cat_info['label']} ({len(feeds)} feeds)...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_feed, feed, cutoff): feed for feed in feeds}
        for future in as_completed(futures):
            articles = future.result()
            all_articles.extend(articles)

    # Deduplicate by URL
    seen = set()
    unique = []
    for a in all_articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    # Sort by published_at descending (None last)
    unique.sort(key=lambda x: x["published_at"] or "", reverse=True)

    log.info(f"  → {len(unique)} unique articles in {cat_info['label']}")
    return {
        "key": cat_key,
        "label": cat_info["label"],
        "emoji": cat_info["emoji"],
        "articles": unique,
        "article_count": len(unique),
    }


def run_scraper() -> dict:
    """Main scraper entry point. Returns all scraped data."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=LOOKBACK_HOURS)

    # Determine which categories to run
    env_cats = os.getenv("CATEGORIES", "")
    if env_cats:
        categories = [c.strip() for c in env_cats.split(",") if c.strip() in SOURCES]
    else:
        categories = DEFAULT_CATEGORIES

    log.info(f"Starting scraper — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    log.info(f"Categories: {categories}")
    log.info(f"Lookback: {LOOKBACK_HOURS}h | Cutoff: {cutoff.strftime('%Y-%m-%d %H:%M UTC')}")

    results = {}
    total_articles = 0

    for cat_key in categories:
        if cat_key not in SOURCES:
            log.warning(f"Unknown category: {cat_key}")
            continue
        cat_info = SOURCES[cat_key]
        cat_data = scrape_category(cat_key, cat_info, cutoff)
        results[cat_key] = cat_data
        total_articles += cat_data["article_count"]

    log.info(f"\n✅ Scraping complete: {total_articles} total articles across {len(results)} categories")

    return {
        "scraped_at": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "total_articles": total_articles,
        "categories": results,
    }


if __name__ == "__main__":
    data = run_scraper()

    # Save raw data
    out_dir = Path(__file__).parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "latest_raw.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    log.info(f"Raw data saved → {out_path}")
