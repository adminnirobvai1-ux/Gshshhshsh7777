"""
WinGo VIP Automation Platform - Configuration Module
সকল কনফিগারেশন, টোকেন, পেমেন্ট নম্বর এবং ওনার আইডি
"""
import os

# টেলিগ্রাম বট টোকেন
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4")

# মালিকের চ্যাট আইডি (Owner Chat ID)
OWNER_CHAT_ID = int(os.environ.get("OWNER_CHAT_ID", 8707571669))

# বাধ্যতামুলক জয়েনিং চ্যানেল লিঙ্ক (Lock System)
CHANNELS = [
    {
        "name": "DARK 67 HACK",
        "url": "https://t.me/DARK67HACK"
    },
    {
        "name": "BD WIN 24",
        "url": "https://t.me/bdwin24_bd"
    }
]

# বিকাশ ও নগদ মার্চেন্ট/পার্সোনাল পেমেন্ট নম্বর
PAYMENT_METHODS = {
    "bkash": {
        "name": "বিকাশ (Bkash)",
        "number": "01870829343",
        "type": "Send Money"
    },
    "nagad": {
        "name": "নগদ (Nagad)",
        "number": "01876685711",
        "type": "Send Money"
    }
}

# সাবস্ক্রিপশন প্রাইস লিস্ট
PRICING_PLANS = {
    "1d": {
        "btn_label": "1D - 500",
        "title": "1 Day VIP Access",
        "days": 1,
        "price": 500
    },
    "3d": {
        "btn_label": "3D - 1300",
        "title": "3 Days VIP Access",
        "days": 3,
        "price": 1300
    },
    "6d": {
        "btn_label": "6D - 2400",
        "title": "6 Days VIP Access",
        "days": 6,
        "price": 2400
    },
    "7d": {
        "btn_label": "7D - 2700",
        "title": "7 Days VIP Access",
        "days": 7,
        "price": 2700
    },
    "10d": {
        "btn_label": "10D - 3500",
        "title": "10 Days VIP Access",
        "days": 10,
        "price": 3500
    },
    "30d": {
        "btn_label": "30D - 9000",
        "title": "1 Month (30 Days) VIP Access",
        "days": 30,
        "price": 9000
    }
}

# প্ল্যাটফর্ম টার্গেট ইউআরএল
PLATFORMS = {
    "amarclub": {
        "name": "Amar Club",
        "login_url": "https://amarclub1.com/#/login",
        "wingo_url": "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "dkwin": {
        "name": "DK Win",
        "login_url": "https://dkwin6.com/#/login",
        "wingo_url": "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    }
}

# ডাটাবেস এবং ডিরেক্টরি পাথ
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_DIR = os.path.join(DATA_DIR, "browser_profiles")
SCREENSHOTS_DIR = os.path.join(DATA_DIR, "screenshots")
DB_FILE = os.path.join(DATA_DIR, "bot_database.json")

# ডিরেক্টরি তৈরি
os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
