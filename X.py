import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket

# ==========================================
# 1. Automatic Package Installer
# ==========================================
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
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==========================================
# 2. Premium Mathematical Bold Unicode Converter (Clean, No Brackets)
# ==========================================
def to_bold(text: str) -> str:
    """Converts ASCII letters and digits to Mathematical Bold Unicode (A->𝐀, a->𝐚, 0->𝟎)"""
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
    """Finds an available local network port to isolate WebDriver instances."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

# ==========================================
# 3. Configuration & URLs
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

# User Session Database: chat_id -> Session Dictionary
user_sessions = {}

# ==========================================
# 4. Multi-User Firefox Clone & Absolute Isolation
# ==========================================
def launch_firefox_instance(chat_id, target_url):
    """
    Launches a dedicated cloned Firefox instance for EACH user.
    Uses:
    1. Separate persistent profile folder per chat_id.
    2. Completely unique Geckodriver port per user.
    3. Dedicated, unique Marionette port passed to Geckodriver and Firefox.
    4. Independent TMPDIR and MOZ_NO_REMOTE environment variables.
    This guarantees 100+ users can run simultaneously without closing or overriding each other.
    """
    user_profile_dir = os.path.join(PROFILES_BASE_DIR, f"user_{chat_id}")
    os.makedirs(user_profile_dir, exist_ok=True)

    # Clean old stale locks for this specific user profile only
    for lock_name in [".parentlock", "parent.lock", "lock", "sessionstore.jsonlz4"]:
        lp = os.path.join(user_profile_dir, lock_name)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    gecko_port = find_free_port()
    marionette_port = find_free_port()

    # Isolated temporary directory per user to avoid shared-memory collisions
    user_tmp_dir = os.path.join(PROFILES_BASE_DIR, f"tmp_{chat_id}")
    os.makedirs(user_tmp_dir, exist_ok=True)

    env = os.environ.copy()
    env["MOZ_NO_REMOTE"] = "1"
    env["TMPDIR"] = user_tmp_dir

    if "DISPLAY" not in env or not env["DISPLAY"]:
        env["DISPLAY"] = ":0"

    options = Options()
    options.add_argument("-no-remote")
    options.add_argument("-new-instance")
    options.add_argument("-profile")
    options.add_argument(user_profile_dir)
    options.add_argument("--marionette-port")
    options.add_argument(str(marionette_port))

    # Multi-instance isolation preferences
    options.set_preference("marionette.port", marionette_port)
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)
    options.set_preference("browser.sessionstore.resume_from_crash", False)
    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("browser.shell.checkDefaultBrowser", False)

    # Launch geckodriver with dedicated port AND dedicated marionette-port
    service = FirefoxService(
        port=gecko_port,
        service_args=["--marionette-port", str(marionette_port), "--connect-existing=false"],
        env=env
    )
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.maximize_window()
    except Exception:
        pass

    driver.get(target_url)
    return driver, user_profile_dir

def close_user_browser(chat_id):
    """Safely closes ONLY this user's browser without touching other active users' browsers."""
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

# ==========================================
# 5. In-Browser JavaScript Automation Code
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

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

if (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Win Go') || bodyText.includes('30S') || bodyText.includes('Lottery')) {
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

# ==========================================
# 6. Core Client Trading Engine (Original Hard-Lock & VIP API)
# ==========================================
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

# ==========================================
# 7. Multi-Language Messages (Strictly Clean, NO BRACKETS, Pure VIP Bold)
# ==========================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")

    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"স্বাগতম! এটি একটি সম্পূর্ণ স্বয়ংক্রিয় ও হাই-স্পিড ভিআইপি উইনগো ট্রেডিং সিস্টেম।\n\n"
                f"অনুগ্রহ করে আপনার পছন্দের ভাষা নির্বাচন করুন:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনি কোন সাইটে অটো ট্রেড করতে চান? নিচে থেকে প্ল্যাটফর্ম নির্বাচন করুন:"
            ),
            "input_phone": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"আপনার রেজিস্টার্ড একাউন্ট নম্বর (ফোন নম্বর) লিখে সেন্ড করুন:"
            ),
            "input_pass": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"একাউন্ট নম্বর: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"এবার আপনার একাউন্টের সঠিক পাসওয়ার্ড লিখে সেন্ড করুন:"
            ),
            "login_wait": (
                f"<b>{to_bold('CONNECTING TO SERVER')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"আপনার জন্য একটি সম্পূর্ণ পৃথক ফায়ারফক্স ব্রাউজার চালু করে একাউন্টে লগইন করা হচ্ছে..."
            ),
            "login_success_redirecting": (
                f"<b>{to_bold('LOGIN COMPLETED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"একাউন্ট নম্বর: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"লগইন সফল হয়েছে! এখন স্বয়ংক্রিয়ভাবে উইনগো ৩০এস (WinGo 30S) মূল গেম পেজে প্রবেশ করা হচ্ছে..."
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"সমস্যা: <i>{kwargs.get('error', 'ভুল তথ্য বা নেটওয়ার্ক সমস্যা')}</i>\n\n"
                f"পুনরায় চেষ্টা করতে /start লিখে সেন্ড করুন।"
            ),
            "wingo_ready": (
                f"<b>{to_bold('WINGO 30S READY')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b> (WinGo 30S)\n"
                f"আপনার বর্তমান ওয়ালেট ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"উইনগো ৩০এস পেজ প্রস্তুত হয়েছে।\n"
                f"ট্রেডিং শুরু করতে নিচে {to_bold('START')} চাপুন, অথবা ব্রাউজারটি বন্ধ করতে {to_bold('CANCEL')} চাপুন:"
            ),
            "input_target": (
                f"<b>{to_bold('SET TARGET PROFIT')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"বর্তমান ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"আপনি কত টাকা মোট প্রফিট (লাভ) করতে চান? লাভ অর্জিত হওয়া মাত্রই অটোমেশন নিজে থেকেই ট্রেড থামিয়ে দেবে।\n"
                f"আপনার টার্গেট অ্যামাউন্টটি লিখে সেন্ড করুন (যেমন: <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('SET MARTINGALE STEPS')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"টার্গেট প্রফিট: <code>৳ {kwargs.get('target', 0)}</code> সংরক্ষিত হয়েছে।\n\n"
                f"মার্টিনগেল ব্যাকআপের জন্য আপনি কতটি স্টেপ রাখতে চান?\n"
                f"স্টেপ সংখ্যা লিখে সেন্ড করুন (যেমন: <code>7</code> বা <code>10</code>):"
            ),
            "starting_trade": (
                f"<b>{to_bold('STARTING TRADING ENGINE')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"টার্গেট ও স্টেপ সফলভাবে সেট করা হয়েছে।\n"
                f"স্ক্রিন হার্ড-লক সহ ভিআইপি সিগন্যাল অ্যালগরিদম সক্রিয় করা হচ্ছে...\n"
                f"নিচে ব্রাউজারের লাইভ স্ক্রিন ফুটেজ পাঠানো হচ্ছে।"
            ),
            "running_dashboard": (
                f"<b>{to_bold('AUTOMATION ACTIVE 24/7')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"শুরুর ব্যালেন্স: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"টার্গেট ব্যালেন্স: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"মোট ব্যাকআপ স্টেপ: <b>{kwargs.get('steps', 7)} Steps</b>\n\n"
                f"ব্রাউজারটি নিরবচ্ছিন্নভাবে ব্যাকগ্রাউন্ডে ট্রেড পরিচালনা করছে।"
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"আপনার ফায়ারফক্স ব্রাউজার উইন্ডোটি সম্পূর্ণভাবে বন্ধ করা হয়েছে।\n"
                f"অন্যদের ব্রাউজারে কোনো প্রভাব পড়েনি।\n"
                f"নতুন সেশন চালু করতে চাইলে /start লিখে সেন্ড করুন।"
            ),
            "target_achieved": (
                f"<b>{to_bold('CONGRATULATIONS TARGET ACHIEVED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"আলহামদুলিল্লাহ! আপনার কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে।\n\n"
                f"চূড়ান্ত ট্রেডিং রিপোর্ট:\n"
                f"শুরুর ব্যালেন্স: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"শেষ ব্যালেন্স: <code>৳ {kwargs.get('cur_bal', '0.00')}</code>\n"
                f"মোট প্রফিট: <code>+৳ {kwargs.get('profit', '0.00')}</code>\n\n"
                f"মোট উইন: <b>{kwargs.get('wins', 0)}</b> বার\n"
                f"মোট লস: <b>{kwargs.get('losses', 0)}</b> বার\n"
                f"টানা সর্বোচ্চ উইন: <b>{kwargs.get('max_w', 0)}</b> বার\n"
                f"টানা সর্বোচ্চ লস: <b>{kwargs.get('max_l', 0)}</b> বার\n\n"
                f"নিচে সমাপ্তির লাইভ স্ক্রিন ফুটেজ সংযুক্ত করা হলো:"
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Welcome to the Premium WinGo 30S Auto-Trading Platform.\n\n"
                f"Please select your preferred language:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Which platform do you want to automate? Select below:"
            ),
            "input_phone": (
                f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"Please enter your account / phone number:"
            ),
            "input_pass": (
                f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Now enter your account password:"
            ),
            "login_wait": (
                f"<b>{to_bold('CONNECTING TO SERVER')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n\n"
                f"Launching isolated browser and logging in..."
            ),
            "login_success_redirecting": (
                f"<b>{to_bold('LOGIN COMPLETED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login successful! Auto-redirecting to WinGo 30S game page..."
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Invalid credentials or timeout')}</i>\n\n"
                f"Send /start to try again."
            ),
            "wingo_ready": (
                f"<b>{to_bold('WINGO 30S READY')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b> (WinGo 30S)\n"
                f"Wallet Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"WinGo 30S page is ready.\n"
                f"Press {to_bold('START')} to begin trading or {to_bold('CANCEL')} to close this browser:"
            ),
            "input_target": (
                f"<b>{to_bold('SET TARGET PROFIT')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Enter your Target Profit amount (e.g. <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('SET MARTINGALE STEPS')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Target Profit: <code>৳ {kwargs.get('target', 0)}</code> saved.\n\n"
                f"Enter total Martingale backup steps (e.g. <code>7</code> or <code>10</code>):"
            ),
            "starting_trade": (
                f"<b>{to_bold('STARTING TRADING ENGINE')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Target and steps successfully registered.\n"
                f"Screen hard-lock and VIP algorithm activated...\n"
                f"Live browser footage attached below."
            ),
            "running_dashboard": (
                f"<b>{to_bold('AUTOMATION ACTIVE 24/7')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)} Steps</b>\n\n"
                f"Browser is running trades 24/7 in background."
            ),
            "cancelled": (
                f"<b>{to_bold('SESSION TERMINATED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Your browser session has been cleanly closed.\n"
                f"Send /start to begin a new session."
            ),
            "target_achieved": (
                f"<b>{to_bold('CONGRATULATIONS TARGET ACHIEVED')}</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"Your requested target profit has been successfully reached.\n\n"
                f"Performance Report:\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Final Balance: <code>৳ {kwargs.get('cur_bal', '0.00')}</code>\n"
                f"Net Profit: <code>+৳ {kwargs.get('profit', '0.00')}</code>\n\n"
                f"Total Wins: <b>{kwargs.get('wins', 0)}</b>\n"
                f"Total Losses: <b>{kwargs.get('losses', 0)}</b>\n"
                f"Max Win Streak: <b>{kwargs.get('max_w', 0)}</b>\n"
                f"Max Loss Streak: <b>{kwargs.get('max_l', 0)}</b>\n\n"
                f"Live final footage attached below:"
            )
        }
    }

    return messages.get(lang, messages["bn"]).get(key, "")

# ==========================================
# 8. Keyboard Controls (Strictly NO BRACKETS, Pure VIP Bold)
# ==========================================
def get_language_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('ENGLISH')}", callback_data="lang_en"),
        InlineKeyboardButton(f"{to_bold('BANGLA')}", callback_data="lang_bn")
    )
    return markup

def get_platform_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
        InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
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

# ==========================================
# 9. Background Progress & 24-Hour Persistence Monitor
# ==========================================
def monitor_trading_progress(chat_id):
    """Background monitor thread: checks balance, records streaks, sends completion alert."""
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

                # Target completed: celebrate and notify
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

# 24-Hour Idle Cleaner: only closes an abandoned browser if completely idle with NO trading for a full 24 hours
def idle_session_reaper():
    while True:
        try:
            now = time.time()
            for cid, sess in list(user_sessions.items()):
                # Never kill an actively running trading session!
                if not sess.get("is_trading"):
                    last_active = sess.get("last_active", now)
                    if now - last_active > 86400: # 24 hours idle
                        print(f"[*] Cleaning up 24h idle browser session for {cid}")
                        close_user_browser(cid)
        except Exception:
            pass
        time.sleep(3600)

threading.Thread(target=idle_session_reaper, daemon=True).start()

# ==========================================
# 10. Login & Direct WinGo 30S Navigation Executor
# ==========================================
def process_login(chat_id, phone, password, status_msg_id):
    sess = user_sessions.get(chat_id, {})
    sess["last_active"] = time.time()
    site_name = sess.get("site_name", "Amar Club")

    # Step 1: Login URL
    login_url = URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN
    # Step 2: Real WinGo 30S URL
    wingo_url = URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO

    # Animated progress indicator (Clean, No Brackets)
    stop_spinner = threading.Event()
    def spinner_task():
        spinners = ["-", "\\", "|", "/"]
        i = 0
        while not stop_spinner.is_set():
            try:
                bot.edit_message_text(
                    f"<b>{to_bold('CONNECTING TO SERVER')} {spinners[i % len(spinners)]}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"প্ল্যাটফর্ম: <b>{site_name}</b>\n"
                    f"আইসোলেটেড ফায়ারফক্স তৈরি হচ্ছে...",
                    chat_id=chat_id,
                    message_id=status_msg_id
                )
            except Exception:
                pass
            i += 1
            time.sleep(0.6)

    threading.Thread(target=spinner_task, daemon=True).start()

    driver = None
    try:
        driver, prof_dir = launch_firefox_instance(chat_id, login_url)
        sess["driver"] = driver
        sess["profile_dir"] = prof_dir
    except Exception as e:
        stop_spinner.set()
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error=str(e)),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        return

    # Auto-fill credentials
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
        stop_spinner.set()
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error="লগইন ইনপুট ফিল্ড পাওয়া যায়নি"),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        close_user_browser(chat_id)
        return

    # Verify login success or error rejection
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
                err_detail = res.get("message", "ভুল ফোন বা পাসওয়ার্ড")
                break
        except Exception:
            pass
        time.sleep(0.5)

    stop_spinner.set()

    if login_status == "ERROR":
        close_user_browser(chat_id)
        bot.edit_message_text(
            get_text(chat_id, "login_failed", site_name=site_name, error=err_detail),
            chat_id=chat_id,
            message_id=status_msg_id
        )
        return

    # 1. Notify login completion
    bot.edit_message_text(
        get_text(chat_id, "login_success_redirecting", site_name=site_name, phone=phone),
        chat_id=chat_id,
        message_id=status_msg_id
    )

    # 2. Strict Requirement: Immediately open the Real WinGo 30S Game Link!
    # Multiple fallback strategies to ensure hash-router single page apps transition without fail:
    nav_script = """
    const targetUrl = arguments[0];
    try {
        // Dismiss any modal overlays or daily bonus dialogs
        document.querySelectorAll('.van-dialog__confirm, .van-overlay, button[class*="confirm"], button[class*="close"], .van-popup__close-icon').forEach(el => {
            try { el.click(); } catch(e){}
        });
    } catch(e){}

    const parts = targetUrl.split('#');
    if (parts.length > 1) {
        window.location.hash = parts[1];
    }
    window.location.href = targetUrl;
    """

    time.sleep(1.2)
    wingo_ready = False
    for attempt in range(8):
        try:
            driver.execute_script(nav_script, wingo_url)
        except Exception:
            pass
        try:
            driver.get(wingo_url)
        except Exception:
            pass

        time.sleep(2)
        try:
            if driver.execute_script(CHECK_WINGO_READY_JS):
                wingo_ready = True
                break
        except Exception:
            pass

    time.sleep(2.5)

    # 3. Read the live balance from the WinGo 30S page
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

    # 4. Send message with balance and two clean buttons: START and CANCEL
    bot.send_message(
        chat_id,
        get_text(chat_id, "wingo_ready", site_name=site_name, balance=f"{current_bal:.2f}"),
        reply_markup=get_start_or_cancel_keyboard()
    )

# ==========================================
# 11. Telegram Handlers & Interaction
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    # If user already has an active trading driver, do not destroy it!
    existing_sess = user_sessions.get(chat_id)
    if existing_sess and existing_sess.get("is_trading"):
        bot.send_message(
            chat_id,
            f"<b>{to_bold('TRADING IS ALREADY RUNNING')}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"আপনার ট্রেডিং ব্যাকগ্রাউন্ডে সক্রিয় রয়েছে। লাইভ কন্ট্রোল প্যানেল নিচে পাঠানো হলো:",
            reply_markup=get_trading_control_keyboard()
        )
        return

    # Initialize / reset session for this specific chat_id
    user_sessions[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn",
        "last_active": time.time(),
        "driver": existing_sess.get("driver") if existing_sess else None,
        "profile_dir": existing_sess.get("profile_dir") if existing_sess else None
    }

    bot.send_message(
        chat_id,
        get_text(chat_id, "welcome"),
        reply_markup=get_language_keyboard()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data
    sess = user_sessions.setdefault(chat_id, {"last_active": time.time()})
    sess["last_active"] = time.time()

    # 1. Language Selection
    if data in ["lang_en", "lang_bn"]:
        sess["lang"] = "en" if data == "lang_en" else "bn"
        sess["step"] = "CHOOSE_SITE"

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "choose_site"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_platform_keyboard()
        )

    # 2. Platform Selection
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        sess["site_name"] = site_name
        sess["step"] = "WAITING_PHONE"

        bot.answer_callback_query(call.id, site_name)
        bot.edit_message_text(
            get_text(chat_id, "input_phone", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id
        )

    # 3. WinGo 30S Ready Buttons: START or CANCEL
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

    # 4. Live Control: Screen Footage Snapshot
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
                        caption=f"<b>{to_bold('LIVE BROWSER FOOTAGE')}</b>\nসময়: <code>{time.strftime('%H:%M:%S')}</code>"
                    )
                os.remove(temp_shot)
            except Exception as e:
                bot.send_message(chat_id, f"Error: {e}")
        else:
            bot.answer_callback_query(call.id, "Browser not active!", show_alert=True)

    # 5. Live Control: Live Balance
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

    # 6. Live Control: Statistics Report
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
                        f"<b>{to_bold('LIVE TRADING STATS')}</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"বর্তমান ব্যালেন্স: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                        f"টার্গেট: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                        f"মার্টিনগেল স্টেপ: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                        f"উইন: <b>{data_rep['w']}</b> বার | লস: <b>{data_rep['l']}</b> বার"
                    )
                    bot.send_message(chat_id, stat_txt)
                else:
                    bot.answer_callback_query(call.id, "Script initializing...", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "No stats available.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Browser not active!", show_alert=True)

    # 7. Live Control: Stop Trading
    elif data == "btn_stop_trade":
        driver = sess.get("driver")
        if driver:
            try:
                driver.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
                sess["is_trading"] = False
                bot.answer_callback_query(call.id, "Trading paused.", show_alert=True)
                bot.send_message(
                    chat_id,
                    f"<b>{to_bold('TRADING PAUSED')}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"ট্রেডিং সাময়িকভাবে থামানো হয়েছে।"
                )
            except Exception:
                bot.answer_callback_query(call.id, "Error executing stop.", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "No active trade!", show_alert=True)

@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_user_text(message):
    chat_id = message.chat.id
    sess = user_sessions[chat_id]
    sess["last_active"] = time.time()
    step = sess.get("step")
    text = message.text.strip()

    # Step: Input Phone
    if step == "WAITING_PHONE":
        sess["phone"] = text
        sess["step"] = "WAITING_PASS"
        bot.send_message(chat_id, get_text(chat_id, "input_pass", phone=text))

    # Step: Input Password
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

    # Step: Input Target Profit
    elif step == "WAITING_TARGET_PROFIT":
        try:
            val = float(text)
            if val <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "দয়া করে একটি সঠিক পজিটিভ অ্যামাউন্ট লিখুন (যেমন: <code>500</code>):")
            return

        sess["target_profit"] = val
        sess["step"] = "WAITING_STEPS"

        bot.send_message(
            chat_id,
            get_text(chat_id, "input_steps", target=val)
        )

    # Step: Input Martingale Steps & Launch Script
    elif step == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0:
                raise ValueError()
        except ValueError:
            bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: <code>7</code>):")
            return

        sess["total_steps"] = steps_val
        sess["step"] = "TRADING_RUNNING"
        sess["is_trading"] = True

        driver = sess.get("driver")
        if not driver:
            bot.send_message(chat_id, "ব্রাউজার সংযোগ নেই। /start দিয়ে পুনরায় শুরু করুন।")
            return

        bot.send_message(chat_id, get_text(chat_id, "starting_trade"))

        # Inject original automation JavaScript
        try:
            driver.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
        except Exception as e:
            bot.send_message(chat_id, f"স্ক্রিপ্ট এক্সিকিউশনে সমস্যা: {e}")
            return

        time.sleep(2)

        # Initial live screenshot
        start_snap = os.path.join(PROFILES_BASE_DIR, f"start_{chat_id}.png")
        try:
            driver.save_screenshot(start_snap)
            with open(start_snap, "rb") as ph:
                bot.send_photo(
                    chat_id, ph,
                    caption=(
                        f"<b>{to_bold('LIVE BROWSER FOOTAGE')}</b>\n"
                        f"━━━━━━━━━━━━━━━━━━━━\n"
                        f"টার্গেট প্রফিট: <code>৳ {sess['target_profit']}</code> | ব্যাকআপ: <code>{sess['total_steps']} Steps</code>"
                    )
                )
            os.remove(start_snap)
        except Exception as e:
            print(f"[*] Snapshot error: {e}")

        # Control Panel Dashboard
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

# ==========================================
# 12. Main Runner
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT MULTI-INSTANCE READY')}...")
    bot.infinity_polling()
