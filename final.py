import numpy as np
import cv2
import time
from switch import switch_asset
import os
from PIL import Image
from watch import Watcher,TimeLimit
import requests,json
from requests.structures import CaseInsensitiveDict
import requests
from asset import get_dict
import pymysql
from datetime import datetime
from aws_rds import get_device,get_latlng,get_rule_id,get_asset_id,get_asset,get_cam,insert_details
from flask import Flask,request
import threading
import queue
app = Flask(__name__)


fifo_queue = queue.Queue()

semaphore = threading.Semaphore()

key=os.getenv('KEY')


def pin(status,no,ip):
    #url = os.getenv("RPI_PINS_API")+ status
    url = 'http://'+ip+':8083/api/pins/'+status
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = json.dumps({"pin":no})
    resp = requests.post(url, headers=headers, data=data)
    return resp.status_code





def temp(lat,lng,rng):
    day=time.strftime("%p")
    url = os.getenv('URL').format(lat,lng,key)
    try:
        c =int(float(requests.get(url).json()['current']['temp'])-273.15)
    except:
        c = 30
    if 1 <= c <= rng:
        a = 'R1'
        
    elif 1+rng <= c <= 2 * rng:
        a = 'R2'
        
    else:
        a = 'R3'
    
    return day+a


def sendtoserver(frame):
    imencoded = cv2.imencode(".jpg", frame)[1]
    file = {'image': ('image.jpg', imencoded.tobytes(), 'image/jpeg', {'Expires': '0'})}
    s = time.time()
    print(type(file))
    response_face = requests.post(os.getenv('MULTIFACE'), files=file, timeout=5)
    e = time.time()
    f = response_face.json()
    return f,round(e-s,2)

@app.route('/')
def sample():
    return "This application running"

    
@app.route('/ads', methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        data = request.form.get('metadata', '')
        npimg = np.fromfile(request.files['imagedata'], np.uint8)
        a = threading.Thread(target=inference_thread, args=[data,npimg])
        a.name = "main_t"
        a.setDaemon(True)
        fifo_queue.put(a)
        a.start()
        return "200"
    else:
        return "401"




def inference_thread(data,npimg):
    # w = Watcher(0)
    # t = TimeLimit()
    od = eval(data)
    #print(od,type(od))
    od_list = od['objDetectionList']
    camera_id = od['cameraId']
    print(camera_id)
    count = len(od_list)
    if count >= 1:
        try:
            cams = get_cam(camera_id)
            device_id = cams[1]
            device_data = get_device(device_id)
            latlng = get_latlng(device_data[2])
            #print(od_list)
            
            if eval(device_data[-2]):
                try:
                    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
                    agd,it = sendtoserver(img)
                    print("time for done image",it)
                    genders=[]
                    ages=[]
                    for i in agd:
                        genders.append(i['gender'])
                        ages.append(i['age'])

                    z = tuple(zip(genders,ages))
                    print("this is z",z)
                    g = genders.count('male') > genders.count('female')
                    #print(g)
                    ages_males = [ y for x, y in z if x  == 'male' ]
                    #print(ages_males)
                    m_classifications = [(i//device_data[-3] + 1) for i in ages_males]
                    ages_females = [ y for x, y in z if x  == 'female' ]
                    #print(ages_females)
                    f_classifications = [(i//device_data[-3] + 1) for i in ages_females]

                            
                    if g:
                        #print('its true')
                        m = max(m_classifications,key=m_classifications.count)
                        #print(m)
                        r1=temp(latlng[0],latlng[1],device_data[3])+'MC'+str(m)
                                
                    else:
                        #print('its false')
                        f = max(f_classifications,key=f_classifications.count)
                        r1=temp(latlng[0],latlng[1],device_data[3])+'FC'+str(f)
                except Exception as e:
                    #return "no faces detected"
                    print("no faces detected")
                    z = None
                    r1 = temp(latlng[0],latlng[1],device_data[3])

            else:
                z=None
                r1 = temp(latlng[0],latlng[1],device_data[3])

            print(r1)
            r_id = get_rule_id(r1)
            print(r_id)
            a_id = get_asset_id(device_data[2],r_id,device_data[1],device_id)
            asset = get_asset(a_id)
            #print(asset)
            print(device_data[0])
            data_dict = get_dict(device_data[0],asset)
            #print(data_dict)

            mimetype = str(data_dict['mimetype'])
            name = str(data_dict['name'])
            duration = int(data_dict['duration'])
            print(name,mimetype)
            insert_details(device_data[2],device_data[0],name,mimetype,count,z,r1)

            thread_list=[thread.name for thread in threading.enumerate()]
            print(thread_list,"list")
            ds = thread_list.count("main_t") 
            if ds >= 2:
                def countdown(t):
                    while t:
                        mins, secs = divmod(t, 60)
                        timer = '{:02d}:{:02d}'.format(mins, secs)
                        print(timer, end="\r")
                        time.sleep(1)
                        t -= 1
                    cc = threading.Thread(target = switch_asset,args = [asset,device_data[0],duration])
                    #thread_list.append("running")
                    fifo_queue.put(cc)
                    cc.name="running"
                    cc.start()
                    print(thread_list,"run_passed")
                if 2<= ds <=3:
                    countdown(duration)
                else:
                    print("passing")
                    pass



            else:
                #if t.check_value() > duration:
                cc = threading.Thread(target = switch_asset,args = [asset,device_data[0],duration])
                fifo_queue.put(cc)
                cc.name="running"
                cc.start()
                print(thread_list,"run")
            print(thread_list,"done")
            # time.sleep(duration+1)

            #return "its done"
            print("its done")
        except Exception as e:
            #return str(e)
            print(e)
    else:
        print("no object detected")

if __name__=="__main__":
    app.run(host='0.0.0.0')



