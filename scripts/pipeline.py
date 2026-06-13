"""
pipeline.py — Main entry point. Runs the full pipeline:
  1. Scrape RSS feeds
  2. Summarize with Claude AI
  3. Generate static website

Usage:
  python scripts/pipeline.py
  python scripts/pipeline.py --scrape-only
  python scripts/pipeline.py --summarize-only
  python scripts/pipeline.py --generate-only
"""

import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Daily News Digest Pipeline")
    parser.add_argument("--scrape-only", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    run_all = not (args.scrape_only or args.summarize_only or args.generate_only)

    # Step 1: Scrape
    if run_all or args.scrape_only:
        log.info("=" * 50)
        log.info("STEP 1: SCRAPING")
        log.info("=" * 50)
        from scraper import run_scraper
        raw_data = run_scraper()
        raw_path = DATA_DIR / "latest_raw.json"
        raw_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2))
        log.info(f"Raw data saved → {raw_path}")
        if args.scrape_only:
            log.info("Done (scrape only)")
            return

    # Step 2: Summarize
    if run_all or args.summarize_only:
        log.info("\n" + "=" * 50)
        log.info("STEP 2: SUMMARIZING")
        log.info("=" * 50)
        raw_path = DATA_DIR / "latest_raw.json"
        if not raw_path.exists():
            log.error("No raw data found. Run --scrape-only first.")
            sys.exit(1)
        raw_data = json.loads(raw_path.read_text())
        from summarizer import run_summarizer
        digest = run_summarizer(raw_data)
        digest_path = DATA_DIR / "latest_digest.json"
        digest_path.write_text(json.dumps(digest, ensure_ascii=False, indent=2))
        log.info(f"Digest saved → {digest_path}")
        if args.summarize_only:
            log.info("Done (summarize only)")
            return

    # Step 3: Generate site
    if run_all or args.generate_only:
        log.info("\n" + "=" * 50)
        log.info("STEP 3: GENERATING SITE")
        log.info("=" * 50)
        digest_path = DATA_DIR / "latest_digest.json"
        if not digest_path.exists():
            log.error("No digest found. Run summarizer first.")
            sys.exit(1)
        digest = json.loads(digest_path.read_text())
        from generate_site import generate_site
        generate_site(digest)

    log.info("\n✅ Pipeline complete!")


if __name__ == "__main__":
    main()
