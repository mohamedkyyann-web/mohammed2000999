from flask import Flask, render_template_string, request, jsonify
import asyncio, httpx, random, urllib3

urllib3.disable_warnings()

app = Flask(__name__)

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 Flask القائد الأعظم - Ultimate Strike Command</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#000003;color:#00ff88;font-family:'Courier New',Consolas,monospace;min-height:100vh;padding:20px}
.container{max-width:1200px;margin:auto}
h1{text-align:center;font-size:36px;text-shadow:0 0 40px #ff0040;margin:25px 0;color:#ff0040}
.badges{text-align:center;margin-bottom:25px}
.badge{display:inline-block;background:#140105;border:1px solid #ff0040;color:#ff3366;padding:6px 14px;border-radius:6px;font-size:12px;margin:4px;font-weight:bold}
.panel{background:#04060d;border:1px solid #ff0040;border-radius:12px;padding:25px;box-shadow:0 0 30px rgba(255,0,64,0.35)}
.input-group{display:flex;gap:12px;margin-bottom:20px}
input{flex:1;background:#010204;border:2px solid #ff0040;color:#fff;padding:16px;border-radius:8px;font-size:15px;outline:none}
input:focus{box-shadow:0 0 35px #ff0040}
button{background:#ff0040;color:#fff;border:none;padding:16px 35px;border-radius:8px;font-weight:bold;cursor:pointer;font-size:16px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 40px #ff0040}
button:disabled{opacity:0.5}
.status{margin:15px 0;padding:14px;background:#070b16;border-right:6px solid #ff0040;border-radius:6px;display:none;color:#fff;font-size:14px}
.results{margin-top:20px}
.card{background:#070a14;border:1px solid #1a2a40;border-radius:10px;padding:20px;margin:15px 0;border-right:8px solid}
.card.Critical{border-right-color:#ff0000;background:#1c0105}
.card.High{border-right-color:#ff0040}
.card.Medium{border-right-color:#ffaa00}
.card.Low{border-right-color:#00aaff}
.sev{padding:3px 10px;border-radius:4px;font-size:11px;font-weight:bold;float:left}
.sev.Critical{background:#ff0000;color:#fff}
.sev.High{background:#ff0040;color:#fff}
.sev.Medium{background:#ffaa00;color:#000}
.sev.Low{background:#00aaff;color:#fff}
.proof{background:#000;color:#00ff88;padding:12px;border-radius:6px;margin-top:10px;font-size:12px;direction:ltr;word-break:break-all;white-space:pre-wrap;border:1px solid #004422}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 Flask القائد الأعظم - ترسانة الاجتياح المطلق ⚔️</h1>
<div class="badges">
<span class="badge">Flask Framework Engine</span>
<span class="badge">Advanced Proxy Spoofing</span>
<span class="badge">Surveillance Payload Engine</span>
</div>
<div class="panel">
<div class="input-group">
<input id="target_url" placeholder="أدخل آي بي أو رابط الهدف (مثال: https://target.com أو IP:Port)" value="https://">
<button id="exec_btn" onclick="runUltimateCommand()">إطلاق الهجوم الميداني الشامل 🚀</button>
</div>
<div id="status" class="status"></div>
<div id="results" class="results"></div>
</div>
</div>

<script>
async function runUltimateCommand(){
 const url = document.getElementById('target_url').value.trim();
 if(!url || url==='https://'){ alert('يرجى إدخال عنوان الهدف يا فندم!'); return; }
 const btn = document.getElementById('exec_btn');
 const status = document.getElementById('status');
 const results = document.getElementById('results');
 btn.disabled=true; btn.textContent='جاري تنفيذ الاجتياح المكثف... ⚡';
 status.style.display='block'; status.textContent='⏳ جارٍ إطلاق حزم الفحص المكثف وتجاوز الجدران النارية للهدف: '+url;
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
     results.innerHTML='<div class="card Low"><span class="sev Low">SECURE</span><b>تقرير الترسانة:</b><div class="proof">Target defenses held successfully against all paths.</div></div>';
   } else {
     data.actions.forEach(v=>{
       results.innerHTML+=`
       <div class="card ${v.severity}">
         <span class="sev ${v.severity}">${v.severity}</span>
         <b>${escapeHtml(v.type)}</b>
         <div style="margin:10px 0">${escapeHtml(v.desc)}</div>
         <div class="proof">${escapeHtml(v.proof)}</div>
       </div>`;
     });
   }
 }catch(e){
   status.textContent='❌ خطأ أثناء الهجوم الميداني: '+e.message;
 }
 btn.disabled=false; btn.textContent='إطلاق الهجوم الميداني الشامل 🚀';
}

function escapeHtml(text) {
    return String(text).replace(/&/g, "&").replace(/</g, "<").replace(/>/g, ">").replace(/"/g, """).replace(/'/g, "'");
}
</script>
</body>
</html>"""

def clean_url(raw):
    if not raw: return "https://example.com"
    s = raw.strip().lstrip('/').strip()
    if not s.startswith('http'):
        s = 'https://' + s
    return s.rstrip('/')

async def execute_ultimate_engine(target):
    actions = []
    waf_status = "Dynamic Perimeter Guard"
    fake_ip = f"{random.randint(10,200)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) V400-Flask-Strike/4.0",
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
                            "severity": "Critical",
                            "desc": "تم اختراق المسار بنجاح واستجابة الهدف برمز 200 بدون حجب.",
                            "proof": f"URL: {r.url} | Status: 200 OK | Size: {len(r.content)}"
                        })
                    elif r.status_code == 403:
                        actions.append({
                            "type": f"FIREWALL BLOCK: {path}",
                            "severity": "Medium",
                            "desc": "جدار الحماية للهدف تصدى للطلب وأعاد رمز 403.",
                            "proof": f"URL: {r.url} | Status: 403 Forbidden"
                        })

            if not actions:
                actions.append({
                    "type": "Ultimate Strike Completed",
                    "severity": "Low",
                    "desc": "تم إطلاق الهجوم الشامل عبر Flask، وتبين أن الأهداف والمنافذ مغلقة.",
                    "proof": f"Main Target Status: {res.status_code} | Server Shield: {srv or 'Active'}"
                })

    except Exception as e:
        actions.append({
            "type": "Strike Connection Error",
            "severity": "Low",
            "desc": "تعذر إكمال الاتصال بالهدف بسبب الحجب العنيف أو انقطاع المهلة.",
            "proof": str(e)
        })

    return actions, waf_status

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def index(path):
    if request.method == 'POST':
        try:
            body_data = request.get_json(silent=True) or {}
            raw = body_data.get('url', 'https://example.com')
        except:
            raw = 'https://example.com'
        
        target = clean_url(raw)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        actions, waf_status = loop.run_until_complete(execute_ultimate_engine(target))
        loop.close()
        
        return jsonify({"url": target, "waf_status": waf_status, "actions": actions})
    
    return render_template_string(HTML_COMMAND_CENTER)
