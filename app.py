from flask import Flask, request
import openai
import requests

app = Flask(__name__)

# ใส่คีย์ที่คุณได้มา
LINE_CHANNEL_ACCESS_TOKEN = 'ใส่ LINE Access Token'
OPENAI_API_KEY = 'ใส่ OpenAI API Key'

openai.api_key = OPENAI_API_KEY

@app.route("/webhook", methods=['POST'])
def webhook():
    body = request.get_json()
    events = body['events']
    
    for event in events:
        if event['type'] == 'message' and 'text' in event['message']:
            user_message = event['message']['text']
            reply_token = event['replyToken']

            # เรียก ChatGPT
            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_message}]
            )
            gpt_reply = completion.choices[0].message.content

            # ตอบกลับ LINE
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
            }
            reply_body = {
                "replyToken": reply_token,
                "messages": [{"type": "text", "text": gpt_reply}]
            }
            requests.post("https://api.line.me/v2/bot/message/reply",
                          headers=headers, json=reply_body)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)

