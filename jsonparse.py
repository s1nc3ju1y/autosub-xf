import json
import shelve
from pprint import pprint

message = {'code': 0,
           'data': {'result': {'bg': 0,
                               'ed': 0,
                               'ls': False,
                               'sn': 15,
                               'vad': {'ws': [{'bg': 5804, 'ed': 5996, 'eg': 70.65}]},
                               'ws': [{'bg': 5817, 'cw': [{'sc': 0, 'w': ' Iran'}]},
                                      {'bg': 5917, 'cw': [{'sc': 0, 'w': ' or'}]},
                                      {'bg': 5941, 'cw': [{'sc': 0, 'w': ' even'}]},
                                      {'bg': 5961, 'cw': [{'sc': 0, 'w': ' prevent'}]}]},
                    'status': 1},
           'message': 'success',
           'sid': 'iat00076046@dx17093fc0cf1a493802'}

json_str = json.dumps(message)
# print(json_str)
data = json.loads(json_str)["data"]["result"]["ws"]
result = ""
for i in data:
    for w in i["cw"]:
        result += w["w"]
vad = json.loads(json_str)["data"]["result"]["vad"]
item = vad["ws"][0]
bg = item["bg"]
ed = item["ed"]
# 构造一个json对象
words = {
    "bg": bg,
    "ed": ed,
    "w": result
}
# print(words)
with shelve.open('lines.db') as db:
    file_name = 'Audio/part_sound_6.wav'
    pprint(db[file_name])
