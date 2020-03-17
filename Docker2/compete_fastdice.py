#!/usr/bin/env python
# Prepared for DARPA AlphaDogfight Trials
# Developed by JHU/APL, Aug 2019
import time
import logging
import logging.config
#import yaml

from adt import Configuration, Manager

import adt.agents.bud_fsm as red
from SimCode import fastcube as blue

import sample_test as test

import numpy as np
import boto3
import pickle
import argparse

from decimal import *


class Configurator:
    def __init__(self, logger):
        #LOAD UP ALL OUR IMPORTANT INFO
        #Initialize-------------------------------------------------------------------------------------------
        #Take in argumetns.
        parser = argparse.ArgumentParser(description="Accepts Integers.")
        parser.add_argument('integers', metavar='N', type=int, nargs='+', help='an integer for the accumulator')
        args = parser.parse_args()
        trialNum = args.integers[0]
        iteration = args.integers[1]

        #Grab Table Entry
        db = boto3.resource("dynamodb", region_name = 'us-west-1')
        table = db.Table("ADFEval" + str(iteration))
        simInfo = table.get_item(
        	Key={
        		'TrialNum': trialNum,
        	}
        )['Item']

        policyNum = simInfo['PolicyNum']
        confNum = simInfo['Configuration']

        #Grab Policy
        s3 = boto3.resource('s3', region_name = 'us-west-1')
        bucket = s3.Bucket('adfproject')
        directory_name = "policy" + str(iteration)
        with open('pdump', 'wb') as data:
        	bucket.download_fileobj(directory_name + '/policy', data)
        with open('pdump', 'rb') as data:
        	Controller = pickle.load(data)
        #Set to sampled policy.
        #This controller can be made a lot more light weight later.
        Controller.setGraph(int(policyNum))

        #Grab Configuration
        directory_name = "config" + str(iteration)
        bucket.download_file(directory_name + '/rc' + str(confNum) + '.xml', "conf.xml")

        #Initiation Finish

        configuration = Configuration("conf.xml")
        # config.write_configuration("sample_output_config.xml")

        self.manager = Manager(logger, configuration)
        self.gym_env = self.manager.get_gym_env()
        self.red = red.Agent(self.gym_env.red_action_space, self.gym_env.red_observation_space)
        self.blue = blue.Agent(self.gym_env.blue_action_space, self.gym_env.blue_observation_space)
        self.blue.setpolicy(Controller)
        self.manager.set_red_agent(self.red)
        self.manager.set_blue_agent(self.blue)
        self.test = test.Sample(logger, self.manager)

        #Update Table
        sim_time = self.manager._red.state[self.manager._red.info['red_simulation_sim_time_sec']]/300
        getcontext().prec = 3
        reward = Decimal(self.manager._blue.reward) - Decimal(self.manager._red.reward)
        if(self.manager._red.reward <= -1):
             reward += Decimal(1 - sim_time)
        table.update_item(
            Key={
        		'TrialNum': trialNum,
            },
            UpdateExpression="SET reward = :r",
            ExpressionAttributeValues={
                ':r': reward,
            }
        )




if __name__ == "__main__":
#    with open('logger_config.yaml', 'r') as f:
#        config = yaml.safe_load(f.read())
#        logfile = f'{config["handlers"]["file"]["filename"]}-{time.strftime("%Y%m%d-%H%M%S",time.gmtime(time.time()))}.log'
#        config["handlers"]["file"]["filename"] = logfile
#        logging.config.dictConfig(config)

    logger = logging.getLogger(__name__)

    Configurator(logger)
