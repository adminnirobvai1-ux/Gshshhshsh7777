import os
import sys
import subprocess
import time
import threading
import shutil
import tempfile

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
# ২. কনফিগারেশন, নতুন টোকেন ও লিঙ্কসমূহ
# ==========================================
TOKEN = "8808949150:AAF236nZ7xG3kPxlxubELHqChpn4IPycFL4"
bot = telebot.TeleBot(TOKEN)

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"

URL_AMARCLUB_GAME = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_GAME = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_fixed_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

active_browsers = {}
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
            print(f"[*] ২৪ ঘণ্টা পার হওয়ায় সেশন {session_key} বন্ধ করা হচ্ছে...")
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
    """ক্র্যাশ ছাড়া পাশাপাশি একাধিক ব্রাউজার চালানোর নিরপেক্ষ লঞ্চার"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

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
    options.set_preference("dom.webnotifications.enabled", False)
    options.set_preference("dom.push.enabled", False)

    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    driver.get(target_url)
    return driver

# ==========================================
# ৪. জাভাস্ক্রিপ্ট স্ক্রিপ্টসমূহ
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

FETCH_BALANCE_JS = r"""
function chkBal(){
    let els = document.querySelectorAll('*');
    for(let i=0; i<els.length; i++){
        let txt = els[i].innerText || '';
        if(txt.includes('Wallet balance') || txt.includes('Balance')){
            let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
            let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
            if(match){
                return parseFloat(match[1].replace(/,/g,''));
            }
        }
    }
    for(let i=0; i<els.length; i++){
        let txt = els[i].innerText || '';
        if(txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)){
            return parseFloat(txt.replace(/[^\d.]/g,''));
        }
    }
    return null;
}
return chkBal();
"""

MARTINGALE_SCRIPT_JS = r"""(function(){if(document.getElementById('sys-core-fin'))return;const uF=s=>String(s).toUpperCase().split('').map(c=>{let n=c.charCodeAt(0);if(n>=65&&n<=90)return String.fromCodePoint(n+119743);if(n>=48&&n<=57)return String.fromCodePoint(n+120764);return c;}).join('');const cfg={fRt:300,syncDly:2500,minSf:10};let st={isRun:false,startBal:0,tgtAmt:0,curBal:0,autoInt:null,preScn:null,isTrd:false,stpIdx:0,dynSeq:[],totalSteps:10,tradesDone:0,lastPred:null,lastPeriod:null,balanceCheckInterval:null,manualOverrideBet:null,w:0,l:0};let curApiIdx=0,isFetchingApi=false;const VoiceEngine={speak(msg,lang='en-US',rate=1.1){if(!('speechSynthesis' in window))return;window.speechSynthesis.cancel();let utter=new SpeechSynthesisUtterance(msg);utter.lang=lang;utter.rate=rate;utter.pitch=1.2;utter.volume=1;window.speechSynthesis.speak(utter);}};let dTimeLeft=30;setInterval(()=>{let uClk=document.getElementById('ui-clk');if(uClk){let minutes=Math.floor(dTimeLeft/60),seconds=dTimeLeft%60;uClk.textContent=uF(`${String(minutes).padStart(2,'0')}:${String(seconds).padStart(2,'0')}`);}dTimeLeft--;if(dTimeLeft<0)dTimeLeft=30;},1000);let lkOvl=document.createElement('div');lkOvl.id='drx-lck-bg';lkOvl.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.01);z-index:9999997;display:none;';lkOvl.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();},true);document.body.appendChild(lkOvl);function chkBal(){let els=document.querySelectorAll('*');for(let i=0;i<els.length;i++){let txt=els[i].innerText||'';if(txt.includes('Wallet balance')||txt.includes('Balance')){let parentTxt=(els[i].parentNode&&els[i].parentNode.innerText)?els[i].parentNode.innerText:'';let match=parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);if(match){st.curBal=parseFloat(match[1].replace(/,/g,''));return st.curBal;}}}for(let i=0;i<els.length;i++){let txt=els[i].innerText||'';if(txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)){st.curBal=parseFloat(txt.replace(/[^\d.]/g,''));return st.curBal;}}return st.curBal;}function generateSmartSequence(balance,steps){steps=Math.max(1,parseInt(steps)||1);let b=Math.max(1,Math.floor(balance)||1);let units=Math.pow(2,steps)-1;if(units>0&&units<=b){let base=Math.floor(b/units);let seq=[],val=base;for(let i=0;i<steps;i++){seq.push(val);val*=2;}return seq;}let seq=[],val=1,sum=0;for(let i=0;i<steps;i++){if(sum+val<=b){seq.push(val);sum+=val;val*=2;}else{let rem=b-sum;if(rem>0)seq.push(rem);break;}}return seq.length>0?seq:[1];}let p=document.createElement('div');p.id='sys-core-fin';p.style.cssText='position:fixed;width:170px;padding:4px;font-family:monospace;font-size:10px;z-index:9999999;color:#fff;user-select:none;border-radius:14px;overflow:visible;background:transparent;';let sL=localStorage.getItem('drx_ui_x'),sT=localStorage.getItem('drx_ui_y');if(sL&&sT){p.style.left=sL;p.style.top=sT;}else{p.style.top='20px';p.style.right='20px';}let stl=document.createElement('style');stl.innerHTML='@keyframes titlePulseAnim{0%{transform:scale(1);text-shadow:0 0 10px #00ff00;}50%{transform:scale(1.05);text-shadow:0 0 20px #00ff00,0 0 30px #fff;}100%{transform:scale(1);text-shadow:0 0 10px #00ff00;}}.drx-in{background:transparent;position:relative;overflow:visible;z-index:1;display:flex;flex-direction:column;height:100%;border-radius:12px;border:2px solid #000;box-sizing:border-box;}input::-webkit-outer-spin-button,input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0;}.txt-blk{color:#fff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-accent{color:#00ff00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-warn{color:#ffcc00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-err{color:#f00;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-cyan{color:#0ff;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.txt-blk-mag{color:#f0f;text-shadow:1px 1px 0 #000,-1px -1px 0 #000,1px -1px 0 #000,-1px 1px 0 #000,0px 4px 5px #000;font-weight:900;letter-spacing:1px;}.drx-elec-target{border-radius:8px!important;position:relative;z-index:9999!important;transition:all 0.1s;background:rgba(0,0,0,0.5)!important;border:2px solid #000!important;}.drx-title-anim{display:inline-block;animation:titlePulseAnim 2s infinite ease-in-out;}';document.body.appendChild(stl);p.className='drx-wrap';let inC=document.createElement('div');inC.className='drx-in';let h=document.createElement('div');h.style.cssText='padding:8px;font-size:12px;display:flex;justify-content:space-between;cursor:move;border-bottom:2px solid #000;background:transparent;';h.innerHTML=`<span class="txt-blk drx-title-anim" id="drx-title">${uF('WINZY-MARTINGALE')}</span><span style="cursor:pointer;" class="txt-blk-err" id="sys-cls">X</span>`;inC.appendChild(h);let drg=false,sx,sy,sl,st_y;function dSt(e){if(e.target.tagName==='SPAN')return;drg=true;let ev=e.type.includes('touch')?e.touches[0]:e;sx=ev.clientX;sy=ev.clientY;sl=p.offsetLeft;st_y=p.offsetTop;}function dMv(e){if(!drg)return;e.preventDefault();let ev=e.type.includes('touch')?e.touches[0]:e;p.style.left=(sl+ev.clientX-sx)+'px';p.style.top=(st_y+ev.clientY-sy)+'px';}function dEn(){drg=false;localStorage.setItem('drx_ui_x',p.style.left);localStorage.setItem('drx_ui_y',p.style.top);}h.addEventListener('mousedown',dSt);h.addEventListener('touchstart',dSt,{passive:false});document.addEventListener('mousemove',dMv);document.addEventListener('touchmove',dMv,{passive:false});document.addEventListener('mouseup',dEn);document.addEventListener('touchend',dEn);h.querySelector('#sys-cls').onclick=()=>{clearInterval(st.autoInt);clearInterval(st.preScn);if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);p.remove();lkOvl.remove();document.body.style.overflow='';};let b=document.createElement('div');b.style.cssText='padding:10px;display:flex;flex-direction:column;gap:8px;background:transparent;';const p1=document.createElement('div');p1.innerHTML=`<div style="text-align:center;margin-bottom:8px;padding:6px;background:transparent;border-radius:6px;border:2px solid #000;"><span class="txt-blk" style="font-size:9px;color:#ccc;">${uF('CURRENT BAL')}</span><br><span id="pre-bal" class="txt-blk" style="font-size:15px;color:#fff;">--</span></div>`;const tgtInp=document.createElement('input');tgtInp.type='number';tgtInp.placeholder='TARGET PROFIT (৳)';tgtInp.className='txt-blk';tgtInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#fff;';const stepInp=document.createElement('input');stepInp.type='number';stepInp.placeholder='TOTAL STEPS (e.g. 7)';stepInp.className='txt-blk-cyan';stepInp.style.cssText='width:100%;box-sizing:border-box;padding:8px;margin-bottom:8px;background:transparent;border:2px solid #000;border-radius:4px;text-align:center;font-size:11px;outline:none;color:#0ff;';const goBtn=document.createElement('button');goBtn.innerText=uF('START');goBtn.className='txt-blk-accent';goBtn.style.cssText='width:100%;box-sizing:border-box;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;font-weight:bold;transition:0.2s;';p1.appendChild(tgtInp);p1.appendChild(stepInp);p1.appendChild(goBtn);st.preScn=setInterval(()=>{if(!st.isRun){let bal=chkBal();let el=document.getElementById('pre-bal');if(el)el.innerText=uF(bal>0?bal.toFixed(2):'--');}},1000);const p2=document.createElement('div');p2.style.display='none';const balBx=document.createElement('div');balBx.style.cssText='padding:6px;text-align:center;background:transparent;border-radius:6px;border:2px solid #000;margin-bottom:6px;';balBx.innerHTML=`<div class="txt-blk" style="font-size:9px;color:#ccc;">${uF('LIVE BAL / PROFIT')}</div><div id="ui-bal" class="txt-blk" style="font-size:16px;color:#fff;">--</div>`;let aiRow=`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('AI:')}</span><span id="ui-ai" class="txt-blk-cyan">VIP JSON API</span></div>`;const infBx=document.createElement('div');infBx.style.cssText='padding:6px;font-size:10px;line-height:2;background:transparent;border-radius:6px;border:2px solid #000;position:relative;overflow:hidden;';infBx.innerHTML=aiRow+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('TGT:')}</span><span id="ui-tgt" class="txt-blk" style="color:#fff;">0</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;" title="Double-click to set manual fixed bet"><span class="txt-blk" style="color:#ccc;">${uF('STP:')}</span><span id="ui-bet" class="txt-blk-warn" style="color:#ffcc00;cursor:pointer;">5</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('CLK:')}</span><span id="ui-clk" class="txt-blk" style="color:#fff;">00:30</span></div>`+`<div style="display:flex;justify-content:space-between;border-bottom:2px dashed #000;"><span class="txt-blk" style="color:#ccc;">${uF('STS:')}</span><span id="ui-sts" class="txt-blk" style="color:#fff;">${uF('WAIT')}</span></div>`;const ghBox=document.createElement('div');ghBox.id='gh-box-wrap';ghBox.style.cssText='width:100%;height:26px;background:transparent;border:2px solid #000;border-radius:4px;padding:2px 4px;margin-top:4px;box-sizing:border-box;overflow:hidden;display:flex;flex-direction:column;justify-content:center;';ghBox.innerHTML='<div id="gh-content" class="txt-blk" style="font-size:7.5px;line-height:1.2;color:#fff;white-space:pre-wrap;text-align:left;width:100%;">Syncing API...</div>';infBx.appendChild(ghBox);const stpBtn=document.createElement('button');stpBtn.innerText=uF('STOP');stpBtn.className='txt-blk-err';stpBtn.style.cssText='width:100%;padding:8px;background:transparent;border:2px solid #000;border-radius:4px;cursor:pointer;font-size:11px;margin-top:6px;transition:0.2s;';p2.appendChild(balBx);p2.appendChild(infBx);p2.appendChild(stpBtn);b.appendChild(p1);b.appendChild(p2);inC.appendChild(b);p.appendChild(inC);document.body.appendChild(p);setTimeout(()=>{let uBetEl=document.getElementById('ui-bet');if(uBetEl){uBetEl.ondblclick=function(){let currentVal=st.manualOverrideBet||(st.dynSeq&&st.dynSeq[st.stpIdx])||0;let val=prompt("Set Custom Fixed Bet (Enter 0 to clear state):",currentVal);if(val!==null&&!isNaN(val)){let parsed=parseFloat(val);st.manualOverrideBet=parsed>0?parsed:null;this.innerText=uF(st.manualOverrideBet?st.manualOverrideBet+' (FIX)':st.dynSeq[st.stpIdx]);}};}},1000);const drx_triggerEvent=(el,etype)=>{let ev=new Event(etype,{bubbles:true,cancelable:true});el.dispatchEvent(ev);};const drx_simClick=el=>{if(!el)return;['pointerdown','mousedown','touchstart','pointerup','mouseup','touchend','click'].forEach(evt=>{try{el.dispatchEvent(new MouseEvent(evt,{bubbles:true,cancelable:true,view:window}));}catch(e){}});};const exeTrd=(pred,amt,cb)=>{try{let btn=null,targetText=pred.toLowerCase(),btns=document.querySelectorAll('button, div, span');for(let i=0;i<btns.length;i++){let t=(btns[i].innerText||'').trim().toLowerCase();if(t===targetText&&btns[i].offsetParent&&!btns[i].children.length){btn=btns[i];break;}}if(!btn){if(targetText==='big')btn=document.querySelector('.Betting__C-foot-b');else if(targetText==='small')btn=document.querySelector('.Betting__C-foot-s');else if(targetText==='green')btn=document.querySelector('button[class*="green"], div[class*="green"]');else if(targetText==='red')btn=document.querySelector('button[class*="red"], div[class*="red"]');else if(targetText==='violet')btn=document.querySelector('button[class*="violet"], div[class*="violet"]');}if(!btn){if(cb)cb(false);return;}btn.classList.add('drx-elec-target');drx_simClick(btn);let checkAttempts=0,valInterval=setInterval(()=>{checkAttempts++;let inpEl=document.querySelector("input[type='number'], input.van-field__control");if(inpEl||checkAttempts>15){clearInterval(valInterval);if(inpEl){inpEl.focus();let setV=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,"value").set;if(setV)setV.call(inpEl,String(amt));else inpEl.value=amt;drx_triggerEvent(inpEl,'input');drx_triggerEvent(inpEl,'change');drx_triggerEvent(inpEl,'blur');}setTimeout(()=>{let dEl=document.querySelector('button.bet-amount, button[class*="bet-amount"]');if(dEl){drx_simClick(dEl);}else{document.querySelectorAll('button').forEach(b=>{if((b.innerText||'').includes('Total amount')&&b.offsetParent)drx_simClick(b);});}btn.classList.remove('drx-elec-target');setTimeout(()=>{if(cb)cb(true);},2000);},800);}},200);}catch(e){if(cb)cb(false);}};const scnUI=cb=>{let ov=document.createElement('div');ov.style.cssText='position:fixed;top:0;left:0;width:100vw;height:100vh;background:transparent;z-index:9999998;pointer-events:none;overflow:hidden;';let cBase='#00ff00',rL=document.createElement('div');rL.style.cssText=`position:absolute;width:100%;height:2px;background:${cBase};box-shadow:0 0 10px 3px ${cBase};animation:sR 0.6s linear infinite alternate;`;let gL=document.createElement('div');gL.style.cssText=`position:absolute;height:100%;width:3px;background:${cBase};box-shadow:0 0 15px 5px ${cBase};animation:sG 0.6s cubic-bezier(0.25,0.1,0.25,1) infinite alternate;`;let sS=document.createElement('style');sS.innerHTML='@keyframes sR{0%{top:-10px;}100%{top:100vh;}}@keyframes sG{0%{left:-10px;}100%{left:100vw;}}';document.head.appendChild(sS);ov.appendChild(rL);ov.appendChild(gL);document.body.appendChild(ov);setTimeout(()=>{ov.remove();sS.remove();if(cb)cb();},1500);};const getNextLivePeriod=str=>{let chars=str.split('');for(let i=chars.length-1;i>=0;i--){if(chars[i]!=='9'){chars[i]=String.fromCharCode(chars[i].charCodeAt(0)+1);return chars.join('');}chars[i]='0';}return '1'+chars.join('');};const apiLoopTask=async()=>{if(!st.isRun||st.isTrd||isFetchingApi)return;isFetchingApi=true;try{chkBal();const uBal=document.getElementById('ui-bal'),uSts=document.getElementById('ui-sts'),uBet=document.getElementById('ui-bet');if(st.curBal>=st.tgtAmt&&st.curBal>0){uBal.innerText=uF(`${st.curBal.toFixed(2)} (DONE)`);uSts.innerText=uF('DONE');uSts.className='txt-blk-accent';stpBtn.style.display='none';VoiceEngine.speak("Target reached successfully.");st.isRun=false;clearInterval(st.autoInt);lkOvl.style.display='none';document.body.style.overflow='';let dWrap=document.createElement('div');dWrap.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:20px;border:2px solid #00ff00;border-radius:10px;z-index:99999999;text-align:center;box-shadow:0 0 30px #00ff00;';dWrap.innerHTML=`<h2 style="color:#00ff00;margin-bottom:10px;font-family:monospace;">TARGET REACHED</h2><p style="color:#fff;font-family:monospace;margin-bottom:15px;">Balance: ${st.curBal.toFixed(2)}</p><button id="closeDWrap" style="background:transparent;color:#00ff00;border:1px solid #00ff00;padding:5px 15px;cursor:pointer;">OK</button>`;document.body.appendChild(dWrap);document.getElementById('closeDWrap').onclick=()=>dWrap.remove();return;}else{uBal.innerText=uF(st.curBal>0?st.curBal.toFixed(2):'--');}let ts=Math.floor(Date.now()/1000),res=await fetch("https://data-vip-247-hack.ai.studio/apipid.json?ts="+ts),dataArray=await res.json();if(dataArray&&dataArray.length>0){if(curApiIdx>=dataArray.length)curApiIdx=0;let activeLogic=dataArray[curApiIdx],tempHist=activeLogic.history,cSig=getNextLivePeriod(String(tempHist[0].pid)),sSig=sessionStorage.getItem('drx_sig');if(cSig!==sSig){if(st.lastPred&&st.lastPeriod){let actualData=tempHist[0],actualR=actualData.actual==='BIG'?'BIG':'SMALL';if(st.lastPred===actualR){st.w++;st.stpIdx=0;}else{st.l++;st.stpIdx=Math.min(st.stpIdx+1,st.dynSeq.length-1);curApiIdx=(curApiIdx===0&&dataArray.length>1)?1:0;}}st.lastPeriod=cSig;let timeLeft=dTimeLeft;if(timeLeft<=cfg.minSf){uSts.innerText=uF('<10S');uSts.className='txt-blk-warn';}st.isTrd=true;uSts.innerText=uF('CHK...');uSts.className='txt-blk-warn';let nBal=chkBal();uBal.innerText=uF(nBal.toFixed(2));if(nBal>=st.tgtAmt&&nBal>0){st.isTrd=false;isFetchingApi=false;return;}if(st.stpIdx>=st.dynSeq.length)st.stpIdx=st.dynSeq.length-1;let tAmt=st.manualOverrideBet?st.manualOverrideBet:st.dynSeq[st.stpIdx];uBet.innerText=uF(st.manualOverrideBet?tAmt+' (FIX)':`${tAmt} (S${st.stpIdx+1})`);if(nBal<tAmt){uSts.innerText=uF('LOW');uSts.className='txt-blk-err';st.stpIdx=0;st.isTrd=false;isFetchingApi=false;return;}uSts.innerText=uF('DB...');uSts.className='txt-blk-cyan';setTimeout(()=>{let activeLogicNew=dataArray[curApiIdx],prediction=(activeLogicNew.pred||'BIG').toUpperCase();st.lastPred=prediction;let predDisplay=document.getElementById('ui-pred');if(!predDisplay){predDisplay=document.createElement('span');predDisplay.id='ui-pred';predDisplay.className='txt-blk-accent';predDisplay.style.cssText='color: #00ff00 !important; margin-left: 5px; font-weight: bold;';let betSpan=document.getElementById('ui-bet');if(betSpan)betSpan.parentNode.appendChild(predDisplay);}predDisplay.innerText=prediction==='BIG'?'[B]':(prediction==='SMALL'?'[S]':'[SKP]');let ghC=document.getElementById('gh-content');if(ghC)ghC.textContent=`Step: ${st.stpIdx+1}/${st.dynSeq.length} (Amt: ${tAmt})\nPred: ${prediction} | W:${st.w} L:${st.l}`;if(prediction==='SKIP'){uSts.innerText=uF('SKIP');uSts.className='txt-blk-warn';sessionStorage.setItem('drx_sig',cSig);setTimeout(()=>{st.isTrd=false;},1000);}else{uSts.innerText=uF('EXC...');uSts.className='txt-blk';exeTrd(prediction,tAmt,(suc)=>{if(suc){uSts.innerText=uF('OK');uSts.className='txt-blk-accent';sessionStorage.setItem('drx_sig',cSig);sessionStorage.setItem('drx_p_bal',st.curBal);st.tradesDone++;}else{uSts.innerText=uF('ERR');uSts.className='txt-blk-err';}setTimeout(()=>{st.isTrd=false;},1000);});}},1800);}else if(!st.isTrd){uSts.innerText=uF('SCAN');uSts.className='txt-blk';}}}catch(e){st.isTrd=false;}isFetchingApi=false;};goBtn.onclick=()=>{let inputTarget=parseFloat(tgtInp.value);if(!inputTarget||inputTarget<=0){alert('Please enter Target Profit Amount!');tgtInp.focus();return;}let inputSteps=parseInt(stepInp.value)||1;if(inputSteps<=0)inputSteps=1;st.totalSteps=inputSteps;clearInterval(st.preScn);st.tradesDone=0;st.w=0;st.l=0;curApiIdx=0;let liveB=chkBal();st.startBal=liveB;st.tgtAmt=(inputTarget<=liveB)?(liveB+inputTarget):inputTarget;st.dynSeq=generateSmartSequence(liveB,st.totalSteps);st.stpIdx=0;VoiceEngine.speak("Engine started with smart step calculation.");scnUI(()=>{sessionStorage.removeItem('drx_sig');sessionStorage.removeItem('drx_p_bal');document.getElementById('ui-tgt').innerText=uF(st.tgtAmt.toFixed(0));p1.style.display='none';p2.style.display='block';lkOvl.style.display='block';document.body.style.overflow='hidden';st.isRun=true;st.isTrd=false;document.getElementById('ui-sts').innerText=uF('RDY');st.autoInt=setInterval(apiLoopTask,1000);if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);st.balanceCheckInterval=setInterval(()=>{if(!st.isRun)return;let currentBal=chkBal();if(currentBal>=st.tgtAmt&&currentBal>0){st.isRun=false;clearInterval(st.autoInt);clearInterval(st.balanceCheckInterval);st.balanceCheckInterval=null;const uSts=document.getElementById('ui-sts');if(uSts){uSts.innerText=uF('DONE');uSts.className='txt-blk-accent';}stpBtn.style.display='none';lkOvl.style.display='none';document.body.style.overflow='';VoiceEngine.speak("Target reached. Engine stopped.");let dWrap=document.createElement('div');dWrap.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.9);padding:20px;border:2px solid #00ff00;border-radius:10px;z-index:99999999;text-align:center;box-shadow:0 0 30px #00ff00;';dWrap.innerHTML=`<h2 style="color:#00ff00;margin-bottom:10px;font-family:monospace;">TARGET REACHED</h2><p style="color:#fff;font-family:monospace;margin-bottom:15px;">Balance: ${currentBal.toFixed(2)}</p><button id="closeDWrap" style="background:transparent;color:#00ff00;border:1px solid #00ff00;padding:5px 15px;cursor:pointer;">OK</button>`;document.body.appendChild(dWrap);document.getElementById('closeDWrap').onclick=()=>dWrap.remove();}},1000);});};stpBtn.onclick=()=>{st.isRun=false;clearInterval(st.autoInt);if(st.balanceCheckInterval)clearInterval(st.balanceCheckInterval);st.balanceCheckInterval=null;sessionStorage.removeItem('drx_sig');sessionStorage.removeItem('drx_p_bal');document.getElementById('ui-sts').innerText=uF('HLT');document.getElementById('ui-sts').className='txt-blk-err';lkOvl.style.display='none';document.body.style.overflow='';stpBtn.innerText=uF('RBT');stpBtn.onclick=()=>{p2.style.display='none';p1.style.display='block';stpBtn.innerText=uF('STOP');st.preScn=setInterval(()=>{let b=chkBal();let el=document.getElementById('pre-bal');if(el)el.innerText=uF(b>0?b.toFixed(2):'--');},1000);};};})();"""

START_MARTINGALE_TRIGGER_JS = """
const targetProfit = arguments[0];
const totalSteps = arguments[1];

let p = document.getElementById('sys-core-fin');
if (p) {
    let tInp = p.querySelector('input[placeholder*="TARGET PROFIT"]');
    let sInp = p.querySelector('input[placeholder*="TOTAL STEPS"]');
    let btns = p.querySelectorAll('button');
    let goBtn = btns[0];

    if (tInp && sInp && goBtn) {
        tInp.value = targetProfit;
        tInp.dispatchEvent(new Event('input', { bubbles: true }));
        tInp.dispatchEvent(new Event('change', { bubbles: true }));

        sInp.value = totalSteps;
        sInp.dispatchEvent(new Event('input', { bubbles: true }));
        sInp.dispatchEvent(new Event('change', { bubbles: true }));

        setTimeout(() => {
            goBtn.click();
        }, 500);
        return true;
    }
}
return false;
"""

# ==========================================
# ৫. ব্যাকগ্রাউন্ড লগইন ও অটোমেশন প্রসেস
# ==========================================
def process_login(chat_id, session_key, phone, password, status_msg_id):
    state = user_states.get(chat_id, {})
    site_name = state.get("site_name")
    site_url = state.get("site_url")
    profile_path = state.get("profile_path")
    profile_name = state.get("profile_name")
    is_temp = state.get("is_temp", False)

    stop_anim = threading.Event()
    def spinner():
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while not stop_anim.is_set():
            try:
                bot.edit_message_text(
                    f"⏳ **{site_name}**-এ লগইন সম্পন্ন হচ্ছে... [ {spinners[i % len(spinners)]} ]\n"
                    f"ব্রাউজার লোড হচ্ছে...",
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

    if login_status in ["SUCCESS", "PENDING"]:
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
            "is_temp": is_temp
        }

        # গেম লিংকে অটোমেটিক রিডাইরেক্ট করা
        game_url = URL_AMARCLUB_GAME if site_name == "Amarclub1" else URL_DKWIN_GAME
        bot.edit_message_text(
            f"🎉 **লগইন সফল হয়েছে!**\n\n"
            f"🌐 গেম পেজে রিডাইরেক্ট করা হচ্ছে:\n`{game_url}`\n"
            f"⏳ ব্যালেন্স রিড করা হচ্ছে...",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )

        try:
            driver.get(game_url)
        except Exception as e:
            print(f"[!] গেম রিডাইরেকশনে সতর্কতা: {e}")

        # পেজ ও ব্যালেন্স রিড হওয়ার জন্য অপেক্ষা
        time.sleep(6)
        live_bal = None
        for _ in range(15):
            try:
                live_bal = driver.execute_script(FETCH_BALANCE_JS)
                if live_bal is not None and live_bal >= 0:
                    break
            except Exception:
                pass
            time.sleep(1)

        bal_str = f"{live_bal:.2f} ৳" if (live_bal is not None) else "লোড হতে পারেনি"
        state["live_bal"] = live_bal if live_bal is not None else 0
        state["session_key"] = session_key
        state["step"] = "WAITING_TARGET_PROFIT"

        bot.send_message(
            chat_id,
            f"✅ **গেম পেজ (WinGo 30s) সফলভাবে ট্রিগার হয়েছে!**\n\n"
            f"💰 **বর্তমান ব্যালেন্স:** `{bal_str}`\n\n"
            f"🎯 আপনি মোট কত টাকা **প্রফিট (Target Profit)** করতে চান? সংখ্যাটি লিখে পাঠান (যেমন: `500`):",
            parse_mode="Markdown"
        )
    else:
        try:
            driver.quit()
        except Exception:
            pass
        bot.edit_message_text(
            f"⚠️ **লগইন ব্যর্থ হয়েছে!**\n\n"
            f"🌐 **সাইট:** {site_name}\n"
            f"❌ **কারণ:** {err_detail}",
            chat_id=chat_id,
            message_id=status_msg_id,
            parse_mode="Markdown"
        )

# ==========================================
# ৬. টেলিগ্রাম মেনু ও ইন্টারফেস
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
        "🚀 **লগইন ও অটো-ট্রেড কন্ট্রোল প্যানেল**\n\nঅনুগ্রহ করে প্রথমে সাইট নির্বাচন করুন:", 
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

        bot.answer_callback_query(call.id, "নতুন ফ্রেশ প্রোফাইল প্রস্তুত!")
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

# ==========================================
# ৭. টেক্সট মেসেজ ইনপুট ও অটোমেশন এক্সিকিউশন
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
        state["step"] = "PROCESSING"

        session_key = f"{chat_id}_{state['profile_name']}"
        status_msg = bot.send_message(chat_id, "⏳ ব্রাউজার ওপেন এবং লগইন প্রক্রিয়া শুরু হচ্ছে... [ ⠋ ]")

        threading.Thread(
            target=process_login,
            args=(chat_id, session_key, state["phone"], state["password"], status_msg.message_id),
            daemon=True
        ).start()

    # ধাপ ২: টার্গেট প্রফিট গ্রহণ
    elif step == "WAITING_TARGET_PROFIT":
        try:
            target_val = float(text)
            if target_val <= 0:
                bot.send_message(chat_id, "❌ টার্গেট অ্যামাউন্ট ০ এর বেশি হতে হবে। আবার লিখুন:")
                return
        except ValueError:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে শুধুমাত্র সংখ্যা লিখুন (যেমন: 500):")
            return

        state["target_profit"] = target_val
        state["step"] = "WAITING_STEPS"

        bot.send_message(
            chat_id,
            f"🎯 টার্গেট প্রফিট: `{target_val}` ৳ সংরক্ষিত হয়েছে।\n\n"
            f"🔢 এবার মোট **মার্টিনগেল স্টেপ (Total Steps)** লিখে পাঠান (যেমন: `7`):",
            parse_mode="Markdown"
        )

    # ধাপ ৩: মার্টিনগেল স্টেপ গ্রহণ এবং অটো-ট্রেড ইনজেকশন
    elif step == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0:
                steps_val = 1
        except ValueError:
            bot.send_message(chat_id, "❌ অনুগ্রহ করে একটি পূর্ণ সংখ্যা লিখুন (যেমন: 7):")
            return

        state["total_steps"] = steps_val
        state["step"] = "RUNNING_AUTOMATION"

        session_key = state.get("session_key")
        sess = active_browsers.get(session_key)

        if not sess or not sess.get("driver"):
            bot.send_message(chat_id, "❌ ব্রাউজার সেশন পাওয়া যায়নি। অনুগ্রহ করে /start দিয়ে পুনরায় চালু করুন।")
            return

        driver = sess["driver"]
        bot.send_message(chat_id, "⏳ উইনজি-মার্টিনগেল অটোমেশন স্ক্রিপ্ট ইনজেক্ট এবং চালু করা হচ্ছে...")

        try:
            # ১. জাভাস্ক্রিপ্ট ইঞ্জিন ইনজেক্ট করা
            driver.execute_script(MARTINGALE_SCRIPT_JS)
            time.sleep(1.5)

            # ২. টার্গেট ও স্টেপ বসিয়ে স্বয়ংক্রিয়ভাবে START বাটনে ক্লিক
            started = driver.execute_script(START_MARTINGALE_TRIGGER_JS, state["target_profit"], state["total_steps"])

            if started:
                bot.send_message(
                    chat_id,
                    f"🚀 **অটো-ট্রেডিং সফলভাবে চালু হয়েছে!**\n\n"
                    f"🌐 **প্ল্যাটফর্ম:** {sess['site_name']}\n"
                    f"💰 **মূল ব্যালেন্স:** {state.get('live_bal', 0):.2f} ৳\n"
                    f"🎯 **টার্গেট প্রফিট:** {state['target_profit']:.2f} ৳\n"
                    f"🔢 **মার্টিনগেল স্টেপ:** {state['total_steps']}\n\n"
                    f"⚡ ব্রাউজারের ব্যাকগ্রাউন্ডে স্বয়ংক্রিয় সিগন্যাল ও ট্রেড চলছে। টার্গেট সম্পন্ন হলে স্ক্রিপ্ট অটোমেটিক থেমে যাবে।",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(chat_id, "⚠️ অটোমেশন প্যানেল তৈরি হয়েছে, তবে স্টার্ট হতে বিলম্ব হচ্ছে। VNC স্ক্রিনে ব্রাউজার চেক করে নিন।")
        except Exception as e:
            bot.send_message(chat_id, f"❌ অটোমেশন চালু করার সময় ত্রুটি ঘটেছে:\n`{e}`", parse_mode="Markdown")

# ==========================================
# ৮. বট বুটস্ট্র্যাপ ও ওয়েব-হুক ক্লিয়ার
# ==========================================
if __name__ == "__main__":
    # Webhook Conflict (Error 409) দূরীকরণে স্বয়ংক্রিয় ডিলিট
    try:
        print("[*] সক্রিয় ওয়েব-হুক চেক ও ডিলিট করা হচ্ছে...")
        bot.remove_webhook()
        time.sleep(1)
    except Exception as e:
        print(f"[!] ওয়েব-হুক নোটিশ: {e}")

    print("[*] টেলিগ্রাম বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling(skip_pending=True)
