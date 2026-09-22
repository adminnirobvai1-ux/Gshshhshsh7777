import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket
import uuid
import urllib.request
import urllib.error

# ==============================================================================
# 1. Automatic Package Installer & Dynamic Dependency Resolver
# ==============================================================================
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
install_and_import("requests")

import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==============================================================================
# 2. Mathematical Bold Unicode & System Typography Engine
# ==============================================================================
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
    if not message_id or not chat_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ==============================================================================
# 3. Core System Configuration & Constants
# ==============================================================================
TOKEN = "8808949150:AAFCCjX99fBse7qtfmz3PksuxC_cbWCaUMc"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

OWNER_HANDLE = "@MD_NAYEEM_DRX_TM"
OWNER_URL = "https://t.me/MD_NAYEEM_DRX_TM"
CHANNEL_USERNAME = "@DARK67HACK"
CHANNEL_URL = "https://t.me/DARK67HACK"

FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

user_sessions = {}
active_sessions = {}
OWNER_CHAT_IDS = set()

SPINNER_FRAMES = ["-", "\\", "|", "/"]

# Generate Deterministic Cluster Node Identifier
CURRENT_HOSTNAME = socket.gethostname().upper().replace(" ", "_")
CURRENT_PID = os.getpid()
RANDOM_HEX = uuid.uuid4().hex[:6].upper()
CURRENT_TERMINAL_ID = f"NODE_{CURRENT_HOSTNAME}_{CURRENT_PID}_{RANDOM_HEX}"

IS_MASTER = False
POLLING_ACTIVE = False
CLUSTER_RUNNING = True

# ==============================================================================
# 4. Distributed Firebase Realtime Database Client
# ==============================================================================
class FirebaseClusterClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _build_url(self, path: str) -> str:
        clean_path = path.strip("/")
        return f"{self.base_url}/{clean_path}.json"

    def get(self, path: str):
        url = self._build_url(path)
        try:
            res = self.session.get(url, timeout=6)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception as e:
            return None

    def put(self, path: str, data):
        url = self._build_url(path)
        try:
            res = self.session.put(url, json=data, timeout=6)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception as e:
            return None

    def patch(self, path: str, data):
        url = self._build_url(path)
        try:
            res = self.session.patch(url, json=data, timeout=6)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception as e:
            return None

    def delete(self, path: str):
        url = self._build_url(path)
        try:
            res = self.session.delete(url, timeout=6)
            return res.status_code == 200
        except Exception as e:
            return False

firebase = FirebaseClusterClient(FIREBASE_DATABASE_URL)

# ==============================================================================
# 5. In-Browser JavaScript Automation Code (Preserved Verbatim)
# ==============================================================================
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

# ==============================================================================
# 6. Isolated Browser Session Engine (One Driver Per Terminal Node)
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("-profile")
    options.add_argument(profile_dir)
    
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)

    service = FirefoxService(log_output=os.devnull)
    
    driver = webdriver.Firefox(service=service, options=options)
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
        
        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

# ==============================================================================
# 7. Telegram Live Image Engine & UI Card Renderers
# ==============================================================================
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

# ==============================================================================
# 8. Multilingual Card Templates & Text Generators
# ==============================================================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('WINGO 30S VIP AUTOMATION')}              │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ স্বাগতম আপনাকে প্রিমিয়াম উইনগো ট্রেডিং  │\n"
                f"│ অটোমেশন প্ল্যাটফর্মে।                   │\n"
                f"│ দয়া করে আপনার ভাষা নির্বাচন করুন:     │\n"
                f"└────────────────────────────────────────┘"
            ),
            "choose_site": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('SELECT PLATFORM')}                    │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ আসসালামু আলাইকুম, দয়া করে আপনার একটি  │\n"
                f"│ ট্রেডিং সাইট নির্বাচন করুন:             │\n"
                f"└────────────────────────────────────────┘"
            ),
            "credentials_card": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT LOGIN')}                       │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ প্ল্যাটফর্ম: {kwargs.get('site_name', '')}\n"
                f"│ আসসালামু আলাইকুম, দয়া করে নিচের বাটন   │\n"
                f"│ চেপে নাম্বার ও পাসওয়ার্ড ইনপুট দিন।   │\n"
                f"│ এটি কাজ শেষে চ্যাট থেকে মুছে যাবে।    │\n"
                f"└────────────────────────────────────────┘"
            ),
            "ask_number": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT NUMBER')}                     │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ আপনার একাউন্ট নাম্বার (ফোন) পাঠান:    │\n"
                f"└────────────────────────────────────────┘"
            ),
            "ask_password": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT PASSWORD')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ আপনার একাউন্টের পাসওয়ার্ড পাঠান:      │\n"
                f"└────────────────────────────────────────┘"
            ),
            "login_success": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('LOGIN SUCCESSFUL')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform : {kwargs.get('site_name', '')}\n"
                f"│ Account  : {kwargs.get('phone', '')}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ লগইন সফল হয়েছে। ট্রেডিং শুরু করতে     │\n"
                f"│ নিচে START বাটন চাপুন:                 │\n"
                f"└────────────────────────────────────────┘"
            ),
            "login_failed": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('LOGIN FAILED')}                       │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform : {kwargs.get('site_name', '')}\n"
                f"│ Reason   : {kwargs.get('error', 'ভুল তথ্য বা টাইমআউট')}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ পুনরায় চেষ্টা করতে /start চাপুন।        │\n"
                f"└────────────────────────────────────────┘"
            ),
            "input_target": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('TARGET PROFIT')}                      │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ বর্তমান ব্যালেন্স: ৳ {kwargs.get('balance', '0.00')}\n"
                f"│ কত টাকা প্রফিট করতে চান? লিখুন         │\n"
                f"│ (যেমন: 500):                           │\n"
                f"└────────────────────────────────────────┘"
            ),
            "input_steps": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('MARTINGALE STEPS')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ টার্গেট প্রফিট: ৳ {kwargs.get('target', 0)}\n"
                f"│ ব্যাকআপ স্টেপ সংখ্যা লিখুন            │\n"
                f"│ (যেমন: 7 বা 10):                       │\n"
                f"└────────────────────────────────────────┘"
            ),
            "running_dashboard": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('24/7 AUTOMATION ENGINE ACTIVE')}      │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform       : {kwargs.get('site_name', '')}\n"
                f"│ Start Balance  : ৳ {kwargs.get('start_bal', '0.00')}\n"
                f"│ Target Balance : ৳ {kwargs.get('target_bal', '0.00')}\n"
                f"│ Total Steps    : {kwargs.get('steps', 7)}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ STATUS : মার্টিনগেল ইঞ্জিন সচল রয়েছে  │\n"
                f"└────────────────────────────────────────┘"
            ),
            "cancelled": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('SESSION TERMINATED')}                 │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে।      │\n"
                f"│ পুনরায় শুরু করতে /start পাঠান।         │\n"
                f"└────────────────────────────────────────┘"
            )
        },
        "en": {
            "welcome": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('WINGO 30S VIP AUTOMATION')}              │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Welcome to the high-tech WinGo Auto   │\n"
                f"│ Trading Distributed Engine.            │\n"
                f"│ Please select your preferred language: │\n"
                f"└────────────────────────────────────────┘"
            ),
            "choose_site": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('SELECT PLATFORM')}                    │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Please select your trading platform:   │\n"
                f"└────────────────────────────────────────┘"
            ),
            "credentials_card": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT LOGIN')}                       │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform : {kwargs.get('site_name', '')}\n"
                f"│ Tap buttons below to submit Phone and  │\n"
                f"│ Password. Data will be auto-deleted.   │\n"
                f"└────────────────────────────────────────┘"
            ),
            "ask_number": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT NUMBER')}                     │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Enter your account phone number:       │\n"
                f"└────────────────────────────────────────┘"
            ),
            "ask_password": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ACCOUNT PASSWORD')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Enter your account password:           │\n"
                f"└────────────────────────────────────────┘"
            ),
            "login_success": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('LOGIN SUCCESSFUL')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform : {kwargs.get('site_name', '')}\n"
                f"│ Account  : {kwargs.get('phone', '')}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Login verified. Press START below to   │\n"
                f"│ configure automated trading parameters │\n"
                f"└────────────────────────────────────────┘"
            ),
            "login_failed": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('LOGIN FAILED')}                       │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform : {kwargs.get('site_name', '')}\n"
                f"│ Reason   : {kwargs.get('error', 'Invalid credentials')}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Type /start to retry authentication.   │\n"
                f"└────────────────────────────────────────┘"
            ),
            "input_target": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('TARGET PROFIT')}                      │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Live Balance : ৳ {kwargs.get('balance', '0.00')}\n"
                f"│ Enter target profit amount (e.g. 500): │\n"
                f"└────────────────────────────────────────┘"
            ),
            "input_steps": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('MARTINGALE STEPS')}                   │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Target Profit : ৳ {kwargs.get('target', 0)}\n"
                f"│ Enter Martingale steps (e.g. 7 or 10): │\n"
                f"└────────────────────────────────────────┘"
            ),
            "running_dashboard": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('24/7 AUTOMATION ENGINE ACTIVE')}      │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform       : {kwargs.get('site_name', '')}\n"
                f"│ Start Balance  : ৳ {kwargs.get('start_bal', '0.00')}\n"
                f"│ Target Balance : ৳ {kwargs.get('target_bal', '0.00')}\n"
                f"│ Total Steps    : {kwargs.get('steps', 7)}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ STATUS : Martingale running 24/7       │\n"
                f"└────────────────────────────────────────┘"
            ),
            "cancelled": (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('SESSION TERMINATED')}                 │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Session closed cleanly.                │\n"
                f"│ Send /start to begin a new session.    │\n"
                f"└────────────────────────────────────────┘"
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

# ==============================================================================
# 9. Inline Keyboards & Menu Controllers
# ==============================================================================
def get_channel_gateway_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('CHANNEL')}", url=CHANNEL_URL),
        InlineKeyboardButton(f"{to_bold('VERIFY')}", callback_data="verify_join_gate")
    )
    return markup

def get_stage2_auth_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('PASS / PREMIUM')}", callback_data="gate_pass_auth"),
        InlineKeyboardButton(f"{to_bold('OWNER ID')}", url=OWNER_URL)
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
        InlineKeyboardButton(f"{to_bold(f'STOP [{spinner}]')}", callback_data=f"stop:{sid}")
    )
    return markup

def get_admin_pass_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('CREATE PASSWORD')}", callback_data="admin_create_pass"),
        InlineKeyboardButton(f"{to_bold('DELETE PASSWORD')}", callback_data="admin_list_delete_pass")
    )
    return markup

# ==============================================================================
# 10. Login Execution, Navigation & Trading Logic
# ==============================================================================
def play_clean_login_animation(chat_id, msg_id):
    frames = [
        f"┌────────────────────────────────────────┐\n│ {to_bold('CONNECTING REMOTE ENGINE')}            │\n├────────────────────────────────────────┤\n│ [=---------] 10% Allocating node...    │\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('INITIALIZING TARGET PLATFORM')}       │\n├────────────────────────────────────────┤\n│ [===-------] 35% Isolated browser up...│\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('INJECTING AUTHENTICATION DATA')}      │\n├────────────────────────────────────────┤\n│ [======----] 65% Auto-filling data...  │\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('VERIFYING ACTIVE SESSION')}          │\n├────────────────────────────────────────┤\n│ [==========] 100% Verification done!   │\n└────────────────────────────────────────┘"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.4)

def play_pass_auth_animation(chat_id, msg_id):
    frames = [
        f"┌────────────────────────────────────────┐\n│ {to_bold('CONNECTING REMOTE ENGINE...')}         │\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('INITIALIZING TERMINAL ALLOCATION...')} │\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('VERIFYING 24-HOUR ACCESS TOKEN...')}   │\n└────────────────────────────────────────┘",
        f"┌────────────────────────────────────────┐\n│ {to_bold('TERMINAL BOUND SUCCESSFULLY!')}        │\n└────────────────────────────────────────┘"
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
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error="লগইন ফর্ম পাওয়া যায়নি"))
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
        f"┌────────────────────────────────────────┐\n"
        f"│ {to_bold('WINGO 30S MARKET ACTIVE')}              │\n"
        f"├────────────────────────────────────────┤\n"
        f"│ Platform     : {site_name}\n"
        f"│ Live Balance : ৳ {current_bal:.2f}\n"
        f"├────────────────────────────────────────┤\n"
        f"│ নিচের বাটন চেপে টার্গেট ও স্টেপস সেট করুন:│\n"
        f"└────────────────────────────────────────┘"
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
                    f"┌────────────────────────────────────────┐\n"
                    f"│ {to_bold('TARGET ACHIEVED SUCCESSFULLY')}        │\n"
                    f"├────────────────────────────────────────┤\n"
                    f"│ শুরুর ব্যালেন্স : ৳ {start_b:.2f}\n"
                    f"│ শেষ ব্যালেন্স  : ৳ {sess['cur_bal']:.2f}\n"
                    f"│ অর্জিত প্রফিট  : +৳ {profit:.2f}\n"
                    f"│ মোট উইন       : {sess['wins']} | লস: {sess['losses']}\n"
                    f"└────────────────────────────────────────┘"
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

# ==============================================================================
# 11. Distributed Cluster Management, Master Election & Worker Loops
# ==============================================================================
def register_terminal_node():
    node_data = {
        "terminal_id": CURRENT_TERMINAL_ID,
        "status": "FREE",
        "assigned_user_id": None,
        "active_platform": None,
        "last_heartbeat": time.time(),
        "expires_at": None,
        "task": None
    }
    firebase.put(f"terminals/{CURRENT_TERMINAL_ID}", node_data)
    print(f"[*] Terminal Registered in Cluster: {CURRENT_TERMINAL_ID}")

def update_terminal_heartbeat():
    while CLUSTER_RUNNING:
        try:
            firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}", {
                "last_heartbeat": time.time()
            })
        except Exception:
            pass
        time.sleep(5)

def reset_terminal_node_state(tid=CURRENT_TERMINAL_ID):
    firebase.patch(f"terminals/{tid}", {
        "status": "FREE",
        "assigned_user_id": None,
        "active_platform": None,
        "expires_at": None,
        "task": None
    })
    for sid in list(active_sessions.keys()):
        close_session_tab(sid)

def master_election_engine():
    global IS_MASTER, POLLING_ACTIVE
    while CLUSTER_RUNNING:
        try:
            now = time.time()
            lock = firebase.get("cluster/master_lock")
            
            can_claim = False
            if not lock or not isinstance(lock, dict):
                can_claim = True
            else:
                master_id = lock.get("master_id")
                last_hb = lock.get("last_heartbeat", 0)
                if master_id == CURRENT_TERMINAL_ID:
                    can_claim = True
                elif (now - last_hb) > 15.0:
                    can_claim = True

            if can_claim:
                claim_payload = {
                    "master_id": CURRENT_TERMINAL_ID,
                    "last_heartbeat": now
                }
                res = firebase.put("cluster/master_lock", claim_payload)
                if res and res.get("master_id") == CURRENT_TERMINAL_ID:
                    if not IS_MASTER:
                        print(f"[*] [CLUSTER ELECTION] Master lock acquired by {CURRENT_TERMINAL_ID}!")
                    IS_MASTER = True
                else:
                    IS_MASTER = False
            else:
                if IS_MASTER:
                    print(f"[*] [CLUSTER ELECTION] Stepping down as Master on {CURRENT_TERMINAL_ID}.")
                IS_MASTER = False

            if IS_MASTER and not POLLING_ACTIVE:
                threading.Thread(target=start_master_bot_polling, daemon=True).start()
            elif not IS_MASTER and POLLING_ACTIVE:
                try:
                    bot.stop_polling()
                except Exception:
                    pass

        except Exception as e:
            pass
        time.sleep(4)

def start_master_bot_polling():
    global POLLING_ACTIVE
    if POLLING_ACTIVE:
        return
    POLLING_ACTIVE = True
    print(f"[*] TELEGRAM MASTER ENGINE ACTIVE: Polling initialized on {CURRENT_TERMINAL_ID}")
    while IS_MASTER and CLUSTER_RUNNING:
        try:
            bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
        except Exception as e:
            time.sleep(2)
    POLLING_ACTIVE = False

def worker_task_listener():
    while CLUSTER_RUNNING:
        try:
            node = firebase.get(f"terminals/{CURRENT_TERMINAL_ID}")
            if node and isinstance(node, dict):
                status = node.get("status")
                
                # Check Remote Force-Kill Flag
                if status == "FORCE_KILL":
                    print(f"[*] FORCE_KILL detected on {CURRENT_TERMINAL_ID}. Shutting down sessions...")
                    reset_terminal_node_state(CURRENT_TERMINAL_ID)
                    for admin_id in list(OWNER_CHAT_IDS):
                        try:
                            msg = (
                                f"┌────────────────────────────────────────┐\n"
                                f"│ {to_bold('TERMINAL FORCE KILL CONFIRMED')}     │\n"
                                f"├────────────────────────────────────────┤\n"
                                f"│ Terminal : {CURRENT_TERMINAL_ID}\n"
                                f"│ Status   : RESET TO FREE SLOTS         │\n"
                                f"└────────────────────────────────────────┘"
                            )
                            bot.send_message(admin_id, msg)
                        except Exception:
                            pass
                    time.sleep(2)
                    continue

                # Process Task Queue
                task = node.get("task")
                if task and isinstance(task, dict) and task.get("status") == "PENDING":
                    firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "PROCESSING"})
                    action = task.get("action")
                    chat_id = task.get("chat_id")
                    sid = task.get("session_id")
                    
                    if action == "LOGIN":
                        phone = task.get("phone")
                        password = task.get("password")
                        site_name = task.get("site_name", "Amar Club")
                        anim_msg_id = task.get("anim_msg_id")
                        
                        active_sessions[sid] = {
                            "chat_id": chat_id,
                            "session_id": sid,
                            "site_name": site_name,
                            "phone": phone,
                            "password": password,
                            "target_profit": 0,
                            "total_steps": 7,
                            "is_trading": False,
                            "created_at": time.time(),
                            "anim_tick": 0,
                            "lock": threading.RLock()
                        }
                        process_login(chat_id, sid, phone, password, anim_msg_id)
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "START_WINGO":
                        prepare_wingo_parameters(chat_id, sid)
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "RUN_AUTO":
                        sess = active_sessions.get(sid)
                        if sess:
                            sess["target_profit"] = task.get("target_profit", 500)
                            sess["total_steps"] = task.get("total_steps", 7)
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
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "SHOT":
                        sess = active_sessions.get(sid)
                        if sess:
                            temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
                            def _shot(drv):
                                drv.save_screenshot(temp_shot)
                            safe_tab_execute(sid, _shot)
                            if os.path.exists(temp_shot):
                                cur_b = sess.get("cur_bal", sess.get("current_balance", 0.0))
                                t_total = sess.get("start_bal", 0.0) + sess.get("target_profit", 0.0)
                                caption = (
                                    f"┌────────────────────────────────────────┐\n"
                                    f"│ {to_bold('24/7 AUTOMATION ENGINE ACTIVE')}      │\n"
                                    f"├────────────────────────────────────────┤\n"
                                    f"│ Platform     : {sess.get('site_name', '')}\n"
                                    f"│ Live Balance : ৳ {cur_b:.2f}\n"
                                    f"│ Target Total : ৳ {t_total:.2f}\n"
                                    f"│ Total Steps  : {sess.get('total_steps', 7)}\n"
                                    f"│ Time         : {time.strftime('%H:%M:%S')}\n"
                                    f"└────────────────────────────────────────┘"
                                )
                                display_or_replace_photo(chat_id, sid, temp_shot, caption, get_trading_control_keyboard(sid))
                                try:
                                    os.remove(temp_shot)
                                except Exception:
                                    pass
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "BAL":
                        def _bal(drv):
                            return drv.execute_script(FETCH_BALANCE_JS)
                        b_val = safe_tab_execute(sid, _bal)
                        if b_val is not None:
                            bot.send_message(chat_id, f"<b>Live Balance:</b> <code>৳ {b_val:.2f}</code>")
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "STATS":
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
                                f"┌────────────────────────────────────────┐\n"
                                f"│ {to_bold('LIVE STATS REPORT')}                 │\n"
                                f"├────────────────────────────────────────┤\n"
                                f"│ ব্যালেন্স  : ৳ {data_rep['curBal']:.2f}\n"
                                f"│ টার্গেট   : ৳ {data_rep['tgtAmt']:.2f}\n"
                                f"│ মার্টিনগেল : Step {data_rep['step']}/{data_rep['maxStep']}\n"
                                f"│ উইন      : {data_rep['w']} | লস: {data_rep['l']}\n"
                                f"└────────────────────────────────────────┘"
                            )
                            bot.send_message(chat_id, stat_txt)
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "STOP":
                        sess = active_sessions.get(sid)
                        if sess:
                            def _stop(drv):
                                drv.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
                            safe_tab_execute(sid, _stop)
                            sess["is_trading"] = False
                            bot.send_message(chat_id, f"┌────────────────────────────────────────┐\n│ {to_bold('TRADING PAUSED')}                    │\n├────────────────────────────────────────┤\n│ ট্রেডিং অটোমেশন সাময়িকভাবে বন্ধ হয়েছে। │\n└────────────────────────────────────────┘")
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

                    elif action == "CANCEL":
                        close_session_tab(sid)
                        bot.send_message(chat_id, get_text(chat_id, "cancelled"))
                        firebase.patch(f"terminals/{CURRENT_TERMINAL_ID}/task", {"status": "COMPLETED"})

        except Exception as e:
            pass
        time.sleep(0.8)

# ==============================================================================
# 12. 24-Hour Watchdog Thread & Allocation Manager
# ==============================================================================
def continuous_24h_watchdog():
    while CLUSTER_RUNNING:
        try:
            now = time.time()
            # 1. Local terminal check
            node = firebase.get(f"terminals/{CURRENT_TERMINAL_ID}")
            if node and isinstance(node, dict):
                exp = node.get("expires_at")
                if exp and now >= exp:
                    uid = node.get("assigned_user_id")
                    reset_terminal_node_state(CURRENT_TERMINAL_ID)
                    if uid:
                        exp_msg = (
                            f"┌────────────────────────────────────────┐\n"
                            f"│ {to_bold('24-HOUR DEDICATED ACCESS EXPIRED')}   │\n"
                            f"├────────────────────────────────────────┤\n"
                            f"│ আপনার ২৪ ঘণ্টার অ্যাক্সেসের মেয়াদ শেষ  │\n"
                            f"│ হয়েছে। নতুন অ্যাক্সেস নিতে এডমিনের    │\n"
                            f"│ সাথে যোগাযোগ করুন।                     │\n"
                            f"└────────────────────────────────────────┘"
                        )
                        markup = InlineKeyboardMarkup()
                        markup.add(InlineKeyboardButton(f"{to_bold('OWNER ID')}", url=OWNER_URL))
                        try:
                            bot.send_message(uid, exp_msg, reply_markup=markup)
                        except Exception:
                            pass

            # 2. Master node cluster cleanup
            if IS_MASTER:
                terminals = firebase.get("terminals") or {}
                for tid, tdata in terminals.items():
                    if isinstance(tdata, dict) and tdata.get("status") == "BUSY":
                        t_exp = tdata.get("expires_at")
                        if t_exp and now >= t_exp:
                            uid = tdata.get("assigned_user_id")
                            firebase.patch(f"terminals/{tid}", {
                                "status": "FREE",
                                "assigned_user_id": None,
                                "active_platform": None,
                                "expires_at": None,
                                "task": None
                            })
                            if uid:
                                exp_msg = (
                                    f"┌────────────────────────────────────────┐\n"
                                    f"│ {to_bold('24-HOUR DEDICATED ACCESS EXPIRED')}   │\n"
                                    f"├────────────────────────────────────────┤\n"
                                    f"│ আপনার ২৪ ঘণ্টার অ্যাক্সেসের মেয়াদ শেষ  │\n"
                                    f"│ হয়েছে। নতুন অ্যাক্সেস নিতে এডমিনের    │\n"
                                    f"│ সাথে যোগাযোগ করুন।                     │\n"
                                    f"└────────────────────────────────────────┘"
                                )
                                markup = InlineKeyboardMarkup()
                                markup.add(InlineKeyboardButton(f"{to_bold('OWNER ID')}", url=OWNER_URL))
                                try:
                                    bot.send_message(uid, exp_msg, reply_markup=markup)
                                except Exception:
                                    pass

        except Exception as e:
            pass
        time.sleep(15)

def allocate_free_terminal(chat_id):
    terminals = firebase.get("terminals") or {}
    now = time.time()
    
    # Check if user is already bound to an active terminal
    for tid, tdata in terminals.items():
        if isinstance(tdata, dict):
            if tdata.get("assigned_user_id") == chat_id and tdata.get("status") == "BUSY":
                if tdata.get("expires_at", 0) > now:
                    return tid
                else:
                    reset_terminal_node_state(tid)

    # Search for an available FREE terminal slot
    for tid, tdata in terminals.items():
        if isinstance(tdata, dict):
            last_hb = tdata.get("last_heartbeat", 0)
            if tdata.get("status") == "FREE" and (now - last_hb) <= 25.0:
                expires_at = now + 86400
                firebase.patch(f"terminals/{tid}", {
                    "status": "BUSY",
                    "assigned_user_id": chat_id,
                    "expires_at": expires_at
                })
                return tid

    return None

def dispatch_cluster_task(target_tid, task_dict):
    if target_tid == CURRENT_TERMINAL_ID:
        pass
    firebase.put(f"terminals/{target_tid}/task", task_dict)

# ==============================================================================
# 13. Channel Gateway & Authorization Checkers
# ==============================================================================
def is_owner(user_obj) -> bool:
    if not user_obj:
        return False
    if user_obj.username and user_obj.username.lower() == "md_nayeem_drx_tm":
        OWNER_CHAT_IDS.add(user_obj.id)
        return True
    if user_obj.id in OWNER_CHAT_IDS:
        return True
    return False

def verify_channel_member(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ==============================================================================
# 14. Telegram Bot Command & Flow Handlers
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user = message.from_user
    safe_delete_message(chat_id, message.message_id)

    if is_owner(user):
        OWNER_CHAT_IDS.add(chat_id)

    # Mandatory Channel Gateway Check for regular users
    if not is_owner(user) and not verify_channel_member(user.id):
        greeting_card = (
            f"┌────────────────────────────────────────┐\n"
            f"│ {to_bold('MANDATORY CHANNEL GATEWAY')}          │\n"
            f"├────────────────────────────────────────┤\n"
            f"│ আসসালামু আলাইকুম, আশা করি আপনি ভালো আছেন।│\n"
            f"│ আপনি আমার চ্যানেলটি জয়েন করুন।         │\n"
            f"└────────────────────────────────────────┘"
        )
        bot.send_message(chat_id, greeting_card, reply_markup=get_channel_gateway_keyboard())
        return

    # User is verified or owner: Navigate to Stage 2
    user_sessions[chat_id] = {
        "step": "STAGE_2_AUTH",
        "lang": "bn"
    }

    stage2_msg = (
        f"┌────────────────────────────────────────┐\n"
        f"│ {to_bold('WINGO 30S CLUSTER ACCESS')}             │\n"
        f"├────────────────────────────────────────┤\n"
        f"│ ভাষা নির্বাচন করুন এবং অ্যাক্সেস নিতে    │\n"
        f"│ আপনার ২৪ ঘণ্টার পাসওয়ার্ড ইনপুট করুন:   │\n"
        f"└────────────────────────────────────────┘"
    )
    bot.send_message(chat_id, stage2_msg, reply_markup=get_stage2_auth_keyboard())

@bot.message_handler(commands=['pass'])
def handle_admin_pass_command(message):
    chat_id = message.chat.id
    if not is_owner(message.from_user):
        return
    OWNER_CHAT_IDS.add(chat_id)
    safe_delete_message(chat_id, message.message_id)

    msg = (
        f"┌────────────────────────────────────────┐\n"
        f"│ {to_bold('CLUSTER PASSWORD CONTROLLER')}        │\n"
        f"├────────────────────────────────────────┤\n"
        f"│ Choose an action to generate or revoke │\n"
        f"│ 24-hour single-user access keys:       │\n"
        f"└────────────────────────────────────────┘"
    )
    bot.send_message(chat_id, msg, reply_markup=get_admin_pass_menu_keyboard())

@bot.message_handler(commands=['admin', 'terminals'])
def handle_admin_terminals_command(message):
    chat_id = message.chat.id
    if not is_owner(message.from_user):
        return
    OWNER_CHAT_IDS.add(chat_id)
    safe_delete_message(chat_id, message.message_id)

    render_cluster_telemetry(chat_id)

@bot.message_handler(commands=['kick'])
def handle_admin_kick_command(message):
    chat_id = message.chat.id
    if not is_owner(message.from_user):
        return
    safe_delete_message(chat_id, message.message_id)

    parts = message.text.strip().split()
    if len(parts) > 1:
        target_tid = parts[1].strip()
        firebase.patch(f"terminals/{target_tid}", {"status": "FORCE_KILL"})
        bot.send_message(chat_id, f"[*] Signal FORCE_KILL sent to terminal: <code>{target_tid}</code>")
    else:
        bot.send_message(chat_id, "Usage: <code>/kick &lt;TERMINAL_ID&gt;</code>")

def render_cluster_telemetry(chat_id):
    terminals = firebase.get("terminals") or {}
    now = time.time()
    online_nodes = []
    busy_count = 0
    free_count = 0

    for tid, node in terminals.items():
        if isinstance(node, dict):
            last_hb = node.get("last_heartbeat", 0)
            if (now - last_hb) <= 25.0:
                online_nodes.append(node)
                if node.get("status") == "BUSY":
                    busy_count += 1
                else:
                    free_count += 1

    total_online = len(online_nodes)

    lines = [
        "┌────────────────────────────────────────────────────────┐",
        f"│ {to_bold('CLUSTER TERMINAL CONTROLLER')}                            │",
        "├────────────────────────────────────────────────────────┤",
        f"│ TOTAL TERMINALS ONLINE : {str(total_online):<30}│",
        f"│ ACTIVE BUSY SESSIONS   : {str(busy_count):<30}│",
        f"│ AVAILABLE FREE SLOTS   : {str(free_count):<30}│",
        "├────────────────────────────────────────────────────────┤",
        "│ Terminal ID       │ Status   │ Active Site │ User ID   │",
        "├───────────────────┼──────────┼─────────────┼───────────┤"
    ]

    markup = InlineKeyboardMarkup()
    for n in online_nodes:
        tid = str(n.get("terminal_id", "UNKNOWN"))
        tid_short = tid[-17:] if len(tid) > 17 else tid
        status = str(n.get("status", "FREE"))[:8]
        site = str(n.get("active_platform") or "NONE")[:11]
        uid = str(n.get("assigned_user_id") or "NONE")[:9]
        lines.append(f"│ {tid_short:<17} │ {status:<8} │ {site:<11} │ {uid:<9} │")

        if n.get("status") == "BUSY":
            markup.add(InlineKeyboardButton(f"{to_bold('KILL')}: {tid_short}", callback_data=f"kill_node:{tid}"))

    if not online_nodes:
        lines.append("│ NO CLUSTER TERMINALS CURRENTLY ONLINE                  │")

    lines.append("└────────────────────────────────────────────────────────┘")
    table_text = f"<pre>{chr(10).join(lines)}</pre>"
    bot.send_message(chat_id, table_text, reply_markup=markup if len(markup.keyboard) > 0 else None)

# ==============================================================================
# 15. Callback Query Routing Engine
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    # Gate Verification Callback
    if action == "verify_join_gate":
        if verify_channel_member(call.from_user.id):
            safe_delete_message(chat_id, call.message.message_id)
            user_sessions[chat_id] = {"step": "STAGE_2_AUTH", "lang": "bn"}
            stage2_msg = (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('WINGO 30S CLUSTER ACCESS')}             │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ ভাষা নির্বাচন করুন এবং অ্যাক্সেস নিতে    │\n"
                f"│ আপনার ২৪ ঘণ্টার পাসওয়ার্ড ইনপুট করুন:   │\n"
                f"└────────────────────────────────────────┘"
            )
            bot.send_message(chat_id, stage2_msg, reply_markup=get_stage2_auth_keyboard())
        else:
            bot.answer_callback_query(call.id, "দয়া করে আগে চ্যানেলে জয়েন করুন।", show_alert=True)

    # Admin Pass Creation
    elif action == "admin_create_pass":
        if not is_owner(call.from_user):
            bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        
        raw_key = f"DRX-{uuid.uuid4().hex[:6].upper()}"
        now = time.time()
        pass_record = {
            "password": raw_key,
            "created_at": now,
            "expires_at": now + 86400,
            "is_used": False,
            "bound_user_id": None,
            "bound_terminal_id": None
        }
        firebase.put(f"passwords/{raw_key}", pass_record)
        
        conf_msg = (
            f"┌────────────────────────────────────────┐\n"
            f"│ {to_bold('24-HOUR ACCESS TOKEN CREATED')}        │\n"
            f"├────────────────────────────────────────┤\n"
            f"│ KEY        : <code>{raw_key}</code>\n"
            f"│ DURATION   : 24 HOURS\n"
            f"│ EXPIRES IN : 86400 SECONDS             │\n"
            f"└────────────────────────────────────────┘"
        )
        bot.send_message(chat_id, conf_msg)

    # Admin Pass List & Deletion
    elif action == "admin_list_delete_pass":
        if not is_owner(call.from_user):
            bot.answer_callback_query(call.id, "Unauthorized.", show_alert=True)
            return
        bot.answer_callback_query(call.id)
        
        passwords = firebase.get("passwords") or {}
        markup = InlineKeyboardMarkup()
        for pkey in list(passwords.keys())[:20]:
            markup.add(InlineKeyboardButton(f"{to_bold('REVOKE')}: {pkey}", callback_data=f"del_pass:{pkey}"))
            
        if not passwords:
            bot.send_message(chat_id, "No active access keys in database.")
        else:
            bot.send_message(chat_id, "Select a password to revoke immediately:", reply_markup=markup)

    elif action == "del_pass" and sid:
        if not is_owner(call.from_user):
            return
        firebase.delete(f"passwords/{sid}")
        bot.answer_callback_query(call.id, f"Password {sid} deleted!", show_alert=True)
        safe_delete_message(chat_id, call.message.message_id)

    # Admin Remote Terminal Kill
    elif action == "kill_node" and sid:
        if not is_owner(call.from_user):
            return
        firebase.patch(f"terminals/{sid}", {"status": "FORCE_KILL"})
        bot.answer_callback_query(call.id, f"KILL signal sent to {sid}", show_alert=True)

    # Language Switchers
    elif action in ["lang_en", "lang_bn"]:
        u = user_sessions.setdefault(chat_id, {})
        u["lang"] = "en" if action == "lang_en" else "bn"
        bot.answer_callback_query(call.id, f"Language set to {u['lang'].upper()}")

    # Stage 2: Prompt for Password
    elif action == "gate_pass_auth":
        u = user_sessions.setdefault(chat_id, {})
        u["step"] = "WAITING_GATE_PASSWORD"
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, "দয়া করে আপনার ২৪ ঘণ্টার অ্যাক্সেস পাসওয়ার্ডটি ইনপুট করুন:")
        u["pass_prompt_msg_id"] = prompt_m.message_id

    # Platform Selector
    elif action in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if action == "site_amarclub" else "DK Win"
        assigned_tid = user_sessions.get(chat_id, {}).get("assigned_terminal_id")
        
        if not assigned_tid:
            bot.answer_callback_query(call.id, "সেশন পাওয়া যায়নি, পুনরায় /start দিন", show_alert=True)
            return

        sid = f"{chat_id}_{int(time.time()) % 1000000}"
        user_sessions[chat_id]["active_sid"] = sid

        firebase.patch(f"terminals/{assigned_tid}", {
            "active_platform": site_name
        })

        active_sessions[sid] = {
            "chat_id": chat_id,
            "session_id": sid,
            "terminal_id": assigned_tid,
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

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_card", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    # Phone Input Trigger
    elif action == "ask_num" and sid:
        sess = active_sessions.get(sid, {})
        sess["input_mode"] = "WAITING_PHONE"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_number"))
        sess["temp_prompt_id"] = prompt_m.message_id

    # Password Input Trigger
    elif action == "ask_pass" and sid:
        sess = active_sessions.get(sid, {})
        if not sess.get("phone"):
            bot.answer_callback_query(call.id, "দয়া করে আগে নাম্বারটি প্রদান করুন।", show_alert=True)
            return
        sess["input_mode"] = "WAITING_PASS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_password"))
        sess["temp_prompt_id"] = prompt_m.message_id

    # Start WinGo Setup
    elif action == "start_cfg" and sid:
        bot.answer_callback_query(call.id, "উইনগো মার্কেট পেজ প্রস্তুত হচ্ছে...")
        assigned_tid = user_sessions.get(chat_id, {}).get("assigned_terminal_id", CURRENT_TERMINAL_ID)
        dispatch_cluster_task(assigned_tid, {
            "task_id": f"T_{int(time.time())}",
            "action": "START_WINGO",
            "chat_id": chat_id,
            "session_id": sid,
            "status": "PENDING"
        })

    # Set Target Profit
    elif action == "set_tgt" and sid:
        sess = active_sessions.get(sid, {})
        sess["input_mode"] = "WAITING_TARGET"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = sess.get("current_balance", 0.0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_target", balance=f"{cur_bal:.2f}"))
        sess["temp_prompt_id"] = p_msg.message_id

    # Set Martingale Steps
    elif action == "set_stp" and sid:
        sess = active_sessions.get(sid, {})
        sess["input_mode"] = "WAITING_STEPS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        tgt = sess.get("target_profit", 0)
        p_msg = bot.send_message(chat_id, get_text(chat_id, "input_steps", target=tgt))
        sess["temp_prompt_id"] = p_msg.message_id

    # Run Automated Engine
    elif action == "run_auto" and sid:
        sess = active_sessions.get(sid, {})
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় হচ্ছে...")
        assigned_tid = user_sessions.get(chat_id, {}).get("assigned_terminal_id", CURRENT_TERMINAL_ID)
        dispatch_cluster_task(assigned_tid, {
            "task_id": f"T_{int(time.time())}",
            "action": "RUN_AUTO",
            "chat_id": chat_id,
            "session_id": sid,
            "target_profit": sess.get("target_profit"),
            "total_steps": sess.get("total_steps", 7),
            "status": "PENDING"
        })

    # Trading Controls: SHOT, BAL, STATS, STOP, CANCEL
    elif action in ["shot", "bal", "stats", "stop", "cancel"] and sid:
        bot.answer_callback_query(call.id)
        assigned_tid = user_sessions.get(chat_id, {}).get("assigned_terminal_id", CURRENT_TERMINAL_ID)
        dispatch_cluster_task(assigned_tid, {
            "task_id": f"T_{int(time.time())}",
            "action": action.upper(),
            "chat_id": chat_id,
            "session_id": sid,
            "status": "PENDING"
        })

# ==============================================================================
# 16. User Text Input & State Controller
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    safe_delete_message(chat_id, message.message_id)

    u = user_sessions.get(chat_id, {})
    step = u.get("step")

    # Access Password Authentication Handler
    if step == "WAITING_GATE_PASSWORD":
        if u.get("pass_prompt_msg_id"):
            safe_delete_message(chat_id, u["pass_prompt_msg_id"])
            u["pass_prompt_msg_id"] = None

        anim_msg = bot.send_message(chat_id, f"┌────────────────────────────────────────┐\n│ {to_bold('CONNECTING REMOTE ENGINE...')}         │\n└────────────────────────────────────────┘")
        play_pass_auth_animation(chat_id, anim_msg.message_id)

        passwords = firebase.get("passwords") or {}
        now = time.time()
        matched_key = None

        for pkey, pdata in passwords.items():
            if isinstance(pdata, dict):
                if pdata.get("password") == text and pdata.get("expires_at", 0) > now:
                    matched_key = pkey
                    break

        if not matched_key and not is_owner(message.from_user):
            safe_delete_message(chat_id, anim_msg.message_id)
            err_box = (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('INVALID OR EXPIRED PASSWORD')}        │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ আপনার পাসওয়ার্ডটি ভুল বা মেয়াদ শেষ।   │\n"
                f"│ নতুন পাসের জন্য এডমিনের সাথে যোগাযোগ  │\n"
                f"│ করুন।                                  │\n"
                f"└────────────────────────────────────────┘"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{to_bold('OWNER ID')}", url=OWNER_URL))
            bot.send_message(chat_id, err_box, reply_markup=markup)
            return

        # Allocate Dedicated Terminal Node
        allocated_tid = allocate_free_terminal(chat_id)
        safe_delete_message(chat_id, anim_msg.message_id)

        if not allocated_tid:
            no_slot_box = (
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('ALL CLUSTER SLOTS BUSY')}             │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ বর্তমানে ক্লাস্টারের সকল টার্মিনাল ফুল।│\n"
                f"│ অনুগ্রহ করে কিছুক্ষণ পর চেষ্টা করুন।     │\n"
                f"└────────────────────────────────────────┘"
            )
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(f"{to_bold('OWNER ID')}", url=OWNER_URL))
            bot.send_message(chat_id, no_slot_box, reply_markup=markup)
            return

        if matched_key:
            firebase.patch(f"passwords/{matched_key}", {
                "is_used": True,
                "bound_user_id": chat_id,
                "bound_terminal_id": allocated_tid
            })

        u["assigned_terminal_id"] = allocated_tid
        u["step"] = "CHOOSE_SITE"

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
            InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
        )
        bot.send_message(chat_id, get_text(chat_id, "choose_site"), reply_markup=markup)
        return

    # Browser Parameter Input Handlers
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
                    f"┌────────────────────────────────────────┐\n"
                    f"│ {to_bold('ACCOUNT LOGIN')}                       │\n"
                    f"├────────────────────────────────────────┤\n"
                    f"│ প্ল্যাটফর্ম : {sess.get('site_name', '')}\n"
                    f"│ নাম্বার     : {masked} (সংরক্ষিত)\n"
                    f"├────────────────────────────────────────┤\n"
                    f"│ এখন PASSWORD বাটন চেপে পাসওয়ার্ড দিন: │\n"
                    f"└────────────────────────────────────────┘"
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

        anim_msg = bot.send_message(chat_id, f"┌────────────────────────────────────────┐\n│ {to_bold('CONNECTING REMOTE ENGINE')}            │\n└────────────────────────────────────────┘")
        
        assigned_tid = u.get("assigned_terminal_id", CURRENT_TERMINAL_ID)
        dispatch_cluster_task(assigned_tid, {
            "task_id": f"T_{int(time.time())}",
            "action": "LOGIN",
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": sess.get("site_name", "Amar Club"),
            "phone": sess.get("phone"),
            "password": text,
            "anim_msg_id": anim_msg.message_id,
            "status": "PENDING"
        })

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
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('WINGO 30S MARKET ACTIVE')}              │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform     : {sess.get('site_name', '')}\n"
                f"│ Live Balance : ৳ {cur_bal:.2f}\n"
                f"│ Target Total : ৳ {val:.2f}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ প্যারামিটার সেট হয়েছে। START চাপুন:     │\n"
                f"└────────────────────────────────────────┘"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
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
                f"┌────────────────────────────────────────┐\n"
                f"│ {to_bold('WINGO 30S MARKET ACTIVE')}              │\n"
                f"├────────────────────────────────────────┤\n"
                f"│ Platform     : {sess.get('site_name', '')}\n"
                f"│ Live Balance : ৳ {cur_bal:.2f}\n"
                f"│ Total Steps  : {steps_val}\n"
                f"├────────────────────────────────────────┤\n"
                f"│ প্যারামিটার সেট হয়েছে। START চাপুন:     │\n"
                f"└────────────────────────────────────────┘"
            )
            display_or_replace_photo(chat_id, sid, wingo_snap, config_caption, get_setup_param_keyboard(sid))
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==============================================================================
# 17. Distributed Cluster Main Bootstrapper
# ==============================================================================
def main():
    print("┌────────────────────────────────────────────────────────┐")
    print(f"│ {to_bold('DISTRIBUTED CLUSTER ENGINE INITIALIZING')}          │")
    print("├────────────────────────────────────────────────────────┤")
    print(f"│ TERMINAL ID : {CURRENT_TERMINAL_ID}")
    print(f"│ OWNER       : {OWNER_HANDLE}")
    print(f"│ DATABASE    : {FIREBASE_DATABASE_URL}")
    print("└────────────────────────────────────────────────────────┘")

    # 1. Register node in Firebase
    register_terminal_node()

    # 2. Launch background threads
    threading.Thread(target=update_terminal_heartbeat, daemon=True).start()
    threading.Thread(target=master_election_engine, daemon=True).start()
    threading.Thread(target=worker_task_listener, daemon=True).start()
    threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

    # 3. Main thread keep-alive
    while CLUSTER_RUNNING:
        time.sleep(1)

if __name__ == "__main__":
    main()
