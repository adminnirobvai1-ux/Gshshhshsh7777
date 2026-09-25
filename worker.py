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
import logging
import psutil

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [WORKER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("DRX_WORKER")

def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", package_name])

install_and_import("selenium")
install_and_import("psutil")

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
NODE_ID = f"worker_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"
PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() == "true"
active_sessions = {}
RUNNING = True

def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 4.0):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        raw_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=raw_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res = response.read()
            return json.loads(res.decode("utf-8")) if res else None
    except Exception:
        return None

def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try: child.kill()
            except Exception: pass
        parent.kill()
    except Exception:
        pass

def cleanup_zombie_browsers():
    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            pname = (proc.info['name'] or '').lower()
            if 'firefox' in pname or 'geckodriver' in pname:
                if proc.info['ppid'] == 1 or proc.info['ppid'] == current_pid:
                    is_active = False
                    for s in list(active_sessions.values()):
                        d = s.get('driver')
                        if d and hasattr(d, 'service') and d.service and d.service.process:
                            if d.service.process.pid == proc.info['pid']:
                                is_active = True
                                break
                    if not is_active:
                        try: proc.kill()
                        except Exception: pass
    except Exception:
        pass

MODAL_AUTO_DISMISSER_JS = """
(function(){
    const sweep = () => {
        document.querySelectorAll('.announcement-box, .dialog-box, .bonus-dialog, .van-popup, .van-dialog').forEach(d => {
            const btn = d.querySelector('button, .van-button, .van-dialog__confirm, div[role="button"]');
            if (btn) { try { btn.click(); } catch(e){} }
            try { d.remove(); } catch(e){}
        });
        document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, .van-popup__close-icon, .close-btn').forEach(el => {
            try { el.click(); } catch(e){}
        });
    };
    sweep();
    if (!window.__SWEEPER_INTERVAL) window.__SWEEPER_INTERVAL = setInterval(sweep, 500);
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];
if (!window.location.hash.includes('login')) window.location.hash = '#/login';

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]');
let elP = document.querySelector('input[type="password"]');
let elL = document.querySelector('button[type="submit"], body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');

if (!elN || !elP || !elL) return "NOT_READY";

const setVal = (el, val) => {
    el.focus();
    el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
};

setVal(elN, phone);
setTimeout(() => {
    setVal(elP, pass);
    setTimeout(() => {
        elL.click();
    }, 400);
}, 400);
return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const btn = dialog.querySelector('.van-dialog__confirm, button');
    if (btn) { try { btn.click(); } catch(e){} }
}
try {
    if (localStorage.getItem('token') || sessionStorage.getItem('token')) return { status: "SUCCESS" };
} catch(e){}
if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) return { status: "SUCCESS" };
const toast = document.querySelector('.van-toast');
if (toast && toast.innerText) {
    const t = toast.innerText.trim();
    if (t.includes('password') || t.includes('incorrect') || t.includes('frozen')) return { status: "ERROR", message: t };
}
return { status: "PENDING" };
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
    if (txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)) return parseFloat(txt.replace(/[^\d.]/g, ''));
}
return 0;
"""

WINGO_CORE_JS = r"""
const autoTargetProfit = arguments[0];
const autoTotalSteps = arguments[1];

(function(){
    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, parseInt(autoTotalSteps) || 5);
        return "ALREADY_RUNNING";
    }
    if (window.__WINGO_ST && window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt);

    const st = {
        isRun: true,
        tgtAmt: 0,
        startBal: 0,
        curBal: 0,
        autoInt: null,
        isTrd: false,
        stpIdx: 0,
        steps: Math.max(1, parseInt(autoTotalSteps) || 5),
        dynSeq: [],
        tradesDone: 0,
        lastPred: null,
        lastPeriod: null,
        w: 0,
        l: 0
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
                        st.curBal = Math.floor(parseFloat(match[1].replace(/,/g, '')));
                        return st.curBal;
                    }
                }
            }
        } catch(e) {}
        return st.curBal || 0;
    }

    function getRemainingSeconds() {
        try {
            let timeEl = document.querySelector('.time-box, [class*="time" i], .Time');
            if (timeEl) {
                let m = (timeEl.innerText || '').match(/(\d+)\s*:\s*(\d+)/);
                if (m) return (parseInt(m[1]) * 60) + parseInt(m[2]);
            }
        } catch(e){}
        return 30;
    }

    const calcSeq = (cBal, nSteps) => {
        let B = Math.floor(Number(cBal)) || 0;
        let n = parseInt(nSteps) || 5;
        let u = Math.pow(2, n) - 1;
        let s1 = Math.floor(B / u);
        if (s1 < 1) s1 = 1;
        let seq = [];
        let sum = 0;
        for (let k = 1; k < n; k++) {
            let sk = Math.floor(s1 * Math.pow(2, k - 1));
            seq.push(sk);
            sum += sk;
        }
        seq.push(Math.max(1, Math.floor(B - sum)));
        return seq;
    };

    const getNextLivePeriod = (str) => {
        let chars = String(str).split('');
        for (let i = chars.length - 1; i >= 0; i--) {
            if (chars[i] !== '9') {
                chars[i] = String.fromCharCode(chars[i].charCodeAt(0) + 1);
                return chars.join('');
            }
            chars[i] = '0';
        }
        return '1' + chars.join('');
    };

    const exeTrd = (pred, amt, cb) => {
        try {
            if (getRemainingSeconds() <= 5) { if(cb) cb(false); return; }
            let targetText = String(pred).toLowerCase().trim();
            let btn = null;
            if (targetText === 'big') btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
            else if (targetText === 'small') btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
            
            if (!btn) { if(cb) cb(false); return; }
            btn.click();

            let itv = setInterval(() => {
                let inp = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input");
                if (inp) {
                    clearInterval(itv);
                    inp.value = amt;
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                    setTimeout(() => {
                        let cfm = document.querySelector('button.bet-amount, .Betting__C-foot-total, .van-button--danger, .van-button--primary');
                        if (cfm) cfm.click();
                        setTimeout(() => { if(cb) cb(true); }, 1200);
                    }, 400);
                }
            }, 150);
        } catch(e) { if(cb) cb(false); }
    };

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    let targetProfitVal = parseFloat(autoTargetProfit) || 0;
    st.tgtAmt = (targetProfitVal <= initialBal && initialBal > 0) ? (initialBal + targetProfitVal) : targetProfitVal;
    st.dynSeq = calcSeq(initialBal > 0 ? initialBal : st.tgtAmt, st.steps);

    const apiLoop = async () => {
        if (!st.isRun || st.isTrd) return;
        chkBal();
        if (st.curBal >= st.tgtAmt && st.curBal > 0) {
            st.isRun = false;
            clearInterval(st.autoInt);
            return;
        }

        try {
            let res = await fetch("https://data-vip-247-hack.ai.studio/apipid.json?page=1&ts=" + Math.floor(Date.now()/1000));
            let data = await res.json();
            let activeLogic = Array.isArray(data) ? data[0] : (data.data ? data.data[0] : data);
            if (activeLogic && activeLogic.history && activeLogic.history[0]) {
                let cSig = getNextLivePeriod(String(activeLogic.history[0].pid));
                let sSig = sessionStorage.getItem('drx_sig');
                if (cSig && cSig !== sSig) {
                    st.isTrd = true;
                    let prediction = (activeLogic.pred || activeLogic.prediction || 'BIG').toUpperCase();
                    let tAmt = st.dynSeq[st.stpIdx] || 1;

                    if (prediction !== 'SKIP') {
                        exeTrd(prediction, tAmt, (suc) => {
                            if (suc) {
                                sessionStorage.setItem('drx_sig', cSig);
                                st.tradesDone++;
                            }
                            st.isTrd = false;
                        });
                    } else {
                        sessionStorage.setItem('drx_sig', cSig);
                        st.isTrd = false;
                    }
                }
            }
        } catch(e) { st.isTrd = false; }
    };

    st.autoInt = setInterval(apiLoop, 1000);
    return "STARTED";
})();
"""

def allocate_driver(sid, url):
    cleanup_zombie_browsers()
    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{sid}")
    shutil.rmtree(profile_dir, ignore_errors=True)
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    # मेमोरी खपत कम करने के लिए इमेज लोडिंग को ब्लॉक करना
    options.set_preference("permissions.default.image", 2)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(2)

    try:
        driver.get(url)
    except Exception as e:
        logger.warning(f"Timeout loading {url}: {e}")

    active_sessions[sid] = {"driver": driver, "lock": threading.RLock(), "is_trading": False}
    return driver

def close_session(sid):
    sess = active_sessions.pop(sid, None)
    if sess:
        driver = sess.get("driver")
        if driver:
            try: driver.quit()
            except Exception: pass
            try:
                if driver.service and driver.service.process:
                    kill_process_tree(driver.service.process.pid)
            except Exception: pass
    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{sid}")
    shutil.rmtree(profile_dir, ignore_errors=True)
    cleanup_zombie_browsers()
    gc.collect()

def run_worker_loop():
    logger.info(f"Node Registered: {NODE_ID}")
    while RUNNING:
        try:
            # 1. हार्टबीट अपडेट
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                "heartbeat": time.time(),
                "status": "BUSY" if active_sessions else "FREE",
                "load": len(active_sessions)
            })

            # 2. मैनेजर से असाइन किए गए टास्क चेक करना
            task = firebase_sync_http(f"terminals/{NODE_ID}/task", "GET")
            if task and isinstance(task, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/task", "DELETE")
                t_type = task.get("type")
                sid = task.get("session_id")

                if t_type == "LOGIN":
                    phone = task["phone"]
                    pwd = task["password"]
                    login_url = task["login_url"]
                    driver = allocate_driver(sid, login_url)
                    driver.execute_script(MODAL_AUTO_DISMISSER_JS)
                    driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, pwd)
                    
                    # स्टेटस मॉनिटर करना
                    time.sleep(3)
                    st = driver.execute_script(CHECK_LOGIN_STATUS_JS)
                    firebase_sync_http(f"task_results/{sid}", "PUT", {
                        "status": "LOGIN_DONE" if st.get("status") == "SUCCESS" else "FAILED",
                        "error": st.get("message", "")
                    })

                elif t_type == "NAV_WINGO":
                    sess = active_sessions.get(sid)
                    if sess:
                        wingo_url = task["wingo_url"]
                        sess["driver"].get(wingo_url)
                        time.sleep(2)
                        sess["driver"].execute_script(MODAL_AUTO_DISMISSER_JS)
                        bal = sess["driver"].execute_script(FETCH_BALANCE_JS)
                        firebase_sync_http(f"task_results/{sid}", "PUT", {
                            "status": "WINGO_READY",
                            "balance": float(bal or 0)
                        })

                elif t_type == "START_TRADE":
                    sess = active_sessions.get(sid)
                    if sess:
                        target = task.get("target_profit", 100)
                        steps = task.get("total_steps", 5)
                        sess["driver"].execute_script(WINGO_CORE_JS, target, steps)
                        sess["is_trading"] = True
                        firebase_sync_http(f"task_results/{sid}", "PUT", {"status": "TRADING_STARTED"})

                elif t_type == "STOP":
                    close_session(sid)
                    firebase_sync_http(f"task_results/{sid}", "PUT", {"status": "STOPPED"})

            # 3. ट्रेड मॉनिटरिंग
            for sid, s in list(active_sessions.items()):
                if s.get("is_trading") and s.get("driver"):
                    st_data = s["driver"].execute_script("""
                        if (window.__WINGO_ST) {
                            return {
                                curBal: window.__WINGO_ST.curBal || 0,
                                isRun: window.__WINGO_ST.isRun,
                                w: window.__WINGO_ST.w || 0,
                                l: window.__WINGO_ST.l || 0
                            };
                        }
                        return null;
                    """)
                    if st_data:
                        firebase_sync_http(f"live_stats/{sid}", "PUT", st_data)

        except Exception as e:
            logger.error(f"Loop error: {e}")
        time.sleep(2)

if __name__ == "__main__":
    run_worker_loop()
