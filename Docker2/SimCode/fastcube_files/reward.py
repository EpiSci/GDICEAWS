import numpy as np
import math

from .getfs import unitChange
from .getfs import observations
from .getfs.current_pursuit import Current_pursuit as current_pursuit

import random


class Reward():
    def __init__(self):
        # Blue
        self.blue_position = None
        self.blue_vector = None

        # Red
        self.red_position = None
        self.red_vector = None

        # Pa
        self.pa_vector = None

        self.current_pursuit = None

    def __call__(self, blueState, redState, pursuit=None):
        """
        Assume each state has shape
        (float)x_rel_ground_center_m
        (float)y_rel_ground_center_m
        (float)z_rel_ground_center_m
        (float)u_mps
        (float)v_mps
        (float)w_mps
        """
        # Blue
        self.blue_position = np.array([blueState[0], blueState[1], blueState[2]])
        self.blue_vector = np.array([blueState[3], blueState[4], blueState[5]])

        # Red
        self.red_position = np.array([redState[0], redState[1], redState[2]])
        self.red_vector = np.array([redState[3], redState[4], redState[5]])

        self.u_c = unitChange.unitChange(blueState, redState)
        self.obs = observations.observations(self.u_c.aspect_angle(), self.u_c.angle_off(), self.u_c.heading_crossing_angle())

        if not isinstance(pursuit, current_pursuit):
            raise TypeError("Pursuit should be getfs.current_status")

        # Current pursuit
        self.current_pursuit_want = pursuit

        return self._calculate()


    def _calculate(self):
        # Reward of height
        h_delta = self.blue_position[2] - self.red_position[2]
        if h_delta < 2000:
            R_height_rel = h_delta / 1000
        else:
            R_height_rel = -h_delta / 1000 + 4

        if self.blue_position[2] < 300:
            R_height_own = self.blue_position[2]/200 - 3
        else:
            R_height_own = 0

        # Reward of velocity
        blue_velocity = math.sqrt(self.blue_vector[0]**2 + self.blue_vector[1]**2 + self.blue_vector[2]**2)
        red_velocity = math.sqrt(self.red_vector[0]**2 + self.red_vector[1]**2 + self.red_vector[2]**2)
        v_delta = blue_velocity - red_velocity

        R_velocity_rel = v_delta / 100

        if blue_velocity > 50:
            R_velocity_own = blue_velocity/100 - 0.5
        else:
            R_velocity_own = 0

        # Reward of score
        d = (self.blue_position[0] - self.red_position[0]) ** 2
        d += (self.blue_position[1] - self.red_position[1]) ** 2
        d += (self.blue_position[2] - self.red_position[2]) ** 2
        d = math.sqrt(d)
        d_opt = 700
        K = 600

        R_score = 1 - (abs(self.obs.get_aspect_angle() + self.obs.get_angle_off()) / math.pi)
        R_score *= math.exp(-(abs(d-d_opt))/(K*math.pi))

        if self.current_pursuit_want == self.obs.get_current_pursuit():
            R_pursuit = 10
        else:
            R_pursuit = -1

        R = R_height_rel + R_height_own + R_velocity_rel + R_velocity_own + R_score + R_pursuit + 3.6

        return R

# if __name__ == "__main__":
#     """ Select random two vectors """
#     # Our flight
#     B_x = random.uniform(0, 1)
#     B_y = random.uniform(0, 1)
#     B_z = random.uniform(0, 1)
#     B_u = random.uniform(-0.5, 0.5)
#     B_v = random.uniform(-0.5, 0.5)
#     B_w = random.uniform(-0.5, 0.5)

#     # Target flight
#     R_x = random.uniform(0, 1)
#     R_y = random.uniform(0, 1)
#     R_z = random.uniform(0, 1)
#     R_u = random.uniform(-0.5, 0.5)
#     R_v = random.uniform(-0.5, 0.5)
#     R_w = random.uniform(-0.5, 0.5)


#     r = reward()
#     blue_state = np.array([B_x, B_y, B_z, B_u, B_v, B_w])
#     red_state = np.array([R_x, R_y, R_z, R_u, R_v, R_w])
#     reward_calculated = r(blue_state, red_state, current_pursuit.Pure_pursuit)

#     print(reward_calculated)






































