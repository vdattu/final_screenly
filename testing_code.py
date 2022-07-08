import requests
import time
url = "https://ph.mysticalmist.ml/ads"

payload={'metadata': '{"cameraId":"IVISUSA1014C1","timeStamp":1644474393741,"objDetectionList":[{"label":"person","top":171,"width":70,"left":157,"height":279,"score":0.881486},{"label":"person","top":240,"width":98,"left":245,"height":317,"score":0.87694},{"label":"person","top":305,"width":64,"left":484,"height":269,"score":0.839932},{"label":"person","top":175,"width":76,"left":426,"height":203,"score":0.835012},{"label":"person","top":90,"width":61,"left":301,"height":100,"score":0.706838}]}'}
files=[
  ('imagedata',('2061858.jpg',open('people.jpg','rb'),'image/jpeg'))
]
headers = {}
while True:
    time.sleep(0.5)
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
    except:
        print("Exception")
    print(response.text)
