#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Python sdk samples
import yaml
from robot.robot import Robot, RobotState
from math import pi

config = ''

def load_config():
    with open('config.yml') as f:
        global config
        config = yaml.load(f, Loader=yaml.FullLoader)

if __name__ == '__main__':
    load_config()
    robot = Robot(config['robot']['ip'])
    print("current robot mode: {}".format(robot.get_robot_mode()))
    print(robot.get_target_joints())
    print(robot.get_actual_joints())
    print(robot.get_target_tcp_pose())
    print(robot.get_actual_tcp_pose())
    robot.move_check()
    print(robot.movej([0, 0, 0, 0, 0, 0], True))
    print(robot.movej([0, -pi/4, pi/2, -pi/4, pi/2, 0], True))
    print(robot.movel([-0.3, -0.1, 0.2, -pi/2, 0, pi/2], False))