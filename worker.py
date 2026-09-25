import os
import sys
import subprocess
import time
import threading
import shutil
import json
import urllib.request
import logging
import psutil

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')
logger = logging.getLogger("WORKER_ENGINE")

def install_and_import(package_name, import_name=None):
    if import_name is None: import_name = package_name
    try: __import__(import_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir", package_name])

install_and_import("selenium")
install_and_import("psutil")

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
PROFILES_BASE_DIR = os.path.expanduser("~/.ff_worker_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

active_drivers = {}

def firebase_sync_http(path: str, method: str = "GET", payload=None):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=raw_data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=4.0) as resp:
            content = resp.read()
            return json.loads(content.decode("utf-8")) if content else None
    except Exception: return None

# Zombie Process Cleaner
def cleanup_zombie_browsers():
    for proc in psutil.process_iter(['name']):
        try:
            name = (proc.info['name'] or '').lower()
            if 'geckodriver' in name:
                proc.kill()
        except Exception: pass

# Optimized Headless Browser Launch (Zero-Image Mode)
def create_driver(sid):
    cleanup_zombie_browsers()
    p_dir = os.path.join(PROFILES_BASE_DIR, f"p_{sid}")
    shutil.rmtree(p_dir, ignore_errors=True)
    os.makedirs(p_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.page_load_strategy = 'eager'
    options.add_argument("-profile")
    options.add_argument(p_dir)

    # ছবি ডাউনলোড পুরোপুরি ব্লক (র‍্যাম ও ব্যান্ডউইথ সেভ করতে)
    options.set_preference("permissions.default.image", 2)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("dom.disable_open_during_load", True)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(35)
    return driver

# স্ক্রিপ্ট ইনজেকশন স্ট্রিংস
MODAL_SWEEPER_JS = """
(function(){
    document.querySelectorAll('.announcement-box, .dialog-box, .bonus-dialog, .van-popup, .van-dialog').forEach(d => {
        try {
            let b = d.querySelector('button, .van-button, div[role="button"]');
            if (b) b.click();
            d.remove();
        } catch(e){}
    });
})();
"""

AUTO_LOGIN_JS = """
const phone = arguments[0];
const pass = arguments[1];
let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i]');
let elP = document.querySelector('input[type="password"]');
let elL = document.querySelector('button[type="submit"], .van-button--primary');

if (!elN || !elP || !elL) return "NOT_READY";
elN.focus(); elN.value = phone;
elN.dispatchEvent(new Event('input', { bubbles: true }));
elP.focus(); elP.value = pass;
elP.dispatchEvent(new Event('input', { bubbles: true }));
setTimeout(() => { elL.click(); }, 300);
return "SUCCESS";
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
return 0;
"""

WINGO_ENGINE_JS = r"""
const autoTargetProfit = arguments[0];
const autoTotalSteps = arguments[1];

(function(){
    if (window.__WINGO_ST && window.__WINGO_ST.isRun) return "ALREADY_RUNNING";
    const st = {
        isRun: true, tgtAmt: 0, curBal: 0, autoInt: null, isTrd: false,
        stpIdx: 0, steps: Math.max(1, parseInt(autoTotalSteps) || 5),
        dynSeq: [], tradesDone: 0, lastPred: null, lastPeriod: null,
        w: 0, l: 0
    };
    window.__WINGO_ST = st;

    function chkBal() {
        try {
            let els = document.querySelectorAll('*');
            for (let i = 0; i < els.length; i++) {
                let txt = els[i].innerText || '';
                if (txt.includes('Balance')) {
                    let p = els[i].parentNode ? els[i].parentNode.innerText : '';
                    let m = p.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                    if (m) { st.curBal = Math.floor(parseFloat(m[1].replace(/,/g, ''))); return st.curBal; }
                }
            }
        } catch(e){}
        return st.curBal || 0;
    }

    const calcSeq = (cBal, n) => {
        let B = Math.floor(Number(cBal)) || 0;
        let u = Math.pow(2, n) - 1;
        let s1 = Math.max(1, Math.floor(B / u));
        let seq = []; let sum = 0;
        for (let k = 1; k < n; k++) {
            let sk = Math.floor(s1 * Math.pow(2, k - 1));
            seq.push(sk); sum += sk;
        }
        seq.push(Math.max(1, Math.floor(B - sum)));
        return seq;
    };

    let iniBal = chkBal();
    st.curBal = iniBal;
    st.tgtAmt = iniBal + parseFloat(autoTargetProfit);
    st.dynSeq = calcSeq(iniBal, st.steps);

    const apiLoop = async () => {
        if (!st.isRun || st.isTrd) return;
        chkBal();
        if (st.curBal >= st.tgtAmt && st.tgtAmt > 0) {
            st.isRun = false;
            clearInterval(st.autoInt);
            return;
        }
        try {
            let ts = Math.floor(Date.now() / 1000);
            let res = await fetch("https://data-vip-247-hack.ai.studio/apipid.json?page=1&ts=" + ts);
            let data = await res.json();
            let logic = Array.isArray(data) ? data[0] : (data.data ? data.data[0] : data);
            if (logic && logic.history && logic.history[0]) {
                let cPid = String(logic.history[0].pid);
                if (cPid !== st.lastPeriod) {
                    if (st.lastPred) {
                        let actual = logic.history[0].actual === 'BIG' ? 'BIG' : 'SMALL';
                        if (st.lastPred === actual) { st.w++; st.stpIdx = 0; }
                        else { st.l++; st.stpIdx = Math.min(st.stpIdx + 1, st.dynSeq.length - 1); }
                    }
                    st.lastPeriod = cPid;
                    let pred = (logic.pred || 'BIG').toUpperCase();
                    st.lastPred = pred;
                    let amt = st.dynSeq[st.stpIdx] || 1;
                    
                    // প্লেস বেট টাস্ক
                    let bBtn = Array.from(document.querySelectorAll('button, div')).find(el => el.innerText && el.innerText.trim().toUpperCase() === pred);
                    if (bBtn) {
                        bBtn.click();
                        setTimeout(() => {
                            let inp = document.querySelector("input[type='number']");
                            if (inp) { inp.value = amt; inp.dispatchEvent(new Event('input', {bubbles:true})); }
                            setTimeout(() => {
                                let cBtn = document.querySelector('.van-button--danger, .van-button--primary');
                                if (cBtn) cBtn.click();
                                st.tradesDone++;
                            }, 500);
                        }, 500);
                    }
                }
            }
        } catch(e){}
    };
    st.autoInt = setInterval(apiLoop, 1500);
    return "OK";
})();
"""

def process_worker_task(task_data):
    sid = task_data["session_id"]
    phone = task_data["phone"]
    password = task_data["password"]
    login_url = task_data["login_url"]
    wingo_url = task_data["wingo_url"]
    site_name = task_data.get("site_name", "Platform")

    driver = create_driver(sid)
    active_drivers[sid] = driver

    try:
        # ১. লগইন ফেজ
        driver.get(login_url)
        time.sleep(3)
        driver.execute_script(MODAL_SWEEPER_JS)
        for _ in range(20):
            res = driver.execute_script(AUTO_LOGIN_JS, phone, password)
            if res == "SUCCESS": break
            time.sleep(0.5)

        time.sleep(4)
        driver.execute_script(MODAL_SWEEPER_JS)

        # লগইন নিশ্চিত হলে স্ট্যাটাস পাঠানো (কোনো ফটো ছাড়াই)
        firebase_sync_http(f"status/{sid}", "PUT", {
            "stage": "LOGIN_DONE", "site_name": site_name, "cur_bal": 0
        })

        # ২. উইঙ্গো নেভিগেশন ও কমান্ড ওয়েটিং
        while True:
            cmd_data = firebase_sync_http(f"commands/{sid}", "GET")
            if cmd_data:
                cmd = cmd_data.get("cmd")
                firebase_sync_http(f"commands/{sid}", "DELETE")

                if cmd == "NAV_WINGO":
                    driver.get(wingo_url)
                    time.sleep(4)
                    driver.execute_script(MODAL_SWEEPER_JS)
                    bal = driver.execute_script(FETCH_BALANCE_JS) or 0
                    firebase_sync_http(f"status/{sid}", "PUT", {
                        "stage": "WINGO_READY", "site_name": site_name, "cur_bal": bal
                    })

                elif cmd == "START_TRADE":
                    tgt = cmd_data.get("target", 250)
                    stp = cmd_data.get("steps", 5)
                    driver.execute_script(WINGO_ENGINE_JS, tgt, stp)
                    break

                elif cmd == "TERMINATE":
                    driver.quit()
                    return

            time.sleep(1.0)

        # ৩. ব্যাকগ্রাউন্ড ট্রেডিং লুপ (রিয়েল-টাইম ব্যালেন্স রিডিং)
        while True:
            cmd_data = firebase_sync_http(f"commands/{sid}", "GET")
            if cmd_data:
                cmd = cmd_data.get("cmd")
                firebase_sync_http(f"commands/{sid}", "DELETE")
                if cmd == "STOP":
                    driver.execute_script("if(window.__WINGO_ST){ window.__WINGO_ST.isRun = false; clearInterval(window.__WINGO_ST.autoInt); }")
                elif cmd == "TERMINATE":
                    break

            st_data = driver.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        isRun: window.__WINGO_ST.isRun,
                        curBal: window.__WINGO_ST.curBal || 0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        step: (window.__WINGO_ST.stpIdx || 0) + 1
                    };
                }
                return null;
            """)

            if st_data:
                cur_bal = st_data.get("curBal", 0)
                tgt_amt = st_data.get("tgtAmt", 0)
                is_run = st_data.get("isRun", False)

                if is_run and cur_bal >= tgt_amt and tgt_amt > 0:
                    firebase_sync_http(f"status/{sid}", "PUT", {
                        "stage": "COMPLETED", "cur_bal": cur_bal
                    })
                    break

                firebase_sync_http(f"status/{sid}", "PUT", {
                    "stage": "TRADING", "site_name": site_name,
                    "cur_bal": cur_bal, "step": st_data.get("step", 1),
                    "wins": st_data.get("w", 0), "losses": st_data.get("l", 0)
                })

            time.sleep(2.0)

    except Exception as e:
        logger.error(f"Task error sid={sid}: {e}")
    finally:
        try: driver.quit()
        except Exception: pass
        active_drivers.pop(sid, None)

def worker_task_listener():
    while True:
        try:
            tasks = firebase_sync_http("tasks", "GET")
            if tasks and isinstance(tasks, dict):
                for sid, t_val in list(tasks.items()):
                    if isinstance(t_val, dict) and sid not in active_drivers:
                        firebase_sync_http(f"tasks/{sid}", "DELETE")
                        threading.Thread(target=process_worker_task, args=(t_val,), daemon=True).start()
        except Exception: pass
        time.sleep(2.0)

if __name__ == "__main__":
    print("[*] Worker Engine Active & Ready for Automation Tasks...")
    worker_task_listener()
