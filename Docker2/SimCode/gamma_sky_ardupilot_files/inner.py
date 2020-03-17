#!/usr/bin/env python3

#######################################################################
#
# TODO: Add header/copyright block
#
#######################################################################

from .controller import PID, Direct,clip


class Inner(object):
    '''
    Inner-loop control class.

    This algorithm is based on the Fly-By-Wire Mode A implemented in Ardupilot Plane. The commanded states are roll, pitch, and throttle.
    '''
    def __init__(self):
        self.channels = [PID(), PID(), Direct(), PID()]
        self.channels[0].setGains((1, 0.5, 1)) # roll/aileron
        self.channels[0].setRange([-1, 1])
        self.channels[0].setDomain([-3.14159, 3.14159])
        self.channels[0].setWrapAround(True)

        self.channels[1].setGains((-5, -5, 1)) # pitch/elevator
        self.channels[1].setRange([-1, 1])
        self.channels[1].setDomain([-3.14159, 3.14159])
        self.channels[1].setWrapAround(True)
        self.channels[1].setSign(-1)

        self.channels[3].setGains((0.0075, 0.000001, 0.001)) # yaw/rudder
        self.channels[3].setRange([-0.225, 0.225])
        self.channels[3].setDomain([-180, 180])
        self.channels[3].setSign(-1)

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
