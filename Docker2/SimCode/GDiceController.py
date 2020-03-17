from .fastcube_files.tma.ma1_lead import MA1LeadPursuit as TMA0
from .fastcube_files.tma.ma2_lag import MA2LagPursuit as TMA1
from .fastcube_files.tma.ma3_pure import MA3PurePursuit as TMA2
from .fastcube_files.tma.ma4_track import MA4TrackPursuit as TMA3

from .fastcube_files.getfs.unitChange import unitChange


from .fastcube_files.tma.constants import MA, Observation as obs

import numpy as np
import numpy.linalg as la
import math

class GDice():
    def __init__(self, Policy):
        #Initialize Everything
        self.Policy = Policy
        self.Action = [0,0,0,0]
        self.mObs = [0,0,0,0]
        self.CurrentNode = 0
        self.TMA = self.Policy.nodes[0].myTMA
        
        self.prev_distance = None
        self.prev_aspect = None

        self.TMASwitcher = {
            0: TMA0(),
            1: TMA1(),
            2: TMA2(),
	    3: TMA3()
        }

        #This is called ever step update.
    def compute_action(self, observation, info):
        self.TMASwitcher.get(self.TMA, lambda: "Invalid TMA").compute_action(observation, info)

        #Gets the current assigned action.
    def get_Action(self):
        return self.TMASwitcher.get(self.TMA, lambda: "Invalid TMA").get_action()

    def rot_mat_HP(self, a):
        # a : vector of heading and pitch angles in order.  Heading taken in degrees, pitch in rad
        # returns a 3x3 rotation matrix for Heading, Pitch.  Assume vector aligned with roll axis
        rot_Head = np.array([[np.cos(-a[0] * np.pi / 180), -np.sin(-a[0] * np.pi / 180), 0],
                             [np.sin(-a[0] * np.pi / 180), np.cos(-a[0] * np.pi / 180), 0],
                             [0, 0, 1]])
        rot_Pitch = np.array([[1, 0 ,0],
                              [0, np.cos(a[1]), -np.sin(a[1])],
                              [0, np.sin(a[1]), np.cos(a[1])]])
        rot_mat_HP = rot_Head.dot(rot_Pitch)
        return rot_mat_HP

        #This converts observations to macro observations.
    def mObsConversion(self, state, info):
        red_x = state[info['red_x_position_ft']]
        red_y = state[info['red_y_position_ft']]
        blue_x = state[info['blue_x_position_ft']]
        blue_y = state[info['blue_y_position_ft']]
        red_u = state[info['red_velocities_u_fps']]
        red_v = state[info['red_velocities_v_fps']]
        blue_u = state[info['blue_velocities_u_fps']]
        blue_v = state[info['blue_velocities_v_fps']]

        angleConverter = unitChange(
            [blue_x, blue_y, blue_u, blue_v],
            [red_x, red_y, red_u, red_v],
            state[info['blue_attitude_pitch_rad']],
            state[info['red_attitude_pitch_rad']]
            )
        angle_off = angleConverter.angle_off()
        aspect_angle = angleConverter.aspect_angle()

        inside_turn_circle = self._is_inside_turn_circle(state, info)
        angle_off = abs(angle_off)
        aspect_angle = abs(aspect_angle)
        tct_range = state[info['blue_distance_ft']]
        closing_velocity = self._fps_to_kts(self._calculate_closure(tct_range))

        if not self.prev_aspect:
            self.prev_aspect = aspect_angle

        # 0 Ground Avoidance
        # [0, 0, 0, 0]
        ground_avoidance = math.degrees(state[info['blue_attitude_pitch_rad']]) < 0 and abs(math.degrees(state[info['blue_attitude_pitch_rad']])) > state[info['blue_position_h_sl_ft']] // 100

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

        self.mObs = self.current_observation

        #This is called to check if a node transition should occur.
    def checkIfDone(self, observation, info):
        if(self.TMASwitcher.get(self.TMA, lambda: "Invalid TMA").get_done()):
            self.mObsConversion(observation, info)
            self.nextTMA(self.mObs)
            self.nodeSwitch(observation)

        #Switches to a new node and TMA.
    def nextTMA(self, mObs):
        mObsIDX = np.array(mObs).dot(2**np.arange(len(mObs))[::-1])
        [self.CurrentNode, self.TMA] = self.Policy.getNextTMAIdx(self.CurrentNode, mObsIDX)

        #Gets the current assigned action.
    def nodeSwitch(self, observation):
        self.TMASwitcher.get(self.TMA, lambda: "Invalid TMA").selected(observation)

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
        red_u = state[info['red_velocities_u_fps']]
        red_v = state[info['red_velocities_v_fps']]
        red_w = state[info['red_velocities_w_fps']]
        red_speed = math.sqrt(red_u**2 + red_v**2 + red_w**2)

        red_knots = self._fps_to_kts(red_speed)
        red_bank_angle = state[info['red_attitude_roll_rad']]
        turn_radius = min(3000, abs(self._calculate_turn_radius(red_knots, red_bank_angle)))

        return state[info['blue_distance_ft']] <= 2 * turn_radius
