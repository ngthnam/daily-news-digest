"""
RSS/Atom feed sources organized by category.
All sources are FREE — no API keys, no paywalls.
"""

SOURCES = {
    "tech": {
        "label": "Công nghệ & AI",
        "emoji": "💻",
        "feeds": [
            {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
            {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
            {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
            {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
            {"name": "Hacker News Top", "url": "https://hnrss.org/frontpage"},
            {"name": "VnExpress Công Nghệ", "url": "https://vnexpress.net/rss/khoa-hoc-cong-nghe.rss"},
            {"name": "ICTNews", "url": "https://ictnews.vietnamnet.vn/rss/cntt.rss"},
            {"name": "Gizmodo", "url": "https://gizmodo.com/rss"},
            {"name": "Engadget", "url": "https://www.engadget.com/rss.xml"},
            {"name": "VnReview", "url": "https://vnreview.vn/rss/"},
        ],
    },
    "finance": {
        "label": "Tài chính & Kinh tế",
        "emoji": "📈",
        "feeds": [
            {"name": "Reuters Business", "url": "https://feeds.reuters.com/reuters/businessNews"},
            {"name": "CafeF", "url": "https://cafef.vn/rss/home.rss"},
            {"name": "VnEconomy", "url": "https://vneconomy.vn/rss/home.rss"},
            {"name": "Vietnambiz", "url": "https://vietnambiz.vn/rss/home.rss"},
            {"name": "CoinDesk", "url": "https://www.coindesk.com/arc/outboundfeeds/rss/"},
            {"name": "Yahoo Finance", "url": "https://finance.yahoo.com/news/rssindex"},
            {"name": "MarketWatch", "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories"},
            {"name": "DanTri Kinh Doanh", "url": "https://dantri.com.vn/rss/kinh-doanh.rss"},
            {"name": "Thanh Nien Kinh Te", "url": "https://thanhnien.vn/rss/kinh-te.rss"},
            {"name": "Nguoi Dua Tin Tai Chinh", "url": "https://nguoiduatin.vn/rss/tai-chinh.rss"},
        ],
    },
    "realestate": {
        "label": "Bất động sản & Chính sách",
        "emoji": "🏠",
        "feeds": [
            {"name": "Batdongsan.vn", "url": "https://batdongsan.vn/tin-tuc/rss"},
            {"name": "CafeF BDS", "url": "https://cafef.vn/rss/bat-dong-san.rss"},
            {"name": "VnExpress BDS", "url": "https://vnexpress.net/rss/bat-dong-san.rss"},
            {"name": "Thanh Nien BDS", "url": "https://thanhnien.vn/rss/bat-dong-san.rss"},
            {"name": "VnEconomy BDS", "url": "https://vneconomy.vn/rss/bat-dong-san.rss"},
            {"name": "DanTri BDS", "url": "https://dantri.com.vn/rss/bat-dong-san.rss"},
            {"name": "Vietnambiz BDS", "url": "https://vietnambiz.vn/rss/bat-dong-san.rss"},
            {"name": "The Leader BDS", "url": "https://theleader.vn/rss/bat-dong-san.rss"},
        ],
    },
    "construction": {
        "label": "Xây dựng & Quy hoạch",
        "emoji": "🏗️",
        "feeds": [
            {"name": "Báo Xây Dựng", "url": "https://baoxaydung.com.vn/rss/home.rss"},
            {"name": "Tạp chí Kiến Trúc", "url": "https://www.tapchikientruc.com.vn/rss.xml"},
            {"name": "Viet Architecture", "url": "https://vietarchitecture.org/feed/"},
            {"name": "DanTri Xa Hoi", "url": "https://dantri.com.vn/rss/xa-hoi.rss"},
            {"name": "VnExpress Xa Hoi", "url": "https://vnexpress.net/rss/thoi-su.rss"},
            {"name": "CafeF Doanh nghiep", "url": "https://cafef.vn/rss/doanh-nghiep.rss"},
        ],
    },
    "health": {
        "label": "Y tế & Sức khỏe",
        "emoji": "🏥",
        "feeds": [
            {"name": "WHO News", "url": "https://www.who.int/rss-feeds/news-english.xml"},
            {"name": "Sức Khỏe & Đời Sống", "url": "https://suckhoedoisong.vn/rss/home.rss"},
            {"name": "VnExpress Sức Khỏe", "url": "https://vnexpress.net/rss/suc-khoe.rss"},
            {"name": "MedlinePlus Health News", "url": "https://medlineplus.gov/xml/mplus_health_news_en.xml"},
            {"name": "Reuters Health", "url": "https://feeds.reuters.com/reuters/healthNews"},
            {"name": "DanTri Suc Khoe", "url": "https://dantri.com.vn/rss/suc-khoe.rss"},
            {"name": "Thanh Nien Suc Khoe", "url": "https://thanhnien.vn/rss/suc-khoe.rss"},
            {"name": "Tuoi Tre Suc Khoe", "url": "https://tuoitre.vn/rss/suc-khoe.rss"},
        ],
    },
}

# Default categories matching ngthnam's choices
DEFAULT_CATEGORIES = ["tech", "finance", "realestate", "construction", "health"]
