from linebot import LineBotApi, WebhookHandler # type: ignore
from linebot.exceptions import InvalidSignatureError # type: ignore
from linebot.models import MessageEvent, TextMessage, TextSendMessage # type: ignore
from flask import Flask, request, abort # type: ignore
import os
import google.generativeai as genai # type: ignore

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

app = Flask(__name__)

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

personality = ""
can_talk = True

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global personality, can_talk

    message_text = event.message.text

    if message_text.startswith("哈巴狗，"):
        if can_talk:
            response_text = model.generate_content(
                f"#zh-tw 你的設定是一隻哈巴狗，沒有名字也不會被賦予名字，會以一隻狗的口吻進行對話，並且講話偶爾加上「汪」，{personality}，請以這些設定進行以下對話：" + message_text[4:]
            )
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=response_text.text)
            )
    elif message_text.startswith("哈巴狗個性，"):
        personality = message_text[6:]
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="設定成功")
        )
    elif message_text == "哈巴狗安靜":
        can_talk = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="設定成功")
        )
    elif message_text == "哈巴狗聊天":
        can_talk = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="設定成功")
        )
    elif message_text == "哈巴狗再見":
        if event.source.type == "group":
            line_bot_api.leave_group(event.source.group_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)
