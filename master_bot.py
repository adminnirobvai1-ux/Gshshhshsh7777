import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket
import uuid
import random
import string

# ==============================================================================
# 1. Automatic Package Installer
# ==============================================================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing package: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")
install_and_import("requests")

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==============================================================================
# 2. Mathematical Bold Unicode & Utility Functions
# ==============================================================================
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

def generate_random_key(length=10):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# ==============================================================================
# 3. Global Configurations & State Management
# ==============================================================================
TOKEN = os.getenv("BOT_TOKEN", "8808949150:AAGH4C0gvx48tjxDQYqxqPnJ3CoEIMhM8yc")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

OWNER_USERNAME = "MD_NAYEEM_DRX_TM"
CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"
OWNER_URL = "https://t.me/MD_NAYEEM_DRX_TM"

FIREBASE_DB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# Cluster node identity
NODE_ID = f"NODE_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6].upper()}"
IS_MASTER = False
CLUSTER_RUNNING = True

user_sessions = {}
active_sessions = {}

# ==============================================================================
# 4. Firebase Realtime Database REST API Client
# ==============================================================================
class FirebaseClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')

    def _url(self, path):
        clean_path = path.strip('/')
        return f"{self.base_url}/{clean_path}.json"

    def get(self, path):
        try:
            r = requests.get(self._url(path), timeout=7)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[*] Firebase GET error [{path}]: {e}")
        return None

    def put(self, path, data):
        try:
            r = requests.put(self._url(path), json=data, timeout=7)
            return r.status_code in [200, 201, 204]
        except Exception as e:
            print(f"[*] Firebase PUT error [{path}]: {e}")
            return False

    def patch(self, path, data):
        try:
            r = requests.patch(self._url(path), json=data, timeout=7)
            return r.status_code in [200, 201, 204]
        except Exception as e:
            print(f"[*] Firebase PATCH error [{path}]: {e}")
            return False

    def delete(self, path):
        try:
            r = requests.delete(self._url(path), timeout=7)
            return r.status_code in [200, 204]
        except Exception as e:
            print(f"[*] Firebase DELETE error [{path}]: {e}")
            return False

firebase = FirebaseClient(FIREBASE_DB_URL)

# ==============================================================================
# 5. Distributed Cluster Engine & Master Election
# ==============================================================================
def register_node():
    node_payload = {
        "node_id": NODE_ID,
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "status": "FREE",
        "assigned_user_id": None,
        "site": None,
        "expires_at": 0,
        "heartbeat": time.time(),
        "command": None,
        "role": "WORKER"
    }
    firebase.put(f"/terminals/{NODE_ID}", node_payload)
    print(f"[*] Node registered successfully: {NODE_ID}")

def node_heartbeat_worker():
    global IS_MASTER
    while CLUSTER_RUNNING:
        try:
            firebase.patch(f"/terminals/{NODE_ID}", {
                "heartbeat": time.time(),
                "role": "MASTER" if IS_MASTER else "WORKER"
            })
            
            # Check for remote commands on this specific node
            node_data = firebase.get(f"/terminals/{NODE_ID}")
            if node_data:
                cmd = node_data.get("command")
                if cmd == "FORCE_KILL":
                    print(f"[*] FORCE_KILL command received for {NODE_ID}. Resetting node...")
                    for sid in list(active_sessions.keys()):
                        close_session_tab(sid)
                    firebase.patch(f"/terminals/{NODE_ID}", {
                        "status": "FREE",
                        "assigned_user_id": None,
                        "site": None,
                        "expires_at": 0,
                        "command": None
                    })
                elif isinstance(cmd, dict) and cmd.get("action") == "START_SESSION":
                    # Remote trigger for browser automation
                    sid = cmd.get("sid")
                    chat_id = cmd.get("chat_id")
                    phone = cmd.get("phone")
                    pwd = cmd.get("password")
                    site_name = cmd.get("site_name")
                    firebase.patch(f"/terminals/{NODE_ID}", {"command": None})
                    if sid and phone and pwd:
                        active_sessions[sid] = {
                            "chat_id": chat_id,
                            "session_id": sid,
                            "site_name": site_name,
                            "phone": phone,
                            "password": pwd,
                            "target_profit": 0,
                            "total_steps": 7,
                            "is_trading": False,
                            "created_at": time.time(),
                            "anim_tick": 0,
                            "lock": threading.RLock()
                        }
                        threading.Thread(
                            target=process_login,
                            args=(chat_id, sid, phone, pwd, None),
                            daemon=True
                        ).start()
        except Exception as e:
            print(f"[*] Heartbeat error: {e}")
        time.sleep(5)

def master_election_daemon():
    global IS_MASTER
    while CLUSTER_RUNNING:
        try:
            master_data = firebase.get("/cluster/active_master")
            now = time.time()
            needs_election = False
            
            if not master_data:
                needs_election = True
            else:
                last_hb = master_data.get("heartbeat", 0)
                if now - last_hb > 15:
                    print("[*] Master heartbeat expired. Initiating failover election...")
                    needs_election = True

            if needs_election:
                claim_payload = {
                    "master_id": NODE_ID,
                    "heartbeat": now,
                    "started_at": now
                }
                success = firebase.put("/cluster/active_master", claim_payload)
                if success:
                    time.sleep(1)
                    verified = firebase.get("/cluster/active_master")
                    if verified and verified.get("master_id") == NODE_ID:
                        if not IS_MASTER:
                            print(f"[👑] Master lock acquired by {NODE_ID}. Starting Telegram Polling...")
                            IS_MASTER = True
                            threading.Thread(target=start_telegram_polling, daemon=True).start()
                    else:
                        IS_MASTER = False
            else:
                if master_data and master_data.get("master_id") == NODE_ID:
                    firebase.patch("/cluster/active_master", {"heartbeat": now})
                    IS_MASTER = True
                else:
                    IS_MASTER = False
        except Exception as e:
            print(f"[*] Master election error: {e}")
        time.sleep(5)

def cluster_watchdog_thread():
    while CLUSTER_RUNNING:
        try:
            now = time.time()
            terminals = firebase.get("/terminals") or {}
            for t_id, t_info in terminals.items():
                if not isinstance(t_info, dict):
                    continue
                exp = t_info.get("expires_at", 0)
                status = t_info.get("status")
                user_id = t_info.get("assigned_user_id")

                if status == "BUSY" and exp > 0 and now >= exp:
                    print(f"[*] 24h Session expired for terminal {t_id}, user {user_id}")
                    if t_id == NODE_ID:
                        for sid in list(active_sessions.keys()):
                            close_session_tab(sid)
                    firebase.patch(f"/terminals/{t_id}", {
                        "status": "FREE",
                        "assigned_user_id": None,
                        "site": None,
                        "expires_at": 0,
                        "command": None
                    })
                    if user_id:
                        try:
                            bot.send_message(
                                user_id,
                                f"<b>{to_bold('SESSION EXPIRED')}</b>\n"
                                "আপনার ২৪ ঘণ্টার সেশন শেষ হয়েছে। নতুন পাসওয়ার্ড সংগ্রহ করে পুনরায় শুরু করুন।"
                            )
                        except Exception:
                            pass
        except Exception as e:
            print(f"[*] Cluster watchdog error: {e}")
        time.sleep(30)

# ==============================================================================
# 6. Selenium Isolation Driver Management
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("-profile")
    options.add_argument(profile_dir)
    
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_window_size(390, 844)
    driver.get(target_url)
    
    sess["driver"] = driver
    sess["window_handle"] = driver.current_window_handle
    return driver, sess["window_handle"]

def safe_tab_execute(sid, task_fn):
    sess = active_sessions.get(sid)
    if not sess:
        return None
        
    lock = sess.get("lock")
    driver = sess.get("driver")
    
    if not driver or not lock:
        return None

    with lock:
        try:
            return task_fn(driver)
        except Exception as e:
            print(f"[*] Execute error for {sid}: {e}")
            return None

def close_session_tab(session_id):
    sess = active_sessions.pop(session_id, None)
    if sess:
        sess["is_trading"] = False
        driver = sess.get("driver")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        
        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

# ==============================================================================
# 7. Telegram Smart Image Engine
# ==============================================================================
def display_or_replace_photo(chat_id, session_id, image_path, caption_text, reply_markup=None):
    sess = active_sessions.get(session_id, {})
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
                sess["live_photo_message_id"] = msg.message_id
        except Exception as e:
            print(f"[*] Photo replace error: {e}")

# ==============================================================================
# 8. Unminified Core JavaScript Payloads (100% Preserved)
# ==============================================================================
AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
  window.location.hash = '#/login';
}

const initDialogConfirm = document.querySelector('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], .van-button--primary');
if (initDialogConfirm) {
    try { initDialogConfirm.click(); } catch(e){}
}

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input');

let elP = document.querySelector('input[type="password"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input');

let elL = document.querySelector('button[type="submit"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');

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
  }, 700);
}, 700);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const dText = dialog.innerText || '';
    if (dText.includes('already logged in') || dText.includes('somewhere else') || 
        dText.includes('logged in') || dText.includes('22') || dText.includes('other device') ||
        dText.includes('Confirm') || dText.includes('Determine') || dText.includes('continue')) {
        const confirmBtn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm"], .van-button--danger, .van-button--primary, button');
        if (confirmBtn) {
            try { confirmBtn.click(); } catch(e){}
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed already logged in prompt" };
        }
    }
}

const isBonusModal = bodyText.includes('BONUS DAILY RECHARGE') || 
                     bodyText.includes('DAILY RECHARGE') || 
                     bodyText.includes('Daily Bonus') ||
                     bodyText.includes('Deposit Bonus') ||
                     bodyText.includes('Announcement');

if (isBonusModal) {
    const confirmBtn = document.querySelector('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], button[class*="close"], .van-popup__close-icon');
    if (confirmBtn) {
        try { confirmBtn.click(); } catch(e){}
    }
    return { status: "SUCCESS" };
}

try {
    const t1 = localStorage.getItem('token') || localStorage.getItem('token_str') || localStorage.getItem('auth');
    const t2 = sessionStorage.getItem('token') || sessionStorage.getItem('auth');
    if (t1 || t2) {
        return { status: "SUCCESS" };
    }
} catch(e){}

if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) {
    return { status: "SUCCESS" };
}

const toast = document.querySelector('.van-toast--text, .van-toast--fail, .van-toast');
if (toast && toast.innerText && toast.innerText.trim().length > 0) {
    const t = toast.innerText.trim();
    if (t.includes('already logged in') || t.includes('somewhere else') || t.includes('22')) {
        const loginBtn = document.querySelector('button[type="submit"], body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');
        if (loginBtn) {
            try { loginBtn.click(); } catch(e){}
        }
        return { status: "PENDING", message: "Handling session takeover..." };
    }
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('Account does not exist') || t.includes('frozen')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

WINGO_RUNBOX_AND_CLICK_JS = """
(function(){
    if (!document.getElementById('_run_box')) {
        let d = [{"name": "Wingo", "sel": "body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img"}],
            b = document.createElement('div');
        b.id = '_run_box';
        b.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#18181b;padding:6px 10px;border-radius:30px;display:flex;gap:6px;align-items:center;z-index:99999999;box-shadow:0 6px 16px rgba(0,0,0,0.3);font:12px sans-serif;';
        
        let all = document.createElement('button');
        all.innerText = '▶ All';
        all.style.cssText = 'background:#f59e0b;color:#000;border:none;padding:4px 8px;border-radius:20px;cursor:pointer;font-weight:bold;font-size:11px;';
        all.onclick = () => {
            d.forEach((x, i) => {
                setTimeout(() => {
                    let el = document.querySelector(x.sel);
                    if (el) el.click();
                }, i * 400);
            });
        };
        b.appendChild(all);

        d.forEach(x => {
            let btn = document.createElement('button');
            btn.innerText = x.name;
            btn.style.cssText = 'background:#22c55e;color:#000;border:none;padding:4px 8px;border-radius:20px;cursor:pointer;font-weight:bold;font-size:11px;';
            btn.onclick = () => {
                let el = document.querySelector(x.sel);
                if (el) el.click();
            };
            b.appendChild(btn);
        });

        let x = document.createElement('span');
        x.innerText = '✕';
        x.style.cssText = 'cursor:pointer;color:#a1a1aa;margin-left:4px;font-weight:bold;';
        x.onclick = () => b.remove();
        b.appendChild(x);
        document.body.appendChild(b);
    }

    let target = document.querySelector("body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img");
    if (target) {
        target.click();
        return "CLICKED_SELECTOR";
    }
    let alt = document.querySelector("div[class*='wingo' i], img[src*='wingo' i]");
    if (alt) {
        alt.click();
        return "CLICKED_ALT";
    }
    return "INJECTED_WAITING";
})();
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

const dismissBtns = document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close"], .van-dialog button');
dismissBtns.forEach(btn => { try { btn.click(); } catch(e){} });

if (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Win Go') || bodyText.includes('30S') || bodyText.includes('Time remaining')) {
    return true;
}
return false;
"""

FETCH_BALANCE_JS = """
let els = document.querySelectorAll('*');
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.includes('Wallet balance') || txt.includes('Balance')) {
        let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
        let match = parentTxt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
        if (match) return parseFloat(match[1].replace(/,/g, ''));
    }
}
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.trim().match(/^[৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)) {
        return parseFloat(txt.replace(/[^\\d.]/g, ''));
    }
}
return 0;
"""

WINGO_CORE_JS = """
const autoTargetProfit = arguments[0];
const autoTotalSteps = arguments[1];

(function(){
    if(document.getElementById('sys-core-fin')) {
        let tIn = document.querySelector('#sys-core-fin input[placeholder*="TARGET"]');
        let sIn = document.querySelector('#sys-core-fin input[placeholder*="STEPS"]');
        let btn = document.querySelector('#sys-core-fin button');
        if (tIn && sIn && btn) {
            tIn.value = autoTargetProfit;
            sIn.value = autoTotalSteps;
            btn.click();
        }
        return "ALREADY_EXISTS_RESTARTED";
    }

    const uF=s=>String(s).toUpperCase().split('').map(c=>{
        let n=c.charCodeAt(0);
        if(n>=65&&n<=90)return String.fromCodePoint(n+119743);
        if(n>=48&&n<=57)return String.fromCodePoint(n+120764);
        return c;
    }).join('');

    const cfg={fRt:300,syncDly:2500,minSf:10};
    let st={
        isRun:false,
        startBal:0,
        tgtAmt:0,
        curBal:0,
        autoInt:null,
        preScn:null,
        isTrd:false,
        stpIdx:0,
        dynSeq:[],
        totalSteps:autoTotalSteps || 7,
        tradesDone:0,
        lastPred:null,
        lastPeriod:null,
        balanceCheckInterval:null,
        manualOverrideBet:null,
        w:0,
        l:0,
        cur_w_streak:0,
        cur_l_streak:0,
        max_w_streak:0,
        max_l_streak:0
    };

    window.__WINGO_ST = st;

    let curApiIdx=0,isFetchingApi=false;
    const VoiceEngine={
        speak(msg,lang='en-US',rate=1.1){
            if(!('speechSynthesis' in window))return;
            try{
                window.speechSynthesis.cancel();
                let utter=new SpeechSynthesisUtterance(msg);
                utter.lang=lang;
                utter.rate=rate;
                utter.pitch=1.2;
                utter.volume=1;
                window.speechSynthesis.speak(utter);
            }catch(e){}
        }
    };

    let dTimeLeft=30;
    setInterval(()=>{
        let uClk=document.getElementById('ui-clk');
        if(uClk){
            let minutes=Math.floor(dTimeLeft/60),seconds=dTimeLeft%60;
            uClk.textContent=uF(String(minutes).padStart(2,'0') + ':' + String(seconds).padStart(2,'0'));
        }
        dTimeLeft--;
        if(dTimeLeft<0)dTimeLeft=30;
    },1000);

    let lkOvl=document.createElement('div');
    lkOvl.id='drx-lck-bg';
    lkOvl.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.01);z-index:9999997;display:none;';
    lkOvl.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();},true);
    document.body.appendChild(lkOvl);

    function chkBal(){
        let els=document.querySelectorAll('*');
        for(let i=0;i<els.length;i++){
            let txt=els[i].innerText||'';
            if(txt.includes('Wallet balance')||txt.includes('Balance')){
                let parentTxt=(els[i].parentNode&&els[i].parentNode.innerText)?els[i].parentNode.innerText:'';
                let match=parentTxt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
                if(match){
                    st.curBal=parseFloat(match[1].replace(/,/g,''));
                    return st.curBal;
                }
            }
        }
        for(let i=0;i<els.length;i++){
            let txt=els[i].innerText||'';
            if(txt.trim().match(/^[৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)){
                st.curBal=parseFloat(txt.replace(/[^\\d.]/g,''));
                return st.curBal;
            }
        }
        return st.curBal;
    }

    function generateSmartSequence(balance,steps){
        steps=Math.max(1,parseInt(steps)||1);
        let b=Math.max(1,Math.floor(balance)||1);
        let units=Math.pow(2,steps)-1;
        if(units>0&&units<=b){
            let base=Math.floor(b/units);
            let seq=[],val=Math.max(1,base);
            for(let i=0;i<steps;i++){
                seq.push(val);
                val*=2;
            }
            return seq;
        }
        let seq=[],val=1,sum=0;
        for(let i=0;i<steps;i++){
            if(sum+val<=b){
                seq.push(val);
                sum+=val;
                val*=2;
            }else{
                let rem=b-sum;
                if(rem>0)seq.push(rem);
                break;
            }
        }
        return seq.length>0?seq:[1];
    }

    let p=document.createElement('div');
    p.id='sys-core-fin';
    p.style.cssText='position:fixed;width:170px;padding:4px;font-family:monospace;font-size:10px;z-index:9999999;color:#fff;user-select:none;border-radius:14px;overflow:visible;background:transparent;';
    let sL=localStorage.getItem('drx_ui_x'),sT=localStorage.getItem('drx_ui_y');
    if(sL&&sT){p.style.left=sL;p.style.top=sT;}else{p.style.top='20px';p.style.right='20px';}

    let stl=document.createElement('style');
    stl.innerHTML='@keyframes titlePulseAnim{0%{transform:scale(1);text-shadow:0 0 10px #00ff00;}50%{transform:scale(1.05);text-shadow:0 0 20px #00ff00,0 0 30px #fff;}100%{transform:scale(1);text-shadow:0 0 10px #00ff00;}}.drx-in{background:rgba(10,12,18,0.92);backdrop-filter:blur(6px);position:relative;overflow:visible;z-index:1;display:flex;flex-direction:column;height:100%;border-radius:12px;border:2px solid #00ff00;box-sizing:border-box;}input::-webkit-outer-spin-button,input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0;}.txt-blk{color:#fff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-accent{color:#00ff00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-warn{color:#ffcc00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-err{color:#f00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-cyan{color:#0ff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-mag{color:#f0f;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.drx-elec-target{border-radius:8px!important;position:relative;z-index:9999!important;transition:all 0.1s;background:rgba(0,0,0,0.5)!important;border:2px solid #00ff00!important;}.drx-title-anim{display:inline-block;animation:titlePulseAnim 2s infinite ease-in-out;}';
    document.body.appendChild(stl);
    p.className='drx-wrap';

    let inC=document.createElement('div');
    inC.className='drx-in';
    let h=document.createElement('div');
    h.style.cssText='padding:8px;font-size:12px;display:flex;justify-content:space-between;cursor:move;border-bottom:2px solid #000;background:transparent;';
    h.innerHTML='<span class="txt-blk drx-title-anim" id="drx-title">' + uF('WINZY-MARTINGALE') + '</span><span style="cursor:pointer;" class="txt-blk-err" id="sys-cls">X</span>';
    inC.appendChild(h);

    let drg=false,sx,sy,sl,st_y;
    function dSt(e){
        if(e.target.tagName==='SPAN'&&e.target.id==='sys-cls')return;
        drg=true;
        let ev=e.type.includes('touch')?e.touches[0]:e;
        sx=ev.clientX;sy=ev.clientY;
        sl=p.offsetLeft;st_y=p.offsetTop;
    }
    function dMv(e){
        if(!drg)return;
        e.preventDefault();
        let ev=e.type.includes('touch')?e.touches[0]:e;
        p.style.left=(sl+ev.clientX-sx)+'px';
        p.style.top=(st_y+ev.clientY-sy)+'px';
    }
    function dEn(){
        drg=false;
        localStorage.setItem('drx_ui_x',p.style.left);
        localStorage.setItem('drx_ui_y',p.style.top);
    }
    h.addEventListener('mousedown',dSt);
    document.addEventListener('mousemove',dMv);
    document.addEventListener('mouseup',dEn);

    h.querySelector('#sys-cls').onclick=()=>{
        clearInterval(st.autoInt);
        clearInterval(st.preScn);
        if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);
        p.remove();
        lkOvl.remove();
        document.body.style.overflow='';
    };

    let b=document.createElement('div');
    b.style.cssText='padding:10px;display:flex;flex-direction:column;gap:8px;background:transparent;';

    const p1=document.createElement('div');
    p1.innerHTML='<div style="text-align:center;margin-bottom:8px;padding:6px;background:transparent;border-radius:6px;border:2px solid #000;"><span class="txt-blk" style="font-size:9px;color:#ccc;">' + uF('CURRENT BAL') + '</span><br><span id="pre-bal" class="txt-blk" style="font-size:15px;color:#fff;">--</span></div>';

    const tgtInp=document.createElement('input');
    tgtInp.type='number';
    tgtInp.value=autoTargetProfit || '';
    tgtInp.placeholder='TARGET PROFIT (৳)';
    tgtInp.className='txt-blk';
    tgtInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#fff;';

    const stepInp=document.createElement('input');
    stepInp.type='number';
    stepInp.value=autoTotalSteps || 7;
    stepInp.placeholder='TOTAL STEPS (e.g. 7)';
    stepInp.className='txt-blk-cyan';
    stepInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#0ff;';

    const goBtn=document.createElement('button');
    goBtn.innerText=uF('START');
    goBtn.className='txt-blk-accent';
    goBtn.style.cssText='width:100%;box-sizing:border-box;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;transition:0.2s;';

    p1.appendChild(tgtInp);
    p1.appendChild(stepInp);
    p1.appendChild(goBtn);

    st.preScn=setInterval(()=>{
        if(!st.isRun){
            let bal=chkBal();
            let el=document.getElementById('pre-bal');
            if(el)el.innerText=uF(bal>0?bal.toFixed(2):'--');
        }
    },1000);

    const p2=document.createElement('div');
    p2.style.display='none';

    const balBx=document.createElement('div');
    balBx.style.cssText='padding:6px;text-align:center;background:transparent;border-radius:6px;border:2px solid #000;margin-bottom:6px;';
    balBx.innerHTML='<div class="txt-blk" style="font-size:9px;color:#ccc;">' + uF('LIVE BAL / PROFIT') + '</div><div id="ui-bal" class="txt-blk" style="font-size:16px;color:#fff;">--</div>';

    let aiRow='<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">' + uF('AI:') + '</span><span id="ui-ai" class="txt-blk-cyan">VIP JSON API</span></div>';
    const infBx=document.createElement('div');
    infBx.style.cssText='padding:6px;font-size:10px;line-height:2;background:transparent;border-radius:6px;border:2px solid #000;position:relative;overflow:hidden;';
    infBx.innerHTML=aiRow+'<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">' + uF('TGT:') + '</span><span id="ui-tgt" class="txt-blk" style="color:#fff;">0</span></div>' + '<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">' + uF('STP:') + '</span><span id="ui-bet" class="txt-blk-warn" style="color:#ffcc00;cursor:pointer;">5</span></div>' + '<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">' + uF('CLK:') + '</span><span id="ui-clk" class="txt-blk" style="color:#fff;">00:30</span></div>' + '<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">' + uF('STS:') + '</span><span id="ui-sts" class="txt-blk" style="color:#fff;">' + uF('WAIT') + '</span></div>';

    const ghBox=document.createElement('div');
    ghBox.id='gh-box-wrap';
    ghBox.style.cssText='width:100%;height:26px;background:transparent;border:2px solid #000;border-radius:4px;padding:2px 4px;margin-top:4px;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column;justify-content:center;';
    ghBox.innerHTML='<div id="gh-content" class="txt-blk" style="font-size:7.5px;line-height:1.2;color:#fff;white-space:pre-wrap;text-align:left;width:100%;">Syncing API...</div>';
    infBx.appendChild(ghBox);

    const stpBtn=document.createElement('button');
    stpBtn.innerText=uF('STOP');
    stpBtn.className='txt-blk-err';
    stpBtn.style.cssText='width:100%;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;margin-top:6px;transition:0.2s;';

    p2.appendChild(balBx);
    p2.appendChild(infBx);
    p2.appendChild(stpBtn);

    b.appendChild(p1);
    b.appendChild(p2);
    inC.appendChild(b);
    p.appendChild(inC);
    document.body.appendChild(p);

    const drx_triggerEvent=(el,etype)=>{
        let ev=new Event(etype,{bubbles:true,cancelable:true});
        el.dispatchEvent(ev);
    };

    const drx_simClick=el=>{
        if(!el)return;
        ['pointerdown','mousedown','touchstart','pointerup','mouseup','touchend','click'].forEach(evt=>{
            try{
                el.dispatchEvent(new MouseEvent(evt,{bubbles:true,cancelable:true,view:window}));
            }catch(e){}
        });
    };

    const exeTrd=(pred,amt,cb)=>{
        try{
            let btn=null,targetText=pred.toLowerCase(),btns=document.querySelectorAll('button, div, span');
            for(let i=0;i<btns.length;i++){
                let t=(btns[i].innerText||'').trim().toLowerCase();
                if(t===targetText&&btns[i].offsetParent&&!btns[i].children.length){
                    btn=btns[i];
                    break;
                }
            }
            if(!btn){
                if(targetText==='big')btn=document.querySelector('.Betting__C-foot-b');
                else if(targetText==='small')btn=document.querySelector('.Betting__C-foot-s');
                else if(targetText==='green')btn=document.querySelector('button[class*="green"], div[class*="green"]');
                else if(targetText==='red')btn=document.querySelector('button[class*="red"], div[class*="red"]');
                else if(targetText==='violet')btn=document.querySelector('button[class*="violet"], div[class*="violet"]');
            }
            if(!btn){
                if(cb)cb(false);
                return;
            }
            btn.classList.add('drx-elec-target');
            drx_simClick(btn);

            let checkAttempts=0,valInterval=setInterval(()=>{
                checkAttempts++;
                let inpEl=document.querySelector("input[type='number'], input.van-field__control");
                if(inpEl||checkAttempts>15){
                    clearInterval(valInterval);
                    if(inpEl){
                        inpEl.focus();
                        let setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;
                        if(setV)setV.call(inpEl,String(amt));
                        else inpEl.value=amt;
                        drx_triggerEvent(inpEl,'input');
                        drx_triggerEvent(inpEl,'change');
                        drx_triggerEvent(inpEl,'blur');
                    }
                    setTimeout(()=>{
                        let dEl=document.querySelector('button.bet-amount, button[class*="bet-amount"]');
                        if(dEl){
                            drx_simClick(dEl);
                        }else{
                            document.querySelectorAll('button').forEach(b=>{
                                if((b.innerText||'').includes('Total amount')&&b.offsetParent)drx_simClick(b);
                            });
                        }
                        btn.classList.remove('drx-elec-target');
                        setTimeout(()=>{if(cb)cb(true);},2000);
                    },800);
                }
            },200);
        }catch(e){
            if(cb)cb(false);
        }
    };

    const scnUI=cb=>{
        let ov=document.createElement('div');
        ov.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;background:transparent;z-index:9999998;pointer-events:none;overflow:hidden;';
        let cBase='#00ff00',rL=document.createElement('div');
        rL.style.cssText='position:absolute;width:100%;height:2px;background:' + cBase + ';box-shadow:0 0 10px 3px ' + cBase + ';animation:sR 0.6s linear infinite alternate;';
        let gL=document.createElement('div');
        gL.style.cssText='position:absolute;height:100%;width:3px;background:' + cBase + ';box-shadow:0 0 15px 5px ' + cBase + ';animation:sG 0.6s cubic-bezier(0.25,0.1,0.25,1) infinite alternate;';
        let sS=document.createElement('style');
        sS.innerHTML='@keyframes sR{0%{top:-10px;}100%{top:100vh;}}@keyframes sG{0%{left:-10px;}100%{left:100vw;}}';
        document.head.appendChild(sS);
        ov.appendChild(rL);
        ov.appendChild(gL);
        document.body.appendChild(ov);
        setTimeout(()=>{
            ov.remove();
            sS.remove();
            if(cb)cb();
        },1500);
    };

    const getNextLivePeriod=str=>{
        let chars=str.split('');
        for(let i=chars.length-1;i>=0;i--){
            if(chars[i]!=='9'){
                chars[i]=String.fromCharCode(chars[i].charCodeAt(0)+1);
                return chars.join('');
            }
            chars[i]='0';
        }
        return '1'+chars.join('');
    };

    const apiLoopTask=async()=>{
        if(!st.isRun||st.isTrd||isFetchingApi)return;
        isFetchingApi=true;
        try{
            chkBal();
            const uBal=document.getElementById('ui-bal'),uSts=document.getElementById('ui-sts'),uBet=document.getElementById('ui-bet');
            if(st.curBal>=st.tgtAmt&&st.curBal>0){
                uBal.innerText=uF(st.curBal.toFixed(2) + ' (DONE)');
                uSts.innerText=uF('DONE');
                uSts.className='txt-blk-accent';
                stpBtn.style.display='none';
                VoiceEngine.speak("Target reached successfully.");
                st.isRun=false;
                clearInterval(st.autoInt);
                lkOvl.style.display='none';
                document.body.style.overflow='';
                return;
            }else{
                uBal.innerText=uF(st.curBal>0?st.curBal.toFixed(2):'--');
            }

            let ts=Math.floor(Date.now()/1000),res=await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts="+ts),dataArray=await res.json();
            if(dataArray&&dataArray.length>0){
                if(curApiIdx>=dataArray.length)curApiIdx=0;
                let activeLogic=dataArray[curApiIdx],tempHist=activeLogic.history,cSig=getNextLivePeriod(String(tempHist[0].pid)),sSig=sessionStorage.getItem('drx_sig');
                if(cSig!==sSig){
                    if(st.lastPred&&st.lastPeriod){
                        let actualData=tempHist[0],actualR=actualData.actual==='BIG'?'BIG':'SMALL';
                        if(st.lastPred===actualR){
                            st.w++;
                            st.stpIdx=0;
                            st.cur_w_streak++;
                            st.cur_l_streak=0;
                            if(st.cur_w_streak>st.max_w_streak) st.max_w_streak=st.cur_w_streak;
                        }else{
                            st.l++;
                            st.stpIdx=Math.min(st.stpIdx+1,st.dynSeq.length-1);
                            curApiIdx=(curApiIdx===0&&dataArray.length>1)?1:0;
                            st.cur_l_streak++;
                            st.cur_w_streak=0;
                            if(st.cur_l_streak>st.max_l_streak) st.max_l_streak=st.cur_l_streak;
                        }
                    }
                    st.lastPeriod=cSig;
                    let timeLeft=dTimeLeft;
                    if(timeLeft<=cfg.minSf){
                        uSts.innerText=uF('<10S');
                        uSts.className='txt-blk-warn';
                    }
                    st.isTrd=true;
                    uSts.innerText=uF('CHK...');
                    uSts.className='txt-blk-warn';
                    let nBal=chkBal();
                    uBal.innerText=uF(nBal.toFixed(2));
                    if(nBal>=st.tgtAmt&&nBal>0){
                        st.isTrd=false;
                        isFetchingApi=false;
                        return;
                    }
                    if(st.stpIdx>=st.dynSeq.length)st.stpIdx=st.dynSeq.length-1;
                    let tAmt=st.manualOverrideBet?st.manualOverrideBet:st.dynSeq[st.stpIdx];
                    uBet.innerText=uF(st.manualOverrideBet?tAmt+' (FIX)':(tAmt + ' (S' + (st.stpIdx+1) + ')'));
                    if(nBal<tAmt){
                        uSts.innerText=uF('LOW');
                        uSts.className='txt-blk-err';
                        st.stpIdx=0;
                        st.isTrd=false;
                        isFetchingApi=false;
                        return;
                    }
                    uSts.innerText=uF('DB...');
                    uSts.className='txt-blk-cyan';
                    setTimeout(()=>{
                        let activeLogicNew=dataArray[curApiIdx],prediction=(activeLogicNew.pred||'BIG').toUpperCase();
                        st.lastPred=prediction;
                        let ghC=document.getElementById('gh-content');
                        if(ghC)ghC.textContent='Step: ' + (st.stpIdx+1) + '/' + st.dynSeq.length + ' (Amt: ' + tAmt + ')\\nPred: ' + prediction + ' | W:' + st.w + ' L:' + st.l;
                        if(prediction==='SKIP'){
                            uSts.innerText=uF('SKIP');
                            uSts.className='txt-blk-warn';
                            sessionStorage.setItem('drx_sig',cSig);
                            setTimeout(()=>{st.isTrd=false;},1000);
                        }else{
                            uSts.innerText=uF('EXC...');
                            uSts.className='txt-blk';
                            exeTrd(prediction,tAmt,(suc)=>{
                                if(suc){
                                    uSts.innerText=uF('OK');
                                    uSts.className='txt-blk-accent';
                                    sessionStorage.setItem('drx_sig',cSig);
                                    sessionStorage.setItem('drx_p_bal',st.curBal);
                                    st.tradesDone++;
                                }else{
                                    uSts.innerText=uF('ERR');
                                    uSts.className='txt-blk-err';
                                }
                                setTimeout(()=>{st.isTrd=false;},1000);
                            });
                        }
                    },1800);
                }else if(!st.isTrd){
                    uSts.innerText=uF('SCAN');
                    uSts.className='txt-blk';
                }
            }
        }catch(e){
            st.isTrd=false;
        }
        isFetchingApi=false;
    };

    goBtn.onclick=()=>{
        let inputTarget=parseFloat(tgtInp.value);
        if(!inputTarget||inputTarget<=0){
            alert('Please enter Target Profit Amount!');
            tgtInp.focus();
            return;
        }
        let inputSteps=parseInt(stepInp.value)||1;
        if(inputSteps<=0)inputSteps=1;
        st.totalSteps=inputSteps;
        clearInterval(st.preScn);
        st.tradesDone=0;
        st.w=0;
        st.l=0;
        curApiIdx=0;
        let liveB=chkBal();
        st.startBal=liveB;
        st.tgtAmt=(inputTarget<=liveB)?(liveB+inputTarget):inputTarget;
        st.dynSeq=generateSmartSequence(liveB,st.totalSteps);
        st.stpIdx=0;
        VoiceEngine.speak("Engine started with smart step calculation.");
        scnUI(()=>{
            sessionStorage.removeItem('drx_sig');
            sessionStorage.removeItem('drx_p_bal');
            document.getElementById('ui-tgt').innerText=uF(st.tgtAmt.toFixed(0));
            p1.style.display='none';
            p2.style.display='block';
            lkOvl.style.display='block';
            document.body.style.overflow='hidden';
            st.isRun=true;
            st.isTrd=false;
            document.getElementById('ui-sts').innerText=uF('RDY');
            st.autoInt=setInterval(apiLoopTask,1000);
        });
    };

    stpBtn.onclick=()=>{
        st.isRun=false;
        clearInterval(st.autoInt);
        sessionStorage.removeItem('drx_sig');
        sessionStorage.removeItem('drx_p_bal');
        document.getElementById('ui-sts').innerText=uF('HLT');
        document.getElementById('ui-sts').className='txt-blk-err';
        lkOvl.style.display='none';
        document.body.style.overflow='';
        p2.style.display='none';
        p1.style.display='block';
    };

    if (autoTargetProfit && autoTotalSteps) {
        setTimeout(() => {
            goBtn.click();
        }, 1200);
    }

    return "INJECTED_SUCCESSFULLY";
})();
"""

# ==============================================================================
# 9. Clean Multilingual Localization Engine
# ==============================================================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
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
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"ট্রেডিং ব্যাকগ্রাউন্ডে স্বয়ংক্রিয়ভাবে চলছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"বর্তমান সেশনটি বন্ধ করা হয়েছে। নতুন সেশনের জন্য /start পাঠান।"
            )
        },
        "en": {
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login completed. Press <b>START</b> below to configure trading:"
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
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Active browser session closed cleanly. Send /start to begin a new session."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==============================================================================
# 10. Interactive Control Keyboards
# ==============================================================================
def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_sessions.get(sid, {})
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
    sess = active_sessions.get(sid, {})
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
# 11. Selenium Automation: Site Login & WinGo Navigation
# ==============================================================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE ENGINE</b>\n<code>Allocating isolated profile...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>Securing connection instance...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>Auto-filling credentials...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>Login verification complete!</code>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.4)

def process_login(chat_id, sid, phone, password, anim_msg_id):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN

    if anim_msg_id:
        play_clean_login_animation(chat_id, anim_msg_id)

    try:
        driver, handle = allocate_session_tab(sid, login_url)
    except Exception as e:
        if anim_msg_id:
            safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error=str(e)))
        return

    fill_ok = False
    for _ in range(70):
        def _fill(drv):
            return drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
        res = safe_tab_execute(sid, _fill)
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(2.0)
            break
        time.sleep(0.4)

    if not fill_ok:
        if anim_msg_id:
            safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error="লগইন ফর্ম পাওয়া যায়নি"))
        close_session_tab(sid)
        return

    login_status = "PENDING"
    err_detail = ""
    for _ in range(40):
        def _chk(drv):
            return drv.execute_script(CHECK_LOGIN_STATUS_JS)
        res = safe_tab_execute(sid, _chk)
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "CONFIRM_CLICKED":
                time.sleep(1.5)
                continue
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "ভুল ফোন বা পাসওয়ার্ড")
                break
        time.sleep(0.5)

    def _token_chk(drv):
        return drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")
    if safe_tab_execute(sid, _token_chk):
        login_status = "SUCCESS"

    if anim_msg_id:
        safe_delete_message(chat_id, anim_msg_id)

    if login_status == "ERROR":
        close_session_tab(sid)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error=err_detail))
        return

    time.sleep(1.5)

    login_snap = os.path.join(PROFILES_BASE_DIR, f"login_done_{sid}.png")
    def _shot(drv):
        drv.save_screenshot(login_snap)
    safe_tab_execute(sid, _shot)

    masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone

    display_or_replace_photo(
        chat_id, sid,
        login_snap,
        get_text(chat_id, "login_success", site_name=site_name, phone=masked_phone),
        get_start_screen_keyboard(sid)
    )

    try:
        if os.path.exists(login_snap):
            os.remove(login_snap)
    except Exception:
        pass

def prepare_wingo_parameters(chat_id, sid):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")

    def _nav(drv):
        try:
            drv.execute_script(WINGO_RUNBOX_AND_CLICK_JS)
        except Exception:
            pass
        wingo_url = URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO
        try:
            drv.execute_script("""
                const target = arguments[0];
                if (!window.location.href.includes('WinGo')) {
                    window.location.href = target;
                }
            """, wingo_url)
        except Exception:
            pass

    safe_tab_execute(sid, _nav)
    time.sleep(1.5)

    for _ in range(30):
        def _rdy(drv):
            return drv.execute_script(CHECK_WINGO_READY_JS)
        if safe_tab_execute(sid, _rdy):
            break
        time.sleep(0.8)

    current_bal = 0.0
    for _ in range(12):
        def _bal(drv):
            return drv.execute_script(FETCH_BALANCE_JS)
        bal = safe_tab_execute(sid, _bal)
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.5)

    sess["current_balance"] = current_bal

    wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
    def _shot(drv):
        drv.save_screenshot(wingo_snap)
    safe_tab_execute(sid, _shot)

    config_caption = (
        f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Live Balance: <code>৳ {current_bal:.2f}</code>\n\n"
        f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
    )

    display_or_replace_photo(
        chat_id, sid,
        wingo_snap,
        config_caption,
        get_setup_param_keyboard(sid)
    )

    try:
        if os.path.exists(wingo_snap):
            os.remove(wingo_snap)
    except Exception:
        pass

def monitor_trading_progress(chat_id, sid):
    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        def _get_st(drv):
            return drv.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        isRun: window.__WINGO_ST.isRun,
                        curBal: window.__WINGO_ST.curBal || 0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                        startBal: window.__WINGO_ST.startBal || 0,
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                        cur_l_streak: window.__WINGO_ST.cur_l_streak || 0,
                        max_w_streak: window.__WINGO_ST.max_w_streak || 0,
                        max_l_streak: window.__WINGO_ST.max_l_streak || 0
                    };
                }
                return null;
            """)

        js_data = safe_tab_execute(sid, _get_st)

        if js_data:
            sess["cur_bal"] = js_data.get("curBal", sess.get("cur_bal", 0))
            sess["wins"] = js_data.get("w", 0)
            sess["losses"] = js_data.get("l", 0)
            sess["max_w"] = js_data.get("max_w_streak", 0)
            sess["max_l"] = js_data.get("max_l_streak", 0)
            tgt_amt = js_data.get("tgtAmt", 0)

            if sess["cur_bal"] >= tgt_amt and tgt_amt > 0 and sess["cur_bal"] > 0:
                sess["is_trading"] = False
                start_b = sess.get("start_bal", 0)
                profit = sess["cur_bal"] - start_b

                screen_path = os.path.join(PROFILES_BASE_DIR, f"win_{sid}.png")
                def _shot(drv):
                    drv.save_screenshot(screen_path)
                safe_tab_execute(sid, _shot)

                msg = (
                    f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                    f"কাঙ্ক্ষিত টার্গেট পূরণ হয়েছে।\n\n"
                    f"শুরুর ব্যালেন্স: <code>৳ {start_b:.2f}</code>\n"
                    f"বর্তমান ব্যালেন্স: <code>৳ {sess['cur_bal']:.2f}</code>\n"
                    f"অর্জিত প্রফিট: <code>+৳ {profit:.2f}</code>\n"
                    f"মোট উইন: <b>{sess['wins']}</b> | লস: <b>{sess['losses']}</b>"
                )

                if os.path.exists(screen_path):
                    display_or_replace_photo(chat_id, sid, screen_path, msg, None)
                    try:
                        os.remove(screen_path)
                    except Exception:
                        pass
                else:
                    bot.send_message(chat_id, msg)
                break

        time.sleep(4)

# ==============================================================================
# 12. Super Admin Panel Handlers (/pass, /admin, /terminals, /kick)
# ==============================================================================
def is_owner(user):
    return user.username == OWNER_USERNAME

@bot.message_handler(commands=['pass'])
def handle_pass_command(message):
    if not is_owner(message.from_user):
        return
    safe_delete_message(message.chat.id, message.message_id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('CREATE PASS')}", callback_data="admin_create_pass"),
        InlineKeyboardButton(f"{to_bold('DELETE PASS')}", callback_data="admin_list_pass")
    )
    bot.send_message(message.chat.id, f"<b>{to_bold('PASSKEY CONTROLLER')}</b>\nপাসওয়ার্ড নির্বাচন করুন:", reply_markup=markup)

@bot.message_handler(commands=['admin', 'terminals'])
def handle_admin_terminals(message):
    if not is_owner(message.from_user):
        return
    safe_delete_message(message.chat.id, message.message_id)
    render_terminal_monitor(message.chat.id)

def render_terminal_monitor(chat_id, message_id=None):
    terminals = firebase.get("/terminals") or {}
    total = len(terminals)
    busy = sum(1 for t in terminals.values() if isinstance(t, dict) and t.get("status") == "BUSY")
    free = sum(1 for t in terminals.values() if isinstance(t, dict) and t.get("status") == "FREE")

    lines = [
        f"<b>{to_bold('CLUSTER TERMINAL MONITOR')}</b>",
        f"মোট টার্মিনাল: <b>{total}</b>",
        f"ব্যস্ত নোড: <b>{busy}</b>",
        f"ফ্রি নোড: <b>{free}</b>\n"
    ]

    markup = InlineKeyboardMarkup(row_width=1)
    for t_id, data in terminals.items():
        if not isinstance(data, dict):
            continue
        st = data.get("status", "FREE")
        u_id = data.get("assigned_user_id", "None")
        site = data.get("site", "None")
        lines.append(f"• <b>{t_id}</b>: {st} (User: {u_id} | Site: {site})")
        markup.add(InlineKeyboardButton(f"✕ Kill {t_id}", callback_data=f"kill_node:{t_id}"))

    markup.add(InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data="refresh_terminals"))
    text_content = "\n".join(lines)

    if message_id:
        try:
            bot.edit_message_text(text_content, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            pass
    else:
        bot.send_message(chat_id, text_content, reply_markup=markup)

@bot.message_handler(commands=['kick'])
def handle_kick_command(message):
    if not is_owner(message.from_user):
        return
    safe_delete_message(message.chat.id, message.message_id)
    parts = message.text.strip().split()
    if len(parts) > 1:
        target_node = parts[1]
        firebase.patch(f"/terminals/{target_node}", {"command": "FORCE_KILL"})
        bot.send_message(message.chat.id, f"নোড <b>{target_node}</b>-কে FORCE_KILL পাঠানো হয়েছে।")

# ==============================================================================
# 13. Step-by-Step UI Transitions & Callbacks
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    # Super Admin bypass
    if is_owner(message.from_user):
        send_step4_platform_select(chat_id)
        return

    # STEP 1: Channel Membership Gateway
    is_member = False
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
        if member.status in ["creator", "administrator", "member", "restricted"]:
            is_member = True
    except Exception:
        is_member = False

    if is_member:
        send_step2_language_select(chat_id)
    else:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{to_bold('CHANNEL')}", url=CHANNEL_URL),
            InlineKeyboardButton(f"{to_bold('✓ VERIFY')}", callback_data="gate_verify")
        )
        msg = (
            f"<b>{to_bold('CHANNEL JOIN')}</b>\n"
            "দয়া করে চ্যানেলটি জয়েন করুন।"
        )
        bot.send_message(chat_id, msg, reply_markup=markup)

def send_step2_language_select(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="set_lang_en"),
        InlineKeyboardButton(f"{to_bold('বাংলা')}", callback_data="set_lang_bn")
    )
    bot.send_message(chat_id, "দয়া করে আপনার ভাষাটি সেট করুন:", reply_markup=markup)

def send_step3_bot_pass_gate(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('PASS')}", callback_data="ask_bot_pass"),
        InlineKeyboardButton(f"{to_bold('OWNER')}", url=OWNER_URL)
    )
    msg = bot.send_message(chat_id, "দয়া করে পাসওয়ার্ডটি দিন:", reply_markup=markup)
    user_sessions.setdefault(chat_id, {})["pass_prompt_msg_id"] = msg.message_id

def send_step4_platform_select(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="select_site_amarclub"),
        InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="select_site_dkwin")
    )
    bot.send_message(chat_id, "দয়া করে সাইট নির্বাচন করুন:", reply_markup=markup)

def send_step5_site_phone_prompt(chat_id):
    u = user_sessions.setdefault(chat_id, {})
    u["input_mode"] = "WAITING_SITE_PHONE"
    msg = bot.send_message(chat_id, "দয়া করে আপনার অ্যাকাউন্টের ফোন নম্বরটি দিন:")
    u["temp_prompt_id"] = msg.message_id

def send_step5_site_password_prompt(chat_id):
    u = user_sessions.setdefault(chat_id, {})
    u["input_mode"] = "WAITING_SITE_PASS"
    msg = bot.send_message(chat_id, "দয়া করে আপনার অ্যাকাউন্টের পাসওয়ার্ডটি দিন:")
    u["temp_prompt_id"] = msg.message_id

# ==============================================================================
# 14. Telegram Callback Query Router
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    param = parts[1] if len(parts) > 1 else None

    # Step 1: Verify Channel Gate
    if action == "gate_verify":
        try:
            member = bot.get_chat_member(CHANNEL_USERNAME, chat_id)
            if member.status in ["creator", "administrator", "member", "restricted"]:
                bot.answer_callback_query(call.id, "ধন্যবাদ!")
                safe_delete_message(chat_id, call.message.message_id)
                send_step2_language_select(chat_id)
            else:
                bot.answer_callback_query(call.id, "দয়া করে আগে চ্যানেলে জয়েন করুন।", show_alert=True)
        except Exception:
            bot.answer_callback_query(call.id, "দয়া করে আগে চ্যানেলে জয়েন করুন।", show_alert=True)

    # Step 2: Language Select
    elif action in ["set_lang_en", "set_lang_bn"]:
        u = user_sessions.setdefault(chat_id, {})
        u["lang"] = "en" if action == "set_lang_en" else "bn"
        bot.answer_callback_query(call.id)
        safe_delete_message(chat_id, call.message.message_id)
        send_step3_bot_pass_gate(chat_id)

    # Step 3: Trigger Wait Bot Password
    elif action == "ask_bot_pass":
        u = user_sessions.setdefault(chat_id, {})
        u["input_mode"] = "WAIT_BOT_PASS"
        bot.answer_callback_query(call.id, "পাসওয়ার্ড লিখুন")

    # Step 4: Platform Selection
    elif action in ["select_site_amarclub", "select_site_dkwin"]:
        site_name = "Amar Club" if action == "select_site_amarclub" else "DK Win"
        u = user_sessions.setdefault(chat_id, {})
        u["site_name"] = site_name
        bot.answer_callback_query(call.id)
        safe_delete_message(chat_id, call.message.message_id)
        send_step5_site_phone_prompt(chat_id)

    # Admin: Pass Actions
    elif action == "admin_create_pass":
        bot.answer_callback_query(call.id)
        new_key = generate_random_key(10)
        exp = time.time() + 86400
        firebase.put(f"/active_passwords/{new_key}", {
            "created_at": time.time(),
            "expires_at": exp,
            "status": "ACTIVE"
        })
        bot.send_message(chat_id, f"<b>নতুন পাসওয়ার্ড তৈরি হয়েছে:</b>\n<code>{new_key}</code>\n(মেয়াদ: ২৪ ঘণ্টা)")

    elif action == "admin_list_pass":
        bot.answer_callback_query(call.id)
        passes = firebase.get("/active_passwords") or {}
        if not passes:
            bot.send_message(chat_id, "কোনো সক্রিয় পাসওয়ার্ড পাওয়া যায়নি।")
            return
        markup = InlineKeyboardMarkup(row_width=1)
        for k in passes.keys():
            markup.add(InlineKeyboardButton(f"✕ Revoke {k}", callback_data=f"del_key:{k}"))
        bot.send_message(chat_id, "<b>সক্রিয় পাসওয়ার্ড তালিকা:</b>", reply_markup=markup)

    elif action == "del_key" and param:
        bot.answer_callback_query(call.id, "পাসওয়ার্ড মুছে ফেলা হয়েছে")
        firebase.delete(f"/active_passwords/{param}")
        safe_delete_message(chat_id, call.message.message_id)

    elif action == "kill_node" and param:
        bot.answer_callback_query(call.id, f"নোড {param} রিস্টার্ট হচ্ছে...")
        firebase.patch(f"/terminals/{param}", {"command": "FORCE_KILL"})
        time.sleep(1)
        render_terminal_monitor(chat_id, call.message.message_id)

    elif action == "refresh_terminals":
        bot.answer_callback_query(call.id)
        render_terminal_monitor(chat_id, call.message.message_id)

    # WinGo Market Configuration
    elif action == "start_cfg" and param in active_sessions:
        bot.answer_callback_query(call.id, "উইনগো ৩০এস পেজ প্রস্তুত করা হচ্ছে...")
        threading.Thread(target=prepare_wingo_parameters, args=(chat_id, param), daemon=True).start()

    elif action == "set_tgt" and param in active_sessions:
        active_sessions[param]["input_mode"] = "WAITING_TARGET"
        user_sessions[chat_id]["active_sid"] = param
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[param].get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{cur_bal:.2f}"))
        active_sessions[param]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and param in active_sessions:
        active_sessions[param]["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = param
        bot.answer_callback_query(call.id)
        tgt = active_sessions[param].get("target_profit", 0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        active_sessions[param]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and param in active_sessions:
        sess = active_sessions[param]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় করা হচ্ছে...")
        sess["is_trading"] = True

        def _run_core(drv):
            drv.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
        safe_tab_execute(param, _run_core)

        time.sleep(2.0)

        start_snap = os.path.join(PROFILES_BASE_DIR, f"run_{param}.png")
        def _shot(drv):
            drv.save_screenshot(start_snap)
        safe_tab_execute(param, _shot)

        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        dashboard_caption = get_text(
            chat_id, "running_dashboard",
            site_name=sess.get("site_name", "Amar Club"),
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=sess["total_steps"]
        )

        display_or_replace_photo(
            chat_id, param,
            start_snap,
            dashboard_caption,
            get_trading_control_keyboard(param)
        )

        try:
            if os.path.exists(start_snap):
                os.remove(start_snap)
        except Exception:
            pass

        threading.Thread(target=monitor_trading_progress, args=(chat_id, param), daemon=True).start()

    elif action == "shot" and param in active_sessions:
        sess = active_sessions[param]
        bot.answer_callback_query(call.id, "ফুটেজ আপডেট হচ্ছে...")
        temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{param}.png")

        def _shot(drv):
            drv.save_screenshot(temp_shot)
        safe_tab_execute(param, _shot)

        if os.path.exists(temp_shot):
            cur_b = sess.get("cur_bal", sess.get("current_balance", 0.0))
            t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
            caption = (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {sess.get('start_bal', 0.0):.2f}</code>\n"
                f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
                f"Total Steps: <b>{sess.get('total_steps', 7)}</b>\n\n"
                f"সময়: <code>{time.strftime('%H:%M:%S')}</code>"
            )
            display_or_replace_photo(chat_id, param, temp_shot, caption, get_trading_control_keyboard(param))
            try:
                os.remove(temp_shot)
            except Exception:
                pass

    elif action == "bal" and param in active_sessions:
        def _bal(drv):
            return drv.execute_script(FETCH_BALANCE_JS)
        b = safe_tab_execute(param, _bal)
        if b is not None:
            bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "ব্যালেন্স লোড হচ্ছে...", show_alert=True)

    elif action == "stats" and param in active_sessions:
        def _stat(drv):
            return drv.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        step: (window.__WINGO_ST.stpIdx || 0) + 1,
                        maxStep: (window.__WINGO_ST.dynSeq || []).length,
                        curBal: window.__WINGO_ST.curBal || 0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0
                    };
                }
                return null;
            """)
        data_rep = safe_tab_execute(param, _stat)
        if data_rep:
            stat_txt = (
                f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                f"ব্যালেন্স: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                f"টার্গেট: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                f"মার্টিনগেল লেভেল: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                f"উইন: <b>{data_rep['w']}</b> | লস: <b>{data_rep['l']}</b>"
            )
            bot.send_message(chat_id, stat_txt)
        else:
            bot.answer_callback_query(call.id, "ইঞ্জিন লোড হচ্ছে...", show_alert=True)

    elif action == "stop" and param in active_sessions:
        sess = active_sessions[param]
        def _stop(drv):
            drv.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
        safe_tab_execute(param, _stop)
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং সাময়িকভাবে থামানো হয়েছে।")

    elif action == "cancel" and param in active_sessions:
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        close_session_tab(param)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# ==============================================================================
# 15. User Input Handler (Disambiguated Bot Passkey vs Site Login)
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    safe_delete_message(chat_id, message.message_id)

    u = user_sessions.setdefault(chat_id, {})
    input_mode = u.get("input_mode")

    # AUTH SYSTEM A: BOT ACCESS PASSKEY
    if input_mode == "WAIT_BOT_PASS":
        u["input_mode"] = None
        prompt_id = u.pop("pass_prompt_msg_id", None)
        safe_delete_message(chat_id, prompt_id)

        # Validate against Firebase
        key_record = firebase.get(f"/active_passwords/{text}")
        now = time.time()
        is_valid = False

        if key_record and isinstance(key_record, dict):
            if key_record.get("status") == "ACTIVE" and key_record.get("expires_at", 0) > now:
                is_valid = True

        if not is_valid:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(f"{to_bold('OWNER')}", url=OWNER_URL))
            bot.send_message(
                chat_id,
                "ভুল পাসওয়ার্ড! মালিকের সাথে যোগাযোগ করুন।",
                reply_markup=markup
            )
            return

        # Valid Key: Allocate Terminal
        status_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>\nটার্মিনাল নোড বরাদ্দ করা হচ্ছে...")
        terminals = firebase.get("/terminals") or {}
        allocated_node = None

        for t_id, t_info in terminals.items():
            if isinstance(t_info, dict) and t_info.get("status") == "FREE":
                allocated_node = t_id
                break

        if not allocated_node:
            safe_delete_message(chat_id, status_msg.message_id)
            bot.send_message(chat_id, "সবগুলো সার্ভার নোড এখন ব্যস্ত আছে। কিছুক্ষণ পর চেষ্টা করুন।")
            return

        # Bind Node
        firebase.patch(f"/terminals/{allocated_node}", {
            "status": "BUSY",
            "assigned_user_id": chat_id,
            "expires_at": now + 86400
        })
        u["assigned_node"] = allocated_node
        safe_delete_message(chat_id, status_msg.message_id)
        send_step4_platform_select(chat_id)
        return

    # AUTH SYSTEM B: SITE PHONE NUMBER
    if input_mode == "WAITING_SITE_PHONE":
        u["site_phone"] = text
        u["input_mode"] = None
        temp_prompt = u.pop("temp_prompt_id", None)
        safe_delete_message(chat_id, temp_prompt)
        send_step5_site_password_prompt(chat_id)
        return

    # AUTH SYSTEM B: SITE PASSWORD
    if input_mode == "WAITING_SITE_PASS":
        u["site_pass"] = text
        u["input_mode"] = None
        temp_prompt = u.pop("temp_prompt_id", None)
        safe_delete_message(chat_id, temp_prompt)

        assigned_node = u.get("assigned_node", NODE_ID)
        site_name = u.get("site_name", "Amar Club")
        phone = u.get("site_phone")
        pwd = text
        sid = f"{chat_id}_{int(time.time()) % 1000000}"
        u["active_sid"] = sid

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>")

        if assigned_node == NODE_ID:
            active_sessions[sid] = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "phone": phone,
                "password": pwd,
                "target_profit": 0,
                "total_steps": 7,
                "is_trading": False,
                "created_at": time.time(),
                "anim_tick": 0,
                "lock": threading.RLock()
            }
            threading.Thread(
                target=process_login,
                args=(chat_id, sid, phone, pwd, anim_msg.message_id),
                daemon=True
            ).start()
        else:
            # Delegate to assigned worker node via Firebase command
            firebase.patch(f"/terminals/{assigned_node}", {
                "command": {
                    "action": "START_SESSION",
                    "sid": sid,
                    "chat_id": chat_id,
                    "phone": phone,
                    "password": pwd,
                    "site_name": site_name
                },
                "site": site_name
            })
        return

    # PARAMETERS: TARGET & STEPS
    active_sid = u.get("active_sid")
    if active_sid and active_sid in active_sessions:
        sess = active_sessions[active_sid]
        sess_mode = sess.get("input_mode")
        if sess.get("temp_prompt_id"):
            safe_delete_message(chat_id, sess["temp_prompt_id"])
            sess["temp_prompt_id"] = None

        if sess_mode == "WAITING_TARGET":
            try:
                val = float(text)
                if val <= 0: raise ValueError()
                sess["target_profit"] = val
                sess["input_mode"] = None

                wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{active_sid}.png")
                def _shot(drv):
                    drv.save_screenshot(wingo_snap)
                safe_tab_execute(active_sid, _shot)

                cur_bal = sess.get("current_balance", 0.0)
                config_caption = (
                    f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                    f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                    f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
                )
                display_or_replace_photo(chat_id, active_sid, wingo_snap, config_caption, get_setup_param_keyboard(active_sid))
            except ValueError:
                p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
                sess["temp_prompt_id"] = p_msg.message_id

        elif sess_mode == "WAITING_STEPS":
            try:
                steps_val = int(text)
                if steps_val <= 0: raise ValueError()
                sess["total_steps"] = steps_val
                sess["input_mode"] = None

                wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{active_sid}.png")
                def _shot(drv):
                    drv.save_screenshot(wingo_snap)
                safe_tab_execute(active_sid, _shot)

                cur_bal = sess.get("current_balance", 0.0)
                config_caption = (
                    f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                    f"Selected Steps: <b>{steps_val}</b>\n\n"
                    f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
                )
                display_or_replace_photo(chat_id, active_sid, wingo_snap, config_caption, get_setup_param_keyboard(active_sid))
            except ValueError:
                p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
                sess["temp_prompt_id"] = p_msg.message_id

# ==============================================================================
# 16. Telegram Polling Thread
# ==============================================================================
def start_telegram_polling():
    print(f"[*] Starting Telegram infinity polling on {NODE_ID}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    while CLUSTER_RUNNING and IS_MASTER:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            print(f"[*] Polling encountered error: {e}")
            time.sleep(3)

# ==============================================================================
# 17. Main Cluster Entry Point
# ==============================================================================
if __name__ == "__main__":
    print(f"[*] Booting Node: {NODE_ID}...")
    register_node()

    # Launch daemon threads
    threading.Thread(target=node_heartbeat_worker, daemon=True).start()
    threading.Thread(target=cluster_watchdog_thread, daemon=True).start()
    threading.Thread(target=master_election_daemon, daemon=True).start()

    print(f"[*] {to_bold('HYBRID CLUSTER RUNNING')} [Node: {NODE_ID}]")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[*] Shutting down node cleanly...")
        CLUSTER_RUNNING = False
        firebase.delete(f"/terminals/{NODE_ID}")
        master_info = firebase.get("/cluster/active_master")
        if master_info and master_info.get("master_id") == NODE_ID:
            firebase.delete("/cluster/active_master")
        for sid in list(active_sessions.keys()):
            close_session_tab(sid)
        sys.exit(0)
