#!/usr/bin/env python3

#######################################################################
#
# TODO: Add header/copyright block
#
#######################################################################

from .controller import PID, Direct, clip

class Middle(object):
    '''
    Middle-loop control class.
    '''
    def __init__(self):
        self.channels = [PID(), PID(), PID()]
        self.channels[0].setGains((-0.1, -0.001, 0)) # Heading/roll
        self.channels[0].setRange([-1, 1])
        self.channels[0].setDomain([0, 360])
        self.channels[0].setSign(-1)
        self.channels[0].setWrapAround(True)

        self.channels[1].setGains((-0.15,-0.001,0))#Altitude/Pitch
        self.channels[1].setRange([-1, 1])
        self.channels[1].setSign(-1)

        self.channels[2].setGains((-0.05, 0, 0)) # Speed/throttle
        self.channels[2].setRange([0, 2])
        self.channels[2].setSign(-1)

    def updateSetpoint(self, inCommand):
        '''
        Updates the setpoints of each channel.

        Inner control loop states are roll, pitch, and throttle.

        '''
        for channelId in range(3):
            self.channels[channelId].updateSetpoint(inCommand[channelId])

    def updateObservation(self, inObservation):
        '''
        Update the observation of the inner control loop.

        Inner control loop states are roll, pitch, and throttle.

        Right now, assume perfect decoupling between channels. Further, assume no rudder commands. All of this will need to be revisited in a future iteration.
        '''
        for channelId in range(3):
            self.channels[channelId].updateObservation([inObservation[0], inObservation[channelId + 1]])

    def computeCommand(self):
        '''
        Computes the flight control surface output based on the channel PID controllers.
        '''

        return (self.channels[0].computeOutput(),
                self.channels[1].computeOutput(),
                self.channels[2].computeOutput())


    def reset(self):
        self.channels[0].clearIntegratedError()
        self.channels[1].clearIntegratedError()
        self.channels[2].clearIntegratedError()
