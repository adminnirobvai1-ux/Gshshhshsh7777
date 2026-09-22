import os
import sys
import subprocess
import time
import threading
import json
import base64
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
# 3. Master Bot Configurations & Constants
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
OWNER_ID = 8707571669

PAYMENT_BKASH = "01870829343"
PAYMENT_NAGAD = "01876685711"

CHANNEL_DARK67 = "https://t.me/DARK67HACK"
CHANNEL_BDWIN24 = "https://t.me/bdwin24_bd"

MASTER_HOST = "0.0.0.0"
MASTER_PORT = 8088

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

MASTER_TEMP_DIR = os.path.expanduser("~/.master_bot_cache")
os.makedirs(MASTER_TEMP_DIR, exist_ok=True)

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# ==========================================
# 4. Volatile In-Memory Cluster Database Engine
# ==========================================
class ClusterDatabase:
    """
    অভ্যন্তরীণ ইন-মেমোরি ডেটাবেস ইঞ্জিন।
    মাস্টার স্ক্রিপ্ট রিস্টার্ট দিলে সম্পূর্ণ ফ্রেশ মেমোরি দিয়ে শুরু হয়।
    কোনো এক্সটার্নাল ডিপেন্ডেন্সির ঝামেলা নেই।
    """
    def __init__(self):
        self._lock = threading.RLock()
        self.nodes = {}          # {node_id: {status, last_heartbeat, current_chat_id, active_site, ip}}
        self.tasks = {}          # {node_id: {chat_id, site, phone, password, target_profit, total_steps, action, timestamp}}
        self.sessions = {}       # {chat_id: {node_id, status, live_balance, wins, losses, last_update, photo_msg_id}}
        self.subscriptions = {}  # {chat_id: {status: "ACTIVE"|"EXPIRED", expires_at: unix_timestamp}}
        self.user_states = {}    # {chat_id: {lang, step, active_sid, phone, target_profit, total_steps, temp_prompt_id, cred_card_msg_id}}

    def register_node(self, node_id, ip="127.0.0.1"):
        with self._lock:
            if node_id not in self.nodes:
                self.nodes[node_id] = {
                    "node_id": node_id,
                    "status": "IDLE",
                    "last_heartbeat": time.time(),
                    "current_chat_id": None,
                    "active_site": None,
                    "ip": ip
                }
            else:
                self.nodes[node_id]["last_heartbeat"] = time.time()
                self.nodes[node_id]["ip"] = ip
            return True

    def heartbeat_node(self, node_id, status=None, current_chat_id=None, active_site=None):
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id]["last_heartbeat"] = time.time()
                if status:
                    self.nodes[node_id]["status"] = status
                if current_chat_id is not None:
                    self.nodes[node_id]["current_chat_id"] = current_chat_id
                if active_site is not None:
                    self.nodes[node_id]["active_site"] = active_site
                return True
            return False

    def get_idle_node(self):
        with self._lock:
            now = time.time()
            for nid, data in self.nodes.items():
                is_fresh = (now - data.get("last_heartbeat", 0)) <= 35
                if is_fresh and data.get("status") == "IDLE":
                    return nid
            return None

    def assign_task(self, node_id, task_payload):
        with self._lock:
            self.tasks[node_id] = task_payload
            if node_id in self.nodes:
                self.nodes[node_id]["status"] = "BUSY"
                self.nodes[node_id]["current_chat_id"] = task_payload.get("chat_id")
                self.nodes[node_id]["active_site"] = task_payload.get("site")

    def pop_task(self, node_id):
        with self._lock:
            return self.tasks.pop(node_id, None)

    def set_session(self, chat_id, data):
        with self._lock:
            if chat_id not in self.sessions:
                self.sessions[chat_id] = {}
            self.sessions[chat_id].update(data)
            self.sessions[chat_id]["last_update"] = time.time()

    def get_session(self, chat_id):
        with self._lock:
            return self.sessions.get(chat_id, {})

    def remove_session(self, chat_id):
        with self._lock:
            sess = self.sessions.pop(chat_id, None)
            if sess:
                assigned_node = sess.get("node_id")
                if assigned_node and assigned_node in self.nodes:
                    self.nodes[assigned_node]["status"] = "IDLE"
                    self.nodes[assigned_node]["current_chat_id"] = None
                    self.nodes[assigned_node]["active_site"] = None
            return sess

    def get_cluster_snapshot(self):
        with self._lock:
            now = time.time()
            total = len(self.nodes)
            busy = 0
            idle = 0
            offline = 0
            records = []
            for nid, info in self.nodes.items():
                heartbeat_age = now - info.get("last_heartbeat", 0)
                if heartbeat_age > 35:
                    status = "OFFLINE"
                    offline += 1
                else:
                    status = info.get("status", "IDLE")
                    if status == "BUSY":
                        busy += 1
                    else:
                        idle += 1
                records.append({
                    "node_id": nid,
                    "status": status,
                    "chat_id": info.get("current_chat_id"),
                    "heartbeat_age": int(heartbeat_age)
                })
            return {
                "total": total,
                "busy": busy,
                "idle": idle,
                "offline": offline,
                "records": records
            }

db = ClusterDatabase()

# ==========================================
# 5. Master REST API Server for Remote Workers
# ==========================================
class MasterAPIRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            payload = json.loads(post_data)
        except Exception:
            payload = {}

        if parsed.path == "/api/node/register":
            node_id = payload.get("node_id")
            if node_id:
                client_ip = self.client_address[0]
                db.register_node(node_id, ip=client_ip)
                self._send_json(200, {"success": True, "message": "Node registered successfully"})
            else:
                self._send_json(400, {"success": False, "error": "node_id is required"})

        elif parsed.path == "/api/node/heartbeat":
            node_id = payload.get("node_id")
            status = payload.get("status")
            chat_id = payload.get("current_chat_id")
            active_site = payload.get("active_site")
            if node_id and db.heartbeat_node(node_id, status, chat_id, active_site):
                self._send_json(200, {"success": True})
            else:
                self._send_json(404, {"success": False, "error": "Node not recognized"})

        elif parsed.path == "/api/session/update":
            chat_id = payload.get("chat_id")
            node_id = payload.get("node_id")
            if chat_id:
                status = payload.get("status", "RUNNING")
                live_bal = payload.get("live_balance", "0.00")
                wins = payload.get("wins", 0)
                losses = payload.get("losses", 0)
                step_level = payload.get("step_level", 1)
                img_b64 = payload.get("screenshot_base64", None)

                db.set_session(chat_id, {
                    "node_id": node_id,
                    "status": status,
                    "live_balance": live_bal,
                    "wins": wins,
                    "losses": losses,
                    "step_level": step_level
                })

                if img_b64:
                    threading.Thread(
                        target=handle_incoming_worker_frame,
                        args=(chat_id, node_id, status, live_bal, wins, losses, step_level, img_b64),
                        daemon=True
                    ).start()

                self._send_json(200, {"success": True})
            else:
                self._send_json(400, {"success": False, "error": "chat_id is required"})

        elif parsed.path == "/api/session/complete":
            chat_id = payload.get("chat_id")
            node_id = payload.get("node_id")
            reason = payload.get("reason", "TARGET_ACHIEVED")
            final_bal = payload.get("final_balance", "0.00")
            img_b64 = payload.get("screenshot_base64", None)

            if chat_id:
                threading.Thread(
                    target=handle_session_completion,
                    args=(chat_id, node_id, reason, final_bal, img_b64),
                    daemon=True
                ).start()
                self._send_json(200, {"success": True})
            else:
                self._send_json(400, {"success": False, "error": "chat_id is required"})
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/api/node/task":
            node_id = params.get("node_id", [None])[0]
            if node_id:
                task = db.pop_task(node_id)
                if task:
                    self._send_json(200, {"has_task": True, "task": task})
                else:
                    self._send_json(200, {"has_task": False})
            else:
                self._send_json(400, {"error": "node_id param missing"})
        elif parsed.path == "/api/cluster/health":
            snapshot = db.get_cluster_snapshot()
            self._send_json(200, snapshot)
        else:
            self._send_json(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        # সাইলেন্ট লগিং যাতে কনসোল পরিচ্ছন্ন থাকে
        pass

def run_master_api_server():
    server = HTTPServer((MASTER_HOST, MASTER_PORT), MasterAPIRequestHandler)
    print(f"[*] Cluster API Hub online at http://{MASTER_HOST}:{MASTER_PORT}")
    server.serve_forever()

threading.Thread(target=run_master_api_server, daemon=True).start()

# ==========================================
# 6. Telegram UI Templates & Formatting
# ==========================================
def get_text(chat_id, key, **kwargs):
    u = db.user_states.get(chat_id, {})
    lang = u.get("lang", "bn")

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
                f"Account: <code>{kwargs.get('phone', '')}</code>\n"
                f"Assigned Worker Terminal: <code>{kwargs.get('node_id', 'ONLINE')}</code>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং প্যারামিটার সেট করতে নিচে <b>START</b> বাটন চাপুন:"
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
                f"Worker Node: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            ),
            "no_worker_available": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"এই মুহূর্তে ক্লাস্টারের সকল রিমোট টার্মিনাল ব্যস্ত আছে। "
                f"অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন অথবা টার্মিনাল খালি হওয়া পর্যন্ত অপেক্ষা করুন।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে এবং রিমোট ব্রাউজার ডিসকানেক্ট করা হয়েছে। "
                f"নতুন সেশনের জন্য /start পাঠান।"
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
                f"Account: <code>{kwargs.get('phone', '')}</code>\n"
                f"Assigned Worker Terminal: <code>{kwargs.get('node_id', 'ONLINE')}</code>\n\n"
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
                f"Worker Node: <code>{kwargs.get('node_id', '')}</code>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: Martingale engine running smoothly."
            ),
            "no_worker_available": (
                f"<b>{to_bold('ALL TERMINALS OCCUPIED')}</b>\n\n"
                f"All cluster terminals are currently busy. Please wait for an available node or retry shortly."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser session closed cleanly. Send /start to begin a new session."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==========================================
# 7. Interactive Inline Keyboards
# ==========================================
def get_credentials_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data=f"ask_num:{sid}"),
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
    u = db.user_states.get(int(sid.split("_")[0]), {})
    t_val = u.get("target_profit", 0)
    s_val = u.get("total_steps", 7)

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
    chat_id = int(sid.split("_")[0])
    u = db.user_states.get(chat_id, {})
    u["anim_tick"] = u.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[u["anim_tick"] % len(SPINNER_FRAMES)]

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

# ==========================================
# 8. Frame Dispatcher & Image Handler
# ==========================================
def display_or_replace_photo(chat_id, image_path, caption_text, reply_markup=None):
    sess = db.get_session(chat_id)
    last_photo_msg_id = sess.get("live_photo_message_id")
    replaced = False

    if last_photo_msg_id and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as ph:
                media = InputMediaPhoto(ph, caption=caption_text, parse_mode="HTML")
                bot.edit_message_media(
                    media=media,
                    chat_id=chat_id,
                    message_id=last_photo_msg_id,
                    reply_markup=reply_markup
                )
            replaced = True
        except Exception:
            replaced = False

    if not replaced and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as ph:
                msg = bot.send_photo(
                    chat_id, ph,
                    caption=caption_text,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
                db.set_session(chat_id, {"live_photo_message_id": msg.message_id})
        except Exception as e:
            print(f"[*] Photo replace error: {e}")

def handle_incoming_worker_frame(chat_id, node_id, status, live_bal, wins, losses, step_level, img_b64):
    try:
        raw_bytes = base64.b64decode(img_b64)
        file_path = os.path.join(MASTER_TEMP_DIR, f"frame_{chat_id}.png")
        with open(file_path, "wb") as f:
            f.write(raw_bytes)

        u = db.user_states.get(chat_id, {})
        sid = u.get("active_sid", f"{chat_id}_0")
        site_name = u.get("site_name", "WinGo 30S")
        start_b = u.get("start_bal", 0.0)
        target_total = start_b + u.get("target_profit", 0.0)

        caption = (
            f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
            f"Platform: <b>{site_name}</b>\n"
            f"Worker Terminal: <code>{node_id}</code>\n"
            f"Live Balance: <code>৳ {float(live_bal):.2f}</code>\n"
            f"Target Balance: <code>৳ {target_total:.2f}</code>\n"
            f"Current Level: <b>Step {step_level}/{u.get('total_steps', 7)}</b>\n"
            f"Record: <b>{wins} Wins</b> | <b>{losses} Losses</b>\n\n"
            f"Time: <code>{time.strftime('%H:%M:%S')}</code>\n"
            f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
        )

        display_or_replace_photo(chat_id, file_path, caption, get_trading_control_keyboard(sid))

        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"[*] Frame processing error: {e}")

def handle_session_completion(chat_id, node_id, reason, final_bal, img_b64):
    try:
        u = db.user_states.get(chat_id, {})
        start_b = u.get("start_bal", 0.0)
        profit = float(final_bal) - start_b

        msg = (
            f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
            f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
            f"Worker Terminal: <code>{node_id}</code>\n"
            f"শুরুর ব্যালেন্স: <code>৳ {start_b:.2f}</code>\n"
            f"সর্বশেষ ব্যালেন্স: <code>৳ {float(final_bal):.2f}</code>\n"
            f"অর্জিত মোট প্রফিট: <code>+৳ {profit:.2f}</code>\n\n"
            f"রিমোট ব্রাউজার নিরাপদভাবে বন্ধ করা হয়েছে।"
        )

        if img_b64:
            raw_bytes = base64.b64decode(img_b64)
            file_path = os.path.join(MASTER_TEMP_DIR, f"final_{chat_id}.png")
            with open(file_path, "wb") as f:
                f.write(raw_bytes)
            display_or_replace_photo(chat_id, file_path, msg, None)
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            bot.send_message(chat_id, msg)

        db.remove_session(chat_id)
    except Exception as e:
        print(f"[*] Completion error: {e}")

# ==========================================
# 9. Telegram Commands & Admin Panel
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    db.user_states[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn",
        "chat_id": chat_id
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
        bot.send_message(chat_id, f"<b>{to_bold('ACCESS DENIED')}</b>\nএই কমান্ডটি শুধুমাত্র অনারের জন্য সংরক্ষিত।")
        return

    snapshot = db.get_cluster_snapshot()
    
    # প্রিমিয়াম ভিআইপি আসকি ফ্রেম ফরম্যাটিং (কোন অপ্রয়োজনীয় ইমোজি ছাড়া)
    header = "┌──────────────────────────────┐\n│ CLUSTER TERMINAL STATUS\n├──────────────────────────────┤\n"
    counts = (
        f"│ Total Registered Nodes: {snapshot['total']}\n"
        f"│ Active / Running: {snapshot['busy']}\n"
        f"│ Idle / Free: {snapshot['idle']}\n"
        f"│ Offline / Dead: {snapshot['offline']}\n"
        f"├──────────────────────────────┤\n"
    )
    
    body_lines = []
    for rec in snapshot["records"]:
        nid = rec["node_id"]
        st = rec["status"]
        if st == "BUSY":
            user_lbl = f"User: {rec['chat_id']}"
        elif st == "OFFLINE":
            user_lbl = f"Timeout: {rec['heartbeat_age']}s"
        else:
            user_lbl = "Heartbeat: OK"
        body_lines.append(f"│ Node: {nid} | Status: {st} | {user_lbl}")

    if not body_lines:
        body_lines.append("│ No nodes currently connected.")

    footer = "\n└──────────────────────────────┘"

    full_box = f"<code>{header}{counts}" + "\n".join(body_lines) + f"{footer}</code>"
    
    bot.send_message(
        chat_id,
        f"<b>{to_bold('MASTER CLUSTER AUDIT PANEL')}</b>\n\n{full_box}\n\n"
        f"bKash: <code>{PAYMENT_BKASH}</code>\n"
        f"Nagad: <code>{PAYMENT_NAGAD}</code>\n"
        f"Telegram Channels:\n"
        f"• {CHANNEL_DARK67}\n"
        f"• {CHANNEL_BDWIN24}"
    )

# ==========================================
# 10. Interactive Callback Query Handler
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    # ১. ভাষা নির্বাচন
    if action in ["lang_en", "lang_bn"]:
        u = db.user_states.setdefault(chat_id, {})
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

    # ২. প্ল্যাটফর্ম নির্বাচন
    elif action in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if action == "site_amarclub" else "DK Win"
        sid = f"{chat_id}_{int(time.time()) % 1000000}"

        u = db.user_states.setdefault(chat_id, {})
        u["active_sid"] = sid
        u["site_name"] = site_name
        u["phone"] = None
        u["password"] = None
        u["target_profit"] = 0
        u["total_steps"] = 7
        u["created_at"] = time.time()
        u["cred_card_msg_id"] = call.message.message_id

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )

    # ৩. ফোন নাম্বার ইনপুট বাটন
    elif action == "ask_num":
        u = db.user_states.setdefault(chat_id, {})
        u["input_mode"] = "WAITING_PHONE"
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        u["temp_prompt_id"] = prompt_m.message_id

    # ৪. পাসওয়ার্ড ইনপুট বাটন
    elif action == "ask_pass":
        u = db.user_states.setdefault(chat_id, {})
        if not u.get("phone"):
            bot.answer_callback_query(call.id, "দয়া করে নাম্বারটি আগে দিন।", show_alert=True)
            return
        u["input_mode"] = "WAITING_PASS"
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        u["temp_prompt_id"] = prompt_m.message_id

    # ৫. START বাটন (প্যারামিটার স্ক্রিন লোড করা)
    elif action == "start_cfg":
        u = db.user_states.get(chat_id, {})
        bot.answer_callback_query(call.id, "প্যারামিটার সেটিংস প্রস্তুত করা হচ্ছে...")
        sid = u.get("active_sid", f"{chat_id}_0")
        
        caption = (
            f"<b>{to_bold('WINGO 30S MARKET CONFIG')}</b>\n\n"
            f"Platform: <b>{u.get('site_name', '')}</b>\n"
            f"Live Balance: <code>৳ {u.get('current_balance', 0.0):.2f}</code>\n\n"
            f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
        )
        bot.send_message(chat_id, caption, reply_markup=get_setup_param_keyboard(sid))

    # ৬. TARGET প্রফিট বাটন
    elif action == "set_tgt":
        u = db.user_states.get(chat_id, {})
        u["input_mode"] = "WAITING_TARGET"
        bot.answer_callback_query(call.id)
        cur_b = u.get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{cur_b:.2f}"))
        u["temp_prompt_id"] = p_msg.message_id

    # ৭. MARTINGALE STEPS বাটন
    elif action == "set_stp":
        u = db.user_states.get(chat_id, {})
        u["input_mode"] = "WAITING_STEPS"
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=u.get("target_profit", 0)))
        u["temp_prompt_id"] = p_msg.message_id

    # ৮. RUN AUTOMATION বাটন
    elif action == "run_auto":
        u = db.user_states.get(chat_id, {})
        if not u.get("target_profit") or u["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        sess = db.get_session(chat_id)
        assigned_node = sess.get("node_id")

        if not assigned_node:
            bot.answer_callback_query(call.id, "টার্মিনাল ডিসকানেক্টেড!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন রিমোটে সক্রিয় করা হচ্ছে...")

        task_payload = {
            "action": "START_TRADING",
            "chat_id": chat_id,
            "target_profit": u["target_profit"],
            "total_steps": u["total_steps"],
            "timestamp": time.time()
        }
        db.assign_task(assigned_node, task_payload)

        cur_b = u.get("current_balance", 0.0)
        target_total = cur_b + u["target_profit"]
        u["start_bal"] = cur_b

        dashboard_caption = get_text(
            chat_id, "running_dashboard",
            site_name=u.get("site_name", "Amar Club"),
            node_id=assigned_node,
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=u["total_steps"]
        )
        bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(u["active_sid"]))

    # ৯. SHOT বাটন (ম্যানুয়াল ফ্রেম রিকোয়েস্ট)
    elif action == "shot":
        sess = db.get_session(chat_id)
        assigned_node = sess.get("node_id")
        if assigned_node:
            db.assign_task(assigned_node, {"action": "CAPTURE_FRAME", "chat_id": chat_id})
            bot.answer_callback_query(call.id, "রিমোট টার্মিনাল থেকে ফুটেজ আনা হচ্ছে...")
        else:
            bot.answer_callback_query(call.id, "কোনো নোড সংযুক্ত নেই", show_alert=True)

    # ১০. BAL বাটন
    elif action == "bal":
        sess = db.get_session(chat_id)
        bal = sess.get("live_balance", "0.00")
        bot.answer_callback_query(call.id, f"Live Balance: ৳ {float(bal):.2f}", show_alert=True)

    # ১১. STATS বাটন
    elif action == "stats":
        sess = db.get_session(chat_id)
        u = db.user_states.get(chat_id, {})
        stat_txt = (
            f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
            f"Terminal: <code>{sess.get('node_id', 'N/A')}</code>\n"
            f"লাইভ ব্যালেন্স: <code>৳ {float(sess.get('live_balance', 0.0)):.2f}</code>\n"
            f"টার্গেট ব্যালেন্স: <code>৳ {u.get('start_bal', 0.0) + u.get('target_profit', 0.0):.2f}</code>\n"
            f"মার্টিনগেল লেভেল: <b>Step {sess.get('step_level', 1)}/{u.get('total_steps', 7)}</b>\n"
            f"উইন: <b>{sess.get('wins', 0)}</b> | লস: <b>{sess.get('losses', 0)}</b>"
        )
        bot.send_message(chat_id, stat_txt)

    # ১২. STOP বাটন
    elif action == "stop":
        sess = db.get_session(chat_id)
        assigned_node = sess.get("node_id")
        if assigned_node:
            db.assign_task(assigned_node, {"action": "PAUSE_TRADING", "chat_id": chat_id})
        bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং অটোমেশন সাময়িকভাবে থামানো হয়েছে।")

    # ১৩. CANCEL বাটন (ট্যাব অটোমেটিক কেটে দেওয়া ও সেশন মুছে ফেলা)
    elif action == "cancel":
        sess = db.get_session(chat_id)
        assigned_node = sess.get("node_id")
        if assigned_node:
            db.assign_task(assigned_node, {"action": "TERMINATE_SESSION", "chat_id": chat_id})
        db.remove_session(chat_id)
        safe_delete_message(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, "সেশন ক্লোজ করা হয়েছে")
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==========================================
# 11. Text Handler & Dispatch Logic
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()

    u = db.user_states.get(chat_id)
    if not u:
        return

    input_mode = u.get("input_mode")
    safe_delete_message(chat_id, message.message_id)

    if u.get("temp_prompt_id"):
        safe_delete_message(chat_id, u["temp_prompt_id"])
        u["temp_prompt_id"] = None

    if input_mode == "WAITING_PHONE":
        u["phone"] = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            try:
                masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_card_text = (
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"প্ল্যাটফর্ম: <b>{u.get('site_name', '')}</b>\n"
                    f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                    f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
                )
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=u["cred_card_msg_id"],
                    reply_markup=get_credentials_keyboard(u["active_sid"])
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        u["password"] = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            safe_delete_message(chat_id, u["cred_card_msg_id"])
            u["cred_card_msg_id"] = None

        idle_node = db.get_idle_node()
        if not idle_node:
            bot.send_message(chat_id, get_text(chat_id, "no_worker_available"))
            return

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Allocating isolated profile...</code>")

        login_task = {
            "action": "INIT_LOGIN",
            "chat_id": chat_id,
            "site": "amarclub" if "AMAR" in u.get("site_name", "").upper() else "dkwin",
            "site_name": u.get("site_name", "Amar Club"),
            "phone": u["phone"],
            "password": u["password"],
            "anim_msg_id": anim_msg.message_id,
            "timestamp": time.time()
        }

        db.assign_task(idle_node, login_task)
        db.set_session(chat_id, {
            "node_id": idle_node,
            "status": "CONNECTING"
        })

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            u["target_profit"] = val
            u["input_mode"] = None
            cur_b = u.get("current_balance", 0.0)
            caption = (
                f"<b>{to_bold('WINGO 30S MARKET CONFIG')}</b>\n\n"
                f"Platform: <b>{u.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_b:.2f}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            bot.send_message(chat_id, caption, reply_markup=get_setup_param_keyboard(u["active_sid"]))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            u["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            u["total_steps"] = steps_val
            u["input_mode"] = None
            cur_b = u.get("current_balance", 0.0)
            caption = (
                f"<b>{to_bold('WINGO 30S MARKET CONFIG')}</b>\n\n"
                f"Platform: <b>{u.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_b:.2f}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            bot.send_message(chat_id, caption, reply_markup=get_setup_param_keyboard(u["active_sid"]))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            u["temp_prompt_id"] = p_msg.message_id

# ==========================================
# 12. Continuous 24h Lifetime Watchdog
# ==========================================
def continuous_24h_master_watchdog():
    while True:
        try:
            now = time.time()
            for chat_id, u in list(db.user_states.items()):
                created_at = u.get("created_at", now)
                if now - created_at >= 86400: # ২৪ ঘণ্টা পার হয়ে গেলে
                    sess = db.get_session(chat_id)
                    assigned_node = sess.get("node_id")
                    if assigned_node:
                        db.assign_task(assigned_node, {"action": "TERMINATE_SESSION", "chat_id": chat_id})
                    db.remove_session(chat_id)
                    db.user_states.pop(chat_id, None)
                    try:
                        bot.send_message(chat_id, f"<b>{to_bold('24 HOURS REACHED')}</b>\nআপনার ২৪ ঘণ্টার সময়সীমা পূর্ণ হওয়ায় সেশন নিরাপদভাবে শেষ করা হয়েছে।")
                    except Exception:
                        pass
        except Exception:
            pass
        time.sleep(1800)

threading.Thread(target=continuous_24h_master_watchdog, daemon=True).start()

# ==========================================
# 13. Main Master Process Loop
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO MASTER CLUSTER CONTROLLER ONLINE')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
