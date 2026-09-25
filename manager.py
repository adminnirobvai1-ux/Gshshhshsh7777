import os
import sys
import time
import json
import threading
import urllib.request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8808949150:AAFXYTFIkyJHmJxIFdEanv2rvDhABnNMATI"
FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_sessions = {}

PLATFORMS = {
    "site_amarclub": {
        "name": "Amar Club",
        "login": "https://amarclub1.com/#/login",
        "wingo": "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_dkwin": {
        "name": "DK Win",
        "login": "https://dkwin6.com/#/login",
        "wingo": "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    }
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

def firebase_sync_http(path: str, method: str = "GET", payload=None):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=raw_data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4.0) as res:
            data = res.read()
            return json.loads(data.decode("utf-8")) if data else None
    except Exception:
        return None

def get_best_worker():
    terminals = firebase_sync_http("terminals", "GET") or {}
    now = time.time()
    for tid, tval in terminals.items():
        if isinstance(tval, dict) and tval.get("status") == "FREE":
            if now - float(tval.get("heartbeat", 0)) < 10.0:
                return tid
    return list(terminals.keys())[0] if terminals else None

@bot.message_handler(commands=['start'])
def handle_start(msg):
    markup = InlineKeyboardMarkup(row_width=2)
    for k, v in PLATFORMS.items():
        markup.add(InlineKeyboardButton(to_bold(v["name"]), callback_data=f"sel_site:{k}"))
    bot.send_message(msg.chat.id, f"<b>{to_bold('WINGO 30S CLOUD CONTROLLER')}</b>\n\nट्रेडिंग प्लेटफ़ॉर्म चुनें:", reply_markup=markup)

@bot.callback_query_handler(func=lambda c: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data.split(":")
    action = data[0]

    if action == "sel_site":
        site_key = data[1]
        sid = f"sess_{chat_id}_{int(time.time())}"
        user_sessions[chat_id] = {"sid": sid, "site": site_key}
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(to_bold("नंबर दर्ज करें"), callback_data=f"ask_num:{sid}"))
        bot.edit_message_text(f"<b>{to_bold('लॉगिन क्रेडेंशियल')}</b>\n\nप्लेटफ़ॉर्म: <b>{PLATFORMS[site_key]['name']}</b>", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif action == "ask_num":
        user_sessions[chat_id]["mode"] = "INPUT_PHONE"
        bot.send_message(chat_id, "अपना फ़ोन नंबर भेजें:")

    elif action == "start_trade":
        sid = data[1]
        w_id = user_sessions[chat_id].get("worker_id")
        if w_id:
            firebase_sync_http(f"terminals/{w_id}/task", "PUT", {
                "type": "START_TRADE",
                "session_id": sid,
                "target_profit": user_sessions[chat_id].get("target", 200),
                "total_steps": 5
            })
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(to_bold("बैलेंस और स्टैट्स"), callback_data=f"get_stats:{sid}"))
            markup.add(InlineKeyboardButton(to_bold("स्टॉप"), callback_data=f"stop:{sid}"))
            bot.send_message(chat_id, f"<b>{to_bold('ऑटो-ट्रेडिंग शुरू हो चुकी है')}</b>\nबैकग्राउंड में सुरक्षित रूप से ट्रेड चल रहा है।", reply_markup=markup)

    elif action == "get_stats":
        sid = data[1]
        stats = firebase_sync_http(f"live_stats/{sid}", "GET")
        if stats:
            txt = (f"<b>{to_bold('लाइव रिपोर्ट')}</b>\n\n"
                   f"बैलेंस: <code>৳ {stats.get('curBal', 0)}</code>\n"
                   f"जीत: <b>{stats.get('w', 0)}</b> | हार: <b>{stats.get('l', 0)}</b>")
            bot.answer_callback_query(call.id, f"बैलेंस: ৳ {stats.get('curBal', 0)}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "डेटा सिंक हो रहा है...", show_alert=True)

    elif action == "stop":
        sid = data[1]
        w_id = user_sessions[chat_id].get("worker_id")
        if w_id:
            firebase_sync_http(f"terminals/{w_id}/task", "PUT", {"type": "STOP", "session_id": sid})
        bot.send_message(chat_id, "ट्रेडिंग सफलतापूर्वक रोक दी गई है।")

@bot.message_handler(func=lambda msg: True)
def handle_text(msg):
    chat_id = msg.chat.id
    u = user_sessions.get(chat_id, {})
    mode = u.get("mode")

    if mode == "INPUT_PHONE":
        u["phone"] = msg.text.strip()
        u["mode"] = "INPUT_PWD"
        bot.send_message(chat_id, "अपना पासवर्ड भेजें:")
    elif mode == "INPUT_PWD":
        u["password"] = msg.text.strip()
        u["mode"] = None
        sid = u["sid"]
        worker = get_best_worker()

        if not worker:
            bot.send_message(chat_id, "कोई भी वर्कर नोड अभी एक्टिव नहीं है! कृपया worker.py चलाएं।")
            return

        u["worker_id"] = worker
        bot.send_message(chat_id, "लॉगिन प्रोसेस शुरू किया जा रहा है...")

        p_info = PLATFORMS[u["site"]]
        firebase_sync_http(f"terminals/{worker}/task", "PUT", {
            "type": "LOGIN",
            "session_id": sid,
            "login_url": p_info["login"],
            "phone": u["phone"],
            "password": u["password"]
        })

        # लॉगिन स्टेटस मॉनिटरिंग थ्रेड
        def check_status():
            for _ in range(25):
                time.sleep(1.5)
                res = firebase_sync_http(f"task_results/{sid}", "GET")
                if res and res.get("status") == "LOGIN_DONE":
                    firebase_sync_http(f"task_results/{sid}", "DELETE")
                    firebase_sync_http(f"terminals/{worker}/task", "PUT", {
                        "type": "NAV_WINGO",
                        "session_id": sid,
                        "wingo_url": p_info["wingo"]
                    })
                    break
            
            for _ in range(20):
                time.sleep(1.5)
                w_res = firebase_sync_http(f"task_results/{sid}", "GET")
                if w_res and w_res.get("status") == "WINGO_READY":
                    bal = w_res.get("balance", 0)
                    markup = InlineKeyboardMarkup()
                    markup.add(InlineKeyboardButton(to_bold("ट्रेड शुरू करें"), callback_data=f"start_trade:{sid}"))
                    bot.send_message(chat_id, f"<b>{to_bold('लॉगिन सफल')}</b>\n\nलाइव बैलेंस: <code>৳ {bal:.2f}</code>", reply_markup=markup)
                    return

        threading.Thread(target=check_status, daemon=True).start()

if __name__ == "__main__":
    print("[*] Telegram Manager Started...")
    bot.infinity_polling(skip_pending=True)
