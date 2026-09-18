import os
import sys
import subprocess
import time
import threading
import shutil
import glob

# ==========================================
# ১. প্রয়োজনীয় প্যাকেজগুলো অটো-ইনস্টল করা
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] প্যাকেজ নেই, ইনস্টল করা হচ্ছে: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# ২. কনফিগারেশন
# ==========================================
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

# ফায়ারফক্স প্রোফাইল স্বয়ংক্রিয়ভাবে খুঁজে নেওয়ার লজিক (VPN এক্সটেনশন পাওয়ার জন্য)
def get_firefox_profile():
    base_dir = os.path.expanduser("~/.mozilla/firefox/")
    profiles = glob.glob(os.path.join(base_dir, "*default-release*")) or glob.glob(os.path.join(base_dir, "*.default*"))
    if profiles:
        return profiles[0]
    return None

# ==========================================
# ৩. অটো-ফিল এবং বাটন ক্লিক স্ক্রিপ্ট
# ==========================================
# Vue/React ফ্রেমওয়ার্কে ইনপুট রেজিস্টার এবং ক্লিক নিশ্চিত করার শক্তিশালী লজিক
AUTO_LOGIN_JS = """
(function(){
  const setVal = (el, val) => {
    el.focus();
    el.select();
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(el, val);
    else el.value = val;
    // Vue/UniApp এর স্টেট পরিবর্তনের জন্য সব ইভেন্ট ট্রিগার করা
    document.execCommand('insertText', false, val);
    el.dispatchEvent(new InputEvent('input', { bubbles: true, cancelable: true, data: val }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const clickEl = (el) => {
    el.focus();
    ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
      el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
    });
    el.click();
  };

  const selN = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input';
  const selP = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input';
  const selL = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button';

  // ইনপুট বক্স এবং বাটন খোঁজা
  let inputN = document.querySelector(selN) || document.querySelector('input[type="tel"]') || document.querySelector('input[type="text"]');
  let inputP = document.querySelector(selP) || document.querySelector('input[type="password"]');
  let btnL = document.querySelector(selL) || document.querySelector('button[type="submit"]') || document.querySelector('button');

  if (!inputN || !inputP || !btnL) {
    return "ELEMENTS_NOT_READY";
  }

  // ১. N ইনপুটে নাম্বার বসানো
  setVal(inputN, '1876685711');

  // ২. ১ সেকেন্ড পর P ইনপুটে পাসওয়ার্ড বসানো
  setTimeout(() => {
    setVal(inputP, 'NAYYYY');

    // ৩. আরও ১ সেকেন্ড পর L বাটনে ক্লিক
    setTimeout(() => {
      clickEl(btnL);
    }, 1000);
  }, 1000);

  return "SUCCESS";
})();
"""

def launch_and_automate(url):
    """ব্রাউজার ওপেন এবং নির্ভরযোগ্যভাবে ফর্ম পূরণ ও ক্লিক করার ফাংশন"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    options = Options()
    profile_path = get_firefox_profile()

    # আগের প্রোফাইলের লক এড়াতে টেম্প ফোল্ডারে কপি করে লোড করা (VPN এক্সটেনশন সহ)
    if profile_path:
        temp_profile = "/tmp/firefox_auto_profile"
        if not os.path.exists(temp_profile):
            try:
                shutil.copytree(profile_path, temp_profile, ignore=shutil.ignore_patterns("lock", ".parentlock"))
            except Exception:
                pass
        if os.path.exists(temp_profile):
            options.add_argument("-profile")
            options.add_argument(temp_profile)

    driver = None
    try:
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        driver.get(url)

        # পেজ এবং ইনপুট ফিল্ড সম্পূর্ণরূপে রেন্ডার হওয়ার অপেক্ষা করা
        print("[*] সাইট লোড হচ্ছে...")
        time.sleep(5)

        # ইনপুট ফিল্ড তৈরি হওয়া পর্যন্ত প্রতি ৫০০ মিলি-সেকেন্ডে স্ক্রিপ্ট ট্রাই করবে (সর্বোচ্চ ২০ সেকেন্ড)
        executed = False
        for _ in range(40):
            res = driver.execute_script(AUTO_LOGIN_JS)
            if res == "SUCCESS":
                print("[✓] ইনপুট পূরণ হয়েছে এবং ১ সেকেন্ড পর পর N -> P -> L সিকোয়েন্স চালু হয়েছে।")
                executed = True
                break
            time.sleep(0.5)

        if not executed:
            print("[!] এলিমেন্ট নির্দিষ্ট সময়ে পাওয়া যায়নি।")

    except Exception as e:
        print(f"[X] ত্রুটি: {e}")

# ==========================================
# ৪. টেলিগ্রাম বট হ্যান্ডলার
# ==========================================
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
        "ডেক্সটপে সাইট ওপেন এবং অটো-লগইন করতে নির্বাচন করুন:", 
        reply_markup=markup
    )

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
        bot.answer_callback_query(call.id, f"{site_name} চালু হচ্ছে...")
        bot.send_message(call.message.chat.id, f"{site_name} লোড হচ্ছে। সাইট পুরোপুরি আসা মাত্রই ১ সেকেন্ড বিরতিতে N, P বসে L এ ক্লিক হবে।")

        threading.Thread(target=launch_and_automate, args=(target_url,), daemon=True).start()

if __name__ == "__main__":
    print("[*] টেলিগ্রাম বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
