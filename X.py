import os
import sys
import subprocess
import time
import threading
import shutil
import tempfile
import json

# ==========================================
# ১. প্রয়োজনীয় প্যাকেজ অটো-ইনস্টল
# ==========================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] প্যাকেজ ইনস্টল করা হচ্ছে: {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# ==========================================
# ২. কনফিগারেশন ও ডিরেক্টরি সেটআপ (নতুন টোকেন সহ)
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
bot = telebot.TeleBot(TOKEN)

# লগইন ইউআরএল
URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

# লগইন সম্পন্ন হওয়ার পর স্বয়ংক্রিয়ভাবে রিডাইরেক্ট হওয়ার গেম ইউআরএল (WinGo 30S)
URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_fixed_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

# বর্তমানে সচল থাকা ব্রাউজারসমূহ ট্র্যাক করার ডিকশনারি
# কী (key): f"{chat_id}_{profile_name}"
active_browsers = {}

# ইউজারের বর্তমান ইনপুট স্টেট (স্টেপ বাই স্টেপ ফর্ম)
user_states = {}

def get_user_profiles(chat_id):
    """ইউজারের সেভ করা ফিক্সড প্রোফাইলের তালিকা রিটার্ন করে"""
    user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id))
    if not os.path.exists(user_dir):
        return []
    return [d for d in os.listdir(user_dir) if os.path.isdir(os.path.join(user_dir, d))]

def auto_close_browser(session_key):
    """২৪ ঘণ্টা পূর্ণ হলে স্বয়ংক্রিয়ভাবে ব্রাউজার বন্ধ করে মেমোরি ক্লিয়ার করে"""
    sess = active_browsers.get(session_key)
    if sess:
        try:
            print(f"[*] ২৪ ঘন্টা পার হওয়ায় সেশন {session_key} অটোমেটিক বন্ধ করা হচ্ছে...")
            sess["driver"].quit()
        except Exception:
            pass
        if sess.get("is_temp") and os.path.exists(sess.get("profile_path", "")):
            shutil.rmtree(sess["profile_path"], ignore_errors=True)
        active_browsers.pop(session_key, None)

# ==========================================
# ৩. স্বাধীন ফায়ারফক্স ব্রাউজার লঞ্চার
# ==========================================
def launch_firefox_instance(profile_path, target_url):
    """প্রতিটি আইডির জন্য সম্পূর্ণ আলাদা ও নিরপেক্ষ ফায়ারফক্স উইন্ডো চালু করে"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    # লক ফাইল ডিলিট করা যাতে Marionette ক্র্যাশ বা হ্যাং না করে
    for lock in [".parentlock", "parent.lock", "lock", "sessionstore.jsonlz4"]:
        lp = os.path.join(profile_path, lock)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    options = Options()
    options.add_argument("-no-remote")
    options.add_argument("-new-instance")
    options.add_argument("-profile")
    options.add_argument(profile_path)
    
    # অপ্রয়োজনীয় পপআপ ও পুশ নোটিফিকেশন বন্ধ রাখা
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.get(target_url)
    return driver

# ==========================================
# ৪. অটো-ফিল ও নির্ভুল স্ট্যাটাস ভেরিফিকেশন JS
# ==========================================
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

# ব্যালেন্স রিড করার জাভাস্ক্রিপ্ট
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

# ==========================================
# ৫. উইনগো অটো-ট্রেডিং মার্টিনগেল ইঞ্জেকশন স্ক্রিপ্ট
# ==========================================
WINGO_AUTOMATION_JS = """
const autoTargetProfit = arguments[0];
const autoTotalSteps = arguments[1];

(function(){
    if (document.getElementById('sys-core-fin')) {
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

    const uF = s => String(s).toUpperCase().split('').map(c => {
        let n = c.charCodeAt(0);
        if (n >= 65 && n <= 90) return String.fromCodePoint(n + 119743);
        if (n >= 48 && n <= 57) return String.fromCodePoint(n + 120764);
        return c;
    }).join('');

    const cfg = { fRt: 300, syncDly: 2500, minSf: 10 };
    let st = {
        isRun: false,
        startBal: 0,
        tgtAmt: 0,
        curBal: 0,
        autoInt: null,
        preScn: null,
        isTrd: false,
        stpIdx: 0,
        dynSeq: [],
        totalSteps: autoTotalSteps || 7,
        tradesDone: 0,
        lastPred: null,
        lastPeriod: null,
        balanceCheckInterval: null,
        manualOverrideBet: null,
        w: 0,
        l: 0
    };

    let curApiIdx = 0, isFetchingApi = false;

    const VoiceEngine = {
        speak(msg, lang = 'en-US', rate = 1.1) {
            if (!('speechSynthesis' in window)) return;
            try {
                window.speechSynthesis.cancel();
                let utter = new SpeechSynthesisUtterance(msg);
                utter.lang = lang;
                utter.rate = rate;
                utter.pitch = 1.2;
                utter.volume = 1;
                window.speechSynthesis.speak(utter);
            } catch(e){}
        }
    };

    let dTimeLeft = 30;
    setInterval(() => {
        let uClk = document.getElementById('ui-clk');
        if (uClk) {
            let minutes = Math.floor(dTimeLeft / 60), seconds = dTimeLeft % 60;
            uClk.textContent = uF(`${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`);
        }
        dTimeLeft--;
        if (dTimeLeft < 0) dTimeLeft = 30;
    }, 1000);

    let lkOvl = document.createElement('div');
    lkOvl.id = 'drx-lck-bg';
    lkOvl.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.01);z-index:9999997;display:none;';
    lkOvl.addEventListener('click', e => { e.preventDefault(); e.stopPropagation(); }, true);
    document.body.appendChild(lkOvl);

    function chkBal() {
        let els = document.querySelectorAll('*');
        for (let i = 0; i < els.length; i++) {
            let txt = els[i].innerText || '';
            if (txt.includes('Wallet balance') || txt.includes('Balance')) {
                let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
                let match = parentTxt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
                if (match) {
                    st.curBal = parseFloat(match[1].replace(/,/g, ''));
                    return st.curBal;
                }
            }
        }
        for (let i = 0; i < els.length; i++) {
            let txt = els[i].innerText || '';
            if (txt.trim().match(/^[৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)) {
                st.curBal = parseFloat(txt.replace(/[^\\d.]/g, ''));
                return st.curBal;
            }
        }
        return st.curBal;
    }

    function generateSmartSequence(balance, steps) {
        steps = Math.max(1, parseInt(steps) || 1);
        let b = Math.max(1, Math.floor(balance) || 1);
        let units = Math.pow(2, steps) - 1;
        if (units > 0 && units <= b) {
            let base = Math.floor(b / units);
            let seq = [], val = Math.max(1, base);
            for (let i = 0; i < steps; i++) {
                seq.push(val);
                val *= 2;
            }
            return seq;
        }
        let seq = [], val = 1, sum = 0;
        for (let i = 0; i < steps; i++) {
            if (sum + val <= b) {
                seq.push(val);
                sum += val;
                val *= 2;
            } else {
                let rem = b - sum;
                if (rem > 0) seq.push(rem);
                break;
            }
        }
        return seq.length > 0 ? seq : [1];
    }

    let p = document.createElement('div');
    p.id = 'sys-core-fin';
    p.style.cssText = 'position:fixed;width:180px;padding:6px;font-family:monospace;font-size:10px;z-index:9999999;color:#fff;user-select:none;border-radius:14px;overflow:visible;background:rgba(10,15,20,0.92);box-shadow:0 8px 32px rgba(0,0,0,0.8);border:1px solid #00ff88;';
    
    let sL = localStorage.getItem('drx_ui_x'), sT = localStorage.getItem('drx_ui_y');
    if (sL && sT) { p.style.left = sL; p.style.top = sT; }
    else { p.style.top = '25px'; p.style.right = '20px'; }

    let stl = document.createElement('style');
    stl.innerHTML = '@keyframes titlePulseAnim{0%{transform:scale(1);text-shadow:0 0 10px #00ff00;}50%{transform:scale(1.05);text-shadow:0 0 20px #00ff00,0 0 30px #fff;}100%{transform:scale(1);text-shadow:0 0 10px #00ff00;}}.drx-in{display:flex;flex-direction:column;gap:4px;}.txt-blk{color:#fff;font-weight:900;}.txt-blk-accent{color:#00ff88;font-weight:900;}.txt-blk-warn{color:#ffcc00;font-weight:900;}.txt-blk-err{color:#ff3366;font-weight:900;}.txt-blk-cyan{color:#00e5ff;font-weight:900;}.drx-elec-target{outline:3px solid #00ff88!important;}';
    document.body.appendChild(stl);

    let inC = document.createElement('div');
    inC.className = 'drx-in';

    let h = document.createElement('div');
    h.style.cssText = 'padding:6px;font-size:11px;display:flex;justify-content:space-between;cursor:move;border-bottom:1px solid #333;';
    h.innerHTML = `<span class="txt-blk-accent" id="drx-title">${uF('WINZY WINGO')}</span><span style="cursor:pointer;" class="txt-blk-err" id="sys-cls">✕</span>`;
    inC.appendChild(h);

    // ড্র্যাগিং লজিক
    let drg = false, sx, sy, sl, st_y;
    function dSt(e) {
        if (e.target.tagName === 'SPAN' && e.target.id === 'sys-cls') return;
        drg = true;
        let ev = e.type.includes('touch') ? e.touches[0] : e;
        sx = ev.clientX; sy = ev.clientY;
        sl = p.offsetLeft; st_y = p.offsetTop;
    }
    function dMv(e) {
        if (!drg) return;
        e.preventDefault();
        let ev = e.type.includes('touch') ? e.touches[0] : e;
        p.style.left = (sl + ev.clientX - sx) + 'px';
        p.style.top = (st_y + ev.clientY - sy) + 'px';
    }
    function dEn() {
        drg = false;
        localStorage.setItem('drx_ui_x', p.style.left);
        localStorage.setItem('drx_ui_y', p.style.top);
    }
    h.addEventListener('mousedown', dSt);
    document.addEventListener('mousemove', dMv);
    document.addEventListener('mouseup', dEn);

    h.querySelector('#sys-cls').onclick = () => {
        clearInterval(st.autoInt);
        clearInterval(st.preScn);
        if (st.balanceCheckInterval) clearInterval(st.balanceCheckInterval);
        p.remove();
        lkOvl.remove();
    };

    let b = document.createElement('div');
    b.style.cssText = 'padding:6px;display:flex;flex-direction:column;gap:6px;';

    const p1 = document.createElement('div');
    p1.innerHTML = `<div style="text-align:center;margin-bottom:6px;padding:4px;background:#141b22;border-radius:6px;border:1px solid #30363d;"><span class="txt-blk" style="font-size:9px;color:#8b949e;">${uF('CURRENT BAL')}</span><br><span id="pre-bal" class="txt-blk" style="font-size:14px;color:#00ff88;">--</span></div>`;

    const tgtInp = document.createElement('input');
    tgtInp.type = 'number';
    tgtInp.value = autoTargetProfit || '';
    tgtInp.placeholder = 'TARGET PROFIT (৳)';
    tgtInp.className = 'txt-blk';
    tgtInp.style.cssText = 'width:100%;box-sizing:border-box;padding:6px;margin-bottom:4px;background:#0d1117;border:1px solid #30363d;border-radius:4px;text-align:center;font-size:11px;color:#fff;outline:none;';

    const stepInp = document.createElement('input');
    stepInp.type = 'number';
    stepInp.value = autoTotalSteps || 7;
    stepInp.placeholder = 'TOTAL STEPS (e.g. 7)';
    stepInp.className = 'txt-blk-cyan';
    stepInp.style.cssText = 'width:100%;box-sizing:border-box;padding:6px;margin-bottom:6px;background:#0d1117;border:1px solid #30363d;border-radius:4px;text-align:center;font-size:11px;color:#00e5ff;outline:none;';

    const goBtn = document.createElement('button');
    goBtn.innerText = uF('START AUTO TRADE');
    goBtn.className = 'txt-blk-accent';
    goBtn.style.cssText = 'width:100%;box-sizing:border-box;padding:7px;background:#238636;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;';

    p1.appendChild(tgtInp);
    p1.appendChild(stepInp);
    p1.appendChild(goBtn);

    const p2 = document.createElement('div');
    p2.style.display = 'none';

    const balBx = document.createElement('div');
    balBx.style.cssText = 'padding:6px;text-align:center;background:#161b22;border-radius:6px;border:1px solid #30363d;margin-bottom:6px;';
    balBx.innerHTML = `<div class="txt-blk" style="font-size:9px;color:#8b949e;">${uF('LIVE BAL / TARGET')}</div><div id="ui-bal" class="txt-blk-accent" style="font-size:14px;">--</div>`;

    const infBx = document.createElement('div');
    infBx.style.cssText = 'padding:6px;font-size:10px;line-height:1.8;background:#0d1117;border-radius:6px;border:1px solid #30363d;';
    infBx.innerHTML = `
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid #21262d;"><span style="color:#8b949e;">API:</span><span id="ui-ai" class="txt-blk-cyan">VIP JSON</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid #21262d;"><span style="color:#8b949e;">TGT:</span><span id="ui-tgt" class="txt-blk">0</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid #21262d;"><span style="color:#8b949e;">BET:</span><span id="ui-bet" class="txt-blk-warn">--</span></div>
        <div style="display:flex;justify-content:space-between;border-bottom:1px solid #21262d;"><span style="color:#8b949e;">CLK:</span><span id="ui-clk" class="txt-blk">00:30</span></div>
        <div style="display:flex;justify-content:space-between;"><span style="color:#8b949e;">STS:</span><span id="ui-sts" class="txt-blk">WAIT</span></div>
    `;

    const ghBox = document.createElement('div');
    ghBox.id = 'gh-box-wrap';
    ghBox.style.cssText = 'width:100%;min-height:26px;background:#161b22;border:1px solid #30363d;border-radius:4px;padding:4px;margin-top:4px;font-size:8px;line-height:1.3;color:#8b949e;';
    ghBox.innerHTML = '<div id="gh-content">Syncing VIP API...</div>';
    infBx.appendChild(ghBox);

    const stpBtn = document.createElement('button');
    stpBtn.innerText = uF('STOP TRADE');
    stpBtn.className = 'txt-blk-err';
    stpBtn.style.cssText = 'width:100%;padding:7px;background:#da3633;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;margin-top:6px;font-weight:bold;';

    p2.appendChild(balBx);
    p2.appendChild(infBx);
    p2.appendChild(stpBtn);

    b.appendChild(p1);
    b.appendChild(p2);
    inC.appendChild(b);
    p.appendChild(inC);
    document.body.appendChild(p);

    const drx_triggerEvent = (el, etype) => {
        let ev = new Event(etype, { bubbles: true, cancelable: true });
        el.dispatchEvent(ev);
    };

    const drx_simClick = el => {
        if (!el) return;
        ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
            try {
                el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            } catch (e) {}
        });
    };

    const exeTrd = (pred, amt, cb) => {
        try {
            let btn = null, targetText = pred.toLowerCase();
            let btns = document.querySelectorAll('button, div, span');
            for (let i = 0; i < btns.length; i++) {
                let t = (btns[i].innerText || '').trim().toLowerCase();
                if (t === targetText && btns[i].offsetParent && !btns[i].children.length) {
                    btn = btns[i];
                    break;
                }
            }
            if (!btn) {
                if (targetText === 'big') btn = document.querySelector('.Betting__C-foot-b');
                else if (targetText === 'small') btn = document.querySelector('.Betting__C-foot-s');
                else if (targetText === 'green') btn = document.querySelector('button[class*="green"], div[class*="green"]');
                else if (targetText === 'red') btn = document.querySelector('button[class*="red"], div[class*="red"]');
                else if (targetText === 'violet') btn = document.querySelector('button[class*="violet"], div[class*="violet"]');
            }
            if (!btn) {
                if (cb) cb(false);
                return;
            }
            btn.classList.add('drx-elec-target');
            drx_simClick(btn);

            let checkAttempts = 0;
            let valInterval = setInterval(() => {
                checkAttempts++;
                let inpEl = document.querySelector("input[type='number'], input.van-field__control");
                if (inpEl || checkAttempts > 15) {
                    clearInterval(valInterval);
                    if (inpEl) {
                        inpEl.focus();
                        let setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        if (setV) setV.call(inpEl, String(amt));
                        else inpEl.value = amt;
                        drx_triggerEvent(inpEl, 'input');
                        drx_triggerEvent(inpEl, 'change');
                        drx_triggerEvent(inpEl, 'blur');
                    }
                    setTimeout(() => {
                        let dEl = document.querySelector('button.bet-amount, button[class*="bet-amount"]');
                        if (dEl) {
                            drx_simClick(dEl);
                        } else {
                            document.querySelectorAll('button').forEach(b => {
                                if ((b.innerText || '').includes('Total amount') && b.offsetParent) drx_simClick(b);
                            });
                        }
                        btn.classList.remove('drx-elec-target');
                        setTimeout(() => { if (cb) cb(true); }, 2000);
                    }, 800);
                }
            }, 200);
        } catch (e) {
            if (cb) cb(false);
        }
    };

    const getNextLivePeriod = str => {
        let chars = str.split('');
        for (let i = chars.length - 1; i >= 0; i--) {
            if (chars[i] !== '9') {
                chars[i] = String.fromCharCode(chars[i].charCodeAt(0) + 1);
                return chars.join('');
            }
            chars[i] = '0';
        }
        return '1' + chars.join('');
    };

    const apiLoopTask = async () => {
        if (!st.isRun || st.isTrd || isFetchingApi) return;
        isFetchingApi = true;
        try {
            chkBal();
            const uBal = document.getElementById('ui-bal');
            const uSts = document.getElementById('ui-sts');
            const uBet = document.getElementById('ui-bet');

            if (st.curBal >= st.tgtAmt && st.curBal > 0) {
                if (uBal) uBal.innerText = uF(`${st.curBal.toFixed(2)} (DONE)`);
                if (uSts) {
                    uSts.innerText = uF('DONE');
                    uSts.className = 'txt-blk-accent';
                }
                stpBtn.style.display = 'none';
                VoiceEngine.speak("Target reached successfully.");
                st.isRun = false;
                clearInterval(st.autoInt);
                return;
            } else {
                if (uBal) uBal.innerText = uF(st.curBal > 0 ? `${st.curBal.toFixed(2)} / ${st.tgtAmt}` : '--');
            }

            let ts = Math.floor(Date.now() / 1000);
            let res = await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts=" + ts);
            let dataArray = await res.json();

            if (dataArray && dataArray.length > 0) {
                if (curApiIdx >= dataArray.length) curApiIdx = 0;
                let activeLogic = dataArray[curApiIdx];
                let tempHist = activeLogic.history;
                let cSig = getNextLivePeriod(String(tempHist[0].pid));
                let sSig = sessionStorage.getItem('drx_sig');

                if (cSig !== sSig) {
                    if (st.lastPred && st.lastPeriod) {
                        let actualData = tempHist[0];
                        let actualR = actualData.actual === 'BIG' ? 'BIG' : 'SMALL';
                        if (st.lastPred === actualR) {
                            st.w++;
                            st.stpIdx = 0;
                        } else {
                            st.l++;
                            st.stpIdx = Math.min(st.stpIdx + 1, st.dynSeq.length - 1);
                            curApiIdx = (curApiIdx === 0 && dataArray.length > 1) ? 1 : 0;
                        }
                    }
                    st.lastPeriod = cSig;

                    st.isTrd = true;
                    if (uSts) {
                        uSts.innerText = uF('CHK...');
                        uSts.className = 'txt-blk-warn';
                    }

                    let nBal = chkBal();
                    if (uBal) uBal.innerText = uF(`${nBal.toFixed(2)} / ${st.tgtAmt}`);

                    if (nBal >= st.tgtAmt && nBal > 0) {
                        st.isTrd = false;
                        isFetchingApi = false;
                        return;
                    }

                    if (st.stpIdx >= st.dynSeq.length) st.stpIdx = st.dynSeq.length - 1;
                    let tAmt = st.manualOverrideBet ? st.manualOverrideBet : st.dynSeq[st.stpIdx];

                    if (uBet) uBet.innerText = uF(`${tAmt} (S${st.stpIdx + 1})`);

                    if (nBal < tAmt) {
                        if (uSts) {
                            uSts.innerText = uF('LOW BAL');
                            uSts.className = 'txt-blk-err';
                        }
                        st.stpIdx = 0;
                        st.isTrd = false;
                        isFetchingApi = false;
                        return;
                    }

                    setTimeout(() => {
                        let activeLogicNew = dataArray[curApiIdx];
                        let prediction = (activeLogicNew.pred || 'BIG').toUpperCase();
                        st.lastPred = prediction;

                        let ghC = document.getElementById('gh-content');
                        if (ghC) ghC.textContent = `Step: ${st.stpIdx + 1}/${st.dynSeq.length} | Bet: ${tAmt}\\nPred: ${prediction} | W:${st.w} L:${st.l}`;

                        if (prediction === 'SKIP') {
                            if (uSts) uSts.innerText = uF('SKIP');
                            sessionStorage.setItem('drx_sig', cSig);
                            setTimeout(() => { st.isTrd = false; }, 1000);
                        } else {
                            if (uSts) uSts.innerText = uF('BETTING...');
                            exeTrd(prediction, tAmt, (suc) => {
                                if (suc) {
                                    if (uSts) {
                                        uSts.innerText = uF('OK');
                                        uSts.className = 'txt-blk-accent';
                                    }
                                    sessionStorage.setItem('drx_sig', cSig);
                                    st.tradesDone++;
                                } else {
                                    if (uSts) {
                                        uSts.innerText = uF('ERR');
                                        uSts.className = 'txt-blk-err';
                                    }
                                }
                                setTimeout(() => { st.isTrd = false; }, 1000);
                            });
                        }
                    }, 1500);
                } else if (!st.isTrd) {
                    if (uSts) {
                        uSts.innerText = uF('SCAN');
                        uSts.className = 'txt-blk';
                    }
                }
            }
        } catch (e) {
            st.isTrd = false;
        }
        isFetchingApi = false;
    };

    goBtn.onclick = () => {
        let inputTarget = parseFloat(tgtInp.value);
        if (!inputTarget || inputTarget <= 0) {
            alert('Please enter Target Profit Amount!');
            tgtInp.focus();
            return;
        }
        let inputSteps = parseInt(stepInp.value) || 7;
        st.totalSteps = inputSteps;
        st.tradesDone = 0;
        st.w = 0;
        st.l = 0;
        curApiIdx = 0;

        let liveB = chkBal();
        st.startBal = liveB;
        st.tgtAmt = (inputTarget <= liveB) ? (liveB + inputTarget) : inputTarget;
        st.dynSeq = generateSmartSequence(liveB, st.totalSteps);
        st.stpIdx = 0;

        document.getElementById('ui-tgt').innerText = uF(st.tgtAmt.toFixed(0));
        p1.style.display = 'none';
        p2.style.display = 'block';
        st.isRun = true;
        st.isTrd = false;
        document.getElementById('ui-sts').innerText = uF('RDY');

        st.autoInt = setInterval(apiLoopTask, 1000);
    };

    stpBtn.onclick = () => {
        st.isRun = false;
        clearInterval(st.autoInt);
        document.getElementById('ui-sts').innerText = uF('STOPPED');
        p2.style.display = 'none';
        p1.style.display = 'block';
    };

    // অটো স্টার্ট ট্রিগার (যদি আরগুমেন্ট থাকে)
    if (autoTargetProfit && autoTotalSteps) {
        setTimeout(() => {
            goBtn.click();
        }, 1000);
    }

    return "INJECTED_AND_STARTED";
})();
"""

# ==========================================
# ৬. ব্যাকগ্রাউন্ড লগইন প্রসেস ও লিংক ট্রিগার
# ==========================================
def process_login(chat_id, session_key, phone, password, status_msg_id):
    state = user_states.get(chat_id, {})
    site_name = state.get("site_name")
    site_url = state.get("site_url")
    profile_path = state.get("profile_path")
    profile_name = state.get("profile_name")
    is_temp = state.get("is_temp", False)

    # সাইট অনুযায়ী নির্দিষ্ট WinGo 30S লিংক সিলেক্ট করা
    if "amarclub" in site_name.lower():
        wingo_url = URL_AMARCLUB_WINGO
    else:
        wingo_url = URL_DKWIN_WINGO

    stop_anim = threading.Event()
    def spinner():
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_anim.is_set():
            try:
                bot.edit_message_text(
                    f"⏳ **{site_name}**-এ লগইন সম্পন্ন হচ্ছে... [ {spinners[i % len(spinners)]} ]\n"
                    f"ব্রাউজার চালু করে ক্রেডেনশিয়াল সাবমিট করা হচ্ছে...",
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    parse_mode="Markdown"
                )
            except Exception:
                pass
            i += 1
            time.sleep(0.5)

    threading.Thread(target=spinner, daemon=True).start()

    driver = None
    try:
        driver = launch_firefox_instance(profile_path, site_url)
    except Exception as e:
        stop_anim.set()
        bot.edit_message_text(f"❌ ব্রাউজার চালু করতে সমস্যা হয়েছে:\n`{e}`", chat_id=chat_id, message_id=status_msg_id, parse_mode="Markdown")
        return

    # ফর্ম ফিল্ড ফিলাপ করার চেষ্টা (সর্বোচ্চ ৪০ সেকেন্ড)
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
        stop_anim.set()
        bot.edit_message_text("❌ লগইন ফিল্ড পাওয়া যায়নি অথবা পেজ লোড হতে অতিরিক্ত সময় নিয়েছে।", chat_id=chat_id, message_id=status_msg_id)
        return

    # লগইন স্ট্যাটাস ভেরিফাই করা (সর্বোচ্চ ২০ সেকেন্ড)
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
                err_detail = res.get("message", "ভুল পাসওয়ার্ড বা তথ্য দেওয়া হয়েছে।")
                break
        except Exception:
            pass
        time.sleep(0.5)

    stop_anim.set()

    if login_status == "SUCCESS" or login_status == "PENDING":
        # ২৪ ঘণ্টার অটো-ক্লোজ টাইমার চালু
        timer = threading.Timer(86400, auto_close_browser, args=[session_key])
        timer.daemon = True
        timer.start()

        active_browsers[session_key] = {
            "chat_id": chat_id,
            "profile_name": profile_name,
            "profile_path": profile_path,
            "driver": driver,
            "timer": timer,
            "site_name": site_name,
            "phone": phone,
            "is_temp": is_temp,
            "wingo_url": wingo_url
        }

        # ১. লগইন সফল মেসেজ পাঠানো
        bot.edit_message_text(
            f"🎉 **আপনার অ্যাকাউন্ট সফলভাবে লগইন হয়েছে!**\n\n"
            f"🌐 **সাইট:** {site_name}\n"
            f"📱 **অ্যাকাউন্ট:** `{phone}`\n"
            f"📁 **প্রোফাইল:** `{profile_name}`\n\n"
            f"⚡ এবার সরাসরি **WinGo 30S** গেমিং পেজ ট্রিগার করা হচ্ছে...",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )

        time.sleep(2)

        # ২. অটোমেটিক WinGo 30S গেম লিংকে রিডাইরেক্ট করা
        try:
            driver.get(wingo_url)
        except Exception as e:
            print(f"Error navigating to wingo: {e}")

        # পেজ লোড হওয়ার জন্য ৪ সেকেন্ড অপেক্ষা
        time.sleep(4)

        # ৩. পেজ থেকে বর্তমান ব্যালেন্স রিড করা
        current_bal = 0.0
        try:
            bal_res = driver.execute_script(FETCH_BALANCE_JS)
            if bal_res:
                current_bal = float(bal_res)
        except Exception:
            current_bal = 0.0

        # স্টেট আপডেট: ইউজার এখন টার্গেট প্রফিট অ্যামাউন্ট লিখবেন
        user_states[chat_id] = {
            "step": "WAITING_TARGET_PROFIT",
            "session_key": session_key,
            "site_name": site_name,
            "profile_name": profile_name,
            "current_balance": current_bal,
            "wingo_url": wingo_url,
            "driver": driver
        }

        # ৪. টেলিগ্রামে ট্রিগার ও ব্যালেন্স কনফার্মেশন সহ প্রফিট জানতে চাওয়া
        bal_text = f"{current_bal:.2f} ৳" if current_bal > 0 else "রিফ্রেশ হচ্ছে / পেজে দেখা যাচ্ছে"

        bot.send_message(
            chat_id,
            f"🎯 **গেম লিংক স্বয়ংক্রিয়ভাবে ট্রিগার হয়েছে!**\n\n"
            f"🌐 **সাইট:** {site_name}\n"
            f"🔗 **গেম পেজ:** WinGo 30S\n"
            f"💰 **আপনার বর্তমান ব্যালেন্স:** `{bal_text}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📈 **টার্গেট প্রফিট নির্ধারণ করুন:**\n"
            f"আপনি মোট কত টাকা প্রফিট (লাভ) করতে চান? অনুগ্রহ করে সংখ্যা লিখে পাঠান (যেমন: `300` বা `500`):",
            parse_mode="Markdown"
        )

    elif login_status == "ERROR":
        try:
            driver.quit()
        except Exception:
            pass
        bot.edit_message_text(
            f"⚠️ **লগইন ব্যর্থ হয়েছে!**\n\n"
            f"🌐 **সাইট:** {site_name}\n"
            f"📱 **অ্যাকাউন্ট:** `{phone}`\n"
            f"❌ **কারণ:** {err_detail}\n\n"
            f"দয়া করে ফোন নাম্বার ও পাসওয়ার্ড চেক করে /start দিয়ে পুনরায় চেষ্টা করুন।",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )

# ==========================================
# ৭. টেলিগ্রাম মেনু ও ইন্টারফেস
# ==========================================
def show_profile_menu(chat_id, message_id=None):
    profiles = get_user_profiles(chat_id)
    markup = InlineKeyboardMarkup()

    if profiles:
        for p in profiles:
            markup.add(InlineKeyboardButton(f"📁 Fix: {p}", callback_data=f"selprof_{p}"))

    markup.add(
        InlineKeyboardButton("➕ Create Fix Profile", callback_data="btn_create_fix"),
        InlineKeyboardButton("⚡ Skip Profile", callback_data="btn_skip_prof")
    )
    markup.add(
        InlineKeyboardButton("🌐 রানিং ব্রাউজার তালিকা", callback_data="btn_active_list"),
        InlineKeyboardButton("🗑️ ফিক্স প্রোফাইল ডিলিট", callback_data="btn_del_menu")
    )

    text = "⚙️ **প্রোফাইল মোড নির্বাচন করুন:**\n\n" \
           "• **Fix Profile:** পার্মানেন্ট প্রোফাইল যা ফায়ারফক্সে সেভ থাকবে।\n" \
           "• **Skip Profile:** সম্পূর্ণ ফ্রেশ আলাদা প্রোফাইল (কোনো ডাটা সেভ হবে না)।"

    if message_id:
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# ৮. টেলিগ্রাম কমান্ড হ্যান্ডলার
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Amarclub1", callback_data="site_amarclub"),
        InlineKeyboardButton("Dkwin6", callback_data="site_dkwin")
    )
    bot.send_message(
        message.chat.id, 
        "🚀 **WinGo অটোমেশন ও ট্রেডিং প্যানেল**\n\nঅনুগ্রহ করে প্রথমে কাঙ্ক্ষিত সাইট নির্বাচন করুন:", 
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    if data in ["site_amarclub", "site_dkwin"]:
        site_url = URL_AMARCLUB_LOGIN if data == "site_amarclub" else URL_DKWIN_LOGIN
        site_name = "Amarclub1" if data == "site_amarclub" else "Dkwin6"

        user_states[chat_id] = {
            "site_url": site_url,
            "site_name": site_name,
            "step": "WAITING_PROFILE_CHOICE"
        }
        bot.answer_callback_query(call.id)
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_skip_prof":
        temp_dir = tempfile.mkdtemp(prefix=f"ff_skip_{chat_id}_")
        state = user_states.get(chat_id, {})
        state.update({
            "profile_path": temp_dir,
            "profile_name": f"Temp_{int(time.time())}",
            "is_temp": True,
            "step": "WAITING_PHONE"
        })
        user_states[chat_id] = state

        bot.answer_callback_query(call.id, "নতুন ফ্রেশ প্রোফাইল সক্রিয় হয়েছে...")
        bot.edit_message_text(
            f"⚡ **Skip Profile মোড প্রস্তুত!**\n\n"
            f"📱 আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif data == "btn_create_fix":
        user_states[chat_id]["step"] = "WAITING_NEW_PROFILE_NAME"
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "✍️ ফিক্সড প্রোফাইলের জন্য একটি নাম লিখে পাঠান (যেমন: RDP1 বা Account1):",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif data.startswith("selprof_"):
        prof_name = data.split("selprof_")[1]
        prof_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), prof_name)

        state = user_states.get(chat_id, {})
        state.update({
            "profile_path": prof_path,
            "profile_name": prof_name,
            "is_temp": False,
            "step": "WAITING_PHONE"
        })
        user_states[chat_id] = state

        bot.answer_callback_query(call.id, f"প্রোফাইল: {prof_name}")
        bot.edit_message_text(
            f"📁 **ফিক্সড প্রোফাইল:** `{prof_name}` নির্বাচিত হয়েছে।\n\n"
            f"📱 আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            chat_id=chat_id,
            message_id=call.message.message_id,
            parse_mode="Markdown"
        )

    elif data == "btn_active_list":
        markup = InlineKeyboardMarkup()
        found = False
        for k, v in list(active_browsers.items()):
            if v["chat_id"] == chat_id:
                found = True
                markup.add(InlineKeyboardButton(f"❌ বন্ধ করুন: {v['profile_name']} ({v['site_name']})", callback_data=f"kill_{k}"))
        markup.add(InlineKeyboardButton("🔙 ফিরে যান", callback_data="btn_back_to_prof"))

        txt = "🌐 **বর্তমানে সচল থাকা ব্রাউজারসমূহ:**\nযেকোনো ব্রাউজার ম্যানুয়ালি বন্ধ করতে নিচের বাটনে ক্লিক করুন:" if found else "বর্তমানে আপনার কোনো সচল ব্রাউজার চালু নেই।"
        bot.edit_message_text(txt, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("kill_"):
        sk = data.split("kill_")[1]
        sess = active_browsers.pop(sk, None)
        if sess:
            try:
                sess["driver"].quit()
            except Exception:
                pass
            bot.answer_callback_query(call.id, "ব্রাউজারটি সফলভাবে বন্ধ করা হয়েছে!")
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_del_menu":
        profiles = get_user_profiles(chat_id)
        markup = InlineKeyboardMarkup()
        for p in profiles:
            markup.add(InlineKeyboardButton(f"🗑️ ডিলিট: {p}", callback_data=f"dodel_{p}"))
        markup.add(InlineKeyboardButton("🔙 ফিরে যান", callback_data="btn_back_to_prof"))
        bot.edit_message_text("🗑️ যে প্রোফাইলটি ডিলিট করতে চান তা নির্বাচন করুন:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    elif data.startswith("dodel_"):
        p_name = data.split("dodel_")[1]
        target_path = os.path.join(PROFILES_BASE_DIR, str(chat_id), p_name)
        
        sk = f"{chat_id}_{p_name}"
        sess = active_browsers.pop(sk, None)
        if sess:
            try:
                sess["driver"].quit()
            except Exception:
                pass

        if os.path.exists(target_path):
            shutil.rmtree(target_path, ignore_errors=True)
        bot.answer_callback_query(call.id, f"{p_name} প্রোফাইল ডিলিট সম্পন্ন!")
        show_profile_menu(chat_id, call.message.message_id)

    elif data == "btn_back_to_prof":
        show_profile_menu(chat_id, call.message.message_id)

    elif data.startswith("chkbal_"):
        sk = data.split("chkbal_")[1]
        sess = active_browsers.get(sk)
        if sess and sess.get("driver"):
            try:
                bal = sess["driver"].execute_script(FETCH_BALANCE_JS)
                bot.answer_callback_query(call.id, f"বর্তমান ব্যালেন্স: {bal} ৳", show_alert=True)
            except Exception as e:
                bot.answer_callback_query(call.id, "ব্যালেন্স পড়তে সমস্যা হয়েছে।", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "সেশনটি আর সচল নেই।", show_alert=True)

    elif data.startswith("stoptrade_"):
        sk = data.split("stoptrade_")[1]
        sess = active_browsers.get(sk)
        if sess and sess.get("driver"):
            try:
                sess["driver"].execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
                bot.answer_callback_query(call.id, "অটো-ট্রেড বন্ধের কমান্ড পাঠানো হয়েছে!", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "কমান্ড পাঠাতে ব্যর্থ হয়েছে।", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "সেশনটি আর সচল নেই।", show_alert=True)

# ==========================================
# ৯. টেক্সট মেসেজ ইনপুট হ্যান্ডলার (টার্গেট ও স্টেপ গ্রহণ)
# ==========================================
@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_text_inputs(message):
    chat_id = message.chat.id
    state = user_states[chat_id]
    step = state.get("step")
    text = message.text.strip()

    if step == "WAITING_NEW_PROFILE_NAME":
        clean_name = "".join([c for c in text if c.isalnum() or c in ('_', '-')]).strip()
        if not clean_name:
            bot.send_message(chat_id, "❌ প্রোফাইল নামে কোনো স্পেশাল ক্যারেক্টার ব্যবহার করবেন না। আবার লিখুন:")
            return

        user_dir = os.path.join(PROFILES_BASE_DIR, str(chat_id), clean_name)
        os.makedirs(user_dir, exist_ok=True)

        state["profile_path"] = user_dir
        state["profile_name"] = clean_name
        state["is_temp"] = False
        state["step"] = "WAITING_PHONE"

        bot.send_message(
            chat_id,
            f"✅ ফিক্সড প্রোফাইল `{clean_name}` সংরক্ষিত হয়েছে!\n\n"
            f"📱 এবার আপনার **ফোন নাম্বার (N)** লিখে পাঠান:",
            parse_mode="Markdown"
        )

    elif step == "WAITING_PHONE":
        state["phone"] = text
        state["step"] = "WAITING_PASSWORD"
        bot.send_message(
            chat_id,
            f"📱 নাম্বার: `{text}` সংরক্ষিত হয়েছে।\n\n"
            f"🔑 এবার আপনার **পাসওয়ার্ড (P)** লিখে পাঠান:",
            parse_mode="Markdown"
        )

    elif step == "WAITING_PASSWORD":
        state["password"] = text
        state["step"] = "COMPLETED_INPUTS"

        session_key = f"{chat_id}_{state['profile_name']}"
        status_msg = bot.send_message(chat_id, "⏳ ব্রাউজার চালু করে স্বয়ংক্রিয় লগইন শুরু হচ্ছে... [ ⠋ ]")

        threading.Thread(
            target=process_login,
            args=(chat_id, session_key, state["phone"], state["password"], status_msg.message_id),
            daemon=True
        ).start()

    # ২য় সেশন: টার্গেট প্রফিট গ্রহণ
    elif step == "WAITING_TARGET_PROFIT":
        try:
            target_profit = float(text)
            if target_profit <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে একটি সঠিক পজিটিভ সংখ্যা লিখুন (যেমন: `500`):", parse_mode="Markdown")
            return

        state["target_profit"] = target_profit
        state["step"] = "WAITING_STEPS"

        bot.send_message(
            chat_id,
            f"✅ **টার্গেট প্রফিট:** `{target_profit}` ৳ রেকর্ড করা হয়েছে।\n\n"
            f"🔢 **মার্টিনগেল স্টেপ (Total Steps):**\n"
            f"আপনি কত স্টেপ সিকোয়েন্স নিয়ে ট্রেড করতে চান? সংখ্যাটি লিখে পাঠান (যেমন: `7` বা `10`):",
            parse_mode="Markdown"
        )

    # ৩য় সেশন: টোটাল স্টেপ গ্রহণ ও অটোমেশন চালু
    elif step == "WAITING_STEPS":
        try:
            total_steps = int(text)
            if total_steps <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: `7`):", parse_mode="Markdown")
            return

        state["total_steps"] = total_steps
        state["step"] = "TRADING_RUNNING"

        session_key = state.get("session_key")
        sess = active_browsers.get(session_key)
        target_profit = state.get("target_profit")
        site_name = state.get("site_name")

        if not sess or not sess.get("driver"):
            bot.send_message(chat_id, "❌ ব্রাউজার সেশনটি পাওয়া যায়নি। অনুগ্রহ করে /start দিয়ে আবার শুরু করুন।")
            return

        driver = sess["driver"]

        # ব্রাউজারে স্বয়ংক্রিয় অটো-ট্রেড স্ক্রিপ্ট ইঞ্জেক্ট করা
        try:
            driver.execute_script(WINGO_AUTOMATION_JS, target_profit, total_steps)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ স্ক্রিপ্ট ইঞ্জেকশনে ত্রুটি: `{e}`", parse_mode="Markdown")
            return

        # কন্ট্রোল মেনু বাটন তৈরি
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("📊 লাইভ ব্যালেন্স চেক", callback_data=f"chkbal_{session_key}"),
            InlineKeyboardButton("🛑 অটো-ট্রেড বন্ধ", callback_data=f"stoptrade_{session_key}")
        )
        markup.add(
            InlineKeyboardButton("❌ ব্রাউজার বন্ধ করুন", callback_data=f"kill_{session_key}")
        )

        bot.send_message(
            chat_id,
            f"🚀 **উইনগো অটো-ট্রেডিং সফলভাবে শুরু হয়েছে!**\n\n"
            f"🌐 **প্ল্যাটফর্ম:** {site_name} (WinGo 30S)\n"
            f"🎯 **টার্গেট প্রফিট:** `{target_profit}` ৳\n"
            f"🔢 **মার্টিনগেল স্টেপ:** `{total_steps}` Steps\n"
            f"⚡ **স্ট্যাটাস:** ব্রাউজার স্ক্রিনে লাইভ উইজেট সক্রিয় রয়েছে এবং সিগন্যাল অনুযায়ী অটো ট্রেড হচ্ছে।\n\n"
            f"💡 *টার্গেট প্রফিট সম্পন্ন হলে ব্রাউজার স্বয়ংক্রিয়ভাবে থামবে অথবা নিচের বাটন দিয়ে নিয়ন্ত্রণ করতে পারেন:*",
            reply_markup=markup,
            parse_mode="Markdown"
        )

if __name__ == "__main__":
    print("[*] টেলিগ্রাম বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
