import math

from .current_status import current_status
from .current_pursuit import Current_pursuit


class observations():
    def __init__(self, AA, AO, HCA):
        self.aspect_angle = AA
        self.angle_off = AO
        self.heading_crossing_angle = HCA
        # self.deviation_angle_of_Blue = DAB
        # self.deviation_angle_of_Red = DAR
        self.current_status = current_status.Nothing
        self.current_pursuit = Current_pursuit.Nothing

        # calculate current getfs one of (Offensive, Defensive, Neutral)
        self._decide_current_status()
        self._decide_current_pursuit()

    # Getter
    def get_aspect_angle(self):
        return self.aspect_angle

    def get_angle_off(self):
        return self.angle_off

    def get_heading_crossing_angle(self):
        return self.heading_crossing_angle

    """
    def get_deviation_angle_of_Blue(self):
        return self.aspect_angle

    def get_deviation_angle_of_Red(self):
        return self.aspect_angle
    """

    def get_current_status(self):
        return self.current_status

    def get_current_pursuit(self):
        return self.current_pursuit

    # Setter
    def set_aspect_angle(self, new_AA):
        self.aspect_angle = new_AA

    def set_angle_off(self, new_AO):
        self.aspect_angle = new_AO

    def set_heading_crossing_angle(self, new_HCA):
        self.heading_crossing_angle = new_HCA

    """
    def set_deviation_angle_of_Blue(self, new_DAB):
        self.aspect_angle = new_DAB

    def set_deviation_angle_of_Red(self, new_DAR):
        self.aspect_angle = new_DAR
    """

    # private methods
    def _decide_current_status(self):
        if (self.aspect_angle + self.angle_off) < math.pi / 2:
            self.current_status = current_status.Offensive
        elif (self.aspect_angle + self.angle_off) > math.pi * 3 / 2:
            self.current_status = current_status.Defensive
        else:
            self.current_status = current_status.Neutral

    def _decide_current_pursuit(self):
        if 0 <= self.angle_off * 180 / math.pi <= 10:
            self.current_pursuit = Current_pursuit.Pure_pursuit
        elif 5 < self.angle_off * 180 / math.pi <= 20:
            if self.heading_crossing_angle <= self.aspect_angle:
                self.current_pursuit = Current_pursuit.Lead_pursuit
            else:
                self.current_pursuit = Current_pursuit.Lag_pursuit
        else:
            self.current_pursuit = Current_pursuit.Nothing
