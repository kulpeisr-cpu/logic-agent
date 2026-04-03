import os
from flask import Flask, request, jsonify, render_template_string
from anthropic import Anthropic

app = Flask(__name__)
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """Ты — агент логического анализа. Анализируй аргументы по четырём законам логики:
1. Закон тождества
2. Закон непротиворечия
3. Закон исключённого третьего
4. Закон достаточного основания

Для каждого аргумента: перефразируй, проверь по каждому закону, укажи бреши, предложи исправление."""

HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Агент логики</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:sans-serif;background:#f5f5f5;display:flex;flex-direction:column;height:100vh}
#header{padding:16px 20px;background:#fff;border-bottom:1px solid #e0e0e0}
#header h1{font-size:16px;font-weight:600}
#header p{font-size:13px;color:#888;margin-top:2px}
#chat{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:75%;padding:10px 14px;border-radius:12px;font-size:14px;line-height:1.5;white-space:pre-wrap}
.user{align-self:flex-end;background:#0066ff;color:#fff}
.agent{align-self:flex-start;background:#fff;border:1px solid #e0e0e0}
.thinking{color:#aaa;font-style:italic}
#input-area{padding:16px 20px;background:#fff;border-top:1px solid #e0e0e0;display:flex;gap:10px}
#input-area textarea{flex:1;padding:10px 12px;border:1px solid #ddd;border-radius:8px;font-size:14px;resize:none;height:44px;font-family:sans-serif}
#input-area button{padding:0 20px;background:#0066ff;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
#input-area button:disabled{background:#ccc}
</style></head>
<body>
<div id="header"><h1>Агент логического анализа</h1><p>Приведи аргумент — найду бреши по 4 законам логики</p></div>
<div id="chat"></div>
<div id="input-area">
<textarea id="input" placeholder="Введи свой аргумент..." onkeydown="handleKey(event)"></textarea>
<button id="btn" onclick="send()">Отправить</button>
</div>
<script>
let history=[];
function handleKey(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}}
function addMsg(text,role){const chat=document.getElementById('chat');const div=document.createElement('div');div.className='msg '+role;div.textContent=text;chat.appendChild(div);chat.scrollTop=chat.scrollHeight;return div;}
async function send(){
const input=document.getElementById('input');
const btn=document.getElementById('btn');
const text=input.value.trim();
if(!text)return;
input.value='';btn.disabled=true;
addMsg(text,'user');
history.push({role:'user',content:text});
const t=addMsg('Анализирую...','agent thinking');
const res=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:history})});
const data=await res.json();
t.remove();
addMsg(data.reply,'agent');
history.push({role:'assistant',content:data.reply});
btn.disabled=false;input.focus();
}
</script>
</body></html>"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return jsonify({"reply": response.content[0].text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
