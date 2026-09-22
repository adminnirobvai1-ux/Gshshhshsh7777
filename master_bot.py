import os
import sys
import subprocess
import time
import threading
import json
import base64
from io import BytesIO
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse

# ==========================================
# 1. Automatic Package Installer
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing package: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("requests")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

# ==========================================
# 2. Mathematical Bold Unicode & System Utils
# ==========================================
def to_bold(text: str) -> str:
    res = []
    for c in str(text):
        n = ord(c)
        if 65 <= n <= 90:
            res.append(chr(n + 119743))
        elif 97 <= n <= 122:
            res.append(chr(n + 119737))
        elif 48 <= n <= 57:
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

# ==========================================
# 3. Master Configurations & Tokens
# ==========================================
TOKEN = "8808949150:AAGehY-s2kZKblgZtYqwtsCiDRypLx8O8hU"
OWNER_ID = 8707571669
MASTER_SERVER_PORT = 8080

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==========================================
# 4. In-Memory Internal Cluster Database
# (মাস্টার রিস্টার্ট হলে এটি সম্পূর্ণ নতুনভাবে শুরু হবে)
# ==========================================
class ClusterDatabase:
    def __init__(self):
        self.lock = threading.RLock()
        self.nodes = {}       # node_id -> {status, last_heartbeat, current_chat_id, ip}
        self.tasks = {}       # node_id -> task_payload
        self.sessions = {}    # chat_id -> session_data
        self.user_states = {} # chat_id -> user UI state

    def register_node(self, node_id, ip=""):
        with self.lock:
            self.nodes[node_id] = {
                "status": "FREE",
                "last_heartbeat": time.time(),
                "current_chat_id": None,
                "ip": ip
            }
            if node_id not in self.tasks:
                self.tasks[node_id] = None

    def heartbeat(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["last_heartbeat"] = time.time()

    def get_idle_node(self):
        with self.lock:
            now = time.time()
            for nid, data in self.nodes.items():
                if data["status"] == "FREE" and (now - data["last_heartbeat"]) <= 35:
                    return nid
            return None

    def assign_task(self, node_id, chat_id, action, payload=None):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "USED"
                self.nodes[node_id]["current_chat_id"] = chat_id
            task_data = {
                "action": action,
                "chat_id": chat_id,
                "timestamp": int(time.time())
            }
            if payload:
                task_data.update(payload)
            self.tasks[node_id] = task_data

    def pop_task(self, node_id):
        with self.lock:
            task = self.tasks.get(node_id)
            self.tasks[node_id] = None
            return task

    def update_session(self, chat_id, data):
        with self.lock:
            if chat_id not in self.sessions:
                self.sessions[chat_id] = {}
            self.sessions[chat_id].update(data)
            self.sessions[chat_id]["last_update"] = time.time()

    def release_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "FREE"
                self.nodes[node_id]["current_chat_id"] = None
            self.tasks[node_id] = None

db = ClusterDatabase()

# ==========================================
# 5. Internal Multithreaded Master HTTP API Server
# ==========================================
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

class MasterAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

        path = self.path

        if path == "/api/register":
            node_id = data.get("node_id")
            if node_id:
                client_ip = self.client_address[0]
                db.register_node(node_id, client_ip)
                self._send_json(200, {"success": True, "message": "Registered successfully"})
                return

        elif path == "/api/heartbeat":
            node_id = data.get("node_id")
            if node_id:
                db.heartbeat(node_id)
                self._send_json(200, {"success": True})
                return

        elif path == "/api/update_session":
            chat_id = data.get("chat_id")
            session_payload = data.get("session_data", {})
            if chat_id:
                db.update_session(chat_id, session_payload)
                self._send_json(200, {"success": True})
                return

        elif path == "/api/release":
            node_id = data.get("node_id")
            if node_id:
                db.release_node(node_id)
                self._send_json(200, {"success": True})
                return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/get_task":
            node_id = params.get("node_id", [None])[0]
            if node_id:
                db.heartbeat(node_id)
                task = db.pop_task(node_id)
                self._send_json(200, {"task": task})
                return

        self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        return # টার্মিনাল লগ পরিষ্কার রাখার জন্য অফ রাখা হলো

def start_master_api_server():
    server = ThreadedHTTPServer(("0.0.0.0", MASTER_SERVER_PORT), MasterAPIHandler)
    print(f"[*] Internal Cluster Master Server listening on port {MASTER_SERVER_PORT}...")
    server.serve_forever()

threading.Thread(target=start_master_api_server, daemon=True).start()

# ==========================================
# 6. Dynamic Multilingual Templates (100% Preserved)
# ==========================================
SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

def get_text(chat_id, key, **kwargs):
    sess = db.user_states.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে প্রিমিয়াম উইনগো ট্রেডিং অটোমেশন প্ল্যাটফর্মে।\n"
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
                f"এটি সম্পূর্ণ গোপন থাকবে এবং কাজ শেষে চ্যাট থেকে মুছে যাবে।"
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"আপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:"
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং শুরু করতে নিচে <b>START</b> বাটন চাপুন:"
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
                f"Terminal Node: <code>{kwargs.get('node_id', 'N/A')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে। নতুন সেশনের জন্য /start পাঠান।"
            ),
            "cluster_busy": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"দুঃখিত, এই মুহূর্তে ক্লাস্টারের সকল ডিভাইস ও টার্মিনাল ব্যস্ত আছে। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"Welcome to the high-tech WinGo Auto-Trading Platform.\n"
                f"Please choose your preferred language:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"Please select your trading platform:"
            ),
            "credentials_card": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Please click buttons below to provide your Number and Password. "
                f"Credentials will be hidden and auto-deleted immediately for security."
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"Enter your account phone number:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"Enter your account password:"
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login completed. Press <b>START</b> below to configure and run trading:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Invalid credentials')}</i>\n\n"
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
                f"Terminal Node: <code>{kwargs.get('node_id', 'N/A')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: Martingale engine running smoothly."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser session closed cleanly. Send /start to begin a new session."
            ),
            "cluster_busy": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"All cluster terminals are currently busy. Please try again shortly."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==========================================
# 7. Interactive Control Keyboards
# ==========================================
def get_credentials_keyboard(chat_id):
    sess = db.user_states.get(chat_id, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data="btn_ask_num"),
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data="btn_ask_pass")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data="btn_ask_pass")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="btn_cancel"))
    return markup

def get_start_screen_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data="btn_start_cfg"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="btn_cancel")
    )
    return markup

def get_setup_param_keyboard(chat_id):
    sess = db.user_states.get(chat_id, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_lbl)}", callback_data="btn_set_tgt"),
        InlineKeyboardButton(f"{to_bold(s_lbl)}", callback_data="btn_set_stp")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data="btn_run_auto"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="btn_cancel")
    )
    return markup

def get_trading_control_keyboard(chat_id):
    sess = db.user_states.get(chat_id, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SHOT')}", callback_data="btn_shot"),
        InlineKeyboardButton(f"{to_bold('BAL')}", callback_data="btn_bal")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS')}", callback_data="btn_stats"),
        InlineKeyboardButton(f"{to_bold(f'STOP {spinner}')}", callback_data="btn_stop")
    )
    return markup

# ==========================================
# 8. Realtime Photo Bridge & Relay Engine
# ==========================================
def display_or_replace_photo(chat_id, image_bytes, caption_text, reply_markup=None):
    sess = db.user_states.get(chat_id, {})
    last_photo_msg_id = sess.get("live_photo_message_id")
    replaced = False

    if last_photo_msg_id:
        try:
            bio = BytesIO(image_bytes)
            bio.name = 'screen.png'
            media = InputMediaPhoto(bio, caption=caption_text, parse_mode="HTML")
            bot.edit_message_media(
                media=media,
                chat_id=chat_id,
                message_id=last_photo_msg_id,
                reply_markup=reply_markup
            )
            replaced = True
        except Exception:
            replaced = False

    if not replaced:
        try:
            bio = BytesIO(image_bytes)
            bio.name = 'screen.png'
            msg = bot.send_photo(
                chat_id, bio,
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            sess["live_photo_message_id"] = msg.message_id
        except Exception as e:
            print(f"[*] Photo display error: {e}")

def monitor_session_updates(chat_id):
    last_status = None
    while True:
        sess = db.user_states.get(chat_id)
        if not sess or sess.get("step") == "TERMINATED":
            break

        session_data = db.sessions.get(chat_id)
        if session_data:
            status = session_data.get("status")
            node_id = session_data.get("node_id", "N/A")
            live_bal = session_data.get("live_balance", "0.00")
            b64_img = session_data.get("screenshot_base64")
            err_msg = session_data.get("error_message")

            if status == "LOGIN_SUCCESS" and last_status != "LOGIN_SUCCESS":
                last_status = "LOGIN_SUCCESS"
                masked = sess.get("phone", "")
                if len(masked) >= 6:
                    masked = masked[:3] + "****" + masked[-3:]
                cap = get_text(chat_id, "login_success", site_name=sess.get("site_name"), phone=masked)
                if b64_img:
                    display_or_replace_photo(chat_id, base64.b64decode(b64_img), cap, get_start_screen_keyboard())
                else:
                    bot.send_message(chat_id, cap, reply_markup=get_start_screen_keyboard())

            elif status == "LOGIN_FAILED":
                bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=sess.get("site_name"), error=err_msg))
                sess["step"] = "TERMINATED"
                db.sessions.pop(chat_id, None)
                break

            elif status == "WINGO_READY" and last_status != "WINGO_READY":
                last_status = "WINGO_READY"
                sess["current_balance"] = float(live_bal) if live_bal else 0.0
                cap = (
                    f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name')}</b>\n"
                    f"Live Balance: <code>৳ {sess['current_balance']:.2f}</code>\n\n"
                    f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
                )
                if b64_img:
                    display_or_replace_photo(chat_id, base64.b64decode(b64_img), cap, get_setup_param_keyboard(chat_id))
                else:
                    bot.send_message(chat_id, cap, reply_markup=get_setup_param_keyboard(chat_id))

            elif status == "RUNNING" and (sess.get("force_refresh") or last_status != "RUNNING"):
                sess["force_refresh"] = False
                last_status = "RUNNING"
                t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
                cap = get_text(
                    chat_id, "running_dashboard",
                    site_name=sess.get("site_name"),
                    node_id=node_id,
                    start_bal=f"{sess.get('start_bal', 0.0):.2f}",
                    target_bal=f"{t_total:.2f}",
                    steps=sess.get("total_steps", 7)
                )
                if b64_img:
                    display_or_replace_photo(chat_id, base64.b64decode(b64_img), cap, get_trading_control_keyboard(chat_id))

            elif status == "TARGET_ACHIEVED":
                last_status = "TARGET_ACHIEVED"
                start_b = sess.get("start_bal", 0.0)
                cur_b = float(live_bal) if live_bal else start_b
                profit = cur_b - start_b
                msg = (
                    f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                    f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
                    f"শুরুর ব্যালেন্স: <code>৳ {start_b:.2f}</code>\n"
                    f"বর্তমান ব্যালেন্স: <code>৳ {cur_b:.2f}</code>\n"
                    f"অর্জিত প্রফিট: <code>+৳ {profit:.2f}</code>"
                )
                if b64_img:
                    display_or_replace_photo(chat_id, base64.b64decode(b64_img), msg, None)
                else:
                    bot.send_message(chat_id, msg)
                sess["step"] = "TERMINATED"
                break

            elif status == "STOPPED":
                bot.send_message(chat_id, get_text(chat_id, "cancelled"))
                sess["step"] = "TERMINATED"
                db.sessions.pop(chat_id, None)
                break

        time.sleep(3)

# ==========================================
# 9. Telegram Commands & Exclusive Owner Admin Panel
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    db.user_states[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn"
    }

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    bot.send_message(chat_id, get_text(chat_id, "welcome"), reply_markup=markup)

@bot.message_handler(commands=['admin', 'nodes'])
def handle_admin_panel(message):
    if message.chat.id != OWNER_ID:
        return

    now = time.time()
    total_count = len(db.nodes)
    used_count = 0
    free_count = 0
    offline_count = 0
    lines = []

    for nid, nd in db.nodes.items():
        st = nd.get("status", "OFFLINE")
        last_hb = nd.get("last_heartbeat", 0)
        diff = int(now - last_hb)
        is_active = diff <= 35
        c_chat = nd.get("current_chat_id")

        if st == "USED" and is_active:
            used_count += 1
            lines.append(f"│ Node: {nid:<8} │ Status: USED    │ User: {c_chat}")
        elif is_active:
            free_count += 1
            lines.append(f"│ Node: {nid:<8} │ Status: FREE    │ Heartbeat: OK")
        else:
            offline_count += 1
            lines.append(f"│ Node: {nid:<8} │ Status: OFFLINE │ Seen: {diff}s ago")

    if not lines:
        lines.append("│ No terminal nodes registered yet.                        │")

    report = (
        "┌────────────────────────────────────────────────────────┐\n"
        "│ CLUSTER TERMINAL CONTROLLER                            │\n"
        "├────────────────────────────────────────────────────────┤\n"
        f"│ TOTAL DEVICES     : {total_count:<34} │\n"
        f"│ RUNNING / USED    : {used_count:<34} │\n"
        f"│ IDLE / FREE       : {free_count:<34} │\n"
        f"│ OFFLINE           : {offline_count:<34} │\n"
        "├────────────────────────────────────────────────────────┤\n"
        "│ TERMINAL DETAILED AUDIT:                               │\n"
        + "\n".join(lines) + "\n"
        "└────────────────────────────────────────────────────────┘"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"{to_bold('REFRESH PANEL')}", callback_data="admin_refresh"))
    bot.send_message(OWNER_ID, f"<code>{report}</code>", reply_markup=markup)

# ==========================================
# 10. Telegram Callbacks Handler
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    sess = db.user_states.setdefault(chat_id, {})

    if data == "admin_refresh":
        if chat_id == OWNER_ID:
            handle_admin_panel(call.message)
            bot.answer_callback_query(call.id, "Refreshed")
        return

    # Language selection
    if data in ["lang_en", "lang_bn"]:
        sess["lang"] = "en" if data == "lang_en" else "bn"
        sess["step"] = "CHOOSE_SITE"
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

    # Site selection
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        sess["site_name"] = site_name
        sess["site_code"] = "amarclub" if data == "site_amarclub" else "dkwin"
        sess["phone"] = None
        sess["password"] = None
        sess["step"] = "CREDENTIALS"

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(chat_id)
        )
        sess["cred_card_msg_id"] = call.message.message_id

    # Phone input mode
    elif data == "btn_ask_num":
        sess["input_mode"] = "WAITING_PHONE"
        bot.answer_callback_query(call.id)
        p = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        sess["temp_prompt_id"] = p.message_id

    # Password input mode
    elif data == "btn_ask_pass":
        if not sess.get("phone"):
            bot.answer_callback_query(call.id, "আগে নাম্বার প্রদান করুন!", show_alert=True)
            return
        sess["input_mode"] = "WAITING_PASS"
        bot.answer_callback_query(call.id)
        p = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        sess["temp_prompt_id"] = p.message_id

    # Start WinGo configuration
    elif data == "btn_start_cfg":
        node_id = sess.get("assigned_node")
        if node_id:
            bot.answer_callback_query(call.id, "উইনগো ৩০এস পেজ প্রস্তুত করা হচ্ছে...")
            db.assign_task(node_id, chat_id, "PREPARE_WINGO")

    # Set Target
    elif data == "btn_set_tgt":
        sess["input_mode"] = "WAITING_TARGET"
        bot.answer_callback_query(call.id)
        cur_bal = sess.get("current_balance", 0.0)
        p = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{cur_bal:.2f}"))
        sess["temp_prompt_id"] = p.message_id

    # Set Steps
    elif data == "btn_set_stp":
        sess["input_mode"] = "WAITING_STEPS"
        bot.answer_callback_query(call.id)
        tgt = sess.get("target_profit", 0)
        p = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        sess["temp_prompt_id"] = p.message_id

    # Run automation
    elif data == "btn_run_auto":
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return
        node_id = sess.get("assigned_node")
        if node_id:
            bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় করা হচ্ছে...")
            sess["start_bal"] = sess.get("current_balance", 0.0)
            db.assign_task(node_id, chat_id, "RUN_AUTOMATION", {
                "target_profit": sess["target_profit"],
                "total_steps": sess.get("total_steps", 7)
            })

    # Fetch shot
    elif data == "btn_shot":
        node_id = sess.get("assigned_node")
        if node_id:
            bot.answer_callback_query(call.id, "ফুটেজ আপডেট হচ্ছে...")
            sess["force_refresh"] = True
            db.assign_task(node_id, chat_id, "FETCH_SHOT")

    # Balance check
    elif data == "btn_bal":
        s_data = db.sessions.get(chat_id)
        b_val = s_data.get("live_balance", "0.00") if s_data else "0.00"
        bot.answer_callback_query(call.id, f"Live Balance: ৳ {b_val}", show_alert=True)

    # Live stats report
    elif data == "btn_stats":
        s_data = db.sessions.get(chat_id)
        if s_data and s_data.get("stats"):
            st = s_data["stats"]
            stat_txt = (
                f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                f"ব্যালেন্স: <code>৳ {s_data.get('live_balance', '0.00')}</code>\n"
                f"টার্গেট: <code>৳ {st.get('tgtAmt', 0):.2f}</code>\n"
                f"মার্টিনগেল লেভেল: <b>Step {st.get('step', 1)}/{st.get('maxStep', 7)}</b>\n"
                f"উইন: <b>{st.get('w', 0)}</b> | লস: <b>{st.get('l', 0)}</b>"
            )
            bot.send_message(chat_id, stat_txt)
        else:
            bot.answer_callback_query(call.id, "পরিসংখ্যান সিঙ্ক হচ্ছে...", show_alert=True)

    # Stop trading
    elif data == "btn_stop":
        node_id = sess.get("assigned_node")
        if node_id:
            bot.answer_callback_query(call.id, "ট্রেডিং স্থগিত করা হচ্ছে...", show_alert=True)
            db.assign_task(node_id, chat_id, "STOP_TRADING")

    # Cancel session
    elif data == "btn_cancel":
        node_id = sess.get("assigned_node")
        if node_id:
            db.assign_task(node_id, chat_id, "TERMINATE")
        sess["step"] = "TERMINATED"
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==========================================
# 11. Text Handler & Auto Credential Cleanup
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_input(message):
    chat_id = message.chat.id
    text = message.text.strip()
    sess = db.user_states.get(chat_id)

    if not sess:
        return

    mode = sess.get("input_mode")
    safe_delete_message(chat_id, message.message_id)

    if sess.get("temp_prompt_id"):
        safe_delete_message(chat_id, sess["temp_prompt_id"])
        sess["temp_prompt_id"] = None

    if mode == "WAITING_PHONE":
        sess["phone"] = text
        sess["input_mode"] = None
        masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
        if sess.get("cred_card_msg_id"):
            bot.edit_message_text(
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{sess.get('site_name', '')}</b>\n"
                f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:",
                chat_id=chat_id,
                message_id=sess["cred_card_msg_id"],
                reply_markup=get_credentials_keyboard(chat_id)
            )

    elif mode == "WAITING_PASS":
        sess["password"] = text
        sess["input_mode"] = None

        if sess.get("cred_card_msg_id"):
            safe_delete_message(chat_id, sess["cred_card_msg_id"])
            sess["cred_card_msg_id"] = None

        target_node = db.get_idle_node()
        if not target_node:
            bot.send_message(chat_id, get_text(chat_id, "cluster_busy"))
            return

        sess["assigned_node"] = target_node
        db.update_session(chat_id, {
            "node_id": target_node,
            "status": "ALLOCATED",
            "live_balance": "0.00"
        })

        bot.send_message(
            chat_id,
            f"<b>ALLOCATED CLUSTER TERMINAL:</b> <code>{target_node}</code>\n"
            f"<i>Connecting remote browser engine...</i>"
        )

        db.assign_task(target_node, chat_id, "LOGIN", {
            "site": sess["site_code"],
            "phone": sess["phone"],
            "password": sess["password"]
        })

        threading.Thread(target=monitor_session_updates, args=(chat_id,), daemon=True).start()

    elif mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            sess["target_profit"] = val
            sess["input_mode"] = None
            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(chat_id))
        except ValueError:
            p = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            sess["temp_prompt_id"] = p.message_id

    elif mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            sess["total_steps"] = steps_val
            sess["input_mode"] = None
            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(chat_id))
        except ValueError:
            p = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            sess["temp_prompt_id"] = p.message_id

# ==========================================
# 12. Main Execution
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP MASTER ORCHESTRATOR ONLINE')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)`12
