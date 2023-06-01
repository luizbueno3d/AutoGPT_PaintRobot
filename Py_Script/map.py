import numpy as np
import logging
import time

class WallMapping:
    """Class for mapping the wall and generating G-code for painting."""
    def __init__(self, robot_control, main_window):
        self.corner_points = []
        self.g_code = ""
        self.robot_control = robot_control
        self.main_window = main_window


    def map_manually(self):
        """Maps manually (without camera)."""
        logging.info("Mapping manually...")
        self.g_code = self.map_manually_and_generate_gcode(self.corner_points)

    def map_manually_and_generate_gcode(self, points):
        """Generates G-code for the entire rectangular area."""
        g_code = "G-code from manual"
        return g_code

    def set_corner(self):
        """Sets the corner point based on the current position."""
        x, y = self.get_current_coordinates()
        self.corner_points.append((x, y))
        logging.info(f"Corner point set at: {x}, {y}")

    def get_current_coordinates(self):
        retries = 3  # Number of times to retry if response is not in expected format
        while retries > 0:
            response = self.robot_control.send_gcode("M114")
            time.sleep(1)  # Add a delay of 1 second
            print(f"Response from M114 command: {response}")  # Print the response
            coordinates = response.split(' ')
            if len(coordinates) >= 3:
                x = float(coordinates[0].split(':')[1])
                y = float(coordinates[1].split(':')[1])
                return x, y
            else:
                print(f"Unexpected response from M114 command: {response}")
                retries -= 1
        return None, None  # Return default values if response is not in expected format after all retries


    def confirm_mapping(self):
        """Confirms mapping."""
        logging.info(f"Start mapping area from point {self.corner_points[0]} to point {self.corner_points[1]}?")
        return True

    def store_gcode(self, g_code):
        """Stores the generated G-code."""
        self.g_code = g_code

    def mapping_ready_message(self):
        """Returns the message for when the painting area is ready."""
        return "Painting Area READY: Click Start Painting Area"

    def start_painting_area(self):
        """Starts the painting process."""
        self.execute_gcode(self.g_code)
        self.main_window.update_command_display()


    def get_stored_gcode(self):
        """Retrieves the stored G-code."""
        return self.g_code

    def execute_gcode(self, g_code):
        """Executes the G-code and starts the painting process."""
        g_code_commands = g_code.split('\n')
        for command in g_code_commands:
            self.robot_control.send_gcode(command)

    def pick_point(self):
        x, y = self.get_current_coordinates()
        self.corner_points.append((x, y))
        logging.info(f"Point picked at: {x}, {y}")
        if len(self.corner_points) == 2:
            self.g_code = self.map_manually_and_generate_gcode(self.corner_points)
        self.main_window.update_command_display()


