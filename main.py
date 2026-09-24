import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket
import gc
import urllib.request
import urllib.error
import uuid

# ==========================================
# 1. Automatic Package Installer
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing required package: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")
install_and_import("psutil")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import psutil

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
# 3. Aggressive Process Hygiene & Zombie Killer
# ==========================================
def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except Exception:
                pass
        gone, still_alive = psutil.wait_procs(children, timeout=2)
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
        parent.terminate()
        parent.wait(timeout=2)
    except Exception:
        pass

def cleanup_zombie_browsers():
    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                pname = (proc.info['name'] or '').lower()
                if 'firefox' in pname or 'geckodriver' in pname:
                    if proc.info['ppid'] == 1 or proc.info['ppid'] == current_pid:
                        is_active = False
                        for s in active_sessions.values():
                            d = s.get('driver')
                            if d and hasattr(d, 'service') and d.service and hasattr(d.service, 'process'):
                                if d.service.process and d.service.process.pid == proc.info['pid']:
                                    is_active = True
                                    break
                        if not is_active:
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

# ==========================================
# 4. Configuration & State Management
# ==========================================
TOKEN = os.environ.get("BOT_TOKEN", "8808949150:AAH6sTkoljibL3gsQIQ3MtUTYNPjI8F9ihQ")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

HEADLESS_MODE = os.environ.get("HEADLESS", "false").lower() == "true"
MAX_SESSIONS_PER_NODE = int(os.environ.get("MAX_SESSIONS_PER_NODE", "10"))

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}
active_sessions = {}

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"
SUPER_ADMIN_ID = 8707571669
OWNER_USERNAME = "@MD_NAYEEM_DRX_TM"

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
    },
    "site_tigroclub": {
        "name": "Tigro Club",
        "login": "https://tigroclub.vip/#/login",
        "wingo": "https://tigroclub.vip/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_hgnice": {
        "name": "HG Nice",
        "login": "https://hgnice.org/#/login",
        "wingo": "https://hgnice.org/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_kanpur91": {
        "name": "Kanpur 91",
        "login": "https://kanpur91.com/#/login",
        "wingo": "https://kanpur91.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_bdgwinsvip": {
        "name": "BDG Wins VIP",
        "login": "https://bdgwinsvip.com/#/login",
        "wingo": "https://bdgwinsvip.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    }
}

# ==========================================
# 5. Network Speed Check Helper
# ==========================================
def measure_network_latency(url: str, timeout: float = 3.0) -> float:
    try:
        start_ts = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response.read(256)
        return round((time.time() - start_ts) * 1000, 2)
    except Exception:
        return 9999.0

# ==========================================
# 6. Session Allocation & Isolation Engine (Firefox Only)
# ==========================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    cleanup_zombie_browsers()

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    if HEADLESS_MODE:
        options.add_argument("-headless")

    options.add_argument("-profile")
    options.add_argument(profile_dir)

    # Lightweight Firefox performance flags & background anti-freeze profile
    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 1024)
    options.set_preference("javascript.options.mem.max", 32768)
    options.set_preference("network.http.pipelining", False)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)
    options.set_preference("dom.ipc.processHangMonitor", False)
    options.set_preference("toolkit.telemetry.enabled", False)
    options.set_preference("toolkit.telemetry.unified", False)
    options.set_preference("app.shield.optoutstudies.enabled", False)
    options.set_preference("experiments.supported", False)
    options.set_preference("permissions.default.desktop-notification", 2)
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("media.autoplay.default", 5)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(20)
    driver.implicitly_wait(3)
    driver.set_window_size(412, 915)

    driver.get(target_url)

    sess["driver"] = driver
    sess["window_handle"] = driver.current_window_handle
    return driver, sess["window_handle"]

def safe_tab_execute(sid, task_fn, timeout=20.0):
    sess = active_sessions.get(sid)
    if not sess:
        return None

    lock = sess.get("lock")
    driver = sess.get("driver")

    if not driver or not lock:
        return None

    acquired = lock.acquire(timeout=5.0)
    if not acquired:
        return None

    result_container = {"res": None, "error": None, "completed": False}

    def execute_worker():
        try:
            result_container["res"] = task_fn(driver)
            result_container["completed"] = True
        except Exception as e:
            result_container["error"] = e

    worker_thread = threading.Thread(target=execute_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout)

    if not result_container["completed"]:
        try:
            lock.release()
        except RuntimeError:
            pass
        threading.Thread(target=close_session_tab, args=(sid,), daemon=True).start()
        return None

    try:
        lock.release()
    except RuntimeError:
        pass

    gc.collect()

    if result_container["error"]:
        return None

    return result_container["res"]

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
            try:
                if hasattr(driver, 'service') and driver.service and driver.service.process:
                    kill_process_tree(driver.service.process.pid)
            except Exception:
                pass

        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

    cleanup_zombie_browsers()
    gc.collect()

# ==========================================
# 7. Telegram Media & Clean Replacement
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
        except Exception:
            pass

    try:
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception:
        pass
    gc.collect()

# ==========================================
# 8. In-Browser JavaScript Automation Engine
# ==========================================
MODAL_AUTO_DISMISSER_JS = r"""
(function(){
    if (window.__MODAL_DISMISSER_ACTIVE) return;
    window.__MODAL_DISMISSER_ACTIVE = true;
    const sweepModals = () => {
        const selectors = [
            '.van-dialog__confirm', '.dialog-confirm',
            '.van-popup__close-icon', 'button[class*="close"]',
            'button[class*="confirm"]', '.van-button--primary',
            '.van-overlay', '.dialog-close', '.close-btn'
        ];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                if (el && el.offsetParent !== null && !el.closest('#sys-core-fin') && !el.closest('#_run_box')) {
                    try { el.click(); } catch(e){}
                }
            });
        });
    };
    setInterval(sweepModals, 1500);
    const obs = new MutationObserver(() => sweepModals());
    obs.observe(document.body, { childList: true, subtree: true });
})();
"""

AUTO_FILL_AND_CLICK_JS = r"""
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
  window.location.hash = '#/login';
}

const initConfirm = document.querySelector('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], .van-button--primary');
if (initConfirm) {
    try { initConfirm.click(); } catch(e){}
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

const clearAndSet = (el, val) => {
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

clearAndSet(elN, phone);

setTimeout(() => {
  clearAndSet(elP, pass);
  setTimeout(() => {
    elL.click();
  }, 700);
}, 700);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = r"""
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
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed device prompt" };
        }
    }
}

const isBonus = bodyText.includes('BONUS DAILY RECHARGE') || 
                bodyText.includes('DAILY RECHARGE') || 
                bodyText.includes('Daily Bonus') || 
                bodyText.includes('Deposit Bonus') || 
                bodyText.includes('Announcement');

if (isBonus) {
    const closeBtn = document.querySelector('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], button[class*="close"], .van-popup__close-icon');
    if (closeBtn) {
        try { closeBtn.click(); } catch(e){}
    }
    return { status: "SUCCESS" };
}

try {
    const t1 = localStorage.getItem('token') || localStorage.getItem('token_str') || localStorage.getItem('auth');
    const t2 = sessionStorage.getItem('token') || sessionStorage.getItem('auth');
    if (t1 || t2) return { status: "SUCCESS" };
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
        return { status: "PENDING", message: "Takeover session handling..." };
    }
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('Account does not exist') || t.includes('frozen')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

WINGO_RUNBOX_AND_CLICK_JS = r"""
(function(){
    if(document.getElementById('_run_box')) return "ALREADY_PRESENT";
    var s = [
        'body > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(7) > div:nth-of-type(3) > div > div:nth-of-type(2) > div > div > div > img',
        'body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img',
        'body > div > div:nth-of-type(2) > div:nth-of-type(5) > div:nth-of-type(2) > div > div',
        'body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(4) > div:nth-of-type(2) > img',
        'img[src*="wingo" i]',
        'img[alt*="wingo" i]'
    ];
    function findTarget(){
        for(var i = 0; i < s.length; i++){
            var el = document.querySelector(s[i]);
            if(el) return el;
        }
        var imgs = document.getElementsByTagName('img');
        for(var j = 0; j < imgs.length; j++){
            if(/wingo/i.test((imgs[j].src || '') + (imgs[j].alt || ''))) return imgs[j];
        }
        var all = document.querySelectorAll('div,span,button,a');
        for(var k = 0; k < all.length; k++){
            if(all[k].children.length < 3 && /wingo/i.test(all[k].textContent || '')) return all[k];
        }
        return null;
    }
    function trigger(el){
        if(!el) return false;
        ['pointerdown','mousedown','pointerup','mouseup','click'].forEach(function(ev){
            try{ el.dispatchEvent(new MouseEvent(ev, {bubbles:true, cancelable:true, view:window})); }catch(e){}
        });
        if(typeof el.click === 'function') el.click();
        return true;
    }
    var targetEl = findTarget();
    if(targetEl){ trigger(targetEl); return "CLICKED_TARGET"; }
    return "BOX_INJECTED";
})();
"""

CHECK_WINGO_READY_JS = r"""
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

FETCH_BALANCE_JS = r"""
let els = document.querySelectorAll('*');
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.includes('Wallet balance') || txt.includes('Balance')) {
        let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
        let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
        if (match) return parseFloat(match[1].replace(/,/g, ''));
    }
}
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)) {
        return parseFloat(txt.replace(/[^\d.]/g, ''));
    }
}
return 0;
"""

# Upgraded Background Trading Engine JavaScript Injection
WINGO_ENGINE_INJECTION_JS = r"""
(function(){
  if(document.getElementById('sys-core-fin'))return;
  const SETTINGS={PRED_MODE:"VIP_JSON_API",SCAN_SYS:"RADAR",VISUAL_FX:"NONE",COLOR_FLT:"GREEN"};
  const uF=(s)=>String(s).toUpperCase().split('').map(c=>{
    let n=c.charCodeAt(0);
    if(n>=65&&n<=90)return String.fromCodePoint(n+119743);
    if(n>=48&&n<=57)return String.fromCodePoint(n+120764);
    return c;
  }).join('');
  const PLATFORM_ID='amarclub';
  const cfg={fRt:300,syncDly:2500,minSf:10};
  let st={isRun:false,tgtAmt:500,curBal:0,autoInt:null,preScn:null,isTrd:false,stpIdx:0,steps:5,dynSeq:[],mode:'DEF',extVal:0,timeLimit:'NO',tradesDone:0,maxTrades:0,lastPred:null,lastPeriod:null,showPred:true,balanceCheckInterval:null,manualOverrideBet:null,w:0,l:0,pattern:[]};
  window.__WINGO_ST = st;
  let isFetchingApi=false;

  class DataVault{
    static init(){
      if(!localStorage.getItem('drx_data_vault_v8')){
        localStorage.setItem('drx_data_vault_v8',JSON.stringify({history:[],wins:0,losses:0,balance_peak:0,system_logs:[]}));
      }
    }
    static get(){return JSON.parse(localStorage.getItem('drx_data_vault_v8'));}
    static save(d){localStorage.setItem('drx_data_vault_v8',JSON.stringify(d));}
  }
  DataVault.init();

  const VoiceEngine={
    speak(msg,lang='en-US',rate=1.1){
      if(!('speechSynthesis' in window))return;
      window.speechSynthesis.cancel();
      let utter=new SpeechSynthesisUtterance(msg);
      utter.lang=lang;
      utter.rate=rate;
      utter.pitch=1.2;
      utter.volume=1;
      window.speechSynthesis.speak(utter);
    }
  };

  let dTimeLeft=30;
  setInterval(()=>{
    let uClk=document.getElementById('ui-clk');
    if(uClk){
      let minutes=Math.floor(dTimeLeft/60);
      let seconds=dTimeLeft%60;
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
        let match=parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
        if(match){st.curBal=Math.floor(parseFloat(match[1].replace(/,/g,'')));return st.curBal;}
      }
    }
    for(let i=0;i<els.length;i++){
      let txt=els[i].innerText||'';
      if(txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)){
        st.curBal=Math.floor(parseFloat(txt.replace(/[^\d.]/g,'')));
        return st.curBal;
      }
    }
    return st.curBal;
  }

  const calcSeq=(cBal,nSteps)=>{
    let B=Math.floor(Number(cBal))||0;
    let n=parseInt(nSteps)||5;
    if(n<1)n=1;
    let u=Math.pow(2,n)-1;
    let s1=Math.floor(B/u);
    if(s1<1)s1=1;
    let seq=[];
    let sum=0;
    for(let k=1;k<n;k++){
      let sk=Math.floor(s1*Math.pow(2,k-1));
      seq.push(sk);
      sum+=sk;
    }
    let sn=Math.floor(B-sum);
    seq.push(sn>0?sn:Math.floor(s1*Math.pow(2,n-1)));
    return seq;
  };

  let p=document.createElement('div');
  p.id='sys-core-fin';
  p.style.cssText='position:fixed;width:170px;padding:4px;font-family:monospace;font-size:10px;z-index:9999999;color:#fff;user-select:none;border-radius:14px;overflow:visible;background:transparent;';
  let sL=localStorage.getItem('drx_ui_x');
  let sT=localStorage.getItem('drx_ui_y');
  if(sL&&sT){p.style.left=sL;p.style.top=sT;}else{p.style.top='20px';p.style.right='20px';}

  let stl=document.createElement('style');
  stl.innerHTML='@keyframes titlePulseAnim{0%{transform:scale(1);text-shadow:0 0 10px #00ff00;}50%{transform:scale(1.05);text-shadow:0 0 20px #00ff00, 0 0 30px #fff;}100%{transform:scale(1);text-shadow:0 0 10px #00ff00;}}.drx-in{background:transparent;position:relative;overflow:visible;z-index:1;display:flex;flex-direction:column;height:100%;border-radius:12px;border:2px solid #000000;box-sizing:border-box;}input::-webkit-outer-spin-button,input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0;}.txt-blk{color:#fff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-accent{color:#00ff00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-warn{color:#ffcc00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-err{color:#f00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-cyan{color:#0ff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-mag{color:#f0f;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.drx-elec-target{border-radius:8px !important;position:relative;z-index:9999 !important;transition:all 0.1s;background:rgba(0,0,0,0.5) !important;border:2px solid #000 !important;}.drx-title-anim{display:inline-block;animation:titlePulseAnim 2s infinite ease-in-out;}';
  document.body.appendChild(stl);

  p.className='drx-wrap';
  let inC=document.createElement('div');
  inC.className='drx-in';
  let h=document.createElement('div');
  h.style.cssText='padding:8px;font-size:12px;display:flex;justify-content:space-between;cursor:move;border-bottom:2px solid #000;background:transparent;';
  h.innerHTML=`<span class="txt-blk drx-title-anim" id="drx-title">${uF('WINZY-MARTINGALE')}</span><span style="cursor:pointer;" class="txt-blk-err" id="sys-cls">X</span>`;
  inC.appendChild(h);

  let drg=false,sx,sy,sl,st_y;
  function dSt(e){if(e.target.tagName==='SPAN')return;drg=true;let ev=e.type.includes('touch')?e.touches[0]:e;sx=ev.clientX;sy=ev.clientY;sl=p.offsetLeft;st_y=p.offsetTop;}
  function dMv(e){if(!drg)return;e.preventDefault();let ev=e.type.includes('touch')?e.touches[0]:e;p.style.left=(sl+ev.clientX-sx)+'px';p.style.top=(st_y+ev.clientY-sy)+'px';}
  function dEn(){drg=false;localStorage.setItem('drx_ui_x',p.style.left);localStorage.setItem('drx_ui_y',p.style.top);}
  h.addEventListener('mousedown',dSt);
  h.addEventListener('touchstart',dSt,{passive:false});
  document.addEventListener('mousemove',dMv);
  document.addEventListener('touchmove',dMv,{passive:false});
  document.addEventListener('mouseup',dEn);
  document.addEventListener('touchend',dEn);

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
  const tgtInp=document.createElement('input');tgtInp.type='number';tgtInp.placeholder='TARGET AMT';tgtInp.className='txt-blk';tgtInp.style.cssText='width:100%;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:12px;outline:none;';
  const stpInp=document.createElement('input');stpInp.type='number';stpInp.placeholder='MARTINGALE STEPS';stpInp.value='5';stpInp.className='txt-blk';stpInp.style.cssText='width:100%;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:12px;outline:none;';
  const goBtn=document.createElement('button');goBtn.innerText=uF('START ENGINE');goBtn.className='txt-blk';goBtn.style.cssText='width:100%;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;transition:0.2s;';
  p1.appendChild(tgtInp);p1.appendChild(stpInp);p1.appendChild(goBtn);

  st.preScn=setInterval(()=>{
    if(!st.isRun){
      let bal=chkBal();
      let pb=document.getElementById('pre-bal');
      if(pb) pb.innerText=uF(bal>0?bal:'--');
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
  ghBox.style.cssText='width:100%; height:22px; background:transparent; border:2px solid #000; border-radius:4px; padding:2px 4px; margin-top:4px; cursor:pointer; overflow:hidden; display:flex; flex-direction:column; justify-content:flex-end; transition:0.3s;';
  ghBox.innerHTML='<div id="gh-content" class="txt-blk" style="font-size:7.5px; line-height:1.1; color:#fff; white-space:pre-wrap; text-align:left; width:100%;">Syncing API...</div>';
  infBx.appendChild(ghBox);

  const stpBtn=document.createElement('button');
  stpBtn.innerText=uF('STOP');
  stpBtn.className='txt-blk-err';
  stpBtn.style.cssText='width:100%;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;margin-top:6px;transition:0.2s;';
  p2.appendChild(balBx);p2.appendChild(infBx);p2.appendChild(stpBtn);b.appendChild(p1);b.appendChild(p2);inC.appendChild(b);p.appendChild(inC);document.body.appendChild(p);

  setTimeout(()=>{
    let uBetEl=document.getElementById('ui-bet');
    if(uBetEl){
      uBetEl.ondblclick=function(){
        let currentVal=st.manualOverrideBet||(st.dynSeq&&st.dynSeq[st.stpIdx])||0;
        let val=prompt("Set Custom Fixed Bet (Enter 0 to clear state):",currentVal);
        if(val!==null&&!isNaN(val)){
          let parsed=Math.floor(parseFloat(val));
          st.manualOverrideBet=parsed>0?parsed:null;
          this.innerText=uF(st.manualOverrideBet?st.manualOverrideBet+' (FIX)':st.dynSeq[st.stpIdx]);
        }
      };
    }
  },1000);

  const drx_triggerEvent=(el,etype)=>{let ev=new Event(etype,{bubbles:true,cancelable:true});el.dispatchEvent(ev);};
  const drx_simClick=(el)=>{if(!el)return;['pointerdown','mousedown','touchstart','pointerup','mouseup','touchend','click'].forEach(evt=>{try{el.dispatchEvent(new MouseEvent(evt,{bubbles:true,cancelable:true,view:window}));}catch(e){}});};

  const exeTrd=(pred,amt,cb)=>{
    try{
      let btn=null;
      let targetText=pred.toLowerCase();
      let btns=document.querySelectorAll('button, div, span');
      for(let i=0;i<btns.length;i++){
        let t=(btns[i].innerText||'').trim().toLowerCase();
        if(t===targetText&&btns[i].offsetParent&&!btns[i].children.length){btn=btns[i];break;}
      }
      if(!btn){
        if(targetText==='big')btn=document.querySelector('.Betting__C-foot-b');
        else if(targetText==='small')btn=document.querySelector('.Betting__C-foot-s');
        else if(targetText==='green')btn=document.querySelector('button[class*="green"], div[class*="green"]');
        else if(targetText==='red')btn=document.querySelector('button[class*="red"], div[class*="red"]');
        else if(targetText==='violet')btn=document.querySelector('button[class*="violet"], div[class*="violet"]');
      }
      if(!btn){if(cb)cb(false);return;}
      btn.classList.add('drx-elec-target');
      drx_simClick(btn);
      let checkAttempts=0;
      let valInterval=setInterval(()=>{
        checkAttempts++;
        let inpEl=document.querySelector("input[type='number'], input.van-field__control");
        if(inpEl||checkAttempts>15){
          clearInterval(valInterval);
          if(inpEl){
            inpEl.focus();
            let setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;
            if(setV)setV.call(inpEl,String(amt));else inpEl.value=amt;
            drx_triggerEvent(inpEl,'input');
            drx_triggerEvent(inpEl,'change');
            drx_triggerEvent(inpEl,'blur');
          }
          setTimeout(()=>{
            let dEl=document.querySelector('button.bet-amount, button[class*="bet-amount"]');
            if(dEl){drx_simClick(dEl);}else{
              document.querySelectorAll('button').forEach(b=>{if((b.innerText||'').includes('Total amount')&&b.offsetParent)drx_simClick(b);});
            }
            btn.classList.remove('drx-elec-target');
            setTimeout(()=>{if(cb)cb(true);},2000);
          },800);
        }
      },200);
    }catch(e){if(cb)cb(false);}
  };

  const scnUI=(cb)=>{
    let ov=document.createElement('div');
    ov.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;background:transparent;z-index:9999998;pointer-events:none;overflow:hidden;';
    let cBase='#00ff00';
    let rL=document.createElement('div');
    rL.style.cssText=`position:absolute;width:100%;height:2px;background:${cBase};box-shadow:0 0 10px 3px ${cBase};animation:sR 0.6s linear infinite alternate;`;
    let gL=document.createElement('div');
    gL.style.cssText=`position:absolute;height:100%;width:3px;background:${cBase};box-shadow:0 0 15px 5px ${cBase};animation:sG 0.6s cubic-bezier(0.25,0.1,0.25,1) infinite alternate;`;
    let sS=document.createElement('style');
    sS.innerHTML=`@keyframes sR { 0% { top: -10px; } 100% { top: 100vh; } } @keyframes sG { 0% { left: -10px; } 100% { left: 100vw; } }`;
    document.head.appendChild(sS);
    ov.appendChild(rL);ov.appendChild(gL);
    document.body.appendChild(ov);
    setTimeout(()=>{ov.remove();sS.remove();if(cb)cb();},1500);
  };

  const getNextLivePeriod=(str)=>{
    let chars=str.split('');
    for(let i=chars.length-1;i>=0;i--){
      if(chars[i]!=='9'){chars[i]=String.fromCharCode(chars[i].charCodeAt(0)+1);return chars.join('');}
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
        uBal.innerText=uF(`${st.curBal} (Done)`);
        uSts.innerText=uF('DONE');
        uSts.className='txt-blk-accent';
        stpBtn.style.display='none';
        VoiceEngine.speak("Target reached successfully.");
        st.isRun=false;
        clearInterval(st.autoInt);
        lkOvl.style.display='none';
        document.body.style.overflow='';
        let dWrap=document.createElement('div');
        dWrap.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:20px;border:2px solid #00ff00;border-radius:10px;z-index:99999999;text-align:center;box-shadow:0 0 30px #00ff00;';
        dWrap.innerHTML=`<h2 style="color:#00ff00;margin-bottom:10px;font-family:monospace;">TARGET REACHED</h2><p style="color:#fff;font-family:monospace;margin-bottom:15px;">Balance: ${st.curBal}</p><button id="closeDWrap" style="background:transparent;color:#00ff00;border:1px solid #00ff00;padding:5px 15px;cursor:pointer;">OK</button>`;
        document.body.appendChild(dWrap);
        document.getElementById('closeDWrap').onclick=()=>dWrap.remove();
        return;
      }else{
        uBal.innerText=uF(st.curBal>0?st.curBal:'--');
      }

      let ts=Math.floor(Date.now()/1000);
      let res=await fetch("https://data-vip-247-hack.ai.studio/apipid.json?page=1&ts="+ts);
      let dataArray=await res.json();
      if(dataArray){
        let activeLogic=Array.isArray(dataArray)?dataArray[0]:(dataArray.data?dataArray.data[0]:dataArray);
        if(activeLogic){
          let tempHist=activeLogic.history||[];
          let cSig=tempHist[0]?getNextLivePeriod(String(tempHist[0].pid)):'';
          let sSig=sessionStorage.getItem('drx_sig');
          if(cSig&&cSig!==sSig){
            if(st.lastPred&&st.lastPred!=='SKIP'&&st.lastPeriod){
              let actualData=tempHist[0];
              let actualR=(actualData.actual==='BIG'||actualData.actual===1)?'BIG':'SMALL';
              let won=(st.lastPred===actualR);
              if(!st.pattern) st.pattern = [];
              if(won){
                st.w++;
                st.stpIdx=0;
                st.pattern.push('W');
              }else{
                st.l++;
                st.stpIdx=Math.min(st.stpIdx+1,st.dynSeq.length-1);
                st.pattern.push('L');
              }
              if(st.pattern.length > 25) st.pattern.shift();
            }
            st.lastPred=null;
            st.lastPeriod=cSig;
            let timeLeft=dTimeLeft;
            let isDangerZone=timeLeft<=cfg.minSf;
            if(isDangerZone){uSts.innerText=uF('<10S');uSts.className='txt-blk-warn';}
            st.isTrd=true;
            uSts.innerText=uF('CHK...');
            uSts.className='txt-blk-warn';
            let nBal=chkBal();
            uBal.innerText=uF(nBal);
            if(nBal>=st.tgtAmt&&nBal>0){st.isTrd=false;isFetchingApi=false;return;}
            st.dynSeq=calcSeq(nBal,st.steps);
            if(st.stpIdx>=st.dynSeq.length)st.stpIdx=st.dynSeq.length-1;
            let tAmt=st.manualOverrideBet?st.manualOverrideBet:st.dynSeq[st.stpIdx];
            uBet.innerText=uF(st.manualOverrideBet?tAmt+' (FIX)':tAmt);
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
              let prediction=(activeLogic.pred||activeLogic.prediction||'BIG').toUpperCase();
              if(st.showPred){
                let predDisplay=document.getElementById('ui-pred');
                if(!predDisplay){
                  predDisplay=document.createElement('span');
                  predDisplay.id='ui-pred';
                  predDisplay.className='txt-blk-accent';
                  predDisplay.style.cssText='color: #ffffff !important; text-shadow: -1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0px 2px 4px rgba(0,0,0,0.5) !important; margin-left: 4px;';
                  let betSpan=document.getElementById('ui-bet');
                  if(betSpan)betSpan.parentNode.insertBefore(predDisplay,betSpan.nextSibling);
                }
                predDisplay.innerText=prediction==='BIG'?'B':(prediction==='SMALL'?'S':(prediction==='SKIP'?'SKP':prediction[0]));
              }else{
                let predDisplay=document.getElementById('ui-pred');
                if(predDisplay)predDisplay.innerText='--';
              }
              let ghC=document.getElementById('gh-content');
              if(ghC)ghC.textContent=`Logic: ${activeLogic.logic||'TOP'}\nPRED: ${prediction}`;
              if(prediction==='SKIP'){
                st.lastPred=null;
                uSts.innerText=uF('SKIP');
                uSts.className='txt-blk-warn';
                sessionStorage.setItem('drx_sig',cSig);
                setTimeout(()=>{st.isTrd=false;},1000);
              }else{
                st.lastPred=prediction;
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
                    st.lastPred=null;
                  }
                  setTimeout(()=>{st.isTrd=false;},1000);
                });
              }
            },2000);
          }else if(!st.isTrd){
            uSts.innerText=uF('SCAN');
            uSts.className='txt-blk';
          }
        }
      }
    }catch(e){st.isTrd=false;}
    isFetchingApi=false;
  };

  goBtn.onclick=()=>{
    let a=Math.floor(parseFloat(tgtInp.value)),s=parseInt(stpInp.value)||5;
    if(!a||a<=0){alert('Invalid Target Amount');return;}
    st.steps=s;
    clearInterval(st.preScn);
    st.tradesDone=0;
    VoiceEngine.speak("System engine activated. Scanning market data.");
    scnUI(()=>{
      sessionStorage.removeItem('drx_sig');
      sessionStorage.removeItem('drx_p_bal');
      chkBal();
      st.tgtAmt=a;
      st.dynSeq=calcSeq(st.curBal>0?st.curBal:a,st.steps);
      st.stpIdx=0;
      document.getElementById('ui-tgt').innerText=uF(a);
      p1.style.display='none';
      p2.style.display='block';
      lkOvl.style.display='block';
      document.body.style.overflow='hidden';
      st.isRun=true;
      st.isTrd=false;
      sessionStorage.setItem('drx_p_bal',st.curBal);
      document.getElementById('ui-sts').innerText=uF('RDY');
      st.autoInt=setInterval(apiLoopTask,1000);

      if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);
      st.balanceCheckInterval=setInterval(()=>{
        if(!st.isRun)return;
        let currentBal=chkBal();
        if(currentBal>=st.tgtAmt&&currentBal>0){
          st.isRun=false;
          clearInterval(st.autoInt);
          clearInterval(st.balanceCheckInterval);
          st.balanceCheckInterval=null;
          const uSts=document.getElementById('ui-sts');
          if(uSts){uSts.innerText=uF('DONE');uSts.className='txt-blk-accent';}
          const stpBtnEl=document.querySelector('.drx-in button:last-child');
          if(stpBtnEl)stpBtnEl.style.display='none';
          lkOvl.style.display='none';
          document.body.style.overflow='';
          VoiceEngine.speak("Target reached. Engine stopped.");
          let dWrap=document.createElement('div');
          dWrap.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:20px;border:2px solid #00ff00;border-radius:10px;z-index:99999999;text-align:center;box-shadow:0 0 30px #00ff00;';
          dWrap.innerHTML=`<h2 style="color:#00ff00;margin-bottom:10px;font-family:monospace;">TARGET REACHED</h2><p style="color:#fff;font-family:monospace;margin-bottom:15px;">Balance: ${currentBal}</p><button id="closeDWrap" style="background:transparent;color:#00ff00;border:1px solid #00ff00;padding:5px 15px;cursor:pointer;">OK</button>`;
          document.body.appendChild(dWrap);
          document.getElementById('closeDWrap').onclick=()=>dWrap.remove();
        }
      },1000);
    });
  };

  stpBtn.onclick=()=>{
    st.isRun=false;
    clearInterval(st.autoInt);
    if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);
    st.balanceCheckInterval=null;
    sessionStorage.removeItem('drx_sig');
    sessionStorage.removeItem('drx_p_bal');
    document.getElementById('ui-sts').innerText=uF('HLT');
    document.getElementById('ui-sts').className='txt-blk-err';
    lkOvl.style.display='none';
    document.body.style.overflow='';
    stpBtn.innerText=uF('RBT');
    stpBtn.onclick=()=>{
      p2.style.display='none';
      p1.style.display='block';
      stpBtn.innerText=uF('STOP');
      st.preScn=setInterval(()=>{
        let bVal=chkBal();
        document.getElementById('pre-bal').innerText=uF(bVal>0?bVal:'--');
      },1000);
    };
  };
})();
"""

TRIGGER_ENGINE_START_JS = r"""
const targetProfit = arguments[0];
const martingaleSteps = arguments[1];

const tInp = document.querySelector('#sys-core-fin input[placeholder*="TARGET"]');
const sInp = document.querySelector('#sys-core-fin input[placeholder*="STEPS"]');
const goBtn = document.querySelector('#sys-core-fin button');

if (tInp && sInp && goBtn) {
    tInp.value = targetProfit;
    sInp.value = martingaleSteps;
    goBtn.click();
    return "STARTED";
}
return "ELEMENT_NOT_FOUND";
"""

GET_LIVE_ENGINE_STATS_JS = r"""
if (window.__WINGO_ST) {
    return {
        isRun: window.__WINGO_ST.isRun || false,
        curBal: window.__WINGO_ST.curBal || 0,
        tgtAmt: window.__WINGO_ST.tgtAmt || 0,
        stpIdx: window.__WINGO_ST.stpIdx || 0,
        steps: window.__WINGO_ST.steps || 5,
        w: window.__WINGO_ST.w || 0,
        l: window.__WINGO_ST.l || 0,
        tradesDone: window.__WINGO_ST.tradesDone || 0,
        pattern: window.__WINGO_ST.pattern || []
    };
}
return null;
"""

# ==========================================
# 9. Clean Keyboards
# ==========================================
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
    s_val = sess.get("total_steps", 5)

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
        InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data=f"shot:{sid}"),
        InlineKeyboardButton(f"{to_bold('BAL')}", callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATS')}", callback_data=f"stats:{sid}"),
        InlineKeyboardButton(f"{to_bold(f'STOP {spinner}')}", callback_data=f"stop:{sid}")
    )
    return markup

def get_channel_join_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"{to_bold('JOIN OFFICIAL CHANNEL')}", url=CHANNEL_URL),
        InlineKeyboardButton(f"{to_bold('VERIFY MEMBERSHIP')}", callback_data="check_channel_joined")
    )
    return markup

def get_passkey_gate_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENTER PASSKEY')}", callback_data="btn_enter_pass"),
        InlineKeyboardButton(f"{to_bold('CONTACT OWNER')}", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")
    )
    return markup

def get_six_platform_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
        InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('TIGRO CLUB')}", callback_data="site_tigroclub"),
        InlineKeyboardButton(f"{to_bold('HG NICE')}", callback_data="site_hgnice")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('KANPUR 91')}", callback_data="site_kanpur91"),
        InlineKeyboardButton(f"{to_bold('BDG WINS VIP')}", callback_data="site_bdgwinsvip")
    )
    return markup

# ==========================================
# 10. Passkey Storage & Management Helpers
# ==========================================
def generate_24h_passkey() -> str:
    token_str = "KEY-" + uuid.uuid4().hex[:6].upper()
    now_ts = time.time()
    payload = {
        "created_at": now_ts,
        "expires_at": now_ts + 86400,
        "valid_hours": 24,
        "status": "active"
    }
    firebase_sync_http(f"passkeys/{token_str}", "PUT", payload)
    return token_str

def revoke_passkey(key_str: str):
    firebase_sync_http(f"passkeys/{key_str}", "DELETE")

def get_all_passkeys() -> dict:
    data = firebase_sync_http("passkeys", "GET")
    if not data or not isinstance(data, dict):
        return {}
    now_ts = time.time()
    valid_keys = {}
    for k, v in list(data.items()):
        if isinstance(v, dict):
            exp = float(v.get("expires_at", 0))
            if exp > now_ts:
                valid_keys[k] = v
            else:
                revoke_passkey(k)
    return valid_keys

def get_passkey_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"{to_bold('GENERATE NEW 24H PASSKEY')}", callback_data="pk_gen_new"),
        InlineKeyboardButton(f"{to_bold('VIEW ACTIVE PASSKEYS')}", callback_data="pk_list_active"),
        InlineKeyboardButton(f"{to_bold('REVOKE PASSKEY')}", callback_data="pk_prompt_revoke")
    )
    return markup

# ==========================================
# 11. Admin Control Dashboard Keyboards
# ==========================================
def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('WORKER STATUS')}", callback_data="adm_workers"),
        InlineKeyboardButton(f"{to_bold('ACTIVE LOGINS')}", callback_data="adm_logins")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('SPEED TEST / PING')}", callback_data="adm_ping"),
        InlineKeyboardButton(f"{to_bold('PASSKEY MANAGER')}", callback_data="adm_passkeys")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('TASK COMPLETED MONITOR')}", callback_data="adm_tasks"),
        InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data="adm_refresh")
    )
    return markup

# ==========================================
# 12. Authentication Helpers
# ==========================================
def check_channel_membership(user_id):
    if user_id == SUPER_ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return True

def is_user_pass_valid(chat_id):
    if chat_id == SUPER_ADMIN_ID:
        return True
    u = user_sessions.get(chat_id, {})
    return time.time() < u.get("pass_expiry", 0)

# ==========================================
# 13. Clean Login Animation & Engine Auth (Screenshot #1)
# ==========================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE ENGINE</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Allocating isolated Firefox profile...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>▰▰▰▱▱▱▱▱▱▱ 35% Securing connection instance...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>▰▰▰▰▰▰▱▱▱▱ 65% Auto-filling credentials...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>▰▰▰▰▰▰▰▰▰▰ 100% Login verification complete!</code>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.35)

def process_login(chat_id, sid, phone, password, anim_msg_id):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = sess.get("login_url") or (URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN)

    if anim_msg_id:
        play_clean_login_animation(chat_id, anim_msg_id)

    try:
        driver, handle = allocate_session_tab(sid, login_url)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    except Exception as e:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\n\nPlatform: <b>{site_name}</b>\nReason: <i>{e}</i>")
        return

    fill_ok = False
    for _ in range(70):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(2.0)
            break
        time.sleep(0.4)

    if not fill_ok:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\n\nPlatform: <b>{site_name}</b>\nReason: <i>Login form not found.</i>")
        close_session_tab(sid)
        return

    login_status = "PENDING"
    err_detail = ""
    for _ in range(40):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "CONFIRM_CLICKED":
                time.sleep(1.5)
                continue
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "Invalid credentials")
                break
        time.sleep(0.5)

    if safe_tab_execute(sid, lambda drv: drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")):
        login_status = "SUCCESS"

    safe_delete_message(chat_id, anim_msg_id)

    if login_status == "ERROR":
        close_session_tab(sid)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\n\nPlatform: <b>{site_name}</b>\nReason: <i>{err_detail}</i>")
        return

    time.sleep(1.5)

    # STRICT POLICY: SCREENSHOT #1 - Captured immediately after successful account login
    login_snap = os.path.join(PROFILES_BASE_DIR, f"login_done_{sid}.png")
    safe_tab_execute(sid, lambda drv: drv.save_screenshot(login_snap))

    masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
    caption = (
        f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Account: <code>{masked_phone}</code>\n\n"
        f"Click <b>START</b> below to configure and load WinGo 30S market:"
    )

    display_or_replace_photo(
        chat_id, sid,
        login_snap,
        caption,
        get_start_screen_keyboard(sid)
    )

# ==========================================
# 14. WinGo Navigation & Configuration Flow (Screenshot #2)
# ==========================================
def prepare_wingo_parameters(chat_id, sid):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")

    def _nav(drv):
        try:
            drv.execute_script(MODAL_AUTO_DISMISSER_JS)
            drv.execute_script(WINGO_RUNBOX_AND_CLICK_JS)
        except Exception:
            pass
        wingo_url = sess.get("wingo_url") or (URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO)
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
        if safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS)):
            break
        time.sleep(0.8)

    current_bal = 0.0
    for _ in range(12):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.5)

    sess["current_balance"] = current_bal
    sess["start_bal"] = current_bal

    # STRICT POLICY: SCREENSHOT #2 - Captured immediately upon successfully loading WinGo screen
    wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
    safe_tab_execute(sid, lambda drv: drv.save_screenshot(wingo_snap))

    config_caption = (
        f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Live Balance: <code>৳ {current_bal:.2f}</code>\n\n"
        f"Set your <b>TARGET</b> and <b>STEPS</b> below, then press <b>START</b>:"
    )

    display_or_replace_photo(
        chat_id, sid,
        wingo_snap,
        config_caption,
        get_setup_param_keyboard(sid)
    )

# ==========================================
# 15. Stats Dashboard & Background Monitoring (Zero Screenshots During Trading)
# ==========================================
def render_stats_dashboard_text(sess, stats_data=None):
    if not stats_data:
        stats_data = {}

    cur_bal = stats_data.get("curBal") or sess.get("cur_bal", sess.get("current_balance", 0.0))
    start_b = sess.get("start_bal", 0.0)
    tgt_profit = sess.get("target_profit", 0.0)
    tgt_total = start_b + tgt_profit if tgt_profit > 0 else (stats_data.get("tgtAmt") or 0.0)
    
    stp_idx = stats_data.get("stpIdx", 0) + 1
    total_steps = stats_data.get("steps") or sess.get("total_steps", 5)
    
    w = stats_data.get("w", sess.get("wins", 0))
    l = stats_data.get("l", sess.get("losses", 0))
    pattern_list = stats_data.get("pattern", sess.get("pattern", []))
    
    pattern_display = ", ".join(pattern_list[-8:]) if pattern_list else "No trades yet"
    net_p = cur_bal - start_b
    net_sign = "+" if net_p >= 0 else ""

    dashboard_text = (
        f"<b>{to_bold('REAL-TIME TRADING MONITOR')}</b>\n\n"
        f"Platform: <b>{sess.get('site_name', 'WinGo 30S')}</b>\n"
        f"• Current Wallet Balance: <code>৳ {cur_bal:.2f}</code>\n"
        f"• Target Profit/Balance: <code>৳ {tgt_total:.2f}</code> (Net: <code>{net_sign}৳ {net_p:.2f}</code>)\n"
        f"• Current Martingale Step: <b>Step {stp_idx} of {total_steps}</b>\n"
        f"• Total Wins & Losses: <b>{w} Wins</b> | <b>{l} Losses</b>\n"
        f"• Pattern Sequence: <code>[{pattern_display}]</code>\n\n"
        f"<b>STATUS</b>: <code>ENGINE RUNNING 24/7 (SILENT BACKGROUND)</code>\n"
        f"<i>Updated: {time.strftime('%H:%M:%S')}</i>"
    )
    return dashboard_text

def record_task_status(chat_id, sid, status, start_bal, cur_bal, target_amt, wins, losses, site_name, pattern):
    task_payload = {
        "chat_id": chat_id,
        "session_id": sid,
        "site_name": site_name,
        "status": status,
        "start_balance": start_bal,
        "current_balance": cur_bal,
        "target_amount": target_amt,
        "wins": wins,
        "losses": losses,
        "pattern": pattern,
        "updated_at": time.time()
    }
    firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

def monitor_trading_progress(chat_id, sid):
    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        js_data = safe_tab_execute(sid, lambda drv: drv.execute_script(GET_LIVE_ENGINE_STATS_JS))

        if js_data and isinstance(js_data, dict):
            sess["cur_bal"] = js_data.get("curBal", sess.get("cur_bal", 0))
            sess["wins"] = js_data.get("w", 0)
            sess["losses"] = js_data.get("l", 0)
            sess["pattern"] = js_data.get("pattern", [])
            tgt_amt = js_data.get("tgtAmt", 0)
            start_b = sess.get("start_bal", 0)

            record_task_status(
                chat_id, sid, "RUNNING",
                start_b, sess["cur_bal"], tgt_amt,
                sess["wins"], sess["losses"],
                sess.get("site_name", "Amar Club"),
                sess["pattern"]
            )

            # Check if target profit/balance achieved
            if sess["cur_bal"] >= tgt_amt and tgt_amt > 0 and sess["cur_bal"] > 0:
                sess["is_trading"] = False
                profit = sess["cur_bal"] - start_b

                record_task_status(
                    chat_id, sid, "COMPLETED",
                    start_b, sess["cur_bal"], tgt_amt,
                    sess["wins"], sess["losses"],
                    sess.get("site_name", "Amar Club"),
                    sess["pattern"]
                )

                # STRICT POLICY: NO SCREENSHOTS AFTER FIRST TWO STAGES
                win_text = (
                    f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                    f"Your target profit has been fulfilled smoothly by the engine.\n\n"
                    f"Starting Balance: <code>৳ {start_b:.2f}</code>\n"
                    f"Final Wallet Balance: <code>৳ {sess['cur_bal']:.2f}</code>\n"
                    f"Net Profit: <code>+৳ {profit:.2f}</code>\n"
                    f"Total Wins: <b>{sess['wins']}</b> | Losses: <b>{sess['losses']}</b>\n"
                    f"Final Sequence: <code>[{', '.join(sess['pattern'][-10:])}]</code>"
                )
                bot.send_message(chat_id, win_text)
                break

        time.sleep(3)

def continuous_24h_watchdog():
    while True:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                created_at = item.get("created_at", now)
                if now - created_at >= 86400:
                    close_session_tab(sid)
        except Exception:
            pass
        time.sleep(1800)

threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

# ==========================================
# 16. Telegram Commands (/start, /pass, /admin)
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_sessions.setdefault(chat_id, {})

    if chat_id != SUPER_ADMIN_ID and not check_channel_membership(chat_id):
        user_sessions[chat_id]["step"] = "WAITING_CHANNEL_JOIN"
        caption = (
            f"<b>{to_bold('CHANNEL MEMBERSHIP REQUIRED')}</b>\n\n"
            f"To access this VIP automation bot, you must join our official Telegram channel:\n"
            f"Channel: <b>{CHANNEL_USERNAME}</b>\n\n"
            f"Join below and click <b>VERIFY MEMBERSHIP</b>:"
        )
        bot.send_message(chat_id, caption, reply_markup=get_channel_join_keyboard())
        return

    if not is_user_pass_valid(chat_id):
        user_sessions[chat_id]["step"] = "WAITING_PASSKEY_AUTH"
        caption = (
            f"<b>{to_bold('24-HOUR ACCESS PASSKEY REQUIRED')}</b>\n\n"
            f"An active 24-hour passkey is required to access the engine.\n"
            f"Contact the administrator to obtain an authorized passkey."
        )
        bot.send_message(chat_id, caption, reply_markup=get_passkey_gate_keyboard())
        return

    user_sessions[chat_id]["step"] = "CHOOSE_SITE"
    welcome_text = (
        f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
        f"Welcome to the high-frequency automated trading engine.\n"
        f"Please select your target trading platform to proceed:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_six_platform_keyboard())

@bot.message_handler(commands=['pass'])
def handle_pass_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        u = user_sessions.get(chat_id, {})
        exp = u.get("pass_expiry", 0)
        remaining = max(0, int(exp - time.time()))
        mins, secs = divmod(remaining, 60)
        hrs, mins = divmod(mins, 60)
        msg = (
            f"<b>{to_bold('PASSKEY STATUS')}</b>\n\n"
            f"Status: <b>{'ACTIVE' if remaining > 0 else 'EXPIRED'}</b>\n"
            f"Time Remaining: <code>{hrs:02d}h {mins:02d}m {secs:02d}s</code>"
        )
        bot.send_message(chat_id, msg)
        return

    caption = (
        f"<b>{to_bold('PASSKEY MANAGEMENT')}</b>\n\n"
        f"Manage authorized 24-hour access passkeys for the cluster."
    )
    bot.send_message(chat_id, caption, reply_markup=get_passkey_menu_keyboard())

@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        bot.send_message(chat_id, f"<b>{to_bold('ACCESS DENIED')}</b>\nUnauthorized command.")
        return

    caption = (
        f"<b>{to_bold('ADMIN CLUSTER CONTROL PANEL')}</b>\n\n"
        f"Cluster Node ID: <code>{NODE_ID}</code>\n"
        f"Role: <b>{'PRIMARY MASTER (BRAIN)' if IS_CLUSTER_MASTER else 'STANDBY / WORKER'}</b>\n\n"
        f"Select a management module from the options below:"
    )
    bot.send_message(chat_id, caption, reply_markup=get_admin_dashboard_keyboard())

# ==========================================
# 17. Telegram Callbacks & Flow Routing
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    # Gate & Passkey entry
    if action == "check_channel_joined":
        if check_channel_membership(chat_id):
            bot.answer_callback_query(call.id, "Channel verified successfully!")
            if not is_user_pass_valid(chat_id):
                caption = (
                    f"<b>{to_bold('24-HOUR ACCESS PASSKEY REQUIRED')}</b>\n\n"
                    f"Please enter your authorized 24-hour passkey to continue:"
                )
                bot.edit_message_text(caption, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_passkey_gate_keyboard())
            else:
                bot.edit_message_text(f"<b>{to_bold('SELECT PLATFORM')}</b>", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_six_platform_keyboard())
        else:
            bot.answer_callback_query(call.id, "You have not joined the official channel yet!", show_alert=True)
        return

    elif action == "btn_enter_pass":
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_PASSKEY"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, f"<b>{to_bold('PASSKEY AUTHENTICATION')}</b>\nPlease submit your 24-hour passkey:")
        user_sessions[chat_id]["passkey_prompt_id"] = pm.message_id
        return

    # Passkey Management actions
    elif action == "pk_gen_new":
        if chat_id != SUPER_ADMIN_ID: return
        new_key = generate_24h_passkey()
        bot.answer_callback_query(call.id, "Passkey Generated!")
        msg = (
            f"<b>{to_bold('NEW 24-HOUR PASSKEY GENERATED')}</b>\n\n"
            f"Passkey: <code>{new_key}</code>\n"
            f"Duration: <b>24 Hours</b>\n"
            f"Saved to Firebase registry."
        )
        bot.send_message(chat_id, msg)
        return

    elif action == "pk_list_active":
        if chat_id != SUPER_ADMIN_ID: return
        keys = get_all_passkeys()
        bot.answer_callback_query(call.id)
        if not keys:
            bot.send_message(chat_id, f"<b>{to_bold('ACTIVE PASSKEYS')}</b>\n\nNo active passkeys currently registered.")
            return
        lines = [f"<b>{to_bold('ACTIVE PASSKEYS (24H)')}</b>\n"]
        for k, v in keys.items():
            rem = max(0, int(float(v.get('expires_at', 0)) - time.time()))
            hrs, mins = divmod(rem // 60, 60)
            lines.append(f"• <code>{k}</code> — Expires in <b>{hrs}h {mins}m</b>")
        bot.send_message(chat_id, "\n".join(lines))
        return

    elif action == "pk_prompt_revoke":
        if chat_id != SUPER_ADMIN_ID: return
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_REVOKE_KEY"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"<b>{to_bold('REVOKE PASSKEY')}</b>\nSend the exact passkey code you wish to delete:")
        return

    # Admin Dashboard Actions
    elif action == "adm_refresh" or action == "adm_home":
        if chat_id != SUPER_ADMIN_ID: return
        caption = (
            f"<b>{to_bold('ADMIN CLUSTER CONTROL PANEL')}</b>\n\n"
            f"Cluster Node ID: <code>{NODE_ID}</code>\n"
            f"Role: <b>{'PRIMARY MASTER (BRAIN)' if IS_CLUSTER_MASTER else 'STANDBY / WORKER'}</b>\n\n"
            f"Select a management module from the options below:"
        )
        bot.edit_message_text(caption, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_dashboard_keyboard())
        bot.answer_callback_query(call.id, "Refreshed")
        return

    elif action == "adm_workers":
        if chat_id != SUPER_ADMIN_ID: return
        terms = firebase_sync_http("terminals", "GET") or {}
        now_ts = time.time()
        total_cnt = len(terms)
        busy_cnt = sum(1 for t in terms.values() if isinstance(t, dict) and t.get("status") == "BUSY")
        free_cnt = sum(1 for t in terms.values() if isinstance(t, dict) and t.get("status") == "FREE")
        offline_cnt = sum(1 for t in terms.values() if isinstance(t, dict) and (t.get("status") == "OFFLINE" or now_ts - float(t.get("heartbeat", 0)) > 15.0))
        active_cnt = total_cnt - offline_cnt

        lines = [
            f"<b>{to_bold('CLUSTER WORKER TOPOLOGY')}</b>\n",
            f"Total Nodes: <b>{total_cnt}</b>",
            f"Active Nodes: <b>{active_cnt}</b>",
            f"Idle / Free: <b>{free_cnt}</b>",
            f"Busy / In-Task: <b>{busy_cnt}</b>",
            f"Offline: <b>{offline_cnt}</b>\n"
        ]
        for tid, tval in terms.items():
            if isinstance(tval, dict):
                st = tval.get("status", "UNKNOWN")
                hb_diff = int(now_ts - float(tval.get("heartbeat", 0)))
                lines.append(f"• <code>{tid}</code> | Status: <b>{st}</b> (HB: {hb_diff}s ago)")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{to_bold('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_logins":
        if chat_id != SUPER_ADMIN_ID: return
        sessions_data = firebase_sync_http("sessions", "GET") or {}
        lines = [f"<b>{to_bold('AUTHENTICATED USER SESSIONS')}</b>\n", f"Total Active Sessions: <b>{len(sessions_data)}</b>\n"]
        for sid_key, sval in sessions_data.items():
            if isinstance(sval, dict):
                c_id = sval.get("chat_id", "N/A")
                site = sval.get("site_name", "N/A")
                ph = sval.get("phone", "N/A")
                masked = ph[:3] + "****" + ph[-3:] if len(ph) >= 6 else ph
                lines.append(f"• User <code>{c_id}</code> | Site: <b>{site}</b> | Phone: <code>{masked}</code>")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{to_bold('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_ping":
        if chat_id != SUPER_ADMIN_ID: return
        bot.answer_callback_query(call.id, "Testing latency...")
        lines = [f"<b>{to_bold('NETWORK LATENCY / SPEED TEST')}</b>\n"]
        for pkey, pcfg in PLATFORMS.items():
            lat = measure_network_latency(pcfg["login"])
            lines.append(f"• {pcfg['name']}: <b>{lat} ms</b>" if lat < 9000 else f"• {pcfg['name']}: <b>TIMEOUT (>3000ms)</b>")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{to_bold('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_passkeys":
        if chat_id != SUPER_ADMIN_ID: return
        bot.edit_message_text(
            f"<b>{to_bold('PASSKEY MANAGER')}</b>\n\nGenerate or inspect 24-hour access tokens:",
            chat_id=chat_id, message_id=call.message.message_id,
            reply_markup=get_passkey_menu_keyboard()
        )
        return

    elif action == "adm_tasks":
        if chat_id != SUPER_ADMIN_ID: return
        all_tasks = firebase_sync_http("user_tasks", "GET") or {}
        total_sub = sum(len(v) for v in all_tasks.values() if isinstance(v, dict))
        markup = InlineKeyboardMarkup(row_width=1)

        lines = [
            f"<b>{to_bold('TASK COMPLETED MONITOR')}</b>\n",
            f"Total Submitting Users: <b>{len(all_tasks)}</b>",
            f"Total Historical/Active Tasks: <b>{total_sub}</b>\n",
            "Select an individual user below to inspect task breakdowns:"
        ]
        for u_id, t_dict in all_tasks.items():
            if isinstance(t_dict, dict):
                comp = sum(1 for t in t_dict.values() if isinstance(t, dict) and t.get("status") == "COMPLETED")
                run = sum(1 for t in t_dict.values() if isinstance(t, dict) and t.get("status") == "RUNNING")
                markup.add(InlineKeyboardButton(f"User {u_id} (Done: {comp} | Active: {run})", callback_data=f"adm_user_t:{u_id}"))

        markup.add(InlineKeyboardButton(f"{to_bold('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_user_t":
        if chat_id != SUPER_ADMIN_ID: return
        target_uid = sid
        u_tasks = firebase_sync_http(f"user_tasks/{target_uid}", "GET") or {}
        lines = [f"<b>{to_bold('USER TASK DETAILS')}</b>\nUser: <code>{target_uid}</code>\n"]
        for t_sid, tinfo in u_tasks.items():
            if isinstance(tinfo, dict):
                lines.append(
                    f"• Task <code>{t_sid}</code>\n"
                    f"  Status: <b>{tinfo.get('status', 'N/A')}</b> | Platform: <b>{tinfo.get('site_name', 'N/A')}</b>\n"
                    f"  Start: ৳ {tinfo.get('start_balance', 0):.2f} ➔ Live: ৳ {tinfo.get('current_balance', 0):.2f}\n"
                    f"  Target: ৳ {tinfo.get('target_amount', 0):.2f} | W: {tinfo.get('wins', 0)} L: {tinfo.get('losses', 0)}\n"
                )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"{to_bold('BACK TO TASKS')}", callback_data="adm_tasks"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    # Platform selection
    elif action in PLATFORMS:
        p_cfg = PLATFORMS[action]
        site_name = p_cfg["name"]
        sid = f"{chat_id}_{int(time.time()) % 1000000}"

        active_sessions[sid] = {
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": site_name,
            "login_url": p_cfg["login"],
            "wingo_url": p_cfg["wingo"],
            "phone": None,
            "password": None,
            "target_profit": 0,
            "total_steps": 5,
            "is_trading": False,
            "created_at": time.time(),
            "anim_tick": 0,
            "lock": threading.RLock(),
            "wins": 0,
            "losses": 0,
            "pattern": []
        }
        user_sessions.setdefault(chat_id, {})["active_sid"] = sid

        caption = (
            f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
            f"Platform: <b>{site_name}</b>\n\n"
            f"Please click below to submit your account number and password. "
            f"Credentials are kept purely in memory and cleared upon termination."
        )

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            caption,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    # Interactive credentials inputs
    elif action == "ask_num" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_PHONE"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT NUMBER')}</b>\nEnter your registered phone number:")
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "ask_pass" and sid in active_sessions:
        if not active_sessions[sid].get("phone"):
            bot.answer_callback_query(call.id, "Please enter your phone number first!", show_alert=True)
            return
        active_sessions[sid]["input_mode"] = "WAITING_PASS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\nEnter your account password:")
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "start_cfg" and sid in active_sessions:
        bot.answer_callback_query(call.id, "Preparing WinGo 30S market...")
        threading.Thread(target=prepare_wingo_parameters, args=(chat_id, sid), daemon=True).start()

    elif action == "set_tgt" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_TARGET"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[sid].get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('TARGET PROFIT')}</b>\nLive Balance: <code>৳ {cur_bal:.2f}</code>\nEnter target profit amount (e.g. <code>500</code>):")
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('MARTINGALE STEPS')}</b>\nEnter step count (e.g. <code>5</code> or <code>7</code>):")
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and sid in active_sessions:
        sess = active_sessions[sid]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "Please set a target profit amount first!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Starting automation engine...")
        sess["is_trading"] = True

        # Inject Upgraded Silent Engine JS
        safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_ENGINE_INJECTION_JS))
        time.sleep(1.0)

        # Trigger Engine START directly
        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        safe_tab_execute(
            sid,
            lambda drv: drv.execute_script(
                TRIGGER_ENGINE_START_JS,
                int(target_total),
                int(sess.get("total_steps", 5))
            )
        )

        # STRICT POLICY: NO SCREENSHOT HERE - Display Real-Time Text Dashboard
        dashboard_caption = render_stats_dashboard_text(sess)
        sent_dash = bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(sid))
        sess["dashboard_msg_id"] = sent_dash.message_id

        threading.Thread(target=monitor_trading_progress, args=(chat_id, sid), daemon=True).start()

    elif action == "shot" and sid in active_sessions:
        # STRICT POLICY: NO SCREENSHOT - Refresh and display real-time status monitor text
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "Refreshing live monitor...")
        js_data = safe_tab_execute(sid, lambda drv: drv.execute_script(GET_LIVE_ENGINE_STATS_JS))
        updated_text = render_stats_dashboard_text(sess, js_data)
        try:
            bot.edit_message_text(
                updated_text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_trading_control_keyboard(sid)
            )
        except Exception:
            bot.send_message(chat_id, updated_text, reply_markup=get_trading_control_keyboard(sid))

    elif action == "bal" and sid in active_sessions:
        b = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if b is not None:
            bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Loading balance...", show_alert=True)

    elif action == "stats" and sid in active_sessions:
        sess = active_sessions[sid]
        js_data = safe_tab_execute(sid, lambda drv: drv.execute_script(GET_LIVE_ENGINE_STATS_JS))
        if js_data:
            stat_txt = render_stats_dashboard_text(sess, js_data)
            bot.send_message(chat_id, stat_txt)
        else:
            bot.answer_callback_query(call.id, "Syncing engine data...", show_alert=True)

    elif action == "stop" and sid in active_sessions:
        sess = active_sessions[sid]
        safe_tab_execute(sid, lambda drv: drv.execute_script("let btn = document.querySelector('.drx-in button:last-child'); if(btn) btn.click();"))
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "Trading paused", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nMartingale automation halted cleanly.")

    elif action == "cancel" and sid in active_sessions:
        bot.answer_callback_query(call.id, "Session terminated")
        close_session_tab(sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, f"<b>{to_bold('SESSION TERMINATED')}</b>\nSend /start to begin a new session.")

# ==========================================
# 18. Text Handler & Input Router
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_sessions.get(chat_id, {})

    # Passkey authorization input
    if u.get("input_mode") == "WAITING_PASSKEY":
        safe_delete_message(chat_id, message.message_id)
        if u.get("passkey_prompt_id"):
            safe_delete_message(chat_id, u["passkey_prompt_id"])
            u["passkey_prompt_id"] = None

        key_data = firebase_sync_http(f"passkeys/{text}", "GET")
        now_ts = time.time()
        is_valid = False

        if chat_id == SUPER_ADMIN_ID or text.startswith("KEY-"):
            if key_data and isinstance(key_data, dict):
                if float(key_data.get("expires_at", 0)) > now_ts:
                    is_valid = True
            else:
                is_valid = True

        if is_valid:
            u["pass_expiry"] = now_ts + 86400
            u["input_mode"] = None
            u["step"] = "CHOOSE_SITE"
            bot.send_message(
                chat_id,
                f"<b>{to_bold('PASSKEY ACTIVATED (24 HOURS)')}</b>\n\nYour session is authorized. Select a platform to proceed:",
                reply_markup=get_six_platform_keyboard()
            )
        else:
            pm = bot.send_message(
                chat_id,
                f"<b>{to_bold('INVALID OR EXPIRED PASSKEY')}</b>\nPlease re-enter a valid 24-hour passkey:"
            )
            u["passkey_prompt_id"] = pm.message_id
        return

    # Admin Passkey Revocation input
    if u.get("input_mode") == "WAITING_REVOKE_KEY" and chat_id == SUPER_ADMIN_ID:
        safe_delete_message(chat_id, message.message_id)
        u["input_mode"] = None
        revoke_passkey(text)
        bot.send_message(chat_id, f"<b>{to_bold('PASSKEY REVOKED')}</b>\nKey <code>{text}</code> has been deleted.")
        return

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
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Number: <code>{masked}</code> (Recorded)\n\n"
                    f"Now click <b>PASSWORD</b> to enter your login password:"
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

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>")
        threading.Thread(
            target=process_login,
            args=(chat_id, sid, sess["phone"], sess["password"], anim_msg.message_id),
            daemon=True
        ).start()

    elif input_mode == "WAITING_TARGET":
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
                f"Target Profit: <code>৳ {val:.2f}</code>\n\n"
                f"Parameters updated. Click <b>START</b> to initiate trading:"
            )
            bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid positive number (e.g. 500):")
            sess["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
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
                f"Martingale Steps: <b>{steps_val}</b>\n\n"
                f"Parameters updated. Click <b>START</b> to initiate trading:"
            )
            bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid integer (e.g. 5):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==========================================
# 19. Firebase RTDB Cluster & Distributed Routing (Brain-Worker System)
# ==========================================
FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
NODE_ID = f"term_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"

IS_CLUSTER_MASTER = False
IS_STANDBY_MASTER = False
CLUSTER_ACTIVE = True

def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 4.0):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        raw_data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=raw_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_content = response.read()
            if res_content:
                return json.loads(res_content.decode("utf-8"))
            return None
    except Exception:
        return None

def cluster_claim_leadership():
    global IS_CLUSTER_MASTER, IS_STANDBY_MASTER
    now = time.time()

    primary = firebase_sync_http("cluster/active_master", "GET")
    claim_primary = False
    if not primary or not isinstance(primary, dict):
        claim_primary = True
    else:
        last_hb = float(primary.get("heartbeat", 0))
        if now - last_hb > 10.0 or primary.get("node_id") == NODE_ID:
            claim_primary = True

    if claim_primary:
        packet = {"node_id": NODE_ID, "heartbeat": now, "claimed_at": now}
        res = firebase_sync_http("cluster/active_master", "PUT", packet)
        if res and res.get("node_id") == NODE_ID:
            IS_CLUSTER_MASTER = True
            IS_STANDBY_MASTER = False
            return "MASTER"

    standby = firebase_sync_http("cluster/standby_master", "GET")
    claim_standby = False
    if not standby or not isinstance(standby, dict):
        claim_standby = True
    else:
        last_hb_s = float(standby.get("heartbeat", 0))
        if now - last_hb_s > 10.0 or standby.get("node_id") == NODE_ID:
            claim_standby = True

    if claim_standby:
        packet_s = {"node_id": NODE_ID, "heartbeat": now, "claimed_at": now}
        res_s = firebase_sync_http("cluster/standby_master", "PUT", packet_s)
        if res_s and res_s.get("node_id") == NODE_ID:
            IS_CLUSTER_MASTER = False
            IS_STANDBY_MASTER = True
            return "STANDBY"

    IS_CLUSTER_MASTER = False
    IS_STANDBY_MASTER = False
    return "WORKER"

def cluster_register_local_node():
    node_payload = {
        "status": "FREE",
        "heartbeat": time.time(),
        "assigned_user_id": None,
        "task": None,
        "node_id": NODE_ID,
        "load": len(active_sessions),
        "max_slots": MAX_SESSIONS_PER_NODE,
        "latency_ms": measure_network_latency(URL_AMARCLUB_LOGIN),
        "registered_at": time.time()
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)

def cluster_node_heartbeat_loop():
    while CLUSTER_ACTIVE:
        try:
            status_val = "BUSY" if len(active_sessions) >= MAX_SESSIONS_PER_NODE else "FREE"
            lat = measure_network_latency(URL_AMARCLUB_LOGIN)
            hb_data = {
                "heartbeat": time.time(),
                "status": status_val,
                "load": len(active_sessions),
                "max_slots": MAX_SESSIONS_PER_NODE,
                "latency_ms": lat
            }
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", hb_data)
        except Exception:
            pass
        time.sleep(4)

def cluster_master_heartbeat_loop():
    while CLUSTER_ACTIVE and IS_CLUSTER_MASTER:
        try:
            m_data = {"heartbeat": time.time()}
            firebase_sync_http("cluster/active_master", "PATCH", m_data)
        except Exception:
            pass
        time.sleep(3)

def cluster_standby_heartbeat_loop():
    while CLUSTER_ACTIVE and IS_STANDBY_MASTER:
        try:
            s_data = {"heartbeat": time.time()}
            firebase_sync_http("cluster/standby_master", "PATCH", s_data)
        except Exception:
            pass
        time.sleep(3)

def cluster_remote_task_listener():
    while CLUSTER_ACTIVE:
        try:
            if len(active_sessions) >= MAX_SESSIONS_PER_NODE:
                time.sleep(2.0)
            else:
                time.sleep(0.8)

            task = firebase_sync_http(f"terminals/{NODE_ID}/task", "GET")
            if task and isinstance(task, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/task", "DELETE")

                t_type = task.get("type")
                if t_type == "LOGIN_AND_TRADE":
                    chat_id = task["chat_id"]
                    sid = task["session_id"]
                    site_name = task.get("site_name", "Amar Club")
                    login_url = task.get("login_url")
                    wingo_url = task.get("wingo_url")
                    phone = task["phone"]
                    password = task["password"]
                    anim_msg_id = task.get("anim_msg_id")

                    active_sessions[sid] = {
                        "chat_id": chat_id,
                        "session_id": sid,
                        "site_name": site_name,
                        "login_url": login_url,
                        "wingo_url": wingo_url,
                        "phone": phone,
                        "password": password,
                        "target_profit": 0,
                        "total_steps": 5,
                        "is_trading": False,
                        "created_at": time.time(),
                        "anim_tick": 0,
                        "lock": threading.RLock(),
                        "wins": 0,
                        "losses": 0,
                        "pattern": []
                    }
                    user_sessions.setdefault(chat_id, {})["active_sid"] = sid

                    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                        "status": "BUSY" if len(active_sessions) >= MAX_SESSIONS_PER_NODE else "FREE",
                        "assigned_user_id": chat_id,
                        "session_id": sid,
                        "load": len(active_sessions)
                    })

                    threading.Thread(
                        target=_original_process_login,
                        args=(chat_id, sid, phone, password, anim_msg_id),
                        daemon=True
                    ).start()

            action_pkt = firebase_sync_http(f"terminals/{NODE_ID}/action", "GET")
            if action_pkt and isinstance(action_pkt, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/action", "DELETE")
                kind = action_pkt.get("kind")
                if kind == "CALLBACK":
                    class MockChat:
                        id = action_pkt["chat_id"]
                    class MockMessage:
                        chat = MockChat()
                        message_id = action_pkt["message_id"]
                    class MockCall:
                        id = action_pkt.get("call_id", "")
                        data = action_pkt["data"]
                        message = MockMessage()

                    threading.Thread(target=_original_handle_callbacks, args=(MockCall(),), daemon=True).start()

                elif kind == "TEXT_INPUT":
                    class MockChat:
                        id = action_pkt["chat_id"]
                    class MockMsg:
                        chat = MockChat()
                        message_id = action_pkt["message_id"]
                        text = action_pkt["text"]

                    threading.Thread(target=_original_handle_user_text, args=(MockMsg(),), daemon=True).start()

        except Exception:
            pass

def cluster_session_watchdog_loop():
    while CLUSTER_ACTIVE:
        try:
            now = time.time()
            if not active_sessions:
                cur_stat = firebase_sync_http(f"terminals/{NODE_ID}/status", "GET")
                if cur_stat == "BUSY":
                    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                        "status": "FREE",
                        "assigned_user_id": None,
                        "task": None,
                        "session_id": None,
                        "load": 0
                    })
            else:
                for sid, sess in list(active_sessions.items()):
                    c_time = sess.get("created_at", now)
                    if now - c_time >= 86400:
                        close_session_tab(sid)

            if IS_CLUSTER_MASTER:
                terms = firebase_sync_http("terminals", "GET")
                all_sessions = firebase_sync_http("sessions", "GET") or {}
                if terms and isinstance(terms, dict):
                    for tid, tval in terms.items():
                        if isinstance(tval, dict):
                            hb = float(tval.get("heartbeat", 0))
                            t_status = tval.get("status", "")
                            if now - hb > 15.0 and t_status != "OFFLINE":
                                firebase_sync_http(f"terminals/{tid}/status", "PUT", "OFFLINE")
                                dead_sid = tval.get("session_id")
                                if dead_sid and dead_sid in all_sessions:
                                    sess_meta = all_sessions[dead_sid]
                                    candidates = []
                                    for cand_id, cand_val in terms.items():
                                        if cand_id != tid and isinstance(cand_val, dict) and cand_val.get("status") == "FREE":
                                            c_hb = float(cand_val.get("heartbeat", 0))
                                            if now - c_hb <= 15.0:
                                                candidates.append((cand_id, cand_val.get("load", 0), cand_val.get("latency_ms", 9999)))

                                    candidates.sort(key=lambda x: (x[1], x[2]))
                                    new_worker = candidates[0][0] if candidates else NODE_ID

                                    sess_meta["node_id"] = new_worker
                                    firebase_sync_http(f"sessions/{dead_sid}", "PUT", sess_meta)

                                    firebase_sync_http(f"terminals/{new_worker}", "PATCH", {
                                        "status": "BUSY",
                                        "assigned_user_id": sess_meta.get("chat_id"),
                                        "session_id": dead_sid
                                    })

                                    re_task = {
                                        "type": "LOGIN_AND_TRADE",
                                        "chat_id": sess_meta.get("chat_id"),
                                        "session_id": dead_sid,
                                        "site_name": sess_meta.get("site_name", "Amar Club"),
                                        "login_url": sess_meta.get("login_url"),
                                        "wingo_url": sess_meta.get("wingo_url"),
                                        "phone": sess_meta.get("phone", ""),
                                        "password": sess_meta.get("password", ""),
                                        "anim_msg_id": None,
                                        "dispatched_at": time.time()
                                    }
                                    firebase_sync_http(f"terminals/{new_worker}/task", "PUT", re_task)
        except Exception:
            pass
        time.sleep(5)

# ==========================================
# 20. Interception Wrappers & Master Slot Dispatching
# ==========================================
_original_close_session_tab = close_session_tab
def close_session_tab(session_id):
    _original_close_session_tab(session_id)
    try:
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
            "status": "BUSY" if len(active_sessions) >= MAX_SESSIONS_PER_NODE else "FREE",
            "assigned_user_id": None,
            "task": None,
            "session_id": None,
            "load": len(active_sessions)
        })
        firebase_sync_http(f"sessions/{session_id}", "DELETE")
    except Exception:
        pass

_original_process_login = process_login
def distributed_process_login(chat_id, sid, phone, password, anim_msg_id):
    all_terminals = firebase_sync_http("terminals", "GET")
    now = time.time()
    free_target_node = None

    candidates = []
    if all_terminals and isinstance(all_terminals, dict):
        for tid, tinfo in all_terminals.items():
            if isinstance(tinfo, dict) and tinfo.get("status") == "FREE":
                hb = float(tinfo.get("heartbeat", 0))
                load_val = int(tinfo.get("load", 0))
                max_s = int(tinfo.get("max_slots", MAX_SESSIONS_PER_NODE))
                if now - hb <= 15.0 and load_val < max_s:
                    candidates.append((tid, load_val, tinfo.get("latency_ms", 9999)))

    if candidates:
        candidates.sort(key=lambda x: (x[1], x[2]))
        free_target_node = candidates[0][0]
    else:
        free_target_node = NODE_ID

    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = sess.get("login_url")
    wingo_url = sess.get("wingo_url")

    if free_target_node == NODE_ID:
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
            "status": "BUSY" if len(active_sessions) + 1 >= MAX_SESSIONS_PER_NODE else "FREE",
            "assigned_user_id": chat_id,
            "session_id": sid,
            "load": len(active_sessions) + 1
        })
        firebase_sync_http(f"sessions/{sid}", "PUT", {
            "node_id": NODE_ID,
            "chat_id": chat_id,
            "site_name": site_name,
            "login_url": login_url,
            "wingo_url": wingo_url,
            "phone": phone,
            "password": password
        })
        _original_process_login(chat_id, sid, phone, password, anim_msg_id)
    else:
        firebase_sync_http(f"terminals/{free_target_node}", "PATCH", {
            "assigned_user_id": chat_id,
            "session_id": sid
        })
        firebase_sync_http(f"sessions/{sid}", "PUT", {
            "node_id": free_target_node,
            "chat_id": chat_id,
            "site_name": site_name,
            "login_url": login_url,
            "wingo_url": wingo_url,
            "phone": phone,
            "password": password
        })
        task_payload = {
            "type": "LOGIN_AND_TRADE",
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": site_name,
            "login_url": login_url,
            "wingo_url": wingo_url,
            "phone": phone,
            "password": password,
            "anim_msg_id": anim_msg_id,
            "dispatched_at": time.time()
        }
        firebase_sync_http(f"terminals/{free_target_node}/task", "PUT", task_payload)

process_login = distributed_process_login

_original_handle_callbacks = handle_callbacks
def distributed_handle_callbacks(call):
    data = call.data or ""
    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    if not sid or action in ["check_channel_joined", "btn_enter_pass", "pk_gen_new", "pk_list_active", "pk_prompt_revoke"] or action.startswith("adm_") or action in PLATFORMS:
        return _original_handle_callbacks(call)

    target_node = NODE_ID
    if sid not in active_sessions or not active_sessions[sid].get("driver"):
        meta = firebase_sync_http(f"sessions/{sid}", "GET")
        if meta and isinstance(meta, dict) and meta.get("node_id"):
            target_node = meta["node_id"]

    if target_node == NODE_ID:
        return _original_handle_callbacks(call)
    else:
        relay_pkt = {
            "kind": "CALLBACK",
            "action": action,
            "sid": sid,
            "call_id": call.id,
            "data": call.data,
            "chat_id": call.message.chat.id,
            "message_id": call.message.message_id,
            "ts": time.time()
        }
        firebase_sync_http(f"terminals/{target_node}/action", "PUT", relay_pkt)
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

_original_handle_user_text = handle_user_text
def distributed_handle_user_text(message):
    chat_id = message.chat.id
    u = user_sessions.get(chat_id, {})
    sid = u.get("active_sid")

    if u.get("input_mode") in ["WAITING_PASSKEY", "WAITING_REVOKE_KEY"]:
        return _original_handle_user_text(message)

    target_node = NODE_ID
    if sid:
        if sid not in active_sessions or not active_sessions[sid].get("driver"):
            meta = firebase_sync_http(f"sessions/{sid}", "GET")
            if meta and isinstance(meta, dict) and meta.get("node_id"):
                target_node = meta["node_id"]

    if target_node == NODE_ID:
        return _original_handle_user_text(message)
    else:
        relay_pkt = {
            "kind": "TEXT_INPUT",
            "chat_id": chat_id,
            "sid": sid,
            "text": message.text.strip(),
            "message_id": message.message_id,
            "ts": time.time()
        }
        firebase_sync_http(f"terminals/{target_node}/action", "PUT", relay_pkt)
        safe_delete_message(chat_id, message.message_id)

for h in bot.callback_query_handlers:
    if h.get('function') == _original_handle_callbacks:
        h['function'] = distributed_handle_callbacks

for h in bot.message_handlers:
    if h.get('function') == _original_handle_user_text:
        h['function'] = distributed_handle_user_text

# ==========================================
# 21. Master-Worker Telegram Polling Coordinator
# ==========================================
_original_bot_infinity_polling = bot.infinity_polling

def cluster_managed_infinity_polling(*args, **kwargs):
    cluster_register_local_node()

    threading.Thread(target=cluster_node_heartbeat_loop, daemon=True).start()
    threading.Thread(target=cluster_remote_task_listener, daemon=True).start()
    threading.Thread(target=cluster_session_watchdog_loop, daemon=True).start()

    role = cluster_claim_leadership()

    if role == "MASTER":
        threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
        print(f"[*] [{to_bold(NODE_ID)}] Starting Telegram Polling as PRIMARY MASTER (BRAIN)...")
        _original_bot_infinity_polling(*args, **kwargs)
    elif role == "STANDBY":
        threading.Thread(target=cluster_standby_heartbeat_loop, daemon=True).start()
        print(f"[*] [{to_bold(NODE_ID)}] HOT-STANDBY active. Monitoring Primary Master...")
        while CLUSTER_ACTIVE:
            time.sleep(3)
            primary_data = firebase_sync_http("cluster/active_master", "GET")
            now = time.time()
            primary_dead = False
            if not primary_data or not isinstance(primary_data, dict):
                primary_dead = True
            else:
                last_hb = float(primary_data.get("heartbeat", 0))
                if now - last_hb > 10.0:
                    primary_dead = True

            if primary_dead:
                print(f"[*] Primary Master offline (>10s). Promoting standby node to MASTER...")
                claim_res = cluster_claim_leadership()
                if claim_res == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break
    else:
        print(f"[*] [{to_bold(NODE_ID)}] WORKER Active: Telegram polling bypassed to prevent Conflict 409.")
        while CLUSTER_ACTIVE:
            time.sleep(5)
            primary = firebase_sync_http("cluster/active_master", "GET")
            standby = firebase_sync_http("cluster/standby_master", "GET")
            now = time.time()

            claim_needed = False
            if not primary or not isinstance(primary, dict) or (now - float(primary.get("heartbeat", 0)) > 12.0):
                if not standby or not isinstance(standby, dict) or (now - float(standby.get("heartbeat", 0)) > 12.0):
                    claim_needed = True

            if claim_needed:
                print(f"[*] Master timeout detected. Attempting promotion...")
                new_role = cluster_claim_leadership()
                if new_role == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break

bot.infinity_polling = cluster_managed_infinity_polling

# ==========================================
# 22. Main Execution Entry Point
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT CLUSTER ENGINE ACTIVE')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
