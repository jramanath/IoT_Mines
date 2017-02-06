#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ce script permet d'aggréger les données de tous les capteurs utilisés
"""
from bluepy.btle import Scanner
from bluepy import sensortag

import os,sys
import argparse
from time import gmtime, strftime, sleep
import datetime

import numpy as np
import requests,json
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from gpio import gpio

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

    data=[]
    for tag in Sensors:
        meas={}
        meas['ID']=tag.addr
        loc=tag.humidity.read()
        meas['Temperature']=loc[0] # T in degC
        meas['Humidite']=loc[1] #HR in %
        meas['Luminosite']=tag.lightmeter.read() # Illuminance
        meas['creation_datetime']=datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
        # Add relevant measurement here.
        # Adding the measured value to the globale dict.
        data.append(meas)
    return data


def sendJson_TI(input_json):
    """send JSON to Amazon bucket """

    s3_client = boto3.client('s3')
    s3 = boto3.resource('s3')
    current_time=gmtime()

    filename='TI'+ datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")

#    filename='/home/pi/data/'+filename
    try:
        with open(filename+'.txt', 'w+') as doc:
            doc.write(json.dumps(input_json))
        s3_client.upload_file(filename+'.txt', 'sensortag',filename+'.txt')

    except Exception as e:
        print('BOTO : ' + str(e.message)) # not crashing if error


def sendJson_windows(input_json):
    """send JSON to Amazon bucket """

    s3_client = boto3.client('s3')
    s3 = boto3.resource('s3')
    current_time=gmtime()

    filename='windows'+ datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
#    filename='/home/pi/data/'+filename
    try:
        with open(filename+'.txt', 'w+') as doc:
            doc.write(json.dumps(input_json))
        s3_client.upload_file(filename+'.txt', 'sensortag',filename+'.txt')

    except Exception as e:
        print('BOTO : ' + str(e.message)) # not crashing if error


def dispData(verbose,data=None):
    ''' display data if verbose is True and data are provided'''
    if not verbose or data is None:
        return
    else:
        first=True
        for meas in data:
                if first :
                    print  datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")+'  :  ' + str(meas.keys())
                    first=False
                print ' :'+str([meas[k2] for k2 in meas.keys()])


"""
def sendJson_error(input_json):
    #send an error JSON to Amazon bucket

    s3_client = boto3.client('s3')
    s3 = boto3.resource('s3')
    current_time=gmtime()
    filename=datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
#    filename='/home/pi/data/'+filename
    try:
        with open(filename+'.txt', 'w+') as doc:
            doc.write(json.dumps(input_json))
        s3_client.upload_file(filename+'.txt', 'sensortagerror',filename+'.txt')
    except Exception as e:
        print('BOTO : ' + str(e.message)) # not crashing if error

"""

def dispData(verbose,data=None):
    ''' display data if verbose is True and data are provided'''
    if not verbose or data is None:
        return
    else:
        first=True
        for meas in data:
                if first :
                    print  datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")+'  :  ' + str(meas.keys())
                    first=False
                print ' :'+str([meas[k2] for k2 in meas.keys()])

def old_main():
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


def main():
    print "Init"
    sensors=autopairing()
    print "Done"
    print "GPIO Init"
    #fixme : update pin number
    windows_dict={}
    windows=[gpio(12,'Tableau'), gpio(21,'Milieu'), gpio(17,'Fond')]
    for w in windows:
        windows_dict[w.ID] = w.getState()
    windows_dict[creation_datetime] = datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
    # main loop / no error managment
    print "Starting measurements"
    while True:
        data=acquire(sensors)
        for i in range (0,len(data)+1):
            sendJson_TI(data[i])
        sendJson_windows(windows_dict)
        dispData(True,data)
        sleep(300) # Prise de mesure toutes les 5 minutes environ


if __name__ == '__main__':
    main()
