import os
import sys
import subprocess
import time
import threading
import shutil
import json
import base64
import random
import string
import tempfile

# ==============================================================================
# 1. AUTOMATIC PACKAGE INSTALLER & ENVIRONMENT BOOTSTRAP
# ==============================================================================
def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        print(f"[*] Bootstrapping dependency: {package_name}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        except Exception as err:
            print(f"[!] Package install error: {err}")

install_and_import("requests")
install_and_import("selenium")

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==============================================================================
# 2. CLUSTER CONFIGURATION & CONSTANTS
# ==============================================================================
FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

# ★ দৃশ্যমান ব্রাউজার উইন্ডো সরাসরি চালু করার জন্য HEADLESS_MODE = False
# ব্যাকগ্রাউন্ডে চালাতে চাইলে True করবেন
HEADLESS_MODE = False

WINDOW_WIDTH = 430
WINDOW_HEIGHT = 932

BASE_PROFILES_DIR = os.path.expanduser("~/.cluster_worker_profiles")
os.makedirs(BASE_PROFILES_DIR, exist_ok=True)

# ==============================================================================
# 3. MATHEMATICAL BOLD UNICODE HELPER
# ==============================================================================
def to_bold(text: str) -> str:
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

# ==============================================================================
# 4. PERSISTENT NODE IDENTITY MANAGEMENT
# ==============================================================================
NODE_ID_FILE = os.path.join(os.getcwd(), "node_id.txt")

def get_or_create_node_id() -> str:
    if os.path.exists(NODE_ID_FILE):
        try:
            with open(NODE_ID_FILE, "r", encoding="utf-8") as f:
                saved_id = f.read().strip()
                if saved_id:
                    return saved_id
        except Exception:
            pass

    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=3))
    new_id = f"00{suffix}"
    try:
        with open(NODE_ID_FILE, "w", encoding="utf-8") as f:
            f.write(new_id)
    except Exception as ex:
        print(f"[!] Could not write node_id.txt: {ex}")
    return new_id

NODE_ID = get_or_create_node_id()

# ==============================================================================
# 5. FIREBASE REALTIME DATABASE CLIENT (REST API)
# ==============================================================================
class FirebaseDBClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

    def _url(self, path: str) -> str:
        clean_path = path.strip('/')
        return f"{self.base_url}/{clean_path}.json"

    def get(self, path: str):
        try:
            resp = self.session.get(self._url(path), timeout=10)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    def put(self, path: str, data):
        try:
            resp = self.session.put(self._url(path), json=data, timeout=10)
            return resp.status_code in [200, 204]
        except Exception:
            return False

    def patch(self, path: str, data):
        try:
            resp = self.session.patch(self._url(path), json=data, timeout=10)
            return resp.status_code in [200, 204]
        except Exception:
            return False

    def delete(self, path: str):
        try:
            resp = self.session.delete(self._url(path), timeout=10)
            return resp.status_code in [200, 204]
        except Exception:
            return False

db = FirebaseDBClient(FIREBASE_DATABASE_URL)

# ==============================================================================
# 6. IN-BROWSER AUTOMATION JAVASCRIPT ENGINE (ENHANCED WITH PATIENT WAITS)
# ==============================================================================
AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

// ১. পেজের প্রাথমিক পপআপ নোটিশ থাকলে তা বন্ধ করা
const initDialogConfirm = document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm"], .van-button--primary, button[class*="close"], .van-popup__close-icon');
initDialogConfirm.forEach(btn => {
    try { btn.click(); } catch(e){}
});

if (!window.location.hash.includes('login') && !window.location.href.includes('login')) {
    window.location.hash = '#/login';
}

// ২. ইনপুট এলিমেন্ট লোড হয়েছে কিনা চেক
let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input');

let elP = document.querySelector('input[type="password"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input');

let elL = document.querySelector('button[type="submit"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button') ||
          document.querySelector('button.login-btn, button[class*="login"]');

if (!elN || !elP || !elL) {
    return "NOT_READY";
}

// ৩. নিরাপদ মান সেট করার ফাংশন (Vue / React v-model সাপোর্ট)
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
    el.dispatchEvent(new Event('blur', { bubbles: true }));
};

// ফোন নম্বর সেট করা
clearAndSetVal(elN, phone);

// ৪. ধৈর্য সহকারে পাসওয়ার্ড সেট করা এবং সাবমিট বাটনে ক্লিক করা
setTimeout(() => {
    clearAndSetVal(elP, pass);
    setTimeout(() => {
        ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
            try {
                elL.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            } catch(e){}
        });
    }, 1200);
}, 1200);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

// ১. অন্য ডিভাইসে লগইন থাকলে বা ডায়ালগ কনফার্মেশন প্রম্পট
const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const dText = dialog.innerText || '';
    if (dText.includes('already logged in') || dText.includes('somewhere else') || 
        dText.includes('logged in') || dText.includes('22') || dText.includes('other device') ||
        dText.includes('Confirm') || dText.includes('Determine') || dText.includes('continue')) {
        const confirmBtn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm"], .van-button--danger, .van-button--primary, button');
        if (confirmBtn) {
            try { confirmBtn.click(); } catch(e){}
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed multi-device session prompt" };
        }
    }
}

// ২. ওয়েলকাম বা বোনাস পপআপ অটো বন্ধ করা
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

// ৩. লোকাল স্টোরেজে অথ টোকেন থাকলে লগইন সফল
try {
    const t1 = localStorage.getItem('token') || localStorage.getItem('token_str') || localStorage.getItem('auth');
    const t2 = sessionStorage.getItem('token') || sessionStorage.getItem('auth');
    if (t1 || t2) {
        return { status: "SUCCESS" };
    }
} catch(e){}

// ৪. ইউআরএল লগইন পেজ পরিবর্তন হলে সফল
if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) {
    return { status: "SUCCESS" };
}

// ৫. এরর টোস্ট ধরা
const toast = document.querySelector('.van-toast--text, .van-toast--fail, .van-toast');
if (toast && toast.innerText && toast.innerText.trim().length > 0) {
    const t = toast.innerText.trim();
    if (t.includes('already logged in') || t.includes('somewhere else') || t.includes('22')) {
        const loginBtn = document.querySelector('button[type="submit"], button.login-btn');
        if (loginBtn) {
            try { loginBtn.click(); } catch(e){}
        }
        return { status: "PENDING", message: "Resolving session handover..." };
    }
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('Account does not exist') || t.includes('frozen')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

WINGO_RUNBOX_AND_CLICK_JS = """
(function(){
    // ব্যানার বা ডায়ালগ মুছে ফেলা
    document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close"]').forEach(b => {
        try { b.click(); } catch(e){}
    });

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
    return "WAITING";
})();
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

// ডায়ালগ বন্ধ করা
document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close"], .van-dialog button').forEach(btn => {
    try { btn.click(); } catch(e){}
});

// উইনগো ৩০এস এর টাইমার বা বেটিং বাটন রেন্ডার হয়েছে কিনা যাচাই
const hasTimer = document.querySelector('.TimeLeft__C-time, [class*="TimeLeft"], [class*="countdown" i]') !== null;
const hasBetButtons = document.querySelector('.Betting__C, [class*="Betting"], .Betting__C-foot-b') !== null;

if (hasTimer || hasBetButtons || hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Time remaining') || bodyText.includes('Win Go 30S')) {
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

    const cfg={fRt:300,syncDly:2500,minSf:8};
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

            // পর্যাপ্ত সময় নিয়ে ডায়ালগ ওপেন এবং ইনপুট ফিল্ড খোঁজা (৪০ বার পর্যন্ত চেকিং)
            let checkAttempts=0,valInterval=setInterval(()=>{
                checkAttempts++;
                let inpEl=document.querySelector("input[type='number'], input.van-field__control");
                if(inpEl||checkAttempts>40){
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
                        setTimeout(()=>{if(cb)cb(true);},2500);
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
                        uSts.innerText=uF('<8S SKIP');
                        uSts.className='txt-blk-warn';
                        sessionStorage.setItem('drx_sig',cSig);
                        isFetchingApi=false;
                        return;
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
                                setTimeout(()=>{st.isTrd=false;},1500);
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
# 7. WORKER DRIVER FACTORY & SESSION CONTROLLER
# ==============================================================================
class NodeSessionWorker:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.driver = None
        self.profile_dir = os.path.join(BASE_PROFILES_DIR, f"profile_{node_id}")
        self.lock = threading.RLock()
        self.is_active = False
        self.current_chat_id = None
        self.current_site = None
        self.target_profit = 0
        self.total_steps = 7

    def init_driver(self, target_url: str):
        self.close_driver()
        os.makedirs(self.profile_dir, exist_ok=True)

        # ১. ক্রোম দিয়ে দৃশ্যমান উইন্ডো ওপেন করার চেষ্টা
        try:
            chrome_opts = ChromeOptions()
            if HEADLESS_MODE:
                chrome_opts.add_argument("--headless=new")
            
            chrome_opts.add_argument("--no-sandbox")
            chrome_opts.add_argument("--disable-dev-shm-usage")
            chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
            chrome_opts.add_argument(f"--user-data-dir={self.profile_dir}")
            chrome_opts.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
            chrome_opts.add_argument("--window-position=50,50")
            chrome_opts.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1")

            self.driver = webdriver.Chrome(options=chrome_opts)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.driver.set_window_position(50, 50)
            print(f"[+] [SUCCESS] Chrome দৃশ্যমান উইন্ডো চালু হয়েছে (নোড: {self.node_id})")
            self.driver.get(target_url)
            time.sleep(3.5) # পেজ এসেট লোড হওয়ার পর্যাপ্ত সময়
            return self.driver
        except Exception as e_chrome:
            print(f"[*] Chrome ওপেন হয়নি ({e_chrome}). ফায়ারফক্স ট্রাই করা হচ্ছে...")

        # ২. ফায়ারফক্স দিয়ে দৃশ্যমান উইন্ডো ওপেন করার চেষ্টা
        try:
            ff_opts = FirefoxOptions()
            if HEADLESS_MODE:
                ff_opts.add_argument("-headless")
            ff_opts.add_argument("-profile")
            ff_opts.add_argument(self.profile_dir)
            ff_opts.set_preference("browser.cache.disk.enable", False)
            ff_opts.set_preference("browser.cache.memory.enable", True)

            service = FirefoxService(log_output=os.devnull)
            self.driver = webdriver.Firefox(service=service, options=ff_opts)
            self.driver.set_page_load_timeout(60)
            self.driver.implicitly_wait(10)
            self.driver.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.driver.set_window_position(50, 50)
            print(f"[+] [SUCCESS] Firefox দৃশ্যমান উইন্ডো চালু হয়েছে (নোড: {self.node_id})")
            self.driver.get(target_url)
            time.sleep(3.5)
            return self.driver
        except Exception as e_ff:
            print(f"[!] ব্রাউজার চালু করা যায়নি: {e_ff}")
            raise e_ff

    def capture_base64_screenshot(self) -> str:
        if not self.driver:
            return ""
        try:
            png_bytes = self.driver.get_screenshot_as_png()
            return base64.b64encode(png_bytes).decode("utf-8")
        except Exception as ex:
            print(f"[!] Screenshot err: {ex}")
            return ""

    def close_driver(self):
        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None
            if os.path.exists(self.profile_dir):
                try:
                    shutil.rmtree(self.profile_dir, ignore_errors=True)
                except Exception:
                    pass

worker_instance = NodeSessionWorker(NODE_ID)

# ==============================================================================
# 8. HEARTBEAT DAEMON TO FIREBASE
# ==============================================================================
def heartbeat_daemon():
    while True:
        try:
            status = "BUSY" if worker_instance.is_active else "IDLE"
            db.patch(f"nodes/{NODE_ID}", {
                "status": status,
                "last_heartbeat": time.time(),
                "current_chat_id": worker_instance.current_chat_id,
                "active_site": worker_instance.current_site,
                "platform": sys.platform
            })
        except Exception as ex:
            print(f"[Heartbeat Err]: {ex}")
        time.sleep(10)

threading.Thread(target=heartbeat_daemon, daemon=True).start()

# ==============================================================================
# 9. TASK LISTENER & PATIENT AUTOMATION CONTROLLER
# ==============================================================================
def execute_task_pipeline(task_data: dict):
    action = task_data.get("action")
    chat_id = task_data.get("chat_id")

    # ==========================================
    # অ্যাকশন ১: START (লগইন ও উইন্ডো চালু)
    # ==========================================
    if action == "START":
        worker_instance.is_active = True
        worker_instance.current_chat_id = chat_id
        site = task_data.get("site", "amarclub")
        worker_instance.current_site = site
        phone = task_data.get("phone", "")
        password = task_data.get("password", "")

        db.patch(f"nodes/{NODE_ID}", {"status": "BUSY", "current_chat_id": chat_id, "active_site": site})
        db.patch(f"sessions/{chat_id}", {"status": "CONNECTING", "node_id": NODE_ID})

        login_url = URL_AMARCLUB_LOGIN if "AMAR" in site.upper() else URL_DKWIN_LOGIN

        try:
            worker_instance.init_driver(login_url)
        except Exception as ex:
            db.patch(f"sessions/{chat_id}", {"status": "ERROR", "error_message": f"Browser launch failed: {ex}"})
            worker_instance.is_active = False
            return

        # ধৈর্য সহকারে ইনপুট ফর্ম লোড হওয়া পর্যন্ত অপেক্ষা (৭০ বার x ১ সেকেন্ড)
        fill_ok = False
        for _ in range(70):
            try:
                res = worker_instance.driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
                if res == "SUCCESS":
                    fill_ok = True
                    time.sleep(3.5) # সাবমিট হওয়ার জন্য পর্যাপ্ত অপেক্ষা
                    break
            except Exception:
                pass
            time.sleep(1.0)

        if not fill_ok:
            db.patch(f"sessions/{chat_id}", {"status": "ERROR", "error_message": "লগইন ফর্ম পাওয়া যায়নি বা লোড হয়নি"})
            worker_instance.close_driver()
            worker_instance.is_active = False
            return

        # লগইন স্ট্যাটাস ভেরিফাই (৫০ বার x ১.৫ সেকেন্ড = ৭৫ সেকেন্ড পর্যন্ত ধৈর্য)
        login_success = False
        err_detail = ""
        for _ in range(50):
            try:
                res = worker_instance.driver.execute_script(CHECK_LOGIN_STATUS_JS)
                if isinstance(res, dict):
                    if res.get("status") == "SUCCESS":
                        login_success = True
                        break
                    elif res.get("status") == "CONFIRM_CLICKED":
                        time.sleep(2.0)
                        continue
                    elif res.get("status") == "ERROR":
                        err_detail = res.get("message", "ভুল তথ্য")
                        break
            except Exception:
                pass
            time.sleep(1.5)

        if not login_success:
            try:
                tok = worker_instance.driver.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")
                if tok:
                    login_success = True
            except Exception:
                pass

        if not login_success:
            db.patch(f"sessions/{chat_id}", {"status": "ERROR", "error_message": err_detail or "Login timeout"})
            worker_instance.close_driver()
            worker_instance.is_active = False
            return

        # লগইন সফল হলে উইনগো পেজে যাওয়া
        time.sleep(2.5)
        try:
            worker_instance.driver.execute_script(WINGO_RUNBOX_AND_CLICK_JS)
        except Exception:
            pass

        wingo_url = URL_AMARCLUB_WINGO if "AMAR" in site.upper() else URL_DKWIN_WINGO
        try:
            worker_instance.driver.execute_script("""
                const target = arguments[0];
                if (!window.location.href.includes('WinGo')) {
                    window.location.href = target;
                }
            """, wingo_url)
        except Exception:
            pass

        # উইনগো পেজ সম্পূর্ণ রেন্ডার হওয়া পর্যন্ত অপেক্ষা (৬০ বার x ১.২ সেকেন্ড)
        for _ in range(60):
            try:
                rdy = worker_instance.driver.execute_script(CHECK_WINGO_READY_JS)
                if rdy:
                    break
            except Exception:
                pass
            time.sleep(1.2)

        # ব্যালেন্স অনুসন্ধান (২০ বার x ১ সেকেন্ড)
        current_bal = 0.0
        for _ in range(20):
            try:
                bal = worker_instance.driver.execute_script(FETCH_BALANCE_JS)
                if bal and float(bal) > 0:
                    current_bal = float(bal)
                    break
            except Exception:
                pass
            time.sleep(1.0)

        # স্ক্রিনশট নেওয়া
        b64_snap = worker_instance.capture_base64_screenshot()

        db.patch(f"sessions/{chat_id}", {
            "status": "LOGIN_SUCCESS",
            "live_balance": current_bal,
            "screenshot_b64": b64_snap,
            "shot_delivered": False,
            "shot_caption": f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\\n\\nNode: <code>{NODE_ID}</code>\\nLive Balance: <code>৳ {current_bal:.2f}</code>\\n\\nট্রেডিং সেটআপ সম্পন্ন করুন:"
        })

    # ==========================================
    # অ্যাকশন ২: PREPARE_WINGO
    # ==========================================
    elif action == "PREPARE_WINGO":
        if worker_instance.driver:
            for _ in range(25):
                try:
                    rdy = worker_instance.driver.execute_script(CHECK_WINGO_READY_JS)
                    if rdy: break
                except Exception: pass
                time.sleep(1.0)

            cur_b = 0.0
            for _ in range(15):
                try:
                    b = worker_instance.driver.execute_script(FETCH_BALANCE_JS)
                    if b and float(b) > 0:
                        cur_b = float(b)
                        break
                except Exception: pass
                time.sleep(1.0)

            b64_snap = worker_instance.capture_base64_screenshot()
            db.patch(f"sessions/{chat_id}", {
                "live_balance": cur_b,
                "screenshot_b64": b64_snap,
                "shot_delivered": False
            })

    # ==========================================
    # অ্যাকশন ৩: RUN_CORE (মার্টিনগেল ইঞ্জিন চালু)
    # ==========================================
    elif action == "RUN_CORE":
        target = task_data.get("target_profit", 500)
        steps = task_data.get("total_steps", 7)

        if worker_instance.driver:
            try:
                worker_instance.driver.execute_script(WINGO_CORE_JS, target, steps)
            except Exception as ex:
                print(f"[!] Error injecting core: {ex}")

            time.sleep(3.0)
            b64_snap = worker_instance.capture_base64_screenshot()

            db.patch(f"sessions/{chat_id}", {
                "status": "TRADING_ACTIVE",
                "screenshot_b64": b64_snap,
                "shot_delivered": False
            })

            def monitor_node_trading_progress(cid: int):
                while worker_instance.is_active and worker_instance.driver:
                    try:
                        st = worker_instance.driver.execute_script("""
                            if (window.__WINGO_ST) {
                                return {
                                    isRun: window.__WINGO_ST.isRun,
                                    curBal: window.__WINGO_ST.curBal || 0,
                                    tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                                    startBal: window.__WINGO_ST.startBal || 0,
                                    w: window.__WINGO_ST.w || 0,
                                    l: window.__WINGO_ST.l || 0,
                                    step: (window.__WINGO_ST.stpIdx || 0) + 1,
                                    maxStep: (window.__WINGO_ST.dynSeq || []).length,
                                    cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                                    cur_l_streak: window.__WINGO_ST.cur_l_streak || 0,
                                    max_w_streak: window.__WINGO_ST.max_w_streak || 0,
                                    max_l_streak: window.__WINGO_ST.max_l_streak || 0
                                };
                            }
                            return null;
                        """)
                        if st:
                            cur_bal = float(st.get("curBal", 0))
                            tgt_amt = float(st.get("tgtAmt", 0))
                            start_bal = float(st.get("startBal", 0))

                            db.patch(f"sessions/{cid}", {
                                "live_balance": cur_bal,
                                "start_balance": start_bal,
                                "target_profit_amt": tgt_amt,
                                "live_stats": {
                                    "w": st.get("w", 0),
                                    "l": st.get("l", 0),
                                    "step": st.get("step", 1),
                                    "maxStep": st.get("maxStep", 7),
                                    "cur_w_streak": st.get("cur_w_streak", 0),
                                    "cur_l_streak": st.get("cur_l_streak", 0),
                                    "max_w_streak": st.get("max_w_streak", 0),
                                    "max_l_streak": st.get("max_l_streak", 0)
                                },
                                "last_poll_ts": time.time()
                            })

                            if cur_bal >= tgt_amt and tgt_amt > 0 and cur_bal > 0:
                                b64_win = worker_instance.capture_base64_screenshot()
                                db.patch(f"sessions/{cid}", {
                                    "status": "TARGET_ACHIEVED",
                                    "screenshot_b64": b64_win,
                                    "shot_delivered": False,
                                    "wins": st.get("w", 0),
                                    "losses": st.get("l", 0),
                                    "live_balance": cur_bal,
                                    "start_balance": start_bal
                                })
                                worker_instance.is_active = False
                                db.patch(f"nodes/{NODE_ID}", {"status": "IDLE", "current_chat_id": None})
                                break
                    except Exception as ex:
                        print(f"[Node Monitor Err]: {ex}")

                    time.sleep(3.5)

            threading.Thread(target=monitor_node_trading_progress, args=(chat_id,), daemon=True).start()

    # ==========================================
    # অ্যাকশন ৪: TAKE_SCREENSHOT
    # ==========================================
    elif action == "TAKE_SCREENSHOT":
        if worker_instance.driver:
            b64_snap = worker_instance.capture_base64_screenshot()
            db.patch(f"sessions/{chat_id}", {
                "screenshot_b64": b64_snap,
                "shot_delivered": False
            })

    # ==========================================
    # অ্যাকশন ৫: STOP
    # ==========================================
    elif action == "STOP":
        if worker_instance.driver:
            try:
                worker_instance.driver.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
            except Exception:
                pass
        worker_instance.close_driver()
        worker_instance.is_active = False
        db.patch(f"nodes/{NODE_ID}", {"status": "IDLE", "current_chat_id": None})
        db.patch(f"sessions/{chat_id}", {"status": "HALTED"})

# ==============================================================================
# 10. MAIN TASK DISPATCHER LOOP
# ==============================================================================
def main_task_listener():
    print(f"[*] {to_bold('WORKER NODE ONLINE & LISTENING')}: {NODE_ID}")
    print(f"[*] Visible GUI Mode: {not HEADLESS_MODE}")

    while True:
        try:
            task_path = f"tasks/{NODE_ID}"
            task_data = db.get(task_path)

            if task_data and isinstance(task_data, dict):
                print(f"[+] Processing Task: {task_data.get('action')}")
                db.delete(task_path)
                threading.Thread(target=execute_task_pipeline, args=(task_data,), daemon=True).start()

        except Exception as ex:
            print(f"[Task Loop Err]: {ex}")

        time.sleep(2.5)

if __name__ == "__main__":
    db.put(f"nodes/{NODE_ID}", {
        "status": "IDLE",
        "last_heartbeat": time.time(),
        "created_at": time.time(),
        "node_id": NODE_ID,
        "platform": sys.platform
    })

    main_task_listener()
