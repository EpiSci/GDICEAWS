"""
    This agent flies straight and level, at a fixed speed, using a PID controller.
"""
import time
import numpy as np
import math
import gym
from .GDiceController import GDice

from adt import AgentBase

class Agent(AgentBase):
    def __init__(self, action_space: gym.spaces.Box, observation_space: gym.spaces.Box):
        super(Agent, self).__init__("Fastcube", action_space,observation_space )

    def reset(self):
        super(Agent, self).reset()

    def setpolicy(self, policy):
        self.GDice = GDice(policy)

    def compute_action(self, sim_done: bool):
        state = self.get_state()
        info = self.get_info()

        self.GDice.compute_action(state, info)
        self.set_action(self.GDice.get_Action())
        self.GDice.checkIfDone(state, info)
