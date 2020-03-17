import math

import numpy as np

from ...constants import MA, StateInfo
from ...getfs.unitChange import unitChange
from .. import inner, middle
from .tma import TMAObject


class MA3PurePursuit(TMAObject):
    """
    Pure pursuit of bandit
    """
    def __init__(self):
        super().__init__()
        # Pid controllers
        self.inner = inner.Inner()
        self.middle = middle.Middle()

    def __str__(self):
        return MA.MA3
    
    def selected(self, observation):
        self.is_done = False
        self.inner.reset()
        self.middle.reset()
        self.inner.channels[0].setGains((0.45, 0.0001, 2.0))
        self.inner.channels[1].setGains((-2.75, -1, -3.50))
        self.middle.channels[0].setRange([-1.15, 1.15])

    def compute_action(self, observation, info):
        '''
        Track the bandit in WEZ
        '''
        state = observation

        # Update the observations as appropriate
        currentTime = state[info[StateInfo.SELF_SIMULATION_TIME_SEC]]
        
        self.inner.updateObservation([currentTime, state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]], state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]], 0])
        tmpSpeed = math.sqrt(state[info[StateInfo.SELF_VELOCITIES_U_FPS]]**2 + state[info[StateInfo.SELF_VELOCITIES_V_FPS]]**2 + state[info[StateInfo.SELF_VELOCITIES_W_FPS]]**2)
        self.middle.updateObservation([currentTime, state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]], state[info[StateInfo.SELF_POSITION_H_SL_FT]], tmpSpeed])

        # Run the middle control loop to figure out what we need to do
        # Middle maps from [heading, pitch, speed] to [roll, pitch, throttle]
        blue_x = state[info[StateInfo.SELF_X_POSITION]]
        blue_y = state[info[StateInfo.SELF_Y_POSITION]]
        blue_u = state[info[StateInfo.SELF_VELOCITIES_U_FPS]]
        blue_v = state[info[StateInfo.SELF_VELOCITIES_V_FPS]]

        blue_state = np.array([blue_x, blue_y, blue_u, blue_v])

        red_x = state[info[StateInfo.BANDIT_X_POSITION]]
        red_y = state[info[StateInfo.BANDIT_Y_POSITION]]
        red_u = state[info[StateInfo.BANDIT_VELOCITIES_U_FPS]]
        red_v = state[info[StateInfo.BANDIT_VELOCITIES_V_FPS]]
        red_w = state[info[StateInfo.BANDIT_VELOCITIES_W_FPS]]

        red_state = np.array([red_x, red_y, red_u, red_v])     

        blue_heading_rad = math.radians(state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]])
        red_heading_rad = math.radians(state[info[StateInfo.BANDIT_ATTITUDE_PSI_DEG]])
        uc = unitChange(blue_state, red_state, blue_heading_rad, red_heading_rad)
        angle_off = math.degrees(uc.angle_off())
        aspect_angle = math.degrees(uc.aspect_angle())

        tmpHeadingSetpoint = state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]] - angle_off
        # Respond to reversal
        #Chris - Increased reversal_delta to more agressively maneuver to match
        if math.degrees(state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]]) >= 10:
            reversal_delta = 15 #edited from 10
            if self._is_inside_turn_circle(state, info):
                reversal_delta = 30     #edited from 20
            opposite_bank = np.sign(state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]]) != np.sign(state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]])
            if opposite_bank and state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]] < 0:
                tmpHeadingSetpoint += reversal_delta
            elif opposite_bank and state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]] > 0:
                tmpHeadingSetpoint -= reversal_delta
            elif abs(angle_off) < reversal_delta and state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]] > 0:
                tmpHeadingSetpoint += reversal_delta
            elif abs(angle_off) < reversal_delta and state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]] < 0:
                tmpHeadingSetpoint -= reversal_delta

        tmpAltSetPoint = state[info[StateInfo.BANDIT_POSITION_H_SL_FT]]
        rel_altitude = state[info[StateInfo.SELF_POSITION_H_SL_FT]] - state[info[StateInfo.BANDIT_POSITION_H_SL_FT]]
        if rel_altitude >= 500:
            self.middle.channels[0].setRange([-1.5, 1.5])
            tmpAltSetPoint = state[info[StateInfo.SELF_POSITION_H_SL_FT]]
        else:
            self.middle.channels[0].setRange([-1.15, 1.15])

        tmpSpeedSetpoint = math.sqrt(red_u**2 + red_v**2 + red_w**2)
        xy_range = math.sqrt((red_x - blue_x) ** 2 + (red_y - blue_y) ** 2)
        if xy_range > 3000:
            tmpSpeedSetpoint += self._kts_to_fps(50)  # Edited from 80

        elif xy_range > 2000:
            tmpSpeedSetpoint += self._kts_to_fps(20)

        #increasing speed to close into track range
        elif xy_range > 1000:
            tmpSpeedSetpoint += self._kts_to_fps(8)

        self.middle.updateSetpoint([tmpHeadingSetpoint, tmpAltSetPoint, tmpSpeedSetpoint])
        (tmpRollSetPoint, tmpPitchSetPoint, tmpThrottleSetpoint) = self.middle.computeCommand()

        # Finally, update the inner control loop
        # if state[info[StateInfo.SELF_DISTANCE_FT]] <= 3000 and angle_off <= 10 and aspect_angle <= 10 and abs(rel_altitude) <= 500:
        #     if tmpRollSetPoint < 0:
        #         tmpRollSetPoint = max(tmpRollSetPoint, state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]])
        #     else:
        #         tmpRollSetPoint = min(tmpRollSetPoint, state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]])

        if state[info[StateInfo.SELF_DISTANCE_FT]] <= 1500 and abs(angle_off) <= 2 and abs(aspect_angle) <= 2 and abs(rel_altitude) <= 100:
            tmpRollSetPoint = state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]]
        
        # if state[info[StateInfo.SELF_POSITION_H_SL_FT]] <= 3000:
        #     tmpPitchSetPoint = max(math.radians(10), tmpPitchSetPoint)
        
        # if state[info[StateInfo.SELF_POSITION_H_SL_FT]] <= 2000:
        #     tmpPitchSetPoint = max(math.radians(15), tmpPitchSetPoint)

        self.inner.updateSetpoint([tmpRollSetPoint, tmpPitchSetPoint, tmpThrottleSetpoint])
        (tmpAileron, tmpElevator, tmpThrottle) = self.inner.computeCommand()
        tmpRudder = 0
        if self._fps_to_kts(tmpSpeed) <= 140 and state[info[StateInfo.SELF_DISTANCE_FT]] > 1000:
            tmpThrottle = 1.0

        # Outer loop maps from state space to [heading, altitude, spee
        self.current_action = np.array([tmpAileron, tmpElevator, tmpRudder, tmpThrottle])

        aspect_angle = math.degrees(uc.aspect_angle())
        self._check_done(MA.MA3, angle_off, aspect_angle, state, info)
        self.step_count += 1

    def get_action(self):
        return self.current_action

    def get_done(self):
        return self.is_done