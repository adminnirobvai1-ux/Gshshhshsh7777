import os
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

# সাইট লিংক
URL_AMARCLUB = "https://amarclub1.com/#/login"
URL_DKWIN = "https://dkwin6.com/#/login"

# জাভাস্ক্রিপ্ট বুকমার্কলেট থেকে পাওয়া সিলেক্টর
SEL_N = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input"
SEL_P = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input"
SEL_L = "body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button"

# ইউজারের ডাটা এবং ব্রাউজার সেশন ট্র্যাক করার ডিকশনারি
user_sessions = {}

def get_firefox_driver():
    """VPS ডেস্কটপ স্ক্রিনে ফায়ারফক্স রান করার ড্রাইভার"""
    os.environ["DISPLAY"] = ":0"  # ভার্চুয়াল ডেস্কটপের ডিসপ্লে
    options = Options()
    # options.add_argument("--headless") # ব্যাকগ্রাউন্ডে চালাতে চাইলে আনকমেন্ট করুন
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()
    return driver

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
        "ডেস্কটপে সাইট ওপেন করতে নিচের বাটনে ক্লিক করুন:", 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    target_url = URL_AMARCLUB if call.data == "btn_amarclub" else URL_DKWIN
    site_name = "Amarclub1" if call.data == "btn_amarclub" else "Dkwin6"

    bot.answer_callback_query(call.id, f"{site_name} ওপেন করা হচ্ছে...")
    msg = bot.send_message(chat_id, f"ব্রাউজারে {site_name} লোড হচ্ছে, অনুগ্রহ করে অপেক্ষা করুন...")

    try:
        driver = get_firefox_driver()
        driver.get(target_url)
        
        # সেশন সেভ রাখা
        user_sessions[chat_id] = {
            "driver": driver,
            "url": target_url
        }
        
        time.sleep(2) # এনিমেশন ও লোডিংয়ের জন্য বিরতি
        bot.edit_message_text(f"{site_name} সফলভাবে ওপেন হয়েছে।", chat_id, msg.message_id)
        
        # নাম্বার চাওয়ার প্রম্পট
        next_msg = bot.send_message(chat_id, "লগইনের জন্য **নাম্বার (N)** প্রবেশ করান:")
        bot.register_next_step_handler(next_msg, process_number_step)

    except Exception as e:
        bot.send_message(chat_id, f"ব্রাউজার ওপেন করতে সমস্যা হয়েছে: {str(e)}")

def process_number_step(message):
    chat_id = message.chat.id
    number = message.text.strip()

    if chat_id not in user_sessions:
        bot.send_message(chat_id, "সেশন পাওয়া যায়নি। অনুগ্রহ করে আবার /start দিন।")
        return

    user_sessions[chat_id]["number"] = number

    next_msg = bot.send_message(chat_id, "এবার **পাসওয়ার্ড (P)** প্রবেশ করান:")
    bot.register_next_step_handler(next_msg, process_password_step)

def process_password_step(message):
    chat_id = message.chat.id
    password = message.text.strip()

    if chat_id not in user_sessions:
        bot.send_message(chat_id, "সেশন পাওয়া যায়নি। অনুগ্রহ করে আবার /start দিন।")
        return

    session = user_sessions[chat_id]
    driver = session["driver"]
    number = session["number"]

    bot.send_message(chat_id, "তথ্য পাওয়া গেছে। সাইটে অটোমেশন শুরু হচ্ছে...")

    try:
        # ইনপুট ফিল্ড লোড হওয়া পর্যন্ত সর্বোচ্চ ২০ সেকেন্ড অপেক্ষা
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, SEL_N)))

        # জাভাস্ক্রিপ্ট ইভেন্ট ট্রিগার করে নাম্বার ও পাসওয়ার্ড বসানো এবং বাটনে ক্লিক
        js_script = """
            let n_input = document.querySelector(arguments[0]);
            let p_input = document.querySelector(arguments[1]);
            let l_btn = document.querySelector(arguments[2]);

            if (n_input && p_input && l_btn) {
                // নাম্বার বসানো
                n_input.focus();
                n_input.value = arguments[3];
                n_input.dispatchEvent(new Event('input', { bubbles: true }));
                n_input.dispatchEvent(new Event('change', { bubbles: true }));

                // পাসওয়ার্ড বসানো
                p_input.focus();
                p_input.value = arguments[4];
                p_input.dispatchEvent(new Event('input', { bubbles: true }));
                p_input.dispatchEvent(new Event('change', { bubbles: true }));

                // লগইন বাটনে ক্লিক
                setTimeout(() => {
                    l_btn.click();
                }, 500);

                return { status: true };
            } else {
                return { status: false, msg: "উপাদান পাওয়া যায়নি।" };
            }
        """

        res = driver.execute_script(js_script, SEL_N, SEL_P, SEL_L, number, password)

        if res.get("status"):
            bot.send_message(chat_id, "সফলভাবে নাম্বার ও পাসওয়ার্ড বসিয়ে লগইন বাটনে ক্লিক করা হয়েছে!")
        else:
            bot.send_message(chat_id, f"ইনপুট ফিল্ডে বসানো সম্ভব হয়নি: {res.get('msg')}")

    except Exception as e:
        bot.send_message(chat_id, f"অটোমেশনে সমস্যা দেখা দিয়েছে: {str(e)}")

if __name__ == "__main__":
    print("টেলিগ্রাম অটোমেশন বট চালু হয়েছে...")
    bot.infinity_polling()
