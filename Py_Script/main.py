#main.py

from obstacle_detection import ObstacleDetection
from camera_feed import CameraFeed
from paint_optimization import PaintOptimization
from ai_camera import AICamera
from gui_handler import GUIHandler
import RPi.GPIO as GPIO
import sys
from PyQt6.QtWidgets import QApplication
from paint_app import MainWindow, RobotControl


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

        # Create an instance of the CameraFeed class
        self.camera_feed = CameraFeed(self)

        # Initialize the GUI
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow()

        # Connect the update_status_signal from the GUIHandler to the update_status method in the MainWindow
        self.gui_handler.update_status_signal.connect(self.main_window.update_status)

        # Connect the frame_signal from the CameraFeed to the update_camera_feed method in the MainWindow
        self.camera_feed.frame_signal.connect(self.main_window.update_camera_feed)

        # ObstacleDetection class
        self.obstacle_detection = ObstacleDetection(self.ai_camera)

        self.camera_feed.obstacle_signal.connect(self.obstacle_detection.process_obstacles)

       
        self.robot_control = RobotControl(port='/dev/ttyUSB0', baudrate=115200)

        # Create a GUIHandler instance and pass the RobotControl instance
        self.gui_handler = GUIHandler(self.robot_control)

        # Set up button callbacks to call the corresponding methods in the GUIHandler
        self.main_window.xp_button.clicked.connect(lambda: self.gui_handler.move_right_action(10))
        self.main_window.xm_button.clicked.connect(lambda: self.gui_handler.move_left_action(10))
        self.main_window.yp_button.clicked.connect(lambda: self.gui_handler.move_up_action(10))
        self.main_window.ym_button.clicked.connect(lambda: self.gui_handler.move_down_action(10))
        self.main_window.start_button.clicked.connect(self.gui_handler.activate_sprayer_action)
        self.main_window.stop_button.clicked.connect(self.gui_handler.deactivate_sprayer_action)
        self.main_window.pause_button.clicked.connect(self.gui_handler.pause_machine_action)
        self.main_window.restart_button.clicked.connect(self.gui_handler.resume_machine_action)

        # Set up GPIO pins for paint level sensor
        self.paint_level_pin = 18
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.paint_level_pin, GPIO.IN)

    def run(self):
        try:
            # Start the camera feed thread
            self.camera_feed.start()
            # Run the QApplication
            sys.exit(self.app.exec_())
        except Exception as e:
            print(f"An error occurred: {e}")

    def run_optimization(self):
        # Example input, replace with actual data
        building_edges = {(2, 2), (2, 3), (2, 4), (2, 5)}
        painting_areas = [((1, 1), (4, 1)), ((4, 4), (1, 4))]

        optimized_painting_commands = self.paint_optimizer._optimize_painting(building_edges, painting_areas)

    

    def check_paint_level(self):
        return GPIO.input(self.paint_level_pin)




if __name__ == "__main__":
    app = Application()
    app.run()
