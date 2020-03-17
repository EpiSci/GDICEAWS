import math

import numpy as np
import numpy.linalg as la

from ...constants import MA, StateInfo
from .. import inner, middle, outer
from ...getfs.unitChange import unitChange
from .tma import TMAObject

class MA1LeadPursuit(TMAObject):
    """
    Lead pursuit towards bandit with out of plane scaled to closing velocity with ground avoidance routine
    """
    def __init__(self):
        super().__init__()
        # Pid controllers
        self.inner = inner.Inner()
        self.middle = middle.Middle()
        self.outer = outer.Outer()

        self.flag = False

    def __str__(self):
        return MA.MA1
    
    def selected(self, observation):
        self.is_done = False
        self.inner.reset()
        self.middle.reset()
        self.outer.reset()

    def compute_action(self, observation, info):
        state = observation

        # Update the observations as appropriate
        currentTime = state[info[StateInfo.SELF_SIMULATION_TIME_SEC]]
        blue_u = state[info[StateInfo.SELF_VELOCITIES_U_FPS]]
        blue_v = state[info[StateInfo.SELF_VELOCITIES_V_FPS]]
        blue_w = state[info[StateInfo.SELF_VELOCITIES_W_FPS]]

        tmpSpeed = math.sqrt(blue_u**2 + blue_v**2 + blue_w**2)
        blue_roll_rads = state[info[StateInfo.SELF_ATTITUDE_ROLL_RAD]]

        # Calculate bank angle to point to red
        distance = state[info[StateInfo.SELF_DISTANCE_FT]]
        rel_alt = state[info[StateInfo.BANDIT_POSITION_H_SL_FT]] - state[info[StateInfo.SELF_POSITION_H_SL_FT]]
        bank_angle = 90 - math.degrees(math.asin(rel_alt / distance))
        if bank_angle > 0:
            bank_angle = min(80, bank_angle)
        else:
            bank_angle = max(-80, bank_angle)

        blue_heading_rad = math.radians(state[info[StateInfo.SELF_ATTITUDE_PSI_DEG]])
        blue_x = state[info[StateInfo.SELF_X_POSITION]]
        blue_y = state[info[StateInfo.SELF_Y_POSITION]]
        blue_v = state[info[StateInfo.SELF_VELOCITIES_V_FPS]]
        blue_w = state[info[StateInfo.SELF_VELOCITIES_W_FPS]]
        blue_state = np.array([blue_x, blue_y, blue_u, blue_v])

        red_heading_rad = math.radians(state[info[StateInfo.BANDIT_ATTITUDE_PSI_DEG]])
        red_x = state[info[StateInfo.BANDIT_X_POSITION]]
        red_y = state[info[StateInfo.BANDIT_Y_POSITION]]
        red_u = state[info[StateInfo.BANDIT_VELOCITIES_U_FPS]]
        red_v = state[info[StateInfo.BANDIT_VELOCITIES_V_FPS]]
        red_state = np.array([red_x, red_y, red_u, red_v])

        uc = unitChange(blue_state, red_state, blue_heading_rad, red_heading_rad)
        angle_off = math.degrees(uc.angle_off())

        if angle_off > 0:
            bank_angle = min(-bank_angle, bank_angle)
            bank_angle -= 10
        else:
            bank_angle = max(-bank_angle, bank_angle)
            bank_angle += 10
        
        self.inner.channels[0].updateObservation([currentTime, blue_roll_rads])
        self.inner.channels[0].updateSetpoint(math.radians(bank_angle))
        tmpAileronCmd = self.inner.channels[0].computeOutput()

        # Calculate elevator control for desired G
        self.outer.channels[0].updateObservation([currentTime, angle_off])
        self.outer.channels[0].updateSetpoint(0)
        tmpSpeedSetpoint = self._kts_to_fps(self.outer.channels[0].computeOutput())   #target speed from AO?

        self.middle.channels[1].updateObservation([currentTime, tmpSpeed])
        self.middle.channels[1].updateSetpoint(tmpSpeedSetpoint)
        tmpGSetPoint = self.middle.channels[1].computeOutput()

        G = abs(tmpSpeed * state[[info[StateInfo.SELF_VELOCITIES_Q_RAD_SEC]]] / 32.2)
        self.inner.channels[1].updateObservation([currentTime, G])
        self.inner.channels[1].updateSetpoint(tmpGSetPoint)
        tmpElevatorCmd = self.inner.channels[1].computeOutput()

        # Calculate throttle control for desired G
        self.middle.channels[2].updateObservation([currentTime, tmpSpeed])
        self.middle.channels[1].updateSetpoint(tmpSpeedSetpoint)
        tmpThrottleCmd = self.middle.channels[2].computeOutput()
        xy_range =  math.sqrt((red_x - blue_x) ** 2 + (red_y - blue_y) ** 2)
        if xy_range <= 6000:
            red_w = state[info[StateInfo.BANDIT_VELOCITIES_W_FPS]]
            tmpSpeedSetpoint = self._fps_to_kts(la.norm([red_u, red_v, red_w]))
            self.middle.channels[2].updateSetpoint(tmpSpeedSetpoint)
            tmpThrottleCmd = self.middle.channels[2].computeOutput()
        else:
            tmpThrottleCmd = 2.0

        # Calculate rudder control
        self.inner.channels[3].updateObservation([currentTime, angle_off])
        self.inner.channels[3].updateSetpoint(0)
        tmpRudderCmd = self.inner.channels[3].computeOutput()
        
        if abs(angle_off) > 170:
            bank_angle = 90
            tmpAileronCmd = -0.8
            tmpElevatorCmd = -1
            tmpThrottleCmd = 2.0

        if not self.prev_alt:
            self.prev_alt = state[info[StateInfo.SELF_POSITION_H_SL_FT]]

        # Max pull if outside turn circle
        if self._is_inside_turn_circle(state, info):
            tmpElevatorCmd = -1

        # Don't pull until LV on bandit
        if abs(abs(math.degrees(blue_roll_rads)) - abs(bank_angle)) > 15:
            tmpElevatorCmd /= 5

        # Limit dive angle
        if math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < -state[info[StateInfo.SELF_POSITION_H_SL_FT]] / 100:
            tmpAileronCmd /= 10
            tmpElevatorCmd /=5
            tmpThrottleCmd = 2.0

        # Ground Avoidance
        if state[info[StateInfo.SELF_SCORE_FLOOR_HEIGHT]] < 2500 and math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < 5:
            tmpAileronCmd /= 2
            tmpElevatorCmd = min(tmpElevatorCmd/2, -0.25)
            tmpRudderCmd /= 5
            tmpThrottleCmd /= 2

        if state[info[StateInfo.SELF_SCORE_FLOOR_HEIGHT]] < 2000 and math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < 5:
            tmpAileronCmd = 0
            tmpElevatorCmd = -1
            tmpRudderCmd = 0
            tmpThrottleCmd = 2.0

        self.prev_alt = state[info[StateInfo.SELF_POSITION_H_SL_FT]]
        self.current_action = np.array([tmpAileronCmd, tmpElevatorCmd, tmpRudderCmd, tmpThrottleCmd])
        
        aspect_angle = math.degrees(uc.aspect_angle())
        self._check_done(MA.MA1, angle_off, aspect_angle, state, info)
        self.step_count += 1

    def get_action(self):
        return self.current_action

    def get_done(self):
        return self.is_done

