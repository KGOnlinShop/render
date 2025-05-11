from flask import Flask, request
import requests
import openai

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_LINE_CHANNEL_ACCESS_TOKEN'
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'

@app.route('/webhook', methods=['POST'])
def webhook():
    events = request.json['events']
    for event in events:
        if event['type'] == 'message':
            user_text = event['message']['text']
            reply_token = event['replyToken']
            
            # ส่งข้อความไปยัง ChatGPT
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_text}]
            )
            reply_text = response.choices[0].message['content']
            
            # ตอบกลับผู้ใช้ใน LINE
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
            }
            body = {
                'replyToken': reply_token,
                'messages': [{'type': 'text', 'text': reply_text}]
            }
            requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=body)
    return 'OK'
