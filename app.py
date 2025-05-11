import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI

# โหลดค่าจาก Environment Variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ตรวจสอบว่า ENV ถูกตั้งครบ
if not all([LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, OPENAI_API_KEY]):
    raise Exception("Missing environment variables.")

# สร้าง instance ของ Flask, LINE และ OpenAI
app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/webhook", methods=['POST'])
def webhook():
    # ป้องกัน verify webhook จาก LINE ที่ไม่ส่ง signature มา
    signature = request.headers.get('X-Line-Signature', None)
    body = request.get_data(as_text=True)

    if signature is None:
        return 'OK', 200  # ให้ LINE Developer Verify ผ่านได้

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK', 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    try:
        # เรียก OpenAI Chat API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response.choices[0].message.content.strip()

    except Exception as e:
        reply_text = "ขออภัย เกิดข้อผิดพลาดในการติดต่อกับ ChatGPT."

    # ส่งข้อความกลับไปยัง LINE
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

