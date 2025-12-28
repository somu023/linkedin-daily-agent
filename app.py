import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# WhatsApp Cloud API Configuration
WHATSAPP_TOKEN = os.environ.get('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.environ.get('PHONE_NUMBER_ID')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN', 'linkedin_daily_agent_verify')

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'running',
        'app': 'LinkedIn Daily Agent',
        'whatsapp_api': 'active'
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Webhook verification
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return 'Forbidden', 403
    
    elif request.method == 'POST':
        # Handle incoming messages
        data = request.get_json()
        print(f"Received webhook: {data}")
        
        # Send auto-reply
        try:
            if 'messages' in data['entry'][0]['changes'][0]['value']:
                message = data['entry'][0]['changes'][0]['value']['messages'][0]
                from_number = message['from']
                message_body = message['text']['body']
                
                # Send response
                send_message(from_number, f"Echo: {message_body}")
        except Exception as e:
            print(f"Error processing message: {e}")
        
        return jsonify({'status': 'received'}), 200

def send_message(to_number, message):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {WHATSAPP_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': to_number,
        'type': 'text',
        'text': {'body': message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
