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
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

# ==========================================
# 2. Helper Functions & Port Isolation
# ==========================================
def to_bold(text: str) -> str:
    """ASCII text-ke Mathematical Bold Unicode-e convert kore"""
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
    """Protiti Firefox session-ke alada rakhte free port ber kore"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def safe_delete_message(chat_id, message_id):
    """Message delete korar shomoy kono error hole handle kore"""
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ==========================================
# 3. Configuration & Constants
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

# User Sessions & Active Driver Storage
user_sessions = {}
active_drivers = {}

# ==========================================
# 4. Multi-Instance Isolated Firefox Launcher
# ==========================================
def launch_firefox_instance(chat_id, target_url):
    session_id = f"{chat_id}_{int(time.time())}_{find_free_port()}"
    user_profile_dir = os.path.join(PROFILES_BASE_DIR, f"user_{session_id}")
    os.makedirs(user_profile_dir, exist_ok=True)

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

    active_drivers[session_id] = {
        "driver": driver,
        "profile_dir": user_profile_dir,
        "chat_id": chat_id,
        "created_at": time.time(),
        "session_id": session_id
    }

    driver.get(target_url)
    return driver, user_profile_dir, session_id

def close_user_browser(chat_id, session_id=None):
    sess = user_sessions.get(chat_id)
    target_sid = session_id or (sess.get("session_id") if sess else None)

    if target_sid and target_sid in active_drivers:
        active_item = active_drivers.pop(target_sid, None)
        if active_item:
            driver = active_item.get("driver")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
    elif sess and sess.get("driver"):
        try:
            sess["driver"].quit()
        except Exception:
            pass

    if sess:
        sess["is_trading"] = False
        sess["driver"] = None
        sess["step"] = "IDLE"

# ==========================================
# 5. Dynamic Photo Replacement Engine
# ==========================================
def display_or_replace_photo(chat_id, image_path, caption_text, reply_markup=None):
    sess = user_sessions.setdefault(chat_id, {})
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

# ==========================================
# 6. JavaScript Automation Scripts
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
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed device prompt" };
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
        return { status: "PENDING", message: "Handling takeover..." };
    }
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('Account does not exist') || t.includes('frozen')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

# Custom WinGo selector from user script
CLICK_WINGO_TAB_JS = """
(function(){
    let el = document.querySelector("body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img");
    if (el) {
        el.click();
        return "CLICKED_SELECTOR";
    }
    // Fallbacks
    let alt = document.querySelector("div[class*='wingo' i], img[src*='wingo' i]");
    if (alt) {
        alt.click();
        return "CLICKED_ALT";
    }
    return "NOT_FOUND";
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
        return "RESTARTED";
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

    let inC=document.createElement('div');
    inC.className='drx-in';
    let h=document.createElement('div');
    h.style.cssText='padding:8px;font-size:12px;display:flex;justify-content:space-between;cursor:move;border-bottom:2px solid #00ff00;background:rgba(10,12,18,0.92);border-radius:12px 12px 0 0;';
    h.innerHTML='<span style="color:#00ff00;font-weight:bold;">' + uF('WINZY-VIP') + '</span><span style="cursor:pointer;color:#f00;font-weight:bold;" id="sys-cls">X</span>';
    inC.appendChild(h);

    let b=document.createElement('div');
    b.style.cssText='padding:10px;display:flex;flex-direction:column;gap:8px;background:rgba(10,12,18,0.92);border-radius:0 0 12px 12px;';

    const p1=document.createElement('div');
    const tgtInp=document.createElement('input');
    tgtInp.type='number';
    tgtInp.value=autoTargetProfit || '';
    tgtInp.placeholder='TARGET PROFIT';
    tgtInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:#18181b;border:1px solid #333;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#fff;';

    const stepInp=document.createElement('input');
    stepInp.type='number';
    stepInp.value=autoTotalSteps || 7;
    stepInp.placeholder='TOTAL STEPS';
    stepInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:#18181b;border:1px solid #333;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#0ff;';

    const goBtn=document.createElement('button');
    goBtn.innerText=uF('START');
    goBtn.style.cssText='width:100%;box-sizing:border-box;padding:8px;background:#22c55e;color:#000;border:none;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;';

    p1.appendChild(tgtInp);
    p1.appendChild(stepInp);
    p1.appendChild(goBtn);

    const p2=document.createElement('div');
    p2.style.display='none';

    const balBx=document.createElement('div');
    balBx.style.cssText='padding:6px;text-align:center;background:#18181b;border-radius:6px;margin-bottom:6px;';
    balBx.innerHTML='<div style="font-size:9px;color:#ccc;">' + uF('LIVE BAL') + '</div><div id="ui-bal" style="font-size:16px;color:#00ff00;font-weight:bold;">--</div>';

    const infBx=document.createElement('div');
    infBx.style.cssText='padding:6px;font-size:10px;line-height:2;background:#18181b;border-radius:6px;';
    infBx.innerHTML='<div style="display:flex;justify-content:space-between;"><span style="color:#ccc;">TGT:</span><span id="ui-tgt" style="color:#fff;">0</span></div>' + 
                    '<div style="display:flex;justify-content:space-between;"><span style="color:#ccc;">STP:</span><span id="ui-bet" style="color:#ffcc00;">1</span></div>' + 
                    '<div style="display:flex;justify-content:space-between;"><span style="color:#ccc;">STS:</span><span id="ui-sts" style="color:#0ff;">RUNNING</span></div>';

    const stpBtn=document.createElement('button');
    stpBtn.innerText=uF('STOP');
    stpBtn.style.cssText='width:100%;padding:8px;background:#ef4444;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:11px;margin-top:6px;font-weight:bold;';

    p2.appendChild(balBx);
    p2.appendChild(infBx);
    p2.appendChild(stpBtn);

    b.appendChild(p1);
    b.appendChild(p2);
    inC.appendChild(b);
    p.appendChild(inC);
    document.body.appendChild(p);

    const drx_simClick=el=>{
        if(!el)return;
        ['pointerdown','mousedown','touchstart','pointerup','mouseup','touchend','click'].forEach(evt=>{
            try{ el.dispatchEvent(new MouseEvent(evt,{bubbles:true,cancelable:true,view:window})); }catch(e){}
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
            }
            if(!btn){ if(cb)cb(false); return; }
            drx_simClick(btn);

            let valInterval=setInterval(()=>{
                let inpEl=document.querySelector("input[type='number'], input.van-field__control");
                if(inpEl){
                    clearInterval(valInterval);
                    inpEl.focus();
                    let setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;
                    if(setV)setV.call(inpEl,String(amt));
                    else inpEl.value=amt;
                    inpEl.dispatchEvent(new Event('input',{bubbles:true}));
                    inpEl.dispatchEvent(new Event('change',{bubbles:true}));

                    setTimeout(()=>{
                        let dEl=document.querySelector('button.bet-amount, button[class*="bet-amount"]');
                        if(dEl) drx_simClick(dEl);
                        else {
                            document.querySelectorAll('button').forEach(b=>{
                                if((b.innerText||'').includes('Total amount')&&b.offsetParent)drx_simClick(b);
                            });
                        }
                        setTimeout(()=>{if(cb)cb(true);},2000);
                    },600);
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
                st.isRun=false;
                clearInterval(st.autoInt);
                return;
            }else{
                uBal.innerText=uF(st.curBal>0?st.curBal.toFixed(2):'--');
            }

            let ts=Math.floor(Date.now()/1000),res=await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts="+ts),dataArray=await res.json();
            if(dataArray&&dataArray.length>0){
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
                            st.cur_l_streak++;
                            st.cur_w_streak=0;
                            if(st.cur_l_streak>st.max_l_streak) st.max_l_streak=st.cur_l_streak;
                        }
                    }
                    st.lastPeriod=cSig;
                    st.isTrd=true;
                    let nBal=chkBal();
                    if(st.stpIdx>=st.dynSeq.length)st.stpIdx=st.dynSeq.length-1;
                    let tAmt=st.dynSeq[st.stpIdx];
                    uBet.innerText=uF(tAmt + ' (S' + (st.stpIdx+1) + ')');

                    let activeLogicNew=dataArray[curApiIdx],prediction=(activeLogicNew.pred||'BIG').toUpperCase();
                    st.lastPred=prediction;

                    if(prediction!=='SKIP'){
                        exeTrd(prediction,tAmt,(suc)=>{
                            if(suc){
                                sessionStorage.setItem('drx_sig',cSig);
                                st.tradesDone++;
                            }
                            setTimeout(()=>{st.isTrd=false;},1000);
                        });
                    }else{
                        sessionStorage.setItem('drx_sig',cSig);
                        setTimeout(()=>{st.isTrd=false;},1000);
                    }
                }
            }
        }catch(e){
            st.isTrd=false;
        }
        isFetchingApi=false;
    };

    goBtn.onclick=()=>{
        let inputTarget=parseFloat(tgtInp.value);
        if(!inputTarget||inputTarget<=0)return;
        let inputSteps=parseInt(stepInp.value)||1;
        st.totalSteps=inputSteps;
        let liveB=chkBal();
        st.startBal=liveB;
        st.tgtAmt=(inputTarget<=liveB)?(liveB+inputTarget):inputTarget;
        st.dynSeq=generateSmartSequence(liveB,st.totalSteps);
        st.stpIdx=0;

        document.getElementById('ui-tgt').innerText=uF(st.tgtAmt.toFixed(0));
        p1.style.display='none';
        p2.style.display='block';
        st.isRun=true;
        st.autoInt=setInterval(apiLoopTask,1000);
    };

    stpBtn.onclick=()=>{
        st.isRun=false;
        clearInterval(st.autoInt);
        p2.style.display='none';
        p1.style.display='block';
    };

    if (autoTargetProfit && autoTotalSteps) {
        setTimeout(() => { goBtn.click(); }, 1200);
    }
    return "SUCCESS";
})();
"""

# ==========================================
# 7. Dynamic Text & Keyboards
# ==========================================
def get_text(chat_id, key, **kwargs):
    sess = user_sessions.get(chat_id, {})
    lang = sess.get("lang", "bn")
    messages = {
        "bn": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"স্বাগতম আপনাকে প্রিমিয়াম উইনগো ট্রেডিং অটোমেশন প্ল্যাটফর্মে।\n"
                f"দয়া করে আপনার পছন্দের ভাষা নির্বাচন করুন:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"ট্রেডিং প্ল্যাটফর্ম নির্বাচন করুন:"
            ),
            "credentials_prompt": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"দয়া করে নিচের বাটন ব্যবহার করে আপনার নাম্বার এবং পাসওয়ার্ড দিন।\n"
                f"<i>(এটি সম্পূর্ণ গোপন থাকবে এবং কাজ শেষে চ্যাট থেকে মুছে যাবে)</i>"
            ),
            "ask_phone": "দয়া করে আপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:",
            "ask_pass": "দয়া করে আপনার পাসওয়ার্ড লিখে পাঠান:",
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"একাউন্ট: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"লগইন সফল হয়েছে। ট্রেডিং শুরু করতে START চাপুন:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"কারণ: <i>{kwargs.get('error', 'ভুল তথ্য বা টাইমআউট')}</i>\n\n"
                f"পুনরায় চেষ্টা করতে /start চাপুন।"
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"বর্তমান ব্যালেন্স: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"আপনি কত টাকা প্রফিট করতে চান? পরিমাণটি লিখুন (যেমন: <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"টার্গেট প্রফিট: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"মার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখুন (যেমন: <code>7</code> বা <code>10</code>):"
            ),
            "running_dashboard": (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"প্ল্যাটফর্ম: <b>{kwargs.get('site_name', '')}</b>\n"
                f"শুরুর ব্যালেন্স: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"টার্গেট ব্যালেন্স: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"মোট স্টেপ: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"সার্বক্ষণিক ব্যাকগ্রাউন্ডে স্বয়ংক্রিয়ভাবে ট্রেডিং চলছে..."
            )
        },
        "en": {
            "welcome": (
                f"<b>{to_bold('WINGO 30S VIP AUTOMATION')}</b>\n\n"
                f"Welcome to the VIP WinGo Automation Platform.\n"
                f"Please choose your preferred language:"
            ),
            "choose_site": (
                f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
                f"Select your trading platform:"
            ),
            "credentials_prompt": (
                f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Please provide your Account Number and Password using buttons below.\n"
                f"<i>(Credentials remain completely private & deleted)</i>"
            ),
            "ask_phone": "Enter your account phone number:",
            "ask_pass": "Enter your password:",
            "login_success": (
                f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Account: <code>{kwargs.get('phone', '')}</code>\n\n"
                f"Login completed. Press START to configure trading:"
            ),
            "login_failed": (
                f"<b>{to_bold('LOGIN FAILED')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Reason: <i>{kwargs.get('error', 'Invalid info')}</i>\n\n"
                f"Send /start to retry."
            ),
            "input_target": (
                f"<b>{to_bold('TARGET PROFIT')}</b>\n\n"
                f"Current Balance: <code>৳ {kwargs.get('balance', '0.00')}</code>\n\n"
                f"Enter target profit amount (e.g. <code>500</code>):"
            ),
            "input_steps": (
                f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\n"
                f"Target Profit: <code>৳ {kwargs.get('target', 0)}</code>\n\n"
                f"Enter Martingale steps (e.g. <code>7</code> or <code>10</code>):"
            ),
            "running_dashboard": (
                f"<b>{to_bold('24/7 AUTOMATION ACTIVE')}</b>\n\n"
                f"Platform: <b>{kwargs.get('site_name', '')}</b>\n"
                f"Starting Balance: <code>৳ {kwargs.get('start_bal', '0.00')}</code>\n"
                f"Target Balance: <code>৳ {kwargs.get('target_bal', '0.00')}</code>\n"
                f"Total Steps: <b>{kwargs.get('steps', 7)}</b>\n\n"
                f"Trading automatically in background."
            )
        }
    }
    return messages.get(lang, messages["bn"]).get(key, "")

def get_credential_keyboard(chat_id):
    sess = user_sessions.get(chat_id, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('📱 NUMBER')}", callback_data="btn_inp_phone"),
            InlineKeyboardButton(f"{to_bold('🔑 PASSWORD')}", callback_data="btn_inp_pass")
        )
    else:
        # Number input done -> remove Number button, keep Password
        markup.add(
            InlineKeyboardButton(f"{to_bold('🔑 PASSWORD')}", callback_data="btn_inp_pass")
        )
    markup.add(InlineKeyboardButton(f"{to_bold('❌ CANCEL')}", callback_data="btn_cancel_flow"))
    return markup

def get_post_login_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('▶ START')}", callback_data="btn_start_flow"),
        InlineKeyboardButton(f"{to_bold('❌ CANCEL')}", callback_data="btn_cancel_flow")
    )
    return markup

def get_trading_control_keyboard(anim_tick=0):
    # Rotating black and white icons for animated Stop button
    stop_icons = ["⚪", "⚫", "🔘", "⚪"]
    icon = stop_icons[anim_tick % len(stop_icons)]
    
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('🔄 REFRESH FOOTAGE')}", callback_data="btn_screenshot"),
        InlineKeyboardButton(f"{to_bold('💰 LIVE BALANCE')}", callback_data="btn_live_balance")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('📊 STATS REPORT')}", callback_data="btn_stats_report"),
        InlineKeyboardButton(f"{to_bold(f'⏹ {icon} STOP TRADING')}", callback_data="btn_stop_trade")
    )
    return markup

# ==========================================
# 8. Fast In-Message Animation & Login Processor
# ==========================================
def play_login_animation(chat_id, msg_id):
    frames = [
        "<b>[ ⚡ CONNECTING... ]</b>\n<code>[▰▱▱▱▱▱▱▱▱▱] 10% Initializing browser...</code>",
        "<b>[ 🚀 LAUNCHING... ]</b>\n<code>[▰▰▰▱▱▱▱▱▱▱] 35% Isolated Firefox ready...</code>",
        "<b>[ 🔐 INJECTING... ]</b>\n<code>[▰▰▰▰▰▰▱▱▱▱] 65% Auto-filling credentials...</code>",
        "<b>[ ✅ VERIFYING... ]</b>\n<code>[▰▰▰▰▰▰▰▰▰▰] 100% Checking login session...</code>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.4)

def process_login(chat_id, phone, password, anim_msg_id):
    sess = user_sessions.get(chat_id, {})
    site_name = sess.get("site_name", "Amar Club")
    login_url = URL_AMARCLUB_LOGIN if "AMAR" in site_name.upper() else URL_DKWIN_LOGIN

    play_login_animation(chat_id, anim_msg_id)

    driver = None
    session_id = None
    try:
        driver, prof_dir, session_id = launch_firefox_instance(chat_id, login_url)
        sess["driver"] = driver
        sess["profile_dir"] = prof_dir
        sess["session_id"] = session_id
    except Exception as e:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error=str(e)))
        return

    # Auto fill
    fill_ok = False
    for _ in range(60):
        try:
            res = driver.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password)
            if res == "SUCCESS":
                fill_ok = True
                time.sleep(2.0)
                break
        except Exception:
            pass
        time.sleep(0.4)

    if not fill_ok:
        safe_delete_message(chat_id, anim_msg_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error="Login form not responsive"))
        close_user_browser(chat_id, session_id)
        return

    # Verify status
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
                err_detail = res.get("message", "Incorrect credentials")
                break
        except Exception:
            pass
        time.sleep(0.5)

    try:
        if driver.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));"):
            login_status = "SUCCESS"
    except Exception:
        pass

    safe_delete_message(chat_id, anim_msg_id)

    if login_status == "ERROR":
        close_user_browser(chat_id, session_id)
        bot.send_message(chat_id, get_text(chat_id, "login_failed", site_name=site_name, error=err_detail))
        return

    # Screenshot & Post-login message with START button
    time.sleep(1.5)
    login_snap = os.path.join(PROFILES_BASE_DIR, f"login_done_{session_id}.png")
    try:
        driver.save_screenshot(login_snap)
    except Exception:
        pass

    display_or_replace_photo(
        chat_id,
        login_snap,
        get_text(chat_id, "login_success", site_name=site_name, phone=phone[:3] + "****" + phone[-3:]),
        get_post_login_keyboard()
    )

    if os.path.exists(login_snap):
        try:
            os.remove(login_snap)
        except Exception:
            pass

# ==========================================
# 9. WinGo Navigation & Click Handling
# ==========================================
def start_wingo_flow(chat_id):
    sess = user_sessions.get(chat_id, {})
    driver = sess.get("driver")
    site_name = sess.get("site_name", "Amar Club")

    if not driver:
        bot.send_message(chat_id, "Active browser not found. /start pathan.")
        return

    # Execute custom selector click script
    try:
        driver.execute_script(CLICK_WINGO_TAB_JS)
    except Exception:
        pass

    time.sleep(1.5)

    # Backup navigation in case click didn't redirect
    wingo_url = URL_AMARCLUB_WINGO if "AMAR" in site_name.upper() else URL_DKWIN_WINGO
    try:
        driver.execute_script("""
            const target = arguments[0];
            if (!window.location.href.includes('WinGo')) {
                window.location.href = target;
            }
        """, wingo_url)
    except Exception:
        pass

    for _ in range(30):
        try:
            if driver.execute_script(CHECK_WINGO_READY_JS):
                break
        except Exception:
            pass
        time.sleep(0.8)

    # Fetch live balance
    current_bal = 0.0
    for _ in range(12):
        try:
            bal = driver.execute_script(FETCH_BALANCE_JS)
            if bal and float(bal) > 0:
                current_bal = float(bal)
                break
        except Exception:
            pass
        time.sleep(0.5)

    sess["current_balance"] = current_bal
    sess["step"] = "WAITING_TARGET_PROFIT"

    q_msg = bot.send_message(
        chat_id,
        get_text(chat_id, "input_target", balance=f"{current_bal:.2f}")
    )
    sess["last_prompt_msg_id"] = q_msg.message_id

# ==========================================
# 10. Telegram Bot Handlers
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_sessions[chat_id] = {
        "step": "CHOOSE_LANGUAGE",
        "lang": "bn",
        "last_active": time.time(),
        "live_photo_message_id": None,
        "phone": None,
        "password": None,
        "anim_tick": 0
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
    sess = user_sessions.setdefault(chat_id, {})
    sess["last_active"] = time.time()

    # 1. Language Select
    if data in ["lang_en", "lang_bn"]:
        sess["lang"] = "en" if data == "lang_en" else "bn"
        sess["step"] = "CHOOSE_SITE"

        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data="site_amarclub"),
            InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data="site_dkwin")
        )
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "choose_site"),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

    # 2. Site Select -> Show Number & Password Buttons
    elif data in ["site_amarclub", "site_dkwin"]:
        site_name = "Amar Club" if data == "site_amarclub" else "DK Win"
        sess["site_name"] = site_name
        sess["step"] = "PROMPT_CREDENTIALS"
        sess["phone"] = None
        sess["password"] = None

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            get_text(chat_id, "credentials_prompt", site_name=site_name),
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credential_keyboard(chat_id)
        )
        sess["cred_msg_id"] = call.message.message_id

    # 3. Number Button Click
    elif data == "btn_inp_phone":
        sess["step"] = "WAITING_PHONE"
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_phone"))
        sess["temp_ask_msg_id"] = prompt_m.message_id

    # 4. Password Button Click (Strict Order Check)
    elif data == "btn_inp_pass":
        if not sess.get("phone"):
            # Reject if phone not provided yet
            bot.answer_callback_query(
                call.id,
                "এটা হবে না! আপনি দয়া করে নাম্বারটি আগে দিন।",
                show_alert=True
            )
            return
        
        sess["step"] = "WAITING_PASS"
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, get_text(chat_id, "ask_pass"))
        sess["temp_ask_msg_id"] = prompt_m.message_id

    # 5. START Button (Click WinGo Selector & Proceed)
    elif data == "btn_start_flow":
        bot.answer_callback_query(call.id, "WinGo 30S লোড হচ্ছে...")
        threading.Thread(target=start_wingo_flow, args=(chat_id,), daemon=True).start()

    # 6. Cancel
    elif data == "btn_cancel_flow":
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        curr_sid = sess.get("session_id")
        close_user_browser(chat_id, curr_sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, f"<b>{to_bold('SESSION TERMINATED')}</b>\nনতুন সেশনের জন্য /start চাপুন।")

    # 7. Footage Refresh
    elif data == "btn_screenshot":
        driver = sess.get("driver")
        if driver:
            bot.answer_callback_query(call.id, "স্ক্রিনশট আপডেট হচ্ছে...")
            sid = sess.get("session_id", chat_id)
            temp_shot = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
            try:
                driver.save_screenshot(temp_shot)
                sess["anim_tick"] = sess.get("anim_tick", 0) + 1
                caption = f"<b>{to_bold('LIVE BROWSER FOOTAGE')}</b>\nসময়: <code>{time.strftime('%H:%M:%S')}</code>"
                display_or_replace_photo(chat_id, temp_shot, caption, get_trading_control_keyboard(sess["anim_tick"]))
                if os.path.exists(temp_shot):
                    os.remove(temp_shot)
            except Exception as e:
                bot.send_message(chat_id, f"Error: {e}")
        else:
            bot.answer_callback_query(call.id, "Active browser নেই!", show_alert=True)

    # 8. Live Balance
    elif data == "btn_live_balance":
        driver = sess.get("driver")
        if driver:
            try:
                b = driver.execute_script(FETCH_BALANCE_JS)
                bot.answer_callback_query(call.id, f"Live Balance: ৳ {b:.2f}", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "Checking...", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Browser active নেই!", show_alert=True)

    # 9. Stop Trade
    elif data == "btn_stop_trade":
        driver = sess.get("driver")
        if driver:
            try:
                driver.execute_script("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
                sess["is_trading"] = False
                bot.answer_callback_query(call.id, "Automation paused", show_alert=True)
                bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nঅটোমেশন সাময়িকভাবে থামানো হয়েছে।")
            except Exception:
                bot.answer_callback_query(call.id, "Error stopping trade", show_alert=True)

    # 10. Stats Report
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
                        f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                        f"ব্যালেন্স: <code>৳ {data_rep['curBal']:.2f}</code>\n"
                        f"টার্গেট: <code>৳ {data_rep['tgtAmt']:.2f}</code>\n"
                        f"লেভেল: <b>Step {data_rep['step']}/{data_rep['maxStep']}</b>\n"
                        f"উইন: <b>{data_rep['w']}</b> | লস: <b>{data_rep['l']}</b>"
                    )
                    bot.send_message(chat_id, stat_txt)
            except Exception:
                pass

# ==========================================
# 11. Text Input & Auto Deletion Handler
# ==========================================
@bot.message_handler(func=lambda msg: msg.chat.id in user_sessions)
def handle_user_input(message):
    chat_id = message.chat.id
    sess = user_sessions[chat_id]
    step = sess.get("step")
    text = message.text.strip()

    # Always immediately delete user's secret inputs
    safe_delete_message(chat_id, message.message_id)

    # Delete temporary question prompt if exists
    if sess.get("temp_ask_msg_id"):
        safe_delete_message(chat_id, sess["temp_ask_msg_id"])
        sess["temp_ask_msg_id"] = None

    # Step: Input Phone Number
    if step == "WAITING_PHONE":
        sess["phone"] = text
        sess["step"] = "PROMPT_CREDENTIALS"

        # Update credential message: show masked number, leave ONLY Password button
        if sess.get("cred_msg_id"):
            try:
                masked_phone = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_txt = (
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"প্ল্যাটফর্ম: <b>{sess.get('site_name', '')}</b>\n"
                    f"নাম্বার: <code>{masked_phone}</code> ✅\n\n"
                    f"এখন নিচের <b>PASSWORD</b> বাটনে ক্লিক করে পাসওয়ার্ড দিন:"
                )
                bot.edit_message_text(
                    updated_txt,
                    chat_id=chat_id,
                    message_id=sess["cred_msg_id"],
                    reply_markup=get_credential_keyboard(chat_id)
                )
            except Exception:
                pass

    # Step: Input Password
    elif step == "WAITING_PASS":
        sess["password"] = text
        sess["step"] = "LOGGING_IN"

        # Remove credential prompt message cleanly
        if sess.get("cred_msg_id"):
            safe_delete_message(chat_id, sess["cred_msg_id"])
            sess["cred_msg_id"] = None

        # Start animation message
        anim_msg = bot.send_message(chat_id, "<b>[ ⚡ CONNECTING... ]</b>")
        threading.Thread(
            target=process_login,
            args=(chat_id, sess["phone"], sess["password"], anim_msg.message_id),
            daemon=True
        ).start()

    # Step: Input Target Profit
    elif step == "WAITING_TARGET_PROFIT":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
        except ValueError:
            m = bot.send_message(chat_id, "সঠিক প্রফিট অ্যামাউন্ট লিখুন (যেমন: 500):")
            sess["temp_ask_msg_id"] = m.message_id
            return

        # Delete target prompt
        if sess.get("last_prompt_msg_id"):
            safe_delete_message(chat_id, sess["last_prompt_msg_id"])

        sess["target_profit"] = val
        sess["step"] = "WAITING_STEPS"

        q_msg = bot.send_message(
            chat_id,
            get_text(chat_id, "input_steps", target=val)
        )
        sess["last_prompt_msg_id"] = q_msg.message_id

    # Step: Input Martingale Steps
    elif step == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
        except ValueError:
            m = bot.send_message(chat_id, "সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            sess["temp_ask_msg_id"] = m.message_id
            return

        # Delete steps prompt
        if sess.get("last_prompt_msg_id"):
            safe_delete_message(chat_id, sess["last_prompt_msg_id"])

        sess["total_steps"] = steps_val
        sess["step"] = "TRADING_RUNNING"
        sess["is_trading"] = True

        driver = sess.get("driver")
        if not driver:
            bot.send_message(chat_id, "ব্রাউজার সংযোগ নেই। /start চাপুন।")
            return

        # Inject Martingale Core Engine
        try:
            driver.execute_script(WINGO_CORE_JS, sess["target_profit"], sess["total_steps"])
        except Exception as e:
            bot.send_message(chat_id, f"Automation error: {e}")
            return

        time.sleep(2.0)

        sid = sess.get("session_id", chat_id)
        start_snap = os.path.join(PROFILES_BASE_DIR, f"start_{sid}.png")
        try:
            driver.save_screenshot(start_snap)
        except Exception:
            pass

        cur_b = sess.get("current_balance", 0.0)
        target_total = cur_b + sess["target_profit"]
        sess["start_bal"] = cur_b

        dashboard_caption = (
            f"{get_text(chat_id, 'running_dashboard', site_name=sess.get('site_name', 'Amar Club'), start_bal=f'{cur_b:.2f}', target_bal=f'{target_total:.2f}', steps=sess['total_steps'])}\n\n"
            f"<b>{to_bold('LIVE STATUS')}</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
        )

        display_or_replace_photo(
            chat_id,
            start_snap,
            dashboard_caption,
            get_trading_control_keyboard(0)
        )

        if os.path.exists(start_snap):
            try:
                os.remove(start_snap)
            except Exception:
                pass

# ==========================================
# 12. Bot Initialization
# ==========================================
if __name__ == "__main__":
    print(f"[*] {to_bold('WINGO VIP BOT MULTI-INSTANCE READY')}...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
