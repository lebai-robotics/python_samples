#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Python sdk samples
import yaml
from robot.robot import Robot, RobotState, ReqProtocol
from math import pi
import robot.api as api
import asyncio

config = ''

def load_config():
    with open('config.yml') as f:
        global config
        config = yaml.load(f, Loader=yaml.FullLoader)

if __name__ == '__main__':
    load_config()
    robot = Robot(config['robot']['ip'])
    asyncio.get_event_loop().run_until_complete(robot.cmd_via_ws(api.CMD_START_SYS))

    # 1. send cmd via http
    print("========================================")
    print("The following cmd was sent via http")
    print("current robot mode: {}".format(robot.get_robot_mode()))
    print(robot.get_target_joints())
    print(robot.get_actual_joints())
    print(robot.get_target_tcp_pose())
    print(robot.get_actual_tcp_pose())
    robot.move_check()
    print(robot.movej([0, 0, 0, 0, 0, 0], True, 1, 1, 0))
    print(robot.movej([0, -pi/4, pi/2, -pi/4, pi/2, 0], True, 1, 1, 0))
    print(robot.movel([-0.3, -0.1, 0.2, -pi/2, 0, pi/2], False, 1, 1, 0))
    print("========================================")

    # 2. send cmd via ws
    print("The following cmd was sent via websocket")
    
    print("current robot mode: {}".format(robot.get_robot_mode(ReqProtocol.WS)))
    print(robot.get_target_joints(ReqProtocol.WS))
    print(robot.get_actual_joints(ReqProtocol.WS))
    print(robot.get_target_tcp_pose(ReqProtocol.WS))
    print(robot.get_actual_tcp_pose(ReqProtocol.WS))
    robot.move_check(ReqProtocol.WS)
    print(robot.movej([0, 0, 0, 0, 0, 0], True, 1, 1, 0, ReqProtocol.WS))
    print(robot.movej([0, -pi/4, pi/2, -pi/4, pi/2, 0], True, 1, 1, 0, ReqProtocol.WS))
    print(robot.movel([-0.3, -0.1, 0.2, -pi/2, 0, pi/2], False, 1, 1, 0, ReqProtocol.WS))
    print("========================================")