import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import json
import requests
import tempfile, shutil, os
from PIL import Image
from io import BytesIO

from linebot.models import (
    TemplateSendMessage, AudioSendMessage,
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, PostbackEvent, StickerMessage, StickerSendMessage, 
    LocationMessage, LocationSendMessage, ImageMessage, ImageSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__, static_url_path="/static")

UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'jpg', 'png','.jpeg'}

lineaccesstoken = '2NOT4Pl8K9kwpXqtgysrpbE478zcQk4UnT20Qee1jvVMNavFA0+T+Wh9ZpXx2wU6BSlx7bGkXnaf6G8V7nXtXTQ5awraPgf6KGZG7fUxvrAZWuSUVjFBnQL/QMOK3Lq5aG2iDpVpE1IXTuAq81QYQgdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(lineaccesstoken)

# APP CONFIGURATIONS
app.config['SECRET_KEY'] = 'opencv'  
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
# limit upload size upto 6mb
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)
            data={
                "processed_img":'static/downloads/'+filename,
                "uploaded_img":'static/uploads/'+filename
            }
            return render_template("index.html",data=data)  
    return render_template('index.html')


def process_file(path, filename):
    detect_object(path, filename)
    
def detect_object(path, filename):    
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    prototxt="ssd/MobileNetSSD_deploy.prototxt.txt"
    model ="ssd/MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(prototxt, model)
    image = cv2.imread(path)
    image = cv2.resize(image,(480,360))
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.60:
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            # print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

    cv2.imwrite(f"{DOWNLOAD_FOLDER}{filename}",image)

@app.route('/callback', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    
    # เชื่อมต่อกับ line 
    no_event = len(decoded['events'])
    for i in range(no_event):
            event = decoded['events'][i]
            event_handle(event)

    # เชื่อมต่อกับ dialogflow
    #intent = decoded["queryResult"]["intent"]["displayName"] 
    #text = decoded['originalDetectIntentRequest']['payload']['data']['message']['text'] 
    #reply_token = decoded['originalDetectIntentRequest']['payload']['data']['replyToken']
    #id = decoded['originalDetectIntentRequest']['payload']['data']['source']['userId']
    #disname = line_bot_api.get_profile(id).display_name
    #reply(intent,text,reply_token,id,disname)

    return '',200

def reply(intent,text,reply_token,id,disname):
    text_message = TextSendMessage(text="ทดสอบ")
    line_bot_api.reply_message(reply_token,text_message)

def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])
        if msg == "สวัสดี" :
          replyObj = TextSendMessage(text="เออ...ดีด้วย")
      elif msg == "กินข้าวไหม" :
          replyObj = TextSendMessage(text="ม่ายยยยละ")
      elif msg == "ไปเที่ยวกันไหม" :
          replyObj = TextSendMessage(text="ไปดิ")
      elif :
          replyObj = TextSendMessage(text=msg)
        line_bot_api.reply_message(rtoken, replyObj)
    elif msgType == "image":
        try:
            message_content = line_bot_api.get_message_content(event['message']['id'])
            i = Image.open(BytesIO(message_content.content))
            filename = event['message']['id'] + '.jpg'
            i.save(UPLOAD_FOLDER + filename)
            process_file(os.path.join(UPLOAD_FOLDER, filename), filename)

            url = request.url_root + DOWNLOAD_FOLDER + filename
            
            line_bot_api.reply_message(
                rtoken, [
                    TextSendMessage(text='Object detection result:'),
                    ImageSendMessage(url,url)
                ])    
    
        except:
            message = TextSendMessage(text="เกิดข้อผิดพลาด กรุณาส่งใหม่อีกครั้ง")
            line_bot_api.reply_message(event.reply_token, message)

            return 0

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

if __name__ == '__main__':
    app.run()
