"""
summarizer.py — Summarizes scraped articles using Claude API.
Requires ANTHROPIC_API_KEY environment variable.
"""

import os
import json
import logging
import time
from pathlib import Path
from datetime import datetime, timezone

import anthropic

log = logging.getLogger(__name__)

# Config
MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
LANGUAGE = os.getenv("SUMMARY_LANGUAGE", "vi")  # vi | en | bilingual
MAX_ARTICLES_PER_SUMMARY = int(os.getenv("MAX_ARTICLES_PER_SUMMARY", "30"))

LANGUAGE_INSTRUCTIONS = {
    "vi": "Viết tóm tắt hoàn toàn bằng tiếng Việt, ngôn ngữ tự nhiên, dễ đọc.",
    "en": "Write the summary entirely in English, clear and concise.",
    "bilingual": "Write in both Vietnamese and English. Vietnamese first, then English translation.",
}


def build_prompt(category_label: str, articles: list[dict]) -> str:
    """Build the summarization prompt for a category."""
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(LANGUAGE, LANGUAGE_INSTRUCTIONS["vi"])

    articles_text = ""
    for i, a in enumerate(articles[:MAX_ARTICLES_PER_SUMMARY], 1):
        articles_text += f"\n[{i}] {a['title']}\nNguồn: {a['source']}\n"
        if a.get("summary"):
            articles_text += f"Mô tả: {a['summary'][:300]}\n"
        articles_text += "\n"

    return f"""Bạn là một biên tập viên tin tức chuyên nghiệp. Tôi sẽ cung cấp {len(articles[:MAX_ARTICLES_PER_SUMMARY])} bài viết từ chuyên mục "{category_label}".

{lang_instruction}

Nhiệm vụ:
1. Xác định 3–5 CHỦ ĐỀ/XU HƯỚNG chính nổi bật nhất từ các bài viết
2. Với mỗi chủ đề, viết 2–3 câu tóm tắt súc tích, bao gồm thông tin quan trọng nhất
3. Kết thúc bằng 1 câu "Điểm nhấn hôm nay" — câu quan trọng nhất của ngày

Định dạng JSON output (chỉ trả về JSON, không có text khác):
{{
  "themes": [
    {{
      "title": "Tên chủ đề ngắn gọn",
      "summary": "2-3 câu tóm tắt",
      "articles": [số thứ tự bài viết liên quan, VD: [1, 3, 7]]
    }}
  ],
  "highlight": "Câu điểm nhấn quan trọng nhất hôm nay",
  "total_sources": {len(articles)}
}}

Các bài viết:
{articles_text}"""


def summarize_category(client: anthropic.Anthropic, category_data: dict) -> dict:
    """Summarize one category using Claude."""
    cat_key = category_data["key"]
    cat_label = category_data["label"]
    articles = category_data["articles"]

    if not articles:
        log.warning(f"  No articles for {cat_label}, skipping")
        return {**category_data, "summary": None, "themes": [], "highlight": ""}

    log.info(f"  Summarizing {cat_label} ({len(articles)} articles)...")

    prompt = build_prompt(cat_label, articles)

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()

        # Parse JSON — handle markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        summary_data = json.loads(raw)

        # Attach source article details to each theme
        themes = summary_data.get("themes", [])
        for theme in themes:
            ref_indices = theme.get("articles", [])
            theme["source_articles"] = [
                {"title": articles[i - 1]["title"], "url": articles[i - 1]["url"], "source": articles[i - 1]["source"]}
                for i in ref_indices
                if 1 <= i <= len(articles)
            ]

        log.info(f"  ✓ {cat_label}: {len(themes)} themes")
        return {
            **category_data,
            "themes": themes,
            "highlight": summary_data.get("highlight", ""),
            "total_sources_referenced": summary_data.get("total_sources", len(articles)),
        }

    except json.JSONDecodeError as e:
        log.error(f"  ✗ JSON parse error for {cat_label}: {e}")
        log.error(f"  Raw response: {raw[:200]}")
        return {**category_data, "themes": [], "highlight": ""}
    except Exception as e:
        log.error(f"  ✗ Error summarizing {cat_label}: {e}")
        return {**category_data, "themes": [], "highlight": ""}


def run_summarizer(raw_data: dict) -> dict:
    """Summarize all categories. Returns enriched digest data."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)

    log.info(f"\nStarting summarization — model: {MODEL}, language: {LANGUAGE}")

    summarized_categories = {}
    for cat_key, cat_data in raw_data["categories"].items():
        result = summarize_category(client, cat_data)
        summarized_categories[cat_key] = result
        # Rate limiting — be gentle with the API
        time.sleep(0.5)

    return {
        **raw_data,
        "summarized_at": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "language": LANGUAGE,
        "categories": summarized_categories,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

    data_dir = Path(__file__).parent.parent / "data"
    raw_path = data_dir / "latest_raw.json"

    if not raw_path.exists():
        print("No raw data found. Run scraper.py first.")
        exit(1)

    raw_data = json.loads(raw_path.read_text())
    digest = run_summarizer(raw_data)

    out_path = data_dir / "latest_digest.json"
    out_path.write_text(json.dumps(digest, ensure_ascii=False, indent=2))
    log.info(f"Digest saved → {out_path}")
