import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket
from datetime import datetime, timedelta

# ==============================================================================
# 1. AUTOMATIC PACKAGE DEPENDENCY INSTALLER
# ==============================================================================
def install_and_import(package_name, import_name=None):
    """Checks for required Python packages and installs them automatically if missing."""
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Missing package detected. Installing: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==============================================================================
# 2. MATHEMATICAL BOLD UNICODE CONVERTER & PORT FINDER
# ==============================================================================
def to_bold(text: str) -> str:
    """Converts standard ASCII letters and digits to Mathematical Bold Unicode (A->𝐀, a->𝐚, 0->𝟎)."""
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

def find_free_port():
    """Finds an available local network port dynamically to isolate WebDriver instances."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

# ==============================================================================
# 3. CORE CONFIGURATION & CONSTANTS
# ==============================================================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
ADMIN_CHAT_ID = 5693051408  # আপনার নিজস্ব এডমিন চ্যাট আইডি

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Platform URLs
URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"
URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

# Subscription Plans & Pricing Configuration
PAYMENT_CONFIG = {
    "BKASH_NUMBER": "017XXXXXXXX",   # আপনার বিকাশ পার্সোনাল নম্বর
    "NAGAD_NUMBER": "018XXXXXXXX",   # আপনার নগদ পার্সোনাল নম্বর
    "PLANS": {
        "plan_1d": {
            "name_bn": "১ দিন (২৪ ঘণ্টা ট্রায়াল)",
            "name_en": "1 Day VIP Trial (24h)",
            "price": 150,
            "days": 1,
            "duration_text_bn": "২৪ ঘণ্টা (১ দিন)",
            "duration_text_en": "24 Hours (1 Day)",
            "desc_bn": "অটোমেটেড ২৪ ঘণ্টা উইনগো সিগন্যাল ও মার্টিনগেল ট্রেডিং।"
        },
        "plan_7d": {
            "name_bn": "৭ দিন (সাপ্তাহিক ভিআইপি)",
            "name_en": "7 Days Weekly VIP",
            "price": 500,
            "days": 7,
            "duration_text_bn": "৭ দিন (সাপ্তাহিক)",
            "duration_text_en": "7 Days (Weekly)",
            "desc_bn": "১ সপ্তাহের ফুল সার্ভার এক্সেস, লাইভ ব্যালেন্স ও রিয়েলটাইম মনিটর।"
        },
        "plan_30d": {
            "name_bn": "১ মাস (৩০ দিন মান্থলি প্রো)",
            "name_en": "30 Days Monthly Pro",
            "price": 1500,
            "days": 30,
            "duration_text_bn": "৩০ দিন (১ মাস)",
            "duration_text_en": "30 Days (1 Month)",
            "desc_bn": "প্রফেশনাল ট্রেডারদের জন্য ৩০ দিনের ডেডিকেটেড ক্লাউড সেশন।"
        },
        "plan_365d": {
            "name_bn": "১ বছর (ইয়ারলি মাস্টার প্ল্যান)",
            "name_en": "1 Year Master VIP Plan",
            "price": 4500,
            "days": 365,
            "duration_text_bn": "৩৬৫ দিন (১ বছর)",
            "duration_text_en": "365 Days (1 Year)",
            "desc_bn": "১ বছরের আনলিমিটেড ট্রেডিং সাপোর্ট ও এআই ভিআইপি প্রিডিকশন ইঞ্জিন।"
        },
        "plan_life": {
            "name_bn": "লাইফটাইম (আজীবন আনলিমিটেড)",
            "name_en": "Lifetime Access",
            "price": 8000,
            "days": 3650,
            "duration_text_bn": "আজীবন (লাইফটাইম)",
            "duration_text_en": "Lifetime Unlimited",
            "desc_bn": "কোনো প্রকার মেয়াদ শেষ হওয়ার ঝামেলা ছাড়া লাইফটাইম ফুল অটোমেশন।"
        }
    }
}

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
DATABASE_FILE = os.path.expanduser("~/.ff_bot_users.json")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}
user_db = {}

# ==============================================================================
# DATABASE MANAGEMENT & VIP STATUS VALIDATION
# ==============================================================================
def load_database():
    global user_db
    if os.path.exists(DATABASE_FILE):
        try:
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                user_db = json.load(f)
        except Exception:
            user_db = {}
    else:
        user_db = {}

def save_database():
    try:
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(user_db, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Database save error: {e}")

load_database()

def is_vip_active(chat_id: int) -> bool:
    """Validates whether the user holds an active, non-expired VIP subscription."""
    str_id = str(chat_id)
    if chat_id == ADMIN_CHAT_ID:
        return True
    if str_id in user_db:
        sub_end = user_db[str_id].get("vip_until")
        if sub_end:
            try:
                expiry = datetime.strptime(sub_end, "%Y-%m-%d %H:%M:%S")
                return datetime.now() < expiry
            except Exception:
                return False
    return False

def get_vip_expiry_text(chat_id: int) -> str:
    """Returns the readable subscription validity string for users."""
    str_id = str(chat_id)
    if chat_id == ADMIN_CHAT_ID:
        return "LIFETIME ADMIN VIP"
    if str_id in user_db:
        return user_db[str_id].get("vip_until", "Expired")
    return "Not Subscribed"

# ==============================================================================
# 4. MULTI-INSTANCE ISOLATED FIREFOX LAUNCHER
# ==============================================================================
def launch_firefox_instance(chat_id, target_url):
    """
    Launches an independent Firefox clone instance for each user.
    Uses separate profile folders, separate ports, and avoids session clashing.
    """
    user_profile_dir = os.path.join(PROFILES_BASE_DIR, f"user_{chat_id}")
    os.makedirs(user_profile_dir, exist_ok=True)

    for lock_name in [".parentlock", "parent.lock", "lock"]:
        lp = os.path.join(user_profile_dir, lock_name)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    gecko_port = find_free_port()
    marionette_port = find_free_port()

    options = Options()
    options.add_argument("-no-remote")
    options.add_argument("-new-instance")
    options.add_argument("-profile")
    options.add_argument(user_profile_dir)

    if "DISPLAY" not in os.environ or not os.environ["DISPLAY"]:
        os.environ["DISPLAY"] = ":0"

    options.set_preference("marionette.port", marionette_port)
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)
    options.set_preference("browser.sessionstore.resume_from_crash", False)
    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("browser.shell.checkDefaultBrowser", False)

    service = FirefoxService(port=gecko_port)
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.maximize_window()
    except Exception:
        pass

    driver.get(target_url)
    return driver, user_profile_dir

def close_user_browser(chat_id):
    """Safely closes ONLY this user's browser without terminating other active users."""
    sess = user_sessions.get(chat_id)
    if not sess:
        return
    sess["is_trading"] = False
    driver = sess.get("driver")
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
        sess["driver"] = None
    sess["step"] = "IDLE"

    prof_dir = sess.get("profile_dir")
    if prof_dir and os.path.exists(prof_dir):
        for lock_name in [".parentlock", "parent.lock", "lock"]:
            lp = os.path.join(prof_dir, lock_name)
            if os.path.exists(lp):
                try:
                    os.remove(lp)
                except Exception:
                    pass

# ==============================================================================
# 5. IN-BROWSER JAVASCRIPT AUTOMATION CODE
# ==============================================================================
AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
  window.location.hash = '#/login';
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
  }, 1000);
}, 1000);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

const isBonusModal = bodyText.includes('BONUS DAILY RECHARGE') || 
                     bodyText.includes('DAILY RECHARGE') || 
                     bodyText.includes('Daily Bonus') ||
                     bodyText.includes('Deposit Bonus');

if (isBonusModal) {
    const confirmBtn = document.querySelector('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], button[class*="close"]');
    if (confirmBtn) {
        try { confirmBtn.click(); } catch(e){}
    }
    return { status: "SUCCESS" };
}

if (!href.includes('/login') && (!hash.includes('login') || hash === '#/' || hash.length >= 2)) {
    return { status: "SUCCESS" };
}

const toast = document.querySelector('.van-toast--text, .van-toast--fail, .van-toast');
if (toast && toast.innerText && toast.innerText.trim().length > 0) {
    const t = toast.innerText.trim();
    if (t.includes('Error') || t.includes('password') || t.includes('incorrect') || 
        t.includes('logged in') || t.includes('wrong') || t.includes('failed')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

if (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Win Go') || bodyText.includes('30S')) {
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
            uClk.textContent=uF(`${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`);
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
    h.innerHTML=`<span class="txt-blk drx-title-anim" id="drx-title">${uF('WINZY-MARTINGALE')}</span><span style="cursor:pointer;" class="txt-blk-err" id="sys-cls">X</span>`;
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
    p1.innerHTML=`<div style="text-align:center;margin-bottom:8px;padding:6px;background:transparent;border-radius:6px;border:2px solid #000;"><span class="txt-blk" style="font-size:9px;color:#ccc;">${uF('CURRENT BAL')}</span><br><span id="pre-bal" class="txt-blk" style="font-size:15px;color:#fff;">--</span></div>`;

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
    balBx.innerHTML=`<div class="txt-blk" style="font-size:9px;color:#ccc;">${uF('LIVE BAL / PROFIT')}</div><div id="ui-bal" class="txt-blk" style="font-size:16px;color:#fff;">--</div>`;

    let aiRow=`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('AI:')}</span><span id="ui-ai" class="txt-blk-cyan">VIP JSON API</span></div>`;
    const infBx=document.createElement('div');
    infBx.style.cssText='padding:6px;font-size:10px;line-height:2;background:transparent;border-radius:6px;border:2px solid #000;position:relative;overflow:hidden;';
    infBx.innerHTML=aiRow+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('TGT:')}</span><span id="ui-tgt" class="txt-blk" style="color:#fff;">0</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;" title="Double-click to set manual fixed bet"><span class="txt-blk" style="color:#ccc;">${uF('STP:')}</span><span id="ui-bet" class="txt-blk-warn" style="color:#ffcc00;cursor:pointer;">5</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('CLK:')}</span><span id="ui-clk" class="txt-blk" style="color:#fff;">00:30</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('STS:')}</span><span id="ui-sts" class="txt-blk" style="color:#fff;">${uF('WAIT')}</span></div>`;

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
        rL.style.cssText=`position:absolute;width:100%;height:2px;background:${cBase};box-shadow:0 0 10px 3px ${cBase};animation:sR 0.6s linear infinite alternate;`;
        let gL=document.createElement('div');
        gL.style.cssText=`position:absolute;height:100%;width:3px;background:${cBase};box-shadow:0 0 15px 5px ${cBase};animation:sG 0.6s cubic-bezier(0.25,0.1,0.25,1) infinite alternate;`;
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
                uBal.innerText=uF(`${st.curBal.toFixed(2)} (DONE)`);
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
                    uBet.innerText=uF(st.manualOverrideBet?tAmt+' (FIX)':`${tAmt} (S${st.stpIdx+1})`);
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
                        if(ghC)ghC.textContent=`Step: ${st.stpIdx+1}/${st.dynSeq.length} (Amt: ${tAmt})\\nPred: ${prediction} | W:${st.w} L:${st.l}`;
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
# 6. ENHANCED MESSAGING TEMPLATES (DETAILED TEXTS FOR ALL PLANS)
# ==============================================================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে প্রিমিয়াম উইনগো ট্রেডিং অটোমেশন সিস্টেমে।\n"
                f"দয়া করে আপনার পছন্দের ভাষা নির্বাচন করুন:"
            ),
            "vip_expired_menu": (
                f"<b>{to_bold('VIP SUBSCRIPTION REQUIRED')}</b>\n\n"
                f"প্রিয় গ্রাহক, এই প্রিমিয়াম অটোমেশন ইঞ্জিনটি ব্যবহার করতে সক্রিয় সাবস্ক্রিপশন প্রয়োজন।\n\n"
                f"<b>আমাদের বর্তমান ভিআইপি প্ল্যানসমূহ:</b>\n"
                f"🔹 ১ দিন (২৪ ঘণ্টা ট্রায়াল): <code>৳১৫০</code>\n"
                f"🔹 ৭ দিন (সাপ্তাহিক ভিআইপি): <code>৳৫০০</code>\n"
                f"🔹 ১ মাস (৩০ দিন মান্থলি প্রো): <code>৳১৫০০</code>\n"
                f"🔹 ১ বছর (৩৬৫ দিন ইয়ারলি মাস্টার): <code>৳৪৫০০</code>\n"
                f"🔹 আজীবন (লাইফটাইম আনলিমিটেড): <code>৳৮০০০</code>\n\n"
                f"<b>আপনি কতদিনের জন্য নিতে চান? নিচের বাটন থেকে নির্বাচন করুন:</b>"
            ),
            "plan_overview": (
                f"<b>{to_bold('SELECTED PLAN DETAILS')}</b>\n\n"
                f"নির্বাচিত প্ল্যান: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"অ্যাক্টিভেশন মেয়াদ: <b>{kwargs.get('duration', '')}</b>\n"
                f"প্রাইস: <code>৳ {kwargs.get('price', 0)} BDT</code>\n"
                f"বিবরণ: <i>{kwargs.get('desc', '')}</i>\n\n"
                f"<b>পেমেন্ট পদ্ধতি নির্বাচন করুন:</b>\n"
                f"আপনি কোন মাধ্যমে পেমেন্ট সম্পন্ন করতে চান? বিকাশ অথবা নগদ সিলেক্ট করুন:"
            ),
            "payment_sendmoney_guide": (
                f"<b>{to_bold('PAYMENT SEND MONEY INSTRUCTIONS')}</b>\n\n"
                f"গেটওয়ে: <b>{kwargs.get('method', '')} (Personal)</b>\n"
                f"প্ল্যান: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"মেয়াদ: <b>{kwargs.get('duration', '')}</b>\n"
                f"মোট প্রদেয় টাকা: <code>৳ {kwargs.get('price', 0)}</code>\n\n"
                f"<b>আমাদের {kwargs.get('method', '')} নম্বর:</b>\n"
                f"👉 <code>{kwargs.get('number', '')}</code> (ক্লিক করে কপি করুন)\n\n"
                f"<b>টাকা পাঠানোর নিয়মাবলী:</b>\n"
                f"১. আপনার {kwargs.get('method', '')} অ্যাপে ঢুকে <b>Send Money</b> অপশনে যান।\n"
                f"২. উপরে দেওয়া নম্বরে সঠিক পরিমাণ <code>৳{kwargs.get('price', 0)}</code> পাঠান।\n"
                f"৩. টাকা পাঠানোর পর ফিরতি এসএমএস থেকে প্রাপ্ত <b>Transaction ID (TrxID)</b> টি কপি করুন।\n"
                f"৪. কপি করা <b>TrxID</b> টি নিচে মেসেজ আকারে লিখে পাঠিয়ে দিন।"
            ),
            "trx_verified_success": (
                f"<b>{to_bold('PAYMENT VERIFIED & ACTIVATED')}</b>\n\n"
                f"অভিনন্দন! আপনার সাবস্ক্রিপশন সফলভাবে সক্রিয় করা হয়েছে।\n\n"
                f"সাবস্ক্রিপশন সারসংক্ষেপ:\n"
                f"প্যাকেজ: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"ট্রানজেকশন আইডি: <code>{kwargs.get('trx', '')}</code>\n"
                f"পদ্ধতি: <b>{kwargs.get('method', '')}</b>\n"
                f"মেয়াদ শেষ হবে: <code>{kwargs.get('expiry', '')}</code>\n\n"
                f"এখন আপনি সরাসরি ট্রেডিং প্ল্যাটফর্ম নির্বাচন করে কাজ শুরু করতে পারবেন।"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"ভিআইপি স্ট্যাটাস: <b>ACTIVE</b>\n"
                f"মেয়াদ: <code>{kwargs.get('expiry', 'Active')}</code>\n\n"
                f"ট্রেডিং প্ল্যাটফর্ম নির্বাচন করুন:"
            ),
            "input_phone": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:"
            ),
            "input_pass": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"একাউন্ট: <code>{kwargs.get('phone', '')}</code>\n"
                f"এবার আপনার পাসওয়ার্ড টি লিখে পাঠান:"
            ),
            "login_wait": (
                f"<b>{to_bold('CONNECTING')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"আইসোলেটেড ব্রাউজার চালু করে লগইন সম্পন্ন করা হচ্ছে..."
            ),
            "login_success_redirecting": (
                f"<b>{to_bold('LOGIN COMPLETED')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"একাউন্ট: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"স্বয়ংক্রিয়ভাবে উইনগো ৩০এস পেজে রিডাইরেক্ট করা হচ্ছে..."
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"কারণ: <i>{kwargs.get('error', 'ভুল তথ্য বা সংযোগ সমস্যা')}</i>\n\n"
                f"পুনরায় চেষ্টা করার জন্য /start পাঠান।"
            ),
            "wingo_ready": (
                f"<b>{to_bold('WINGO 30S TRIGGERED')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b> (WinGo 30S)\n"
                f"বর্তমান ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"ট্রেডিং শুরু করতে START অথবা বাতিল করতে CANCEL চাপুন:"
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"বর্তমান ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"আপনি কত টাকা প্রফিট করতে চান? সংখ্যাটি লিখে পাঠান (যেমন: <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"টার্গেট প্রফিট: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"মার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখে পাঠান (যেমন: <code>7</code> বা <code>10</code>):"
            ),
            "starting_trade": (
                f"<b>{to_bold('STARTING TRADING ENGINE')}</b>\n\n"
                f"অটো ট্রেডিং স্ক্রিপ্ট চালু হচ্ছে...\n"
                f"লাইভ স্ক্রিনশট নিচে পাঠানো হচ্ছে..."
            ),
            "running_dashboard": (
                f"<b>{to_bold('AUTOMATION ACTIVE 24/7')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"শুরুর ব্যালেন্স: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"টার্গেট ব্যালেন্স: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"মোট স্টেপ: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"ব্যাকগ্রাউন্ডে স্বয়ংক্রিয়ভাবে ট্রেডিং চলছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION CANCELLED')}</b>\n\n"
                f"আপনার ব্রাউজার সেশন বন্ধ করা হয়েছে।\n"
                f"নতুন সেশন শুরু করতে /start পাঠান।"
            ),
            "target_achieved": (
                f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
                f"রিপোর্ট:\n"
                f"শুরুর ব্যালেন্স: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"শেষ ব্যালেন্স: <code>৳ {kwargs.get('cur_bal', '0.00')}</code>\n"
                f"মোট প্রফিট: <code>+৳ {kwargs.get('profit', '0.00')}</code>\n\n"
                f"মোট উইন: <b>{kwargs.get('wins', 0)}</b>\n"
                f"মোট লস: <b>{kwargs.get('losses', 0)}</b>\n"
                f"টানা সর্বোচ্চ উইন: <b>{kwargs.get('max_w', 0)}</b>\n"
                f"টানা সর্বোচ্চ লস: <b>{kwargs.get('max_l', 0)}</b>"
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"Welcome to the Premium WinGo Auto-Trading Platform.\n"
                f"Please select your language:"
            ),
            "vip_expired_menu": (
                f"<b>{to_bold('VIP SUBSCRIPTION REQUIRED')}</b>\n\n"
                f"Dear user, you need an active subscription to access the cloud auto-bettor.\n\n"
                f"<b>Available Plans:</b>\n"
                f"🔹 1 Day Trial (24h): <code>৳150</code>\n"
                f"🔹 7 Days Weekly: <code>৳500</code>\n"
                f"🔹 1 Month (30 Days Pro): <code>৳1500</code>\n"
                f"🔹 1 Year (365 Days Master): <code>৳4500</code>\n"
                f"🔹 Lifetime Access: <code>৳8000</code>\n\n"
                f"<b>Select your preferred duration below:</b>"
            ),
            "plan_overview": (
                f"<b>{to_bold('SELECTED PLAN DETAILS')}</b>\n\n"
                f"Selected Plan: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"Duration: <b>{kwargs.get('duration', '')}</b>\n"
                f"Pricing: <code>৳ {kwargs.get('price', 0)} BDT</code>\n"
                f"Info: <i>{kwargs.get('desc', '')}</i>\n\n"
                f"<b>Choose Payment Gateway:</b>\n"
                f"Select bKash or Nagad to view payment instructions:"
            ),
            "payment_sendmoney_guide": (
                f"<b>{to_bold('PAYMENT SEND MONEY INSTRUCTIONS')}</b>\n\n"
                f"Method: <b>{kwargs.get('method', '')} (Personal)</b>\n"
                f"Plan: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"Duration: <b>{kwargs.get('duration', '')}</b>\n"
                f"Payable Amount: <code>৳ {kwargs.get('price', 0)}</code>\n\n"
                f"<b>Our {kwargs.get('method', '')} Wallet Number:</b>\n"
                f"👉 <code>{kwargs.get('number', '')}</code> (Click to copy)\n\n"
                f"<b>Payment Steps:</b>\n"
                f"1. Open your {kwargs.get('method', '')} App and go to <b>Send Money</b>.\n"
                f"2. Send exactly <code>৳{kwargs.get('price', 0)}</code> to the number above.\n"
                f"3. Copy the <b>Transaction ID (TrxID)</b> from the confirmation SMS.\n"
                f"4. Send the <b>TrxID</b> as a reply message here."
            ),
            "trx_verified_success": (
                f"<b>{to_bold('PAYMENT VERIFIED & ACTIVATED')}</b>\n\n"
                f"Congratulations! Your VIP plan is active now.\n\n"
                f"Details:\n"
                f"Plan: <b>{kwargs.get('plan_name', '')}</b>\n"
                f"TrxID: <code>{kwargs.get('trx', '')}</code>\n"
                f"Provider: <b>{kwargs.get('method', '')}</b>\n"
                f"Valid Until: <code>{kwargs.get('expiry', '')}</code>\n\n"
                f"You may now choose your trading platform and start."
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"VIP Status: <b>ACTIVE</b>\n"
                f"Expiry: <code>{kwargs.get('expiry', 'Active')}</code>\n\n"
                f"Choose Platform:"
            ),
            "input_phone": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\n"
                f"Enter your account phone number:"
            ),
            "input_pass": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n"
                f"Now enter your password:"
            ),
            "login_wait": (
                f"<b>{to_bold('CONNECTING')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Launching isolated browser and logging in..."
            ),
            "login_success_redirecting": (
                f"<b>{to_bold('LOGIN COMPLETED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Redirecting automatically to WinGo 30S page..."
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Invalid credentials or timeout')}</i>\n\n"
                f"Type /start to try again."
            ),
            "wingo_ready": (
                f"<b>{to_bold('WINGO 30S TRIGGERED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b> (WinGo 30S)\n"
                f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Press START to configure trading or CANCEL to exit:"
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Enter Target Profit Amount (e.g. <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"Target Profit: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"Enter total Martingale steps (e.g. <code>7</code> or <code>10</code>):"
            ),
            "starting_trade": (
                f"<b>{to_bold('STARTING TRADING ENGINE')}</b>\n\n"
                f"Automation script running...\n"
                f"Live browser footage attached below..."
            ),
            "running_dashboard": (
                f"<b>{to_bold('AUTOMATION ACTIVE 24/7')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background 24/7."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION CANCELLED')}</b>\n\n"
                f"Your browser session has been cleanly terminated.\n"
                f"Send /start to begin a new session."
            ),
            "target_achieved": (
                f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                f"Target profit reached.\n\n"
                f"Performance Report:\n"
                f"Start Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Final Balance: <code>৳ {kwargs.get('cur_bal', '0.00')}</code>\n"
                f"Net Profit: <code>+৳ {kwargs.get('profit', '0.00')}</code>\n\n"
                f"Total Wins: <b>{kwargs.get('wins', 0)}</b>\n"
                f"Total Losses: <b>{kwargs.get('losses', 0)}</b>\n"
                f"Max Win Streak: <b>{kwargs.get('max_w', 0)}</b>\n"
                f"Max Loss Streak: <b>{kwargs.get('max_l', 0)}</b>"
            )
        }
    }

    return messages.get(lang, messages["bn"]).get(key, "")

# ==============================================================================
# 7. KEYBOARD CONTROLS (DETAILED BUTTONS WITH PRICING)
# ==============================================================================
def get_plans_keyboard():
    """Generates keyboard for all plans with exact pricing tags."""
    markup = InlineKeyboardMarkup(row_width=1)
    p = PAYMENT_CONFIG["PLANS"]
    markup.add(
        InlineKeyboardButton(f"১ দিন (২৪ ঘণ্টা) - ৳{p['plan_1d']['price']}", callback_data="buy_plan_1d"),
        InlineKeyboardButton(f"৭ দিন (সাপ্তাহিক) - ৳{p['plan_7d']['price']}", callback_data="buy_plan_7d"),
        InlineKeyboardButton(f"১ মাস (৩০ দিন) - ৳{p['plan_30d']['price']}", callback_data="buy_plan_30d"),
        InlineKeyboardButton(f"১ বছর (৩৬৫ দিন) - ৳{p['plan_365d']['price']}", callback_data="buy_plan_365d"),
        InlineKeyboardButton(f"আজীবন (লাইফটাইম) - ৳{p['plan_life']['price']}", callback_data="buy_plan_life")
    )
    return markup

def get_payment_method_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('BKASH')}", callback_data="pay_bkash"),
        InlineKeyboardButton(f"{to_bold('NAGAD')}", callback_data="pay_nagad")
    )
    markup.add(
        InlineKeyboardButton(f"« {to_bold('BACK TO PLANS')}", callback_data="pay_back_plans")
    )
    return markup

def get_start_or_cancel_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START')}", callback_data="btn_start_flow"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data="btn_cancel_flow")
    )
    return markup

def get_trading_control_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('LIVE FOOTAGE')}", callback_data="btn_screenshot"),
        InlineKeyboardButton(f"{to_bold('LIVE BALANCE')}", callback_data="btn_live_balance")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS REPORT')}", callback_data="btn_stats_report"),
        InlineKeyboardButton(f"{to_bold('STOP TRADING')}", callback_data="btn_stop_trade")
    )
    return markup

# ==============================================================================
# 8. BACKGROUND MONITORING & 24H CLEANER
# ==============================================================================
def monitor_trading_progress(chat_id):
    while True:
        sess = user_sessions.get(chat_id)
        if not sess or not sess.get("is_trading"):
            break

        driver = sess.get("driver")
        if not driver:
            break

        try:
            js_data = driver.execute_script("""
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

                    screen_path = os.path.join(PROFILES_BASE_DIR, f"win_{chat_id}.png")
                    try:
                        driver.save_screenshot(screen_path)
                    except Exception:
                        screen_path = None

                    msg = get_text(
                        chat_id, "target_achieved",
                        start_bal=f"{start_b:.2f}",
                        cur_bal=f"{sess['cur_bal']:.2f}",
                        profit=f"{profit:.2f}",
                        wins=sess["wins"],
                        losses=sess["losses"],
                        max_w=sess["max_w"],
                        max_l=sess["max_l"]
                    )

                    if screen_path and os.path.exists(screen_path):
                        with open(screen_path, "rb") as photo:
                            bot.send_photo(chat_id, photo, caption=msg)
                        try:
                            os.remove(screen_path)
                        except Exception:
                            pass
                    else:
                        bot.send_message(chat_id, msg)
                    break
        except Exception:
            pass

        time.sleep(4)

def idle_session_reaper():
    """Keeps idle sessions alive up to 24 hours before removing them."""
    while True:
        try:
            now = time.time()
            for cid, sess in list(user_sessions.items()):
                if not sess.get("is_trading"):
                    last_active = sess.get("last_active", now)
                    if now - last_active > 86400:  # 24 hours
                        print(f"[*] Cleaning up 24h idle browser session for {cid}")
                        close_user_browser(cid)
        except Exception:
            pass
        time.sleep(3600)

threading.Thread(target=idle_session_reaper, daemon=True).start()

# ==============================================================================
# 9. LOGIN & DIRECT REDIRECT FLOW
# ==============================================================================
def process_login(chat_id, phone, password, status_msg_id):
    sess = user_sessions.get(chat_id, {})
    sess["last_active"] = time.time()
    site_name = sess.get("site_name", "Amar Club")

    login_url = URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN
    wingo_url = URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO

    driver = None
    try:
        driver, prof_dir = launch_firefox_instance(chat_id, login_url)
        sess["driver"] = driver
        sess["profile_dir"] = prof_dir
    except Exception as e:
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error=str(e)),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        return

    fill_ok = False
    for _ in range(80):
        try:
            res = driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
            if res == "SUCCESS":
                fill_ok = True
                time.sleep(2.5)
                break
        except Exception:
            pass
        time.sleep(0.5)

    if not fill_ok:
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error="লগইন ইনপুট ফিল্ড পাওয়া যায়নি"),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        close_user_browser(chat_id)
        return

    login_status = "PENDING"
    err_detail = ""
    for _ in range(40):
        try:
            res = driver.execute_script(CHECK_LOGIN_STATUS_JS)
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "ভুল ফোন বা পাসওয়ার্ড")
                break
        except Exception:
            pass
        time.sleep(0.5)

    if login_status == "ERROR":
        close_user_browser(chat_id)
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error=err_detail),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        return

    bot.edit_message_text(
        get_text(chat_id, "login_success_redirecting", site_name=site_name, phone=phone),
        chat_id=chat_id,
        message_id=status_msg_id
    )

    time.sleep(1.2)
    try:
        driver.get(wingo_url)
    except Exception as e:
        print(f"[*] Navigation error: {e}")

    wingo_ready = False
    for _ in range(30):
        try:
            ready_res = driver.execute_script(CHECK_WINGO_READY_JS)
            if ready_res:
                wingo_ready = True
                break
        except Exception:
            pass
        time.sleep(1)

    time.sleep(2)

    current_bal = 0.0
    for _ in range(15):
        try:
            bal_res = driver.execute_script(FETCH_BALANCE_JS)
            if bal_res and float(bal_res) > 0:
                current_bal = float(bal_res)
                break
        except Exception:
            pass
        time.sleep(0.8)

    sess["current_balance"] = current_bal
    sess["step"] = "WINGO_TRIGGERED_READY"

    bot.send_message(
        chat_id,
        get_text(chat_id, "wingo_ready", site_name=site_name, balance=f"{current_bal:.2f}"),
        reply_markup=get_start_or_cancel_keyboard()
    )

# ==============================================================================
# 10. TELEGRAM HANDLERS (VIP PLANS, PAYMENTS & TRADING)
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn",
        "last_active": time.time()
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
    sess = user_sessions.setdefault(chat_id, {"last_active": time.time()})
    sess["last_active"] = time.time()

    # 1. Language Handler
    if data in ["lang_en", "lang_bn"]:
        sess["lang"] = "en" if data == "lang_en" else "bn"
        bot.answer_callback_query(call.id)

        # Check Subscription
        if is_vip_active(chat_id):
            sess["step"] = "CHOOSE_SITE"
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
                InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
            )
            bot.edit_message_text(
                get_text(chat_id, "choose_site", expiry=get_vip_expiry_text(chat_id)),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=markup
            )
        else:
            sess["step"] = "SELECTING_PLAN"
            bot.edit_message_text(
                get_text(chat_id, "vip_expired_menu"),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_plans_keyboard()
            )

    # 2. Plan Selection Handlers
    elif data.startswith("buy_plan_"):
        plan_key = data.replace("buy_", "")
        plan_dict = PAYMENT_CONFIG["PLANS"].get(plan_key)
        if plan_dict:
            sess["selected_plan"] = plan_key
            sess["step"] = "SELECTING_PAYMENT_METHOD"
            bot.answer_callback_query(call.id)

            is_bn = sess.get("lang", "bn") == "bn"
            p_name = plan_dict["name_bn"] if is_bn else plan_dict["name_en"]
            d_text = plan_dict["duration_text_bn"] if is_bn else plan_dict["duration_text_en"]
            desc_text = plan_dict["desc_bn"]

            bot.edit_message_text(
                get_text(
                    chat_id, "plan_overview",
                    plan_name=p_name,
                    duration=d_text,
                    price=plan_dict["price"],
                    desc=desc_text
                ),
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_payment_method_keyboard()
            )

    elif data == "pay_back_plans":
        bot.answer_callback_query(call.id)
        sess["step"] = "SELECTING_PLAN"
        bot.edit_message_text(
            get_text(chat_id, "vip_expired_menu"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_plans_keyboard()
        )

    # 3. Payment Method Handlers (bKash & Nagad)
    elif data in ["pay_bkash", "pay_nagad"]:
        method_name = "bKash" if data == "pay_bkash" else "Nagad"
        target_number = PAYMENT_CONFIG["BKASH_NUMBER"] if data == "pay_bkash" else PAYMENT_CONFIG["NAGAD_NUMBER"]
        plan_key = sess.get("selected_plan", "plan_1d")
        plan_dict = PAYMENT_CONFIG["PLANS"].get(plan_key)

        sess["payment_method"] = method_name
        sess["step"] = "WAITING_TRXID"
        bot.answer_callback_query(call.id)

        is_bn = sess.get("lang", "bn") == "bn"
        p_name = plan_dict["name_bn"] if is_bn else plan_dict["name_en"]
        d_text = plan_dict["duration_text_bn"] if is_bn else plan_dict["duration_text_en"]

        bot.edit_message_text(
            get_text(
                chat_id, "payment_sendmoney_guide",
                method=method_name,
                plan_name=p_name,
                duration=d_text,
                price=plan_dict["price"],
                number=target_number
            ),
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # 4. Target Portal Handlers
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        sess["site_name"] = site_name
        sess["step"] = "WAITING_PHONE"

        bot.answer_callback_query(call.id, site_name)
        bot.edit_message_text(
            get_text(chat_id, "input_phone"),
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # 5. Trading Flow Buttons
    elif data == "btn_start_flow":
        bot.answer_callback_query(call.id)
        sess["step"] = "WAITING_TARGET_PROFIT"
        cur_bal = sess.get("current_balance", 0.0)
        bot.send_message(
            chat_id,
            get_text(chat_id, "input_target", balance=f"{cur_bal:.2f}")
        )

    elif data == "btn_cancel_flow":
        bot.answer_callback_query(call.id, "Session Cancelled")
        close_user_browser(chat_id)
        bot.edit_message_text(
            get_text(chat_id, "cancelled"),
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # 6. Live Dashboard Control Buttons
    elif data == "btn_screenshot":
        driver = sess.get("driver")
        if driver:
            bot.answer_callback_query(call.id, "Capturing live footage...")
            temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{chat_id}.png")
            try:
                driver.save_screenshot(temp_shot)
                with open(temp_shot, "rb") as p:
                    bot.send_photo(
                        chat_id, p,
                        caption=f"<b>{to_bold('LIVE BROWSER FOOTAGE')}</b>\nসময়: <code>{time.strftime('%H:%M:%S')}</code>"
                    )
                os.remove(temp_shot)
            except Exception as e:
                bot.send_message(chat_id, f"Error: {e}")
        else:
            bot.answer_callback_query(call.id, "Browser not active!", show_alert=True)

    elif data == "btn_live_balance":
        driver = sess.get("driver")
        if driver:
            try:
                b = driver.execute_script(FETCH_BALANCE_JS)
                bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "Fetching...", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "No active session!", show_alert=True)

    elif data == "btn_stats_report":
        driver = sess.get("driver")
        if driver:
            try:
                data_rep = driver.execute_script("""
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
                if data_rep:
                    stat_txt = (
                        f"<b>{to_bold('LIVE TRADING STATS')}</b>\n\n"
                        f"বর্তমান ব্যালেন্স: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                        f"টার্গেট: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                        f"মার্টিনগেল স্টেপ: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                        f"উইন: <b>{data_rep['w']}</b> | লস: <b>{data_rep['l']}</b>"
                    )
                    bot.send_message(chat_id, stat_txt)
                else:
                    bot.answer_callback_query(call.id, "Script initializing...", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "No stats available.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Browser not active!", show_alert=True)

    elif data == "btn_stop_trade":
        driver = sess.get("driver")
        if driver:
            try:
                driver.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
                sess["is_trading"] = False
                bot.answer_callback_query(call.id, "Trading paused.", show_alert=True)
                bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং সাময়িকভাবে থামানো হয়েছে।")
            except Exception:
                bot.answer_callback_query(call.id, "Error executing stop.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "No active trade!", show_alert=True)

# ==============================================================================
# 11. TEXT INPUT DISPATCHER & SESSION STEP ROUTER
# ==============================================================================
@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_user_text(message):
    chat_id = message.chat.id
    sess = user_sessions[chat_id]
    sess["last_active"] = time.time()
    step = sess.get("step")
    text = message.text.strip()

    # Step A: Waiting for Transaction ID (TrxID)
    if step == "WAITING_TRXID":
        if len(text) < 6:
            bot.send_message(chat_id, "দয়া করে সঠিক Transaction ID (TrxID) লিখে পাঠান (যেমন: <code>BL57XX89</code>):")
            return

        plan_key = sess.get("selected_plan", "plan_1d")
        plan_dict = PAYMENT_CONFIG["PLANS"].get(plan_key)
        valid_days = plan_dict["days"]
        expiry_time = (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d %H:%M:%S")

        # Store to database
        user_db[str(chat_id)] = {
            "vip_until": expiry_time,
            "trx": text,
            "method": sess.get("payment_method", "bKash"),
            "plan": plan_key,
            "activated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_database()

        is_bn = sess.get("lang", "bn") == "bn"
        p_name = plan_dict["name_bn"] if is_bn else plan_dict["name_en"]

        bot.send_message(
            chat_id,
            get_text(
                chat_id, "trx_verified_success",
                plan_name=p_name,
                trx=text,
                method=sess.get("payment_method", "bKash"),
                expiry=expiry_time
            )
        )

        sess["step"] = "CHOOSE_SITE"
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
            InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
        )
        bot.send_message(
            chat_id,
            get_text(chat_id, "choose_site", expiry=expiry_time),
            reply_markup=markup
        )

    # Step B: Waiting for Platform Phone Number
    elif step == "WAITING_PHONE":
        sess["phone"] = text
        sess["step"] = "WAITING_PASS"
        bot.send_message(chat_id, get_text(chat_id, "input_pass", phone=text))

    # Step C: Waiting for Platform Password
    elif step == "WAITING_PASS":
        sess["password"] = text
        sess["step"] = "LOGGING_IN"

        status_msg = bot.send_message(
            chat_id,
            get_text(chat_id, "login_wait", site_name=sess.get("site_name", "Amar Club"))
        )

        threading.Thread(
            target=process_login,
            args=(chat_id, sess["phone"], sess["password"], status_msg.message_id),
            daemon=True
        ).start()

    # Step D: Waiting for Target Profit Amount
    elif step == "WAITING_TARGET_PROFIT":
        try:
            val = float(text)
            if val <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "দয়া করে একটি সঠিক পজিটিভ অ্যামাউন্ট লিখুন (যেমন: <code>500</code>):")
            return

        sess["target_profit"] = val
        sess["step"] = "WAITING_STEPS"

        bot.send_message(
            chat_id,
            get_text(chat_id, "input_steps", target=val)
        )

    # Step E: Waiting for Martingale Steps and Inject Engine
    elif step == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: <code>7</code>):")
            return

        sess["total_steps"] = steps_val
        sess["step"] = "TRADING_RUNNING"
        sess["is_trading"] = True

        driver = sess.get("driver")
        if not driver:
            bot.send_message(chat_id, "ব্রাউজার সংযোগ নেই। /start দিয়ে পুনরায় শুরু করুন।")
            return

        bot.send_message(chat_id, get_text(chat_id, "starting_trade"))

        try:
            driver.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
        except Exception as e:
            bot.send_message(chat_id, f"স্ক্রিপ্ট এক্সিকিউশনে সমস্যা: {e}")
            return

        time.sleep(2)

        start_snap = os.path.join(PROFILES_BASE_DIR, f"start_{chat_id}.png")
        try:
            driver.save_screenshot(start_snap)
            with open(start_snap, "rb") as ph:
                bot.send_photo(
                    chat_id, ph,
                    caption=f"<b>{to_bold('LIVE BROWSER FOOTAGE')}</b>\nটার্গেট প্রফিট: <code>৳ {sess['target_profit']}</code> | ব্যাকআপ: <code>{sess['total_steps']} Steps</code>"
                )
            os.remove(start_snap)
        except Exception as e:
            print(f"[*] Snapshot error: {e}")

        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        bot.send_message(
            chat_id,
            get_text(
                chat_id, "running_dashboard",
                site_name=sess.get("site_name", "Amar Club"),
                start_bal=f"{cur_b:.2f}",
                target_bal=f"{target_total:.2f}",
                steps=sess["total_steps"]
            ),
            reply_markup=get_trading_control_keyboard()
        )

        threading.Thread(target=monitor_trading_progress, args=(chat_id,), daemon=True).start()

# ==============================================================================
# 12. MAIN INITIALIZATION
# ==============================================================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT MULTI-INSTANCE READY')}...")
    bot.infinity_polling()
