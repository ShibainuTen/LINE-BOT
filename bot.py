from flask import Flask, request, abort
import linebot
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageMessage, MessageEvent, TextMessage, TextSendMessage
import base64
import requests, json, os, io
from io import BytesIO
from PIL import Image
import numpy as np
from keras.preprocessing.image import img_to_array, load_img
from keras.models import load_model

print('***ライブラリのインポート***')

app = Flask(__name__)

line_bot_api = linebot.LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = linebot.WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

header = {
    "Content-Type": "application/json",
    "Authorization":  "Bearer " + os.environ['LINE_CHANNEL_ACCESS_TOKEN']
}

# model はグローバルで宣言し、初期化しておく
model = None

print('****前準備****')
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

    print('****コールバック****')

# テキストを受け取る部分
@handler.add(MessageEvent, message=TextMessage)
def handler_message(event):
     line_bot_api.reply_message(
         event.reply_token,
         TextSendMessage('画像を送ってね'))


# 画像を受け取る部分
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    print("handle_image:", event)

    message_id = event.message.id
    getImageLine(message_id)

    try:
        image_text = get_text_by_ms(image_url=getImageLine(message_id))

        messages = [
            TextSendMessage(text=image_text),
        ]

        line_bot_api.reply_message(event, messages)

    except Exception as e:
        line_bot_api.reply_message(event, TextSendMessage(text='エラーが発生しました'))

def getImageLine(id):

    line_url = 'https://api.line.me/v2/bot/message/' + id + '/content/'

    # 画像の取得
    result = requests.get(line_url, headers=header)
    print(result)

    # 画像の保存
    im = Image.open(BytesIO(result.content))
    filename = '/tmp/' + id + '.jpg'
    print(filename)
    im.save(filename)

    return filename


def get_text_by_ms(image_url):

    # 90行目で保存した url から画像を書き出す。
    img = Image.open(image_url)
    img_byte = im.read()
    img_content = base64.b64encode(img_byte)
    img = img_to_array(load_img(img_content, target_size=(256,256)))
    detect_who(img)
    
    text = face
    return text

def detect_who(img):

    face=""
    # グローバル変数を取得する
    global model

    # 一番初めだけ model をロードしたい
    if model is None:
        model = load_model('./acc_77.h5')
    
    # 0-1に変換
    img_nad = (img_to_array(img)/255)

    # 4次元配列に
    img_nad = img_nad[None, ...]
    
    predict = model.predict(img_nad)
    faceNumLabel=np.argmax(predict)
    
    # 「判定」
    if faceNumLabel == 0:
        face = "コーギー"
    elif faceNumLabel == 1:
        face = "柴犬"
    elif faceNumLabel == 2:
        face = "パグ"
    elif faceNumLabel == 3:
        face = "キャバリア"
    elif faceNumLabel == 4:
        face = "チワワ"
    elif faceNumLabel == 5:
        face = "ダックスフンド"
    elif faceNumLabel == 6:
        face = "プードル" 
    
    return face

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
