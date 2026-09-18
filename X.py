import os
import sys
import subprocess
import time
import threading
import shutil
import glob

# ==========================================
# ১. প্রয়োজনীয় প্যাকেজ অটো-ইনস্টল
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] প্যাকেজ ইনস্টল করা হচ্ছে: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# ==========================================
# ২. কনফিগারেশন ও সেশন ডাটা
# ==========================================
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

# উভয় সাইটেই সরাসরি লগইন পেজের লিংক
URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

user_sessions = {}

def get_fast_profile_dir():
    """ভারী ক্যাশে ও পুরোনো লক ফাইল ছাড়া দ্রুত ফায়ারফক্স প্রোফাইল লোড করার ফাংশন"""
    base_dir = os.path.expanduser("~/.mozilla/firefox/")
    profiles = glob.glob(os.path.join(base_dir, "*default-release*")) or glob.glob(os.path.join(base_dir, "*.default*"))
    if not profiles:
        return None
    
    src_profile = profiles[0]
    temp_profile = "/tmp/firefox_fast_profile"

    # প্রোফাইল তৈরি না থাকলে অপ্টিমাইজ করে কপি করা
    if not os.path.exists(temp_profile):
        try:
            print("[*] ফায়ারফক্স প্রোফাইল অপ্টিমাইজ করা হচ্ছে...")
            ignore_list = shutil.ignore_patterns(
                "cache2", "storage", "safebrowsing", "jumpListCache",
                "datareporting", "minidumps", "saved-telemetry-pings",
                "lock", ".parentlock", "parent.lock"
            )
            shutil.copytree(src_profile, temp_profile, ignore=ignore_list)
        except Exception as e:
            print(f"[!] প্রোফাইল কপি সতর্কবার্তা: {e}")
            return src_profile

    # পুরোনো কোনো লক ফাইল বা সেশন হিস্ট্রি থাকলে তা মুছে দেওয়া যাতে ফ্রেশ উইন্ডো খোলে
    for lock_name in [".parentlock", "lock", "parent.lock", "sessionstore.jsonlz4"]:
        lock_path = os.path.join(temp_profile, lock_name)
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except Exception:
                pass

    return temp_profile

# ==========================================
# ৩. ব্রাউজার হ্যান্ডলিং
# ==========================================
def start_browser_for_user(chat_id, target_url):
    """সাইট সিলেক্ট করার সাথে সাথেই ব্রাউজার ওপেন করা শুরু করবে"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    options = Options()
    profile_path = get_fast_profile_dir()
    if profile_path and os.path.exists(profile_path):
        options.add_argument("-profile")
        options.add_argument(profile_path)

    try:
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        driver.get(target_url)

        if chat_id in user_sessions:
            user_sessions[chat_id]["driver"] = driver
            user_sessions[chat_id]["driver_ready"] = True
            print(f"[✓] চ্যাট {chat_id}-এর জন্য সাইট লোড সফল।")
    except Exception as e:
        print(f"[X] ব্রাউজার চালুর ত্রুটি: {e}")
        if chat_id in user_sessions:
            user_sessions[chat_id]["error"] = str(e)

# ==========================================
# ৪. ডায়নামিক অটো-ফিল ও ক্লিক জাভাস্ক্রিপ্ট
# ==========================================
AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

// হ্যাশ না থাকলে নিশ্চিতভাবে /login এ পাঠানো
if (!window.location.hash.includes('login')) {
  window.location.hash = '#/login';
}

const selN = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input';
const selP = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input';
const selL = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button';

const elN = document.querySelector(selN);
const elP = document.querySelector(selP);
const elL = document.querySelector(selL);

// যতক্ষণ তিনটি এলিমেন্ট পুরোপুরি লোড না হবে, ততক্ষণ কাজ শুরু করবে না
if (!elN || !elP || !elL) {
  return "NOT_READY";
}

const setVal = (el, val) => {
  el.focus();
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
  if (setter) setter.call(el, val);
  else el.value = val;
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
};

// ১. N ইনপুটে নাম্বার বসানো
setVal(elN, phone);

// ২. ১ সেকেন্ড পর P ইনপুটে পাসওয়ার্ড বসানো
setTimeout(() => {
  setVal(elP, pass);

  // ৩. আরও ১ সেকেন্ড পর L বাটনে ক্লিক
  setTimeout(() => {
    elL.click();
  }, 1000);
}, 1000);

return "SUCCESS";
"""

def execute_login_process(chat_id, phone, password, status_msg_id):
    """ডাটা ইনজেক্ট করা এবং টেলিগ্রামে লাইভ স্পিনার দেখানো"""
    session = user_sessions.get(chat_id)
    if not session:
        return

    # টেলিগ্রামে লোডিং স্পিনার অ্যানিমেশন
    stop_animation = threading.Event()
    def spinner_animation():
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while not stop_animation.is_set():
            try:
                bot.edit_message_text(
                    f"⏳ সাইট লোড হওয়া এবং তথ্য পেজে সেট করার অপেক্ষা করা হচ্ছে... [ {spinners[idx % len(spinners)]} ]\nঅনুগ্রহ করে অপেক্ষা করুন...",
                    chat_id=chat_id,
                    message_id=status_msg_id
                )
            except Exception:
                pass
            idx += 1
            time.sleep(0.5)

    anim_thread = threading.Thread(target=spinner_animation, daemon=True)
    anim_thread.start()

    # সাইট ও ইনপুট ফিল্ড দৃশ্যমান হওয়া পর্যন্ত অপেক্ষা (সর্বোচ্চ ৬০ সেকেন্ড)
    driver = None
    success = False
    for _ in range(120):
        if session.get("error"):
            break
        driver = session.get("driver")
        if driver and session.get("driver_ready"):
            try:
                res = driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
                if res == "SUCCESS":
                    success = True
                    # জাভাস্ক্রিপ্টের ১ সেকেন্ড বিরতিতে P এবং L ক্লিকের কাজ শেষ হতে ২.৫ সেকেন্ড অপেক্ষা
                    time.sleep(2.5)
                    break
            except Exception:
                pass
        time.sleep(0.5)

    stop_animation.set()
    anim_thread.join()

    # কাজ সম্পন্ন হলে ডান (Done) মেসেজ দেখানো
    if success:
        bot.edit_message_text(
            f"✅ **Done!**\n\n"
            f"🌐 **সাইট:** {session.get('site_name')}\n"
            f"📱 **নাম্বার (N):** `{phone}`\n"
            f"🔑 **পাসওয়ার্ড (P):** `••••••••`\n\n"
            f"সাইট পুরোপুরি লোড হয়ে ১ সেকেন্ড বিরতিতে N, P বসেছে এবং L বাটনে ক্লিক সম্পন্ন হয়েছে!",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )
    else:
        err_msg = session.get("error", "নির্দিষ্ট সময়ে সাইটের ইনপুট বক্স খুঁজে পাওয়া যায়নি।")
        bot.edit_message_text(
            f"❌ ব্যর্থ হয়েছে!\nকারণ: {err_msg}",
            chat_id=chat_id,
            message_id=status_msg_id
        )

# ==========================================
# ৫. টেলিগ্রাম বট হ্যান্ডলারসমূহ
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
        "লগইন করতে নিচের সাইট নির্বাচন করুন:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    target_url = None
    site_name = ""

    if call.data == "btn_amarclub":
        target_url = URL_AMARCLUB
        site_name = "Amarclub1"
    elif call.data == "btn_dkwin":
        target_url = URL_DKWIN
        site_name = "Dkwin6"

    if target_url:
        # আগের কোনো খোলা ব্রাউজার থাকলে বন্ধ করা
        if chat_id in user_sessions and user_sessions[chat_id].get("driver"):
            try:
                user_sessions[chat_id]["driver"].quit()
            except Exception:
                pass

        user_sessions[chat_id] = {
            "site_url": target_url,
            "site_name": site_name,
            "step": "WAITING_PHONE",
            "driver": None,
            "driver_ready": False,
            "error": None
        }

        bot.answer_callback_query(call.id, f"{site_name} লোড হচ্ছে...")

        # ব্যাকগ্রাউন্ডে ব্রাউজার ওপেন শুরু করা
        threading.Thread(target=start_browser_for_user, args=(chat_id, target_url), daemon=True).start()

        # ব্যবহারকারীর কাছে নাম্বার চাওয়া
        bot.send_message(
            chat_id, 
            f"🌐 **{site_name}** ব্রাউজারে লোড হচ্ছে...\n\n"
            f"📱 অনুগ্রহ করে আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            parse_mode="Markdown"
        )

@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_user_input(message):
    chat_id = message.chat.id
    session = user_sessions[chat_id]
    step = session.get("step")
    text = message.text.strip()

    # ধাপ ১: নাম্বার গ্রহণ
    if step == "WAITING_PHONE":
        session["phone"] = text
        session["step"] = "WAITING_PASSWORD"
        bot.send_message(
            chat_id, 
            f"📱 নাম্বার: `{text}` সংরক্ষিত হয়েছে।\n\n"
            f"🔑 এবার আপনার **পাসওয়ার্ড (P)** লিখে পাঠান:",
            parse_mode="Markdown"
        )

    # ধাপ ২: পাসওয়ার্ড গ্রহণ ও প্রসেসিং শুরু
    elif step == "WAITING_PASSWORD":
        session["password"] = text
        session["step"] = "PROCESSING"

        loading_msg = bot.send_message(chat_id, "⏳ সাইট লোড হওয়া এবং তথ্য পেজে সেট করার অপেক্ষা করা হচ্ছে... [ ⠋ ]")

        threading.Thread(
            target=execute_login_process, 
            args=(chat_id, session["phone"], session["password"], loading_msg.message_id),
            daemon=True
        ).start()

if __name__ == "__main__":
    print("[*] টেলিগ্রাম বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
