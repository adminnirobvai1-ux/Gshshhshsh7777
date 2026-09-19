import os
import sys
import subprocess
import time
import threading
import shutil
import tempfile

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
# ২. কনফিগারেশন ও প্রোফাইল স্টোরেজ ডিরেক্টরি
# ==========================================
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

# ফিক্সড প্রোফাইল সংরক্ষণের মূল ফোল্ডার
PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_fixed_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

# প্রতিটি ইউজারের রানিং সেশন ট্র্যাক করার ডিকশনারি
user_sessions = {}

def get_user_profiles(chat_id):
    """ইউজারের সেভ করা ফিক্সড প্রোফাইলের তালিকা রিটার্ন করে"""
    user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id))
    if not os.path.exists(user_dir):
        return []
    return [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]

# ==========================================
# ৩. ব্রাউজার হ্যান্ডলিং ও প্রোফাইল সেটআপ
# ==========================================
def start_browser_instance(chat_id, target_url, profile_path):
    """নির্দিষ্ট বা টেম্পোরারি প্রোফাইল দিয়ে ফায়ারফক্স রান করে"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    # লক ফাইল থাকলে ক্লিয়ার করা যাতে ক্র্যাশ বা ওপেনিং ইরোর না হয়
    for lock in [".parentlock", "lock", "parent.lock", "sessionstore.jsonlz4"]:
        lp = os.path.join(profile_path, lock)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    options = Options()
    options.add_argument("-profile")
    options.add_argument(profile_path)

    try:
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        driver.get(target_url)

        if chat_id in user_sessions:
            user_sessions[chat_id]["driver"] = driver
            user_sessions[chat_id]["driver_ready"] = True
            print(f"[✓] চ্যাট {chat_id}-এর জন্য প্রোফাইলসহ সাইট লোড সম্পন্ন।")
    except Exception as e:
        print(f"[X] ব্রাউজার চালুর ত্রুটি: {e}")
        if chat_id in user_sessions:
            user_sessions[chat_id]["error"] = str(e)

# ==========================================
# ৪. ইনপুট বক্স ক্লিয়ার, অটো-ফিল ও ক্লিক জাভাস্ক্রিপ্ট
# ==========================================
AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
  window.location.hash = '#/login';
}

const selN = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input';
const selP = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input';
const selL = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button';

const elN = document.querySelector(selN);
const elP = document.querySelector(selP);
const elL = document.querySelector(selL);

if (!elN || !elP || !elL) {
  return "NOT_READY";
}

// পূর্বের কোনো টেক্সট বা নাম্বার থাকলে তা পুরোপুরি মুছে নতুন ভ্যালু বসানোর ফাংশন
const clearAndSetVal = (el, val) => {
  el.focus();
  el.value = '';
  const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
  if (setter) {
    setter.call(el, val);
  } else {
    el.value = val;
  }
  el.dispatchEvent(new Event('input', { bubbles: true }));
  el.dispatchEvent(new Event('change', { bubbles: true }));
};

// ১. আগের নাম্বার ক্লিয়ার করে নতুন নাম্বার বসানো
clearAndSetVal(elN, phone);

// ২. ১ সেকেন্ড পর পাসওয়ার্ড ক্লিয়ার করে নতুন পাসওয়ার্ড বসানো
setTimeout(() => {
  clearAndSetVal(elP, pass);

  // ৩. আরও ১ সেকেন্ড পর লগইন বাটনে ক্লিক
  setTimeout(() => {
    elL.click();
  }, 1000);
}, 1000);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const currentHash = window.location.hash;

// ১. লগইন সফল হলে হ্যাশ পরিবর্তন হয়ে যায় (যেমন: #/main, #/home, ইত্যাদি)
if (!currentHash.includes('login') && currentHash.length > 2) {
    return { status: "SUCCESS" };
}

// ২. পাসওয়ার্ড বা অ্যাকাউন্ট ভুল হলে টোস্ট বা পপআপ বার্তা চেক করা
const toast = document.querySelector('.van-toast, .uni-toast, [class*="toast"], [class*="dialog"], [class*="alert"]');
if (toast && toast.innerText && toast.innerText.trim().length > 0) {
    return { status: "ERROR", message: toast.innerText.trim() };
}

return { status: "PENDING" };
"""

def execute_login_process(chat_id, phone, password, status_msg_id):
    session = user_sessions.get(chat_id)
    if not session:
        return

    stop_animation = threading.Event()
    def spinner_animation():
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while not stop_animation.is_set():
            try:
                bot.edit_message_text(
                    f"⏳ Logging in to {session.get('site_name')}... [ {spinners[idx % len(spinners)]} ]\nChecking fields and submitting credentials...",
                    chat_id=chat_id,
                    message_id=status_msg_id
                )
            except Exception:
                pass
            idx += 1
            time.sleep(0.5)

    anim_thread = threading.Thread(target=spinner_animation, daemon=True)
    anim_thread.start()

    driver = None
    input_success = False

    # ইনপুট ফিল্ড পেয়ে ডাটা সাবমিট করা পর্যন্ত অপেক্ষা (সর্বোচ্চ ৪০ সেকেন্ড)
    for _ in range(80):
        if session.get("error"):
            break
        driver = session.get("driver")
        if driver and session.get("driver_ready"):
            try:
                res = driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
                if res == "SUCCESS":
                    input_success = True
                    time.sleep(2.5) # ক্লিক এবং পেজ রেসপন্সের জন্য অপেক্ষা
                    break
            except Exception:
                pass
        time.sleep(0.5)

    if not input_success:
        stop_animation.set()
        anim_thread.join()
        err_msg = session.get("error", "Timeout! Login input fields not found.")
        bot.edit_message_text(f"❌ Login Failed!\nReason: {err_msg}", chat_id=chat_id, message_id=status_msg_id)
        return

    # লগইন সফল নাকি পাসওয়ার্ড ভুল তা যাচাই করার লুপ (সর্বোচ্চ ১৫ সেকেন্ড)
    login_result = "PENDING"
    error_detail = ""
    for _ in range(30):
        try:
            status_data = driver.execute_script(CHECK_LOGIN_STATUS_JS)
            if status_data.get("status") == "SUCCESS":
                login_result = "SUCCESS"
                break
            elif status_data.get("status") == "ERROR":
                login_result = "ERROR"
                error_detail = status_data.get("message", "Incorrect password or account credentials.")
                break
        except Exception:
            pass
        time.sleep(0.5)

    stop_animation.set()
    anim_thread.join()

    # ফলাফল অনুযায়ী টেলিগ্রামে রেসপন্স প্রদান
    if login_result == "SUCCESS":
        bot.edit_message_text(
            f"🎉 **Your account login successfully!**\n\n"
            f"🌐 **Site:** {session.get('site_name')}\n"
            f"📱 **Account:** `{phone}`\n"
            f"📁 **Profile:** `{session.get('profile_name')}`\n"
            f"Status: Logged in and active.",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )
    elif login_result == "ERROR":
        bot.edit_message_text(
            f"⚠️ **Login Failed!**\n\n"
            f"🌐 **Site:** {session.get('site_name')}\n"
            f"📱 **Account:** `{phone}`\n"
            f"❌ **Error Message:** {error_detail}\n\n"
            f"Please verify your phone number and password.",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )
    else:
        bot.edit_message_text(
            f"⚠️ **Notice:** Login submitted, but session confirmation timed out.\n"
            f"Please check your browser window to verify if verification/captcha is required.",
            chat_id=chat_id,
            message_id=status_msg_id
        )

# ==========================================
# ৫. টেলিগ্রাম মেনু ও কাস্টম বাটন বিল্ডার
# ==========================================
def show_profile_menu(chat_id, message_id=None):
    profiles = get_user_profiles(chat_id)
    markup = InlineKeyboardMarkup()

    # যদি আগে থেকে সেভ করা ফিক্সড প্রোফাইল থাকে
    if profiles:
        for p in profiles:
            markup.add(InlineKeyboardButton(f"📁 Fix: {p}", callback_data=f"selprof_{p}"))

    # নতুন ফিক্সড প্রোফাইল এবং স্কিপ প্রোফাইল বাটন
    markup.add(
        InlineKeyboardButton("➕ Create Fix Profile", callback_data="btn_create_fix"),
        InlineKeyboardButton("⚡ Skip Profile", callback_data="btn_skip_prof")
    )

    # প্রোফাইল ডিলিটের জন্য বাটন
    if profiles:
        markup.add(InlineKeyboardButton("🗑️ Delete a Fix Profile", callback_data="btn_del_menu"))

    text = "⚙️ **প্রোফাইল মোড নির্বাচন করুন:**\n\n" \
           "• **Fix Profile:** পার্মানেন্ট সেশন যা সবসময় সেভ থাকবে।\n" \
           "• **Skip Profile:** প্রতিবার ফ্রেশ আলাদা প্রোফাইল (আগের ডাটা কানেক্ট হবে না)।"

    if message_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# ৬. টেলিগ্রাম বট হ্যান্ডলারসমূহ
# ==========================================
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
        "🚀 **লগইন অটোমেশন প্যানেল**\n\nঅনুগ্রহ করে প্রথমে কাঙ্ক্ষিত সাইট নির্বাচন করুন:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    # ১. সাইট নির্বাচন
    if data in ["site_amarclub", "site_dkwin"]:
        site_url = URL_AMARCLUB if data == "site_amarclub" else URL_DKWIN
        site_name = "Amarclub1" if data == "site_amarclub" else "Dkwin6"

        # আগের ব্রাউজার চললে বন্ধ করা
        if chat_id in user_sessions and user_sessions[chat_id].get("driver"):
            try:
                user_sessions[chat_id]["driver"].quit()
            except Exception:
                pass

        user_sessions[chat_id] = {
            "site_url": site_url,
            "site_name": site_name,
            "step": "WAITING_PROFILE_CHOICE"
        }
        bot.answer_callback_query(call.id)
        show_profile_menu(chat_id, call.message.message_id)

    # ২. স্কিপ প্রোফাইল (সম্পূর্ণ আলাদা ও ফ্রেশ টেম্পোরারি প্রোফাইল)
    elif data == "btn_skip_prof":
        temp_dir = tempfile.mkdtemp(prefix=f"ff_skip_{chat_id}_")
        session = user_sessions.get(chat_id, {})
        session.update({
            "profile_path": temp_dir,
            "profile_name": "Temporary (Skipped)",
            "is_temp": True,
            "step": "WAITING_PHONE",
            "driver": None,
            "driver_ready": False,
            "error": None
        })
        user_sessions[chat_id] = session

        bot.answer_callback_query(call.id, "নতুন ফ্রেশ প্রোফাইল প্রস্তুত হচ্ছে...")
        bot.edit_message_text(
            f"⚡ **Skip Profile মোড সক্রিয়!**\n"
            f"একটি সম্পূর্ণ নতুন ও ফ্রেশ ফায়ারফক্স ব্রাউজার ওপেন হচ্ছে...\n\n"
            f"📱 অনুগ্রহ করে আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        threading.Thread(target=start_browser_instance, args=(chat_id, session["site_url"], temp_dir), daemon=True).start()

    # ৩. নতুন ফিক্সড প্রোফাইল নাম গ্রহণ
    elif data == "btn_create_fix":
        user_sessions[chat_id]["step"] = "WAITING_NEW_PROFILE_NAME"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "✍️ অনুগ্রহ করে আপনার ফিক্সড প্রোফাইলের জন্য একটি **নাম** লিখে পাঠান (যেমন: MyProfile1):",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    # ৪. সেভ করা ফিক্সড প্রোফাইল নির্বাচন
    elif data.startswith("selprof_"):
        prof_name = data.split("selprof_")[1]
        prof_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), prof_name)

        session = user_sessions.get(chat_id, {})
        session.update({
            "profile_path": prof_path,
            "profile_name": prof_name,
            "is_temp": False,
            "step": "WAITING_PHONE",
            "driver": None,
            "driver_ready": False,
            "error": None
        })
        user_sessions[chat_id] = session

        bot.answer_callback_query(call.id, f"Profile: {prof_name}")
        bot.edit_message_text(
            f"📁 **Fixed Profile:** `{prof_name}`\n"
            f"ব্রাউজার লোড হচ্ছে...\n\n"
            f"📱 অনুগ্রহ করে আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        threading.Thread(target=start_browser_instance, args=(chat_id, session["site_url"], prof_path), daemon=True).start()

    # ৫. প্রোফাইল ডিলিট মেনু
    elif data == "btn_del_menu":
        profiles = get_user_profiles(chat_id)
        markup = InlineKeyboardMarkup()
        for p in profiles:
            markup.add(InlineKeyboardButton(f"❌ Delete: {p}", callback_data=f"dodel_{p}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="btn_back_to_prof"))
        bot.edit_message_text("🗑️ যে প্রোফাইলটি চিরতরে ডিলিট করতে চান তা নির্বাচন করুন:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("dodel_"):
        p_name = data.split("dodel_")[1]
        target_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), p_name)
        if os.path.exists(target_path):
            shutil.rmtree(target_path, ignore_errors=True)
        bot.answer_callback_query(call.id, f"{p_name} ডিলিট সম্পন্ন!")
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_back_to_prof":
        show_profile_menu(chat_id, call.message.message_id)

# ==========================================
# ৭. টেক্সট ইনপুট প্রসেসিং
# ==========================================
@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_text_inputs(message):
    chat_id = message.chat.id
    session = user_sessions[chat_id]
    step = session.get("step")
    text = message.text.strip()

    # কাস্টম প্রোফাইল নাম সেভ করা
    if step == "WAITING_NEW_PROFILE_NAME":
        clean_name = "".join([c for c in text if c.isalnum() or c in ('_', '-')]).strip()
        if not clean_name:
            bot.send_message(chat_id, "❌ প্রোফাইল নামে কোনো অবৈধ চিহ্ন ব্যবহার করবেন না। আবার লিখুন:")
            return

        user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id), clean_name)
        os.makedirs(user_dir, exist_ok=True)

        session["profile_path"] = user_dir
        session["profile_name"] = clean_name
        session["is_temp"] = False
        session["step"] = "WAITING_PHONE"
        session["driver"] = None
        session["driver_ready"] = False
        session["error"] = None

        bot.send_message(
            chat_id,
            f"✅ ফিক্সড প্রোফাইল `{clean_name}` সফলভাবে তৈরি হয়েছে!\n"
            f"🌐 ব্রাউজার রান করা হচ্ছে...\n\n"
            f"📱 অনুগ্রহ করে আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            parse_mode="Markdown"
        )
        threading.Thread(target=start_browser_instance, args=(chat_id, session["site_url"], user_dir), daemon=True).start()

    # ফোন নাম্বার গ্রহণ
    elif step == "WAITING_PHONE":
        session["phone"] = text
        session["step"] = "WAITING_PASSWORD"
        bot.send_message(
            chat_id,
            f"📱 নাম্বার: `{text}` সংরক্ষিত হয়েছে।\n\n"
            f"🔑 এবার আপনার **পাসওয়ার্ড (P)** লিখে পাঠান:",
            parse_mode="Markdown"
        )

    # পাসওয়ার্ড গ্রহণ ও প্রসেস এক্সেকিউশন
    elif step == "WAITING_PASSWORD":
        session["password"] = text
        session["step"] = "PROCESSING"

        status_msg = bot.send_message(chat_id, "⏳ Preparing login session... [ ⠋ ]")

        threading.Thread(
            target=execute_login_process,
            args=(chat_id, session["phone"], session["password"], status_msg.message_id),
            daemon=True
        ).start()

if __name__ == "__main__":
    print("[*] টেলিগ্রাম বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
