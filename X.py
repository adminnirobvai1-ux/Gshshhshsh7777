import os
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# আপনার নতুন টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

# সাইট লিংক
URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

# ফায়ারফক্স প্রোফাইল পাথ (VPN চালু রাখার জন্য জরুরি)
# ফায়ারফক্সের অ্যাড্রেস বারে about:profiles লিখে পাথটি সংগ্রহ করে এখানে বসান
FIREFOX_PROFILE_PATH = "/home/username/.mozilla/firefox/xxxxxxxx.default-release"

# স্বয়ংক্রিয়ভাবে N, P বসিয়ে L এ ক্লিক করার জাভাস্ক্রিপ্ট কোড
AUTO_PLAY_JS = """
(function autoFillAndClick() {
  const setVal = (el, val) => {
    el.focus();
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(el, val);
    else el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const selN = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input';
  const selP = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input';
  const selL = 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button';

  let attempts = 0;
  // পেজের ইনপুট লোড হওয়া পর্যন্ত প্রতি ৫০০ মিলি-সেকেন্ড পর পর চেক করবে
  const timer = setInterval(() => {
    attempts++;
    const elN = document.querySelector(selN);
    const elP = document.querySelector(selP);
    const elL = document.querySelector(selL);

    if (elN && elP && elL) {
      clearInterval(timer);

      // ১. N ইনপুট বসানো
      setVal(elN, '1876685711');

      // ২. ৪০০ মিলি-সেকেন্ড পর P ইনপুট বসানো
      setTimeout(() => {
        setVal(elP, 'NAYYYY');

        // ৩. আরও ৪০০ মিলি-সেকেন্ড পর L বাটনে ক্লিক
        setTimeout(() => {
          elL.click();
        }, 400);
      }, 400);

    } else if (attempts > 40) { // ২০ সেকেন্ডের মধ্যে না পেলে থামবে
      clearInterval(timer);
      console.log('Login selectors not found.');
    }
  }, 500);
})();
"""

def launch_browser_and_automate(url):
    """ব্রাউজার ওপেন এবং স্বয়ংক্রিয় জাভাস্ক্রিপ্ট রান করার ফাংশন"""
    if "DISPLAY" not in os.environ:
        os.environ["DISPLAY"] = ":0"

    options = Options()
    if os.path.exists(FIREFOX_PROFILE_PATH):
        options.add_argument("-profile")
        options.add_argument(FIREFOX_PROFILE_PATH)

    try:
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()
        driver.get(url)

        # প্রাথমিক পেজ লোড হওয়ার জন্য কিছুটা সময়
        time.sleep(3)

        # জাভাস্ক্রিপ্ট অটোমেশন রান করা
        driver.execute_script(AUTO_PLAY_JS)

    except Exception as e:
        print(f"Error during automation: {e}")

# /start হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Amarclub1", callback_data="btn_amarclub"),
        InlineKeyboardButton("Dkwin6", callback_data="btn_dkwin")
    )
    bot.send_message(
        message.chat.id, 
        "ডেক্সটপে সাইট ওপেন এবং অটো-লগইন করতে নির্বাচন করুন:", 
        reply_markup=markup
    )

# বাটন অ্যাকশন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    target_url = None
    site_name = ""

    if call.data == "btn_amarclub":
        target_url = URL_AMARCLUB
        site_name = "Amarclub1"
    elif call.data == "btn_dkwin":
        target_url = URL_DKWIN
        site_name = "Dkwin6"

    if target_url:
        bot.answer_callback_query(call.id, f"{site_name} প্রসেস শুরু হয়েছে")
        bot.send_message(call.message.chat.id, f"{site_name} ওপেন হচ্ছে এবং অটোমেশন কার্যকর হচ্ছে...")

        # ব্যাকগ্রাউন্ড থ্রেডে অটোমেশন চালানো
        threading.Thread(target=launch_browser_and_automate, args=(target_url,), daemon=True).start()

if __name__ == "__main__":
    print("বট নতুন টোকেন সহ সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
