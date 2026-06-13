# 📡 Daily News Digest

Tự động thu thập tin tức từ 40+ nguồn RSS miễn phí, tóm tắt bằng AI, và publish lên website tĩnh — mỗi ngày lúc 6:00 sáng (ICT).

**Website:** https://ngthnam.github.io/daily-news-digest

## Tính năng

- **100% miễn phí** — RSS feeds + Claude API (free tier) + GitHub Actions + GitHub Pages
- **5 chuyên mục:** Công nghệ, Tài chính, Bất động sản, Xây dựng, Y tế
- **40+ nguồn RSS** tiếng Việt và quốc tế
- **Tự động chạy** lúc 6:00 sáng mỗi ngày (cron job)
- **Static website** — nhanh, không cần server, không tốn tiền hosting
- **Dark mode** tự động theo hệ thống

## Cách triển khai (5 phút)

### 1. Fork repo này

Nhấn **Fork** ở góc trên phải trang GitHub này.

### 2. Lấy Anthropic API Key

1. Vào [console.anthropic.com](https://console.anthropic.com)
2. Đăng ký tài khoản (miễn phí)
3. Vào **API Keys** → **Create Key**
4. Copy key (bắt đầu bằng `sk-ant-...`)

### 3. Thêm API key vào GitHub Secrets

1. Vào repo của bạn → **Settings** → **Secrets and variables** → **Actions**
2. Nhấn **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: dán API key vừa copy
5. Nhấn **Add secret**

### 4. Bật GitHub Pages

1. Vào **Settings** → **Pages**
2. Source: chọn **Deploy from a branch**
3. Branch: `gh-pages` → `/root`
4. Nhấn **Save**

### 5. Chạy lần đầu

1. Vào **Actions** tab
2. Chọn workflow **Daily News Digest**
3. Nhấn **Run workflow** → **Run workflow**
4. Đợi ~5 phút, website sẽ live tại `https://ngthnam.github.io/daily-news-digest`

---

## Chạy local (để test)

```bash
# Clone repo
git clone https://github.com/ngthnam/daily-news-digest
cd daily-news-digest

# Cài dependencies
pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Chạy toàn bộ pipeline
cd scripts
python pipeline.py

# Hoặc chạy từng bước
python pipeline.py --scrape-only     # chỉ scrape
python pipeline.py --summarize-only  # chỉ summarize
python pipeline.py --generate-only   # chỉ generate site
```

Sau khi chạy, mở `site/index.html` trong trình duyệt để xem kết quả.

---

## Cấu hình

Tất cả cấu hình qua environment variables:

| Variable | Mặc định | Mô tả |
|---|---|---|
| `ANTHROPIC_API_KEY` | (bắt buộc) | Claude API key |
| `CATEGORIES` | `tech,finance,realestate,construction,health` | Danh mục chạy |
| `SUMMARY_LANGUAGE` | `vi` | Ngôn ngữ: `vi` / `en` / `bilingual` |
| `LOOKBACK_HOURS` | `25` | Lấy bài trong vòng N giờ qua |
| `MAX_PER_FEED` | `10` | Tối đa bài/feed |
| `MAX_WORKERS` | `8` | Số worker song song |

### Thêm/bớt nguồn tin

Sửa file `scripts/sources.py` — thêm vào dict `SOURCES` theo format:

```python
{"name": "Tên nguồn", "url": "https://example.com/rss.xml"},
```

---

## Cấu trúc project

```
daily-news-digest/
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # GitHub Actions cron job
├── scripts/
│   ├── pipeline.py            # Entry point chính
│   ├── scraper.py             # Thu thập RSS feeds
│   ├── summarizer.py          # Tóm tắt bằng Claude AI
│   ├── generate_site.py       # Tạo HTML tĩnh
│   └── sources.py             # Danh sách 40+ nguồn RSS
├── data/                      # JSON output (auto-generated)
│   ├── latest_raw.json
│   └── latest_digest.json
├── site/                      # Static website (auto-generated)
│   └── index.html
├── requirements.txt
└── README.md
```

---

## Chi phí

| Thành phần | Chi phí |
|---|---|
| GitHub Actions | Miễn phí (2,000 phút/tháng) |
| GitHub Pages | Miễn phí |
| RSS feeds | Miễn phí |
| Claude Haiku API | ~$0.80–1.00/ngày ≈ $25/tháng |

> **Tip tiết kiệm:** Claude API có free tier $5 credit khi đăng ký mới. Đủ để chạy thử ~5 ngày miễn phí.

---

## License

MIT — fork thoải mái.
