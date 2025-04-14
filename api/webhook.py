from flask import Flask, request, Response
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# === Função para gerar resposta usando Gemini via API REST ===
def gerar_resposta_com_gemini(texto_usuario):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}"
    
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {
                "parts": [
                    {"text": texto_usuario}
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        try:
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Erro ao interpretar a resposta da Gemini."
    else:
        return f"Erro ao chamar a Gemini: {response.status_code} - {response.text}"

# === Função para enviar mensagem via Twilio ===
def send_whatsapp_message(to, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json"
    data = {
        "From": "whatsapp:+14155238886",
        "To": to,
        "Body": body
    }
    auth = (os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
    requests.post(url, data=data, auth=auth)

# === Rota principal para o webhook ===
@app.route("/api/webhook", methods=["POST"])
def webhook():
    msg = request.form.get("Body")
    from_number = request.form.get("From")

    if not msg:
        return Response(status=200)

    reply = gerar_resposta_com_gemini(msg)
    send_whatsapp_message(from_number, reply)
    return Response(status=200)

# (Opcional) Rota GET só para teste local
@app.route("/", methods=["GET"])
def home():
    return "Bot rodando localmente com Gemini e Twilio 🚀"