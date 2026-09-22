#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
DISTRIBUTED CLIENT-SIDE WORKER RUNTIME & EXECUTION ENGINE
File Name   : worker.py
Architecture: Autonomous Node Execution Daemon (Selenium Firefox + Firebase RTDB)
Standard    : Pure ASCII Formatting, Robust Fault Tolerance, Zero Code Omission
================================================================================
"""

# ==============================================================================
# SECTION 1: AUTOMATIC DEPENDENCY RESOLUTION & SYSTEM IMPORTS
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

def ensure_runtime_packages():
    required_packages = {
        "requests": "requests",
        "selenium": "selenium",
        "psutil": "psutil"
    }
    for mod_name, pkg_name in required_packages.items():
        try:
            __import__(mod_name)
        except ImportError:
            sys.stdout.write(f"[*] Missing runtime module: {pkg_name}. Installing via pip...\n")
            sys.stdout.flush()
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
            except subprocess.CalledProcessError as exc:
                sys.stderr.write(f"[!] Package installation failed for {pkg_name}: {exc}\n")
                sys.exit(1)

ensure_runtime_packages()

import requests
import psutil
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import (
    WebDriverException,
    JavascriptException,
    TimeoutException,
    NoSuchElementException,
    SessionNotCreatedException
)

# ==============================================================================
# SECTION 2: GLOBAL CONFIGURATION & SYSTEM CONSTANTS
# ==============================================================================
FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

def resolve_node_identifier() -> str:
    env_node_id = os.environ.get("NODE_ID")
    if env_node_id and env_node_id.strip():
        return env_node_id.strip().upper()
    try:
        mac_addr = uuid.getnode()
        mac_hex = f"{mac_addr:012X}"
        return f"W-NODE-{mac_hex[-6:]}"
    except Exception:
        fallback_uuid = str(uuid.uuid4())[:8].upper()
        return f"W-NODE-{fallback_uuid}"

NODE_ID = resolve_node_identifier()
PROFILES_BASE_DIR = os.path.expanduser(f"~/.worker_profiles_{NODE_ID}")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

HEARTBEAT_INTERVAL_SEC = 6.0
WATCHDOG_CHECK_INTERVAL_SEC = 2.0
NETWORK_RETRY_DELAY_SEC = 5.0

# ==============================================================================
# SECTION 3: PURE ASCII BOX FORMATTING & LOGGING ENGINE
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(NODE_ID)

def print_ascii_card(title: str, lines: list, min_width: int = 60):
    content_width = max([len(title)] + [len(str(line)) for line in lines] + [min_width])
    horizontal_border = "─" * (content_width + 2)
    top_border = f"┌{horizontal_border}┐"
    divider_border = f"├{horizontal_border}┤"
    bottom_border = f"└{horizontal_border}┘"

    output = [top_border]
    output.append(f"│ {title.center(content_width)} │")
    output.append(divider_border)
    for line in lines:
        output.append(f"│ {str(line).ljust(content_width)} │")
    output.append(bottom_border)
    sys.stdout.write("\n" + "\n".join(output) + "\n")
    sys.stdout.flush()

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
# SECTION 5: SYSTEM & PROCESS CLEANUP ENGINE
# ==============================================================================
class ProcessCleanupManager:
    @staticmethod
    def kill_zombie_processes(session_id: str = None):
        """Terminates stray Firefox and Geckodriver instances to release memory."""
        current_pid = os.getpid()
        target_binaries = ["geckodriver", "firefox", "firefox-bin", "firefox.exe", "geckodriver.exe"]
        killed_count = 0

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                p_info = proc.info
                p_name = p_info['name'].lower() if p_info['name'] else ""
                p_cmd = " ".join(p_info['cmdline']).lower() if p_info['cmdline'] else ""

                if proc.pid == current_pid:
                    continue

                is_match = any(b in p_name for b in target_binaries)
                if not is_match and session_id and session_id.lower() in p_cmd:
                    is_match = True

                if is_match:
                    proc.kill()
                    killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if killed_count > 0:
            logger.info(f"Cleaned up {killed_count} orphan browser/driver process(es).")

    @staticmethod
    def purge_profile_directory(session_id: str):
        if not session_id:
            return
        profile_path = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_path):
            try:
                shutil.rmtree(profile_path, ignore_errors=True)
                logger.info(f"Purged isolated profile directory: {profile_path}")
            except Exception as e:
                logger.warning(f"Error purging profile {profile_path}: {e}")

# ==============================================================================
# SECTION 6: RESILIENT FIREBASE REALTIME DATABASE CLIENT
# ==============================================================================
class FirebaseNodeClient:
    def __init__(self, base_url: str, node_id: str):
        self.base_url = base_url.rstrip("/")
        self.node_id = node_id
        self.session = requests.Session()
        self.lock = threading.Lock()

    def _url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.strip('/')}.json"

    def register_or_sync_node(self) -> bool:
        """Initializes or reconciles node state in the cluster registry."""
        node_endpoint = f"nodes/{self.node_id}"
        payload = {
            "status": "FREE",
            "active_user_id": None,
            "assigned_at": None,
            "expires_at": None,
            "last_heartbeat": int(time.time()),
            "task_payload": None,
            "system_info": {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "hostname": socket.gethostname(),
                "pid": os.getpid()
            }
        }
        try:
            resp = self.session.patch(self._url(node_endpoint), json=payload, timeout=10.0)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Cluster registration error: {e}")
            return False

    def emit_heartbeat(self) -> bool:
        try:
            data = {"last_heartbeat": int(time.time())}
            resp = self.session.patch(self._url(f"nodes/{self.node_id}"), json=data, timeout=8.0)
            return resp.status_code == 200
        except Exception:
            return False

    def get_node_state(self) -> dict:
        try:
            resp = self.session.get(self._url(f"nodes/{self.node_id}"), timeout=10.0)
            if resp.status_code == 200 and resp.text != "null":
                return resp.json() or {}
        except Exception as e:
            logger.debug(f"Failed to fetch state: {e}")
        return {}

    def update_node_state(self, updates: dict) -> bool:
        with self.lock:
            try:
                resp = self.session.patch(self._url(f"nodes/{self.node_id}"), json=updates, timeout=10.0)
                return resp.status_code == 200
            except Exception as e:
                logger.error(f"Failed to update node state: {e}")
                return False

    def set_status_free(self) -> bool:
        updates = {
            "status": "FREE",
            "active_user_id": None,
            "assigned_at": None,
            "expires_at": None,
            "task_payload": None
        }
        return self.update_node_state(updates)

    def log_node_event(self, message: str):
        timestamp = int(time.time())
        try:
            self.session.post(self._url(f"nodes/{self.node_id}/audit_logs"), json={
                "timestamp": timestamp,
                "message": message
            }, timeout=6.0)
        except Exception:
            pass

# ==============================================================================
# SECTION 7: DEDICATED SELENIUM DRIVER RUNTIME
# ==============================================================================
class IsolatedDriverSession:
    def __init__(self, session_id: str, headless: bool = True):
        self.session_id = session_id
        self.headless = headless
        self.profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        os.makedirs(self.profile_dir, exist_ok=True)
        self.driver = None
        self.lock = threading.RLock()

    def spawn(self, target_url: str):
        with self.lock:
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("-profile")
            options.add_argument(self.profile_dir)

            # High-performance in-memory caching and clean headless options
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", True)
            options.set_preference("network.http.use-cache", False)
            options.set_preference("dom.ipc.plugins.enabled", False)
            options.set_preference("media.volume_scale", "0.0")

            service = FirefoxService(log_output=os.devnull)
            self.driver = webdriver.Firefox(service=service, options=options)
            self.driver.set_window_size(390, 844)  # iPhone 12 standard viewport
            self.driver.set_page_load_timeout(35.0)
            self.driver.set_script_timeout(30.0)
            self.driver.get(target_url)
            return self.driver

    def execute_script_safe(self, script: str, *args):
        with self.lock:
            if not self.driver:
                return None
            try:
                return self.driver.execute_script(script, *args)
            except (WebDriverException, JavascriptException) as e:
                logger.debug(f"JS execution notice: {e.msg if hasattr(e, 'msg') else e}")
                return None
            except Exception as e:
                logger.debug(f"General script exception: {e}")
                return None

    def teardown(self):
        with self.lock:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                finally:
                    self.driver = None
            ProcessCleanupManager.kill_zombie_processes(self.session_id)
            ProcessCleanupManager.purge_profile_directory(self.session_id)

# ==============================================================================
# SECTION 8: AUTOMATION EXECUTION & SESSION WORKER
# ==============================================================================
class AutomationSessionWorker:
    def __init__(self, client: FirebaseNodeClient, session_id: str, task_payload: dict, expires_at: int):
        self.client = client
        self.session_id = session_id
        self.task_payload = task_payload
        self.expires_at = expires_at
        self.interrupted = threading.Event()
        self.driver_session = None

    def trigger_interrupt(self, reason: str = "Admin Force-Kill"):
        logger.warning(f"Session {self.session_id} interrupt flagged: {reason}")
        self.interrupted.set()
        if self.driver_session:
            self.driver_session.teardown()

    def run_session(self) -> bool:
        target_url = self.task_payload.get("target_url")
        wingo_url = self.task_payload.get("wingo_url")
        phone = self.task_payload.get("phone")
        password = self.task_payload.get("password")
        target_profit = float(self.task_payload.get("target_profit", 0))
        total_steps = int(self.task_payload.get("total_steps", 7))

        if not target_url or not phone or not password:
            logger.error(f"Invalid task payload parameters for session {self.session_id}.")
            return False

        logger.info(f"Initializing browser tab for session: {self.session_id}")
        self.driver_session = IsolatedDriverSession(self.session_id, headless=True)

        try:
            self.driver_session.spawn(target_url)
        except Exception as e:
            logger.error(f"Failed to spawn Firefox instance: {e}")
            self.driver_session.teardown()
            return False

        if self.interrupted.is_set():
            return False

        # Phase 1: Authentication Form Injection
        logger.info("Injecting credentials via DOM automation...")
        fill_confirmed = False
        for _ in range(60):
            if self.interrupted.is_set():
                return False
            res = self.driver_session.execute_script_safe(AUTO_FILL_AND_CLICK_JS, phone, password)
            if res == "SUCCESS":
                fill_confirmed = True
                time.sleep(2.0)
                break
            time.sleep(0.5)

        if not fill_confirmed:
            logger.error("Login form elements could not be detected or submitted.")
            self.driver_session.teardown()
            return False

        # Phase 2: Login Status Verification
        logger.info("Verifying session authentication state...")
        authenticated = False
        for _ in range(45):
            if self.interrupted.is_set():
                return False
            stat = self.driver_session.execute_script_safe(CHECK_LOGIN_STATUS_JS)
            if isinstance(stat, dict):
                if stat.get("status") == "SUCCESS":
                    authenticated = True
                    break
                elif stat.get("status") == "CONFIRM_CLICKED":
                    time.sleep(1.5)
                    continue
                elif stat.get("status") == "ERROR":
                    logger.error(f"Remote authentication rejected: {stat.get('message')}")
                    self.driver_session.teardown()
                    return False
            time.sleep(0.5)

        token_ok = self.driver_session.execute_script_safe(
            "return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));"
        )
        if token_ok:
            authenticated = True

        if not authenticated:
            logger.error("Authentication timed out or failed.")
            self.driver_session.teardown()
            return False

        logger.info("Login verified. Transitioning to target WinGo market...")
        time.sleep(1.5)

        # Phase 3: Route to Target WinGo Engine Page
        self.driver_session.execute_script_safe(WINGO_RUNBOX_AND_CLICK_JS)
        if wingo_url:
            self.driver_session.execute_script_safe(
                """
                const dest = arguments[0];
                if (!window.location.href.includes('WinGo')) {
                    window.location.href = dest;
                }
                """, wingo_url
            )

        wingo_ready = False
        for _ in range(30):
            if self.interrupted.is_set():
                return False
            if self.driver_session.execute_script_safe(CHECK_WINGO_READY_JS):
                wingo_ready = True
                break
            time.sleep(0.8)

        if not wingo_ready:
            logger.warning("WinGo readiness check was indeterminate. Attempting core injection...")

        # Extract Initial Balance
        initial_balance = 0.0
        for _ in range(15):
            bal = self.driver_session.execute_script_safe(FETCH_BALANCE_JS)
            if bal and float(bal) > 0:
                initial_balance = float(bal)
                break
            time.sleep(0.4)

        logger.info(f"Verified wallet balance: {initial_balance:.2f}")

        # Phase 4: Core Engine Script Injection
        logger.info(f"Injecting WinGo Martingale engine. Target: {target_profit} | Steps: {total_steps}")
        core_resp = self.driver_session.execute_script_safe(WINGO_CORE_JS, target_profit, total_steps)
        logger.info(f"Core script execution status: {core_resp}")

        # Phase 5: Continuous In-Session Monitoring Loop
        logger.info("Engine fully operational. Continuous background monitoring active.")
        while not self.interrupted.is_set():
            if self.expires_at and time.time() >= self.expires_at:
                logger.info(f"24-Hour session limit reached for session {self.session_id}.")
                break

            telemetry = self.driver_session.execute_script_safe("""
                if (window.__WINGO_ST) {
                    return {
                        isRun: window.__WINGO_ST.isRun,
                        curBal: window.__WINGO_ST.curBal || 0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0,
                        startBal: window.__WINGO_ST.startBal || 0,
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                        cur_l_streak: window.__WINGO_ST.cur_l_streak || 0
                    };
                }
                return null;
            """)

            if telemetry and isinstance(telemetry, dict):
                current_bal = telemetry.get("curBal", 0)
                target_amt = telemetry.get("tgtAmt", 0)
                if current_bal >= target_amt and target_amt > 0 and current_bal > 0:
                    logger.info(f"Profit target attained: {current_bal} >= {target_amt}. Session successful.")
                    break

            time.sleep(WATCHDOG_CHECK_INTERVAL_SEC)

        self.driver_session.teardown()
        return True

# ==============================================================================
# SECTION 9: BACKGROUND HEARTBEAT & REMOTE EVENT WATCHDOG
# ==============================================================================
class ClusterRuntimeWatchdog:
    def __init__(self, client: FirebaseNodeClient):
        self.client = client
        self.running = True
        self.current_worker = None
        self.lock = threading.Lock()

    def set_active_worker(self, worker: AutomationSessionWorker):
        with self.lock:
            self.current_worker = worker

    def clear_active_worker(self):
        with self.lock:
            self.current_worker = None

    def start_heartbeat_loop(self):
        def _loop():
            backoff = 1.0
            while self.running:
                ok = self.client.emit_heartbeat()
                if ok:
                    backoff = 1.0
                else:
                    backoff = min(backoff * 1.5, 30.0)
                    time.sleep(backoff)
                time.sleep(HEARTBEAT_INTERVAL_SEC)
        t = threading.Thread(target=_loop, name="HeartbeatThread", daemon=True)
        t.start()

    def start_kill_switch_listener(self):
        def _loop():
            while self.running:
                try:
                    node_data = self.client.get_node_state()
                    status = node_data.get("status", "").upper()

                    if status == "FORCE_KILL":
                        logger.warning("Administrative FORCE_KILL signal received!")
                        with self.lock:
                            if self.current_worker:
                                self.current_worker.trigger_interrupt("Admin Force-Kill")
                        self.client.log_node_event("Session terminated by Administrator.")
                        self.client.set_status_free()
                except Exception as e:
                    logger.debug(f"Kill switch poll exception: {e}")
                time.sleep(2.0)
        t = threading.Thread(target=_loop, name="KillSwitchThread", daemon=True)
        t.start()

# ==============================================================================
# SECTION 10: MAIN WORKER ORCHESTRATION ENGINE
# ==============================================================================
def main():
    terminal_banner = [
        f"Node Identifier    : {NODE_ID}",
        f"Firebase Database  : {FIREBASE_PROJECT_ID}",
        f"Engine Runtime     : FIREFOX HEADLESS MULTI-TAB",
        f"Process PID        : {os.getpid()}",
        f"Storage Directory  : {PROFILES_BASE_DIR}",
        "Cluster Listener   : ACTIVE & POLLING FOR TASKS"
    ]
    print_ascii_card(to_bold("WORKER EXECUTION ENGINE ONLINE"), terminal_banner)

    ProcessCleanupManager.kill_zombie_processes()
    firebase_client = FirebaseNodeClient(FIREBASE_DATABASE_URL, NODE_ID)

    # Initial cluster handshake
    connected = False
    for attempt in range(1, 11):
        if firebase_client.register_or_sync_node():
            connected = True
            logger.info("Connected and registered with centralized cluster.")
            break
        logger.warning(f"Connecting to cluster... (Attempt {attempt}/10)")
        time.sleep(NETWORK_RETRY_DELAY_SEC)

    if not connected:
        logger.critical("Could not establish connection to Firebase RTDB. Terminating worker.")
        sys.exit(1)

    watchdog = ClusterRuntimeWatchdog(firebase_client)
    watchdog.start_heartbeat_loop()
    watchdog.start_kill_switch_listener()

    def sig_handler(signum, frame):
        logger.info("Termination signal received. Releasing node and exiting...")
        watchdog.running = False
        if watchdog.current_worker:
            watchdog.current_worker.trigger_interrupt("Process Exit")
        firebase_client.update_node_state({"status": "OFFLINE", "active_user_id": None})
        ProcessCleanupManager.kill_zombie_processes()
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    # Main Task Polling Loop
    while True:
        try:
            node_state = firebase_client.get_node_state()
            current_status = node_state.get("status", "FREE").upper()

            if current_status == "BUSY":
                task_payload = node_state.get("task_payload")
                active_user = node_state.get("active_user_id")
                expires_at = node_state.get("expires_at")

                if task_payload and isinstance(task_payload, dict):
                    session_id = task_payload.get("session_id", f"SESSION_{int(time.time())}")
                    task_lines = [
                        f"Session ID     : {session_id}",
                        f"Target URL     : {task_payload.get('target_url')}",
                        f"Active User    : {active_user}",
                        f"Expiration     : {expires_at if expires_at else 'NONE'}"
                    ]
                    print_ascii_card(to_bold("DISPATCHING ACTIVE TASK"), task_lines)

                    worker = AutomationSessionWorker(
                        client=firebase_client,
                        session_id=session_id,
                        task_payload=task_payload,
                        expires_at=expires_at
                    )
                    watchdog.set_active_worker(worker)

                    try:
                        worker.run_session()
                    except Exception as exc:
                        logger.error(f"Unhandled session exception: {exc}")
                    finally:
                        watchdog.clear_active_worker()
                        firebase_client.set_status_free()
                        logger.info("Session cycle completed. Node state reset to FREE.")

            elif current_status == "FORCE_KILL":
                firebase_client.set_status_free()

        except Exception as e:
            logger.error(f"Core orchestration loop error: {e}")

        time.sleep(2.5)

if __name__ == "__main__":
    main()
