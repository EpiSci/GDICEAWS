import math

import numpy as np

from .constants import MA, StateInfo
from ...getfs.unitChange import unitChange
from .. import inner, middle
from .tma import TMAObject


class MA2LagPursuit(TMAObject):
    """
    Lag pursuit bandit
    """
    def __init__(self):
        super().__init__()
        # Pid controllers
        self.inner = inner.Inner()
        self.middle = middle.Middle()

    def __str__(self):
        return MA.MA2
    
    def selected(self, observation):
        self.is_done = False
        self.inner.reset()
        self.middle.reset()
        self.inner.channels[0].setGains((0.45, 0.0001, 2.0))
        self.inner.channels[1].setGains((-2.7, -1, -3.50))
        self.middle.channels[0].setRange([-1.15, 1.15])
        
    def compute_action(self, observation, info):
        '''
        Track the bandit in WEZ
        '''
        state = observation

        # Update the observations as appropriate
        currentTime = state[info[StateInfo.SELF_SIMULATION_TIME_SEC]]
        blue_u = state[info[StateInfo.SELF_VELOCITIES_U_FPS]]
        blue_v = state[info[StateInfo.SELF_VELOCITIES_V_FPS]]
        blue_w = state[info[StateInfo.SELF_VELOCITIES_W_FPS]]

        tmpSpeed = math.sqrt(blue_u**2 + blue_v**2 + blue_w**2)
        blue_roll_rads = state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]]
        blue_pitch_rads = state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]

        self.inner.updateObservation([currentTime, blue_roll_rads, blue_pitch_rads, tmpSpeed])

        # Calculate bank angle to point to red
        blue_x = state[info[StateInfo.SELF_X_POSITION]]
        blue_y = state[info[StateInfo.SELF_Y_POSITION]]

        blue_state = np.array([blue_x, blue_y, blue_u, blue_v])

        red_x = state[info[StateInfo.BANDIT_X_POSITION]]
        red_y = state[info[StateInfo.BANDIT_Y_POSITION]]
        red_u = state[info[StateInfo.BANDIT_VELOCITIES_U_FPS]]
        red_v = state[info[StateInfo.BANDIT_VELOCITIES_V_FPS]]
        red_w = state[info[StateInfo.BANDIT_VELOCITIES_W_FPS]]

        blue_heading_rad = math.radians(state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]])
        red_heading_rad = math.radians(state[info[StateInfo.BANDIT_ATTITUDE_PSI_DEG]])

        red_state = np.array([red_x, red_y, red_u, red_v])

        uc = unitChange(blue_state, red_state, blue_heading_rad, red_heading_rad)
        angle_off = math.degrees(uc.angle_off())
        distance = state[info[StateInfo.SELF_DISTANCE_FT]]
        rel_alt = state[info[StateInfo.BANDIT_POSITION_H_SL_FT]] - state[info[StateInfo.SELF_POSITION_H_SL_FT]]
        bank_angle = min(90, 90 - math.degrees(math.asin(rel_alt / distance)))

        if angle_off > 0:
            bank_angle = min(-bank_angle, bank_angle)
            bank_angle += 10
        else:
            bank_angle = max(-bank_angle, bank_angle)
            bank_angle -= 10
            
        rel_altitude = state[info[StateInfo.SELF_Z_POSITION]] - state[info[StateInfo.BANDIT_Z_POSITION]]
        if rel_altitude >= 100:
            pitch_angle = state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]
        else:
            rel_altitude = abs(rel_altitude)
            dist = state[info[StateInfo.SELF_DISTANCE_FT]]
            pitch_angle = min(60, math.degrees(math.asin(rel_altitude / dist)) + 5)

        angle_off = math.degrees(uc.angle_off())
        tmpHeadingSetpoint = state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]] - 2 * angle_off
        # if angle_off > 0:
        #     tmpHeadingSetpoint -= 30
        # else:
        #     tmpHeadingSetpoint += 30

        self.middle.channels[0].updateObservation([currentTime, state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]]])
        self.middle.channels[0].updateSetpoint(tmpHeadingSetpoint)
        self.middle.channels[1].updateObservation([currentTime, state[info[StateInfo.SELF_POSITION_H_SL_FT]]])
        self.middle.channels[1].updateSetpoint(state[info[StateInfo.BANDIT_POSITION_H_SL_FT]] + 1000)

        self.middle.channels[2].updateObservation([currentTime, tmpSpeed])
        if state[info[StateInfo.SELF_DISTANCE_FT]] > 3000:
            self.middle.channels[2].updateSetpoint(self._kts_to_fps(450))
        else:
            red_speed = math.sqrt(red_u**2 + red_v**2 + red_w**2)
            self.middle.channels[2].updateSetpoint(red_speed - self._kts_to_fps(50))
        
        tmpRollSetPoint = self.middle.channels[0].computeOutput()
        tmpPitchSetPoint = self.middle.channels[1].computeOutput()
        tmpThrottleSetpoint = self.middle.channels[2].computeOutput()

        # if not self._is_inside_turn_circle(state, info):
        #     if state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]] < 0:
        #         tmpRollSetPoint = min(tmpRollSetPoint, 0)
        #     else:
        #         tmpRollSetPoint = max(tmpRollSetPoint, 0)
        
        if state[info[StateInfo.SELF_POSITION_H_SL_FT]] <= 3000:
            tmpPitchSetPoint = math.radians(10)

        if state[info[StateInfo.SELF_POSITION_H_SL_FT]] <= 2000:
            tmpPitchSetPoint = math.radians(15)

        self.inner.channels[0].updateSetpoint(math.degrees(bank_angle))
        self.inner.channels[1].updateSetpoint(tmpPitchSetPoint)
        self.inner.channels[2].updateSetpoint(tmpThrottleSetpoint)

        # Finally, update the inner control loop
        (tmpAileron, tmpElevator, tmpThrottle) = self.inner.computeCommand()
        tmpRudder = 0

        # Outer loop maps from state space to [heading, altitude, speed]
        self.current_action = np.array([tmpAileron, tmpElevator, tmpRudder, tmpThrottle])

        aspect_angle = math.degrees(uc.aspect_angle())
        self._check_done(MA.MA2, angle_off, aspect_angle, state, info)
        self.step_count += 1

    def get_action(self):
        return self.current_action

    def get_done(self):
        return self.is_done

