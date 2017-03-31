#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ce script permet d'aggréger les données de tous les capteurs utilisés
"""
from bluepy.btle import Scanner
from bluepy import sensortag

from time import gmtime, strftime, sleep
import datetime

import json
import boto3
from gpio import gpio


def autopairing(timeout=10.0, devices=None):
    """
    Autoscan BLE for neighbouring advertising Sensortag
    and turn on environmental sensors
    """

    # Auto scan if no sensors are provided
    if devices is None:
        BLE = Scanner()

        print("Scanning in progress \n")
        devices = BLE.scan(timeout)

    Sensors = []
    dev_list = 'Liste : \n'
    for dev in devices:
        if 'SensorTag' in str(dev.getValueText(9)):

            print("Device %s (SensorTag), RSSI=%d dB" % (dev.addr, dev.rssi))
            dev_list += "Device %s (SensorTag), RSSI=%d dB \n" % (dev.addr, dev.rssi)
            sleep(1)
            idx = 0
            while True:
                try:
                    tag = sensortag.SensorTag(dev.addr)
                    tag.addr = dev.addr

                    # Add here relevant sensors to enable at start. check from sensortag.py for more info
                    tag.lightmeter.enable()
                    tag.humidity.enable()
                    tag.IRtemperature.enable()
                    Sensors.append(tag)
                    break
                except Exception as e:
                    # it happens that the sensors failed to start for some reasons
                    # Retrying is usually enough to connect.
                    print(e)
                    print("Sensor disconnected, retrying")
                    idx += 1
                    sleep(.5)
                    pass
                if idx > 5:  # if it's not, then you have to remove this sensors from the list
                    print("Forgetting about THAT sensor")
                    break
                # if everything goes well, add the sensors to the list

    del devices
    return Sensors

def reconnect(tag):
### try reconnecting lost sensor###
    print("Device %s has lost connection, reconnecting" % (tag.deviceAddr))

    addr=tag.deviceAddr
    sleep(1)
    idx=0
    while idx<2:
        try :
            tag.disconnect()
        except :
            pass
        tag = None
        try:
            idx+=1
            tag = sensortag.SensorTag(addr)
            tag.addr =addr

            # Add here relevant sensors to enable at start. check from sensortag.py for more info
            tag.lightmeter.enable()
            tag.humidity.enable()
            tag.IRtemperature.enable()
            return tag
        except Exception as e:
            print("problem reconnecting device, retry %d out of %d" %(idx,2))
            print(e)

        if idx==2:
            print("Device %s is lost" % (tag.deviceAddr))
            return None
	if tag is not None : 
        	print("Device %s sucessfully reconnected" % (tag.deviceAddr))
        return tag


def acquire(Sensors):
    """
    Read sensors measured value and return a data dictionary
    Warning : this is not error proof : any disconnection from one
    of the sensor make the full function to crash.
    """
    data = []
    for ind,tag in enumerate(Sensors):

        try :
            meas = {}
            meas['ID'] = tag.addr
            loc = tag.humidity.read()

            meas['creation_datetime'] = datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
            meas['Temperature'] = loc[0]  # T in C°
            meas['Humidite'] = loc[1]  # HR in %
            meas['Luminosite'] = tag.lightmeter.read()  # Illuminance

            # Add relevant measurement here.
            # Adding the measured value to the globale dict.
            data.append(meas)
        except Exception as e :
            print(e.message)
            tag2 = reconnect(tag)
            if tag2 is None:
                Sensors.remove(tag)
            else:
                Sensors[ind]=tag2

    return data


def sendJson_TI(input_json):
    """
    Send JSON to Amazon bucket from TI sensor
    """

    s3_client = boto3.client('s3')

    filename = 'TI_' + datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC") + '.txt'

    try:
        with open(filename, 'w+') as doc:
            doc.write(json.dumps(input_json))
        s3_client.upload_file(filename+'.txt', 'sensortag', filename+'.txt')

    except Exception as e:
        print('Error while sending to S3 : ' + str(e.message))  # log in case of exception


def sendJson_windows(input_json):
    """
    Send Json to Amazon bucket from windows sensor
    """

    s3_client = boto3.client('s3')

    filename = 'windows_' + datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC") + '.txt'

    try:
        with open(filename, 'w+') as doc:
            doc.write(json.dumps(input_json))
        s3_client.upload_file(filename+'.txt', 'sensortag', filename+'.txt')

    except Exception as e:
        print('Error while sending to S3 : ' + str(e.message))  # log in case of exception


def dispData(verbose, data=None):
    """
    Display data if verbose is True and data are provided
    """

    if not verbose or data is None:
        return
    else:
        first = True
        for meas in data:
                if first:
                    now = datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
                    print(now + '  :  ' + str(meas.keys()))
                    first = False
                print(' :'+str([meas[k2] for k2 in meas.keys()]))


def main():
    """
    Fonction principale permettant de prendre une mesure
    toutes les 5 minutes et d'envoyer les fichiers Json au bucket
    """
    print("Init : autopairing")
    sensors = autopairing()
    print("Done !")

    print("GPIO Init")

    windows = [gpio(12, 'Tableau'), gpio(21, 'Milieu'), gpio(17, 'Fond')]


    print("Starting TI measurements")
    while True:
        data = acquire(sensors)
        dispData(True, data)

        # envoyer autant de json que de capteur TI
        for dat in data:
            sendJson_TI(dat)
        #recuperer les mesures fenetres
        windows_dict = {}
        for w in windows:
            windows_dict[w.ID] = w.getState()

        windows_dict['creation_datetime'] = datetime.datetime.now().strftime("%Y_%m_%d-%H:%M:%S UTC")
        # envoyer la mesure fenêtre
        sendJson_windows(windows_dict)
        sleep(10)  # Prise de mesure toutes les 5 minutes environ


if __name__ == '__main__':
    main()
