"""
WinGo VIP Master Automation Runner (main.py)
মেইন ফাইল - এটি একবার রান করলেই সব ডিপেন্ডেন্সি চেক হবে এবং পুরো বট সচল হবে
"""
import sys
import os
import time

# ১. স্বয়ংক্রিয় প্যাকেজ ইন্সটলার কল করা
try:
    from installer import auto_install_packages
    auto_install_packages()
except Exception as e:
    print(f"[*] Package installer notice: {e}")

# ২. মূল মডিউলগুলো ইমপোর্ট
from config import BOT_TOKEN, OWNER_CHAT_ID, CHANNELS, PRICING_PLANS
from database import db
from bot_handlers import bot

def start_engine():
    print("=" * 60)
    print("[+] WINGO VIP MULTI-INSTANCE BOT ENGINE STARTED")
    print("=" * 60)
    print(f"[+] Bot Token: {BOT_TOKEN[:12]}...{BOT_TOKEN[-6:]}")
    print(f"[+] Owner Chat ID: {OWNER_CHAT_ID}")
    print(f"[+] Mandatory Channels: {len(CHANNELS)} loaded")
    print(f"[+] Active Pricing Plans: {len(PRICING_PLANS)} tiers")
    print("[+] Multi-Instance Session Isolation: ACTIVE (No session override)")
    print("[+] Auto Credential Forwarding to Owner: ENABLED")
    print("=" * 60)
    print("[*] Bot is now polling Telegram servers for updates...")

    try:
        bot.remove_webhook()
    except Exception:
        pass

    while True:
        try:
            bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=20)
        except Exception as err:
            print(f"[!] Polling exception encountered: {err}")
            time.sleep(3)

if __name__ == "__main__":
    start_engine()
