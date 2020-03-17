from abc import ABC, abstractmethod
import math

import numpy as np

from ...constants import MA, Observation as obs, StateInfo


class TMAObject(ABC):
    """
    Abstract class to define GammaSky Task Macro Actions
    """

    @abstractmethod
    def __init__(self):
        #Anything you need to initialize the TMA
        self.step_count = 0
        self.is_done = False
        self.current_observation = None
        self.prev_alt = None
        self.prev_distance = None
        self.prev_aspect = None
        self.prev_macro_observation = None
        self.closure = 0

    @abstractmethod
    def selected(self, observation):
        #This method is called whenever this TMA is switched to.
        pass

    @abstractmethod
    def compute_action(self, observation, info):
        #Called every action update.
        pass

    @abstractmethod
    def get_action(self) -> np.ndarray:
        #Returns the current action from this TMA.
        pass

    @abstractmethod
    def get_done(self) -> bool:
        #Return boolean signifying if this TMA is done.
        pass

    def _kts_to_fps(self, knots):
        return knots * 1.68781
    
    def _fps_to_kts(self, fps):
        return fps / 1.68781
    
    def _calculate_g(self, bank_angle):
        return 1 / math.cos(bank_angle)
    
    def _calculate_closure(self, distance):
        if not self.prev_distance:
            self.prev_distance = distance
            return 0

        closure = (self.prev_distance - distance) / .02
        self.prev_distance = distance
        self.closure = closure

        return closure

    def _calculate_turn_radius(self, knots, bank_angle):
        return knots **2 / (11.26 * math.tan(bank_angle))

    def _is_inside_turn_circle(self, state, info):
        bandit_u = state[info[StateInfo.BANDIT_VELOCITIES_U_FPS]]
        bandit_v = state[info[StateInfo.BANDIT_VELOCITIES_V_FPS]]
        bandit_w = state[info[StateInfo.BANDIT_VELOCITIES_W_FPS]]
        bandit_speed = math.sqrt(bandit_u**2 + bandit_v**2 + bandit_w**2)

        bandit_knots = self._fps_to_kts(bandit_speed)
        bandit_bank_angle = state[info[StateInfo.BANDIT_ATTITUDE_ROLL_RAD]]
        turn_radius = min(6000, abs(self._calculate_turn_radius(bandit_knots, bandit_bank_angle)))

        return state[info[StateInfo.SELF_DISTANCE_FT]] <= 2 * turn_radius

    def _get_macro_observation(self, curr_ma, angle_off, aspect_angle, state, info):
        inside_turn_circle = self._is_inside_turn_circle(state, info)            
        angle_off = abs(angle_off)
        aspect_angle = abs(aspect_angle)
        tct_range = state[info[StateInfo.SELF_DISTANCE_FT]]
        closing_velocity = self._fps_to_kts(self._calculate_closure(tct_range))

        if not self.prev_aspect:
            self.prev_aspect = aspect_angle

        # 0 Ground Avoidance
        # [0, 0, 0, 0]
        ground_avoidance = math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]]) < 0 and abs(math.degrees(state[info[StateInfo.SELF_ATTITUDE_PITCH_RAD]])) > state[info[StateInfo.SELF_POSITION_H_SL_FT]] // 100

        # 1 Employment Conditions
        track = 500 < tct_range < 1000 and angle_off < 40 and aspect_angle < 40
        out_track_inside_snap = 1000 < tct_range < 3000 and angle_off < 40 and aspect_angle < 40
        inside_gun = tct_range < 500 and aspect_angle < 40 and closing_velocity < 50

        # 2 Overshoot Conditions
        flight_path_overshoot = tct_range > 1000 and angle_off > aspect_angle and closing_velocity > 0
        defensive_overshoot = tct_range < 1000 and aspect_angle > 40 and aspect_angle > self.prev_aspect and closing_velocity > 20

        # 3 Offensive Conditions
        tail_chase = angle_off < 60 and aspect_angle < 40 and tct_range > 6000
        turn_circle_alignment = angle_off < 40 and aspect_angle > 40 and closing_velocity > 0
        turn_circle_entry = aspect_angle > 40 and angle_off > 30 and abs(angle_off - aspect_angle) < 20
        maintain_close_range = angle_off < 40 and aspect_angle < 40 and tct_range < 6000

        # 4 Neutral Conditions
        neutral_away = angle_off > 60 and aspect_angle < 120
        neutral_opening = angle_off > 60 and aspect_angle < angle_off and closing_velocity < 0

        self.prev_aspect = aspect_angle

        if ground_avoidance:
             self.current_observation = obs.GROUND_AVOIDANCE
        elif track:
            self.current_observation = obs.TRACK
        elif out_track_inside_snap:
            self.current_observation = obs.OUT_TRACK_INSIDE_SNAP
        elif inside_gun:
            self.current_observation = obs.INSIDE_GUN
        elif flight_path_overshoot:
            self.current_observation = obs.FLIGHT_PATH_OVERSHOOT
        elif defensive_overshoot:
            self.current_observation = obs.DEFENSIVE_OVERSHOOT
        elif tail_chase:
            self.current_observation = obs.TAIL_CHASE
        elif turn_circle_alignment:
            self.current_observation = obs.TURN_CIRCLE_ALIGNMENT
        elif turn_circle_entry:
            self.current_observation = obs.TURN_CIRCLE_ENTRY
        elif maintain_close_range:
            self.current_observation = obs.MAINTAIN_CLOSE_RANGE
        elif neutral_away:
            self.current_observation = obs.NEUTRAL_AWAY
        elif neutral_opening:
            self.current_observation = obs.NEUTRAL_OPENING

        return self.current_observation
    
    def _check_done(self, curr_ma, angle_off, aspect_angle, state, info):
        # check if done
        macro_observation = self._get_macro_observation(curr_ma, angle_off, aspect_angle, state, info)
        if not macro_observation:
            self.prev_macro_observation = macro_observation

        if macro_observation != self.prev_macro_observation or self.step_count >= 1000:
            self.is_done = True
            self.step_count = 0
        
        self.prev_macro_observation = macro_observation
