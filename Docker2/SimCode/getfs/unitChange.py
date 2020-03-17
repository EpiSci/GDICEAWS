import math
import numpy as np


class unitChange():
    def __init__(self, blueState, redState, blueHeadingAngle, redHeadingAngle):
        """
        Assume each state has shape
        (float)x_rel_ground_center_m
        (float)y_rel_ground_center_m
        (float)u_mps
        (float)v_mps
        (rad)heading angle
        """

        # Blue
        self.blue_position = np.array([blueState[0], blueState[1]])
        self.blue_vector = self._rotate([0, 0], np.array([blueState[3], blueState[2]]), blueHeadingAngle)

        # Red
        self.red_position = np.array([redState[0], redState[1]])
        self.red_vector = self._rotate([0, 0], np.array([redState[3], redState[2]]), redHeadingAngle)

        # Pa
        self.pa_vector = np.array([redState[0] - blueState[0], redState[1] - blueState[1]])

    def _magnitude_vector(self, vector):
        return np.sqrt(np.sum(vector ** 2))

    def _angle(self, vector1, vector2):  # return radians
        return np.arccos(
            (np.dot(vector1, vector2)) / (self._magnitude_vector(vector1) * self._magnitude_vector(vector2)))

    def angle_off(self):
        return self._signed_angle(self.blue_vector, self.pa_vector)

    def aspect_angle(self):
        return self._signed_angle(self.red_vector, self.pa_vector)

    def heading_crossing_angle(self):
        return self._signed_angle(self.red_vector, self.blue_vector)

    """
    def attacker_deviation_angle(self):
        return self._angle(self.blue_vector, self.pa_vector)

    def target_deviation_angle(self):
        return math.pi-self._angle(self.red_vector, self.pa_vector)
    """

    def closure_velocity(self):
        return (self.red_position - self.blue_position) * (
            np.dot(self.red_vector - self.blue_vector, self.red_position - self.blue_position)) / (
                       self._magnitude_vector(self.red_position - self.blue_position) ** 2)

    def closure_speed(self):
        return (np.dot(self.red_vector - self.blue_vector,
                       self.red_position - self.blue_position)) / self._magnitude_vector(
            self.red_position - self.blue_position)

    def _signed_angle(self, vector1, vector2):
        angle = np.arctan2(vector2[1], vector2[0]) - np.arctan2(vector1[1], vector1[0])
        if -2*math.pi <= angle <= -math.pi:  # -360 <= angle <= -180
            angle += 2*math.pi
        elif math.pi <= angle <= 2*math.pi:  # 180 <= angle <= 360
            angle -= 2*math.pi
        return angle

    def _rotate(self, origin, vector, theta):  # rotate vector around origin by theta (rad)
        clockwise_theta = 2 * math.pi - theta
        xr = math.cos(clockwise_theta) * (vector[0] - origin[0]) - math.sin(clockwise_theta) * (vector[1] - origin[1]) + \
             origin[0]
        yr = math.sin(clockwise_theta) * (vector[0] - origin[0]) + math.cos(clockwise_theta) * (vector[1] - origin[1]) + \
             origin[1]
        return np.array([xr, yr])