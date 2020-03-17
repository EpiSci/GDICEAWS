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
        self.channels = [Direct(), PID(), PID()]
        self.channels[1].setGains((-0.25,-0.0001,1)) # Desired G for elevator to pull
        self.channels[1].setRange([1, 9])

        self.channels[2].setGains((0.1, 0.001, 0.1)) # Speed/throttle
        self.channels[2].setRange([0.2, 2])

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
                clip(self.channels[1].computeOutput(), [-1, 1]),
                self.channels[2].computeOutput())


    def reset(self):
        self.channels[1].clearIntegratedError()
        self.channels[2].clearIntegratedError()
