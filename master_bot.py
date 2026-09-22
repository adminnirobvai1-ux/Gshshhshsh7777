#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASTER CONTROLLER & DISTRIBUTED CLUSTER ORCHESTRATOR
File Name: master_bot.py
Architecture: Hybrid Central Master (Telegram + SQLite + Firebase RTDB Cluster)
Visual Standard: Pure ASCII Box Formatting & Bold Unicode (Strictly Zero Emojis)
"""

# ==============================================================================
# SECTION 1: AUTOMATIC DEPENDENCY INSTALLATION & CORE IMPORTS
# ==============================================================================
import os
import sys
import subprocess
import time
import threading
import json
import sqlite3
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

def ensure_dependencies():
    packages = {
        "telebot": "pyTelegramBotAPI",
        "requests": "requests"
    }
    for mod_name, pkg_name in packages.items():
        try:
            __import__(mod_name)
        except ImportError:
            sys.stdout.write(f"[*] Package missing: {pkg_name}. Installing...\n")
            sys.stdout.flush()
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])

ensure_dependencies()

import telebot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import requests

# ==============================================================================
# SECTION 2: SYSTEM CONFIGURATION & GLOBAL CONSTANTS
# ==============================================================================
BOT_TOKEN = "8808949150:AAGehY-s2kZKblgZtYqwtsCiDRypLx8O8hU"
OWNER_ID = 8707571669
CHANNEL_URL = "https://t.me/DARK67HACK"
CHANNEL_ID = "@DARK67HACK"

BKASH_NUMBER = "01870829343"
NAGAD_NUMBER = "01876685711"
SUBSCRIPTION_PRICE_BDT = 350.0

FREE_MODE_REFERRAL_QUOTA = 5
PAID_MODE_REFERRAL_QUOTA = 10

FIREBASE_DATABASE_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
FIREBASE_PROJECT_ID = "x7e77eey"
FIREBASE_STORAGE_BUCKET = "x7e77eey.firebasestorage.app"
FIREBASE_APP_ID = "1:1083361150222:web:60a5a8371dada67b57c35f"

LOCAL_DB_NAME = "master_controller.db"

URL_AMARCLUB_LOGIN = "https://amarclub1.com/#/login"
URL_DKWIN_LOGIN = "https://dkwin6.com/#/login"
URL_AMARCLUB_WINGO = "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
URL_DKWIN_WINGO = "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"

# ==============================================================================
# SECTION 3: MATHEMATICAL BOLD TYPOGRAPHY & TEXT UTILITIES
# ==============================================================================
def to_bold(text: str) -> str:
    """
    Transforms alphanumeric characters into Mathematical Bold Unicode.
    Uppercase: U+1D400 (base A=65 + 119743)
    Lowercase: U+1D41A (base a=97 + 119737)
    Digits:    U+1D7CE (base 0=48 + 120764)
    """
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

def safe_delete_message(bot_instance, chat_id, message_id):
    if not message_id:
        return
    try:
        bot_instance.delete_message(chat_id=chat_id, message_id=message_id)
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

# ==============================================
# SECTION 5: THREAD-SAFE LOCAL SQLITE CONTROLLER
# ==============================================
class MasterDatabaseManager:
    def __init__(self, db_path: str = LOCAL_DB_NAME):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    joined_channel INTEGER DEFAULT 0,
                    referral_code TEXT,
                    referred_by INTEGER,
                    total_referrals INTEGER DEFAULT 0,
                    access_mode TEXT DEFAULT 'FREE',
                    paid_until INTEGER DEFAULT 0,
                    created_at INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pending_payments (
                    trx_id TEXT PRIMARY KEY,
                    chat_id INTEGER,
                    method TEXT,
                    amount REAL,
                    timestamp INTEGER,
                    status TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    session_id TEXT PRIMARY KEY,
                    chat_id INTEGER,
                    node_id TEXT,
                    start_time INTEGER,
                    end_time INTEGER,
                    is_active INTEGER
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS system_config (
                    config_key TEXT PRIMARY KEY,
                    config_val TEXT
                )
            """)
            cur.execute("INSERT OR IGNORE INTO system_config (config_key, config_val) VALUES ('GLOBAL_MODE', 'FREE_MODE')")
            conn.commit()
            conn.close()

    def get_global_mode(self) -> str:
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT config_val FROM system_config WHERE config_key = 'GLOBAL_MODE'")
            row = cur.fetchone()
            conn.close()
            return row["config_val"] if row else "FREE_MODE"

    def set_global_mode(self, mode: str):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE system_config SET config_val = ? WHERE config_key = 'GLOBAL_MODE'", (mode,))
            conn.commit()
            conn.close()

    def register_user_if_absent(self, chat_id: int, username: str, referred_by: int = None) -> bool:
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT chat_id FROM users WHERE chat_id = ?", (chat_id,))
            exists = cur.fetchone()
            if not exists:
                now = int(time.time())
                ref_code = str(chat_id)
                cur.execute("""
                    INSERT INTO users (chat_id, username, joined_channel, referral_code, referred_by, total_referrals, access_mode, paid_until, created_at)
                    VALUES (?, ?, 0, ?, ?, 0, 'FREE', 0, ?)
                """, (chat_id, username or "", ref_code, referred_by, now))
                conn.commit()
                conn.close()
                return True
            conn.close()
            return False

    def mark_channel_joined(self, chat_id: int):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE users SET joined_channel = 1 WHERE chat_id = ?", (chat_id,))
            cur.execute("SELECT referred_by FROM users WHERE chat_id = ?", (chat_id,))
            row = cur.fetchone()
            if row and row["referred_by"]:
                ref_parent = row["referred_by"]
                cur.execute("UPDATE users SET total_referrals = total_referrals + 1 WHERE chat_id = ?", (ref_parent,))
            conn.commit()
            conn.close()

    def get_user(self, chat_id: int):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None

    def add_payment_record(self, trx_id: str, chat_id: int, method: str, amount: float):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            now = int(time.time())
            cur.execute("""
                INSERT OR REPLACE INTO pending_payments (trx_id, chat_id, method, amount, timestamp, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING')
            """, (trx_id, chat_id, method, amount, now))
            conn.commit()
            conn.close()

    def update_payment_status(self, trx_id: str, status: str):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE pending_payments SET status = ? WHERE trx_id = ?", (status, trx_id))
            cur.execute("SELECT chat_id FROM pending_payments WHERE trx_id = ?", (trx_id,))
            row = cur.fetchone()
            if row and status == "APPROVED":
                cid = row["chat_id"]
                now = int(time.time())
                cur.execute("SELECT paid_until FROM users WHERE chat_id = ?", (cid,))
                u_row = cur.fetchone()
                current_expiry = u_row["paid_until"] if u_row else 0
                new_expiry = max(now, current_expiry) + 86400
                cur.execute("UPDATE users SET paid_until = ?, access_mode = 'PAID' WHERE chat_id = ?", (new_expiry, cid))
            conn.commit()
            conn.close()

    def create_session(self, session_id: str, chat_id: int, node_id: str, duration_sec: int = 86400):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            now = int(time.time())
            end = now + duration_sec
            cur.execute("""
                INSERT OR REPLACE INTO active_sessions (session_id, chat_id, node_id, start_time, end_time, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (session_id, chat_id, node_id, now, end))
            conn.commit()
            conn.close()

    def get_active_session_by_user(self, chat_id: int):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM active_sessions WHERE chat_id = ? AND is_active = 1", (chat_id,))
            row = cur.fetchone()
            conn.close()
            return dict(row) if row else None

    def terminate_session(self, session_id: str):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE active_sessions SET is_active = 0 WHERE session_id = ?", (session_id,))
            conn.commit()
            conn.close()

    def get_expired_sessions(self):
        with self.lock:
            conn = self.get_connection()
            cur = conn.cursor()
            now = int(time.time())
            cur.execute("SELECT * FROM active_sessions WHERE is_active = 1 AND end_time <= ?", (now,))
            rows = cur.fetchall()
            conn.close()
            return [dict(r) for r in rows]

db = MasterDatabaseManager()

# ==============================================================================
# SECTION 6: DISTRIBUTED FIREBASE REALTIME CLUSTER ENGINE
# ==============================================================================
class FirebaseClusterManager:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.strip('/')}.json"

    def fetch_all_nodes(self) -> dict:
        try:
            r = requests.get(self._url("nodes"), timeout=10.0)
            if r.status_code == 200 and r.text != "null":
                return r.json() or {}
        except Exception as e:
            sys.stderr.write(f"[!] Firebase fetch error: {e}\n")
        return {}

    def fetch_node(self, node_id: str) -> dict:
        try:
            r = requests.get(self._url(f"nodes/{node_id}"), timeout=10.0)
            if r.status_code == 200 and r.text != "null":
                return r.json() or {}
        except Exception as e:
            sys.stderr.write(f"[!] Firebase fetch node error: {e}\n")
        return {}

    def update_node(self, node_id: str, data: dict) -> bool:
        try:
            r = requests.patch(self._url(f"nodes/{node_id}"), json=data, timeout=10.0)
            return r.status_code == 200
        except Exception as e:
            sys.stderr.write(f"[!] Firebase update node error: {e}\n")
            return False

    def acquire_free_node(self, user_id: int, duration_sec: int = 86400) -> tuple:
        nodes = self.fetch_all_nodes()
        now = int(time.time())
        for node_id, data in nodes.items():
            st = data.get("status", "FREE").upper()
            if st == "FREE":
                payload = {
                    "status": "BUSY",
                    "active_user_id": user_id,
                    "assigned_at": now,
                    "expires_at": now + duration_sec,
                    "task_payload": None
                }
                if self.update_node(node_id, payload):
                    return node_id, data
        return None, None

    def dispatch_task(self, node_id: str, task_dict: dict) -> bool:
        payload = {
            "status": "BUSY",
            "task_payload": task_dict
        }
        return self.update_node(node_id, payload)

    def force_kill_node(self, node_id: str) -> bool:
        payload = {
            "status": "FORCE_KILL",
            "active_user_id": None,
            "task_payload": None,
            "expires_at": None
        }
        return self.update_node(node_id, payload)

    def release_node(self, node_id: str) -> bool:
        payload = {
            "status": "FREE",
            "active_user_id": None,
            "task_payload": None,
            "assigned_at": None,
            "expires_at": None
        }
        return self.update_node(node_id, payload)

firebase_cluster = FirebaseClusterManager(FIREBASE_DATABASE_URL)

# ==============================================================================
# SECTION 7: INTERFACE BUILDERS & ASCII TEMPLATES (STRICTLY ZERO EMOJIS)
# ==============================================================================
def get_main_persistent_keyboard() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    markup.row(
        KeyboardButton(f"{to_bold('NEW TASK')}"),
        KeyboardButton(f"{to_bold('REFERRAL')}"),
        KeyboardButton(f"{to_bold('TASK')}")
    )
    return markup

def get_channel_gateway_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"{to_bold('CHANNEL')}", url=CHANNEL_URL))
    markup.add(InlineKeyboardButton(f"{to_bold('VERIFY')}", callback_data="action_verify_channel"))
    return markup

def get_platform_selection_keyboard(node_id: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('AMAR CLUB')}", callback_data=f"cfg_site:AMAR:{node_id}"),
        InlineKeyboardButton(f"{to_bold('DK WIN')}", callback_data=f"cfg_site:DKWIN:{node_id}")
    )
    markup.add(InlineKeyboardButton(f"{to_bold('ABORT')}", callback_data=f"cfg_abort:{node_id}"))
    return markup

def get_credentials_input_keyboard(node_id: str, has_phone: bool) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"{to_bold('NUMBER')}", callback_data=f"in_num:{node_id}"),
            InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"in_pwd:{node_id}")
        )
    else:
        markup.add(InlineKeyboardButton(f"{to_bold('PASSWORD')}", callback_data=f"in_pwd:{node_id}"))
    markup.add(InlineKeyboardButton(f"{to_bold('ABORT')}", callback_data=f"cfg_abort:{node_id}"))
    return markup

def get_parameters_setup_keyboard(node_id: str, target: float, steps: int) -> InlineKeyboardMarkup:
    t_str = f"TARGET: {int(target)}" if target > 0 else "TARGET"
    s_str = f"STEPS: {int(steps)}" if steps > 0 else "STEPS"
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold(t_str)}", callback_data=f"in_tgt:{node_id}"),
        InlineKeyboardButton(f"{to_bold(s_str)}", callback_data=f"in_stp:{node_id}")
    )
    markup.add(
        InlineKeyboardButton(f"{to_bold('DISPATCH ENGINE')}", callback_data=f"in_go:{node_id}"),
        InlineKeyboardButton(f"{to_bold('ABORT')}", callback_data=f"cfg_abort:{node_id}")
    )
    return markup

def get_payment_submission_keyboard() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('SUBMIT BKASH')}", callback_data="pay_submit:BKASH"),
        InlineKeyboardButton(f"{to_bold('SUBMIT NAGAD')}", callback_data="pay_submit:NAGAD")
    )
    return markup

def get_admin_approval_keyboard(trx_id: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"{to_bold('APPROVE (24H)')}", callback_data=f"adm_app:{trx_id}"),
        InlineKeyboardButton(f"{to_bold('REJECT')}", callback_data=f"adm_rej:{trx_id}")
    )
    return markup

def format_ascii_box(title: str, lines: list) -> str:
    content_width = max(len(title), 40)
    for l in lines:
        if len(l) > content_width:
            content_width = len(l)
    content_width += 2

    top = f"┌{'─' * content_width}┐"
    divider = f"├{'─' * content_width}┤"
    bottom = f"└{'─' * content_width}┘"

    out = [top]
    out.append(f"│ {title.center(content_width - 2)} │")
    out.append(divider)
    for l in lines:
        out.append(f"│ {l.ljust(content_width - 2)} │")
    out.append(bottom)
    return "\n".join(out)

# ==============================================================================
# SECTION 8: BOT INITIALIZATION & STATE MANAGEMENT
# ==============================================================================
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
user_input_states = {}

def is_user_channel_member(chat_id: int) -> bool:
    try:
        member = bot.get_chat_member(CHANNEL_ID, chat_id)
        if member.status in ['creator', 'administrator', 'member']:
            return True
    except Exception:
        pass
    return False

# ==============================================================================
# SECTION 9: WATCHDOG THREADS (LIFETIME WATCHDOG & HEARTBEAT SCANNER)
# ==============================================================================
def subscription_and_session_watchdog():
    while True:
        try:
            expired = db.get_expired_sessions()
            for sess in expired:
                sid = sess["session_id"]
                nid = sess["node_id"]
                cid = sess["chat_id"]
                sys.stdout.write(f"[*] Expiration trigger for session: {sid} | Node: {nid}\n")
                firebase_cluster.force_kill_node(nid)
                db.terminate_session(sid)
                msg_lines = [
                    "Your allocated 24-hour automation session",
                    "has reached its lifetime expiration.",
                    "Terminal has been cleanly freed."
                ]
                card = format_ascii_box(to_bold("SESSION EXPIRED"), msg_lines)
                try:
                    bot.send_message(cid, f"<pre>{card}</pre>")
                except Exception:
                    pass

            nodes = firebase_cluster.fetch_all_nodes()
            now = int(time.time())
            for nid, ndata in nodes.items():
                st = ndata.get("status", "FREE").upper()
                exp = ndata.get("expires_at")
                if st == "BUSY" and exp and now >= exp:
                    firebase_cluster.force_kill_node(nid)
        except Exception as e:
            sys.stderr.write(f"[!] Session watchdog exception: {e}\n")
        time.sleep(60)

threading.Thread(target=subscription_and_session_watchdog, daemon=True).start()

# ==============================================================================
# SECTION 10: ROUTING & COMMAND HANDLERS
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start_command(message):
    chat_id = message.chat.id
    username = message.from_user.username or message.from_user.first_name
    text = message.text.strip()
    safe_delete_message(bot, chat_id, message.message_id)

    referred_by = None
    parts = text.split()
    if len(parts) > 1 and parts[1].isdigit():
        possible_ref = int(parts[1])
        if possible_ref != chat_id:
            referred_by = possible_ref

    db.register_user_if_absent(chat_id, username, referred_by)

    if not is_user_channel_member(chat_id):
        lines = [
            "You must join our official channel to",
            "activate automation tools.",
            f"Channel: {CHANNEL_URL}"
        ]
        card = format_ascii_box(to_bold("ACCESS VERIFICATION"), lines)
        bot.send_message(
            chat_id,
            f"<pre>{card}</pre>",
            reply_markup=get_channel_gateway_keyboard()
        )
        return

    db.mark_channel_joined(chat_id)
    welcome_lines = [
        "Distributed Automation Terminal Controller",
        "Select an operation below to proceed."
    ]
    card = format_ascii_box(to_bold("CLUSTER CORE ACTIVE"), welcome_lines)
    bot.send_message(
        chat_id,
        f"<pre>{card}</pre>",
        reply_markup=get_main_persistent_keyboard()
    )

@bot.message_handler(commands=['mode'])
def handle_mode_command(message):
    chat_id = message.chat.id
    safe_delete_message(bot, chat_id, message.message_id)
    cur_mode = db.get_global_mode()
    lines = [
        f"OPERATIONAL MODE : {cur_mode}",
        "Security Engine  : STRICT",
        "Nodes Sync       : ONLINE"
    ]
    card = format_ascii_box(to_bold("SYSTEM CONFIGURATION"), lines)
    bot.send_message(chat_id, f"<pre>{card}</pre>")

@bot.message_handler(commands=['paid'])
def handle_set_paid_mode(message):
    chat_id = message.chat.id
    safe_delete_message(bot, chat_id, message.message_id)
    if chat_id != OWNER_ID:
        return
    db.set_global_mode("PAID_MODE")
    lines = [
        "GLOBAL MODE SWITCHED TO: PAID_MODE",
        "Requirement: 24H Sub or 10 Referrals"
    ]
    card = format_ascii_box(to_bold("MODE ALTERATION"), lines)
    bot.send_message(chat_id, f"<pre>{card}</pre>")

@bot.message_handler(commands=['free'])
def handle_set_free_mode(message):
    chat_id = message.chat.id
    safe_delete_message(bot, chat_id, message.message_id)
    if chat_id != OWNER_ID:
        return
    db.set_global_mode("FREE_MODE")
    lines = [
        "GLOBAL MODE SWITCHED TO: FREE_MODE",
        "Requirement: 5 Referrals"
    ]
    card = format_ascii_box(to_bold("MODE ALTERATION"), lines)
    bot.send_message(chat_id, f"<pre>{card}</pre>")

@bot.message_handler(commands=['admin'])
def handle_admin_telemetry(message):
    chat_id = message.chat.id
    safe_delete_message(bot, chat_id, message.message_id)
    if chat_id != OWNER_ID:
        return

    nodes = firebase_cluster.fetch_all_nodes()
    tot = len(nodes)
    free_c = sum(1 for n in nodes.values() if n.get("status", "FREE").upper() == "FREE")
    busy_c = sum(1 for n in nodes.values() if n.get("status").upper() == "BUSY")
    off_c = tot - (free_c + busy_c)

    mode = db.get_global_mode()
    lines = [
        f"GLOBAL STATUS    : {mode}",
        f"TOTAL TERMINALS  : {tot}",
        f"FREE NODES       : {free_c}",
        f"BUSY NODES       : {busy_c}",
        f"OFFLINE NODES    : {off_c}"
    ]
    card = format_ascii_box(to_bold("TELEMETRY CONTROL REPORT"), lines)
    bot.send_message(chat_id, f"<pre>{card}</pre>")

@bot.message_handler(commands=['kick'])
def handle_remote_kick(message):
    chat_id = message.chat.id
    safe_delete_message(bot, chat_id, message.message_id)
    if chat_id != OWNER_ID:
        return

    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.send_message(chat_id, "Usage: /kick <node_id>")
        return

    target_node = parts[1]
    ok = firebase_cluster.force_kill_node(target_node)
    lines = [
        f"TARGET NODE      : {target_node}",
        f"FORCE KILL STATE : {'DISPATCHED' if ok else 'FAILED'}"
    ]
    card = format_ascii_box(to_bold("TERMINAL OVERRIDE"), lines)
    bot.send_message(chat_id, f"<pre>{card}</pre>")

# ==============================================================================
# SECTION 11: TEXT & PERSISTENT BUTTONS DISPATCHER
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_all_text_inputs(message):
    chat_id = message.chat.id
    text = message.text.strip()
    safe_delete_message(bot, chat_id, message.message_id)

    if not is_user_channel_member(chat_id):
        lines = [
            "You must join our official channel to",
            "activate automation tools.",
            f"Channel: {CHANNEL_URL}"
        ]
        card = format_ascii_box(to_bold("ACCESS VERIFICATION"), lines)
        bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_channel_gateway_keyboard())
        return

    db.mark_channel_joined(chat_id)

    # 1. Persistent Button: NEW TASK
    if text == to_bold("NEW TASK") or text.upper() == "NEW TASK":
        nodes = firebase_cluster.fetch_all_nodes()
        total_nodes = len(nodes)
        free_nodes = sum(1 for n in nodes.values() if n.get("status", "FREE").upper() == "FREE")
        busy_nodes = sum(1 for n in nodes.values() if n.get("status").upper() == "BUSY")

        inv_lines = [
            f"TOTAL DEVICES     : {total_nodes}",
            f"FREE TERMINALS    : {free_nodes}",
            f"OCCUPIED NODES    : {busy_nodes}",
            "━" * 38,
            f"{'Terminal ID'.ljust(15)} │ {'Status'.ljust(8)} │ {'Mode'}"
        ]
        for nid, ndata in list(nodes.items())[:15]:
            nst = ndata.get("status", "FREE").upper().ljust(8)
            nmod = "24H_LOCK" if "BUSY" in nst else "READY"
            inv_lines.append(f"{nid.ljust(15)} │ {nst} │ {nmod}")

        card = format_ascii_box(to_bold("CLUSTER TERMINAL INVENTORY"), inv_lines)
        bot.send_message(chat_id, f"<pre>{card}</pre>")
        return

    # 2. Persistent Button: REFERRAL
    if text == to_bold("REFERRAL") or text.upper() == "REFERRAL":
        u = db.get_user(chat_id)
        if not u:
            return
        bot_uname = bot.get_me().username
        inv_link = f"https://t.me/{bot_uname}?start={chat_id}"
        mode = db.get_global_mode()
        quota = FREE_MODE_REFERRAL_QUOTA if mode == "FREE_MODE" else PAID_MODE_REFERRAL_QUOTA

        lines = [
            f"Your ID           : {chat_id}",
            f"Total Completed   : {u['total_referrals']}",
            f"Quota Required    : {quota}",
            f"Invite Link       : {inv_link}"
        ]
        card = format_ascii_box(to_bold("REFERRAL DASHBOARD"), lines)
        bot.send_message(chat_id, f"<pre>{card}</pre>")
        return

    # 3. Persistent Button: TASK
    if text == to_bold("TASK") or text.upper() == "TASK":
        u = db.get_user(chat_id)
        if not u:
            return

        mode = db.get_global_mode()
        has_access = False

        if mode == "FREE_MODE":
            if u["total_referrals"] >= FREE_MODE_REFERRAL_QUOTA:
                has_access = True
            else:
                bot_uname = bot.get_me().username
                inv_link = f"https://t.me/{bot_uname}?start={chat_id}"
                lines = [
                    f"Status            : {u['total_referrals']}/{FREE_MODE_REFERRAL_QUOTA} Referrals",
                    "Requirement       : 5 Valid Referrals",
                    f"Invite Link       : {inv_link}"
                ]
                card = format_ascii_box(to_bold("QUOTA DEFICIT"), lines)
                bot.send_message(chat_id, "দয়া করে আপনার রেফারটি কমপ্লিট করুন")
                bot.send_message(chat_id, f"<pre>{card}</pre>")
                return

        elif mode == "PAID_MODE":
            now = int(time.time())
            if u["paid_until"] > now or u["total_referrals"] >= PAID_MODE_REFERRAL_QUOTA:
                has_access = True
            else:
                bot_uname = bot.get_me().username
                inv_link = f"https://t.me/{bot_uname}?start={chat_id}"
                lines = [
                    f"24H Premium Rate  : ৳ {SUBSCRIPTION_PRICE_BDT:.2f} BDT",
                    f"bKash Personal    : {BKASH_NUMBER}",
                    f"Nagad Personal    : {NAGAD_NUMBER}",
                    "━" * 38,
                    f"Free Alternative  : {PAID_MODE_REFERRAL_QUOTA} Referrals",
                    f"Current Referrals : {u['total_referrals']}/{PAID_MODE_REFERRAL_QUOTA}",
                    f"Invite Link       : {inv_link}"
                ]
                card = format_ascii_box(to_bold("SUBSCRIPTION REQUIRED"), lines)
                bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_payment_submission_keyboard())
                return

        if has_access:
            active = db.get_active_session_by_user(chat_id)
            if active:
                lines = [
                    f"Session ID        : {active['session_id']}",
                    f"Terminal Node     : {active['node_id']}",
                    f"Expires At        : {datetime.fromtimestamp(active['end_time'], tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
                ]
                card = format_ascii_box(to_bold("ACTIVE SESSION IN PROGRESS"), lines)
                bot.send_message(chat_id, f"<pre>{card}</pre>")
                return

            node_id, ndata = firebase_cluster.acquire_free_node(chat_id)
            if not node_id:
                lines = [
                    "All worker terminals are occupied.",
                    "Please wait for an open device or check [ NEW TASK ]."
                ]
                card = format_ascii_box(to_bold("QUEUE EXHAUSTED"), lines)
                bot.send_message(chat_id, f"<pre>{card}</pre>")
                return

            sid = f"SESS_{chat_id}_{int(time.time()) % 100000}"
            db.create_session(sid, chat_id, node_id, duration_sec=86400)

            user_input_states[chat_id] = {
                "node_id": node_id,
                "session_id": sid,
                "site": "AMAR",
                "phone": None,
                "password": None,
                "target": 0.0,
                "steps": 7,
                "mode_input": None
            }

            lines = [
                f"Terminal Node     : {node_id}",
                f"Session ID        : {sid}",
                "Select trading portal:"
            ]
            card = format_ascii_box(to_bold("TERMINAL ALLOCATED"), lines)
            bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_platform_selection_keyboard(node_id))
            return

    # Handle Input Modes for Active Flow
    state = user_input_states.get(chat_id)
    if state and state.get("mode_input"):
        mode_in = state["mode_input"]
        node_id = state["node_id"]

        if mode_in == "WAIT_PHONE":
            state["phone"] = text
            state["mode_input"] = None
            lines = [
                f"Terminal Node     : {node_id}",
                f"Account Number    : {text[:3]}****{text[-3:] if len(text)>=6 else text}",
                "Provide password below:"
            ]
            card = format_ascii_box(to_bold("CREDENTIAL REGISTERED"), lines)
            bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_credentials_input_keyboard(node_id, True))
            return

        elif mode_in == "WAIT_PASSWORD":
            state["password"] = text
            state["mode_input"] = None
            lines = [
                f"Terminal Node     : {node_id}",
                "Credentials Set   : COMPLETE",
                "Configure trade parameters:"
            ]
            card = format_ascii_box(to_bold("SECURITY VALIDATED"), lines)
            bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_parameters_setup_keyboard(node_id, state["target"], state["steps"]))
            return

        elif mode_in == "WAIT_TARGET":
            try:
                val = float(text)
                if val <= 0: raise ValueError()
                state["target"] = val
                state["mode_input"] = None
                lines = [
                    f"Terminal Node     : {node_id}",
                    f"Target Profit     : ৳ {val:.2f}",
                    f"Martingale Steps  : {state['steps']}"
                ]
                card = format_ascii_box(to_bold("PARAMETERS UPDATED"), lines)
                bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_parameters_setup_keyboard(node_id, state["target"], state["steps"]))
            except ValueError:
                bot.send_message(chat_id, "Enter valid positive number for Target Profit:")
            return

        elif mode_in == "WAIT_STEPS":
            try:
                val = int(text)
                if val <= 0: raise ValueError()
                state["steps"] = val
                state["mode_input"] = None
                lines = [
                    f"Terminal Node     : {node_id}",
                    f"Target Profit     : ৳ {state['target']:.2f}",
                    f"Martingale Steps  : {val}"
                ]
                card = format_ascii_box(to_bold("PARAMETERS UPDATED"), lines)
                bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_parameters_setup_keyboard(node_id, state["target"], state["steps"]))
            except ValueError:
                bot.send_message(chat_id, "Enter valid positive integer for Steps:")
            return

        elif mode_in.startswith("WAIT_TRX:"):
            method = mode_in.split(":")[1]
            trx_id = text.strip()
            state["mode_input"] = None
            db.add_payment_record(trx_id, chat_id, method, SUBSCRIPTION_PRICE_BDT)

            lines = [
                f"Transaction ID    : {trx_id}",
                f"Payment Method    : {method}",
                f"Amount            : ৳ {SUBSCRIPTION_PRICE_BDT:.2f}",
                "Status            : PENDING VERIFICATION"
            ]
            card = format_ascii_box(to_bold("PAYMENT SUBMITTED"), lines)
            bot.send_message(chat_id, f"<pre>{card}</pre>")

            admin_lines = [
                f"User Chat ID      : {chat_id}",
                f"Method            : {method}",
                f"Amount            : ৳ {SUBSCRIPTION_PRICE_BDT:.2f}",
                f"TrxID             : {trx_id}"
            ]
            admin_card = format_ascii_box(to_bold("INCOMING PAYMENT AUDIT"), admin_lines)
            bot.send_message(OWNER_ID, f"<pre>{admin_card}</pre>", reply_markup=get_admin_approval_keyboard(trx_id))
            return

# ==============================================================================
# SECTION 12: CALLBACK QUERIES ROUTING ENGINE
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_all_callback_queries(call):
    chat_id = call.message.chat.id
    data = call.data

    if data == "action_verify_channel":
        if is_user_channel_member(chat_id):
            db.mark_channel_joined(chat_id)
            bot.answer_callback_query(call.id, "Verification complete!")
            safe_delete_message(bot, chat_id, call.message.message_id)
            welcome_lines = [
                "Distributed Automation Terminal Controller",
                "Select an operation below to proceed."
            ]
            card = format_ascii_box(to_bold("CLUSTER CORE ACTIVE"), welcome_lines)
            bot.send_message(chat_id, f"<pre>{card}</pre>", reply_markup=get_main_persistent_keyboard())
        else:
            bot.answer_callback_query(call.id, "You have not joined the channel yet.", show_alert=True)
        return

    # Site Selection
    if data.startswith("cfg_site:"):
        parts = data.split(":")
        site = parts[1]
        node_id = parts[2]
        state = user_input_states.setdefault(chat_id, {})
        state["site"] = site
        state["node_id"] = node_id
        bot.answer_callback_query(call.id)
        lines = [
            f"Terminal Node     : {node_id}",
            f"Target Platform   : {site}",
            "Provide authentication credentials:"
        ]
        card = format_ascii_box(to_bold("CREDENTIAL GATEWAY"), lines)
        bot.edit_message_text(f"<pre>{card}</pre>", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_credentials_input_keyboard(node_id, False))
        return

    # Abort Allocation
    if data.startswith("cfg_abort:"):
        node_id = data.split(":")[1]
        firebase_cluster.release_node(node_id)
        state = user_input_states.pop(chat_id, None)
        if state and state.get("session_id"):
            db.terminate_session(state["session_id"])
        bot.answer_callback_query(call.id, "Allocation aborted.")
        safe_delete_message(bot, chat_id, call.message.message_id)
        return

    # Credential Inputs
    if data.startswith("in_num:"):
        node_id = data.split(":")[1]
        user_input_states.setdefault(chat_id, {})["mode_input"] = "WAIT_PHONE"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Enter your account phone number:")
        return

    if data.startswith("in_pwd:"):
        node_id = data.split(":")[1]
        state = user_input_states.get(chat_id, {})
        if not state.get("phone"):
            bot.answer_callback_query(call.id, "Provide account number first!", show_alert=True)
            return
        state["mode_input"] = "WAIT_PASSWORD"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Enter your account password:")
        return

    if data.startswith("in_tgt:"):
        node_id = data.split(":")[1]
        user_input_states.setdefault(chat_id, {})["mode_input"] = "WAIT_TARGET"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Enter Target Profit Amount (e.g. 500):")
        return

    if data.startswith("in_stp:"):
        node_id = data.split(":")[1]
        user_input_states.setdefault(chat_id, {})["mode_input"] = "WAIT_STEPS"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Enter Martingale Steps (e.g. 7):")
        return

    # Dispatch to Remote Node
    if data.startswith("in_go:"):
        node_id = data.split(":")[1]
        state = user_input_states.get(chat_id)
        if not state or not state.get("phone") or not state.get("password"):
            bot.answer_callback_query(call.id, "Phone and Password are required!", show_alert=True)
            return
        if not state.get("target") or state["target"] <= 0:
            bot.answer_callback_query(call.id, "Valid Target Profit is required!", show_alert=True)
            return

        target_url = URL_AMARCLUB_LOGIN if state["site"] == "AMAR" else URL_DKWIN_LOGIN
        wingo_url = URL_AMARCLUB_WINGO if state["site"] == "AMAR" else URL_DKWIN_WINGO

        task_payload = {
            "session_id": state["session_id"],
            "target_url": target_url,
            "wingo_url": wingo_url,
            "phone": state["phone"],
            "password": state["password"],
            "target_profit": state["target"],
            "total_steps": state["steps"],
            "scripts": {
                "AUTO_FILL_AND_CLICK_JS": AUTO_FILL_AND_CLICK_JS,
                "CHECK_LOGIN_STATUS_JS": CHECK_LOGIN_STATUS_JS,
                "WINGO_RUNBOX_AND_CLICK_JS": WINGO_RUNBOX_AND_CLICK_JS,
                "CHECK_WINGO_READY_JS": CHECK_WINGO_READY_JS,
                "FETCH_BALANCE_JS": FETCH_BALANCE_JS,
                "WINGO_CORE_JS": WINGO_CORE_JS
            }
        }

        ok = firebase_cluster.dispatch_task(node_id, task_payload)
        bot.answer_callback_query(call.id)
        safe_delete_message(bot, chat_id, call.message.message_id)

        lines = [
            f"Terminal Node     : {node_id}",
            f"Target Portal     : {state['site']}",
            f"Target Profit     : ৳ {state['target']:.2f}",
            f"Martingale Steps  : {state['steps']}",
            f"Cluster Dispatch  : {'SUCCESS' if ok else 'FAILED'}",
            "Terminal active in 24/7 background mode."
        ]
        card = format_ascii_box(to_bold("TASK DISPATCHED TO WORKER"), lines)
        bot.send_message(chat_id, f"<pre>{card}</pre>")
        user_input_states.pop(chat_id, None)
        return

    # Payment Submission Selection
    if data.startswith("pay_submit:"):
        method = data.split(":")[1]
        user_input_states.setdefault(chat_id, {})["mode_input"] = f"WAIT_TRX:{method}"
        bot.answer_callback_query(call.id)
        acc_num = BKASH_NUMBER if method == "BKASH" else NAGAD_NUMBER
        lines = [
            f"Method            : {method}",
            f"Personal Number   : {acc_num}",
            f"Amount Required   : ৳ {SUBSCRIPTION_PRICE_BDT:.2f}",
            "Send money and reply with your TrxID below:"
        ]
        card = format_ascii_box(to_bold("TRANSACTION INSTRUCTIONS"), lines)
        bot.send_message(chat_id, f"<pre>{card}</pre>")
        return

    # Admin Audit Actions
    if data.startswith("adm_app:"):
        if chat_id != OWNER_ID: return
        trx_id = data.split(":")[1]
        db.update_payment_status(trx_id, "APPROVED")
        bot.answer_callback_query(call.id, "Approved!")
        bot.edit_message_text(f"Transaction {trx_id} has been APPROVED for 24H.", chat_id=chat_id, message_id=call.message.message_id)
        return

    if data.startswith("adm_rej:"):
        if chat_id != OWNER_ID: return
        trx_id = data.split(":")[1]
        db.update_payment_status(trx_id, "REJECTED")
        bot.answer_callback_query(call.id, "Rejected!")
        bot.edit_message_text(f"Transaction {trx_id} has been REJECTED.", chat_id=chat_id, message_id=call.message.message_id)
        return

# ==============================================================================
# SECTION 13: PRODUCTION BOOT SEQUENCE
# ==============================================================================
def main():
    boot_lines = [
        "Distributed Master Cluster Orchestrator",
        "SQLite Thread-Safe Storage Engine : INITIALIZED",
        "Firebase Cluster Synchronizer    : CONNECTED",
        "Lifetime Watchdog Daemon         : RUNNING",
        "Bot Polling State                : DISPATCHING"
    ]
    sys.stdout.write(format_ascii_box(to_bold("SYSTEM BOOT ENGINE"), boot_lines) + "\n")
    sys.stdout.flush()

    try:
        bot.remove_webhook()
    except Exception:
        pass

    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    main()
