import cv2
import threading
import datetime
import time
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

print(cv2.__version__)

class CameraThread(threading.Thread):
    def __init__(self, camera_url, capture):
        threading.Thread.__init__(self)
        self.camera_url = camera_url
        self.stop_camera = False
        self.capture = capture
        self.frame = None

    def run(self):
        cap = cv2.VideoCapture(self.camera_url)
        if not cap.isOpened():
           print("Error opening video stream or file")
        else:
            print("camera is opened")
        while not self.stop_camera:
            ret, frame = cap.read()
            if ret:
                self.frame = frame
            else:
                break
        cap.release()

    def get_frame(self):
        return self.frame
    
    def set_capture(self,capture):
        self.capture = capture

    def stop(self):
        self.stop_camera = True
        self.join()
        print("thread is closed")
    

# Create camera threads
camera_threads = []
camera_urls = ["rtsp://admin:rtspuno10@192.168.7.142:80/0","rtsp://admin:rtspuno10@192.168.7.143:80/0","rtsp://admin:rtspuno10@192.168.7.144:80/0"]

@app.route("/")
def hello_world():
    
    return "<h1>Local App for IPCAM</h1>"

@app.route("/snapshot",methods=['GET'])
def snap():
    result = []
    cap_url = request.args.get('urlparameter')
    url_list = cap_url.split(",")
    path = request.args.get('filename')
    time_now = request.args.get('timestamp')
    os.chdir(path)
    # print("url = ",url)
    # print("path = ",path)
    iswrite = False
    responsestate = ""
   
    current_time = datetime.datetime.fromtimestamp(time.time())
    timestring = current_time.strftime("%Y%m%d%H%M%S_%f")
    start_time = current_time.strftime("%Y/%m/%d/%H:%M:%S.%f")
    filename =""
    for i, camera_thread in enumerate(camera_threads):
        # if(camera_thread.camera_url == cap_url):
        if camera_thread.camera_url in url_list:
            frame = camera_thread.get_frame()
            filename =  "image_" + str(i) + "_"+ timestring + ".jpg"
            print("filename = ",filename)
            iswrite = cv2.imwrite(filename,frame)
            if(iswrite):
                responsestate = "success"
            end_time = datetime.datetime.fromtimestamp(time.time())
            endtimestring = end_time.strftime("%Y/%m/%d/%H:%M:%S.%f")
            data = {
                'timerequest':start_time,
                'timestamp':endtimestring,
                'filename':filename,
                'responseStatue':responsestate,
                'responseCode':'100100'
            }
            result.append(data)
    
    return jsonify(result)
@app.route("/option",methods=['GET'])
def SettingUrl():
    arr_url = request.args.get('cameraurl')
    url_list = arr_url.split(",")

    # for camera_thread in camera_threads:
    #     camera_thread.stop()

    for url in url_list:
        camera_thread = CameraThread(url,False)
        camera_thread.start()
        camera_threads.append(camera_thread)    

    print(url_list)

    return "<h1>Local App for IPCAM</h1>"




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)