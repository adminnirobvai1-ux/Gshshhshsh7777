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
import secrets
import string

# ==========================================
# 1. Automatic Package Installer
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing dependency: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")
install_and_import("psutil")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
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
# 3. Process Hygiene & Zombie Process Terminator
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
# 4. Configuration & Master/Worker Constants
# ==========================================
TOKEN = "8808949150:AAGSpz9tmSWxOiEHc6C7TjEmHikgO8bZR-A"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# Non-Headless execution inside VPS desktop display by default
HEADLESS_MODE = os.environ.get("HEADLESS_MODE", "false").lower() in ("true", "1", "yes")

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"
URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_cluster_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}
active_sessions = {}

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"
SUPER_ADMIN_ID = 8707571669
OWNER_USERNAME = "@MD_NAYEEM_DRX_TM"

FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
NODE_ID = f"vps_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"

IS_CLUSTER_MASTER = False
IS_STANDBY_MASTER = False
CLUSTER_ACTIVE = True

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
# 5. Firebase Realtime Database Engine
# ==========================================
def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 5.0):
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

# ==========================================
# 6. Network Latency & Speed Diagnostics
# ==========================================
def measure_network_latency(url: str, timeout: float = 3.5) -> float:
    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return round((time.time() - start) * 1000, 2)
    except Exception:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response.read(128)
                return round((time.time() - start) * 1000, 2)
        except Exception:
            return 9999.0

def get_cluster_platform_latencies():
    results = {}
    for p_id, p_info in PLATFORMS.items():
        results[p_info["name"]] = measure_network_latency(p_info["login"])
    return results

# ==========================================
# 7. Background Modal & Popup Killer JS
# ==========================================
AGGRESSIVE_MODAL_WATCHER_JS = """
(function(){
    if (window.__MODAL_WATCHER_ACTIVE) return;
    window.__MODAL_WATCHER_ACTIVE = true;

    const killModals = () => {
        try {
            const promoKeywords = [
                'BONUS', 'DAILY RECHARGE', 'DAILY BONUS', 'DEPOSIT BONUS',
                'ANNOUNCEMENT', 'NOTICE', 'CHECK IN', 'SIGN IN', 'RECHARGE BONUS',
                'ALREADY LOGGED IN', 'CONFIRM', 'DETERMINE', 'REMINDER'
            ];

            const dialogs = document.querySelectorAll('.van-dialog, .van-popup, .van-overlay, div[role="dialog"]');
            dialogs.forEach(d => {
                if (d.closest('#sys-core-fin') || d.closest('#_run_box')) return;
                const txt = (d.innerText || '').toUpperCase();
                for (let kw of promoKeywords) {
                    if (txt.includes(kw)) {
                        const closeBtn = d.querySelector('.van-dialog__confirm, .van-popup__close-icon, button[class*="close"], button[class*="confirm"], .van-button--primary, button');
                        if (closeBtn) {
                            try { closeBtn.click(); } catch(e){}
                        }
                        break;
                    }
                }
            });

            const genericCloseSelectors = [
                '.van-dialog__confirm', '.dialog-confirm', '.van-popup__close-icon',
                'button[class*="close"]', '.dialog-close', '.van-button--primary',
                '.van-dialog button', 'div[class*="modal-close"]'
            ];

            genericCloseSelectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(btn => {
                    if (btn && btn.offsetParent !== null && !btn.closest('#sys-core-fin') && !btn.closest('#_run_box')) {
                        try { btn.click(); } catch(e){}
                    }
                });
            });
        } catch(e){}
    };

    const observer = new MutationObserver(() => killModals());
    observer.observe(document.documentElement, { childList: true, subtree: true });
    setInterval(killModals, 300);
})();
"""

# ==========================================
# 8. Isolated Firefox Execution Engine
# ==========================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session state not allocated.")

    cleanup_zombie_browsers()

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    if HEADLESS_MODE:
        options.add_argument("--headless")

    options.add_argument("-profile")
    options.add_argument(profile_dir)

    # Stability & Resource Optimization
    options.set_preference("browser.sessionhistory.max_entries", 2)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 2048)
    options.set_preference("javascript.options.mem.max", 32768)
    options.set_preference("network.http.pipelining", False)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(20)
    driver.implicitly_wait(3)
    driver.set_window_size(420, 900)

    driver.get(target_url)

    try:
        driver.execute_script(AGGRESSIVE_MODAL_WATCHER_JS)
    except Exception:
        pass

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
        print(f"[*] Lock acquisition timed out for session {sid}.")
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
        print(f"[*] Task execution timeout (> {timeout}s) for {sid}. Releasing lock.")
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
        print(f"[*] Tab execution error for {sid}: {result_container['error']}")
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

    try:
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
            "status": "FREE",
            "assigned_user_id": None,
            "session_id": None,
            "load": len(active_sessions)
        })
        firebase_sync_http(f"sessions/{session_id}", "DELETE")
    except Exception:
        pass

# ==========================================
# 9. Smart Telegram Image Replacement Engine
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
            print(f"[*] Photo replace error: {e}")

    try:
        if os.path.exists(image_path):
            os.remove(image_path)
    except Exception:
        pass
    gc.collect()

# ==========================================
# 10. Automation Injections & Game Core
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
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed concurrent session prompt" };
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

NEW_WINGO_RUNBOX_JS = """
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
    tgtInp.placeholder='TARGET PROFIT';
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
                st.isRun=false;
                clearInterval(st.autoInt);
                lkOvl.style.display='none';
                document.body.style.overflow='';
                return;
            }else{
                uBal.innerText=uF(st.curBal>0?st.curBal.toFixed(2):'--');
            }

            let ts=Math.floor(Date.now()/1000);
            let dataArray = null;
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3500);
                let res = await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts=" + ts, { signal: controller.signal });
                clearTimeout(timeoutId);
                dataArray = await res.json();
            } catch(e) {
                isFetchingApi = false;
                return;
            }

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

    let tradeStartTs = 0;
    setInterval(() => {
        if (st.isTrd) {
            if (!tradeStartTs) tradeStartTs = Date.now();
            else if (Date.now() - tradeStartTs > 12000) {
                st.isTrd = false;
                isFetchingApi = false;
                tradeStartTs = 0;
                document.querySelectorAll('.drx-elec-target').forEach(el => el.classList.remove('drx-elec-target'));
                const uSts = document.getElementById('ui-sts');
                if (uSts) { uSts.innerText = uF('RST'); uSts.className = 'txt-blk-warn'; }
            }
        } else {
            tradeStartTs = 0;
        }
    }, 3000);

    goBtn.onclick=()=>{
        let inputTarget=parseFloat(tgtInp.value);
        if(!inputTarget||inputTarget<=0){
            alert('Please specify a valid Target Profit Amount.');
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
# 11. Clean English Communication Center
# ==========================================
def get_text(key, **kwargs):
    messages = {
        "welcome": (
            f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
            f"Welcome to the high-performance distributed trading cluster.\n"
            f"All operations are continuously secured and executed 24/7."
        ),
        "choose_site": (
            f"<b>{to_bold('SELECT TARGET PLATFORM')}</b>\n\n"
            f"Please choose your target gaming platform to proceed:"
        ),
        "credentials_card": (
            f"<b>{to_bold('ACCOUNT AUTHENTICATION')}</b>\n\n"
            f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
            f"Please click the buttons below to enter your account phone number and password. "
            f"Credentials are kept strictly confidential and purged from chat history upon execution."
        ),
        "ask_number": (
            f"<b>{to_bold('ACCOUNT PHONE NUMBER')}</b>\n\n"
            f"Please enter your registered phone number:"
        ),
        "ask_password": (
            f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\n"
            f"Please enter your account password:"
        ),
        "login_success": (
            f"<b>{to_bold('AUTHENTICATION SUCCESSFUL')}</b>\n\n"
            f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
            f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
            f"Session established. Press <b>START CONFIGURATION</b> below to proceed:"
        ),
        "login_failed": (
            f"<b>{to_bold('AUTHENTICATION FAILED')}</b>\n\n"
            f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
            f"Reason: <i>{kwargs.get('error', 'Invalid credentials or connection timeout.')}</i>\n\n"
            f"Send /start to reinitialize the session."
        ),
        "input_target": (
            f"<b>{to_bold('TARGET PROFIT CONFIGURATION')}</b>\n\n"
            f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
            f"Enter your target profit amount in currency units (e.g. <code>500</code>):"
        ),
        "input_steps": (
            f"<b>{to_bold('MARTINGALE RECOVERY STEPS')}</b>\n\n"
            f"Target Profit: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
            f"Enter total Martingale defense steps (recommended: <code>7</code> or <code>10</code>):"
        ),
        "running_dashboard": (
            f"<b>{to_bold('24/7 TRADING ENGINE ACTIVE')}</b>\n\n"
            f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
            f"Assigned Worker: <code>{kwargs.get('worker_id', NODE_ID)}</code>\n"
            f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
            f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
            f"Martingale Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
            f"Status: <b>Continuous background trading active.</b>"
        ),
        "cancelled": (
            f"<b>{to_bold('SESSION TERMINATED')}</b>\n\n"
            f"The active browser session has been safely closed. Type /start to initiate a new task."
        )
    }
    return messages.get(key, "")

# ==========================================
# 12. Inline Keyboards & Controllers
# ==========================================
def get_credentials_keyboard(sid):
    sess = active_sessions.get(sid, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('INPUT NUMBER')}", callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(f"{to_bold('INPUT PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"{to_bold('INPUT PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('START CONFIGURATION')}", callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_sessions.get(sid, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 7)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "SET TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "SET STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_lbl)}", callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(f"{to_bold(s_lbl)}", callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('LAUNCH ENGINE')}", callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(f"{to_bold('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid):
    sess = active_sessions.get(sid, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SCREENSHOT')}", callback_data=f"shot:{sid}"),
        InlineKeyboardButton(f"{to_bold('BALANCE')}", callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('STATISTICS')}", callback_data=f"stats:{sid}"),
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

def get_passkey_keyboard():
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

def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⚡ {to_bold('WORKER CLUSTER')}", callback_data="adm:workers"),
        InlineKeyboardButton(f"👥 {to_bold('ACTIVE SESSIONS')}", callback_data="adm:logins")
    )
    markup.add(
        InlineKeyboardButton(f"📶 {to_bold('SPEED / LATENCY')}", callback_data="adm:speed"),
        InlineKeyboardButton(f"🔑 {to_bold('PASSKEY MANAGER')}", callback_data="adm:passkeys")
    )
    markup.add(
        InlineKeyboardButton(f"📋 {to_bold('TASK COMPLETED MONITOR')}", callback_data="adm:tasks"),
        InlineKeyboardButton(f"🔄 {to_bold('REFRESH PANEL')}", callback_data="adm:refresh")
    )
    return markup

def get_admin_back_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"⬅️ {to_bold('BACK TO DASHBOARD')}", callback_data="adm:menu")
    )
    return markup

# ==========================================
# 13. Passkey Validation & Expiration
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
    pass_exp = u.get("pass_expiry", 0)
    return time.time() < pass_exp

def create_24h_passkey(created_by=SUPER_ADMIN_ID):
    raw_token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    pass_code = f"KEY-{raw_token[:4]}-{raw_token[4:]}"
    now = time.time()
    pass_payload = {
        "code": pass_code,
        "created_at": now,
        "expires_at": now + 86400,
        "status": "ACTIVE",
        "created_by": created_by,
        "used_by": None
    }
    firebase_sync_http(f"passkeys/{pass_code}", "PUT", pass_payload)
    return pass_payload

def revoke_passkey(pass_code):
    firebase_sync_http(f"passkeys/{pass_code}", "DELETE")

def get_all_passkeys():
    data = firebase_sync_http("passkeys", "GET") or {}
    now = time.time()
    valid_keys = {}
    for code, kdata in list(data.items()):
        if isinstance(kdata, dict):
            if kdata.get("expires_at", 0) < now:
                firebase_sync_http(f"passkeys/{code}", "DELETE")
            else:
                valid_keys[code] = kdata
    return valid_keys

# ==========================================
# 14. Automation Workflow & Login Engine
# ==========================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING AUTOMATION WORKER</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Spawning browser instance...</code>",
        "<b>TARGET PLATFORM INITIALIZATION</b>\n<code>▰▰▰▱▱▱▱▱▱▱ 35% Establishing handshake...</code>",
        "<b>DISPATCHING CREDENTIALS</b>\n<code>▰▰▰▰▰▰▱▱▱▱ 65% Injecting user credentials...</code>",
        "<b>VERIFYING SESSION TOKENS</b>\n<code>▰▰▰▰▰▰▰▰▰▰ 100% Verification finished!</code>"
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
    login_url = sess.get("login_url") or (URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN)

    if anim_msg_id:
        play_clean_login_animation(chat_id, anim_msg_id)

    try:
        driver, handle = allocate_session_tab(sid, login_url)
    except Exception as e:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text("login_failed", site_name=site_name, error=str(e)))
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
        bot.send_message(chat_id, get_text("login_failed", site_name=site_name, error="Authentication fields not located."))
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
                err_detail = res.get("message", "Incorrect login credentials provided.")
                break
        time.sleep(0.5)

    def _token_chk(drv):
        return drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")
    if safe_tab_execute(sid, _token_chk):
        login_status = "SUCCESS"

    safe_delete_message(chat_id, anim_msg_id)

    if login_status == "ERROR":
        close_session_tab(sid)
        bot.send_message(chat_id, get_text("login_failed", site_name=site_name, error=err_detail))
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
        get_text("login_success", site_name=site_name, phone=masked_phone),
        get_start_screen_keyboard(sid)
    )

def prepare_wingo_parameters(chat_id, sid):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")

    def _nav(drv):
        try:
            drv.execute_script(AGGRESSIVE_MODAL_WATCHER_JS)
            drv.execute_script(NEW_WINGO_RUNBOX_JS)
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
        f"<b>{to_bold('WINGO 30S MARKET SYNCHRONIZED')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Live Balance: <code>৳ {current_bal:.2f}</code>\n\n"
        f"Configure your parameters using the buttons below, then click <b>LAUNCH ENGINE</b>:"
    )

    display_or_replace_photo(
        chat_id, sid,
        wingo_snap,
        config_caption,
        get_setup_param_keyboard(sid)
    )

# ==========================================
# 15. Real-Time Monitor & Task History Loop
# ==========================================
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

            # Sync live task update to Firebase for real-time inspection
            firebase_sync_http(f"tasks/{sid}", "PATCH", {
                "current_balance": sess["cur_bal"],
                "wins": sess["wins"],
                "losses": sess["losses"],
                "last_update": time.time()
            })

            if sess["cur_bal"] >= tgt_amt and tgt_amt > 0 and sess["cur_bal"] > 0:
                sess["is_trading"] = False
                start_b = sess.get("start_bal", 0)
                profit = sess["cur_bal"] - start_b

                # Update completed status in Task Completed Monitor
                firebase_sync_http(f"tasks/{sid}", "PATCH", {
                    "status": "COMPLETED",
                    "final_balance": sess["cur_bal"],
                    "profit": profit,
                    "completed_at": time.time()
                })

                screen_path = os.path.join(PROFILES_BASE_DIR, f"win_{sid}.png")
                def _shot(drv):
                    drv.save_screenshot(screen_path)
                safe_tab_execute(sid, _shot)

                msg = (
                    f"<b>{to_bold('TARGET PROFIT ACHIEVED')}</b>\n\n"
                    f"The specified target has been successfully reached!\n\n"
                    f"Initial Balance: <code>৳ {start_b:.2f}</code>\n"
                    f"Final Balance: <code>৳ {sess['cur_bal']:.2f}</code>\n"
                    f"Net Profit: <code>+৳ {profit:.2f}</code>\n"
                    f"Rounds Won: <b>{sess['wins']}</b> | Rounds Lost: <b>{sess['losses']}</b>"
                )

                if os.path.exists(screen_path):
                    display_or_replace_photo(chat_id, sid, screen_path, msg, None)
                else:
                    bot.send_message(chat_id, msg)
                break

        time.sleep(4)

# ==========================================
# 16. Distributed Cluster Election & Coordination
# ==========================================
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
            print(f"[*] [{to_bold(NODE_ID)}] Cluster Election: ASSUMED PRIMARY MASTER ROLE.")
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
            print(f"[*] [{to_bold(NODE_ID)}] Cluster Role: HOT-STANDBY MASTER.")
            return "STANDBY"

    IS_CLUSTER_MASTER = False
    IS_STANDBY_MASTER = False
    active_id = primary.get("node_id", "Unknown") if isinstance(primary, dict) else "Unknown"
    print(f"[*] [{to_bold(NODE_ID)}] Cluster Role: WORKER NODE (Primary Master: {active_id}).")
    return "WORKER"

def cluster_register_local_node():
    lat = measure_network_latency("https://amarclub1.com")
    node_payload = {
        "status": "FREE",
        "heartbeat": time.time(),
        "assigned_user_id": None,
        "task": None,
        "node_id": NODE_ID,
        "load": len(active_sessions),
        "latency_ms": lat,
        "registered_at": time.time()
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)
    print(f"[*] [{to_bold(NODE_ID)}] Registered in cluster registry as FREE (Latency: {lat}ms).")

def cluster_node_heartbeat_loop():
    while CLUSTER_ACTIVE:
        try:
            status_val = "BUSY" if active_sessions else "FREE"
            lat = measure_network_latency("https://amarclub1.com")
            hb_data = {
                "heartbeat": time.time(),
                "status": status_val,
                "load": len(active_sessions),
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
            if not active_sessions:
                time.sleep(1.5)
            else:
                time.sleep(0.6)

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

                    print(f"[*] [{to_bold(NODE_ID)}] Picked up remote execution task: {sid} for Chat: {chat_id}")

                    active_sessions[sid] = {
                        "chat_id": chat_id,
                        "session_id": sid,
                        "site_name": site_name,
                        "login_url": login_url,
                        "wingo_url": wingo_url,
                        "phone": phone,
                        "password": password,
                        "target_profit": 0,
                        "total_steps": 7,
                        "is_trading": False,
                        "created_at": time.time(),
                        "anim_tick": 0,
                        "lock": threading.RLock()
                    }
                    user_sessions.setdefault(chat_id, {})["active_sid"] = sid

                    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                        "status": "BUSY",
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

            # Master orchestrates dead worker recovery
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
                                                score = cand_val.get("load", 0) * 100 + float(cand_val.get("latency_ms", 100))
                                                candidates.append((cand_id, score))

                                    new_worker = min(candidates, key=lambda x: x[1])[0] if candidates else NODE_ID
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
        time.sleep(6)

# ==========================================
# 17. Load Balancer & Dispatch Wrappers
# ==========================================
_original_process_login = process_login
def distributed_process_login(chat_id, sid, phone, password, anim_msg_id):
    all_terminals = firebase_sync_http("terminals", "GET")
    now = time.time()
    candidates = []

    if all_terminals and isinstance(all_terminals, dict):
        for tid, tinfo in all_terminals.items():
            if isinstance(tinfo, dict) and tinfo.get("status") == "FREE":
                hb = float(tinfo.get("heartbeat", 0))
                if now - hb <= 15.0:
                    score = tinfo.get("load", 0) * 100 + float(tinfo.get("latency_ms", 150))
                    candidates.append((tid, score))

    free_target_node = min(candidates, key=lambda x: x[1])[0] if candidates else NODE_ID

    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = sess.get("login_url")
    wingo_url = sess.get("wingo_url")

    if free_target_node == NODE_ID:
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
            "status": "BUSY",
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
            "status": "BUSY",
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

# ==========================================
# 18. Admin Control Panel (/admin, /pass)
# ==========================================
@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        bot.send_message(chat_id, "<b>ACCESS DENIED</b>: Administrative authorization required.")
        return

    text = (
        f"<b>{to_bold('ADMINISTRATIVE CONTROL DASHBOARD')}</b>\n\n"
        f"Server Host: <code>{NODE_ID}</code>\n"
        f"Assigned Role: <b>{'PRIMARY MASTER' if IS_CLUSTER_MASTER else ('STANDBY' if IS_STANDBY_MASTER else 'WORKER')}</b>\n"
        f"Cluster Time: <code>{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</code>\n\n"
        f"Select a management module below:"
    )
    bot.send_message(chat_id, text, reply_markup=get_admin_dashboard_keyboard())

@bot.message_handler(commands=['pass'])
def handle_pass_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id == SUPER_ADMIN_ID:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"➕ {to_bold('CREATE 24H KEY')}", callback_data="pass_act:gen"),
            InlineKeyboardButton(f"📜 {to_bold('VIEW ACTIVE KEYS')}", callback_data="pass_act:list")
        )
        markup.add(
            InlineKeyboardButton(f"⬅️ {to_bold('BACK TO DASHBOARD')}", callback_data="adm:menu")
        )
        bot.send_message(
            chat_id,
            f"<b>{to_bold('PASSKEY CONTROLLER')}</b>\n\nManage 24-hour access keys below:",
            reply_markup=markup
        )
    else:
        u = user_sessions.get(chat_id, {})
        expiry = u.get("pass_expiry", 0)
        now = time.time()
        if expiry > now:
            rem_hrs = int((expiry - now) // 3600)
            rem_min = int(((expiry - now) % 3600) // 60)
            bot.send_message(
                chat_id,
                f"<b>{to_bold('PASSKEY STATUS')}</b>\n\n"
                f"Status: <b>ACTIVE</b>\n"
                f"Time Remaining: <b>{rem_hrs}h {rem_min}m</b>"
            )
        else:
            bot.send_message(
                chat_id,
                f"<b>{to_bold('PASSKEY REQUIRED')}</b>\n\n"
                f"You do not possess an active 24-hour passkey.\n"
                f"Contact the system owner <b>{OWNER_USERNAME}</b> to obtain access.",
                reply_markup=get_passkey_keyboard()
            )

# ==========================================
# 19. Telegram Callback & Flow Routing
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data or ""
    parts = data.split(":")
    action = parts[0]
    param = parts[1] if len(parts) > 1 else None

    # --- ADMIN ACTIONS ---
    if action == "adm":
        if chat_id != SUPER_ADMIN_ID:
            bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)
            return

        if param == "menu" or param == "refresh":
            bot.answer_callback_query(call.id, "Dashboard updated.")
            text = (
                f"<b>{to_bold('ADMINISTRATIVE CONTROL DASHBOARD')}</b>\n\n"
                f"Server Host: <code>{NODE_ID}</code>\n"
                f"Assigned Role: <b>{'PRIMARY MASTER' if IS_CLUSTER_MASTER else ('STANDBY' if IS_STANDBY_MASTER else 'WORKER')}</b>\n"
                f"Cluster Time: <code>{time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}</code>\n\n"
                f"Select a management module below:"
            )
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_dashboard_keyboard())
            return

        elif param == "workers":
            bot.answer_callback_query(call.id)
            terms = firebase_sync_http("terminals", "GET") or {}
            now = time.time()
            total = len(terms)
            active_cnt = sum(1 for t in terms.values() if isinstance(t, dict) and t.get("status") == "BUSY")
            idle_cnt = sum(1 for t in terms.values() if isinstance(t, dict) and t.get("status") == "FREE" and (now - float(t.get("heartbeat", 0))) <= 15.0)
            offline_cnt = total - (active_cnt + idle_cnt)

            lines = [
                f"<b>{to_bold('CLUSTER WORKER STATUS')}</b>\n",
                f"Total Connected Terminals: <b>{total}</b>",
                f"Active / Busy: <b>{active_cnt}</b>",
                f"Idle / Available: <b>{idle_cnt}</b>",
                f"Offline / Disconnected: <b>{offline_cnt}</b>\n",
                "<b>Node Directory:</b>"
            ]
            for tid, tinfo in terms.items():
                if isinstance(tinfo, dict):
                    st = tinfo.get("status", "UNKNOWN")
                    lat = tinfo.get("latency_ms", "N/A")
                    load = tinfo.get("load", 0)
                    lines.append(f"• <code>{tid}</code> | Status: <b>{st}</b> | Latency: <code>{lat}ms</code> | Active Jobs: <code>{load}</code>")

            bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_back_keyboard())
            return

        elif param == "logins":
            bot.answer_callback_query(call.id)
            all_sess = firebase_sync_http("sessions", "GET") or {}
            lines = [f"<b>{to_bold('ACTIVE USER SESSIONS')}</b>\n"]
            if not all_sess:
                lines.append("<i>No active user browser sessions detected.</i>")
            else:
                lines.append(f"Total Registered Sessions: <b>{len(all_sess)}</b>\n")
                for s_id, s_info in all_sess.items():
                    if isinstance(s_info, dict):
                        u_chat = s_info.get("chat_id", "N/A")
                        site = s_info.get("site_name", "N/A")
                        phone = s_info.get("phone", "N/A")
                        node = s_info.get("node_id", "N/A")
                        m_phone = phone[:3] + "****" + phone[-3:] if len(str(phone)) >= 6 else phone
                        lines.append(f"• User: <code>{u_chat}</code> | Platform: <b>{site}</b> | Account: <code>{m_phone}</code> | Node: <code>{node}</code>")

            bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_back_keyboard())
            return

        elif param == "speed":
            bot.answer_callback_query(call.id, "Testing platform latency...")
            latencies = get_cluster_platform_latencies()
            lines = [
                f"<b>{to_bold('NETWORK SPEED & LATENCY MATRIX')}</b>\n",
                f"Source Node: <code>{NODE_ID}</code>\n"
            ]
            for name, lat in latencies.items():
                icon = "🟢" if lat < 300 else ("🟡" if lat < 800 else "🔴")
                lines.append(f"{icon} <b>{name}</b>: <code>{lat} ms</code>")

            bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_back_keyboard())
            return

        elif param == "passkeys":
            bot.answer_callback_query(call.id)
            keys = get_all_passkeys()
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton(f"➕ {to_bold('CREATE 24H KEY')}", callback_data="pass_act:gen"),
                InlineKeyboardButton(f"🔄 {to_bold('REFRESH')}", callback_data="adm:passkeys")
            )
            for code, kinfo in list(keys.items())[:6]:
                markup.add(
                    InlineKeyboardButton(f"🗑 REVOKE {code}", callback_data=f"pass_del:{code}")
                )
            markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK')}", callback_data="adm:menu"))

            text = f"<b>{to_bold('24-HOUR PASSKEY CONTROLLER')}</b>\n\nActive Keys in Database: <b>{len(keys)}</b>\nClick below to create or revoke access keys:"
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
            return

        elif param == "tasks":
            bot.answer_callback_query(call.id)
            tasks_data = firebase_sync_http("tasks", "GET") or {}
            completed = sum(1 for t in tasks_data.values() if isinstance(t, dict) and t.get("status") == "COMPLETED")
            pending = len(tasks_data) - completed

            markup = InlineKeyboardMarkup(row_width=1)
            seen_users = {}
            for t_id, t_val in tasks_data.items():
                if isinstance(t_val, dict):
                    uid = t_val.get("user_id")
                    if uid and uid not in seen_users:
                        seen_users[uid] = t_val.get("site_name", "WinGo")
                        markup.add(InlineKeyboardButton(f"👤 Account User: {uid} ({seen_users[uid]})", callback_data=f"adm_usr:{uid}"))

            markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK')}", callback_data="adm:menu"))

            text = (
                f"<b>{to_bold('TASK COMPLETED MONITOR')}</b>\n\n"
                f"Total Submitted Accounts: <b>{len(tasks_data)}</b>\n"
                f"Tasks Completed: <b>{completed}</b>\n"
                f"Tasks In Progress: <b>{pending}</b>\n\n"
                f"Select an account submission below to inspect individual progress:"
            )
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
            return

    elif action == "adm_usr":
        if chat_id != SUPER_ADMIN_ID: return
        target_uid = int(param)
        tasks_data = firebase_sync_http("tasks", "GET") or {}
        user_tasks = [t for t in tasks_data.values() if isinstance(t, dict) and t.get("user_id") == target_uid]

        lines = [f"<b>{to_bold(f'TASK DETAILS - USER {target_uid}')}</b>\n"]
        if not user_tasks:
            lines.append("<i>No records found for this account.</i>")
        else:
            for t in user_tasks:
                st = t.get("status", "PENDING")
                site = t.get("site_name", "WinGo")
                start_b = t.get("start_balance", 0.0)
                tgt_p = t.get("target_profit", 0.0)
                cur_b = t.get("current_balance", start_b)
                wins = t.get("wins", 0)
                losses = t.get("losses", 0)
                lines.append(
                    f"• Platform: <b>{site}</b>\n"
                    f"  Status: <b>{st}</b>\n"
                    f"  Initial Bal: <code>৳ {start_b:.2f}</code> | Target: <code>+৳ {tgt_p:.2f}</code>\n"
                    f"  Live Bal: <code>৳ {cur_b:.2f}</code> | Wins: <b>{wins}</b> | Losses: <b>{losses}</b>\n"
                )

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK TO TASKS')}", callback_data="adm:tasks"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    # --- PASSKEY CRUD ACTIONS ---
    elif action == "pass_act":
        if chat_id != SUPER_ADMIN_ID: return
        if param == "gen":
            new_key = create_24h_passkey(chat_id)
            bot.answer_callback_query(call.id, "Passkey Generated!", show_alert=True)
            text = (
                f"<b>{to_bold('NEW 24-HOUR PASSKEY GENERATED')}</b>\n\n"
                f"Passkey Code: <code>{new_key['code']}</code>\n"
                f"Duration: <b>24 Hours</b>\n"
                f"Status: <b>ACTIVE</b>\n\n"
                f"Provide this key to an authorized user to activate bot access."
            )
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK TO PASSKEYS')}", callback_data="adm:passkeys"))
            bot.send_message(chat_id, text, reply_markup=markup)
            return

        elif param == "list":
            bot.answer_callback_query(call.id)
            keys = get_all_passkeys()
            lines = [f"<b>{to_bold('ACTIVE 24H PASSKEYS')}</b>\n"]
            now = time.time()
            for code, kdata in keys.items():
                rem_h = int((kdata.get("expires_at", 0) - now) // 3600)
                lines.append(f"• <code>{code}</code> (Expires in {rem_h} hours)")
            if not keys:
                lines.append("<i>No active passkeys found.</i>")

            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK')}", callback_data="adm:passkeys"))
            bot.send_message(chat_id, "\n".join(lines), reply_markup=markup)
            return

    elif action == "pass_del":
        if chat_id != SUPER_ADMIN_ID: return
        revoke_passkey(param)
        bot.answer_callback_query(call.id, f"Passkey {param} revoked.", show_alert=True)
        keys = get_all_passkeys()
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"➕ {to_bold('CREATE 24H KEY')}", callback_data="pass_act:gen"),
            InlineKeyboardButton(f"🔄 {to_bold('REFRESH')}", callback_data="adm:passkeys")
        )
        for code in list(keys.keys())[:6]:
            markup.add(InlineKeyboardButton(f"🗑 REVOKE {code}", callback_data=f"pass_del:{code}"))
        markup.add(InlineKeyboardButton(f"⬅️ {to_bold('BACK')}", callback_data="adm:menu"))
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    # --- STANDARD USER ACTIONS ---
    if action == "check_channel_joined":
        if check_channel_membership(chat_id):
            bot.answer_callback_query(call.id, "Channel membership confirmed.")
            if not is_user_pass_valid(chat_id):
                user_sessions.setdefault(chat_id, {})["step"] = "WAITING_PASSKEY_AUTH"
                caption = (
                    f"<b>{to_bold('24-HOUR PASSKEY REQUIRED')}</b>\n\n"
                    f"An active 24-hour authorization key is required to utilize the automation engine.\n"
                    f"Click below to input your passkey or request one from the owner."
                )
                bot.edit_message_text(
                    caption,
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=get_passkey_keyboard()
                )
            else:
                user_sessions.setdefault(chat_id, {})["step"] = "CHOOSE_SITE"
                bot.edit_message_text(
                    get_text("choose_site"),
                    chat_id=chat_id,
                    message_id=call.message.message_id,
                    reply_markup=get_six_platform_keyboard()
                )
        else:
            bot.answer_callback_query(call.id, "Channel membership not detected. Please join first.", show_alert=True)
        return

    elif action == "btn_enter_pass":
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_PASSKEY"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, f"<b>{to_bold('INPUT 24H PASSKEY')}</b>\n\nPlease enter your key code:")
        user_sessions[chat_id]["passkey_prompt_id"] = pm.message_id
        return

    elif action in PLATFORMS or action in ["site_amarclub", "site_dkwin"]:
        p_cfg = PLATFORMS.get(action, {
            "name": "Amar Club" if action == "site_amarclub" else "DK Win",
            "login": URL_AMARCLUB_LOGIN if action == "site_amarclub" else URL_DKWIN_LOGIN,
            "wingo": URL_AMARCLUB_WINGO if action == "site_amarclub" else URL_DKWIN_WINGO
        })

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
            "total_steps": 7,
            "is_trading": False,
            "created_at": time.time(),
            "anim_tick": 0,
            "lock": threading.RLock()
        }

        user_sessions.setdefault(chat_id, {})["active_sid"] = sid

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text("credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    elif action == "ask_num" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_PHONE"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text("ask_number"))
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "ask_pass" and sid in active_sessions:
        if not active_sessions[sid].get("phone"):
            bot.answer_callback_query(
                call.id,
                "Please enter your phone number first.",
                show_alert=True
            )
            return

        active_sessions[sid]["input_mode"] = "WAITING_PASS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text("ask_password"))
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "start_cfg" and sid in active_sessions:
        bot.answer_callback_query(call.id, "Preparing WinGo 30S market environment...")
        threading.Thread(target=prepare_wingo_parameters, args=(chat_id, sid), daemon=True).start()

    elif action == "set_tgt" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_TARGET"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[sid].get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, get_text("input_target", balance=f"{cur_bal:.2f}"))
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        tgt = active_sessions[sid].get("target_profit", 0)
        p_msg = bot.send_message(chat_id, get_text("input_steps", target=tgt))
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and sid in active_sessions:
        sess = active_sessions[sid]

        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "Please set a valid target profit amount first.", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Launching 24/7 automation engine...")
        sess["is_trading"] = True

        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        # Record task in Firebase for Admin Monitor
        firebase_sync_http(f"tasks/{sid}", "PUT", {
            "user_id": chat_id,
            "session_id": sid,
            "site_name": sess.get("site_name", "Amar Club"),
            "start_balance": cur_b,
            "target_profit": sess["target_profit"],
            "target_balance": target_total,
            "total_steps": sess["total_steps"],
            "status": "RUNNING",
            "current_balance": cur_b,
            "wins": 0,
            "losses": 0,
            "created_at": time.time()
        })

        def _run_core(drv):
            drv.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
        safe_tab_execute(sid, _run_core)

        time.sleep(2.0)

        start_snap = os.path.join(PROFILES_BASE_DIR, f"run_{sid}.png")
        def _shot(drv):
            drv.save_screenshot(start_snap)
        safe_tab_execute(sid, _shot)

        dashboard_caption = get_text(
            "running_dashboard",
            site_name=sess.get("site_name", "Amar Club"),
            worker_id=NODE_ID,
            start_bal=f"{cur_b:.2f}",
            target_bal=f"{target_total:.2f}",
            steps=sess["total_steps"]
        )

        display_or_replace_photo(
            chat_id, sid,
            start_snap,
            dashboard_caption,
            get_trading_control_keyboard(sid)
        )

        threading.Thread(target=monitor_trading_progress, args=(chat_id, sid), daemon=True).start()

    elif action == "shot" and sid in active_sessions:
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "Capturing live viewport...")
        temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")

        def _shot(drv):
            drv.save_screenshot(temp_shot)
        safe_tab_execute(sid, _shot)

        if os.path.exists(temp_shot):
            t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
            caption = (
                f"<b>{to_bold('24/7 TRADING ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {sess.get('start_bal', 0.0):.2f}</code>\n"
                f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
                f"Martingale Steps: <b>{sess.get('total_steps', 7)}</b>\n\n"
                f"Snapshot Time: <code>{time.strftime('%H:%M:%S UTC')}</code>\n"
                f"Status: <b>Engine executing autonomously.</b>"
            )
            display_or_replace_photo(chat_id, sid, temp_shot, caption, get_trading_control_keyboard(sid))
        else:
            bot.send_message(chat_id, "Viewport screenshot temporarily unavailable. Reloading...")

    elif action == "bal" and sid in active_sessions:
        def _bal(drv):
            return drv.execute_script(FETCH_BALANCE_JS)
        b = safe_tab_execute(sid, _bal)
        if b is not None:
            bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Retrieving balance...", show_alert=True)

    elif action == "stats" and sid in active_sessions:
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
                f"<b>{to_bold('PERFORMANCE DIAGNOSTICS')}</b>\n\n"
                f"Live Balance: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                f"Target Level: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                f"Current Martingale Step: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                f"Rounds Won: <b>{data_rep['w']}</b> | Rounds Lost: <b>{data_rep['l']}</b>"
            )
            bot.send_message(chat_id, stat_txt)
        else:
            bot.answer_callback_query(call.id, "Synchronizing engine data...", show_alert=True)

    elif action == "stop" and sid in active_sessions:
        sess = active_sessions[sid]
        def _stop(drv):
            drv.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
        safe_tab_execute(sid, _stop)
        sess["is_trading"] = False
        firebase_sync_http(f"tasks/{sid}", "PATCH", {"status": "PAUSED"})
        bot.answer_callback_query(call.id, "Trading automation paused.", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nEngine paused by user command.")

    elif action == "cancel" and sid in active_sessions:
        bot.answer_callback_query(call.id, "Session terminated.")
        close_session_tab(sid)
        firebase_sync_http(f"tasks/{sid}", "PATCH", {"status": "TERMINATED"})
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, get_text("cancelled"))

# ==========================================
# 20. Text Handlers & Input Routing
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    chat_id = message.chat.id
    user_sessions[chat_id] = {}

    if not check_channel_membership(chat_id):
        bot.send_message(
            chat_id,
            f"<b>{to_bold('CHANNEL VERIFICATION REQUIRED')}</b>\n\n"
            f"You must join our official Telegram channel before accessing the automation platform.",
            reply_markup=get_channel_join_keyboard()
        )
        return

    if not is_user_pass_valid(chat_id):
        user_sessions[chat_id]["step"] = "WAITING_PASSKEY_AUTH"
        bot.send_message(
            chat_id,
            f"<b>{to_bold('24-HOUR PASSKEY REQUIRED')}</b>\n\n"
            f"An active 24-hour passkey is required to access the engine.\n"
            f"Please enter your key below or contact the administrator.",
            reply_markup=get_passkey_keyboard()
        )
        return

    user_sessions[chat_id]["step"] = "CHOOSE_SITE"
    bot.send_message(
        chat_id,
        get_text("welcome") + "\n\n" + get_text("choose_site"),
        reply_markup=get_six_platform_keyboard()
    )

@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_sessions.get(chat_id, {})

    if u.get("input_mode") == "WAITING_PASSKEY":
        safe_delete_message(chat_id, message.message_id)
        if u.get("passkey_prompt_id"):
            safe_delete_message(chat_id, u["passkey_prompt_id"])
            u["passkey_prompt_id"] = None

        now = time.time()
        key_data = firebase_sync_http(f"passkeys/{text}", "GET")
        is_valid = False

        if key_data and isinstance(key_data, dict):
            if key_data.get("status") == "ACTIVE" and key_data.get("expires_at", 0) > now:
                is_valid = True
                firebase_sync_http(f"passkeys/{text}", "PATCH", {"used_by": chat_id, "used_at": now})
        elif chat_id == SUPER_ADMIN_ID:
            is_valid = True

        if is_valid:
            u["pass_expiry"] = now + 86400
            u["input_mode"] = None
            u["step"] = "CHOOSE_SITE"
            bot.send_message(
                chat_id,
                f"<b>{to_bold('PASSKEY ACTIVATED (24 HOURS)')}</b>\n\n"
                f"Your passkey was validated successfully. Please select your target platform:",
                reply_markup=get_six_platform_keyboard()
            )
        else:
            pm = bot.send_message(
                chat_id,
                f"<b>{to_bold('INVALID PASSKEY')}</b>\n\n"
                f"The key provided is invalid or expired. Please check your key or contact the owner:"
            )
            u["passkey_prompt_id"] = pm.message_id
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
                    f"<b>{to_bold('ACCOUNT AUTHENTICATION')}</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Account: <code>{masked}</code> (Recorded)\n\n"
                    f"Click <b>INPUT PASSWORD</b> to provide your account password:"
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

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING AUTOMATION WORKER</b>")
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

            wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(wingo_snap)
            safe_tab_execute(sid, _shot)

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET SYNCHRONIZED')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Configured Target: <code>৳ {val:.2f}</code>\n\n"
                f"Target updated. Press <b>LAUNCH ENGINE</b> to begin trading:"
            )
            display_or_replace_photo(
                chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid)
            )
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid numeric value (e.g. 500):")
            sess["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            sess["total_steps"] = steps_val
            sess["input_mode"] = None

            wingo_snap = os.path.join(PROFILES_BASE_DIR, f"wingo_{sid}.png")
            def _shot(drv):
                drv.save_screenshot(wingo_snap)
            safe_tab_execute(sid, _shot)

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET SYNCHRONIZED')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Martingale Steps: <b>{steps_val}</b>\n\n"
                f"Configuration updated. Press <b>LAUNCH ENGINE</b> to run:"
            )
            display_or_replace_photo(
                chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid)
            )
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a positive whole integer (e.g. 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==========================================
# 21. Distributed Cluster Handlers Hooking
# ==========================================
_original_handle_callbacks = handle_callbacks
def distributed_handle_callbacks(call):
    data = call.data or ""
    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    if not sid or action in ["adm", "adm_usr", "pass_act", "pass_del", "check_channel_joined", "btn_enter_pass"] or action in PLATFORMS:
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

    if u.get("input_mode") == "WAITING_PASSKEY":
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
# 22. Telegram Polling Failover Coordinator
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
        print(f"[*] [{to_bold(NODE_ID)}] Starting Telegram Polling as PRIMARY CLUSTER MASTER...")
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
                print(f"[*] Primary Master heartbeat timed out (>10s). Promoting HOT-STANDBY to MASTER...")
                claim_res = cluster_claim_leadership()
                if claim_res == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break
    else:
        print(f"[*] [{to_bold(NODE_ID)}] WORKER Active: Telegram polling bypassed to prevent 409 Conflict.")
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
                print(f"[*] Master & Standby timeout detected. Attempting election promotion...")
                new_role = cluster_claim_leadership()
                if new_role == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break

bot.infinity_polling = cluster_managed_infinity_polling

# ==========================================
# 23. Main Entrypoint
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('STARTING DISTRIBUTED TRADING CLUSTER NODE')} [{NODE_ID}]...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
