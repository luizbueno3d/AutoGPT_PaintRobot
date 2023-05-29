from detection import ObstacleDetection
from map_wall import PaintOptimization
import sys
from PyQt6.QtWidgets import QApplication
from paint_app import MainWindow, RobotControl
sys.path.append("/Users/luizbueno/AI/py_paint_robot/Py_Script/paint_app")
from ai_camera import AICamera
#from gui_handler import GUIHandler
import RPi.GPIO as GPIO


class GUIHandler:
    def __init__(self, robot_control):
        self.robot_control = robot_control

    def move_right_action(self, distance):
        self.robot_control.move_x_positive(distance)

    def move_left_action(self, distance):
        self.robot_control.move_x_negative(distance)

    def move_up_action(self, distance):
        self.robot_control.move_y_positive(distance)

    def move_down_action(self, distance):
        self.robot_control.move_y_negative(distance)

    def activate_sprayer_action(self):
        self.robot_control.send_gcode("G1 E10 F300")  # Extrude 10mm of filament at 300mm/min

    def deactivate_sprayer_action(self):
        self.robot_control.send_gcode("G1 E-10 F300")  # Retract 10mm of filament at 300mm/min

    def pause_machine_action(self):
        self.robot_control.send_gcode("M25")  # Pause SD print (also works for USB print)

    def resume_machine_action(self):
        self.robot_control.send_gcode("M24")  # Resume SD print (also works for USB print)


class Application:
    def __init__(self):
        # Load your AI model here (replace 'model_path' with the actual path to your AI model)
        self.ai_camera = AICamera(model_path='model_path')
        self.paint_optimizer = PaintOptimization()

        # Initialize the RobotControl instance
        self.robot_control = RobotControl(baudrate=115200)

        # Initialize the GUI
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self.robot_control)

        # Create a GUIHandler instance and pass the RobotControl instance
        self.gui_handler = GUIHandler(self.robot_control)

        # ObstacleDetection class
        self.obstacle_detection = ObstacleDetection(self.ai_camera)

        # Set up button callbacks to call the corresponding methods in the GUIHandler
        self.main_window.start_button.clicked.connect(self.gui_handler.activate_sprayer_action)
        self.main_window.stop_button.clicked.connect(self.gui_handler.deactivate_sprayer_action)
        self.main_window.pause_button.clicked.connect(self.gui_handler.pause_machine_action)
        self.main_window.restart_button.clicked.connect(self.gui_handler.resume_machine_action)

        # Set up GPIO pins for paint level sensor
        self.paint_level_pin = 18
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.paint_level_pin, GPIO.IN)

    # ... rest of the Application class ...


if __name__ == "__main__":
    app = Application()
    app.run()
