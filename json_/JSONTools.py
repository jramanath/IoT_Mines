"""Collection of function to work with json.
"""
# pylint: disable-msg=C0326

import os,time,datetime
import gzip,json
import numpy as np

def merge_TF_files(folder):
    """This script agregate json files found a specified folder, to output an agregagated array, or a set of json.

    The JSON MUST have the following template (but the numer of sensortag can be less than 4 ):
    {
    "thetime": "Thu, 01 Sep 2016 09:56:35 GMT",
     "c02": 663.0,
     "MC350": {
        "b0:b4:48:c8:27:85": [28.03125, 23.09375, 67.0, 28.2196044921875, 37.9150390625, 0.5700000000000001],
        "b0:b4:48:c8:50:83": [28.9375, 22.15625, 60.6, 28.9447021484375, 35.3271484375, 40.410000000000004],
        "b0:b4:48:c0:aa:07": [28.25, 23.09375, 60.0, 28.3001708984375, 50.848388671875, 34.13],
        "b0:b4:48:c0:4b:86": [24.9375, -71.75, 60.300000000000004, 28.88427734375, 52.35595703125, 0.72]
        },
    "time": "2016-09-01T09:56:40+02:00"
    }
    Thetime : str, heure local (UTC)
    C02 : float, valeur de CO2 en ppm
    MC350 : dict :  clés : hw adress of each connected sensor :
    			content : array -> [ IR Temperature obj[inutile], IR temperature ambient[inutile], sound level [dBa], Temperature[°C], RH [%], luminosité [lux] ]
    time : server time (timestamp when the json is received by the server)

    """
    output=np.zeros((1,26))
    allFiles = os.listdir(folder)
    for filename in allFiles :
        print filename
        with gzip.open(folder+'\\'+filename) as data_file:
            row= data_file.readline()
            try:
                data = json.loads(row)
            except:
                print 'error loading '+filename
                continue
            local=np.zeros((26,1))
            try :
                local[0]=time.mktime(datetime.datetime.strptime(data['thetime'], '%a, %d %b %Y %H:%M:%S GMT').timetuple())+1*60*60 # Warning for UTC to local time conversion here
            except ValueError :
                local[0]=time.mktime(datetime.datetime.strptime(data['thetime'], '%a, %d %b %Y %H:%M:%S').timetuple())+1*60*60
            except Exception as e :
                print e
                pass

            local[1]=data['c02']
            meas=data['MC350']
            i=0
            for iD in meas:
                tmp=meas[iD]
                local[2+i]=tmp[0]
                local[6+i]=tmp[1]
                local[10+i]=tmp[2]
                local[14+i]=tmp[3]
                local[18+i]=tmp[4]
                local[22+i]=tmp[5]
                i+=1
                output=np.vstack((output,local.transpose()))
    output=np.delete(output,0,0)
    return output
