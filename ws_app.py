from webAPI import Ws_Param
import shelve
from websocket import WebSocketApp
import base64
import json
import time
import ssl
import _thread as thread

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class MyAPP:
    def __init__(self, ws_param):
        self.param = ws_param
        self.url = self.param.create_url()
        self.lines = []
        self.ws = None

    # 收到websocket消息的处理
    def on_message(self, message):
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))

            else:
                data = json.loads(message)["data"]["result"]["ws"]
                status = json.loads(message)["data"]["status"]
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                if status != STATUS_LAST_FRAME:
                    vad = json.loads(message)["data"]["result"]["vad"]
                    info = vad["ws"][0]
                    words = {
                        "bg": info["bg"],
                        "ed": info["ed"],
                        "words": result
                    }
                    self.lines.append(words)
                # print("sid:%s call success!" % sid)
                # print(result)
        except Exception as e:
            print("receive msg,but parse exception:", e)

    # 收到websocket错误的处理
    def on_error(self, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(self):
        with shelve.open('lines.db') as db:
            db[self.param.AudioFile] = self.lines
        print("### closed ###")

    # 收到websocket连接建立的处理
    def on_open(self):
        def run(*args):
            frameSize = 8000  # 每一帧的音频大小
            interval = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(self.param.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:

                        d = {"common": self.param.CommonArgs,
                             "business": self.param.BusinessArgs,
                             "data": {"status": 0, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        d = json.dumps(d)
                        self.ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        self.ws.send(json.dumps(d))
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        self.ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    # 模拟音频采样间隔
                    time.sleep(interval)
            self.ws.close()

        thread.start_new_thread(run, ())

    def start(self):
        self.ws = WebSocketApp(self.url,
                               on_message=self.on_message,
                               on_error=self.on_error,
                               on_close=self.on_close)
        self.ws.on_open = self.on_open
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


audios = [f'Audio/part_sound_{i}.wav' for i in range(10)]
for i in range(2):
    wp = Ws_Param(APPID='5e2952b0', APIKey='414ea9ed44eda8363fbc10a5d6483ebc',
                  APISecret='9b7d258ee7d3bfbb014e0d2aa956652c',
                  AudioFile=audios[i])
    app = MyAPP(wp)
    app.start()
