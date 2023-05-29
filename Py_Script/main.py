from detection import ObstacleDetection
import sys
from PyQt6.QtWidgets import QApplication
from paint_app import MainWindow, RobotControl
from ai_camera import AICamera


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
        # self.paint_optimizer = PaintOptimization() # - for future iteration

        # Initialize the RobotControl instance
        self.robot_control = RobotControl(baudrate=115200)

        # Initialize the GUI
        self.app = QApplication(sys.argv)
        self.main_window = MainWindow(self.robot_control)

        # Create a GUIHandler instance and pass the RobotControl instance
        self.gui_handler = GUIHandler(self.robot_control)

        # ObstacleDetection class
        # self.obstacle_detection = ObstacleDetection(self.ai_camera) # - for future iteration

        # Set up button callbacks to call the corresponding methods in the GUIHandler
        self.main_window.start_button.clicked.connect(self.gui_handler.activate_sprayer_action)
        self.main_window.stop_button.clicked.connect(self.gui_handler.deactivate_sprayer_action)
        self.main_window.pause_button.clicked.connect(self.gui_handler.pause_machine_action)
        self.main_window.restart_button.clicked.connect(self.gui_handler.resume_machine_action)

    def run(self):
        try:

            # Show the main window
            self.main_window.show()

            # Run the QApplication
            sys.exit(self.app.exec())
        except Exception as e:
            print(f"An error occurred: {e}")



if __name__ == "__main__":
    app = Application()
    app.run()
