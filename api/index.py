from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

import asyncio
import random
import urllib3
import httpx
urllib3.disable_warnings()

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - Ultimate Strike Command</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#04060d;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:20px;text-align:center}
.container{max-width:1000px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 20px #ff0040}
.panel{background:#070a14;border:1px solid #ff0040;padding:20px;border-radius:12px;box-shadow:0 0 25px rgba(255,0,64,0.3)}
input{padding:14px;width:70%;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:16px;outline:none}
button{padding:14px 25px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:16px;margin-top:10px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 25px #ff0040}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:800px;border-radius:10px;text-align:right;border-right:6px solid #ff0040}
.proof{background:#04060d;color:#00ff88;padding:10px;border-radius:6px;margin-top:8px;font-size:12px;direction:ltr;word-break:break-all;border:1px solid #004422}
.status{margin:15px 0;color:#fff;font-size:14px}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 القائد الأعظم - ترسانة الاجتياح المطلق ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="أدخل رابط الهدف (مثال: https://target.com)" value="https://">
<br>
<button id="exec_btn" onclick="runUltimateCommand()">إطلاق الهجوم الميداني الشامل 🚀</button>
<div id="status" class="status"></div>
<div id="results"></div>
</div>
</div>

<script>
async function runUltimateCommand(){
 const url = document.getElementById('target_url').value.trim();
 if(!url || url==='https://'){ alert('يرجى إدخال الرابط يا فندم!'); return; }
 const btn = document.getElementById('exec_btn');
 const status = document.getElementById('status');
 const results = document.getElementById('results');
 btn.disabled=true; btn.textContent='جاري التنفيذ... ⚡';
 status.textContent='⏳ جارٍ إطلاق الفحص على الهدف: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url:url})
   });
   const data = await res.json();
   status.textContent='✅ اكتمل الهجوم | الهدف: '+data.url+' | حالة الدرع: '+data.waf_status;
   
   if(!data.actions || data.actions.length==0){
     results.innerHTML='<div class="card"><b>مؤمن تماماً</b><div class="proof">Target defenses held successfully.</div></div>';
   } else {
     data.actions.forEach(v=>{
       results.innerHTML+=`
       <div class="card">
         <b>${v.type}</b>
         <div style="margin:5px 0">${v.desc}</div>
         <div class="proof">${v.proof}</div>
       </div>`;
     });
   }
 }catch(e){
   status.textContent='❌ خطأ: '+e.message;
 }
 btn.disabled=false; btn.textContent='إطلاق الهجوم الميداني الشامل 🚀';
}
</script>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "https://" + s
    return s.rstrip("/")

async def execute_ultimate_engine(target):
    actions = []
    waf_status = "Dynamic Perimeter Guard"
    fake_ip = f"{random.randint(10,200)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) V400-Ultimate-Strike/4.0",
        "X-Forwarded-For": fake_ip,
        "X-Real-IP": fake_ip,
        "Connection": "close"
    }

    try:
        async with httpx.AsyncClient(verify=False, timeout=10.0, headers=headers, follow_redirects=True) as client:
            res = await client.get(target)
            srv = res.headers.get('server', '').lower()
            if 'cloudflare' in srv: waf_status = "Cloudflare Shield (Bypass Attempted)"

            ultimate_paths = [
                "/live/ch0_0.jpg", "/snapshot.jpg", "/cgi-bin/snapshot.cgi",
                "/streaming/channels/1", "/onvif/device_service", "/webcam",
                "/video.cgi", "/mjpeg", "/axis-cgi/mjpg/video.cgi", "/admin/login.asp",
                "/config/config.json", "/api/v1/stream"
            ]

            tasks = [client.get(target.rstrip('/') + p, timeout=3.0) for p in ultimate_paths]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for path, r in zip(ultimate_paths, responses):
                if isinstance(r, httpx.Response):
                    if r.status_code == 200:
                        actions.append({
                            "type": f"ULTIMATE BREACH DETECTED: {path}",
                            "desc": "تم اختراق المسار بنجاح واستجابة الهدف برمز 200 بدون حجب.",
                            "proof": f"URL: {r.url} | Status: 200 OK | Size: {len(r.content)}"
                        })
                    elif r.status_code == 403:
                        actions.append({
                            "type": f"FIREWALL BLOCK: {path}",
                            "desc": "جدار الحماية للهدف تصدى للطلب وأعاد رمز 403.",
                            "proof": f"URL: {r.url} | Status: 403 Forbidden"
                        })

            if not actions:
                actions.append({
                    "type": "Ultimate Strike Completed",
                    "desc": "تم إطلاق الهجوم الشامل، وتبين أن الأهداف والمنافذ مغلقة ومحصنة.",
                    "proof": f"Main Target Status: {res.status_code} | Server Shield: {srv or 'Active'}"
                })

    except Exception as e:
        actions.append({
            "type": "Strike Connection Error",
            "desc": "تعذر إكمال الاتصال بالهدف بسبب الحجب العنيف أو انقطاع المهلة.",
            "proof": str(e)
        })

    return actions, waf_status

@app.route('/', methods=['GET'])
def home():
    return HTML_COMMAND_CENTER

@app.route('/api/index', methods=['POST'])
def check():
    target = clean_url((request.get_json(silent=True) or {}).get("url", "https://example.com"))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    actions, waf_status = loop.run_until_complete(execute_ultimate_engine(target))
    loop.close()

    return jsonify({"url": target, "waf_status": waf_status, "actions": actions})
