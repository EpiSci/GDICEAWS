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
        self.channels = [PID()]
        self.channels[0].setGains((10, 1, 1))
        self.channels[0].setRange([300, 500])
        self.channels[0].setDomain([-180, 180])
    
    def reset(self):
        self.channels[0].clearIntegratedError()
