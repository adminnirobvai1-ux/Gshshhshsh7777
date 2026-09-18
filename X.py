import os
import subprocess
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

# ওয়েবসাইটের লিংক
URL_AMARCLUB = "https://amarclub1.com"
URL_DKWIN = "https://dkwin6.com/#/login"

def open_firefox(url):
    """অনলাইন ডেক্সটপের ডিসপ্লেতে ফায়ারফক্স ওপেন করার মূল ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    try:
        subprocess.Popen(["firefox", "--new-tab", url], env=env)
        return True
    except Exception as e:
        print(f"Error opening Firefox: {e}")
        return False

def auto_run_bookmarklet():
    """লিংক ওপেন হওয়ার পর স্বয়ংক্রিয়ভাবে বুকমার্কলেট ট্রিগার করার ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"

    # পেজ ও ভিপিএন পুরোপুরি লোড হওয়ার জন্য ৫ সেকেন্ড অপেক্ষা
    time.sleep(5)

    try:
        # ১. ফায়ারফক্স উইন্ডোটি সামনে (Focus) আনা
        subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "firefox", "windowactivate"], env=env)
        time.sleep(0.5)

        # ২. অ্যাড্রেস বার ফোকাস করা (Ctrl + L)
        subprocess.run(["xdotool", "key", "ctrl+l"], env=env)
        time.sleep(0.3)

        # ৩. বুকমার্কলেটের কি-ওয়ার্ড টাইপ করা (যেমন: run)
        subprocess.run(["xdotool", "type", "run"], env=env)
        time.sleep(0.3)

        # ৪. এন্টার চাপ দেওয়া (যাতে বুকমার্কলেট কার্যকর হয়)
        subprocess.run(["xdotool", "key", "Return"], env=env)
        print("অটো-প্লে স্ক্রিপ্ট রান হয়েছে।")
    except Exception as e:
        print(f"Auto-run error: {e}")

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Amarclub1", callback_data="btn_amarclub"),
        InlineKeyboardButton("Dkwin6", callback_data="btn_dkwin")
    )
    bot.send_message(
        message.chat.id, 
        "ডেক্সটপে সাইট ওপেন করতে নিচের বাটনে ক্লিক করুন:", 
        reply_markup=markup
    )

# বাটন ক্লিক ইভেন্ট হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    target_url = None
    site_name = ""

    if call.data == "btn_amarclub":
        target_url = URL_AMARCLUB
        site_name = "Amarclub1"
    elif call.data == "btn_dkwin":
        target_url = URL_DKWIN
        site_name = "Dkwin6"

    if target_url:
        if open_firefox(target_url):
            bot.answer_callback_query(call.id, f"{site_name} ওপেন করা হয়েছে!")
            bot.send_message(call.message.chat.id, f"{site_name} ওপেন হয়েছে এবং অটো-প্লে শুরু হচ্ছে...")

            # ব্যাকগ্রাউন্ডে বুকমার্কলেট অটো-রান করানো
            threading.Thread(target=auto_run_bookmarklet, daemon=True).start()
        else:
            bot.answer_callback_query(call.id, "ফায়ারফক্স চালু করা সম্ভব হয়নি।")

if __name__ == "__main__":
    print("বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
