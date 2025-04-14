import os
from flask import Flask, request, Response
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurar Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

@app.route('/api/webhook', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body')
    from_number = request.form.get('From')

    if not incoming_msg:
        return Response(status=200)

    # Gera resposta com Gemini
    response = model.generate_content(incoming_msg)
    reply = response.text

    # Envia de volta via Twilio
    send_whatsapp_message(from_number, reply)

    return Response(status=200)

def send_whatsapp_message(to, body):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json"
    data = {
        'From': 'whatsapp:+14155238886',
        'To': to,
        'Body': body
    }
    auth = (os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    requests.post(url, data=data, auth=auth)