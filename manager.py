import os
import sys
import subprocess
import time
import threading
import json
import urllib.request
import uuid
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("MANAGER_NODE")

def install_and_import(package_name, import_name=None):
    if import_name is None: import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8808949150:AAFhSyU5_P98avv-n82URf4JCybbM5YFwhg"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"
SUPER_ADMIN_ID = 8707571669
OWNER_USERNAME = "@MD_NAYEEM_DRX_TM"

user_sessions = {}
active_dashboards = {}
SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

PLATFORMS = {
    "site_amarclub": {"name": "Amar Club", "login": "https://amarclub1.com/#/login", "wingo": "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"},
    "site_dkwin": {"name": "DK Win", "login": "https://dkwin6.com/#/login", "wingo": "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"},
    "site_tigroclub": {"name": "Tigro Club", "login": "https://tigroclub.vip/#/login", "wingo": "https://tigroclub.vip/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"},
    "site_hgnice": {"name": "HG Nice", "login": "https://hgnice.org/#/login", "wingo": "https://hgnice.org/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"},
    "site_kanpur91": {"name": "Kanpur 91", "login": "https://kanpur91.com/#/login", "wingo": "https://kanpur91.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"},
    "site_bdgwinsvip": {"name": "BDG Wins VIP", "login": "https://bdgwinsvip.com/#/login", "wingo": "https://bdgwinsvip.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"}
}

def to_bold(text: str) -> str:
    res = []
    for c in str(text):
        n = ord(c)
        if 65 <= n <= 90: res.append(chr(n + 119743))
        elif 97 <= n <= 122: res.append(chr(n + 119737))
        elif 48 <= n <= 57: res.append(chr(n + 120764))
        else: res.append(c)
    return "".join(res)

def safe_delete_message(chat_id, message_id):
    if not message_id: return
    try: bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception: pass

def firebase_sync_http(path: str, method: str = "GET", payload=None):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=raw_data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            content = resp.read()
            return json.loads(content.decode("utf-8")) if content else None
    except Exception:
        return None

def check_channel_membership(user_id):
    if user_id == SUPER_ADMIN_ID: return True
    try:
        m = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return m.status in ['creator', 'administrator', 'member']
    except Exception: return True

def is_user_pass_valid(chat_id):
    if chat_id == SUPER_ADMIN_ID: return True
    return time.time() < user_sessions.get(chat_id, {}).get("pass_expiry", 0)

# --- কিবোর্ডসমূহ ---
def get_credentials_keyboard(sid, has_phone=False):
    markup = InlineKeyboardMarkup(row_width=2)
    if not has_phone:
        markup.add(
            InlineKeyboardButton(to_bold("NUMBER"), callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(to_bold("PASSWORD"), callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(InlineKeyboardButton(to_bold("PASSWORD"), callback_data=f"ask_pass:{sid}"))
    markup.add(InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold("START"), callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid, t_val=0, s_val=5):
    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold(t_lbl), callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(to_bold(s_lbl), callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(to_bold("START"), callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid, live_bal=0.0, spinner_char="◴"):
    markup = InlineKeyboardMarkup(row_width=2)
    bal_str = f"৳ {float(live_bal):.2f}"
    markup.add(
        InlineKeyboardButton(f"{bal_str}", callback_data="noop"),
        InlineKeyboardButton(to_bold("STATS"), callback_data=f"stats:{sid}")
    )
    markup.add(
        InlineKeyboardButton(to_bold(f"STOP {spinner_char}"), callback_data=f"stop:{sid}"),
        InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}")
    )
    return markup

def get_six_platform_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold("AMAR CLUB"), callback_data="site_amarclub"),
        InlineKeyboardButton(to_bold("DK WIN"), callback_data="site_dkwin")
    )
    markup.add(
        InlineKeyboardButton(to_bold("TIGRO CLUB"), callback_data="site_tigroclub"),
        InlineKeyboardButton(to_bold("HG NICE"), callback_data="site_hgnice")
    )
    markup.add(
        InlineKeyboardButton(to_bold("KANPUR 91"), callback_data="site_kanpur91"),
        InlineKeyboardButton(to_bold("BDG WINS VIP"), callback_data="site_bdgwinsvip")
    )
    return markup

# --- টেলিগ্রাম হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)
    user_sessions.setdefault(chat_id, {})

    if chat_id != SUPER_ADMIN_ID and not check_channel_membership(chat_id):
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(to_bold("JOIN OFFICIAL CHANNEL"), url=CHANNEL_URL),
            InlineKeyboardButton(to_bold("VERIFY MEMBERSHIP"), callback_data="check_channel_joined")
        )
        bot.send_message(chat_id, f"<b>{to_bold('CHANNEL MEMBERSHIP REQUIRED')}</b>\n\nচ্যানেলে যুক্ত হোন:", reply_markup=markup)
        return

    if not is_user_pass_valid(chat_id):
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(to_bold("ENTER PASSKEY"), callback_data="btn_enter_pass"),
            InlineKeyboardButton(to_bold("CONTACT OWNER"), url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")
        )
        bot.send_message(chat_id, f"<b>{to_bold('24-HOUR ACCESS PASSKEY REQUIRED')}</b>", reply_markup=markup)
        return

    bot.send_message(chat_id, f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\nপ্ল্যাটফর্ম বেছে নিন:", reply_markup=get_six_platform_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    if data == "noop":
        bot.answer_callback_query(call.id, "Realtime Live Balance")
        return

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    if action == "check_channel_joined":
        if check_channel_membership(chat_id):
            bot.answer_callback_query(call.id, "Verified!")
            bot.edit_message_text(f"<b>{to_bold('SELECT PLATFORM')}</b>", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_six_platform_keyboard())
        else:
            bot.answer_callback_query(call.id, "You have not joined yet!", show_alert=True)

    elif action == "btn_enter_pass":
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_PASSKEY"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, f"<b>{to_bold('PASSKEY')}</b> কোডটি প্রবেশ করুন:")
        user_sessions[chat_id]["prompt_id"] = pm.message_id

    elif action in PLATFORMS:
        sid = f"{chat_id}_{int(time.time()) % 1000000}"
        p_cfg = PLATFORMS[action]
        user_sessions[chat_id] = {
            "active_sid": sid,
            "site_name": p_cfg["name"],
            "login_url": p_cfg["login"],
            "wingo_url": p_cfg["wingo"],
            "phone": None,
            "password": None,
            "target_profit": 0,
            "total_steps": 5
        }
        card_text = (
            f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
            f"Platform: <b>{p_cfg['name']}</b>\n"
            f"আপনার নম্বর ও পাসওয়ার্ড প্রদান করুন:"
        )
        bot.edit_message_text(card_text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_credentials_keyboard(sid))
        user_sessions[chat_id]["cred_msg_id"] = call.message.message_id

    elif action == "ask_num" and sid:
        user_sessions[chat_id]["input_mode"] = "WAITING_PHONE"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, "<b>Phone Number:</b>")
        user_sessions[chat_id]["prompt_id"] = pm.message_id

    elif action == "ask_pass" and sid:
        user_sessions[chat_id]["input_mode"] = "WAITING_PASS"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, "<b>Password:</b>")
        user_sessions[chat_id]["prompt_id"] = pm.message_id

    elif action == "start_cfg" and sid:
        bot.answer_callback_query(call.id, "Configuring...")
        firebase_sync_http(f"commands/{sid}", "PUT", {"cmd": "NAV_WINGO"})

    elif action == "set_tgt" and sid:
        user_sessions[chat_id]["input_mode"] = "WAITING_TARGET"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, "টার্গেট প্রফিট লিখুন (e.g. 250):")
        user_sessions[chat_id]["prompt_id"] = pm.message_id

    elif action == "set_stp" and sid:
        user_sessions[chat_id]["input_mode"] = "WAITING_STEPS"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, "মার্টিঙ্গেল স্টেপ লিখুন (e.g. 5):")
        user_sessions[chat_id]["prompt_id"] = pm.message_id

    elif action == "run_auto" and sid:
        u = user_sessions.get(chat_id, {})
        tgt = u.get("target_profit", 0)
        stp = u.get("total_steps", 5)
        if tgt <= 0:
            bot.answer_callback_query(call.id, "Target সেট করুন!", show_alert=True)
            return
        bot.answer_callback_query(call.id, "Automation Starting...")
        firebase_sync_http(f"commands/{sid}", "PUT", {"cmd": "START_TRADE", "target": tgt, "steps": stp})

    elif action == "stop" and sid:
        firebase_sync_http(f"commands/{sid}", "PUT", {"cmd": "STOP"})
        bot.answer_callback_query(call.id, "Paused")

    elif action == "cancel" and sid:
        firebase_sync_http(f"commands/{sid}", "PUT", {"cmd": "TERMINATE"})
        bot.answer_callback_query(call.id, "Terminated")
        safe_delete_message(chat_id, call.message.message_id)

@bot.message_handler(func=lambda msg: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_sessions.get(chat_id, {})
    mode = u.get("input_mode")
    sid = u.get("active_sid")

    safe_delete_message(chat_id, message.message_id)
    if u.get("prompt_id"):
        safe_delete_message(chat_id, u["prompt_id"])
        u["prompt_id"] = None

    if mode == "WAITING_PASSKEY":
        if text.startswith("KEY-") or chat_id == SUPER_ADMIN_ID:
            u["pass_expiry"] = time.time() + 86400
            u["input_mode"] = None
            bot.send_message(chat_id, "Passkey Activated!", reply_markup=get_six_platform_keyboard())
        return

    if not sid: return

    if mode == "WAITING_PHONE":
        u["phone"] = text
        u["input_mode"] = None
        bot.edit_message_text(f"<b>NUMBER RECORDED:</b> <code>{text[:3]}****{text[-3:]}</code>\nNow submit Password:",
                              chat_id=chat_id, message_id=u["cred_msg_id"], reply_markup=get_credentials_keyboard(sid, True))

    elif mode == "WAITING_PASS":
        u["password"] = text
        u["input_mode"] = None
        safe_delete_message(chat_id, u.get("cred_msg_id"))
        
        # Worker কে টাস্ক পুশ করা
        task_pkt = {
            "chat_id": chat_id, "session_id": sid, "site_name": u["site_name"],
            "login_url": u["login_url"], "wingo_url": u["wingo_url"],
            "phone": u["phone"], "password": u["password"]
        }
        firebase_sync_http(f"tasks/{sid}", "PUT", task_pkt)
        anim_m = bot.send_message(chat_id, "<b>LOGGING IN</b>\n<code>▰▰▰▱▱▱▱▱ 40% Authenticating...</code>")
        active_dashboards[sid] = {"chat_id": chat_id, "msg_id": anim_m.message_id, "stage": "LOGIN"}

    elif mode == "WAITING_TARGET":
        try:
            u["target_profit"] = float(text)
            u["input_mode"] = None
            msg_id = active_dashboards.get(sid, {}).get("msg_id")
            if msg_id:
                bot.edit_message_text(
                    f"<b>{to_bold('WINGO SETUP')}</b>\nTarget: <code>৳ {u['target_profit']}</code> | Steps: <b>{u['total_steps']}</b>",
                    chat_id=chat_id, message_id=msg_id,
                    reply_markup=get_setup_param_keyboard(sid, u["target_profit"], u["total_steps"])
                )
        except Exception: pass

    elif mode == "WAITING_STEPS":
        try:
            u["total_steps"] = int(text)
            u["input_mode"] = None
            msg_id = active_dashboards.get(sid, {}).get("msg_id")
            if msg_id:
                bot.edit_message_text(
                    f"<b>{to_bold('WINGO SETUP')}</b>\nTarget: <code>৳ {u['target_profit']}</code> | Steps: <b>{u['total_steps']}</b>",
                    chat_id=chat_id, message_id=msg_id,
                    reply_markup=get_setup_param_keyboard(sid, u["target_profit"], u["total_steps"])
                )
        except Exception: pass

# --- ড্যাশবোর্ড আপডেট লুপ (ফায়ারবেস থেকে লাইভ ডাটা সিঙ্ক) ---
def dashboard_sync_loop():
    tick = 0
    while True:
        tick += 1
        time.sleep(2.0)
        spinner = SPINNER_FRAMES[tick % len(SPINNER_FRAMES)]
        for sid, d_info in list(active_dashboards.items()):
            chat_id = d_info["chat_id"]
            msg_id = d_info["msg_id"]
            status_data = firebase_sync_http(f"status/{sid}", "GET")
            if not status_data or not isinstance(status_data, dict):
                continue

            stage = status_data.get("stage")
            live_bal = float(status_data.get("cur_bal", 0.0))

            if stage == "LOGIN_DONE" and d_info.get("stage") != "LOGIN_DONE":
                d_info["stage"] = "LOGIN_DONE"
                bot.edit_message_text(
                    f"<b>{to_bold('LOGIN DONE')}</b>\nAccount verified successfully.\nClick Start to navigate to WinGo:",
                    chat_id=chat_id, message_id=msg_id,
                    reply_markup=get_start_screen_keyboard(sid)
                )

            elif stage == "WINGO_READY" and d_info.get("stage") != "WINGO_READY":
                d_info["stage"] = "WINGO_READY"
                u = user_sessions.get(chat_id, {})
                bot.edit_message_text(
                    f"<b>{to_bold('MARKET READY')}</b>\nLive Balance: <code>৳ {live_bal:.2f}</code>\nSet Target and Steps:",
                    chat_id=chat_id, message_id=msg_id,
                    reply_markup=get_setup_param_keyboard(sid, u.get("target_profit", 0), u.get("total_steps", 5))
                )

            elif stage == "TRADING":
                d_info["stage"] = "TRADING"
                wins = status_data.get("wins", 0)
                losses = status_data.get("losses", 0)
                step = status_data.get("step", 1)
                text = (
                    f"<b>{to_bold('24/7 GHOST ENGINE ACTIVE')}</b>\n\n"
                    f"Platform: <b>{status_data.get('site_name', '')}</b>\n"
                    f"Step: <b>Step {step}</b> | Wins: <b>{wins}</b> | Losses: <b>{losses}</b>\n"
                    f"Status: <code>Running...</code>"
                )
                try:
                    bot.edit_message_text(
                        text, chat_id=chat_id, message_id=msg_id,
                        reply_markup=get_trading_control_keyboard(sid, live_bal, spinner)
                    )
                except Exception: pass

            elif stage == "COMPLETED":
                d_info["stage"] = "COMPLETED"
                bot.send_message(
                    chat_id,
                    f"<b>{to_bold('TARGET ACHIEVED')}</b>\nFinal Balance: <code>৳ {live_bal:.2f}</code>"
                )
                active_dashboards.pop(sid, None)

threading.Thread(target=dashboard_sync_loop, daemon=True).start()

if __name__ == "__main__":
    print("[*] Manager Bot Node Active...")
    try: bot.remove_webhook()
    except Exception: pass
    bot.infinity_polling(skip_pending=True)
