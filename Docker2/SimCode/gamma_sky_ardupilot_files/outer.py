#!/usr/bin/env python3

#######################################################################
#
# TODO: Add header/copyright block
#
# Implements an outer loop controller for BFM.
#######################################################################


from .controller import PID, Direct, clip
import numpy as np
import math

class Outer(object):
    '''
    Middle-loop control class.
    '''
    def __init__(self):
        self.channels = [PID(), Direct()]
        self.channels[0].setGains((-1, -0.05, 0)) # TrackHeading/Heading
        self.channels[0].setRange([-30,30])
        self.channels[0].setDomain([0, 360])
        self.channels[0].setSign(-1)
        self.channels[0].setWrapAround(True)
        
        '''
        self.channels[1].setGains((-10000, -10, 0)) #DesSpeed/Speed
        self.channels[1].setSign(-1)
        self.channels[1].setRange([-200,200])
        '''

    def updateSetpoint(self, inCommand):
        Lag_Dist = -500
        RelPos = [inCommand[0],inCommand[1],inCommand[2]]
        RelDist = math.sqrt(RelPos[0]**2+RelPos[1]**2+RelPos[2]**2)

        oppHeading = inCommand[3]
        Track_Point_Rel = np.array([RelPos[0],RelPos[1],RelPos[2]])-Lag_Dist*np.array([math.sin(math.radians(oppHeading)), math.cos(math.radians(oppHeading)), 0 ])
        
        maxSpeed = 1300

        Track_Head = math.atan2(Track_Point_Rel[0], Track_Point_Rel[1])*180/math.pi
        if Track_Head <0:
           Track_Head += 360

        oppSpeed = inCommand[4]
        ownHeading = inCommand[5]
        
        RelHeading = min(abs(oppHeading - ownHeading),abs(oppHeading+360 - ownHeading), abs(oppHeading - ownHeading-360))
        
        if RelHeading <=60 :
	        if RelDist > 10000:
                    Speed_Des = maxSpeed#min(1200, oppSpeed + 600)
	        elif RelDist > 5000 :
                    Speed_Des = min(maxSpeed, oppSpeed+500)
	        else:
                    Speed_Des = oppSpeed+100
        elif RelHeading <=90 :
	        if RelDist > 10000:
                    Speed_Des = maxSpeed #min(800, oppSpeed + 300)
	        elif RelDist > 5000 :
                     Speed_Des = min(800, oppSpeed)
	        else:
                     Speed_Des = max(oppSpeed-200,400)
        elif RelHeading <=120 :
	        if RelDist > 50000:
                    Speed_Des = maxSpeed #min(600, oppSpeed + 100)
	        elif RelDist > 30000 :
                     Speed_Des = min(500, oppSpeed)
	        else:
                     Speed_Des = max(oppSpeed-200,500)
        else:
	        if RelDist > 50000:
                    Speed_Des = maxSpeed
	        elif RelDist > 30000 :
                    Speed_Des = max(500, oppSpeed-200)
	        else:
                    Speed_Des = max(500,oppSpeed - 300)

        self.channels[0].updateSetpoint(Track_Head)
        self.channels[1].updateSetpoint(Speed_Des)
        

    def updateObservation(self, inObservation):
        self.channels[0].updateObservation([inObservation[0], inObservation[1]])
        #self.channels[1].updateObservation([inObservation[0], inObservation[2]])

    def computeCommand(self):
        

        return (self.channels[0].computeOutput(), self.channels[1].computeOutput())
    
    def reset(self):
        self.channels[0].clearIntegratedError()
        #self.channels[1].clearIntegratedError()
