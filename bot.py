from flask import Flask, request, abort
from pathlib import Path
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
import gc

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
     print("****handle_message****:", event)
     line_bot_api.reply_message(event.reply_token,TextSendMessage('コーギー、パグ、柴犬、キャバリア、チワワ、ダックス、プードル'))

# 画像を受け取る部分
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    print("****handle_image****:", event)
    
    message_id = event.message.id
    
    # message_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(message_id)
    SRC_IMAGE_PATH = "static/images/{}.jpg"
    save_path = Path(SRC_IMAGE_PATH.format(message_id)).absolute()

    with open(save_path, "wb") as f:
        for chunk in message_content.iter_content():
            f.write(chunk)
    
    image_text = get_text_by_ms(event,save_path)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=image_text))
    
def get_text_by_ms(event,result):

    # 90行目で保存した url から画像を書き出す。
    img = img_to_array(load_img(result, target_size=(256,256)))
    face=""
    # グローバル変数を取得する
    global model

    # model をロードする
    model = load_model('./acc_89-.h5')
    
    # 0-1に変換
    img_nad = (img_to_array(img)/255)

    # 4次元配列に
    img_nad = img_nad[None, ...]
    
    predict = model.predict(img_nad)
    print('***predict***',predict)
    faceNumLabel=np.argmax(predict)
    score = np.max(predict)
    score = '{:.2%}'.format(score)
    if score > 70 :
        text = detect_who(faceNumLabel)
        text = text ,':' , score , '%'
    else:
        text = '犬じゃない気がします・・・'
    print('***text***',text)
    
    del img_nad,img,model
    gc.collect()
    
    return text

def detect_who(faceNumLabel):
   
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
    
    print('****face****',face)
    return face

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
