import sys
import subprocess
import os
import time

# --- প্রয়োজনীয় প্যাকেজ অটো-ইন্সটলার ---
REQUIRED_PACKAGES = {
    "pyTelegramBotAPI": "telebot",
    "selenium": "selenium",
    "webdriver-manager": "webdriver_manager"
}

for package, import_name in REQUIRED_PACKAGES.items():
    try:
        __import__(import_name)
    except ImportError:
        print(f"[{package}] প্যাকেজটি পাওয়া যায়নি। অটো-ইন্সটল হচ্ছে...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

# টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFpjgYEYHDyNJ2dJhqZ5S4e4qzINulz5js"
bot = telebot.TeleBot(TOKEN)

# ওয়েবসাইটের ইউআরএল
URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

# আপনার JS কোডের CSS সিলেক্টরগুলো
SEL_PHONE = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input"
SEL_PASS = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input"
SEL_LOGIN_BTN = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button"

# ইউজারের ডাটা সেভ রাখার জন্য ডিকশনারি
user_sessions = {}

def run_selenium_automation(url, phone, password):
    """ভার্চুয়াল ডেস্কটপ ডিসপ্লেতে ফায়ারফক্স ওপেন করে অটোমেটিক লগইন করার ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        os.environ["DISPLAY"] = ":0"  # ডেক্সটপ ডিসপ্লে সেট করা

    options = FirefoxOptions()
    # options.add_argument("--headless") # ব্রাউজার না দেখিয়ে ব্যাকগ্রাউন্ডে চালাতে চাইলে এটি আনকমেন্ট করুন

    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.maximize_window()
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        # ১. ফোন/ইউজারনেম (N) ফিল্ড খুঁজে মান বসানো
        phone_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEL_PHONE)))
        phone_input.click()
        phone_input.clear()
        phone_input.send_keys(phone)
        time.sleep(0.5)

        # ২. পাসওয়ার্ড (P) ফিল্ড খুঁজে মান বসানো
        pass_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEL_PASS)))
        pass_input.click()
        pass_input.clear()
        pass_input.send_keys(password)
        time.sleep(0.5)

        # ৩. লগইন বাটন (L) খুঁজে ক্লিক করা
        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, SEL_LOGIN_BTN)))
        login_btn.click()

        return True, "সফলভাবে লগইন ইনপুট সম্পন্ন হয়েছে!"
    except Exception as e:
        return False, f"সমস্যা হয়েছে: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Amarclub1", callback_data="site_amarclub"),
        InlineKeyboardButton("Dkwin6", callback_data="site_dkwin")
    )
    bot.send_message(
        message.chat.id, 
        "লগইন করতে সাইট সিলেক্ট করুন:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("site_"))
def handle_site_selection(call):
    chat_id = call.message.chat.id
    target_url = URL_AMARCLUB if call.data == "site_amarclub" else URL_DKWIN
    user_sessions[chat_id] = {"url": target_url}

    bot.answer_callback_query(call.id)
    msg = bot.send_message(chat_id, "📱 অনুগ্রহ করে আপনার **নাম্বার (N)** টি পাঠান:")
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    chat_id = message.chat.id
    phone = message.text.strip()
    user_sessions[chat_id]["phone"] = phone

    msg = bot.send_message(chat_id, "🔑 এবার আপনার **পাসওয়ার্ড (P)** দিন:")
    bot.register_next_step_handler(msg, process_password_step)

def process_password_step(message):
    chat_id = message.chat.id
    password = message.text.strip()
    session = user_sessions.get(chat_id)

    if not session:
        bot.send_message(chat_id, "সেশন পাওয়া যায়নি। অনুগ্রহ করে /start দিন।")
        return

    bot.send_message(chat_id, "⚙️ ব্রাউজার চালু হচ্ছে এবং স্বয়ংক্রিয়ভাবে তথ্য পূরণ করা হচ্ছে...")

    success, status_msg = run_selenium_automation(
        url=session["url"], 
        phone=session["phone"], 
        password=password
    )

    if success:
        bot.send_message(chat_id, "✅ তথ্য সাবমিট এবং লগইন বাটনে ক্লিক সম্পন্ন হয়েছে!")
    else:
        bot.send_message(chat_id, f"❌ ত্রুটি: {status_msg}")

    # কাজ শেষে ইউজারের ডাটা পরিষ্কার করা
    user_sessions.pop(chat_id, None)

if __name__ == "__main__":
    print("বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
