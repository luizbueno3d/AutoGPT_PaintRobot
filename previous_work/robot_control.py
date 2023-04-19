import math
import time
from grbl import GRBL_Controller

class RobotController:
    def __init__(self, robot_width=200, robot_height=200, cable_length=1000, max_speed=200):
        self.robot_width = robot_width
        self.robot_height = robot_height
        self.cable_length = cable_length / 2
        self.max_speed = max_speed
        self.grbl = GRBL_Controller("COM3")
        self.grbl.initialize_grbl()
        self.x = 0
        self.y = 0

    def set_position(self, x, y):
        # Calculate cable lengths
        a = (self.robot_width / 2 - x)
        b = (self.robot_height / 2 - y)
        c = math.sqrt(a ** 2 + b ** 2)
        alpha = math.acos((self.cable_length ** 2 + c ** 2 - self.cable_length ** 2) / (2 * self.cable_length * c))
        beta = math.atan2(b, a)
        # Calculate cable angles
        motor_angle_1 = beta - alpha
        motor_angle_2 = beta + alpha
        motor_angle_3 = math.pi + beta + alpha
        motor_angle_4 = math.pi + beta - alpha
        # Calculate motor steps
        steps_1 = int(200 * motor_angle_1 / math.pi + 750)
        steps_2 = int(200 * motor_angle_2 / math.pi + 750)
        steps_3 = int(200 * motor_angle_3 / math.pi + 750)
        steps_4 = int(200 * motor_angle_4 / math.pi + 750)
        # Send motor commands
        self.grbl.send_command("G0 X{} Y{}".format(x, y))
        self.grbl.send_command("G0 Z0")
        self.grbl.send_command("G1 X0 Y0 F{}".format(self.max_speed))
        self.grbl.send_command("G1 Z-10")
        self.grbl.send_command("G1 X{} Y{} F{}".format(steps_1, steps_2, self.max_speed))
        self.grbl.send_command("G1 X{} Y{} F{}".format(steps_3, steps_4, self.max_speed))
        self.grbl.send_command("G1 X0 Y0 F{}".format(self.max_speed))
        self.grbl.send_command("G0 Z0")
        self.x = x
        self.y = y

    def paint(self):
        self.grbl.send_command("M3 S250")
        time.sleep(10)
        self.grbl.send_command("M5")

    def move(self, x, y):
        self.set_position(x, y)

    def stop(self):
        self.grbl.send_command("G0 Z0")
        self.grbl.send_command("M5")