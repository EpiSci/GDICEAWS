#!/usr/bin/env python3

#######################################################################
#
# TODO: Add header/copyright block
#
#######################################################################

import numpy as np

def clip(inValue, inLimits) -> float:
    '''
    Helper function to apply clipping to output variables
    '''
    return (min(inLimits[1], max(inLimits[0], inValue)))

def wrapError(inObservation, inSetpoint, inDomain) -> float:
    '''
    Helper function to handle variables the wrap around, such as angles.
    '''
    if inDomain[0] == 0 :
        error_1 = inSetpoint - inObservation
        error_2 = inSetpoint + inDomain[1] - inObservation
        error_3 = inSetpoint - inObservation - inDomain[1]
        if np.absolute(error_1) < np.absolute(error_2) and np.absolute(error_1) < np.absolute(error_3):
            return -error_1
        elif np.absolute(error_2) < np.absolute(error_1) and np.absolute(error_2) < np.absolute(error_3):
            return -error_2
        else:
            return -error_3
        
    else:
        if inSetpoint >= inObservation:
            error_p = inSetpoint - inObservation
            error_m = (inObservation - inDomain[0]) + (inDomain[1] - inSetpoint)
        else:
            error_p = (inDomain[1] - inObservation) + (inSetpoint - inDomain[0])
            error_m = inObservation - inSetpoint

        if error_p < error_m:
            return error_p
        else:
            return -1 * error_m

class PID(object):
    '''
    Implements a generic discrete time PID controller.

    TODO: Write additional documentation
    '''
    def __init__(self):
        self.gains = (0., 0., 0.)
        self.lastTime = 0.
        self.setpoint = 0.
        self.error = 0.
        self.integratedError = 0.
        self.derivativeError = 0.
        self.int_clamp = False
        self.wrapAround = False
        self.domain = [-1e32, 1e32]
        self.range = [-1e32, 1e32]
        self.tmpCommand = 0
        self.GainSign = 1

    def setWrapAround(self, inWrapAround):
        '''
        Sets if this variable wraps around (i.e. an angle)
        '''
        self.wrapAround = inWrapAround

    def setRange(self, inRange):
        '''
        Set the range of valid output
        '''
        self.range = inRange

    def setDomain(self, inDomain):
        '''
        Set the domain of vaild input (used to wrap error values)
        '''
        self.domain = inDomain

    def setSign(self, sign):
        '''
        Sets flag for sign of the gain, also the sign of input to error
        '''
        self.GainSign = sign

    def setGains(self, inGains):
        '''
        Set the gains of the controller. Must be in the form of (Kp, Ki, Kd)
        '''
        self.gains = inGains

    def updateSetpoint(self, inSetpoint):
        '''
        Updates the setpoint of the PID controller. All future observations will be compared to this setting.
        '''
        self.setpoint = inSetpoint

    def clearIntegratedError(self):
        '''
        Resets the error integrator to zero for all future computations
        '''
        self.integratedError = 0.

    def updateObservation(self, inObservation):
        '''
        Provides a new observation to the PID controller. Input must be in the form of (time, value)
        '''

        # Compute the time since the last observation
        tmpTimeStep = inObservation[0] - self.lastTime

        # Compute the difference between the setpoint and observation
        if not self.wrapAround:
            tmpError = inObservation[1] - self.setpoint
        else:
            tmpError = wrapError(inObservation[1], self.setpoint, self.domain)

        # Compute the rate of change of the error based on the last data
        self.derivativeError = (tmpError - self.error) / tmpTimeStep if tmpTimeStep != 0 else 0

        # Add to the integrated error term
        if self.range[0] >= self.tmpCommand or self.range[1] <= self.tmpCommand :
            if np.sign(self.tmpCommand) == np.sign(self.GainSign*self.integratedError) :
               self.clamp = True
        else:
            self.clamp = False

        if self.clamp == False :
            self.integratedError += tmpError * tmpTimeStep

        # Update the remaining properties of the object
        self.lastTime = inObservation[0]
        self.error = tmpError

    def computeOutput(self):
        '''
        Returns the output from the PID controller.
        '''

        self.tmpCommand = self.error * self.gains[0]
        self.tmpCommand += self.integratedError * self.gains[1]
        self.tmpCommand += self.derivativeError * self.gains[2]

        return clip(self.tmpCommand, self.range)


class Direct(object):
    '''
    Simple interface object to match the methods of the PID class.
    '''
    def __init__(self):
        self.setpoint = 0.
        self.range = [-1e32, 1e32]

    def updateSetpoint(self, inSetpoint):
        self.setpoint = inSetpoint

    def updateObservation(self, inObservation):
        pass

    def computeOutput(self):
        return clip(self.setpoint, self.range)

    def setRange(self, inRange):
        '''
        Set the range of valid output
        '''
        self.range = inRange
