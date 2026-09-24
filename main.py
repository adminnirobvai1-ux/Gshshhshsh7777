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
# 1. Automatic Package Installer & Resilient Importer
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Installing required package: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])
        except Exception as e:
            print(f"[!] Pip install error for {package_name}: {e}")

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
# 2. Mathematical Bold Unicode & Text Decorators
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
# 3. Aggressive Zombie Process & Memory Hygiene
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
        gone, still_alive = psutil.wait_procs(children, timeout=2.0)
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
        parent.terminate()
        parent.wait(timeout=2.0)
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
                        for s in list(active_sessions.values()):
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
# 4. Configuration & Multi-Platform Registry
# ==========================================
TOKEN = "8808949150:AAFwAIsPbB2XZdKdizPIc8k42yVKvQJkH-s"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

HEADLESS_MODE = os.environ.get("HEADLESS", "false").lower() == "true"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}
active_sessions = {}

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"
SUPER_ADMIN_ID = 8707571669
OWNER_USERNAME = "@MD_NAYEEM_DRX_TM"

FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
NODE_ID = f"node_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"

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

URL_AMARCLUB_LOGIN = PLATFORMS["site_amarclub"]["login"]
URL_DKWIN_LOGIN = PLATFORMS["site_dkwin"]["login"]
URL_AMARCLUB_WINGO = PLATFORMS["site_amarclub"]["wingo"]
URL_DKWIN_WINGO = PLATFORMS["site_dkwin"]["wingo"]

# ==========================================
# 5. Network Speed & Firebase Synchronizer
# ==========================================
def measure_network_latency(url: str, timeout: float = 3.5) -> float:
    try:
        start_ts = time.time()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response.read(256)
        return round((time.time() - start_ts) * 1000, 2)
    except Exception:
        return 9999.0

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

# ==========================================
# 6. Hardened Browser Session Isolation
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
        options.add_argument("--headless")

    options.page_load_strategy = 'eager'
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 1024)
    options.set_preference("javascript.options.mem.max", 32768)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)
    options.set_preference("dom.disable_open_during_load", True)
    options.set_preference("dom.popup_maximum", 0)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(15)
    driver.implicitly_wait(3)
    driver.set_window_size(412, 915)

    try:
        driver.get(target_url)
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
# 7. Telegram Media & Clean Screen Replacement
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
# 8. Upgraded JavaScript Automation & Sweeper
# ==========================================
# Super Aggressive Modal & Announcement Dismisser
MODAL_AUTO_DISMISSER_JS = """
(function(){
    const sweepModals = () => {
        const directSelectors = [
            '.van-dialog__confirm', '.dialog-confirm', '.van-button--primary',
            '.van-popup__close-icon', '.van-overlay', '.dialog-close', '.close-btn',
            'button[class*="close" i]', 'button[class*="confirm" i]', 'div[class*="close" i]',
            '.announcement-box .close', '.modal-mask', '.reward-receive-btn',
            'button.van-dialog__cancel'
        ];
        directSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                if (el && el.offsetParent !== null && !el.closest('#sys-core-fin')) {
                    try { 
                        ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
                            el.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window}));
                        });
                        el.click(); 
                    } catch(e){}
                }
            });
        });

        // Scan button and span text for promotional banners seen in video (Confirm, Receive, Got it, etc.)
        const clickableNodes = document.querySelectorAll('button, div[role="button"], span, p, a');
        clickableNodes.forEach(node => {
            if (node && node.offsetParent !== null && !node.closest('#sys-core-fin')) {
                const txt = (node.innerText || '').trim().toLowerCase();
                if (txt === 'confirm' || txt === 'receive' || txt === 'got it' || txt === '確定' || txt === '领取' || txt === 'close') {
                    if (node.closest('.van-dialog') || node.closest('.van-popup') || node.closest('[class*="dialog"]') || node.closest('[class*="modal"]') || node.closest('[class*="notice"]') || node.closest('[class*="reward"]')) {
                        try { node.click(); } catch(e){}
                    }
                }
            }
        });

        // Cleanup stale overlays
        document.querySelectorAll('.van-overlay').forEach(overlay => {
            if (overlay && overlay.offsetParent !== null) {
                try { overlay.remove(); } catch(e){}
            }
        });
    };

    sweepModals();
    if (!window.__SWEEPER_INTERVAL) {
        window.__SWEEPER_INTERVAL = setInterval(sweepModals, 800);
    }
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
    window.location.hash = '#/login';
}

const dismissInitial = () => {
    document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm" i], .van-button--primary, .van-popup__close-icon').forEach(btn => {
        try { btn.click(); } catch(e){}
    });
};
dismissInitial();

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
        ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
            try { elL.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window})); } catch(e){}
        });
        elL.click();
    }, 600);
}, 600);

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
        const confirmBtn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm" i], .van-button--danger, .van-button--primary, button');
        if (confirmBtn) {
            try { confirmBtn.click(); } catch(e){}
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed device prompt" };
        }
    }
}

// Promotional banner auto-dismissal
document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm" i], button[class*="close" i], .van-popup__close-icon').forEach(b => {
    try { b.click(); } catch(e){}
});

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

# Adaptive Persistent Navigation & Fallback DOM Click Engine
WINGO_PERSISTENT_NAV_JS = """
const targetUrl = arguments[0];

(function(){
    // Step A: Sweep all dialogs and banners
    document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm" i], button[class*="close" i], .van-popup__close-icon, .reward-receive-btn').forEach(b => {
        try { b.click(); } catch(e){}
    });

    const currentHash = window.location.hash || '';
    const currentHref = window.location.href || '';
    const bodyTxt = document.body ? document.body.innerText : '';

    if (currentHash.includes('WinGo') || currentHref.includes('WinGo') || bodyTxt.includes('Time remaining') || bodyTxt.includes('30S')) {
        return "ALREADY_VERIFIED";
    }

    // Step B: Direct router redirect
    try {
        if (!window.location.href.includes('WinGo')) {
            window.location.href = targetUrl;
        }
    } catch(e){}

    // Step C: Fallback DOM Selector click
    const s = [
        'img[src*="wingo" i]', 'img[alt*="wingo" i]',
        'body > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(7) > div:nth-of-type(3) > div > div:nth-of-type(2) > div > div > div > img',
        'body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img',
        'body > div > div:nth-of-type(2) > div:nth-of-type(5) > div:nth-of-type(2) > div > div'
    ];
    for (let i = 0; i < s.length; i++) {
        let el = document.querySelector(s[i]);
        if (el && el.offsetParent !== null) {
            ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
                try { el.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window})); } catch(err){}
            });
            try { el.click(); } catch(err){}
            return "CLICKED_SELECTOR";
        }
    }

    return "NAV_INJECTED";
})();
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close" i], .van-dialog button').forEach(btn => {
    try { btn.click(); } catch(e){}
});

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

# ==============================================================================
# UPGRADED GHOST AUTOMATION EXECUTION ENGINE (WINGO_CORE_JS)
# ==============================================================================
WINGO_CORE_JS = r"""
const autoTargetProfit = arguments[0];
const autoTotalSteps = arguments[1];

(function(){
    let ghostContainer = document.getElementById('sys-core-fin');
    if (!ghostContainer) {
        ghostContainer = document.createElement('div');
        ghostContainer.id = 'sys-core-fin';
        ghostContainer.setAttribute('style', 'display: none !important; opacity: 0 !important; pointer-events: none !important; position: fixed !important; top: -9999px !important; left: -9999px !important; width: 0 !important; height: 0 !important; z-index: -9999 !important; overflow: hidden !important;');
        document.body.appendChild(ghostContainer);
    }

    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.totalSteps = Math.max(1, parseInt(autoTotalSteps) || 7);
        if (autoTargetProfit && autoTargetProfit > 0) {
            let liveBal = (typeof chkBal === 'function') ? chkBal() : window.__WINGO_ST.curBal;
            window.__WINGO_ST.tgtAmt = (autoTargetProfit <= liveBal && liveBal > 0) ? (liveBal + autoTargetProfit) : autoTargetProfit;
        }
        return "ALREADY_RUNNING_UPDATED";
    }

    if (window.__WINGO_ST && window.__WINGO_ST.autoInt) {
        clearInterval(window.__WINGO_ST.autoInt);
    }

    const st = {
        isRun: true,
        startBal: 0,
        tgtAmt: 0,
        curBal: 0,
        autoInt: null,
        isTrd: false,
        stpIdx: 0,
        dynSeq: [],
        totalSteps: Math.max(1, parseInt(autoTotalSteps) || 7),
        tradesDone: 0,
        lastPred: null,
        lastPeriod: null,
        w: 0,
        l: 0,
        cur_w_streak: 0,
        cur_l_streak: 0,
        max_w_streak: 0,
        max_l_streak: 0
    };
    window.__WINGO_ST = st;

    function chkBal() {
        try {
            let els = document.querySelectorAll('*');
            for (let i = 0; i < els.length; i++) {
                let txt = els[i].innerText || '';
                if (txt.includes('Wallet balance') || txt.includes('Balance')) {
                    let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
                    let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                    if (match) {
                        st.curBal = parseFloat(match[1].replace(/,/g, ''));
                        return st.curBal;
                    }
                }
            }
            for (let i = 0; i < els.length; i++) {
                let txt = els[i].innerText || '';
                if (txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)) {
                    st.curBal = parseFloat(txt.replace(/[^\d.]/g, ''));
                    return st.curBal;
                }
            }
        } catch(e) {}
        return st.curBal || 0;
    }

    function calculateMartingaleSequence(balance, steps) {
        steps = Math.max(1, parseInt(steps) || 7);
        let b = Math.max(1, Math.floor(balance) || 1);
        let units = Math.pow(2, steps) - 1;
        let s1 = Math.floor(b / units);
        if (s1 < 1) s1 = 1;

        let seq = [];
        let cur = s1;
        for (let k = 0; k < steps; k++) {
            seq.push(cur);
            cur = cur * 2;
        }
        return seq.length > 0 ? seq : [1];
    }

    function getNextLivePeriod(str) {
        let chars = String(str).split('');
        for (let i = chars.length - 1; i >= 0; i--) {
            if (chars[i] !== '9') {
                chars[i] = String.fromCharCode(chars[i].charCodeAt(0) + 1);
                return chars.join('');
            }
            chars[i] = '0';
        }
        return '1' + chars.join('');
    }

    function fireSyntheticEvents(el) {
        if (!el) return;
        ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
            try {
                el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            } catch(e) {}
        });
        if (typeof el.click === 'function') {
            try { el.click(); } catch(e) {}
        }
    }

    function executeBetTrade(pred, amt, cb) {
        try {
            let target = String(pred).trim().toUpperCase();
            let btn = null;

            if (target === 'BIG') {
                btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
            } else if (target === 'SMALL') {
                btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
            } else if (target === 'GREEN') {
                btn = document.querySelector('.bet-btn-green, button[class*="green" i]');
            } else if (target === 'RED') {
                btn = document.querySelector('.bet-btn-red, button[class*="red" i]');
            } else if (target === 'VIOLET') {
                btn = document.querySelector('.bet-btn-violet, button[class*="violet" i]');
            }

            if (!btn) {
                let candidateElements = document.querySelectorAll('button, div[role="button"], span');
                for (let i = 0; i < candidateElements.length; i++) {
                    let el = candidateElements[i];
                    let t = (el.innerText || '').trim().toUpperCase();
                    if (t === target && el.offsetParent !== null && el.children.length === 0) {
                        btn = el;
                        break;
                    }
                }
            }

            if (!btn) {
                if (cb) cb(false);
                return;
            }

            fireSyntheticEvents(btn);

            let attempts = 0;
            let valInterval = setInterval(() => {
                attempts++;
                let inpEl = document.querySelector("input.van-field__control, input[type='number'], .van-stepper__input");
                if (inpEl || attempts > 20) {
                    clearInterval(valInterval);
                    if (inpEl) {
                        try {
                            inpEl.focus();
                            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
                            if (setter) {
                                setter.call(inpEl, amt);
                            } else {
                                inpEl.value = amt;
                            }
                            inpEl.dispatchEvent(new Event('input', { bubbles: true }));
                            inpEl.dispatchEvent(new Event('change', { bubbles: true }));
                        } catch(err) {}

                        setTimeout(() => {
                            let confirmBtn = document.querySelector('button.bet-amount, button[class*="bet-amount" i], .Betting__C-foot-total');
                            if (!confirmBtn) {
                                let buttons = document.querySelectorAll('button');
                                for (let b of buttons) {
                                    let txt = (b.innerText || '').toLowerCase();
                                    if ((txt.includes('total amount') || txt.includes('confirm') || txt.includes('bet')) && b.offsetParent !== null) {
                                        confirmBtn = b;
                                        break;
                                    }
                                }
                            }
                            if (confirmBtn) {
                                fireSyntheticEvents(confirmBtn);
                                setTimeout(() => { if (cb) cb(true); }, 1500);
                            } else {
                                if (cb) cb(false);
                            }
                        }, 600);
                    } else {
                        if (cb) cb(false);
                    }
                }
            }, 150);
        } catch(e) {
            if (cb) cb(false);
        }
    }

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    let targetProfitVal = parseFloat(autoTargetProfit) || 0;
    st.tgtAmt = (targetProfitVal <= initialBal && initialBal > 0) ? (initialBal + targetProfitVal) : targetProfitVal;
    st.dynSeq = calculateMartingaleSequence(initialBal, st.totalSteps);
    st.stpIdx = 0;
    sessionStorage.removeItem('drx_sig');

    let isFetchingApi = false;

    const ghostExecutionLoop = async () => {
        if (!st.isRun || st.isTrd || isFetchingApi) return;
        isFetchingApi = true;

        try {
            let currentBal = chkBal();
            if (currentBal >= st.tgtAmt && st.tgtAmt > 0 && currentBal > 0) {
                st.isRun = false;
                st.isTrd = false;
                if (st.autoInt) clearInterval(st.autoInt);
                isFetchingApi = false;
                return;
            }

            let ts = Math.floor(Date.now() / 1000);
            let dataArray = null;
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 3500);
                let response = await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts=" + ts, { signal: controller.signal });
                clearTimeout(timeoutId);
                dataArray = await response.json();
            } catch(e) {
                isFetchingApi = false;
                return;
            }

            if (dataArray && dataArray.length > 0) {
                let activeLogic = dataArray[0];
                let history = activeLogic.history;
                if (!history || history.length === 0) {
                    isFetchingApi = false;
                    return;
                }

                let cSig = getNextLivePeriod(String(history[0].pid));
                let sSig = sessionStorage.getItem('drx_sig');

                if (cSig !== sSig) {
                    sessionStorage.setItem('drx_sig', cSig);

                    if (st.lastPred && st.lastPeriod) {
                        let actualOutcome = String(history[0].actual || '').trim().toUpperCase();
                        if (actualOutcome === 'BIG' || actualOutcome === 'SMALL') {
                            if (st.lastPred === actualOutcome) {
                                st.w++;
                                st.cur_w_streak++;
                                st.cur_l_streak = 0;
                                if (st.cur_w_streak > st.max_w_streak) st.max_w_streak = st.cur_w_streak;
                                st.stpIdx = 0;
                            } else {
                                st.l++;
                                st.cur_l_streak++;
                                st.cur_w_streak = 0;
                                if (st.cur_l_streak > st.max_l_streak) st.max_l_streak = st.cur_l_streak;
                                st.stpIdx = Math.min(st.stpIdx + 1, st.dynSeq.length - 1);
                            }
                        }
                    }

                    st.lastPeriod = cSig;
                    st.isTrd = true;

                    let liveB = chkBal();
                    if (liveB >= st.tgtAmt && st.tgtAmt > 0 && liveB > 0) {
                        st.isRun = false;
                        st.isTrd = false;
                        if (st.autoInt) clearInterval(st.autoInt);
                        isFetchingApi = false;
                        return;
                    }

                    if (st.stpIdx >= st.dynSeq.length) st.stpIdx = 0;
                    let targetStake = st.dynSeq[st.stpIdx] || 1;

                    if (liveB < targetStake) {
                        st.stpIdx = 0;
                        st.isTrd = false;
                        isFetchingApi = false;
                        return;
                    }

                    let prediction = String(activeLogic.pred || 'BIG').trim().toUpperCase();
                    st.lastPred = prediction;

                    if (prediction === 'SKIP') {
                        setTimeout(() => { st.isTrd = false; }, 1000);
                    } else {
                        executeBetTrade(prediction, targetStake, (success) => {
                            if (success) {
                                st.tradesDone++;
                            }
                            setTimeout(() => { st.isTrd = false; }, 1000);
                        });
                    }
                }
            }
        } catch(e) {
            st.isTrd = false;
        }
        isFetchingApi = false;
    };

    let tradeStartTs = 0;
    setInterval(() => {
        if (st.isTrd) {
            if (!tradeStartTs) tradeStartTs = Date.now();
            else if (Date.now() - tradeStartTs > 15000) {
                st.isTrd = false;
                isFetchingApi = false;
                tradeStartTs = 0;
            }
        } else {
            tradeStartTs = 0;
        }
    }, 3000);

    st.autoInt = setInterval(ghostExecutionLoop, 1000);
    return "GHOST_TRADING_INITIATED";
})();
"""

# ==========================================
# 9. Interactive English Keyboard Matrices
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

def get_passkey_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"{to_bold('GENERATE NEW 24H PASSKEY')}", callback_data="pk_gen_new"),
        InlineKeyboardButton(f"{to_bold('VIEW ACTIVE PASSKEYS')}", callback_data="pk_list_active"),
        InlineKeyboardButton(f"{to_bold('REVOKE PASSKEY')}", callback_data="pk_prompt_revoke")
    )
    return markup

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
        InlineKeyboardButton(f"{to_bold('TASK MONITOR')}", callback_data="adm_tasks"),
        InlineKeyboardButton(f"{to_bold('REFRESH')}", callback_data="adm_refresh")
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
# 11. Authentication & Clean Login Flow
# ==========================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE ENGINE</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Allocating isolated profile...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>▰▰▰▱▱▱▱▱▱▱ 35% Establishing connection instance...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>▰▰▰▰▰▰▱▱▱▱ 65% Submitting credentials securely...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>▰▰▰▰▰▰▰▰▰▰ 100% Authentication successful!</code>"
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

    # Extra sweep to ensure no promotion modal covers the login screen
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    time.sleep(1.2)

    # MILESTONE 1 SCREENSHOT: Captured strictly upon successful login
    login_snap = os.path.join(PROFILES_BASE_DIR, f"login_done_{sid}.png")
    safe_tab_execute(sid, lambda drv: drv.save_screenshot(login_snap))

    masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
    caption = (
        f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
        f"Platform: <b>{site_name}</b>\n"
        f"Account: <code>{masked_phone}</code>\n\n"
        f"Click <b>START</b> below to configure and run trading parameters:"
    )

    display_or_replace_photo(
        chat_id, sid,
        login_snap,
        caption,
        get_start_screen_keyboard(sid)
    )

# ==========================================
# 12. Persistent WinGo 30S Auto-Retry Loop
# ==========================================
def prepare_wingo_parameters(chat_id, sid):
    sess = active_sessions.get(sid, {})
    site_name = sess.get("site_name", "Amar Club")
    wingo_url = sess.get("wingo_url") or (URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO)

    # Persistent loop: Sweep modals, redirect via Vue router or click card, and verify
    verified = False
    max_nav_cycles = 15

    for cycle in range(max_nav_cycles):
        # Step A, B & C: Sweep modals and trigger entrance
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
        safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_PERSISTENT_NAV_JS, wingo_url))
        time.sleep(2.0)

        # Step D: Verification check
        is_ready = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS))
        if is_ready:
            verified = True
            break
        time.sleep(1.0)

    if not verified:
        # Final direct force fallback
        safe_tab_execute(sid, lambda drv: drv.get(wingo_url))
        time.sleep(3.0)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    current_bal = 0.0
    for _ in range(15):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.4)

    sess["current_balance"] = current_bal

    # Sweep once more before capturing MILESTONE 2 SCREENSHOT
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    time.sleep(1.0)

    # MILESTONE 2 SCREENSHOT: Captured strictly upon successful arrival on WinGo screen
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
# 13. Trading Monitor & Background Watchdog
# ==========================================
def record_task_status(chat_id, sid, status, start_bal, cur_bal, target_amt, wins, losses, site_name):
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
        "updated_at": time.time()
    }
    firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

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
                        step: (window.__WINGO_ST.stpIdx || 0) + 1,
                        tradesDone: window.__WINGO_ST.tradesDone || 0
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
            start_b = sess.get("start_bal", 0)
            is_run = js_data.get("isRun", False)

            record_task_status(
                chat_id, sid, "RUNNING" if is_run else "PAUSED",
                start_b, sess["cur_bal"], tgt_amt,
                sess["wins"], sess["losses"],
                sess.get("site_name", "Amar Club")
            )

            if not is_run or (sess["cur_bal"] >= tgt_amt and tgt_amt > 0 and sess["cur_bal"] > 0):
                if sess["cur_bal"] >= tgt_amt and tgt_amt > 0 and sess["cur_bal"] > 0:
                    sess["is_trading"] = False
                    profit = sess["cur_bal"] - start_b

                    record_task_status(
                        chat_id, sid, "COMPLETED",
                        start_b, sess["cur_bal"], tgt_amt,
                        sess["wins"], sess["losses"],
                        sess.get("site_name", "Amar Club")
                    )

                    msg = (
                        f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                        f"Your target profit has been fulfilled smoothly.\n\n"
                        f"Starting Balance: <code>৳ {start_b:.2f}</code>\n"
                        f"Final Balance: <code>৳ {sess['cur_bal']:.2f}</code>\n"
                        f"Net Profit: <code>+৳ {profit:.2f}</code>\n"
                        f"Total Wins: <b>{sess['wins']}</b> | Losses: <b>{sess['losses']}</b>"
                    )
                    bot.send_message(chat_id, msg, parse_mode="HTML")
                    break
                elif not is_run:
                    sess["is_trading"] = False
                    break

        time.sleep(4.0)

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
# 14. Telegram Command Handlers
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
        f"Cluster Role: <b>{'PRIMARY MASTER' if IS_CLUSTER_MASTER else 'STANDBY / WORKER'}</b>\n\n"
        f"Select a management module from the options below:"
    )
    bot.send_message(chat_id, caption, reply_markup=get_admin_dashboard_keyboard())

# ==========================================
# 15. Telegram Callback Routing
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

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
        pm = bot.send_message(chat_id, f"<b>{to_bold('PASSKEY AUTHENTICATION')}</b>\n\nPlease submit your 24-hour passkey:")
        user_sessions[chat_id]["passkey_prompt_id"] = pm.message_id
        return

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

    elif action in ["adm_refresh", "adm_home"]:
        if chat_id != SUPER_ADMIN_ID: return
        caption = (
            f"<b>{to_bold('ADMIN CLUSTER CONTROL PANEL')}</b>\n\n"
            f"Cluster ID: <code>{NODE_ID}</code>\n"
            f"Role: <b>{'PRIMARY MASTER' if IS_CLUSTER_MASTER else 'STANDBY / WORKER'}</b>\n\n"
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
                lat = tval.get("latency_ms", "N/A")
                lines.append(f"• <code>{tid}</code> | Status: <b>{st}</b> (Ping: {lat}ms | HB: {hb_diff}s ago)")

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
        bot.answer_callback_query(call.id, "Testing platform latency...")
        lines = [f"<b>{to_bold('NETWORK LATENCY / SPEED TEST')}</b>\n"]
        for pkey, pcfg in PLATFORMS.items():
            lat = measure_network_latency(pcfg["login"])
            lines.append(f"• {pcfg['name']}: <b>{lat} ms</b>" if lat < 9000 else f"• {pcfg['name']}: <b>TIMEOUT (>3500ms)</b>")

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
            "total_steps": 7,
            "is_trading": False,
            "created_at": time.time(),
            "anim_tick": 0,
            "lock": threading.RLock()
        }
        user_sessions.setdefault(chat_id, {})["active_sid"] = sid

        caption = (
            f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
            f"Platform: <b>{site_name}</b>\n\n"
            f"Please click below to submit your account number and password. "
            f"Credentials are encrypted in memory and deleted after verification."
        )

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            caption,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

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
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('TARGET PROFIT')}</b>\nLive Balance: <code>৳ {cur_bal:.2f}</code>\nEnter profit amount (e.g. <code>500</code>):")
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('MARTINGALE STEPS')}</b>\nEnter backup step count (e.g. <code>7</code> or <code>10</code>):")
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and sid in active_sessions:
        sess = active_sessions[sid]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "Please set a target profit amount first!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Starting background ghost automation...")
        sess["is_trading"] = True
        safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"]))

        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        dashboard_caption = (
            f"<b>{to_bold('24/7 GHOST ENGINE ACTIVE')}</b>\n\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Starting Balance: <code>৳ {cur_b:.2f}</code>\n"
            f"Target Balance: <code>৳ {target_total:.2f}</code>\n"
            f"Total Steps: <b>{sess['total_steps']}</b>\n\n"
            f"<b>LIVE STATUS</b>: Martingale engine running in ghost background mode."
        )

        last_msg_id = sess.get("live_photo_message_id")
        if last_msg_id:
            try:
                bot.edit_message_caption(
                    caption=dashboard_caption,
                    chat_id=chat_id,
                    message_id=last_msg_id,
                    reply_markup=get_trading_control_keyboard(sid)
                )
            except Exception:
                bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(sid))
        else:
            bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(sid))

        threading.Thread(target=monitor_trading_progress, args=(chat_id, sid), daemon=True).start()

    elif action == "shot" and sid in active_sessions:
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "Capturing live footage...")
        temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
        safe_tab_execute(sid, lambda drv: drv.save_screenshot(temp_shot))

        if os.path.exists(temp_shot):
            cur_b = sess.get("cur_bal", sess.get("current_balance", 0.0))
            t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
            caption = (
                f"<b>{to_bold('24/7 GHOST ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {sess.get('start_bal', 0.0):.2f}</code>\n"
                f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
                f"Time: <code>{time.strftime('%H:%M:%S')}</code>\n\n"
                f"<b>LIVE STATUS</b>: Martingale trading execution is continuous."
            )
            display_or_replace_photo(chat_id, sid, temp_shot, caption, get_trading_control_keyboard(sid))

    elif action == "bal" and sid in active_sessions:
        b = safe_tab_execute(sid, lambda drv: drv.execute_script("return (window.__WINGO_ST && window.__WINGO_ST.curBal) ? window.__WINGO_ST.curBal : null;"))
        if b is None or float(b) == 0:
            b = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if b is not None:
            bot.answer_callback_query(call.id, f"Live Balance: ৳ {float(b):.2f}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Loading balance...", show_alert=True)

    elif action == "stats" and sid in active_sessions:
        def _stat(drv):
            return drv.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        step: (window.__WINGO_ST.stpIdx || 0) + 1,
                        totalSteps: window.__WINGO_ST.totalSteps || 7,
                        curBal: window.__WINGO_ST.curBal || 0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                        tradesDone: window.__WINGO_ST.tradesDone || 0,
                        cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                        cur_l_streak: window.__WINGO_ST.cur_l_streak || 0,
                        max_w_streak: window.__WINGO_ST.max_w_streak || 0,
                        max_l_streak: window.__WINGO_ST.max_l_streak || 0
                    };
                }
                return null;
            """)
        data_rep = safe_tab_execute(sid, _stat)
        if data_rep:
            stat_txt = (
                f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                f"Balance: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                f"Target: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                f"Current Martingale Step: <b>Step {data_rep['step']} / {data_rep['totalSteps']}</b>\n"
                f"Wins: <b>{data_rep['w']}</b> | Losses: <b>{data_rep['l']}</b>\n"
                f"Win Streak: <b>{data_rep['cur_w_streak']}</b> (Max: {data_rep['max_w_streak']})\n"
                f"Loss Streak: <b>{data_rep['cur_l_streak']}</b> (Max: {data_rep['max_l_streak']})\n"
                f"Total Trades: <b>{data_rep['tradesDone']}</b>"
            )
            bot.send_message(chat_id, stat_txt, parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, "Syncing engine data...", show_alert=True)

    elif action == "stop" and sid in active_sessions:
        sess = active_sessions[sid]
        safe_tab_execute(sid, lambda drv: drv.execute_script("if(window.__WINGO_ST){ window.__WINGO_ST.isRun = false; if(window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt); }"))
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "Trading paused", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nAutomation paused cleanly.")

    elif action == "cancel" and sid in active_sessions:
        bot.answer_callback_query(call.id, "Session terminated")
        close_session_tab(sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, f"<b>{to_bold('SESSION TERMINATED')}</b>\nSend /start to begin a new session.")

# ==========================================
# 16. Text Input & Credentials Handler
# ==========================================
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
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"Parameters updated. Click <b>START</b> to initiate trading:"
            )

            last_msg_id = sess.get("live_photo_message_id")
            if last_msg_id:
                try:
                    bot.edit_message_caption(
                        caption=config_caption,
                        chat_id=chat_id,
                        message_id=last_msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
            else:
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
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"Parameters updated. Click <b>START</b> to initiate trading:"
            )

            last_msg_id = sess.get("live_photo_message_id")
            if last_msg_id:
                try:
                    bot.edit_message_caption(
                        caption=config_caption,
                        chat_id=chat_id,
                        message_id=last_msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
            else:
                bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid integer (e.g. 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# =======================================================
# 17. Dynamic Fastest-Node Dispatch Engine (Lowest Ping)
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
        "latency_ms": measure_network_latency(URL_AMARCLUB_LOGIN),
        "registered_at": time.time()
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)

def cluster_node_heartbeat_loop():
    while CLUSTER_ACTIVE:
        try:
            status_val = "BUSY" if active_sessions else "FREE"
            lat = measure_network_latency(URL_AMARCLUB_LOGIN)
            hb_data = {
                "heartbeat": time.time(),
                "status": status_val,
                "load": len(active_sessions),
                "latency_ms": lat
            }
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", hb_data)
        except Exception:
            pass
        time.sleep(4.0)

def cluster_master_heartbeat_loop():
    while CLUSTER_ACTIVE and IS_CLUSTER_MASTER:
        try:
            m_data = {"heartbeat": time.time()}
            firebase_sync_http("cluster/active_master", "PATCH", m_data)
        except Exception:
            pass
        time.sleep(3.5)

def cluster_standby_heartbeat_loop():
    while CLUSTER_ACTIVE and IS_STANDBY_MASTER:
        try:
            s_data = {"heartbeat": time.time()}
            firebase_sync_http("cluster/standby_master", "PATCH", s_data)
        except Exception:
            pass
        time.sleep(3.5)

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
                                            if now - c_hb <= 10.0:
                                                candidates.append((cand_id, cand_val.get("load", 0), float(cand_val.get("latency_ms", 9999))))

                                    candidates.sort(key=lambda x: (x[2], x[1]))
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
        time.sleep(5.0)

# ===============================================================
# 18. Interception Wrappers with Lowest-Latency Smart Allocation
# ===============================================================
_original_close_session_tab = close_session_tab
def close_session_tab(session_id):
    _original_close_session_tab(session_id)
    try:
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
            "status": "FREE",
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
                # Must be strictly active (< 10 seconds)
                if now - hb <= 10.0:
                    candidates.append((tid, tinfo.get("load", 0), float(tinfo.get("latency_ms", 9999.0))))

    if candidates:
        # Sort primarily by lowest ping (latency_ms), then load
        candidates.sort(key=lambda x: (x[2], x[1]))
        free_target_node = candidates[0][0]
    else:
        free_target_node = NODE_ID

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
# 19. Failover Polling & Master Election
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
        print(f"[*] [{to_bold(NODE_ID)}] Starting Telegram Polling as PRIMARY MASTER...")
        _original_bot_infinity_polling(*args, **kwargs)
    elif role == "STANDBY":
        threading.Thread(target=cluster_standby_heartbeat_loop, daemon=True).start()
        print(f"[*] [{to_bold(NODE_ID)}] HOT-STANDBY active. Monitoring Primary...")
        while CLUSTER_ACTIVE:
            time.sleep(3.0)
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
                print(f"[*] Primary Master offline (>10s). Promoting to PRIMARY MASTER...")
                claim_res = cluster_claim_leadership()
                if claim_res == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break
    else:
        print(f"[*] [{to_bold(NODE_ID)}] WORKER Active: Telegram polling bypassed to prevent 409 Conflict.")
        while CLUSTER_ACTIVE:
            time.sleep(4.0)
            primary = firebase_sync_http("cluster/active_master", "GET")
            standby = firebase_sync_http("cluster/standby_master", "GET")
            now = time.time()

            claim_needed = False
            if not primary or not isinstance(primary, dict) or (now - float(primary.get("heartbeat", 0)) > 12.0):
                if not standby or not isinstance(standby, dict) or (now - float(standby.get("heartbeat", 0)) > 12.0):
                    claim_needed = True

            if claim_needed:
                print(f"[*] Master timeout detected. Attempting election promotion...")
                new_role = cluster_claim_leadership()
                if new_role == "MASTER":
                    threading.Thread(target=cluster_master_heartbeat_loop, daemon=True).start()
                    _original_bot_infinity_polling(*args, **kwargs)
                    break

bot.infinity_polling = cluster_managed_infinity_polling

# ==========================================
# 20. Main Execution Entrypoint
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT CLUSTER ENGINE ACTIVE')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
