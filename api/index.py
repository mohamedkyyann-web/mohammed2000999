from collections import deque
from urllib.parse import urlparse
from urllib import request as url_request
import datetime
import hashlib
import ipaddress
import os
import socket

from flask import Flask, jsonify, render_template_string, request, Response

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET_KEY", hashlib.sha256(b"pdu_workbench_v2").digest())
DASHBOARD_PASSWORD_HASH = hashlib.sha256(
    os.environ.get("DASHBOARD_PASSWORD", "admin123").encode()
).hexdigest()

MAX_STORED_PACKETS = 200
PACKETS_STORE = deque(maxlen=MAX_STORED_PACKETS)

GSM7_BASIC_MAP = {
    "@": 0x00, "£": 0x01, "$": 0x02, "¥": 0x03, "è": 0x04, "é": 0x05, "ù": 0x06, "ì": 0x07,
    "ò": 0x08, "Ç": 0x09, "\n": 0x0A, "Ø": 0x0B, "ø": 0x0C, "\r": 0x0D, "Å": 0x0E, "å": 0x0F,
    "Δ": 0x10, "_": 0x11, "Φ": 0x12, "Γ": 0x13, "Λ": 0x14, "Ω": 0x15, "Π": 0x16, "Ψ": 0x17,
    "Σ": 0x18, "Θ": 0x19, "Ξ": 0x1A, "Æ": 0x1C, "æ": 0x1D, "ß": 0x1E, "É": 0x1F, " ": 0x20,
    "!": 0x21, '"': 0x22, "#": 0x23, "¤": 0x24, "%": 0x25, "&": 0x26, "'": 0x27, "(": 0x28,
    ")": 0x29, "*": 0x2A, "+": 0x2B, ",": 0x2C, "-": 0x2D, ".": 0x2E, "/": 0x2F,
    **{str(d): 0x30 + d for d in range(10)},
    ":": 0x3A, ";": 0x3B, "<": 0x3C, "=": 0x3D, ">": 0x3E, "?": 0x3F, "¡": 0x40,
    **{chr(65 + i): 0x41 + i for i in range(26)},
    "Ä": 0x5B, "Ö": 0x5C, "Ñ": 0x5D, "Ü": 0x5E, "§": 0x5F, "¿": 0x60,
    **{chr(97 + i): 0x61 + i for i in range(26)},
    "ä": 0x7B, "ö": 0x7C, "ñ": 0x7D, "ü": 0x7E, "à": 0x7F,
}


def encode_gsm7_septets(text: str) -> bytes | None:
    septets = [GSM7_BASIC_MAP[ch] for ch in text if ch in GSM7_BASIC_MAP]
    if len(septets) != len(text):
        return None
    packed = bytearray()
    carry = 0
    carry_bits = 0
    for s in septets:
        val = s & 0x7F
        packed.append(((val << carry_bits) | carry) & 0xFF)
        carry = val >> (7 - carry_bits)
        carry_bits += 1
        if carry_bits == 7:
            packed.append(carry & 0xFF)
            carry = 0
            carry_bits = 0
    if carry_bits > 0:
        packed.append(carry & 0xFF)
    return bytes(packed)


def encode_semi_octets(digits: str) -> bytes:
    padded = digits + ("F" if len(digits) % 2 == 1 else "")
    return bytes(
        ((int(padded[i + 1], 16) if padded[i + 1] != "F" else 0x0F) << 4) | int(padded[i], 16)
        for i in range(0, len(padded), 2)
    )


def compose_command_payload(cmd_name: str, cmd_args: str, note_text: str) -> str:
    clean_cmd = "".join(c for c in cmd_name.strip().upper() if c.isalnum() or c in ("_", "-")) or "PING"
    clean_args = cmd_args.strip()[:80]
    clean_note = note_text.strip()[:120]
    cmd_part = f"CMD:{clean_cmd}" + (f"({clean_args})" if clean_args else "")
    return f"{cmd_part} | {clean_note}" if clean_note else cmd_part


def build_class0_command_packet(phone: str, payload_text: str, encoding_pref: str = "auto") -> dict:
    cleaned = "".join(c for c in phone.strip() if c.isdigit() or c == "+")
    is_intl = cleaned.startswith("+")
    digits = cleaned[1:] if is_intl else cleaned
    if not digits or len(digits) < 5 or len(digits) > 15 or not payload_text:
        raise ValueError("أدخل رقم هاتف صالحاً (من 5 إلى 15 رقماً) ومحتوى نصياً.")

    toa = 0x91 if is_intl else 0x81
    da_bcd = encode_semi_octets(digits)

    gsm7_bytes = encode_gsm7_septets(payload_text) if encoding_pref in ("auto", "gsm7") else None
    if encoding_pref == "gsm7" and gsm7_bytes is None:
        raise ValueError("النص يحتوي على رموز غير مدعومة في GSM 7-bit؛ اختر UCS2.")

    use_gsm7 = encoding_pref == "gsm7" or (encoding_pref == "auto" and gsm7_bytes is not None and len(payload_text) <= 160)

    raw = bytearray([
        0x00,
        0x11,
        0x00,
        len(digits) & 0xFF,
        toa,
        *da_bcd,
        0x00,
    ])

    if use_gsm7 and gsm7_bytes is not None:
        dcs = 0x10
        dcs_label = "Class 0 + GSM 7-bit"
        raw.extend([dcs, 0xAA, len(payload_text) & 0xFF, *gsm7_bytes])
    else:
        dcs = 0x18
        dcs_label = "Class 0 + UCS2"
        ud_bytes = payload_text.encode("utf-16-be")
        if len(ud_bytes) > 140:
            raise ValueError("طول البيانات تجاوز الحد المسموح لحزمة واحدة (140 بايت).")
        raw.extend([dcs, 0xAA, len(ud_bytes) & 0xFF, *ud_bytes])

    raw_bytes = bytes(raw)
    return {
        "phone": cleaned,
        "payload": payload_text,
        "dcs_hex": f"0x{dcs:02X}",
        "dcs_label": dcs_label,
        "byte_length": len(raw_bytes),
        "raw": raw_bytes,
        "hex": "".join(f"{b:02X}" for b in raw_bytes),
    }


def is_safe_endpoint(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False, "يجب أن يبدأ رابط البوابة بـ http:// أو https://."
    try:
        addr_info = socket.getaddrinfo(parsed.hostname, None)
        for item in addr_info:
            ip = ipaddress.ip_address(item[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False, "يُمنع توجيه الطلبات إلى عناوين محلية أو داخلية."
    except OSError:
        return False, "تعذر التحقق من مضيف البوابة."
    return True, ""


def is_authorized(req) -> bool:
    provided = req.headers.get("X-Dashboard-Key", "")
    if not provided:
        return True
    return hashlib.sha256(provided.encode()).hexdigest() == DASHBOARD_PASSWORD_HASH


HTML_PANEL = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>أداة بناء واختبار حزم SMS PDU</title>
  <style>
    body{background:#090d16;color:#e2e8f0;font-family:Tahoma,Arial,sans-serif;padding:18px}
    .box{max-width:900px;margin:auto;background:#111827;border:1px solid #1e293b;border-radius:12px;padding:18px}
    h2{margin-top:0;color:#38bdf8}
    label{display:block;margin-top:10px;margin-bottom:4px;font-weight:bold;color:#cbd5e1}
    input,select,textarea{width:100%;box-sizing:border-box;padding:10px;border-radius:8px;border:1px solid #334155;background:#090d16;color:#fff;font-size:14px}
    textarea{min-height:70px}
    .grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}
    .btns{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
    button{padding:11px 16px;border:none;border-radius:8px;background:#0284c7;color:#fff;font-weight:bold;cursor:pointer}
    .green{background:#16a34a}
    .amber{background:#d97706}
    .out{background:#05080f;border:1px solid #334155;padding:12px;border-radius:8px;margin-top:14px;white-space:pre-wrap;word-break:break-all;font-family:monospace}
  </style>
</head>
<body>
  <div class="box">
    <h2>⚡ أداة بناء واختبار حزم SMS PDU</h2>

    <div class="grid2">
      <div>
        <label>رقم الهدف:</label>
        <input id="phone" placeholder="+967770000000" style="direction:ltr;text-align:left">
      </div>
      <div>
        <label>نوع الأمر:</label>
        <select id="cmd_name">
          <option value="STATUS">STATUS</option>
          <option value="PING">PING</option>
          <option value="SYNC">SYNC</option>
          <option value="ALERT">ALERT</option>
          <option value="CUSTOM">CUSTOM</option>
        </select>
      </div>
    </div>

    <div class="grid2">
      <div>
        <label>معامل الأمر (اختياري):</label>
        <input id="cmd_args" placeholder="mode=fast" style="direction:ltr;text-align:left">
      </div>
      <div>
        <label>الترميز:</label>
        <select id="encoding">
          <option value="auto">تلقائي (GSM-7 / UCS2)</option>
          <option value="gsm7">GSM 7-bit (DCS 0x10)</option>
          <option value="ucs2">UCS2 16-bit (DCS 0x18)</option>
        </select>
      </div>
    </div>

    <label>ملاحظة مرافقة (اختياري):</label>
    <textarea id="note_text" placeholder="ملاحظة اختبارية..."></textarea>

    <div class="grid2">
      <div>
        <label>رابط بوابة الاختبار (اختياري):</label>
        <input id="endpoint" placeholder="https://example.org/gateway" style="direction:ltr;text-align:left">
      </div>
      <div>
        <label>مفتاح التحقق للبوابة (اختياري):</label>
        <input id="dash_key" type="password" placeholder="أدخل كلمة المرور عند الحاجة">
      </div>
    </div>

    <div class="btns">
      <button class="green" onclick="generatePacket()">توليد الحزمة</button>
      <button class="amber" onclick="copyHex()">نسخ Hex</button>
      <button onclick="dispatchPacket()">إرسال إلى البوابة</button>
    </div>

    <div id="result" class="out">جاهز لتوليد الحزمة.</div>
  </div>

  <script>
    let lastId = null;
    let lastHex = "";

    function getHeaders(extra = {}) {
      const key = document.getElementById('dash_key').value;
      const headers = {'Content-Type': 'application/json', ...extra};
      if (key) headers['X-Dashboard-Key'] = key;
      return headers;
    }

    async function generatePacket() {
      const payload = {
        phone: document.getElementById('phone').value.trim(),
        cmd_name: document.getElementById('cmd_name').value,
        cmd_args: document.getElementById('cmd_args').value.trim(),
        encoding: document.getElementById('encoding').value,
        note_text: document.getElementById('note_text').value.trim()
      };
      const res = await fetch('/api/generate_cmd_zeroclick', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        document.getElementById('result').textContent = data.error || 'تعذر التوليد.';
        return;
      }
      lastId = data.id;
      lastHex = data.hex;
      document.getElementById('result').innerHTML =
        `المعرّف: ${data.id}\n` +
        `الهدف: ${data.phone}\n` +
        `المحتوى: ${data.payload}\n` +
        `الترميز: ${data.dcs_label} (${data.dcs_hex}) | الحجم: ${data.byte_length} بايت\n` +
        `Hex: ${data.hex}\n` +
        `<a href="/download_cmd_pdu/${data.id}" style="color:#38bdf8">[تنزيل ملف .bin]</a>`;
    }

    async function copyHex() {
      if (!lastHex) return;
      await navigator.clipboard.writeText(lastHex);
      document.getElementById('result').textContent += '\nتم نسخ Hex.';
    }

    async function dispatchPacket() {
      if (!lastId) {
        await generatePacket();
        if (!lastId) return;
      }
      const endpoint = document.getElementById('endpoint').value.trim();
      const res = await fetch('/api/dispatch_cmd_pdu', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({id: lastId, endpoint})
      });
      const data = await res.json();
      document.getElementById('result').textContent += `\n${data.message || data.error}`;
    }
  </script>
</body>
</html>"""


@app.route("/", methods=["GET"])
def home():
    return HTML_PANEL


def find_packet(pkt_id: str) -> dict | None:
    for item in PACKETS_STORE:
        if item["id"] == pkt_id:
            return item
    return None


@app.route("/api/generate_cmd_zeroclick", methods=["POST"])
def api_generate_cmd_zeroclick():
    if not is_authorized(request):
        return jsonify({"error": "صلاحية الوصول غير صحيحة."}), 401

    data = request.get_json(silent=True) or {}
    payload_text = compose_command_payload(
        str(data.get("cmd_name", "PING")),
        str(data.get("cmd_args", "")),
        str(data.get("note_text", "")),
    )
    try:
        pkt = build_class0_command_packet(
            str(data.get("phone", "")),
            payload_text,
            str(data.get("encoding", "auto")),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    pkt_id = hashlib.sha256(
        f"{datetime.datetime.now(datetime.timezone.utc).isoformat()}-{len(PACKETS_STORE)}".encode()
    ).hexdigest()[:12]

    record = {
        "id": pkt_id,
        "time": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        **pkt,
    }
    PACKETS_STORE.append(record)
    return jsonify({k: v for k, v in record.items() if k != "raw"})


@app.route("/download_cmd_pdu/<pkt_id>", methods=["GET"])
def download_cmd_pdu(pkt_id: str):
    pkt = find_packet(pkt_id)
    if not pkt:
        return "Not found", 404
    return Response(
        pkt["raw"],
        mimetype="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename=pdu_{pkt['id']}.bin"},
    )


@app.route("/api/dispatch_cmd_pdu", methods=["POST"])
def api_dispatch_cmd_pdu():
    if not is_authorized(request):
        return jsonify({"error": "صلاحية الوصول غير صحيحة."}), 401

    data = request.get_json(silent=True) or {}
    pkt_id = str(data.get("id", "")).strip()
    endpoint = str(data.get("endpoint", "")).strip()

    pkt = find_packet(pkt_id)
    if not pkt:
        return jsonify({"error": "الحزمة غير موجودة."}), 404

    if not endpoint:
        return jsonify({"message": "الحزمة جاهزة للتنزيل أو النسخ؛ أدخل رابط بوابة لاختبار الإرسال."})

    safe, reason = is_safe_endpoint(endpoint)
    if not safe:
        return jsonify({"error": reason}), 400

    try:
        req = url_request.Request(
            endpoint,
            data=pkt["raw"],
            headers={
                "Content-Type": "application/octet-stream",
                "X-Target-Phone": pkt["phone"],
            },
            method="POST",
        )
        with url_request.urlopen(req, timeout=8) as resp:
            return jsonify({"message": f"تم الإرسال إلى البوابة (HTTP {resp.status})."})
    except Exception as exc:
        return jsonify({"error": f"تعذر الاتصال بالبوابة: {exc}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
