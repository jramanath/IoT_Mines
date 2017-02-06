"""
Ce script permet d'aggréger les données de tous les capteurs utilisés
"""
from bluepy.btle import Scanner
from bluepy import sensortag

import os,sys
import argparse
from time import gmtime, strftime, sleep

import numpy as np
import requests,json

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')
s3 = boto3.resource('s3')

#On se connecte au serveur S3

def autopairing(timeout=10.0,devices=None):
    '''Autoscan BLE for neighbouring advertising Sensortag and turn on environmental sensors
    '''
    if devices is None: # Auto scan if no sensors are provided
        BLE=Scanner()
        print "scanning in progress \n"
        devices = BLE.scan(timeout)

    Sensors=[]
    dev_list='Liste : \n'
    for dev in devices:
        if 'SensorTag' in str(dev.getValueText(9)):
            print "Device %s (SensorTag), RSSI=%d dB" % (dev.addr, dev.rssi)
            dev_list=dev_list +"Device %s (SensorTag), RSSI=%d dB \n" % (dev.addr, dev.rssi)
            sleep(1)
            idx=0
            while True:
                try:
                    tag=sensortag.SensorTag(dev.addr)
                    tag.addr=dev.addr
                    # Add here relevant sensors to enable at start. check from sensortag.py for more info
                    tag.lightmeter.enable()
                    tag.humidity.enable()
                    tag.IRtemperature.enable()
                    Sensors.append(tag)
                    break
                except Exception as e: # it happens the sensors failed to start for some reasons. Retrying is usually enough to connect.
                    print e
                    print "Sensor disconnected, retrying"
                    idx+=1
                    sleep(.5)
                    pass
                if idx>5: # if it's not, then you have to remove this sensors from the list
                    print "Forgetting about THAT sensor"
                    break
                # if everything goes well, add the sensors to the list

    del devices
    return Sensors


def acquire(Sensors):
    '''Read sensors measured value and return a data dictionary

    Warning : this is not error proof : any disconnection from one of the sensor make the full function to crash.
    '''

    data={}
    data['LocalTime']=gmtime()
    for tag in Sensors:
        meas={}
        loc=tag.IRtemperature.read()
        meas['IRamb']=loc[0] # IR Temperature in degC
        meas['IRobj']=loc[1] # IR Temperature in degC
        loc=tag.humidity.read()
        meas['T']=loc[0] # T in degC
        meas['RH']=loc[1] #HR in %
        meas['Illum']=tag.lightmeter.read() # Illuminance
        # Add relevant measurement here.

        # Adding the measured value to the globale dict.
        data[tag.addr]=meas
    #data["heure"]=gmtime()...
#on met l'heure une seule fois dans le json des mesures de tous les capteurs

    return data



def sendJson(data):
    """send JSON to Amazon bucket """
#Partie sur if not session enlevée
    last_data=open('unsent_data.json', 'w') # create back-up file
    '''last_data.write('')
    last_data.close() #pourquoi on le ferme mtnt'''
    try :
        with open('unsent_data.json', 'a+') as last_data:
            last_data.write(json.dumps(data, indent = 4)) # save data in case of something bad happen
    s3_client.upload_file('last_data.txt', 'sensortag','last_data.txt')

     '''for text in data_:
            res=self._session.post(self.url,data=text) # adapt to fit your server API ! (this is for Amazon S3 server)

            if res.status_code != 200:
                common.display('HTTP : ' +res.content)
                break
        if res.status_code == 200:
            common.display('data sent to server')
            last_data=open('unsent_data.json', 'w')
            last_data.write('')
            last_data.close()

    except Exception as e:
        print('HTTP : ' + str(e.message)) # not crashing if error'''

    finally:
        last_data.close()


def dispData(verbose,data=None):
        ''' display data if verbose is True and data are provided'''
    if not verbose or data is None:
        return
    else:
        first=True
        for k in data.keys():
            if not 'LocalTime' in k:
                if first :
                    print  strftime("%d %b %Y %H:%M:%S", data['LocalTime'])+'  :  ' + str(data[k].keys())
                    first=False
                print k+ '  :  '+str([data[k][k2] for k2 in data[k].keys()])

def main():
    if not os.geteuid() == 0:
        sys.exit('Script must be run as root')
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', action='store', default=14400,type=int, help="Number of times to loop data")
    parser.add_argument('-t',action='store',type=float, default=1., help='time between polling')
    parser.add_argument('-p',action='store',type=float,default=5.,help='pause before starting the measurement')
    parser.add_argument('-v', action='store_true', default=True,help='print out measurement result every iteration')
    arg = parser.parse_args(sys.argv[1:])

    # init
    print "Init"
    sleep(arg.p)
    sensors=autopairing()
    print "Done"
    # main loop / no error managment
    print "starting measurements"
    for i in range(arg.n):
        data= acquire(sensors)
        dispData(arg.v,data)
#        sendJson(data) # Here is an example sending data to an API.
        sleep(arg.t)






if __name__ == '__main__':
    main()
