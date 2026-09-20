"""
Telegram Bot Handlers & UI Interaction Module
চ্যানেল লক, ভাষা নির্বাচন, প্রাইস লিস্ট, পেমেন্ট গেটওয়ে, ওনার অনুমোদন ও অটোমেশন কন্ট্রোল
"""
import os
import time
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from config import BOT_TOKEN, OWNER_CHAT_ID, CHANNELS, PRICING_PLANS, PAYMENT_METHODS, PLATFORMS, PROFILES_DIR
from database import db
from automation_engine import (
    active_sessions,
    session_lock,
    to_bold,
    allocate_session_tab,
    close_session_tab,
    register_session,
    get_session
)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

user_states = {}
SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

def safe_delete_message(chat_id, message_id):
    if not message_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ==========================================
# ১. /start এবং চ্যানেল লক হ্যান্ডলার
# ==========================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    safe_delete_message(chat_id, message.message_id)

    user_states[chat_id] = {"step": "LOCKED_CHANNELS", "user_id": user_id}

    lock_msg = (
        "<b>আসসালামু আলাইকুম।</b>\n\n"
        "আমাদের <b>WinGo VIP অটোমেশন বটে</b> আপনাকে স্বাগতম!\n\n"
        "বটটি ব্যবহার শুরু করার আগে দয়া করে আমাদের অফিশিয়াল দুটি টেলিগ্রাম চ্যানেলে জয়েন করুন।\n"
        "নিচের বাটনে ক্লিক করে জয়েন হয়ে <b>'জয়েন সম্পন্ন করেছি'</b> বাটনে চাপ দিন:"
    )

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("১. DARK 67 HACK চ্যানেলে জয়েন করুন", url=CHANNELS[0]["url"]),
        InlineKeyboardButton("২. BD WIN 24 চ্যানেলে জয়েন করুন", url=CHANNELS[1]["url"]),
        InlineKeyboardButton("জয়েন সম্পন্ন করেছি (Continue)", callback_data="channels_joined")
    )

    bot.send_message(chat_id, lock_msg, reply_markup=markup)

# ==========================================
# ২. কী-বোর্ড জেনারেটরসমূহ
# ==========================================
def get_credentials_keyboard(sid):
    sess = active_sessions.get(sid)
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess and sess.phone)

    if not has_phone:
        markup.add(
            InlineKeyboardButton(to_bold("NUMBER"), callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(to_bold("PASSWORD"), callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(
            InlineKeyboardButton(to_bold("PASSWORD"), callback_data=f"ask_pass:{sid}")
        )
    markup.add(InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold("START"), callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_sessions.get(sid)
    t_val = sess.target_profit if sess else 0
    s_val = sess.total_steps if sess else 7

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold(t_lbl), callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(to_bold(s_lbl), callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(to_bold("START"), callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(to_bold("CANCEL"), callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid):
    sess = active_sessions.get(sid)
    if sess:
        sess.anim_tick += 1
        spinner = SPINNER_FRAMES[sess.anim_tick % len(SPINNER_FRAMES)]
    else:
        spinner = "◴"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold("SHOT"), callback_data=f"shot:{sid}"),
        InlineKeyboardButton(to_bold("BAL"), callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(to_bold("STATS"), callback_data=f"stats:{sid}"),
        InlineKeyboardButton(to_bold(f"STOP {spinner}"), callback_data=f"stop:{sid}")
    )
    return markup

def play_clean_login_animation(chat_id, msg_id):
    frames = [
        "<b>CONNECTING REMOTE ENGINE</b>\n<code>▰▱▱▱▱▱▱▱▱▱ 10% Allocating isolated profile...</code>",
        "<b>INITIALIZING TARGET PLATFORM</b>\n<code>▰▰▰▱▱▱▱▱▱▱ 35% Securing connection instance...</code>",
        "<b>INJECTING AUTHENTICATION DATA</b>\n<code>▰▰▰▰▰▰▱▱▱▱ 65% Auto-filling credentials...</code>",
        "<b>VERIFYING ACTIVE SESSION</b>\n<code>▰▰▰▰▰▰▰▰▰▰ 100% Login verification complete!</code>"
    ]
    for frame in frames:
        try:
            bot.edit_message_text(frame, chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
        time.sleep(0.4)

# ==========================================
# ৩. কলব্যাক হ্যান্ডলার (Button Clicks)
# ==========================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    # ১. চ্যানেল জয়েন সম্পন্ন
    if action == "channels_joined":
        bot.answer_callback_query(call.id)
        lang_msg = (
            "<b>ভাষা নির্বাচন করুন / Choose Your Language:</b>\n\n"
            "দয়া করে আপনার সুবিধাজনক ভাষা সিলেক্ট করুন:"
        )
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("বাংলা (Bangla)", callback_data="lang_bn"),
            InlineKeyboardButton("English", callback_data="lang_en")
        )
        bot.edit_message_text(lang_msg, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    # ২. ভাষা নির্বাচন পরবর্তী ধাপ
    elif action in ["lang_bn", "lang_en"]:
        lang = "bn" if action == "lang_bn" else "en"
        db.set_user_lang(user_id, lang)
        bot.answer_callback_query(call.id)

        if db.has_active_subscription(user_id):
            show_platform_selection(chat_id, user_id, call.message.message_id)
        else:
            show_pricing_plans(chat_id, user_id, call.message.message_id)

    # ৩. প্রাইস প্ল্যান নির্বাচন
    elif action.startswith("plan_"):
        plan_key = action.replace("plan_", "")
        plan = PRICING_PLANS.get(plan_key)
        if not plan:
            return

        user_states[chat_id] = {
            "step": "CHOOSE_PAYMENT",
            "selected_plan": plan_key,
            "user_id": user_id
        }

        bot.answer_callback_query(call.id)
        pay_msg = (
            "<b>আসসালামু আলাইকুম।</b>\n"
            "আশা করি আপনার লেনদেনটি সফল হোক।\n\n"
            f"প্যাকেজ: <b>{plan['title']}</b>\n"
            f"মূল্য: <b>{plan['price']} BDT</b>\n\n"
            "দয়া করে আমাদের নাম্বারে সেন্ড মানি করুন। নিচের যেকোনো একটি পেমেন্ট মেথড সিলেক্ট করুন:"
        )
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("বিকাশ (Bkash)", callback_data=f"pay_bkash_{plan_key}"),
            InlineKeyboardButton("নগদ (Nagad)", callback_data=f"pay_nagad_{plan_key}")
        )
        markup.add(InlineKeyboardButton("প্রাইস লিস্টে ফিরে যান", callback_data="channels_joined"))
        bot.edit_message_text(pay_msg, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)

    # ৪. বিকাশ / নগদ নির্বাচন
    elif action.startswith("pay_"):
        spl = action.split("_")
        method_key = spl[1]
        plan_key = spl[2]
        method_info = PAYMENT_METHODS.get(method_key)
        plan_info = PRICING_PLANS.get(plan_key)

        user_states[chat_id] = {
            "step": "WAITING_TRX",
            "plan_key": plan_key,
            "method_key": method_key,
            "user_id": user_id
        }

        bot.answer_callback_query(call.id)
        number = method_info["number"]
        method_name = method_info["name"]

        inst_msg = (
            "<b>আসসালামু আলাইকুম।</b>\n"
            "আপনার লেনদেনটি সফল হোক এটাই আমাদের কামনা।\n\n"
            f"দয়া করে নিচের {method_name} নাম্বারে <b>{plan_info['price']} BDT</b> সেন্ড মানি করুন:\n\n"
            f"নাম্বার: <b>{number}</b> (Send Money)\n\n"
            "টাকা পাঠানো সম্পন্ন হলে আপনার <b>ট্রানজেকশন আইডিটি (TrxID)</b> খালি পেস্ট করুন আর কিছু করার দরকার নাই:"
        )
        bot.edit_message_text(inst_msg, chat_id=chat_id, message_id=call.message.message_id)

    # ৫. ওনার অনুমোদন বা বাতিল
    elif action.startswith("appr_"):
        req_id = action.replace("appr_", "")
        if call.from_user.id != OWNER_CHAT_ID:
            bot.answer_callback_query(call.id, "অনুমোদন দেওয়ার ক্ষমতা কেবল ওনারের রয়েছে।", show_alert=True)
            return

        req = db._read_data().get("payment_requests", {}).get(req_id)
        if not req:
            bot.answer_callback_query(call.id, "রিকোয়েস্ট পাওয়া যায়নি!")
            return

        plan_key = req["plan_key"]
        days = PRICING_PLANS.get(plan_key, {}).get("days", 1)
        success, target_uid = db.approve_payment(req_id, days)

        if success:
            bot.answer_callback_query(call.id, "পেমেন্ট সফলভাবে অনুমোদিত হয়েছে!")
            bot.edit_message_text(
                f"<b>[সফল] পেমেন্ট অনুমোদিত হয়েছে!</b>\n\nReq ID: <code>{req_id}</code>\nইউজার: <code>{target_uid}</code>\nমেয়াদ: <b>{days} দিন</b>",
                chat_id=chat_id,
                message_id=call.message.message_id
            )

            user_congrats = (
                "<b>আসসালামু আলাইকুম।</b>\n\n"
                "প্রিয় গ্রাহক, আপনার লেনদেনটি সফল হয়েছে। আপনি ফাইলটি নিতে পারবেন বা ইউজ করতে পারবেন।\n"
                "নিচের বাটন চেপে ট্রেডিং সাইট নির্বাচন করুন:"
            )
            bot.send_message(target_uid, user_congrats)
            show_platform_selection(target_uid, target_uid)

    elif action.startswith("canc_"):
        req_id = action.replace("canc_", "")
        if call.from_user.id != OWNER_CHAT_ID:
            bot.answer_callback_query(call.id, "অনুমতি নেই।", show_alert=True)
            return

        success, target_uid = db.reject_payment(req_id)
        if success:
            bot.answer_callback_query(call.id, "পেমেন্ট বাতিল করা হয়েছে।")
            bot.edit_message_text(
                f"<b>[বাতিল] পেমেন্ট বাতিল করা হয়েছে!</b>\n\nReq ID: <code>{req_id}</code>",
                chat_id=chat_id,
                message_id=call.message.message_id
            )
            user_cancel = (
                "<b>আসসালামু আলাইকুম।</b>\n\n"
                "দুঃখিত, আপনার ট্রানজেকশনটি যাচাই করে বাতিল করা হয়েছে।\n"
                "দয়া করে পুনরায় চেষ্টা করার জন্য /start চাপুন।"
            )
            bot.send_message(target_uid, user_cancel)

    # ৬. প্ল্যাটফর্ম সিলেক্ট (Amar Club / DK Win)
    elif action in ["site_amarclub", "site_dkwin"]:
        platform_key = "amarclub" if action == "site_amarclub" else "dkwin"
        plat_info = PLATFORMS[platform_key]

        session = register_session(user_id, chat_id, platform_key, bot)
        user_states[chat_id] = {"active_sid": session.session_id}

        cred_card_text = (
            f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
            f"প্ল্যাটফর্ম: <b>{plat_info['name']}</b>\n\n"
            "আসসালামু আলাইকুম, দয়া করে নিচের বাটন চেপে আপনার নাম্বার এবং পাসওয়ার্ড দিন। "
            "এটি সম্পূর্ণ গোপন থাকবে এবং কাজ শেষে চ্যাট থেকে মুছে যাবে।"
        )

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            cred_card_text,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(session.session_id)
        )
        user_states[chat_id]["cred_card_msg_id"] = call.message.message_id

    # ৭. NUMBER বাটন
    elif action == "ask_num" and sid in active_sessions:
        user_states[chat_id]["input_mode"] = "WAITING_PHONE"
        user_states[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT NUMBER')}</b>\n\nআপনার একাউন্ট নাম্বার (ফোন নাম্বার) লিখে পাঠান:")
        user_states[chat_id]["temp_prompt_id"] = prompt_m.message_id

    # ৮. PASSWORD বাটন
    elif action == "ask_pass" and sid in active_sessions:
        sess = active_sessions[sid]
        if not sess.phone:
            bot.answer_callback_query(call.id, "দয়া করে আগে নাম্বারটি দিন!", show_alert=True)
            return

        user_states[chat_id]["input_mode"] = "WAITING_PASS"
        user_states[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>{to_bold('ACCOUNT PASSWORD')}</b>\n\nআপনার একাউন্টের পাসওয়ার্ড লিখে পাঠান:")
        user_states[chat_id]["temp_prompt_id"] = prompt_m.message_id

    # ৯. START বাটন (উইনগো মার্কেট লোড করা)
    elif action == "start_cfg" and sid in active_sessions:
        bot.answer_callback_query(call.id, "উইনগো ৩০এস পেজ প্রস্তুত করা হচ্ছে...")
        threading.Thread(target=prepare_wingo_task, args=(chat_id, sid), daemon=True).start()

    # ১০. TARGET বাটন
    elif action == "set_tgt" and sid in active_sessions:
        user_states[chat_id]["input_mode"] = "WAITING_TARGET"
        user_states[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[sid].current_balance
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('TARGET PROFIT')}</b>\n\nবর্তমান ব্যালেন্স: <code>৳ {cur_bal:.2f}</code>\n\nআপনি কত টাকা প্রফিট করতে চান? পরিমাণটি লিখুন (যেমন: <code>500</code>):")
        user_states[chat_id]["temp_prompt_id"] = p_msg.message_id

    # ১১. STEPS বাটন
    elif action == "set_stp" and sid in active_sessions:
        user_states[chat_id]["input_mode"] = "WAITING_STEPS"
        user_states[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        tgt = active_sessions[sid].target_profit
        p_msg = bot.send_message(chat_id, f"<b>{to_bold('MARTINGALE STEPS')}</b>\n\nটার্গেট প্রফিট: <code>৳ {tgt:.2f}</code>\n\nমার্টিনগেল ব্যাকআপ স্টেপ সংখ্যা লিখুন (যেমন: <code>7</code> বা <code>10</code>):")
        user_states[chat_id]["temp_prompt_id"] = p_msg.message_id

    # ১২. RUN AUTOMATION বাটন
    elif action == "run_auto" and sid in active_sessions:
        sess = active_sessions[sid]
        if not sess.target_profit or sess.target_profit <= 0:
            bot.answer_callback_query(call.id, "আগে টার্গেট অ্যামাউন্ট লিখুন!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "ট্রেডিং ইঞ্জিন সক্রিয় করা হচ্ছে...")
        sess.start_wingo_automation(sess.target_profit, sess.total_steps)
        time.sleep(1.5)

        start_snap = sess.capture_screenshot("run")
        cur_b = sess.current_balance
        t_total = cur_b + sess.target_profit

        dashboard_caption = (
            f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
            f"Platform: <b>{sess.platform_info['name']}</b>\n"
            f"Starting Balance: <code>৳ {cur_b:.2f}</code>\n"
            f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
            f"Total Steps: <b>{sess.total_steps}</b>\n\n"
            f"Trading automatically in background 24/7.\n"
            f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
        )

        if start_snap and os.path.exists(start_snap):
            sess.display_or_replace_photo(start_snap, dashboard_caption, get_trading_control_keyboard(sid))
            try:
                os.remove(start_snap)
            except Exception:
                pass

    # ১৩. SHOT (রিয়েল-টাইম স্ক্রিনশট)
    elif action == "shot" and sid in active_sessions:
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "ফুটেজ আপডেট হচ্ছে...")
        temp_shot = sess.capture_screenshot("live")
        if temp_shot and os.path.exists(temp_shot):
            t_total = sess.start_balance + sess.target_profit
            caption = (
                f"<b>{to_bold('24/7 AUTOMATION ENGINE ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.platform_info['name']}</b>\n"
                f"Starting Balance: <code>৳ {sess.start_balance:.2f}</code>\n"
                f"Target Balance: <code>৳ {t_total:.2f}</code>\n"
                f"Total Steps: <b>{sess.total_steps}</b>\n\n"
                f"সময়: <code>{time.strftime('%H:%M:%S')}</code>\n"
                f"<b>LIVE STATUS</b>: মার্টিনগেল ইঞ্জিন সফলভাবে সচল রয়েছে।"
            )
            sess.display_or_replace_photo(temp_shot, caption, get_trading_control_keyboard(sid))
            try:
                os.remove(temp_shot)
            except Exception:
                pass

    # ১৪. BAL (লাইভ ব্যালেন্স চেক)
    elif action == "bal" and sid in active_sessions:
        sess = active_sessions[sid]
        b = sess.execute_js("let el=document.getElementById('ui-bal'); return el ? el.innerText : '';")
        bot.answer_callback_query(call.id, f"Live Balance: {b or '৳ ' + str(sess.current_balance)}", show_alert=True)

    # ১৫. STATS (লাইভ ট্রেডিং স্ট্যাটাস)
    elif action == "stats" and sid in active_sessions:
        sess = active_sessions[sid]
        stat_data = sess.execute_js("""
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
        if stat_data:
            rep = (
                f"<b>{to_bold('LIVE STATS REPORT')}</b>\n\n"
                f"ব্যালেন্স: <code>৳ {stat_data['curBal']:.2f}</code>\n"
                f"টার্গেট: <code>৳ {stat_data['tgtAmt']:.2f}</code>\n"
                f"মার্টিনগেল লেভেল: <b>Step {stat_data['step']}/{stat_data['maxStep']}</b>\n"
                f"উইন: <b>{stat_data['w']}</b> | লস: <b>{stat_data['l']}</b>"
            )
            bot.send_message(chat_id, rep)
        else:
            bot.answer_callback_query(call.id, "ইঞ্জিন স্ক্যানিং চলছে...", show_alert=True)

    # ১৬. STOP বাটন
    elif action == "stop" and sid in active_sessions:
        sess = active_sessions[sid]
        sess.execute_js("let btn = document.querySelector('#sys-core-fin button'); if(btn) btn.click();")
        sess.is_trading = False
        bot.answer_callback_query(call.id, "ট্রেডিং সাময়িক স্থগিত করা হয়েছে", show_alert=True)
        bot.send_message(chat_id, f"<b>{to_bold('TRADING PAUSED')}</b>\nট্রেডিং অটোমেশন সাময়িকভাবে থামানো হয়েছে।")

    # ১৭. CANCEL বাটন
    elif action == "cancel" and sid in active_sessions:
        bot.answer_callback_query(call.id, "সেশন বাতিল করা হয়েছে")
        close_session_tab(sid)
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, f"<b>{to_bold('SESSION TERMINATED')}</b>\nবর্তমান সেশনটি সুন্দরভাবে বন্ধ করা হয়েছে। নতুন সেশনের জন্য /start পাঠান।")

# ==========================================
# ৪. টেক্সট মেসেজ ও ইনপুট হ্যান্ডলার
# ==========================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.strip()
    u = user_states.get(chat_id, {})
    step = u.get("step")
    input_mode = u.get("input_mode")
    sid = u.get("active_sid")

    # ট্রানজেকশন আইডি
    if step == "WAITING_TRX":
        plan_key = u.get("plan_key")
        method_key = u.get("method_key")
        plan = PRICING_PLANS.get(plan_key)
        method = PAYMENT_METHODS.get(method_key)

        req_id = db.create_payment_request(
            user_id=user_id,
            username=message.from_user.username,
            plan_key=plan_key,
            plan_title=plan["title"],
            price=plan["price"],
            method_key=method_key,
            method_name=method["name"],
            trx_id=text
        )

        u["step"] = "PENDING_APPROVAL"
        bot.send_message(
            chat_id,
            "<b>ধন্যবাদ! আপনার ট্রানজেকশন আইডিটি সফলভাবে জমা হয়েছে।</b>\n\n"
            f"TrxID: <code>{text}</code>\n"
            f"পরিমাণ: <b>{plan['price']} BDT</b>\n\n"
            "আমাদের অ্যাডমিন প্যানেলে যাচাই চলছে। অনুমোদন সম্পন্ন হওয়ামাত্রই আপনার কাছে স্বয়ংক্রিয় মেসেজ যাবে।"
        )

        owner_alert = (
            "<b>নতুন পেমেন্ট রিকোয়েস্ট এসেছে!</b>\n\n"
            f"Request ID: <code>{req_id}</code>\n"
            f"গ্রাহক: <code>{user_id}</code> (@{message.from_user.username or 'None'})\n"
            f"প্যাকেজ: <b>{plan['title']} ({plan['btn_label']})</b>\n"
            f"মেথড: <b>{method['name']}</b>\n"
            f"টাকার পরিমাণ: <b>{plan['price']} BDT</b>\n"
            f"TrxID: <code>{text}</code>"
        )
        owner_markup = InlineKeyboardMarkup(row_width=2)
        owner_markup.add(
            InlineKeyboardButton("[Approve / অনুমোদন করুন]", callback_data=f"appr_{req_id}"),
            InlineKeyboardButton("[Cancel / বাতিল করুন]", callback_data=f"canc_{req_id}")
        )
        try:
            bot.send_message(OWNER_CHAT_ID, owner_alert, reply_markup=owner_markup)
        except Exception:
            pass
        return

    # ক্রেডেনশিয়াল ইনপুট
    if not sid or sid not in active_sessions:
        return

    sess = active_sessions[sid]
    safe_delete_message(chat_id, message.message_id)

    if u.get("temp_prompt_id"):
        safe_delete_message(chat_id, u["temp_prompt_id"])
        u["temp_prompt_id"] = None

    if input_mode == "WAITING_PHONE":
        sess.phone = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            try:
                masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_card_text = (
                    f"<b>{to_bold('ACCOUNT LOGIN')}</b>\n\n"
                    f"প্ল্যাটফর্ম: <b>{sess.platform_info['name']}</b>\n"
                    f"নাম্বার: <code>{masked}</code> (সংরক্ষিত)\n\n"
                    f"এখন নিচের <b>PASSWORD</b> বাটনে চাপ দিয়ে পাসওয়ার্ড দিন:"
                )
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=u["cred_card_msg_id"],
                    reply_markup=get_credentials_keyboard(sid)
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        sess.password = text
        u["input_mode"] = None

        if u.get("cred_card_msg_id"):
            safe_delete_message(chat_id, u["cred_card_msg_id"])
            u["cred_card_msg_id"] = None

        anim_msg = bot.send_message(chat_id, "<b>CONNECTING REMOTE ENGINE</b>")
        threading.Thread(
            target=process_login_task,
            args=(chat_id, sid, sess.phone, sess.password, anim_msg.message_id),
            daemon=True
        ).start()

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            sess.target_profit = val
            u["input_mode"] = None

            wingo_snap = sess.capture_screenshot("wingo")
            cur_bal = sess.current_balance
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.platform_info['name']}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Target: <code>৳ {val:.2f}</code>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            if wingo_snap and os.path.exists(wingo_snap):
                sess.display_or_replace_photo(wingo_snap, config_caption, get_setup_param_keyboard(sid))
                try:
                    os.remove(wingo_snap)
                except Exception:
                    pass
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক সংখ্যা লিখুন (যেমন: 500):")
            u["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            sess.total_steps = steps_val
            u["input_mode"] = None

            wingo_snap = sess.capture_screenshot("wingo")
            cur_bal = sess.current_balance
            config_caption = (
                f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
                f"Platform: <b>{sess.platform_info['name']}</b>\n"
                f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n"
                f"Selected Steps: <b>{steps_val}</b>\n\n"
                f"প্যারামিটার সেট হয়েছে। ট্রেডিং চালু করতে <b>START</b> চাপুন:"
            )
            if wingo_snap and os.path.exists(wingo_snap):
                sess.display_or_replace_photo(wingo_snap, config_caption, get_setup_param_keyboard(sid))
                try:
                    os.remove(wingo_snap)
                except Exception:
                    pass
        except ValueError:
            p_msg = bot.send_message(chat_id, "দয়া করে সঠিক পূর্ণসংখ্যা লিখুন (যেমন: 7):")
            u["temp_prompt_id"] = p_msg.message_id

# ==========================================
# ৫. ব্যাকগ্রাউন্ড থ্রেড টাস্কসমূহ
# ==========================================
def process_login_task(chat_id, sid, phone, password, anim_msg_id):
    sess = active_sessions.get(sid)
    if not sess:
        return

    play_clean_login_animation(chat_id, anim_msg_id)
    sess.start_driver()
    success, err_msg = sess.auto_login(phone, password)
    safe_delete_message(chat_id, anim_msg_id)

    if not success:
        close_session_tab(sid)
        bot.send_message(chat_id, f"<b>{to_bold('LOGIN FAILED')}</b>\n\nReason: <i>{err_msg}</i>\n\nপুনরায় চেষ্টা করার জন্য /start চাপুন।")
        return

    time.sleep(1.5)
    login_snap = sess.capture_screenshot("login_done")
    masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone

    caption = (
        f"<b>{to_bold('LOGIN SUCCESSFUL')}</b>\n\n"
        f"Platform: <b>{sess.platform_info['name']}</b>\n"
        f"Account: <code>{masked_phone}</code>\n\n"
        f"লগইন সফল হয়েছে। ট্রেডিং শুরু করতে নিচে <b>START</b> বাটন চাপুন:"
    )

    if login_snap and os.path.exists(login_snap):
        sess.display_or_replace_photo(login_snap, caption, get_start_screen_keyboard(sid))
        try:
            os.remove(login_snap)
        except Exception:
            pass

def prepare_wingo_task(chat_id, sid):
    sess = active_sessions.get(sid)
    if not sess:
        return

    cur_bal = sess.navigate_to_wingo()
    wingo_snap = sess.capture_screenshot("wingo")

    config_caption = (
        f"<b>{to_bold('WINGO 30S MARKET ACTIVE')}</b>\n\n"
        f"Platform: <b>{sess.platform_info['name']}</b>\n"
        f"Live Balance: <code>৳ {cur_bal:.2f}</code>\n\n"
        f"নিচের <b>TARGET</b> ও <b>STEPS</b> বাটন চেপে ট্রেডিং সেট করুন, তারপর <b>START</b> চাপুন:"
    )

    if wingo_snap and os.path.exists(wingo_snap):
        sess.display_or_replace_photo(wingo_snap, config_caption, get_setup_param_keyboard(sid))
        try:
            os.remove(wingo_snap)
        except Exception:
            pass

def show_pricing_plans(chat_id, user_id, message_id=None):
    price_text = (
        "<b>WinGo VIP প্রাইজ লিস্ট</b>\n\n"
        "যেকোনো একটি প্যাকেজ সিলেক্ট করে অটোমেশন উপভোগ করুন:\n\n"
        "• 1 Day: 500 BDT\n"
        "• 3 Days: 1,300 BDT\n"
        "• 6 Days: 2,400 BDT\n"
        "• 7 Days: 2,700 BDT\n"
        "• 10 Days: 3,500 BDT\n"
        "• 1 Month (30 Days): 9,000 BDT"
    )
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("1D - 500 BDT", callback_data="plan_1d"),
        InlineKeyboardButton("3D - 1300 BDT", callback_data="plan_3d"),
        InlineKeyboardButton("6D - 2400 BDT", callback_data="plan_6d"),
        InlineKeyboardButton("7D - 2700 BDT", callback_data="plan_7d"),
        InlineKeyboardButton("10D - 3500 BDT", callback_data="plan_10d"),
        InlineKeyboardButton("30D - 9000 BDT", callback_data="plan_30d"),
    ]
    markup.add(*buttons)

    if message_id:
        try:
            bot.edit_message_text(price_text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, price_text, reply_markup=markup)

def show_platform_selection(chat_id, user_id, message_id=None):
    plat_text = (
        f"<b>{to_bold('SELECT PLATFORM')}</b>\n\n"
        "আসসালামু আলাইকুম, দয়া করে আপনি আপনার একটি ট্রেডিং সাইট নির্বাচন করুন:"
    )
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(to_bold("AMAR CLUB"), callback_data="site_amarclub"),
        InlineKeyboardButton(to_bold("DK WIN"), callback_data="site_dkwin")
    )
    if message_id:
        try:
            bot.edit_message_text(plat_text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
            return
        except Exception:
            pass
    bot.send_message(chat_id, plat_text, reply_markup=markup)
