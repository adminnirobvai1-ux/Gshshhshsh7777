import os
import sys
import subprocess
import time
import threading
import json
import base64
import tempfile

# ==============================================================================
# 1. AUTOMATIC PACKAGE INSTALLER & ENVIRONMENT BOOTSTRAP
# ==============================================================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Bootstrapping dependency: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except Exception as err:
            print(f"[!] Package install error: {err}")

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("requests")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import requests

# ==============================================================================
# 2. CONFIGURATION & CLUSTER CONSTANTS
# ==============================================================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
OWNER_ID = 8707571669

PAYMENT_BKASH = "01870829343"
PAYMENT_NAGAD = "01876685711"
COMMUNITY_CHANNELS = ["https://t.me/DARK67HACK", "https://t.me/bdwin24_bd"]

FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

NODE_HEARTBEAT_TIMEOUT = 30  # Seconds before considering a worker node OFFLINE
SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

user_state = {}
active_user_sessions = {}
session_locks = {}

# ==============================================================================
# 3. MATHEMATICAL BOLD UNICODE & FORMATTING ENGINE
# ==============================================================================
def to_bold(text: str) -> str:
    res = []
    for c in str(text):
        n = ord(c)
        if 65 <= n <= 90:      # A-Z
            res.append(chr(n + 119743))
        elif 97 <= n <= 122:   # a-z
            res.append(chr(n + 119737))
        elif 48 <= n <= 57:    # 0-9
            res.append(chr(n + 120764))
        else:
            res.append(c)
    return "".join(res)

def safe_delete_message(chat_id, message_id):
    if not message_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ==============================================================================
# 4. FIREBASE REALTIME DATABASE CLIENT (REST API WRAPPER)
# ==============================================================================
class FirebaseDBClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        clean_path = path.strip('/')
        return f"{self.base_url}/{clean_path}.json"

    def get(self, path: str):
        try:
            resp = self.session.get(self._url(path), timeout=8)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception as ex:
            print(f"[Firebase GET Error] {path}: {ex}")
            return None

    def put(self, path: str, data):
        try:
            resp = self.session.put(self._url(path), json=data, timeout=8)
            return resp.status_code in [200, 204]
        except Exception as ex:
            print(f"[Firebase PUT Error] {path}: {ex}")
            return False

    def patch(self, path: str, data):
        try:
            resp = self.session.patch(self._url(path), json=data, timeout=8)
            return resp.status_code in [200, 204]
        except Exception as ex:
            print(f"[Firebase PATCH Error] {path}: {ex}")
            return False

    def delete(self, path: str):
        try:
            resp = self.session.delete(self._url(path), timeout=8)
            return resp.status_code in [200, 204]
        except Exception as ex:
            print(f"[Firebase DELETE Error] {path}: {ex}")
            return False

db = FirebaseDBClient(FIREBASE_DATABASE_URL)

# ==============================================================================
# 5. DYNAMIC LOAD BALANCER & CLUSTER ORCHESTRATOR
# ==============================================================================
def find_available_idle_node():
    nodes_data = db.get("nodes") or {}
    now = time.time()
    for node_id, info in nodes_data.items():
        if not isinstance(info, dict):
            continue
        status = info.get("status", "OFFLINE")
        last_hb = info.get("last_heartbeat", 0)
        is_fresh = (now - last_hb) <= NODE_HEARTBEAT_TIMEOUT
        if status == "IDLE" and is_fresh:
            return node_id, info
    return None, None

def dispatch_task_to_node(node_id: str, payload: dict) -> bool:
    task_path = f"tasks/{node_id}"
    ok = db.put(task_path, payload)
    if ok:
        db.patch(f"nodes/{node_id}", {
            "status": "BUSY",
            "current_chat_id": payload.get("chat_id"),
            "active_site": payload.get("site")
        })
    return ok

def stop_task_on_node(node_id: str, chat_id: int):
    db.put(f"tasks/{node_id}", {
        "action": "STOP",
        "chat_id": chat_id,
        "timestamp": time.time()
    })
    db.patch(f"nodes/{node_id}", {
        "status": "IDLE",
        "current_chat_id": None,
        "active_site": None
    })

# ==============================================================================
# 6. DYNAMIC MULTILINGUAL TEMPLATES
# ==============================================================================
def get_text(chat_id, key, **kwargs):
    u = user_state.get(chat_id, {})
    lang = u.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে ডিস্ট্রিবিউটেড হাই-স্পিড উইনগো ট্রেডিং ক্লাস্টার প্ল্যাটফর্মে।\n"
                f"দয়া করে আপনার পছন্দের ভাষা নির্বাচন করুন:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"আসসালামু আলাইকুম, দয়া করে আপনি আপনার একটি ট্রেডিং সাইট নির্বাচন করুন:"
            ),
            "credentials_card": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"আসসালামু আলাইকুম, দয়া করে নিচের বাটন চেপে আপনার নাম্বার এবং পাসওয়ার্ড দিন। "
                f"এটি সম্পূর্ণ গোপন থাকবে এবং টার্মিনাল লগইন শেষে স্বয়ংক্রিয়ভাবে মুছে যাবে।"
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"আপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:"
            ),
            "node_allocating": (
                f"<b>{to_bold('ALLOCATING CLUSTER WORKER')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"রিমোট ডেডিকেটেড টার্মিনাল বরাদ্দ করা হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন..."
            ),
            "no_nodes_available": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"দুঃখিত! এই মুহূর্তে ক্লাস্টারের সকল রিমোট টার্মিনাল সচল ও ব্যস্ত রয়েছে।\n"
                f"আপনাকে ওয়েটিং কিউতে রাখা হয়েছে। কিছুক্ষণের মধ্যে স্বয়ংক্রিয়ভাবে নোড ফাঁকা হলে যুক্ত করা হবে।"
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Node ID: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"টার্মিনাল লগইন সফল হয়েছে। ট্রেডিং শুরু করতে নিচে <b>START</b> বাটন চাপুন:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'ভুল তথ্য বা টাইমআউট')}</i>\n\n"
                f"পুনরায় চেষ্টা করার জন্য /start চাপুন।"
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"বর্তমান ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"আপনি কত টাকা প্রফিট করতে চান? পরিমাণটি লিখুন (যেমন: <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"টার্গেট প্রফিট: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"মার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখুন (যেমন: <code>7</code> বা <code>10</code>):"
            ),
            "running_dashboard": (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Assigned Worker: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically on dedicated worker node 24/7.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে এবং নোড রিলিজ হয়েছে। নতুন সেশনের জন্য /start পাঠান।"
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"Welcome to the high-performance distributed WinGo Auto-Trading Platform.\n"
                f"Please select your preferred language:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"Please choose your trading platform:"
            ),
            "credentials_card": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"Please click buttons below to provide your Number and Password. "
                f"Credentials will be masked and auto-deleted immediately for security."
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"Enter your account phone number:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"Enter your account password:"
            ),
            "node_allocating": (
                f"<b>{to_bold('ALLOCATING CLUSTER WORKER')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Allocating remote isolated terminal, please wait..."
            ),
            "no_nodes_available": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"All cluster terminals are currently busy running automated sessions.\n"
                f"You have been placed in the waitlist queue."
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Node ID: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login completed. Press <b>START</b> below to configure and run trading:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Invalid credentials or timeout')}</i>\n\n"
                f"Type /start to retry."
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Enter target profit amount (e.g. <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"Target Profit: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"Enter Martingale backup steps (e.g. <code>7</code> or <code>10</code>):"
            ),
            "running_dashboard": (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Assigned Worker: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically on dedicated worker node 24/7.\n"
                f"<b>LIVE STATUS</b>: Martingale engine running smoothly."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser session closed and node released cleanly. Send /start to begin a new session."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==============================================
# 7. INLINE KEYBOARD GENERATORS
# ==============================================
def get_credentials_keyboard(sid):
    sess = active_user_sessions.get(sid, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_user_sessions.get(sid, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_lbl)}", callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(f"{to_bold(s_lbl)}", callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid):
    sess = active_user_sessions.get(sid, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SHOT')}", callback_data=f"shot:{sid}"),
        InlineKeyboardButton(f"{to_bold('BAL')}", callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS')}", callback_data=f"stats:{sid}"),
        InlineKeyboardButton(f"{to_bold(f'STOP {spinner}')}", callback_data=f"stop:{sid}")
    )
    return markup

# ==============================================================================
# 8. OWNER EXCLUSIVE CLUSTER AUDIT & ADMIN PANEL
# ==============================================================================
@bot.message_handler(commands=['admin', 'nodes', 'cluster'])
def handle_admin_dashboard(message):
    chat_id = message.chat.id
    if chat_id != OWNER_ID:
        return

    nodes_data = db.get("nodes") or {}
    now = time.time()

    total_nodes = len(nodes_data)
    active_busy = 0
    idle_free = 0
    offline_count = 0

    node_rows = []
    for node_id, info in nodes_data.items():
        if not isinstance(info, dict):
            continue
        status = info.get("status", "OFFLINE")
        last_hb = info.get("last_heartbeat", 0)
        user_c = info.get("current_chat_id", None)
        active_site = info.get("active_site", "-")

        is_alive = (now - last_hb) <= NODE_HEARTBEAT_TIMEOUT
        if not is_alive:
            status_str = "OFFLINE"
            offline_count += 1
        elif status == "BUSY":
            status_str = "BUSY"
            active_busy += 1
        else:
            status_str = "IDLE"
            idle_free += 1

        if status_str == "BUSY":
            node_rows.append(f"│ Node: {node_id} | Status: BUSY | User: {user_c or 'N/A'}")
        elif status_str == "IDLE":
            node_rows.append(f"│ Node: {node_id} | Status: IDLE | Heartbeat: OK")
        else:
            node_rows.append(f"│ Node: {node_id} | Status: OFFLINE | Lost: {int(now - last_hb)}s ago")

    header_lines = [
        "┌────────────────────────────────────┐",
        "│ CLUSTER TERMINAL STATUS",
        "├────────────────────────────────────┤",
        f"│ Total Registered Nodes: {total_nodes}",
        f"│ Active / Running: {active_busy}",
        f"│ Idle / Free: {idle_free}",
        f"│ Offline: {offline_count}",
        "├────────────────────────────────────┤"
    ]
    if node_rows:
        body_lines = node_rows
    else:
        body_lines = ["│ No worker nodes currently registered."]
    footer_lines = ["└────────────────────────────────────┘"]

    dashboard_text = "\n".join(header_lines + body_lines + footer_lines)
    full_text = f"<b>{to_bold('DISTRIBUTED CLUSTER AUDIT')}</b>\n\n<pre>{dashboard_text}</pre>"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data="admin_refresh"),
        InlineKeyboardButton(f"{to_bold('PURGE OFFLINE')}", callback_data="admin_purge")
    )
    bot.send_message(chat_id, full_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in ["admin_refresh", "admin_purge"])
def handle_admin_actions(call):
    if call.message.chat.id != OWNER_ID:
        return

    if call.data == "admin_purge":
        nodes_data = db.get("nodes") or {}
        now = time.time()
        purged = 0
        for node_id, info in nodes_data.items():
            if isinstance(info, dict):
                last_hb = info.get("last_heartbeat", 0)
                if (now - last_hb) > 120:
                    db.delete(f"nodes/{node_id}")
                    db.delete(f"tasks/{node_id}")
                    purged += 1
        bot.answer_callback_query(call.id, f"Purged {purged} stale nodes.")

    # Refresh
    nodes_data = db.get("nodes") or {}
    now = time.time()
    total_nodes = len(nodes_data)
    active_busy = 0
    idle_free = 0
    offline_count = 0

    node_rows = []
    for node_id, info in nodes_data.items():
        if not isinstance(info, dict):
            continue
        status = info.get("status", "OFFLINE")
        last_hb = info.get("last_heartbeat", 0)
        user_c = info.get("current_chat_id", None)

        is_alive = (now - last_hb) <= NODE_HEARTBEAT_TIMEOUT
        if not is_alive:
            status_str = "OFFLINE"
            offline_count += 1
        elif status == "BUSY":
            status_str = "BUSY"
            active_busy += 1
        else:
            status_str = "IDLE"
            idle_free += 1

        if status_str == "BUSY":
            node_rows.append(f"│ Node: {node_id} | Status: BUSY | User: {user_c or 'N/A'}")
        elif status_str == "IDLE":
            node_rows.append(f"│ Node: {node_id} | Status: IDLE | Heartbeat: OK")
        else:
            node_rows.append(f"│ Node: {node_id} | Status: OFFLINE | Lost: {int(now - last_hb)}s ago")

    header_lines = [
        "┌────────────────────────────────────┐",
        "│ CLUSTER TERMINAL STATUS",
        "├────────────────────────────────────┤",
        f"│ Total Registered Nodes: {total_nodes}",
        f"│ Active / Running: {active_busy}",
        f"│ Idle / Free: {idle_free}",
        f"│ Offline: {offline_count}",
        "├────────────────────────────────────┤"
    ]
    if node_rows:
        body_lines = node_rows
    else:
        body_lines = ["│ No worker nodes currently registered."]
    footer_lines = ["└────────────────────────────────────┘"]

    dashboard_text = "\n".join(header_lines + body_lines + footer_lines)
    full_text = f"<b>{to_bold('DISTRIBUTED CLUSTER AUDIT')}</b>\n\n<pre>{dashboard_text}</pre>"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data="admin_refresh"),
        InlineKeyboardButton(f"{to_bold('PURGE OFFLINE')}", callback_data="admin_purge")
    )
    try:
        bot.edit_message_text(full_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    except Exception:
        pass
    bot.answer_callback_query(call.id)

# ==============================================================================
# 9. TELEGRAM USER INTERACTION ROUTING & DISPATCH FLOW
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_state[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn"
    }

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    bot.send_message(chat_id, get_text(chat_id, "welcome"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: not call.data.startswith("admin_"))
def handle_user_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    if action in ["lang_en", "lang_bn"]:
        u = user_state.setdefault(chat_id, {})
        u["lang"] = "en" if action == "lang_en" else "bn"
        u["step"] = "CHOOSE_SITE"

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
            InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "choose_site"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    elif action in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if action == "site_amarclub" else "DK Win"
        site_slug = "amarclub" if action == "site_amarclub" else "dkwin"
        sid = f"{chat_id}_{int(time.time()) % 1000000}"

        active_user_sessions[sid] = {
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": site_name,
            "site_slug": site_slug,
            "phone": None,
            "password": None,
            "node_id": None,
            "target_profit": 0,
            "total_steps": 7,
            "is_trading": False,
            "created_at": time.time(),
            "anim_tick": 0,
            "live_photo_msg_id": None
        }

        user_state[chat_id]["active_sid"] = sid

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_user_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    elif action == "ask_num" and sid in active_user_sessions:
        active_user_sessions[sid]["input_mode"] = "WAITING_PHONE"
        user_state[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        active_user_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "ask_pass" and sid in active_user_sessions:
        if not active_user_sessions[sid].get("phone"):
            bot.answer_callback_query(
                call.id,
                "দয়া করে আগে আপনার একাউন্ট নাম্বার দিন।",
                show_alert=True
            )
            return

        active_user_sessions[sid]["input_mode"] = "WAITING_PASS"
        user_state[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        active_user_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "start_cfg" and sid in active_user_sessions:
        bot.answer_callback_query(call.id, "উইনগো ৩০এস মার্কেট কনফিগারেশন লোড হচ্ছে...")
        sess = active_user_sessions[sid]
        cur_bal = sess.get("live_balance", 0.0)
        try:
            cur_bal_num = float(cur_bal)
        except Exception:
            cur_bal_num = 0.0

        config_caption = (
            f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Node: <code>{sess.get('node_id', '')}</code>\n"
            f"Live Balance: <code>৳ {cur_bal_num:.2f}</code>\n\n"
            f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
        )
        msg_id = sess.get("live_photo_msg_id")
        if msg_id:
            try:
                bot.edit_message_caption(
                    caption=config_caption,
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=get_setup_param_keyboard(sid)
                )
            except Exception:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        else:
            bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))

    elif action == "set_tgt" and sid in active_user_sessions:
        active_user_sessions[sid]["input_mode"] = "WAITING_TARGET"
        user_state[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_user_sessions[sid].get("live_balance", "0.00")
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=str(cur_bal)))
        active_user_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and sid in active_user_sessions:
        active_user_sessions[sid]["input_mode"] = "WAITING_STEPS"
        user_state[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        tgt = active_user_sessions[sid].get("target_profit", 0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        active_user_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "রিমোট ওয়ার্কার নোডে অটোমেশন সক্রিয় করা হচ্ছে...")
        sess["is_trading"] = True
        node_id = sess.get("node_id")

        if node_id:
            db.put(f"tasks/{node_id}", {
                "action": "START_TRADING",
                "chat_id": chat_id,
                "target_profit": sess["target_profit"],
                "total_steps": sess["total_steps"],
                "timestamp": time.time()
            })

        cur_b_raw = sess.get("live_balance", 0.0)
        try:
            cur_b = float(cur_b_raw)
        except Exception:
            cur_b = 0.0
        sess["start_bal"] = cur_b
        target_total = cur_b + sess["target_profit"]

        dash_caption = get_text(
            chat_id, "running_dashboard",
            site_name=sess.get("site_name", "Amar Club"),
            node_id=node_id or "REMOTE",
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=sess["total_steps"]
        )

        msg_id = sess.get("live_photo_msg_id")
        if msg_id:
            try:
                bot.edit_message_caption(
                    caption=dash_caption,
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=get_trading_control_keyboard(sid)
                )
            except Exception:
                bot.send_message(chat_id, dash_caption, reply_markup=get_trading_control_keyboard(sid))
        else:
            bot.send_message(chat_id, dash_caption, reply_markup=get_trading_control_keyboard(sid))

    elif action == "shot" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        node_id = sess.get("node_id")
        bot.answer_callback_query(call.id, "রিমোট টার্মিনাল থেকে ফুটেজ আপডেট হচ্ছে...")
        if node_id:
            db.put(f"tasks/{node_id}/trigger_shot", time.time())

    elif action == "bal" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        b = sess.get("live_balance", "0.00")
        bot.answer_callback_query(call.id, f"Live Balance: ৳ {b}", show_alert=True)

    elif action == "stats" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        live_s = db.get(f"sessions/{chat_id}") or {}
        w = live_s.get("w", 0)
        l = live_s.get("l", 0)
        step = live_s.get("step", 1)
        stat_txt = (
            f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
            f"Node: <code>{sess.get('node_id', '')}</code>\n"
            f"ব্যালেন্স: <code>৳ {sess.get('live_balance', '0.00')}</code>\n"
            f"টার্গেট: <code>৳ {sess.get('target_profit', 0)}</code>\n"
            f"মার্টিনগেল লেভেল: <b>Step {step}</b>\n"
            f"উইন: <b>{w}</b> | লস: <b>{l}</b>"
        )
        bot.send_message(chat_id, stat_txt)

    elif action == "stop" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        node_id = sess.get("node_id")
        if node_id:
            stop_task_on_node(node_id, chat_id)
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "ট্রেডিং স্থগিত করা হয়েছে", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nরিমোট অটোমেশন ইঞ্জিন সাময়িকভাবে থামানো হয়েছে।")

    elif action == "cancel" and sid in active_user_sessions:
        sess = active_user_sessions[sid]
        node_id = sess.get("node_id")
        if node_id:
            stop_task_on_node(node_id, chat_id)
        db.delete(f"sessions/{chat_id}")
        active_user_sessions.pop(sid, None)
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==============================================================================
# 10. TEXT INPUT HANDLER & WORKER DISPATCHING
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_text_inputs(message):
    chat_id = message.chat.id
    text = message.text.strip()

    u = user_state.get(chat_id, {})
    sid = u.get("active_sid")
    if not sid or sid not in active_user_sessions:
        return

    sess = active_user_sessions[sid]
    input_mode = sess.get("input_mode")

    safe_delete_message(chat_id, message.message_id)

    if sess.get("temp_prompt_id"):
        safe_delete_message(chat_id, sess["temp_prompt_id"])
        sess["temp_prompt_id"] = None

    if input_mode == "WAITING_PHONE":
        sess["phone"] = text
        sess["input_mode"] = None

        if sess.get("cred_card_msg_id"):
            try:
                masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_card_text = (
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"প্ল্যাটফর্ম: <b>{sess.get('site_name', '')}</b>\n"
                    f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                    f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
                )
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=sess["cred_card_msg_id"],
                    reply_markup=get_credentials_keyboard(sid)
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        sess["password"] = text
        sess["input_mode"] = None

        if sess.get("cred_card_msg_id"):
            safe_delete_message(chat_id, sess["cred_card_msg_id"])
            sess["cred_card_msg_id"] = None

        alloc_msg = bot.send_message(chat_id, get_text(chat_id, "node_allocating", site_name=sess["site_name"]))

        node_id, node_info = find_available_idle_node()
        if not node_id:
            safe_delete_message(chat_id, alloc_msg.message_id)
            bot.send_message(chat_id, get_text(chat_id, "no_nodes_available"))
            db.put(f"queue/{chat_id}", {
                "site": sess["site_slug"],
                "phone": sess["phone"],
                "password": sess["password"],
                "timestamp": time.time()
            })
            return

        sess["node_id"] = node_id
        db.put(f"sessions/{chat_id}", {
            "node_id": node_id,
            "status": "CONNECTING",
            "live_balance": "0.00",
            "last_update": time.time()
        })

        payload = {
            "action": "START",
            "chat_id": chat_id,
            "site": sess["site_slug"],
            "phone": sess["phone"],
            "password": sess["password"],
            "timestamp": time.time()
        }
        dispatch_task_to_node(node_id, payload)
        safe_delete_message(chat_id, alloc_msg.message_id)

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0:
                raise ValueError()
            sess["target_profit"] = val
            sess["input_mode"] = None

            cur_bal = sess.get("live_balance", "0.00")
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            msg_id = sess.get("live_photo_msg_id")
            if msg_id:
                try:
                    bot.edit_message_caption(
                        caption=config_caption,
                        chat_id=chat_id,
                        message_id=msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
            else:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            sess["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0:
                raise ValueError()
            sess["total_steps"] = steps_val
            sess["input_mode"] = None

            cur_bal = sess.get("live_balance", "0.00")
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            msg_id = sess.get("live_photo_msg_id")
            if msg_id:
                try:
                    bot.edit_message_caption(
                        caption=config_caption,
                        chat_id=chat_id,
                        message_id=msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
            else:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==============================================================================
# 11. FIREBASE REAL-TIME SESSION BRIDGE & SCREENSHOT DISPATCHER
# ==============================================================================
def session_sync_bridge_loop():
    while True:
        try:
            sessions_data = db.get("sessions") or {}
            for chat_id_str, s_data in sessions_data.items():
                if not isinstance(s_data, dict):
                    continue
                chat_id = int(chat_id_str)
                u = user_state.get(chat_id, {})
                sid = u.get("active_sid")
                if not sid or sid not in active_user_sessions:
                    continue

                sess = active_user_sessions[sid]
                remote_status = s_data.get("status")
                remote_bal = s_data.get("live_balance")
                img_b64 = s_data.get("screenshot_base64")
                err_msg = s_data.get("error_message")

                if remote_bal is not None:
                    sess["live_balance"] = str(remote_bal)

                if remote_status == "ERROR":
                    db.delete(f"sessions/{chat_id}")
                    bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=sess["site_name"], error=err_msg or "Unknown error"))
                    active_user_sessions.pop(sid, None)
                    continue

                if remote_status == "LOGGED_IN" and not sess.get("handshake_done"):
                    sess["handshake_done"] = True
                    phone_masked = sess.get("phone", "")
                    if len(phone_masked) >= 6:
                        phone_masked = phone_masked[:3] + "****" + phone_masked[-3:]

                    caption = get_text(
                        chat_id, "login_success",
                        site_name=sess["site_name"],
                        node_id=sess.get("node_id", ""),
                        phone=phone_masked
                    )
                    kbm = get_start_screen_keyboard(sid)

                    if img_b64:
                        try:
                            img_bytes = base64.b64decode(img_b64)
                            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                                tf.write(img_bytes)
                                tf_path = tf.name

                            with open(tf_path, "rb") as ph:
                                sent_msg = bot.send_photo(chat_id, ph, caption=caption, reply_markup=kbm)
                                sess["live_photo_msg_id"] = sent_msg.message_id
                            os.remove(tf_path)
                        except Exception as ex:
                            print(f"[!] Login photo send err: {ex}")
                            bot.send_message(chat_id, caption, reply_markup=kbm)
                    else:
                        bot.send_message(chat_id, caption, reply_markup=kbm)

                elif remote_status == "RUNNING" and img_b64 and s_data.get("shot_id") != sess.get("last_handled_shot"):
                    sess["last_handled_shot"] = s_data.get("shot_id")
                    cur_b_raw = sess.get("live_balance", "0.00")
                    try:
                        cur_b = float(cur_b_raw)
                    except Exception:
                        cur_b = 0.0
                    target_total = sess.get("start_bal", cur_b) + sess.get("target_profit", 0)

                    caption = (
                        f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                        f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                        f"Node: <code>{sess.get('node_id', '')}</code>\n"
                        f"Live Balance: <code>৳ {cur_b:.2f}</code>\n"
                        f"Target Balance: <code>৳ {target_total:.2f}</code>\n"
                        f"Steps: <b>{sess.get('total_steps', 7)}</b>\n\n"
                        f"Time: <code>{time.strftime('%H:%M:%S')}</code>\n"
                        f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
                    )
                    try:
                        img_bytes = base64.b64decode(img_b64)
                        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
                            tf.write(img_bytes)
                            tf_path = tf.name

                        msg_id = sess.get("live_photo_msg_id")
                        if msg_id:
                            with open(tf_path, "rb") as ph:
                                bot.edit_message_media(
                                    media=InputMediaPhoto(ph, caption=caption, parse_mode="HTML"),
                                    chat_id=chat_id,
                                    message_id=msg_id,
                                    reply_markup=get_trading_control_keyboard(sid)
                                )
                        else:
                            with open(tf_path, "rb") as ph:
                                m = bot.send_photo(chat_id, ph, caption=caption, reply_markup=get_trading_control_keyboard(sid))
                                sess["live_photo_msg_id"] = m.message_id
                        os.remove(tf_path)
                    except Exception as ex:
                        print(f"[!] Edit media error: {ex}")

                elif remote_status == "TARGET_REACHED":
                    sess["is_trading"] = False
                    start_b = sess.get("start_bal", 0.0)
                    cur_b = float(sess.get("live_balance", 0.0))
                    profit = cur_b - start_b

                    msg = (
                        f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                        f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
                        f"শুরুর ব্যালেন্স: <code>৳ {start_b:.2f}</code>\n"
                        f"বর্তমান ব্যালেন্স: <code>৳ {cur_b:.2f}</code>\n"
                        f"অর্জিত প্রফিট: <code>+৳ {profit:.2f}</code>\n"
                        f"মোট উইন: <b>{s_data.get('w', 0)}</b> | লস: <b>{s_data.get('l', 0)}</b>"
                    )
                    bot.send_message(chat_id, msg)
                    db.delete(f"sessions/{chat_id}")

        except Exception as ex:
            print(f"[Bridge Loop Error]: {ex}")
        time.sleep(2.5)

threading.Thread(target=session_sync_bridge_loop, daemon=True).start()

# ==============================================================================
# 12. CONTINUOUS 24-HOUR LIFETIME WATCHDOG
# ==============================================================================
def continuous_24h_watchdog():
    while True:
        try:
            now = time.time()
            for sid, item in list(active_user_sessions.items()):
                created_at = item.get("created_at", now)
                if now - created_at >= 86400:
                    print(f"[*] 24-hour lifetime reached for session: {sid}")
                    node_id = item.get("node_id")
                    chat_id = item.get("chat_id")
                    if node_id:
                        stop_task_on_node(node_id, chat_id)
                    db.delete(f"sessions/{chat_id}")
                    active_user_sessions.pop(sid, None)
        except Exception:
            pass
        time.sleep(1800)

threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

# ==============================================================================
# 13. MASTER CONTROLLER ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("=" * 65)
    print(f"[*] {to_bold('WINGO 30S DISTRIBUTED MASTER CONTROLLER ACTIVE')}")
    print(f"[*] Cluster Database: {FIREBASE_DATABASE_URL}")
    print(f"[*] Owner Telegram ID: {OWNER_ID}")
    print("=" * 65)
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
