import os
import sys
import subprocess
import time
import threading
import shutil
import json
import sqlite3
import base64
import uuid
import datetime
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
# 3. Master Configurations & Internal DB
# ==========================================
TOKEN = "8808949150:AAGehY-s2kZKblgZtYqwtsCiDRypLx8O8hU"
OWNER_ID = 8707571669
MASTER_CLUSTER_HOST = "0.0.0.0"
MASTER_CLUSTER_PORT = 8080

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# In-memory / ephemeral master storage.
# User requested: "নিজস্ব ডাটাবেস তৈরি করবে নতুন নতুন ধরো এখন হোস্ট করলাম পরেরবার অফ করে রান করলাম নতুন ডাটাবেস আগের ডাটাবেস বাদ"
class InternalClusterDatabase:
    def __init__(self):
        self.lock = threading.RLock()
        self.nodes = {}          # node_id -> {node_id, status, last_heartbeat, current_chat_id, active_site, ip, started_at}
        self.tasks = {}          # node_id -> task dict
        self.sessions = {}       # chat_id -> session dict
        self.user_state = {}     # chat_id -> state dict
        self.wait_queue = []     # list of chat_ids waiting for free worker node
        self.boot_time = time.time()
        print("[*] Internal Ephemeral Cluster Database Initialized Freshly (Memory Backed).")

    def register_or_heartbeat(self, node_id, status="IDLE", ip="127.0.0.1", active_site=None, current_chat_id=None):
        with self.lock:
            now = time.time()
            if node_id not in self.nodes:
                self.nodes[node_id] = {
                    "node_id": node_id,
                    "status": status,
                    "last_heartbeat": now,
                    "current_chat_id": current_chat_id,
                    "active_site": active_site,
                    "ip": ip,
                    "started_at": now
                }
            else:
                self.nodes[node_id]["last_heartbeat"] = now
                self.nodes[node_id]["status"] = status
                self.nodes[node_id]["ip"] = ip
                if active_site is not None:
                    self.nodes[node_id]["active_site"] = active_site
                if current_chat_id is not None:
                    self.nodes[node_id]["current_chat_id"] = current_chat_id
            return self.nodes[node_id]

    def get_idle_node(self):
        with self.lock:
            now = time.time()
            for node_id, data in self.nodes.items():
                if data["status"] == "IDLE" and (now - data["last_heartbeat"]) <= 35:
                    return node_id
            return None

    def allocate_node(self, node_id, chat_id, site_name):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "BUSY"
                self.nodes[node_id]["current_chat_id"] = chat_id
                self.nodes[node_id]["active_site"] = site_name
                return True
            return False

    def release_node(self, node_id):
        with self.lock:
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "IDLE"
                self.nodes[node_id]["current_chat_id"] = None
                self.nodes[node_id]["active_site"] = None
                if node_id in self.tasks:
                    del self.tasks[node_id]

    def set_task(self, node_id, task_data):
        with self.lock:
            self.tasks[node_id] = task_data

    def pull_task(self, node_id):
        with self.lock:
            return self.tasks.get(node_id, None)

    def clear_task(self, node_id):
        with self.lock:
            return self.tasks.pop(node_id, None)

    def update_session(self, chat_id, data):
        with self.lock:
            if chat_id not in self.sessions:
                self.sessions[chat_id] = {}
            self.sessions[chat_id].update(data)
            self.sessions[chat_id]["last_update"] = time.time()

    def get_session(self, chat_id):
        with self.lock:
            return self.sessions.get(chat_id, {})

    def remove_session(self, chat_id):
        with self.lock:
            sess = self.sessions.pop(chat_id, None)
            if sess and sess.get("assigned_node"):
                self.release_node(sess["assigned_node"])
            return sess

    def get_cluster_stats(self):
        with self.lock:
            now = time.time()
            total = len(self.nodes)
            active_running = 0
            idle_free = 0
            offline = 0
            node_list = []

            for nid, d in self.nodes.items():
                is_alive = (now - d["last_heartbeat"]) <= 35
                cur_status = d["status"] if is_alive else "OFFLINE"
                if cur_status == "BUSY":
                    active_running += 1
                elif cur_status == "IDLE":
                    idle_free += 1
                else:
                    offline += 1

                node_list.append({
                    "node_id": nid,
                    "status": cur_status,
                    "is_alive": is_alive,
                    "user": d["current_chat_id"],
                    "site": d["active_site"],
                    "ip": d.get("ip", "remote"),
                    "last_seen_sec": int(now - d["last_heartbeat"])
                })

            return {
                "total": total,
                "active": active_running,
                "idle": idle_free,
                "offline": offline,
                "queue": len(self.wait_queue),
                "nodes": node_list
            }

db = InternalClusterDatabase()

# ==========================================
# 4. Master HTTP API Server for Workers
# ==========================================
class ClusterRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Keep master terminal clean

    def _send_json(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except Exception:
            payload = {}

        # 1. Worker Node Heartbeat & Registration
        if parsed.path == "/api/node/heartbeat":
            node_id = payload.get("node_id")
            if not node_id:
                self._send_json(400, {"error": "Missing node_id"})
                return
            status = payload.get("status", "IDLE")
            active_site = payload.get("active_site")
            current_chat_id = payload.get("current_chat_id")
            client_ip = self.client_address[0]
            db.register_or_heartbeat(node_id, status=status, ip=client_ip, active_site=active_site, current_chat_id=current_chat_id)
            self._send_json(200, {"status": "ACK", "server_time": time.time()})

        # 2. Worker Pulls Assigned Task
        elif parsed.path == "/api/node/pull_task":
            node_id = payload.get("node_id")
            if not node_id:
                self._send_json(400, {"error": "Missing node_id"})
                return
            task = db.pull_task(node_id)
            self._send_json(200, {"task": task})

        # 3. Worker Acknowledges & Clears Task
        elif parsed.path == "/api/node/ack_task":
            node_id = payload.get("node_id")
            if node_id:
                db.clear_task(node_id)
            self._send_json(200, {"status": "CLEARED"})

        # 4. Worker Telemetry & Screenshot Sync
        elif parsed.path == "/api/node/sync_session":
            chat_id = payload.get("chat_id")
            node_id = payload.get("node_id")
            if not chat_id:
                self._send_json(400, {"error": "Missing chat_id"})
                return

            sess_updates = {
                "node_id": node_id,
                "status": payload.get("status"),
                "live_balance": payload.get("live_balance"),
                "wins": payload.get("wins"),
                "losses": payload.get("losses"),
                "step": payload.get("step"),
                "error_message": payload.get("error_message"),
                "target_reached": payload.get("target_reached", False),
                "profit": payload.get("profit", 0)
            }
            if "screenshot_base64" in payload:
                sess_updates["screenshot_base64"] = payload["screenshot_base64"]

            db.update_session(chat_id, sess_updates)

            # Trigger immediate asynchronous dispatch to user on Telegram
            threading.Thread(target=handle_incoming_worker_telemetry, args=(chat_id, sess_updates), daemon=True).start()

            self._send_json(200, {"status": "SUCCESS"})

        # 5. Worker Node Logout / Release
        elif parsed.path == "/api/node/release":
            node_id = payload.get("node_id")
            chat_id = payload.get("chat_id")
            if node_id:
                db.release_node(node_id)
            if chat_id:
                db.remove_session(chat_id)
            self._send_json(200, {"status": "RELEASED"})

        else:
            self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/cluster/status":
            stats = db.get_cluster_stats()
            self._send_json(200, stats)
        else:
            self._send_json(404, {"error": "Not Found"})

def start_master_http_server():
    server = HTTPServer((MASTER_CLUSTER_HOST, MASTER_CLUSTER_PORT), ClusterRequestHandler)
    print(f"[*] Master Cluster HTTP Controller listening on http://{MASTER_CLUSTER_HOST}:{MASTER_CLUSTER_PORT}")
    server.serve_forever()

threading.Thread(target=start_master_http_server, daemon=True).start()

# ==========================================
# 5. Smart Telegram Image Replacement Engine
# ==========================================
def display_or_replace_photo_from_bytes(chat_id, image_bytes, caption_text, reply_markup=None):
    sess = db.get_session(chat_id)
    last_photo_msg_id = sess.get("live_photo_message_id")
    replaced = False

    if last_photo_msg_id and image_bytes:
        try:
            media = InputMediaPhoto(image_bytes, caption=caption_text, parse_mode="HTML")
            bot.edit_message_media(
                media=media,
                chat_id=chat_id,
                message_id=last_photo_msg_id,
                reply_markup=reply_markup
            )
            replaced = True
        except Exception:
            replaced = False

    if not replaced and image_bytes:
        try:
            msg = bot.send_photo(
                chat_id,
                image_bytes,
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            db.update_session(chat_id, {"live_photo_message_id": msg.message_id})
        except Exception as e:
            print(f"[*] Photo replace error: {e}")

# ==========================================
# 6. Dynamic Multilingual Templates
# ==========================================
def get_text(chat_id, key, **kwargs):
    u = db.user_state.get(chat_id, {})
    lang = u.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে প্রিমিয়াম উইনগো ট্রেডিং অটোমেশন প্ল্যাটফর্মে।\n"
                f"দয়া করে আপনার পছন্দের ভাষা নির্বাচন করুন:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"আসসালামু আলাইকুম, দয়া করে আপনি আপনার একটি ট্রেডিং সাইট নির্বাচন করুন:"
            ),
            "credentials_card": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"আসসালামু আলাইকুম, দয়া করে নিচের বাটন চেপে আপনার নাম্বার এবং পাসওয়ার্ড দিন। "
                f"এটি সম্পূর্ণ গোপন থাকবে এবং কাজ শেষে চ্যাট থেকে মুছে যাবে।"
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"আপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:"
            ),
            "no_worker_available": (
                f"<b>{to_bold('CLUSTER CAPACITY OCCUPIED')}</b>\n\n"
                f"দুঃখিত, এই মুহূর্তে ক্লাস্টারের সকল রিমোট টার্মিনাল ব্যস্ত রয়েছে।\n"
                f"আপনাকে স্বয়ংক্রিয় ওয়েটিং লিস্টে রাখা হয়েছে। যেকোনো একটি টার্মিনাল খালি হওয়ামাত্র আপনার সেশন সক্রিয় করা হবে।"
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Assigned Terminal: <code>{kwargs.get('node_id', 'ONLINE')}</code>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং শুরু করতে নিচে <b>START</b> বাটন চাপুন:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'ভুল তথ্য বা টাইমআউট')}</i>\n\n"
                f"পুনরায় চেষ্টা করার জন্য /start চাপুন।"
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
                f"Remote Node: <code>{kwargs.get('node_id', 'AUTO')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7 on remote worker.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে এবং রিমোট ব্রাউজার ট্যাব কেটে দেওয়া হয়েছে। নতুন সেশনের জন্য /start পাঠান।"
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
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
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
            "no_worker_available": (
                f"<b>{to_bold('CLUSTER CAPACITY OCCUPIED')}</b>\n\n"
                f"All distributed remote terminals are currently occupied.\n"
                f"You have been placed in the automatic wait queue."
            ),
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Assigned Terminal: <code>{kwargs.get('node_id', 'ONLINE')}</code>\n"
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
                f"Remote Node: <code>{kwargs.get('node_id', 'AUTO')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7 on remote worker.\n"
                f"<b>LIVE STATUS</b>: Martingale engine running smoothly."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser session closed cleanly and terminal tab released. Send /start to begin a new session."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==========================================
# 7. Interactive Control Keyboards
# ==========================================
def get_credentials_keyboard(chat_id):
    sess = db.get_session(chat_id)
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data=f"ask_num:{chat_id}"),
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"ask_pass:{chat_id}")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"ask_pass:{chat_id}")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{chat_id}"))
    return markup

def get_start_screen_keyboard(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data=f"start_cfg:{chat_id}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{chat_id}")
    )
    return markup

def get_setup_param_keyboard(chat_id):
    sess = db.get_session(chat_id)
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_lbl)}", callback_data=f"set_tgt:{chat_id}"),
        InlineKeyboardButton(f"{to_bold(s_lbl)}", callback_data=f"set_stp:{chat_id}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data=f"run_auto:{chat_id}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{chat_id}")
    )
    return markup

def get_trading_control_keyboard(chat_id):
    sess = db.get_session(chat_id)
    anim_tick = sess.get("anim_tick", 0) + 1
    db.update_session(chat_id, {"anim_tick": anim_tick})
    spinner = SPINNER_FRAMES[anim_tick % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SHOT')}", callback_data=f"shot:{chat_id}"),
        InlineKeyboardButton(f"{to_bold('BAL')}", callback_data=f"bal:{chat_id}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS')}", callback_data=f"stats:{chat_id}"),
        InlineKeyboardButton(f"{to_bold(f'STOP {spinner}')}", callback_data=f"stop:{chat_id}")
    )
    return markup

# ==========================================
# 8. Clean Login Animation & Remote Dispatch
# ==========================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE CLUSTER ENGINE</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Querying cluster terminals...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>▰▰▰▱▱▱▱▱▱▱ 35% Remote worker allocated...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>▰▰▰▰▰▰▱▱▱▱ 65% Auto-filling credentials...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>▰▰▰▰▰▰▰▰▰▰ 100% Login verification complete!</code>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.4)

def dispatch_login_to_worker(chat_id, phone, password, anim_msg_id):
    sess = db.get_session(chat_id)
    site_name = sess.get("site_name", "Amar Club")

    play_clean_login_animation(chat_id, anim_msg_id)

    # Find idle worker node
    idle_node_id = db.get_idle_node()
    if not idle_node_id:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "no_worker_available"))
        if chat_id not in db.wait_queue:
            db.wait_queue.append(chat_id)
        return

    db.allocate_node(idle_node_id, chat_id, site_name)
    db.update_session(chat_id, {
        "assigned_node": idle_node_id,
        "phone": phone,
        "password": password,
        "status": "CONNECTING",
        "anim_msg_id": anim_msg_id
    })

    # Dispatch task payload to worker
    task_payload = {
        "action": "LOGIN",
        "chat_id": chat_id,
        "site": "amarclub" if "AMAR" in site_name.upper() else "dkwin",
        "phone": phone,
        "password": password,
        "timestamp": time.time()
    }
    db.set_task(idle_node_id, task_payload)
    print(f"[*] Dispatched LOGIN task to worker node {idle_node_id} for user {chat_id}")

# Asynchronous handler when worker node posts session status
def handle_incoming_worker_telemetry(chat_id, update):
    sess = db.get_session(chat_id)
    status = update.get("status")
    node_id = update.get("node_id", "ONLINE")
    site_name = sess.get("site_name", "Amar Club")

    # If login succeeded
    if status == "LOGGED_IN":
        anim_msg_id = sess.get("anim_msg_id")
        if anim_msg_id:
            safe_delete_message(chat_id, anim_msg_id)
            db.update_session(chat_id, {"anim_msg_id": None})

        phone = sess.get("phone", "")
        masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
        caption = get_text(chat_id, "login_success", site_name=site_name, node_id=node_id, phone=masked_phone)

        img_b64 = update.get("screenshot_base64")
        if img_b64:
            img_bytes = base64.b64decode(img_b64)
            display_or_replace_photo_from_bytes(chat_id, img_bytes, caption, get_start_screen_keyboard(chat_id))
        else:
            bot.send_message(chat_id, caption, reply_markup=get_start_screen_keyboard(chat_id))

    # If login failed
    elif status == "LOGIN_FAILED":
        anim_msg_id = sess.get("anim_msg_id")
        if anim_msg_id:
            safe_delete_message(chat_id, anim_msg_id)
            db.update_session(chat_id, {"anim_msg_id": None})

        err = update.get("error_message", "ভুল তথ্য বা টাইমআউট")
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error=err))
        db.remove_session(chat_id)

    # If target profit achieved
    elif update.get("target_reached"):
        start_b = sess.get("start_bal", 0.0)
        cur_b = float(update.get("live_balance", 0.0))
        profit = update.get("profit", cur_b - start_b)
        w = update.get("wins", 0)
        l = update.get("losses", 0)

        msg = (
            f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
            f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
            f"শুরুর ব্যালেন্স: <code>৳ {start_b:.2f}</code>\n"
            f"বর্তমান ব্যালেন্স: <code>৳ {cur_b:.2f}</code>\n"
            f"অর্জিত প্রফিট: <code>+৳ {profit:.2f}</code>\n"
            f"মোট উইন: <b>{w}</b> | লস: <b>{l}</b>\n\n"
            f"রিমোট টার্মিনাল ট্যাব সফলভাবে ক্লোজ করা হয়েছে।"
        )
        img_b64 = update.get("screenshot_base64")
        if img_b64:
            img_bytes = base64.b64decode(img_b64)
            display_or_replace_photo_from_bytes(chat_id, img_bytes, msg, None)
        else:
            bot.send_message(chat_id, msg)

        # Release node
        db.release_node(node_id)
        db.remove_session(chat_id)

# ==========================================
# 9. Telegram Commands & Handlers
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    db.user_state[chat_id] = {
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
def handle_admin_dashboard(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != OWNER_ID:
        bot.send_message(chat_id, f"<b>{to_bold('ACCESS DENIED')}</b>\nআপনার কাছে এডমিন প্যানেল এক্সেস করার অনুমতি নেই।")
        return

    stats = db.get_cluster_stats()
    
    # VIP ASCII border formatting matching user specification
    lines = [
        "┌──────────────────────────────┐",
        "│ CLUSTER TERMINAL STATUS",
        "├──────────────────────────────┤",
        f"│ Total Registered Nodes: {stats['total']}",
        f"│ Active / Running: {stats['active']}",
        f"│ Idle / Free: {stats['idle']}",
        f"│ Offline / Disconnected: {stats['offline']}",
        f"│ Waiting Queue Users: {stats['queue']}",
        "├──────────────────────────────┤"
    ]

    if not stats["nodes"]:
        lines.append("│ No worker nodes connected yet.")
    else:
        for n in stats["nodes"]:
            status_text = n["status"]
            user_text = f"User: {n['user']}" if n['user'] else "Heartbeat: OK"
            lines.append(f"│ Node: {n['node_id']} | Status: {status_text} | {user_text}")

    lines.append("└──────────────────────────────┘")

    dashboard_text = "\n".join(lines)
    bot.send_message(chat_id, f"<pre>{dashboard_text}</pre>", parse_mode="HTML")

# ==========================================
# 10. Callbacks Routing
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    target_chat = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else chat_id

    # ১. ভাষা নির্বাচন
    if action in ["lang_en", "lang_bn"]:
        u = db.user_state.setdefault(chat_id, {})
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

    # ২. সাইট নির্বাচন
    elif action in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if action == "site_amarclub" else "DK Win"
        db.update_session(chat_id, {
            "site_name": site_name,
            "chat_id": chat_id,
            "created_at": time.time(),
            "target_profit": 0,
            "total_steps": 7,
            "is_trading": False
        })

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(chat_id)
        )
        db.update_session(chat_id, {"cred_card_msg_id": call.message.message_id})

    # ৩. NUMBER বাটন
    elif action == "ask_num":
        db.update_session(chat_id, {"input_mode": "WAITING_PHONE"})
        bot.answer_callback_query(call.id)
        p = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        db.update_session(chat_id, {"temp_prompt_id": p.message_id})

    # ৪. PASSWORD বাটন
    elif action == "ask_pass":
        sess = db.get_session(chat_id)
        if not sess.get("phone"):
            bot.answer_callback_query(call.id, "এটা হবে না! আপনি দয়া করে নাম্বারটি আগে দিন।", show_alert=True)
            return

        db.update_session(chat_id, {"input_mode": "WAITING_PASS"})
        bot.answer_callback_query(call.id)
        p = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        db.update_session(chat_id, {"temp_prompt_id": p.message_id})

    # ৫. START বাটন (উইনগো মার্কেট লোড ও কনফিগারেশন)
    elif action == "start_cfg":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        if not node_id:
            bot.answer_callback_query(call.id, "রিমোট টার্মিনাল পাওয়া যায়নি", show_alert=True)
            return

        bot.answer_callback_query(call.id, "উইনগো ৩০এস পেজ প্রস্তুত করা হচ্ছে...")
        db.set_task(node_id, {"action": "PREPARE_WINGO", "chat_id": chat_id, "timestamp": time.time()})

    # ৬. TARGET বাটন
    elif action == "set_tgt":
        db.update_session(chat_id, {"input_mode": "WAITING_TARGET"})
        bot.answer_callback_query(call.id)
        sess = db.get_session(chat_id)
        bal = sess.get("live_balance", "0.00")
        p = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=bal))
        db.update_session(chat_id, {"temp_prompt_id": p.message_id})

    # ৭. STEPS বাটন
    elif action == "set_stp":
        db.update_session(chat_id, {"input_mode": "WAITING_STEPS"})
        bot.answer_callback_query(call.id)
        sess = db.get_session(chat_id)
        tgt = sess.get("target_profit", 0)
        p = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        db.update_session(chat_id, {"temp_prompt_id": p.message_id})

    # ৮. RUN AUTOMATION বাটন
    elif action == "run_auto":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় করা হচ্ছে...")
        cur_b = float(sess.get("live_balance", 0.0))
        target_total = cur_b + sess["target_profit"]
        db.update_session(chat_id, {"is_trading": True, "start_bal": cur_b})

        # Send start command to worker node
        db.set_task(node_id, {
            "action": "START_TRADING",
            "chat_id": chat_id,
            "target_profit": sess["target_profit"],
            "total_steps": sess["total_steps"],
            "timestamp": time.time()
        })

        caption = get_text(
            chat_id, "running_dashboard",
            site_name=sess.get("site_name", "Amar Club"),
            node_id=node_id,
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=sess["total_steps"]
        )

        img_b64 = sess.get("screenshot_base64")
        if img_b64:
            img_bytes = base64.b64decode(img_b64)
            display_or_replace_photo_from_bytes(chat_id, img_bytes, caption, get_trading_control_keyboard(chat_id))
        else:
            bot.send_message(chat_id, caption, reply_markup=get_trading_control_keyboard(chat_id))

    # ৯. SHOT (রিয়েল-টাইম ফুটেজ আপডেট)
    elif action == "shot":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        bot.answer_callback_query(call.id, "ফুটেজ আপডেট হচ্ছে...")
        if node_id:
            db.set_task(node_id, {"action": "CAPTURE_SHOT", "chat_id": chat_id, "timestamp": time.time()})

    # ১০. BAL (লাইভ ব্যালেন্স চেক)
    elif action == "bal":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        if node_id:
            db.set_task(node_id, {"action": "FETCH_BALANCE", "chat_id": chat_id, "timestamp": time.time()})
        b = sess.get("live_balance", "0.00")
        bot.answer_callback_query(call.id, f"Live Balance: ৳ {b}", show_alert=True)

    # ১১. STATS (লাইভ ট্রেডিং স্ট্যাটাস)
    elif action == "stats":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node", "AUTO")
        b = sess.get("live_balance", "0.00")
        tgt = sess.get("target_profit", 0)
        w = sess.get("wins", 0)
        l = sess.get("losses", 0)
        st = sess.get("step", 1)
        tot = sess.get("total_steps", 7)

        stat_txt = (
            f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
            f"রিমোট টার্মিনাল: <code>{node_id}</code>\n"
            f"ব্যালেন্স: <code>৳ {b}</code>\n"
            f"টার্গেট: <code>৳ {tgt}</code>\n"
            f"মার্টিনগেল লেভেল: <b>Step {st}/{tot}</b>\n"
            f"উইন: <b>{w}</b> | লস: <b>{l}</b>"
        )
        bot.send_message(chat_id, stat_txt)

    # ১২. STOP বাটন
    elif action == "stop":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        if node_id:
            db.set_task(node_id, {"action": "STOP_TRADING", "chat_id": chat_id, "timestamp": time.time()})
        db.update_session(chat_id, {"is_trading": False})
        bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং অটোমেশন সাময়িকভাবে থামানো হয়েছে।")

    # ১৩. CANCEL বাটন
    elif action == "cancel":
        sess = db.get_session(chat_id)
        node_id = sess.get("assigned_node")
        if node_id:
            # Instruct worker to immediately quit driver, close tab and free RAM
            db.set_task(node_id, {"action": "LOGOUT_AND_CLOSE", "chat_id": chat_id, "timestamp": time.time()})
            db.release_node(node_id)
        db.remove_session(chat_id)
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==========================================
# 11. User Text Input Handler
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    sess = db.get_session(chat_id)
    input_mode = sess.get("input_mode")

    safe_delete_message(chat_id, message.message_id)

    if sess.get("temp_prompt_id"):
        safe_delete_message(chat_id, sess["temp_prompt_id"])
        db.update_session(chat_id, {"temp_prompt_id": None})

    if input_mode == "WAITING_PHONE":
        db.update_session(chat_id, {"phone": text, "input_mode": None})
        cred_card_id = sess.get("cred_card_msg_id")
        if cred_card_id:
            try:
                masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_card_text = (
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"প্ল্যাটফর্ম: <b>{sess.get('site_name', '')}</b>\n"
                    f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                    f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
                )
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=cred_card_id,
                    reply_markup=get_credentials_keyboard(chat_id)
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        phone = sess.get("phone", "")
        db.update_session(chat_id, {"password": text, "input_mode": None})

        cred_card_id = sess.get("cred_card_msg_id")
        if cred_card_id:
            safe_delete_message(chat_id, cred_card_id)
            db.update_session(chat_id, {"cred_card_msg_id": None})

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE CLUSTER ENGINE</b>")
        threading.Thread(
            target=dispatch_login_to_worker,
            args=(chat_id, phone, text, anim_msg.message_id),
            daemon=True
        ).start()

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            db.update_session(chat_id, {"target_profit": val, "input_mode": None})

            cur_bal = sess.get("live_balance", "0.00")
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            img_b64 = sess.get("screenshot_base64")
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                display_or_replace_photo_from_bytes(chat_id, img_bytes, config_caption, get_setup_param_keyboard(chat_id))
            else:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(chat_id))
        except ValueError:
            p = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            db.update_session(chat_id, {"temp_prompt_id": p.message_id})

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            db.update_session(chat_id, {"total_steps": steps_val, "input_mode": None})

            cur_bal = sess.get("live_balance", "0.00")
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            img_b64 = sess.get("screenshot_base64")
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                display_or_replace_photo_from_bytes(chat_id, img_bytes, config_caption, get_setup_param_keyboard(chat_id))
            else:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(chat_id))
        except ValueError:
            p = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            db.update_session(chat_id, {"temp_prompt_id": p.message_id})

# ==========================================
# 12. 24-Hour Lifetime Watchdog
# ==========================================
def continuous_24h_master_watchdog():
    while True:
        try:
            now = time.time()
            # 1. Clean dead worker nodes (heartbeat missed for > 60 seconds)
            with db.lock:
                for nid, n in list(db.nodes.items()):
                    if now - n["last_heartbeat"] > 60:
                        print(f"[*] Node {nid} timed out. Marking OFFLINE.")
                        n["status"] = "OFFLINE"
                        if n.get("current_chat_id"):
                            chat_id = n["current_chat_id"]
                            bot.send_message(chat_id, f"<b>{to_bold('NODE DISCONNECTED')}</b>\nরিমোট টার্মিনালের সংযোগ বিচ্ছিন্ন হয়েছে।")
                            db.remove_session(chat_id)

            # 2. 24-Hour session lifetime enforcement
            for chat_id, s in list(db.sessions.items()):
                created_at = s.get("created_at", now)
                if now - created_at >= 86400:
                    print(f"[*] 24-hour limit reached for user: {chat_id}")
                    node_id = s.get("assigned_node")
                    if node_id:
                        db.set_task(node_id, {"action": "LOGOUT_AND_CLOSE", "chat_id": chat_id, "timestamp": now})
                        db.release_node(node_id)
                    db.remove_session(chat_id)
                    bot.send_message(chat_id, f"<b>{to_bold('24-HOUR LIMIT EXPIRED')}</b>\nআপনার ২৪ ঘণ্টার স্বয়ংক্রিয় সেশন সমাপ্ত হয়েছে। পুনরায় শুরু করতে /start পাঠান।")
        except Exception as e:
            print(f"[*] Watchdog error: {e}")
        time.sleep(30)

threading.Thread(target=continuous_24h_master_watchdog, daemon=True).start()

# ==========================================
# 13. Main Master Bot Entry
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print(f"[*] {to_bold('WINGO 30S DISTRIBUTED MASTER BOT ACTIVE')}...")
    print(f"[*] BOT TOKEN: {TOKEN[:10]}...")
    print(f"[*] OWNER ID: {OWNER_ID}")
    print(f"[*] CLUSTER INTERNAL REST API PORT: {MASTER_CLUSTER_PORT}")
    print("=" * 60)
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
