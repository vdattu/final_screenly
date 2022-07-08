import requests
from requests.structures import CaseInsensitiveDict
import threading
import os
import dot
import time
#import multiprocessing
# from screenly_ose import Screenly


def switch_asset(_id,dev,duration):
    Process_list=[thread.name for thread in threading.enumerate()]
    print(Process_list)
    if Process_list.count("running")==1:
        url = os.getenv("IVIS_SCREENLY_API1")+"{}".format(_id)+os.getenv("IVIS_SCREENLY_API2")+"{}".format(dev) #url = os.getenv("SCREENLY_CONTROL_API")+"asset&{}".format(_id)
        print(url)
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/json"
        resp = requests.get(url, headers=headers)
        time.sleep(duration+1)
    else:
        print("its passing")
        resp.status_code=200
        pass
    return resp.status_code






# class Testprocessing(object):
#     def __init__(self,_id,dev, interval=1):
#         self.interval = interval

#         process = processing.process(target=self.run, args=[_id,dev,])
#         process.daemon = True
#         process.start()
        
#     def run(self,_id,dev):
#         switch_asset(_id,dev)
        
    

