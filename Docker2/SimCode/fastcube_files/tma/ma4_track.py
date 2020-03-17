import math

import numpy as np

from ...constants import MA, StateInfo
from ...getfs.unitChange import unitChange
from ...gamma_sky_ardupilot_files import inner, middle
from .tma import TMAObject


class MA4TrackPursuit(TMAObject):
    """
    Track pursuit of bandit
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

        self.inner.channels[0].setGains((1.5, 0.0001, 3))
        self.inner.channels[1].setGains((-10, 0, -2))

    def compute_action(self, observation, info):
        '''
        Track the bandit in WEZ
        '''
        state = observation

        # Update the observations as appropriate
        currentTime = state[info[StateInfo.SELF_SIMULATION_TIME_SEC]]
        tmpSpeed = math.sqrt(state[info[StateInfo.SELF_VELOCITIES_U_FPS]]**2 + state[info[StateInfo.SELF_VELOCITIES_V_FPS]]**2 + state[info[StateInfo.SELF_VELOCITIES_W_FPS]]**2)
        
        self.inner.updateObservation([currentTime, state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]], state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]], tmpSpeed])
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
        dist = state[info[StateInfo.SELF_DISTANCE_FT]]

        tmpHeadingSetpoint = state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]] - angle_off
        # Respond to reversal
        #Chris - Increased reversal_delta to more agressively maneuver to match
        if math.degrees(state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]]) > 10:
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
        tmpSpeedSetpoint = math.sqrt(red_u**2 + red_v**2 + red_w**2)
        rel_altitude = state[info[StateInfo.SELF_POSITION_H_SL_FT]] - state[info[StateInfo.BANDIT_POSITION_H_SL_FT]] 
        # xy_range =  math.sqrt((red_x - blue_x) ** 2 + (red_y - blue_y) ** 2)
        if dist > 3000:
            tmpSpeedSetpoint += self._kts_to_fps(100)  # Edited from 80
        else:
            closure = self._calculate_closure_kts(dist)
            # tmpSpeedSetpoint = tmpSpeed - self._kts_to_fps(closure) + 3 # 0 closure to track
            tmpAltSetPoint += 500
            # if closure > 10 and rel_altitude < 300:
            #     tmpAltSetPoint += 500 # Convert kinetic to potential energy

        self.middle.updateSetpoint([tmpHeadingSetpoint, tmpAltSetPoint, tmpSpeedSetpoint])
        (tmpRollSetPoint, tmpPitchSetPoint, tmpThrottleSetpoint) = self.middle.computeCommand()

        # # Point nose at bandit
        # if dist < 3000:
        rel_alt = state[info[StateInfo.BANDIT_POSITION_H_SL_FT]] - state[info[StateInfo.SELF_POSITION_H_SL_FT]]
        tmpPitchSetPoint = math.asin(rel_alt / dist)  #+ math.radians(state[16])
        
        # Limit dive angle
        if tmpPitchSetPoint < 0:
            tmpPitchSetPoint = max(tmpPitchSetPoint, -math.radians(state[info[StateInfo.SELF_POSITION_H_SL_FT]] / 100))
        
        self.inner.updateSetpoint([tmpRollSetPoint, tmpPitchSetPoint, tmpThrottleSetpoint])
        (tmpAileron, tmpElevator, tmpThrottle) = self.inner.computeCommand()

        # Calculate Yaw
        tmpRudder = 0
        self.inner.channels[3].updateObservation([currentTime, angle_off])
        self.inner.channels[3].updateSetpoint(0)
        tmpRudder = self.inner.channels[3].computeOutput()

        # Max throttle if large elevator
        if tmpElevator < -0.7:
            tmpThrottle += 0.4

        # Instability avoidance when leveling out altitude
        blue_pitch = math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]])
        if np.sign(blue_pitch) > 0 and np.sign(tmpPitchSetPoint) < 0:
            if abs(blue_pitch) < 10:
                tmpThrottle = 0.1
            elif abs(blue_pitch) < 30:
                tmpThrottle /= 50
            else:
                tmpThrottle /= 30
            
        # Stall Avoidance
        if self._fps_to_kts(tmpSpeed) <= 100 and state[info[StateInfo.SELF_DISTANCE_FT]] > 1000:
            tmpThrottle = 1.0

        # Ground Avoidance
        if state[info[StateInfo.SELF_SCORE_FLOOR_HEIGHT]] < 2500 and math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < 5:
            tmpAileron /= 5
            tmpElevator = min(tmpElevator/2, -0.5)
            tmpRudder /= 5
            tmpThrottle = 1.0

        if state[info[StateInfo.SELF_SCORE_FLOOR_HEIGHT]] < 2000 and math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < 5:
            tmpAileron = 0
            tmpElevator = -1
            tmpRudder = 0
            tmpThrottle = 2.0

        self.current_action = np.array([tmpAileron, tmpElevator, tmpRudder, tmpThrottle])

        aspect_angle = math.degrees(uc.aspect_angle())
        self._check_done(MA.MA4, angle_off, aspect_angle, state, info)
        self.step_count += 1

    def get_action(self):
        return self.current_action

    def get_done(self):
        return self.is_done