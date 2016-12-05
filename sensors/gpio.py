# -*- coding: utf-8 -*-
"""
Class GPIO to read if the GPIO has changed state. More doc to come. 
last update 5/12/2016

@author: Timothé Faivre

ERRORFLAGS
''' description bit par bit: 

Error Flag description. 
0b10000000 : pb with gpio
    0b10000001 : init : pin number bot a number
    0b10000010 : init : pin number not in allowed list
    0b10000011 : setup : state not recognized


"""



import RPi.GPIO as GPIO
import re
    

class gpio():
    
    def __init__(self,pin,ID,state=False,io='in',verbose=True):
        GPIO.setmode(GPIO.BOARD)
        self.state=state
		self.verbose=verbose
        self.allowed=[23,35,37]#range(12,41)
        try:
           self.pin= int(pin)
        except ValueError:
               if self.verbose: print( "I am afraid %s is not a number" % str(pin))
               self.ERRORFLAGS=0b10000001
        if pin not in self.allowed:
           if self.verbose: print(" %s is not an allowed pin number" % str(pin))
           self.ERRORFLAGS=0b10000010 
           
        self.ID=ID
        self.setup(io)

        
    def setup(self,io): # Initialize state and function (input/output)
       
       if re.search('in',io,re.IGNORECASE) : 
           GPIO.setup(self.pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
           self.io='IN'
           self.state=GPIO.input(self.pin)
           self._prevstate=self.state
       elif re.search('out',io,re.IGNORECASE) : 
           GPIO.setup(self.pin,GPIO.OUT, pull_up_down=GPIO.PUD_UP)
           
       else :
           if self.verbose: print( " %s is not an allowed state" % str(io))
           self.ERRORFLAGS=0b10000011
           
    def setState(self,state): 
        GPIO.output(self.pin,state)
        self._prevstate=self.state
        self.state=state
        
    def changeState(self):
        self._prevstate=self.state
        self.setState(not self.state)
        
    def getState(self): # just retrun current state
        if 'OUT' in self.io:
            return self.state
        else:
            self._prevstate=self.state
            self.state=GPIO.input(self.pin)
            return self.state
            
    def checkState(self): # anti bounding : rising edge only trigger flag update
        if not 'OUT' in self.io:
            self.state=GPIO.input(self.pin) 
            if self.state == 0 :
                if  self.state != self._prevstate:
                    if self.verbose: print( "switch %s pressed ! "%(str(self.ID)) )
                    self._prevstate=0
            else : 
                self._prevstate=1

                    
      
 # NOT YET IMPLEMENTED            
    def callback(self):	
	'''NOT YET IMPLEMENTED 
	'''
        return 1
        
    def set_event(self):
		'''NOT YET IMPLEMENTED 
	'''
        #GPIO.add_event(self.ID,GPIO.BOTH,callback=self.callback,bouncetime=75)
		return 1
        
    def clear_event(self):
		'''NOT YET IMPLEMENTED 
	'''
        #GPIO.remove_event_detect(self.ID)
		return 1
        
        