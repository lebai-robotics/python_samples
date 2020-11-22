# 
# Lebai robot instance
# Author: Yonnie Lu
# Email: zhangyong.lu@lebai.ltd
import json
import requests
import robot.api as api
from enum import Enum, unique
from time import sleep
import asyncio
import websockets

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

@unique
class ReqProtocol(Enum):
    HTTP = 0    # http协议
    WS = 1      # Websocket协议

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
        self.ws_url = "ws://{}/ws/public".format(self.ip)
        self.ws_cmd_id = 0
        self.socket_port = 5171
        self.lua_port = 5180
    
    def get_ws_cmd_id(self):
        self.ws_cmd_id += 1
        return self.ws_cmd_id

    def build_req_json(self, cmd, data = None, id = 0):
        req = {"cmd": cmd}
        if data is not None:
            req["data"] = data
        if id > 0:
            req["id"] = id

        return json.dumps(req)

    def cmd_via_http(self, cmd, data = None):
        r = requests.post("{}{}".format(self.http_url, api.HTTP_ROBOT_ACTION), self.build_req_json(cmd, data))
        r = json.loads(r.text)
        # print("http resp:{}".format(r))
        return r

    async def cmd_via_ws(self, cmd, data = None):
        async with websockets.connect(self.ws_url) as websocket:
            self.ws_cmd_id += 1
            await websocket.send(self.build_req_json(cmd, data, self.get_ws_cmd_id()))
            resp = await websocket.recv()
            r = json.loads(resp)
            # print("ws resp:{}".format(r))
            return r

    def get_robot_data(self, rp = ReqProtocol.HTTP):
        if rp == ReqProtocol.HTTP:
            return self.cmd_via_http(api.CMD_ROBOT_DATA)
        elif rp == ReqProtocol.WS:
            return asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_ROBOT_DATA))

    def get_robot_mode(self, rp = ReqProtocol.HTTP):
        return RobotState(self.get_robot_data(rp)['data']['robot_mode'])

    def get_target_joints(self, rp = ReqProtocol.HTTP):
        return self.get_robot_data(rp)['data']['target_joint']

    def get_actual_joints(self, rp = ReqProtocol.HTTP):
        return self.get_robot_data(rp)['data']['actual_joint']

    def get_target_tcp_pose(self, rp = ReqProtocol.HTTP):
        raw = self.get_robot_data(rp)['data']['target_tcp_pose']
        return CartesianPos(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5])

    def get_actual_tcp_pose(self, rp = ReqProtocol.HTTP):
        raw = self.get_robot_data(rp)['data']['actual_tcp_pose']
        return CartesianPos(raw[0], raw[1], raw[2], raw[3], raw[4], raw[5])

    def move_check(self, rp = ReqProtocol.HTTP):
        mode = self.get_robot_mode()
        if mode == RobotState.ROBOT_ON or mode == RobotState.STOP or mode == RobotState.ESTOP: # start robot
            if rp == ReqProtocol.HTTP:
                self.cmd_via_http(api.CMD_START_SYS)
            elif rp == ReqProtocol.WS:
                asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_START_SYS))
        elif mode == RobotState.TEACHING: # end teach
            if rp == ReqProtocol.HTTP:
                self.cmd_via_http(api.CMD_END_TEACH_MODE)
            elif rp == ReqProtocol.WS:
                asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_END_TEACH_MODE))
        mode = self.get_robot_mode()
        while mode != RobotState.IDLE:
            print('robot not ready, current mode: {}'.format(mode))
            sleep(1)
            mode = self.get_robot_mode()

    def movej(self, pose, is_joint_angle = True, acc = 1, vel = 1, time = 0, rp = ReqProtocol.HTTP):
        data ={
            "pose_to": pose,
            "is_joint_angle": is_joint_angle,
            "acceleration": acc,
            "velocity": vel,
            "time": time,
            "smooth_move_to_next": 0
        }
        if rp == ReqProtocol.HTTP:
            return self.cmd_via_http(api.CMD_MOVEJ, data)
        elif rp == ReqProtocol.WS:
            return asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_MOVEJ, data))

    def movel(self, pose, is_joint_angle = True, acc = 1, vel = 1, time = 0, rp = ReqProtocol.HTTP):
        data ={
            "pose_to": pose,
            "is_joint_angle": is_joint_angle,
            "acceleration": acc,
            "velocity": vel,
            "time": time,
            "smooth_move_to_next": 0
        }
        if rp == ReqProtocol.HTTP:
            return self.cmd_via_http(api.CMD_MOVEL, data)
        elif rp == ReqProtocol.WS:
            return asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_MOVEL, data))
    
    def stop_move(self, rp = ReqProtocol.HTTP):
        if rp == ReqProtocol.HTTP:
            return self.cmd_via_http(api.CMD_STOP_MOVE)
        elif rp == ReqProtocol.WS:
            return asyncio.get_event_loop().run_until_complete(self.cmd_via_ws(api.CMD_STOP_MOVE))
    
