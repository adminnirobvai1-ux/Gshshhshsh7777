import os
import subprocess
import threading
import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# টেলিগ্রাম বট টোকেন
TOKEN = "8955426078:AAFyefL1ul-qt6HtYhFOhuQVIW4_k47R7Pw"
bot = telebot.TeleBot(TOKEN)

# সাইট লিংক
URL_AMARCLUB = "https://amarclub1.com"
URL_DKWIN = "https://dkwin6.com/#/login"

# সম্পূর্ণ জাভাস্ক্রিপ্ট কোড (১ সেকেন্ড পর পর N -> P -> L অটো-প্লে হবে)
JS_CODE = """
(function(){
  if(document.getElementById('_run_box')) return;

  const setVal = (el, val) => {
    el.focus();
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(el, val);
    else el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const d = [
    { name: 'N', sel: 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input', val: '1876685711' },
    { name: 'P', sel: 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input', val: 'NAYYYY' },
    { name: 'L', sel: 'body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button' }
  ];

  const exec = (x, showAlert) => {
    const el = document.querySelector(x.sel);
    if (!el) {
      if (showAlert) alert(x.name + ' not found');
      return;
    }
    if (x.val !== undefined) setVal(el, x.val);
    else el.click();
  };

  // ১ সেকেন্ড ব্যবধানে N -> P -> L অটো-রান করার ফাংশন
  const runSequence = () => {
    // ১. N বসানো
    exec(d[0], false);

    // ২. ১ সেকেন্ড পর P বসানো
    setTimeout(() => {
      exec(d[1], false);

      // ৩. আরও ১ সেকেন্ড পর L বাটনে ক্লিক
      setTimeout(() => {
        exec(d[2], false);
      }, 1000);
    }, 1000);
  };

  // স্ক্রিনের নিচের কন্ট্রোল বক্স
  const b = document.createElement('div');
  b.id = '_run_box';
  b.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#18181b;padding:6px 10px;border-radius:30px;display:flex;gap:6px;align-items:center;z-index:99999999;box-shadow:0 6px 16px rgba(0,0,0,0.3);font:12px sans-serif;';

  const all = document.createElement('button');
  all.innerText = '▶ All';
  all.style.cssText = 'background:#f59e0b;color:#000;border:none;padding:4px 8px;border-radius:20px;cursor:pointer;font-weight:bold;font-size:11px;';
  all.onclick = runSequence;
  b.appendChild(all);

  d.forEach(x => {
    const btn = document.createElement('button');
    btn.innerText = x.name;
    btn.style.cssText = 'background:#22c55e;color:#000;border:none;padding:4px 8px;border-radius:20px;cursor:pointer;font-weight:bold;font-size:11px;';
    btn.onclick = () => exec(x, true);
    b.appendChild(btn);
  });

  const close = document.createElement('span');
  close.innerText = '✕';
  close.style.cssText = 'cursor:pointer;color:#a1a1aa;margin-left:4px;font-weight:bold;';
  close.onclick = () => b.remove();
  b.appendChild(close);

  document.body.appendChild(b);

  // ইনপুট ফিল্ড ও বাটন সম্পূর্ণ লোড হওয়া যাচাই এবং ১ সেকেন্ড পর অটো প্লে
  let attempts = 0;
  const timer = setInterval(() => {
    attempts++;
    const readyN = document.querySelector(d[0].sel);
    const readyP = document.querySelector(d[1].sel);
    const readyL = document.querySelector(d[2].sel);

    if (readyN && readyP && readyL) {
      clearInterval(timer);
      // সাইট সম্পূর্ণ দৃশ্যমান হওয়ার ঠিক ১ সেকেন্ড পর প্লে শুরু হবে
      setTimeout(() => {
        runSequence();
      }, 1000);
    } else if (attempts > 60) {
      clearInterval(timer);
    }
  }, 400);

})();
"""

def open_firefox(url):
    """অনলাইন ডেক্সটপের ডিসপ্লেতে ফায়ারফক্স ওপেন করার মূল ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"
    try:
        subprocess.Popen(["firefox", "--new-tab", url], env=env)
        return True
    except Exception as e:
        print(f"Error opening Firefox: {e}")
        return False

def inject_and_run_javascript():
    """ফায়ারফক্স ওপেন হওয়ার পর ব্রাউজারের ভেতর কোড ইনজেক্ট করার ফাংশন"""
    env = os.environ.copy()
    if "DISPLAY" not in env:
        env["DISPLAY"] = ":0"

    # নতুন ট্যাব খোলা ও ভিপিএন কানেকশন নেওয়ার জন্য ৪ সেকেন্ড বিরতি
    time.sleep(4)

    try:
        # জাভাস্ক্রিপ্ট কোড ক্লিপবোর্ডে কপি করা
        clip_proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, env=env)
        clip_proc.communicate(input=JS_CODE.encode("utf-8"))

        # ফায়ারফক্স উইন্ডো সামনে ফোকাস করা
        subprocess.run(["xdotool", "search", "--onlyvisible", "--class", "firefox", "windowactivate"], env=env)
        time.sleep(0.5)

        # ডেভেলপার কনসোল খোলা (Ctrl + Shift + K)
        subprocess.run(["xdotool", "key", "ctrl+shift+k"], env=env)
        time.sleep(0.8)

        # ফায়ারফক্সের পেস্ট ব্লকার অতিক্রমের কমান্ড
        subprocess.run(["xdotool", "type", "--delay", "5", "allow pasting"], env=env)
        subprocess.run(["xdotool", "key", "Return"], env=env)
        time.sleep(0.3)

        # কোড পেস্ট করে রান করা
        subprocess.run(["xdotool", "key", "ctrl+v"], env=env)
        time.sleep(0.3)
        subprocess.run(["xdotool", "key", "Return"], env=env)
        time.sleep(0.5)

        # কনসোল উইন্ডো বন্ধ করা
        subprocess.run(["xdotool", "key", "ctrl+shift+k"], env=env)
        print("জাভাস্ক্রিপ্ট সেশন স্বয়ংক্রিয়ভাবে চালু হয়েছে।")

    except Exception as e:
        print(f"Injection error: {e}")

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
    target_url = None
    site_name = ""

    if call.data == "btn_amarclub":
        target_url = URL_AMARCLUB
        site_name = "Amarclub1"
    elif call.data == "btn_dkwin":
        target_url = URL_DKWIN
        site_name = "Dkwin6"

    if target_url:
        if open_firefox(target_url):
            bot.answer_callback_query(call.id, f"{site_name} ওপেন করা হয়েছে!")
            bot.send_message(call.message.chat.id, f"{site_name} ওপেন হয়েছে এবং অটোমেশন কার্যকর হচ্ছে...")

            # ব্যাকগ্রাউন্ডে পাইথন স্বয়ংক্রিয়ভাবে জাভাস্ক্রিপ্ট ইনজেক্ট করবে
            threading.Thread(target=inject_and_run_javascript, daemon=True).start()
        else:
            bot.answer_callback_query(call.id, "ফায়ারফক্স চালু করা সম্ভব হয়নি।")

if __name__ == "__main__":
    print("বট সফলভাবে চালু হয়েছে...")
    bot.infinity_polling()
