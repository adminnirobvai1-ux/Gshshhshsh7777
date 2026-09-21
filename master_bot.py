import os
import sys
import subprocess
import time
import threading
import json
import base64
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

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
# 3. Master Configurations & Central State
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
OWNER_ID = 8707571669
HUB_HOST = "0.0.0.0"
HUB_PORT = 8080

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ইন-মেমরি সেন্ট্রাল ক্লাস্টার ডাটাবেস (রিস্টার্ট দিলে ফ্রেশ নতুন ডাটাবেস তৈরি হবে)
db_lock = threading.RLock()
cluster_nodes = {}     # node_id -> {status, last_heartbeat, chat_id, site_name, ip}
cluster_tasks = {}     # node_id -> task dictionary
cluster_sessions = {}  # chat_id -> session state
user_flow = {}         # chat_id -> temp UI input state

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# ==========================================
# 4. Built-in Central Hub Server (REST API)
# ==========================================
class CentralHubRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # টার্মিনাল পরিষ্কার রাখার জন্য ডিফল্ট লগ অফ

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception:
            payload = {}

        # ১. ওয়ার্কার রেজিস্ট্রেশন
        if parsed_path.path == "/api/node/register":
            node_id = payload.get("node_id")
            with db_lock:
                cluster_nodes[node_id] = {
                    "status": "IDLE",
                    "last_heartbeat": time.time(),
                    "chat_id": None,
                    "site_name": None,
                    "ip": self.client_address[0]
                }
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "REGISTERED", "node_id": node_id}).encode('utf-8'))

        # ২. ওয়ার্কার হার্টবিট
        elif parsed_path.path == "/api/node/heartbeat":
            node_id = payload.get("node_id")
            status = payload.get("status", "IDLE")
            with db_lock:
                if node_id in cluster_nodes:
                    cluster_nodes[node_id]["last_heartbeat"] = time.time()
                    if cluster_nodes[node_id]["status"] != "USED":
                        cluster_nodes[node_id]["status"] = status
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "ALIVE"}).encode('utf-8'))

        # ৩. লাইভ সেশন ও স্ক্রিনশট রিসিভ
        elif parsed_path.path == "/api/session/update":
            chat_id = payload.get("chat_id")
            node_id = payload.get("node_id")
            status = payload.get("status")
            live_bal = payload.get("live_balance", 0.0)
            screenshot_b64 = payload.get("screenshot_base64")
            caption_text = payload.get("caption")

            if chat_id and chat_id in cluster_sessions:
                sess = cluster_sessions[chat_id]
                sess["current_balance"] = live_bal
                sess["status"] = status

                if screenshot_b64:
                    try:
                        img_bytes = base64.b64decode(screenshot_b64)
                        media = InputMediaPhoto(img_bytes, caption=caption_text, parse_mode="HTML")
                        last_msg_id = sess.get("live_photo_msg_id")

                        if last_msg_id:
                            bot.edit_message_media(
                                media=media,
                                chat_id=chat_id,
                                message_id=last_msg_id,
                                reply_markup=get_trading_control_keyboard(chat_id)
                            )
                        else:
                            msg = bot.send_photo(
                                chat_id,
                                img_bytes,
                                caption=caption_text,
                                reply_markup=get_trading_control_keyboard(chat_id),
                                parse_mode="HTML"
                            )
                            sess["live_photo_msg_id"] = msg.message_id
                    except Exception as ex:
                        print(f"[*] Update error for chat {chat_id}: {ex}")

            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "UPDATED"}).encode('utf-8'))

        # ৪. সেশন সম্পন্ন / টার্মিনেটেড
        elif parsed_path.path == "/api/session/completed":
            node_id = payload.get("node_id")
            chat_id = payload.get("chat_id")
            with db_lock:
                if node_id in cluster_nodes:
                    cluster_nodes[node_id]["status"] = "IDLE"
                    cluster_nodes[node_id]["chat_id"] = None
                cluster_tasks.pop(node_id, None)
                cluster_sessions.pop(chat_id, None)
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "CLEARED"}).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "NOT_FOUND"}).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        # ওয়ার্কারের নতুন টাস্ক চেক
        if parsed_path.path == "/api/task/poll":
            node_id = params.get("node_id", [None])[0]
            with db_lock:
                task = cluster_tasks.get(node_id)
            self._set_headers(200)
            self.wfile.write(json.dumps(task if task else {}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "NOT_FOUND"}).encode('utf-8'))

def start_central_hub_server():
    server = HTTPServer((HUB_HOST, HUB_PORT), CentralHubRequestHandler)
    print(f"[*] Central Hub REST Server active on {HUB_HOST}:{HUB_PORT}")
    server.serve_forever()

threading.Thread(target=start_central_hub_server, daemon=True).start()

# ==========================================
# 5. Smart Load Balancer Engine
# ==========================================
def find_best_idle_node():
    now = time.time()
    with db_lock:
        for node_id, data in cluster_nodes.items():
            if data["status"] == "IDLE" and (now - data["last_heartbeat"]) <= 30:
                return node_id
    return None

def dispatch_task_to_node(node_id, task_payload):
    with db_lock:
        cluster_nodes[node_id]["status"] = "USED"
        cluster_nodes[node_id]["chat_id"] = task_payload["chat_id"]
        cluster_nodes[node_id]["site_name"] = task_payload["site_name"]
        cluster_tasks[node_id] = task_payload

# ==========================================
# 6. Dynamic Multilingual Templates
# ==========================================
def get_text(chat_id, key, **kwargs):
    u = user_flow.get(chat_id, {})
    lang = u.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে প্রিমিয়াম উইনগো ডিস্ট্রিবিউটেড ট্রেডিং ক্লাস্টারে।\n"
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
                f"এটি এনক্রিপ্ট হয়ে সম্পূর্ণ গোপন থাকবে এবং কাজ শেষে চ্যাট থেকে মুছে যাবে।"
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"আপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:"
            ),
            "no_terminal_available": (
                f"<b>{to_bold('CLUSTER TERMINALS BUSY')}</b>\n\n"
                f"এই মুহূর্তে সকল ক্লাস্টার টার্মিনাল ব্যবহৃত হচ্ছে।\n"
                f"দয়া করে কিছুক্ষণ পর পুনরায় চেষ্টা করুন অথবা অ্যাডমিনের সাথে যোগাযোগ করুন।"
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n"
                f"Assigned Terminal: <b>Node {kwargs.get('node_id', '')}</b>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং সেট করতে নিচে <b>START</b> বাটন চাপুন:"
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
                f"Terminal Node: <b>{kwargs.get('node_id', '')}</b>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান টার্মিনাল সেশনটি সুন্দরভাবে বন্ধ ও লগআউট করা হয়েছে।"
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"Welcome to high-tech WinGo Distributed Trading Cluster.\n"
                f"Please choose your preferred language:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"Please select your trading platform:"
            ),
            "credentials_card": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Please click buttons below to provide Number and Password. "
                f"Credentials will be wiped from chat immediately after dispatch."
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"Enter your account phone number:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"Enter your account password:"
            ),
            "no_terminal_available": (
                f"<b>{to_bold('CLUSTER TERMINALS BUSY')}</b>\n\n"
                f"All cluster terminals are occupied at this moment.\n"
                f"Please try again shortly or contact system administrator."
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n"
                f"Assigned Terminal: <b>Node {kwargs.get('node_id', '')}</b>\n\n"
                f"Login completed. Press <b>START</b> below to configure trading:"
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
                f"Terminal Node: <b>{kwargs.get('node_id', '')}</b>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: Martingale engine running smoothly."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser terminal closed cleanly."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==========================================
# 7. Interactive Control Keyboards
# ==========================================
def get_credentials_keyboard(chat_id):
    u = user_flow.get(chat_id, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(u.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data="ask_num"),
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data="ask_pass")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data="ask_pass")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="cancel"))
    return markup

def get_start_screen_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data="start_cfg"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="cancel")
    )
    return markup

def get_setup_param_keyboard(chat_id):
    sess = cluster_sessions.get(chat_id, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_lbl)}", callback_data="set_tgt"),
        InlineKeyboardButton(f"{to_bold(s_lbl)}", callback_data="set_stp")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data="run_auto"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="cancel")
    )
    return markup

def get_trading_control_keyboard(chat_id):
    sess = cluster_sessions.get(chat_id, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SHOT')}", callback_data="shot"),
        InlineKeyboardButton(f"{to_bold('BAL')}", callback_data="bal")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS')}", callback_data="stats"),
        InlineKeyboardButton(f"{to_bold(f'STOP {spinner}')}", callback_data="stop")
    )
    return markup

# ==========================================
# 8. Owner Admin Panel Auditing Engine
# ==========================================
def render_admin_dashboard():
    now = time.time()
    with db_lock:
        total = len(cluster_nodes)
        used_count = sum(1 for n in cluster_nodes.values() if n["status"] == "USED")
        idle_count = sum(1 for n in cluster_nodes.values() if n["status"] == "IDLE" and (now - n["last_heartbeat"]) <= 30)
        dead_count = total - (used_count + idle_count)

        lines = [
            "┌──────────────────────────────────────────┐",
            f"│ {to_bold('CLUSTER TERMINAL CONTROL PANEL')}",
            "├──────────────────────────────────────────┤",
            f"│ Total Terminals : {total}",
            f"│ Used / Running  : {used_count}",
            f"│ Idle / Free     : {idle_count}",
            f"│ Offline / Dead  : {dead_count}",
            "├──────────────────────────────────────────┤"
        ]

        if not cluster_nodes:
            lines.append("│ No worker nodes registered yet.")
        else:
            for nid, d in cluster_nodes.items():
                is_alive = (now - d["last_heartbeat"]) <= 30
                if d["status"] == "USED":
                    stat = "USED"
                    usr = f"Chat: {d.get('chat_id', 'N/A')}"
                elif is_alive:
                    stat = "IDLE"
                    usr = "Ready"
                else:
                    stat = "OFFLINE"
                    usr = "Timeout"

                line_str = f"│ Node: {to_bold(nid)} | Status: {to_bold(stat)} | {usr}"
                lines.append(line_str)

        lines.append("└──────────────────────────────────────────┘")
        return "\n".join(lines)

@bot.message_handler(commands=['admin', 'nodes'])
def handle_admin_command(message):
    if message.chat.id != OWNER_ID:
        return
    safe_delete_message(message.chat.id, message.message_id)
    panel_text = f"<pre>{render_admin_dashboard()}</pre>"
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"{to_bold('REFRESH AUDIT')}", callback_data="admin_refresh"))
    bot.send_message(message.chat.id, panel_text, reply_markup=markup, parse_mode="HTML")

# ==========================================
# 9. Telegram Flow Handlers
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_flow[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn"
    }

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    bot.send_message(chat_id, get_text(chat_id, "welcome"), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    # অ্যাডমিন প্যানেল রিফ্রেশ
    if data == "admin_refresh" and chat_id == OWNER_ID:
        bot.answer_callback_query(call.id, "আপডেট করা হয়েছে")
        try:
            bot.edit_message_text(
                f"<pre>{render_admin_dashboard()}</pre>",
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=call.message.reply_markup,
                parse_mode="HTML"
            )
        except Exception:
            pass
        return

    # ১. ভাষা নির্বাচন
    if data in ["lang_en", "lang_bn"]:
        u = user_flow.setdefault(chat_id, {})
        u["lang"] = "en" if data == "lang_en" else "bn"
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

    # ২. সাইট নির্বাচন
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        u = user_flow.setdefault(chat_id, {})
        u["site_name"] = site_name
        u["step"] = "INPUT_CREDENTIALS"

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(chat_id)
        )
        u["cred_card_msg_id"] = call.message.message_id

    # ৩. NUMBER বাটন
    elif data == "ask_num":
        user_flow[chat_id]["input_mode"] = "WAITING_PHONE"
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        user_flow[chat_id]["temp_prompt_id"] = p_msg.message_id

    # ৪. PASSWORD বাটন
    elif data == "ask_pass":
        u = user_flow.get(chat_id, {})
        if not u.get("phone"):
            bot.answer_callback_query(call.id, "দয়া করে আগে নাম্বার দিন!", show_alert=True)
            return

        u["input_mode"] = "WAITING_PASS"
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        u["temp_prompt_id"] = p_msg.message_id

    # ৫. START বাটন (প্যারামিটার কনফিগ স্ক্রিন)
    elif data == "start_cfg":
        bot.answer_callback_query(call.id, "প্যারামিটার সেটআপ প্রস্তুত হচ্ছে...")
        sess = cluster_sessions.get(chat_id, {})
        cur_bal = sess.get("current_balance", 0.0)

        config_caption = (
            f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n\n"
            f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
        )

        bot.edit_message_caption(
            caption=config_caption,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_setup_param_keyboard(chat_id),
            parse_mode="HTML"
        )

    # ৬. TARGET বাটন
    elif data == "set_tgt":
        user_flow[chat_id]["input_mode"] = "WAITING_TARGET"
        bot.answer_callback_query(call.id)
        sess = cluster_sessions.get(chat_id, {})
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{sess.get('current_balance', 0.0):.2f}"))
        user_flow[chat_id]["temp_prompt_id"] = p_msg.message_id

    # ৭. STEPS বাটন
    elif data == "set_stp":
        user_flow[chat_id]["input_mode"] = "WAITING_STEPS"
        bot.answer_callback_query(call.id)
        sess = cluster_sessions.get(chat_id, {})
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=sess.get('target_profit', 0)))
        user_flow[chat_id]["temp_prompt_id"] = p_msg.message_id

    # ৮. RUN AUTOMATION বাটন (টাস্ক পাঠানো)
    elif data == "run_auto":
        sess = cluster_sessions.get(chat_id)
        if not sess or not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট প্রফিট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "টার্মিনাল ইঞ্জিন সক্রিয় করা হচ্ছে...")
        node_id = sess["node_id"]

        # ওয়ার্কারের কাছে স্টার্ট টাস্ক প্রেরণ
        task_data = {
            "action": "START_TRADING",
            "chat_id": chat_id,
            "target_profit": sess["target_profit"],
            "total_steps": sess.get("total_steps", 7)
        }
        with db_lock:
            cluster_tasks[node_id] = task_data

    # ৯. SHOT বাটন
    elif data == "shot":
        bot.answer_callback_query(call.id, "লাইভ ফুটেজ রিকোয়েস্ট করা হয়েছে...")
        sess = cluster_sessions.get(chat_id)
        if sess:
            node_id = sess["node_id"]
            with db_lock:
                cluster_tasks[node_id] = {"action": "CAPTURE_SHOT", "chat_id": chat_id}

    # ১০. BAL বাটন
    elif data == "bal":
        sess = cluster_sessions.get(chat_id, {})
        b = sess.get("current_balance", 0.0)
        bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)

    # ১১. STATS বাটন
    elif data == "stats":
        sess = cluster_sessions.get(chat_id, {})
        stat_txt = (
            f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
            f"টার্মিনাল: <b>Node {sess.get('node_id', 'N/A')}</b>\n"
            f"ব্যালেন্স: <code>৳ {sess.get('current_balance', 0.0):.2f}</code>\n"
            f"টার্গেট: <code>৳ {sess.get('target_profit', 0.0):.2f}</code>\n"
            f"স্টেপ সংখ্যা: <b>{sess.get('total_steps', 7)}</b>"
        )
        bot.send_message(chat_id, stat_txt)

    # ১২. STOP বাটন
    elif data == "stop":
        sess = cluster_sessions.get(chat_id)
        if sess:
            node_id = sess["node_id"]
            with db_lock:
                cluster_tasks[node_id] = {"action": "STOP_TRADING", "chat_id": chat_id}
            bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
            bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং সাময়িকভাবে থামানো হয়েছে।")

    # ১৩. CANCEL বাটন (সম্পূর্ণ সেশন ক্লোজ)
    elif data == "cancel":
        bot.answer_callback_query(call.id, "টার্মিনাল সেশন বন্ধ করা হচ্ছে...")
        sess = cluster_sessions.get(chat_id)
        if sess:
            node_id = sess["node_id"]
            with db_lock:
                cluster_tasks[node_id] = {"action": "TERMINATE_SESSION", "chat_id": chat_id}
                if node_id in cluster_nodes:
                    cluster_nodes[node_id]["status"] = "IDLE"
                    cluster_nodes[node_id]["chat_id"] = None
                cluster_sessions.pop(chat_id, None)

        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==========================================
# 10. Text Message Processing
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_flow.get(chat_id, {})
    input_mode = u.get("input_mode")

    safe_delete_message(chat_id, message.message_id)

    if u.get("temp_prompt_id"):
        safe_delete_message(chat_id, u["temp_prompt_id"])
        u["temp_prompt_id"] = None

    if input_mode == "WAITING_PHONE":
        u["phone"] = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
            updated_card_text = (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{u.get('site_name', '')}</b>\n"
                f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
            )
            try:
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=u["cred_card_msg_id"],
                    reply_markup=get_credentials_keyboard(chat_id)
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        u["password"] = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            safe_delete_message(chat_id, u["cred_card_msg_id"])
            u["cred_card_msg_id"] = None

        # ১. উপযুক্ত ফ্রি ওয়ার্কার নোড অনুসন্ধান
        assigned_node = find_best_idle_node()
        if not assigned_node:
            bot.send_message(chat_id, get_text(chat_id, "no_terminal_available"))
            return

        # ২. সেশন রেজিস্টার
        cluster_sessions[chat_id] = {
            "chat_id": chat_id,
            "node_id": assigned_node,
            "site_name": u.get("site_name"),
            "current_balance": 0.0,
            "target_profit": 0.0,
            "total_steps": 7,
            "live_photo_msg_id": None
        }

        # ৩. টাস্ক ডিসপ্যাচ
        login_task = {
            "action": "LOGIN",
            "chat_id": chat_id,
            "site_name": u.get("site_name"),
            "phone": u.get("phone"),
            "password": u.get("password")
        }
        dispatch_task_to_node(assigned_node, login_task)

        anim_msg = bot.send_message(
            chat_id,
            f"<b>{to_bold('CONNECTING CLUSTER TERMINAL')}</b>\n"
            f"<code>Connecting to Node {assigned_node}...</code>"
        )
        cluster_sessions[chat_id]["connecting_msg_id"] = anim_msg.message_id

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            sess = cluster_sessions.get(chat_id, {})
            sess["target_profit"] = val
            u["input_mode"] = None

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            if sess.get("live_photo_msg_id"):
                bot.edit_message_caption(
                    caption=config_caption,
                    chat_id=chat_id,
                    message_id=sess["live_photo_msg_id"],
                    reply_markup=get_setup_param_keyboard(chat_id),
                    parse_mode="HTML"
                )
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            u["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            val = int(text)
            if val <= 0: raise ValueError()
            sess = cluster_sessions.get(chat_id, {})
            sess["total_steps"] = val
            u["input_mode"] = None

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Steps: <b>{val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            if sess.get("live_photo_msg_id"):
                bot.edit_message_caption(
                    caption=config_caption,
                    chat_id=chat_id,
                    message_id=sess["live_photo_msg_id"],
                    reply_markup=get_setup_param_keyboard(chat_id),
                    parse_mode="HTML"
                )
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            u["temp_prompt_id"] = p_msg.message_id

# ==========================================
# 11. Main Startup
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO DISTRIBUTED MASTER ORCHESTRATOR ACTIVE')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
