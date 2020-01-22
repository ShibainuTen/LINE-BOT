# coding=utf-8
import os
import re

import bs4
import flask
import linebot
import requests
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageMessage,ImageSendMessage

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
    
    image_id = event.message.id
    
    # image_idから画像のバイナリデータを取得
    message_content = line_bot_api.get_message_content(image_id)

    with open(Path(f"static/images/{message_id}.jpg").absolute(), "wb") as f:
        # バイナリを1024バイトずつ書き込む
        for chunk in message_content.iter_content():
            f.write(chunk)
            
    get_jagge(image_id)        

    
def get_jagge(image)
    """
    モデルの読み込み
    """
    
    

def get_reply(text):
    """
    返信内容を取得する
    :param text: 受信内容
    :return: 返信内容
    """
    return '****画像を送ってください！！！****'

if __name__ == '__main__':
    app.run()
