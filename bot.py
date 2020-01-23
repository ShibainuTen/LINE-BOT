# coding=utf-8
import re
import bs4
import flask
import linebot
import requests ,json, os, io, cv2
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage,ImageSendMessage
import numpy as np
from keras.preprocessing.image import img_to_array, load_img

"""
BOTっぽい何か
"""

# プログラム情報
__version__ = '1.0.2'

app = flask.Flask(__name__)
app.debug = bool(os.environ['DEBUG'])

api = linebot.LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])
handler = linebot.WebhookHandler(os.environ['LINE_CHANNEL_SECRET'])

# 日本語形態素解析 (Yahoo! JAPAN Webサービス) のURL
yahoo_url = 'http://jlp.yahooapis.jp/DAService/V1/parse'

# modelはグローバルで宣言し、初期化しておく
model = None

@app.route('/callback', methods=['POST'])
def callback():
    """
    コールバック
    """
    # リクエストメッセージボディをテキスト形式で取得
    body = flask.request.get_data(as_text=True)
    app.logger.info('Request body:' + body)

    # WebhookをHandle
    try:
        handler.handle(body, flask.request.headers['X-Line-Signature'])
    except InvalidSignatureError:
        flask.abort(400)

    return 'OK'


@handler.default()
def handle(event):
    """
    デフォルトハンドラ
    :param event: イベント
    """
    api.reply_message(event.reply_token, event.message)
    
# テキストイベント
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    メッセージハンドラ
    :param event: イベント
    """
    # 返信内容
    text = get_reply(event.message.text)

    # 返信する
    api.reply_message(event.reply_token, TextSendMessage(text))    

# 画像イベント
@handler.add(MessageEvent,message=ImageMessage)
def handle_image(event):
    """
    メッセージハンドラ
    :param event: イベント
    """    
    text = '*****識別中*****'
    
    # 返信する
    api.reply_message(event.reply_token, TextSendMessage(text))
    
    # 画像の取得
    print("handle_image:", event)

    message_id = event.message.id
    getImageLine(message_id)

    try:
        image_text = get_text_by_ms(image_url=getImageLine(message_id))

        messages = [
            TextSendMessage(text=image_text),
        ]

        reply_message(event, messages)

    except Exception as e:
        reply_message(event, TextSendMessage(text='エラーが発生しました'))

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
    image = (image_url)
    img = img_to_array(load_img(image,target_size=(256,256)))
    
    # 0-1に変換
    img_nad = (img_to_array(img)/255)

    # 4次元配列に
    img_nad = img_nad[None, ...]
    
    blood = get_jagge(img_nad)
    
    # 「この画像の判定結果は・・・」
    api.reply_message(event.reply_token, '****この画像の判定結果は****')
    
    if probability:
        # 返信する
        api.reply_message(event.reply_token, '{:.2%}'.format(probabilty))    
        
    text = blood
    return text
    
def get_jagge(img_nad)
    """
    モデルの読み込み
    """
    from keras.models import load_model
    
    
    # グローバル変数の取得
    global model
    
    blood = ""
    
    # 一番初めだけmodelロード
    if model is None:
        model = load_model('/acc_77-.h5')
    
    predict = model.predict(img_nad)
    
    # 表示したいクラス
    label = {0:'コーギー',1:'柴犬',2:'パグ',3:'キャバリア',4:'チワワ',5:'ダックスフンド',6:'プードル',}
    
    probability = np.max(predict)
    # 犬の確率判定 70%に満たない場合弾く
    if probability < 0.7:
        blood = '犬じゃないと思われます'
        return blood 
    else
        # 辞書型:labelからvalueを取得して値を返す
        blood = label.get(np.argmax(predict))
        
        return blood,probabilty

def get_reply(text):
    """
    返信内容を取得する
    :param text: 受信内容
    :return: 返信内容
    """
    return '****画像を送ってください！！！****'

if __name__ == '__main__':
    app.run()
