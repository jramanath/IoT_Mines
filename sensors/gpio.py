# -*- coding: utf-8 -*-
"""
Class GPIO to read if the GPIO has changed state. More doc to come.
last update 5/12/2016

@author: Timothé Faivre
"""
import RPi.GPIO as GPIO
import re


class gpio():
    ''' represent a pin, with attribute (in or out) ans state (true of false) as well as an unique ID
    '''
    def __init__(self, pin, ID, state=False, io='in', verbose=True):
        GPIO.setmode(GPIO.BCM) # Modify the pin numbering on rpi
        self.state = state
        self._prevstate = state
        self.verbose = verbose
        self.allowed = range(12,41)
        try:
            self.pin = int(pin)
        except ValueError:
            if self.verbose: print( "I am afraid %s is not a number" % str(pin))
        if pin not in self.allowed:
            if self.verbose: print(" %s is not an allowed pin number" % str(pin))
        self.ID = ID
        self.setup(io)


    def setup(self,io):
        '''Initialize state and function (input/output)
        '''
        if re.search('in', io, re.IGNORECASE):
            GPIO.setup(self.pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
            self.io = 'IN'
            self.state = GPIO.input(self.pin)
            self._prevstate = self.state
        elif re.search('out', io, re.IGNORECASE):
            GPIO.setup(self.pin, GPIO.OUT, pull_up_down=GPIO.PUD_UP)

        else :
            if self.verbose: print(" %s is not an allowed state" % str(io))

    def setState(self, state):
        '''set output to true or false (output only)
        '''
        if 'OUT' in self.io:
            GPIO.output(self.pin, state)
            self._prevstate = self.state
            self.state = state

    def changeState(self):
        '''commute state (output only)
        '''
        if 'OUT' in self.io:
            self._prevstate = self.state
            self.setState(not self.state)

    def getState(self):
        '''return current pin state
        '''
        if 'OUT' in self.io:
            return self.state
        else:
            self._prevstate = self.state
            self.state = GPIO.input(self.pin)
            return self.state

    def checkState(self): # anti bounding : rising edge only trigger flag update
        if not 'OUT' in self.io:
            self.state = GPIO.input(self.pin)
            if self.state == 0 :
                if  self.state != self._prevstate:
                    if self.verbose: print("switch %s pressed ! "%(str(self.ID)))
                    self._prevstate = 0
            else :
                self._prevstate = 1
