import os
import sys
import subprocess
import time
import threading
import shutil
import tempfile

# ==========================================
# 1. Fametrahana sy fanafarana ireo fonosana ilaina
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Mametraka fonosana: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# ==========================================
# 2. Fanamboarana sy tahiry momba ny mombamomba (Profiles)
# ==========================================
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_fixed_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}

def get_user_profiles(chat_id):
    """Mamerina ny lisitry ny mombamomba raikitra an'ilay mpampiasa"""
    user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id))
    if not os.path.exists(user_dir):
        return []
    return [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]

def auto_close_browser_after_24h(chat_id):
    """Manakatona ny navigateur ho azy afaka 24 ora"""
    session = user_sessions.get(chat_id)
    if session and session.get("driver"):
        try:
            print(f"[*] 24 ora tapitra. Manakatona ny navigateur ho an'ny: {chat_id}")
            session["driver"].quit()
        except Exception:
            pass
        session["driver"] = None
        session["driver_ready"] = False

# ==========================================
# 3. Fitantanana ny navigateur sy ny takelaka (Tabs)
# ==========================================
def setup_or_open_tab(chat_id, target_url, profile_path):
    """Manokatra navigateur vaovao na manampy takelaka vaovao raha efa misokatra"""
    session = user_sessions.get(chat_id)
    driver = session.get("driver") if session else None

    # Raha efa mandeha ny navigateur dia manokatra takelaka vaovao
    if driver is not None:
        try:
            driver.switch_to.new_window('tab')
            driver.get(target_url)
            session["driver_ready"] = True
            session["current_tab"] = driver.current_window_handle
            print(f"[✓] Takelaka vaovao nisokatra ho an'i {chat_id}.")
            return
        except Exception as e:
            print(f"[!] Tsy nahomby ny fanokafana takelaka vaovao: {e}, manomboka vaovao...")

    # Raha mbola tsy mandeha dia manokatra navigateur vaovao
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

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
            user_sessions[chat_id]["current_tab"] = driver.current_window_handle

            # Manomboka ny fanisam-potoana 24 ora (86400 segondra)
            timer = threading.Timer(86400, auto_close_browser_after_24h, args=[chat_id])
            timer.daemon = True
            timer.start()
            user_sessions[chat_id]["timer"] = timer

            print(f"[✓] Navigateur vaovao nisokatra miaraka amin'ny fameram-potoana 24 ora ho an'i {chat_id}.")
    except Exception as e:
        print(f"[X] Hadisoana teo am-panokafana ny navigateur: {e}")
        if chat_id in user_sessions:
            user_sessions[chat_id]["error"] = str(e)

# ==========================================
# 4. JavaScript ho an'ny fanoratana sy fidirana
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

clearAndSetVal(elN, phone);

setTimeout(() => {
  clearAndSetVal(elP, pass);
  setTimeout(() => {
    elL.click();
  }, 1000);
}, 1000);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const currentHash = window.location.hash;

if (!currentHash.includes('login') && currentHash.length > 2) {
    return { status: "SUCCESS" };
}

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

    for _ in range(80):
        if session.get("error"):
            break
        driver = session.get("driver")
        if driver and session.get("driver_ready"):
            try:
                # Mifindra amin'ny takelaka misy ankehitriny
                if "current_tab" in session:
                    driver.switch_to.window(session["current_tab"])
                res = driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
                if res == "SUCCESS":
                    input_success = True
                    time.sleep(2.5)
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

    login_result = "PENDING"
    error_detail = ""
    for _ in range(30):
        try:
            if "current_tab" in session:
                driver.switch_to.window(session["current_tab"])
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

    if login_result == "SUCCESS":
        bot.edit_message_text(
            f"🎉 **Your account login successfully!**\n\n"
            f"🌐 **Site:** {session.get('site_name')}\n"
            f"📱 **Account:** `{phone}`\n"
            f"📁 **Profile:** `{session.get('profile_name')}`\n"
            f"Status: Logged in and active in a dedicated tab.\n"
            f"⏰ *Hikatona ho azy afaka 24 ora ity navigateur ity.*",
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
            f"Please check your browser tab to verify if verification/captcha is required.",
            chat_id=chat_id,
            message_id=status_msg_id
        )

# ==========================================
# 5. Safidy sy bokotra ao amin'ny Telegram
# ==========================================
def show_profile_menu(chat_id, message_id=None):
    profiles = get_user_profiles(chat_id)
    markup = InlineKeyboardMarkup()

    if profiles:
        for p in profiles:
            markup.add(InlineKeyboardButton(f"📁 Fix: {p}", callback_data=f"selprof_{p}"))

    markup.add(
        InlineKeyboardButton("➕ Create Fix Profile", callback_data="btn_create_fix"),
        InlineKeyboardButton("⚡ Skip Profile", callback_data="btn_skip_prof")
    )

    if profiles:
        markup.add(InlineKeyboardButton("🗑️ Delete a Fix Profile", callback_data="btn_del_menu"))

    text = "⚙️ **Safidio ny fomba hampiasana ny mombamomba (Profile Mode):**\n\n" \
           "• **Fix Profile:** Mombamomba raikitra izay voatahiry foana.\n" \
           "• **Skip Profile:** Mombamomba vaovao vonjimaika (tsy mifandray amin'ny teo aloha)."

    if message_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# 6. Mpiandraikitra ny baiko Telegram
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
        "🚀 **Fitaovana Fidirana Ho Azy (Automation Panel)**\n\nSafidio ny tranonkala tianao hidirana:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    if data in ["site_amarclub", "site_dkwin"]:
        site_url = URL_AMARCLUB if data == "site_amarclub" else URL_DKWIN
        site_name = "Amarclub1" if data == "site_amarclub" else "Dkwin6"

        current_driver = user_sessions.get(chat_id, {}).get("driver")
        current_timer = user_sessions.get(chat_id, {}).get("timer")

        # Mitahiry ny fampahalalana nefa tsy manakatona ny navigateur raha efa misokatra
        user_sessions[chat_id] = {
            "site_url": site_url,
            "site_name": site_name,
            "step": "WAITING_PROFILE_CHOICE",
            "driver": current_driver,
            "driver_ready": True if current_driver else False,
            "timer": current_timer
        }
        bot.answer_callback_query(call.id)
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_skip_prof":
        session = user_sessions.get(chat_id, {})
        if not session.get("driver"):
            temp_dir = tempfile.mkdtemp(prefix=f"ff_skip_{chat_id}_")
            session["profile_path"] = temp_dir
        else:
            temp_dir = session.get("profile_path", tempfile.gettempdir())

        session.update({
            "profile_name": "Temporary (Skipped)",
            "is_temp": True,
            "step": "WAITING_PHONE",
            "driver_ready": False,
            "error": None
        })
        user_sessions[chat_id] = session

        bot.answer_callback_query(call.id, "Manomana ny takelaka vaovao...")
        bot.edit_message_text(
            f"⚡ **Skip Profile Mode!**\n"
            f"Manokatra takelaka vaovao ao amin'ny navigateur...\n\n"
            f"📱 Ampidiro azafady ny **Laharana finday (N)**:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        threading.Thread(target=setup_or_open_tab, args=(chat_id, session["site_url"], temp_dir), daemon=True).start()

    elif data == "btn_create_fix":
        user_sessions[chat_id]["step"] = "WAITING_NEW_PROFILE_NAME"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "✍️ Soraty eto ny **anarana** tianao omena ny mombamomba raikitra (ohatra: Kaonty1):",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif data.startswith("selprof_"):
        prof_name = data.split("selprof_")[1]
        prof_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), prof_name)

        session = user_sessions.get(chat_id, {})
        session.update({
            "profile_path": prof_path,
            "profile_name": prof_name,
            "is_temp": False,
            "step": "WAITING_PHONE",
            "driver_ready": False,
            "error": None
        })
        user_sessions[chat_id] = session

        bot.answer_callback_query(call.id, f"Profile: {prof_name}")
        bot.edit_message_text(
            f"📁 **Fixed Profile:** `{prof_name}`\n"
            f"Manokatra ny tranonkala amin'ny takelaka vaovao...\n\n"
            f"📱 Ampidiro azafady ny **Laharana finday (N)**:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )
        threading.Thread(target=setup_or_open_tab, args=(chat_id, session["site_url"], prof_path), daemon=True).start()

    elif data == "btn_del_menu":
        profiles = get_user_profiles(chat_id)
        markup = InlineKeyboardMarkup()
        for p in profiles:
            markup.add(InlineKeyboardButton(f"❌ Delete: {p}", callback_data=f"dodel_{p}"))
        markup.add(InlineKeyboardButton("🔙 Back", callback_data="btn_back_to_prof"))
        bot.edit_message_text("🗑️ Safidio ny mombamomba tianao hofafana:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("dodel_"):
        p_name = data.split("dodel_")[1]
        target_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), p_name)
        if os.path.exists(target_path):
            shutil.rmtree(target_path, ignore_errors=True)
        bot.answer_callback_query(call.id, f"Voafafa i {p_name}!")
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_back_to_prof":
        show_profile_menu(chat_id, call.message.message_id)

# ==========================================
# 7. Fikarakarana ny hafatra alefan'ny mpampiasa
# ==========================================
@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_text_inputs(message):
    chat_id = message.chat.id
    session = user_sessions[chat_id]
    step = session.get("step")
    text = message.text.strip()

    if step == "WAITING_NEW_PROFILE_NAME":
        clean_name = "".join([c for c in text if c.isalnum() or c in ('_', '-')]).strip()
        if not clean_name:
            bot.send_message(chat_id, "❌ Misy tarehintsoratra tsy azo ampiasaina. Avereno soratana:")
            return

        user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id), clean_name)
        os.makedirs(user_dir, exist_ok=True)

        session["profile_path"] = user_dir
        session["profile_name"] = clean_name
        session["is_temp"] = False
        session["step"] = "WAITING_PHONE"
        session["driver_ready"] = False
        session["error"] = None

        bot.send_message(
            chat_id,
            f"✅ Voaforona ny mombamomba raikitra `{clean_name}`!\n"
            f"🌐 Manokatra takelaka vaovao...\n\n"
            f"📱 Ampidiro azafady ny **Laharana finday (N)**:",
            parse_mode="Markdown"
        )
        threading.Thread(target=setup_or_open_tab, args=(chat_id, session["site_url"], user_dir), daemon=True).start()

    elif step == "WAITING_PHONE":
        session["phone"] = text
        session["step"] = "WAITING_PASSWORD"
        bot.send_message(
            chat_id,
            f"📱 Laharana voatahiry: `{text}`\n\n"
            f"🔑 Ampidiro azafady ny **Teny miafina (P)**:",
            parse_mode="Markdown"
        )

    elif step == "WAITING_PASSWORD":
        session["password"] = text
        session["step"] = "PROCESSING"

        status_msg = bot.send_message(chat_id, "⏳ Preparing login session in tab... [ ⠋ ]")

        threading.Thread(
            target=execute_login_process,
            args=(chat_id, session["phone"], session["password"], status_msg.message_id),
            daemon=True
        ).start()

if __name__ == "__main__":
    print("[*] Mandefa ny Bot Telegram...")
    bot.infinity_polling()
