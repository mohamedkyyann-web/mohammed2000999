from flask import Flask, request, jsonify

app = Flask(__name__)

import httpx
import urllib3
urllib3.disable_warnings()

HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>فحص حماية موقعي</title>
<style>body{background:#04060d;color:#fff;font-family:sans-serif;padding:20px;text-align:center}input{padding:14px;width:70%;border-radius:8px;border:1px solid #00ff88;background:#000;color:#fff}button{padding:14px 20px;background:#00ff88;border:none;border-radius:8px;font-weight:bold;cursor:pointer;margin-top:10px}.card{background:#070a14;border:1px solid #1a2a40;padding:15px;margin:10px auto;max-width:600px;border-radius:10px;text-align:right}</style>
</head>
<body>
<h1>🛡️ فحص حماية موقعي - اخلاقي</h1>
<p>افحص موقعك انت فقط</p>
<input id="u" placeholder="https://mysite.com" value="https://example.com">
<br><button onclick="run()">افحص الآن</button>
<div id="r"></div>
<script>
async function run(){
 const url=document.getElementById('u').value;
 const res=await fetch('/api/index',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url:url})});
 const data=await res.json();
 document.getElementById('r').innerHTML = data.actions.map(a=>'<div class="card"><b>'+a.type+'</b><br>'+a.desc+'<br><small>'+a.proof+'</small></div>').join('');
}
</script>
</body>
</html>"""

def clean_url(raw):
    s = (raw or "").strip()
    if not s.startswith("http"):
        s = "https://" + s
    return s.rstrip("/")

@app.route('/', methods=['GET'])
def home():
    return HTML

@app.route('/api/index', methods=['POST'])
def check():
    target = clean_url((request.get_json(silent=True) or {}).get("url", "https://example.com"))
    actions = []
    try:
        # اخلاقي: طلب واحد فقط، بدون تزوير IP، بدون verify=False، بدون كاميرات
        with httpx.Client(timeout=8.0, follow_redirects=True, headers={"User-Agent": "My-Site-Security-Check/1.0"}) as client:
            res = client.get(target)
            headers = {k.lower(): v for k, v in res.headers.items()}

            if "strict-transport-security" not in headers:
                actions.append({"type": "Missing HSTS", "desc": "موقعك ناقصه ترويسة HSTS، فعلها لتحمي الزوار.", "proof": f"Status: {res.status_code}"})
            else:
                actions.append({"type": "HSTS OK", "desc": "ترويسة HSTS موجودة، ممتاز.", "proof": headers.get("strict-transport-security", "")})

            if "x-frame-options" not in headers and "content-security-policy" not in headers:
                actions.append({"type": "Missing Clickjacking Protection", "desc": "موقعك بدون حماية من Clickjacking.", "proof": f"Status: {res.status_code}"})
            else:
                actions.append({"type": "Clickjacking Protection OK", "desc": "حماية Clickjacking موجودة.", "proof": "OK"})

            if "server" in headers:
                actions.append({"type": "Server Header Exposed", "desc": "السيرفر يكشف اسمه، اخفيه.", "proof": f"Server: {headers['server']}"})

            if not actions:
                actions.append({"type": "Check Done", "desc": "الفحص اكتمل.", "proof": f"Status: {res.status_code}"})

    except Exception as e:
        actions.append({"type": "Connection Error", "desc": "ما قدرنا نوصل لموقعك، تأكد من الرابط.", "proof": str(e)[:200]})

    return jsonify({"url": target, "actions": actions})
