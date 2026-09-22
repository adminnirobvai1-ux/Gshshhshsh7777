#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTONOMOUS DISTRIBUTED WORKER ENGINE & REAL-TIME TELEGRAM STREAMER
File Name   : worker.py
Architecture: Dedicated Node Daemon (Chromium / Firefox Headless + Telegram Bot API + Firebase RTDB)
Standard    : Zero Code Omission, Full JavaScript Payload Preservation, Real-Time Photo Controls
"""

# ==============================================================================
# SECTION 1: AUTOMATIC PACKAGE INSTALLER & SYSTEM IMPORTS
# ==============================================================================
import os
import sys
import subprocess
import time
import threading
import shutil
import json
import socket
import uuid
import signal
import platform
import logging

def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        sys.stdout.write(f"[*] Installing package: {package_name}...\n")
        sys.stdout.flush()
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

install_and_import("pyTelegramBotAPI", "telebot")
install_and_import("selenium")
install_and_import("requests")
install_and_import("psutil")

import requests
import psutil
import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    WebDriverException,
    JavascriptException,
    TimeoutException,
    NoSuchElementException,
    SessionNotCreatedException
)

# ==============================================================================
# SECTION 2: CONFIGURATION, NODE IDENTITY & GLOBAL STATE
# ==============================================================================
BOT_TOKEN = "8808949150:AAGehY-s2kZKblgZtYqwtsCiDRypLx8O8hU"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"

def resolve_node_id() -> str:
    env_id = os.environ.get("NODE_ID")
    if env_id and env_id.strip():
        return env_id.strip().upper()
    try:
        mac_addr = uuid.getnode()
        return f"W-NODE-{mac_addr:012X}"[-9:]
    except Exception:
        return f"W-NODE-{str(uuid.uuid4())[:6].upper()}"

NODE_ID = resolve_node_id()
PROFILES_BASE_DIR = os.path.expanduser(f"~/.worker_profiles_{NODE_ID}")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

# Thread-safe execution lock and active driver context
global_driver_lock = threading.RLock()
active_driver_instance = None
current_session_info = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(NODE_ID)

# ==============================================================================
# SECTION 3: MATHEMATICAL BOLD UNICODE & UTILITY FUNCTIONS
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
    if not message_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

def kill_zombie_browser_processes():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            name = proc.info['name'].lower() if proc.info['name'] else ""
            if any(b in name for b in ["chromedriver", "chromium", "chrome", "firefox", "geckodriver"]):
                proc.kill()
        except Exception:
            pass

# ==============================================================================
# SECTION 4: UNTRUNCATED IN-BROWSER JAVASCRIPT AUTOMATION PAYLOADS
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
# SECTION 5: SMART TELEGRAM IMAGE REPLACEMENT ENGINE
# ==============================================================================
def display_or_replace_photo(chat_id, session_id, image_path, caption_text, reply_markup=None):
    last_photo_msg_id = current_session_info.get("live_photo_message_id")
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
                current_session_info["live_photo_message_id"] = msg.message_id
        except Exception as e:
            sys.stderr.write(f"[*] Photo replacement error: {e}\n")

def get_trading_control_keyboard(sid):
    current_session_info["anim_tick"] = current_session_info.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[current_session_info["anim_tick"] % len(SPINNER_FRAMES)]

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

# ==============================================================================
# SECTION 6: DUAL CHROMIUM & FIREFOX BROWSER LOADER
# ==============================================================================
def spawn_isolated_driver(session_id: str, target_url: str):
    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    # 1. Attempt Chromium/Chrome Execution First (Optimized for Railway/Ubuntu)
    try:
        c_options = ChromeOptions()
        c_options.add_argument("--headless")
        c_options.add_argument("--no-sandbox")
        c_options.add_argument("--disable-dev-shm-usage")
        c_options.add_argument("--disable-gpu")
        c_options.add_argument(f"--user-data-dir={profile_dir}")
        c_options.add_argument("--window-size=390,844")

        chrome_binaries = ["/usr/bin/chromium-browser", "/usr/bin/chromium", "/usr/bin/google-chrome"]
        for c_bin in chrome_binaries:
            if os.path.exists(c_bin):
                c_options.binary_location = c_bin
                break

        driver_paths = ["/usr/bin/chromedriver", "/usr/lib/chromium-browser/chromedriver", "/usr/local/bin/chromedriver"]
        selected_driver = None
        for d_path in driver_paths:
            if os.path.exists(d_path):
                selected_driver = d_path
                break

        c_service = ChromeService(executable_path=selected_driver) if selected_driver else ChromeService()
        drv = webdriver.Chrome(service=c_service, options=c_options)
        drv.set_page_load_timeout(35.0)
        drv.get(target_url)
        return drv
    except Exception as e_chrome:
        logger.warning(f"Chromium spawn failed: {e_chrome}. Falling back to Firefox...")

    # 2. Fallback to Firefox
    f_options = FirefoxOptions()
    f_options.add_argument("--headless")
    f_options.add_argument("-profile")
    f_options.add_argument(profile_dir)
    f_options.set_preference("browser.cache.disk.enable", False)
    f_options.set_preference("browser.cache.memory.enable", True)
    f_options.set_preference("network.http.use-cache", False)

    f_service = FirefoxService(log_output=os.devnull)
    drv = webdriver.Firefox(service=f_service, options=f_options)
    drv.set_window_size(390, 844)
    drv.set_page_load_timeout(35.0)
    drv.get(target_url)
    return drv

# ==============================================================================
# SECTION 7: IN-SESSION TELEGRAM LIVE CALLBACK DISPATCHER
# ==============================================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith(("shot:", "bal:", "stats:", "stop:")))
def handle_live_trading_callbacks(call):
    global active_driver_instance, current_session_info
    action, sid = call.data.split(":", 1)
    chat_id = call.message.chat.id

    if not active_driver_instance or current_session_info.get("session_id") != sid:
        bot.answer_callback_query(call.id, "সেশনটি এই টার্মিনালে সক্রিয় নেই!", show_alert=True)
        return

    with global_driver_lock:
        if action == "shot":
            bot.answer_callback_query(call.id, "ফুটেজ সংগ্রহ করা হচ্ছে...")
            shot_path = os.path.join(PROFILES_BASE_DIR, f"live_{sid}.png")
            try:
                active_driver_instance.save_screenshot(shot_path)
                cur_b = current_session_info.get("cur_bal", current_session_info.get("start_bal", 0.0))
                t_total = current_session_info.get("start_bal", 0.0) + current_session_info.get("target_profit", 0.0)
                caption = (
                    f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                    f"• প্ল্যাটফর্ম: <b>{current_session_info.get('site_name', '')}</b>\n"
                    f"• শুরুর ব্যালেন্স: <code>৳ {current_session_info.get('start_bal', 0.0):.2f}</code>\n"
                    f"• টার্গেট ব্যালেন্স: <code>৳ {t_total:.2f}</code>\n"
                    f"• মার্টিনগেল স্টেপস: <b>{current_session_info.get('total_steps', 7)}</b>\n\n"
                    f"সময়: <code>{time.strftime('%H:%M:%S')}</code>\n"
                    f"স্ট্যাটাস: মার্টিনগেল ইঞ্জিন সফলভাবে ট্রেড পরিচালনা করছে।"
                )
                display_or_replace_photo(chat_id, sid, shot_path, caption, get_trading_control_keyboard(sid))
                if os.path.exists(shot_path): os.remove(shot_path)
            except Exception as e:
                bot.send_message(chat_id, f"ফুটেজ ক্যাপচার এরর: {e}")

        elif action == "bal":
            try:
                b = active_driver_instance.execute_script("return window.__WINGO_ST ? window.__WINGO_ST.curBal : 0;")
                bot.answer_callback_query(call.id, f"লাইভ ব্যালেন্স: ৳ {float(b):.2f}", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "ব্যালেন্স লোড হচ্ছে...", show_alert=True)

        elif action == "stats":
            try:
                data = active_driver_instance.execute_script("""
                    if(window.__WINGO_ST) {
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
                if data:
                    stat_msg = (
                        f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                        f"• ব্যালেন্স: <code>৳ {data['curBal']:.2f}</code>\n"
                        f"• টার্গেট: <code>৳ {data['tgtAmt']:.2f}</code>\n"
                        f"• মার্টিনগেল লেভেল: <b>Step {data['step']}/{data['maxStep']}</b>\n"
                        f"• উইন: <b>{data['w']}</b> | লস: <b>{data['l']}</b>"
                    )
                    bot.send_message(chat_id, stat_msg)
                else:
                    bot.answer_callback_query(call.id, "ইঞ্জিন ডাটা সিঙ্ক হচ্ছে...", show_alert=True)
            except Exception:
                bot.answer_callback_query(call.id, "ডাটা রিড এরর", show_alert=True)

        elif action == "stop":
            try:
                active_driver_instance.execute_script("let b = document.querySelector('#sys-core-fin button'); if(b) b.click();")
                current_session_info["is_trading"] = False
                bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
                bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং অটোমেশন সাময়িকভাবে থামানো হয়েছে।")
            except Exception:
                pass

# Background thread for handling Telegram inline callback interactions instantly
threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True), daemon=True).start()

# ==============================================================================
# SECTION 8: WORKER TASK EXECUTION PIPELINE
# ==============================================================================
def execute_session_pipeline(task_payload: dict) -> bool:
    global active_driver_instance, current_session_info

    session_id = task_payload.get("session_id")
    chat_id = task_payload.get("chat_id")
    site_name = task_payload.get("site_name", "Amar Club")
    target_url = task_payload.get("target_url")
    wingo_url = task_payload.get("wingo_url")
    phone = task_payload.get("phone")
    password = task_payload.get("password")
    target_profit = float(task_payload.get("target_profit", 0))
    total_steps = int(task_payload.get("total_steps", 7))
    scripts = task_payload.get("scripts", {})

    current_session_info = {
        "session_id": session_id,
        "chat_id": chat_id,
        "site_name": site_name,
        "target_profit": target_profit,
        "total_steps": total_steps,
        "is_trading": True,
        "live_photo_message_id": None
    }

    bot.send_message(chat_id, f"<b>{to_bold('TERMINAL CONNECTED')}</b>\nনোড <code>{NODE_ID}</code> ব্রাউজার চালু করছে এবং লগইন পেজে প্রবেশ করছে...")

    with global_driver_lock:
        try:
            active_driver_instance = spawn_isolated_driver(session_id, target_url)
        except Exception as e:
            bot.send_message(chat_id, f"ব্রাউজার চালু করতে ব্যর্থ হয়েছে: {e}")
            return False

        # Phase 1: Authentication Form Injection
        fill_ok = False
        for _ in range(60):
            try:
                res = active_driver_instance.execute_script(scripts.get("AUTO_FILL_AND_CLICK_JS", AUTO_FILL_AND_CLICK_JS), phone, password)
                if res == "SUCCESS":
                    fill_ok = True
                    time.sleep(2.0)
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not fill_ok:
            bot.send_message(chat_id, "লগইন ফর্ম পাওয়া যায়নি বা ইনপুট ফেইল হয়েছে।")
            active_driver_instance.quit()
            active_driver_instance = None
            return False

        # Phase 2: Login Status Verification
        authenticated = False
        for _ in range(40):
            try:
                stat = active_driver_instance.execute_script(scripts.get("CHECK_LOGIN_STATUS_JS", CHECK_LOGIN_STATUS_JS))
                if isinstance(stat, dict) and stat.get("status") == "SUCCESS":
                    authenticated = True
                    break
                if active_driver_instance.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));"):
                    authenticated = True
                    break
            except Exception:
                pass
            time.sleep(0.5)

        if not authenticated:
            bot.send_message(chat_id, "লগইন ব্যর্থ বা টাইমআউট হয়েছে। ফোন নম্বর ও পাসওয়ার্ড যাচাই করুন।")
            active_driver_instance.quit()
            active_driver_instance = None
            return False

        time.sleep(1.5)

        # Phase 3: Login Snapshot to Telegram
        login_snap = os.path.join(PROFILES_BASE_DIR, f"login_{session_id}.png")
        active_driver_instance.save_screenshot(login_snap)
        masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
        login_caption = (
            f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
            f"• প্ল্যাটফর্ম: <b>{site_name}</b>\n"
            f"• অ্যাকাউন্ট: <code>{masked_phone}</code>\n\n"
            f"উইনগো মার্কেটে রিডাইরেক্ট করা হচ্ছে..."
        )
        display_or_replace_photo(chat_id, session_id, login_snap, login_caption)
        if os.path.exists(login_snap): os.remove(login_snap)

        # Phase 4: Route to WinGo 30S
        try:
            active_driver_instance.execute_script(scripts.get("WINGO_RUNBOX_AND_CLICK_JS", WINGO_RUNBOX_AND_CLICK_JS))
            active_driver_instance.execute_script("if(!window.location.href.includes('WinGo')) window.location.href = arguments[0];", wingo_url)
        except Exception:
            pass

        time.sleep(3.0)

        # Phase 5: Fetch Live Balance
        current_balance = 0.0
        for _ in range(15):
            try:
                bal = active_driver_instance.execute_script(scripts.get("FETCH_BALANCE_JS", FETCH_BALANCE_JS))
                if bal and float(bal) > 0:
                    current_balance = float(bal)
                    break
            except Exception:
                pass
            time.sleep(0.5)

        current_session_info["start_bal"] = current_balance

        # Phase 6: Inject Core Martingale Automation Engine
        try:
            active_driver_instance.execute_script(scripts.get("WINGO_CORE_JS", WINGO_CORE_JS), target_profit, total_steps)
        except Exception as e:
            bot.send_message(chat_id, f"ট্রেডিং ইঞ্জিন ইনজেকশন এরর: {e}")
            active_driver_instance.quit()
            active_driver_instance = None
            return False

        time.sleep(2.0)

        # Phase 7: Send Live Dashboard Photo with Interactive Controls
        run_snap = os.path.join(PROFILES_BASE_DIR, f"run_{session_id}.png")
        active_driver_instance.save_screenshot(run_snap)
        target_total = current_balance + target_profit
        dashboard_caption = (
            f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
            f"• প্ল্যাটফর্ম: <b>{site_name}</b>\n"
            f"• শুরুর ব্যালেন্স: <code>৳ {current_balance:.2f}</code>\n"
            f"• টার্গেট ব্যালেন্স: <code>৳ {target_total:.2f}</code>\n"
            f"• মার্টিনগেল স্টেপস: <b>{total_steps}</b>\n\n"
            f"মার্টিনগেল ইঞ্জিন সফলভাবে স্বয়ংক্রিয় ট্রেডিং পরিচালনা করছে।"
        )
        display_or_replace_photo(chat_id, session_id, run_snap, dashboard_caption, get_trading_control_keyboard(session_id))
        if os.path.exists(run_snap): os.remove(run_snap)

    # Phase 8: Continuous Background Telemetry Loop
    while current_session_info.get("is_trading"):
        with global_driver_lock:
            if not active_driver_instance:
                break
            try:
                st = active_driver_instance.execute_script("""
                    if(window.__WINGO_ST) {
                        return {
                            curBal: window.__WINGO_ST.curBal || 0,
                            tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                            w: window.__WINGO_ST.w || 0,
                            l: window.__WINGO_ST.l || 0
                        };
                    }
                    return null;
                """)
                if st:
                    current_session_info["cur_bal"] = st.get("curBal", 0)
                    tgt = st.get("tgtAmt", 0)
                    if current_session_info["cur_bal"] >= tgt and tgt > 0 and current_session_info["cur_bal"] > 0:
                        # Target achieved!
                        win_snap = os.path.join(PROFILES_BASE_DIR, f"win_{session_id}.png")
                        active_driver_instance.save_screenshot(win_snap)
                        profit = current_session_info["cur_bal"] - current_balance
                        win_msg = (
                            f"<b>{to_bold('TARGET ACHIEVED SUCCESSFULLY')}</b>\n\n"
                            f"কাঙ্ক্ষিত টার্গেট সম্পূর্ণ সফলভাবে পূরণ হয়েছে!\n\n"
                            f"• শুরুর ব্যালেন্স: <code>৳ {current_balance:.2f}</code>\n"
                            f"• শেষ ব্যালেন্স: <code>৳ {current_session_info['cur_bal']:.2f}</code>\n"
                            f"• অর্জিত প্রফিট: <code>+৳ {profit:.2f}</code>\n"
                            f"• মোট উইন: <b>{st.get('w', 0)}</b> | লস: <b>{st.get('l', 0)}</b>"
                        )
                        display_or_replace_photo(chat_id, session_id, win_snap, win_msg, None)
                        if os.path.exists(win_snap): os.remove(win_snap)
                        break
            except Exception:
                pass

        time.sleep(3.0)

    with global_driver_lock:
        if active_driver_instance:
            try:
                active_driver_instance.quit()
            except Exception:
                pass
            active_driver_instance = None
    kill_zombie_browser_processes()
    return True

# ==============================================================================
# SECTION 9: MAIN WORKER DAEMON & FIREBASE SYNCHRONIZER
# ==============================================================================
def main():
    sys.stdout.write("==================================================\n")
    sys.stdout.write(f"[*] AUTONOMOUS WORKER RUNTIME STARTED: {NODE_ID}\n")
    sys.stdout.write(f"[*] FIREBASE CLUSTER TARGET: {FIREBASE_DATABASE_URL}\n")
    sys.stdout.write("==================================================\n")
    sys.stdout.flush()

    kill_zombie_browser_processes()

    # Heartbeat daemon
    def _heartbeat():
        while True:
            try:
                requests.patch(
                    f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json",
                    json={"last_heartbeat": int(time.time())},
                    timeout=5.0
                )
            except Exception:
                pass
            time.sleep(6.0)

    threading.Thread(target=_heartbeat, daemon=True).start()

    # Initial registration with central cluster
    try:
        requests.patch(
            f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json",
            json={"status": "FREE", "active_user_id": None, "task_payload": None},
            timeout=10.0
        )
    except Exception as e:
        logger.error(f"Initial register failed: {e}")

    def sig_handler(signum, frame):
        logger.info("Termination signal received. Cleaning node...")
        global active_driver_instance
        with global_driver_lock:
            if active_driver_instance:
                try: active_driver_instance.quit()
                except Exception: pass
        kill_zombie_browser_processes()
        try:
            requests.patch(
                f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json",
                json={"status": "OFFLINE", "active_user_id": None},
                timeout=5.0
            )
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Core Polling Loop
    while True:
        try:
            r = requests.get(f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json", timeout=10.0)
            if r.status_code == 200 and r.text != "null":
                node_data = r.json() or {}
                status = node_data.get("status", "FREE").upper()

                if status == "BUSY":
                    payload = node_data.get("task_payload")
                    if payload and isinstance(payload, dict):
                        logger.info(f"Task payload received for session: {payload.get('session_id')}")
                        try:
                            execute_session_pipeline(payload)
                        except Exception as e:
                            logger.error(f"Pipeline error: {e}")
                        finally:
                            # Reset back to free
                            requests.patch(
                                f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json",
                                json={"status": "FREE", "active_user_id": None, "task_payload": None},
                                timeout=10.0
                            )
                            logger.info(f"Task completed. Node {NODE_ID} reset to FREE.")

                elif status == "FORCE_KILL":
                    logger.warning("Administrative FORCE_KILL signal received!")
                    with global_driver_lock:
                        if active_driver_instance:
                            try: active_driver_instance.quit()
                            except Exception: pass
                            active_driver_instance = None
                    kill_zombie_browser_processes()
                    requests.patch(
                        f"{FIREBASE_DATABASE_URL}/nodes/{NODE_ID}.json",
                        json={"status": "FREE", "active_user_id": None, "task_payload": None},
                        timeout=10.0
                    )

        except Exception as e:
            logger.error(f"Worker polling error: {e}")

        time.sleep(2.0)

if __name__ == "__main__":
    main()
