# 
# Lebai robot instance
# Author: Yonnie Lu
# Email: zhangyong.lu@lebai.ltd
import json
import requests
import robot.api as api
from enum import Enum, unique
from time import sleep

@unique
class RobotState(Enum):
    DISCONNECTED = 0  # 已断开连接
    ESTOP = 1         # 急停停止状态
    BOOTING = 2       # 启动中
    ROBOT_OFF = 3     # 电源关闭
    ROBOT_ON = 4      # 电源开启
    IDLE = 5          # 空闲中
    BACKDRIVE = 6     # undefined
    RUNNING = 7       # 机器人运动运行中
    UPDATING = 8      # 更新固件中
    STARTING = 9      # 启动中
    STOPPING = 10     # 停止中
    TEACHING = 11     # 示教中
    STOP = 12         # 普通停止
    FINETUNING = 13   # 微调中


class Pose:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Rotation:
    def __init__(self, rz, ry, rx):
        self.Rz = rz
        self.Ry = ry
        self.Rx = rx

# 笛卡尔下的位置和姿态位置信息
class CartesianPos:
    def __init__(self, x, y, z, rz, ry, rx):
        self.pose = Pose(x, y, z)
        self.rotation = Rotation(rz, ry, rx)
    
    def __str__(self):
        return "pose({}, {}, {}), rotation({}, {}, {})".format(self.pose.x, self.pose.y, self.pose.z, self.rotation.Rz, self.rotation.Ry, self.rotation.Rx)

class Robot():
    def __init__(self, ip):
        self.ip = ip
        self.http_port = 80
        self.http_url = "http://{}:{}".format(self.ip, self.http_port)
        self.socket_port = 5171
        self.lua_port = 5180
    
    def cmd_via_http(self, cmd, data = None):
        req = ''
        if data is None:
            req = json.dumps({
                "cmd": cmd
            })
        else:
            req = json.dumps({
                "cmd": cmd,
                "data": data,
            })
        r = requests.post("{}{}".format(self.http_url, api.HTTP_ROBOT_ACTION), req)
        r = json.loads(r.text)
        return r

    def get_robot_data(self):
        r = self.cmd_via_http(api.HTTP_CMD_ROBOT_DATA)
        return r

    def get_robot_mode(self):
        mode = RobotState(self.get_robot_data()['data']['robot_mode'])
        return mode

    def get_target_joints(self):
        return self.get_robot_data()['data']['target_joint']

    def get_actual_joints(self):
        return self.get_robot_data()['data']['actual_joint']

    def get_target_tcp_pose(self):
        raw = self.get_robot_data()['data']['target_tcp_pose']
        return CartesianPos(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5])

    def get_actual_tcp_pose(self):
        raw = self.get_robot_data()['data']['actual_tcp_pose']
        return CartesianPos(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5])

    def move_check(self):
        mode = self.get_robot_mode()
        if mode == RobotState.ROBOT_ON or mode == RobotState.STOP or mode == RobotState.ESTOP: # start robot
            self.cmd_via_http(api.HTTP_CMD_START_SYS)
        elif mode == RobotState.TEACHING: # end teach
            self.cmd_via_http(api.HTTP_CMD_END_TEACH_MODE)
        mode = self.get_robot_mode()
        while mode != RobotState.IDLE:
            print('robot not ready, current mode: {}'.format(mode))
            sleep(1)
            mode = self.get_robot_mode()

    def movej(self, pose, is_joint_angle = True, acc = 1, vel = 1, time = 0):
        data ={
            "pose_to": pose,
            "is_joint_angle": is_joint_angle,
            "acceleration": acc,
            "velocity": vel,
            "time": time,
            "smooth_move_to_next": 0
        }
        return self.cmd_via_http(api.HTTP_CMD_MOVEJ, data)

    def movel(self, pose, is_joint_angle = True, acc = 1, vel = 1, time = 0):
        data ={
            "pose_to": pose,
            "is_joint_angle": is_joint_angle,
            "acceleration": acc,
            "velocity": vel,
            "time": time,
            "smooth_move_to_next": 0
        }
        return self.cmd_via_http(api.HTTP_CMD_MOVEL, data)

    
