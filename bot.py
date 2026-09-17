import os
import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# আপনার টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFpjgYEYHDyNJ2dJhqZ5S4e4qzINulz5js"
bot = telebot.TeleBot(TOKEN)

# ওয়েবসাইটের লিংক
URL_AMARCLUB = "https://amarclub1.com"
URL_DKWIN = "https://dkwin6.com"

def open_firefox(url):
    """অনলাইন ডেক্সটপের ডিসপ্লেতে ফায়ারফক্স ওপেন করার ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"  # ভার্চুয়াল ডেক্সটপের ডিফল্ট ডিসপ্লে স্ক্রিন
    try:
        subprocess.Popen(["firefox", "--new-tab", url], env=env)
        return True
    except Exception as e:
        print(f"Error opening Firefox: {e}")
        return False

# /start কমান্ড হ্যান্ডলার
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
        "ডেক্সটপে সাইট ওপেন করতে নিচের বাটনে ক্লিক করুন:", 
        reply_markup=markup
    )

# বাটন ক্লিক ইভেন্ট হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "btn_amarclub":
        if open_firefox(URL_AMARCLUB):
            bot.answer_callback_query(call.id, "Amarclub1 ওপেন করা হয়েছে!")
            bot.send_message(call.message.chat.id, "Amarclub1.com ডেক্সটপে ওপেন হয়েছে।")
        else:
            bot.answer_callback_query(call.id, "ফায়ারফক্স চালু করা সম্ভব হয়নি।")

    elif call.data == "btn_dkwin":
        if open_firefox(URL_DKWIN):
            bot.answer_callback_query(call.id, "Dkwin6 ওপেন করা হয়েছে!")
            bot.send_message(call.message.chat.id, "Dkwin6.com ডেক্সটপে ওপেন হয়েছে।")
        else:
            bot.answer_callback_query(call.id, "ফায়ারফক্স চালু করা সম্ভব হয়নি।")

if __name__ == "__main__":
    print("বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
