import numpy as np
import logging

class WallMapping:
    """Class for mapping the wall and generating G-code for painting."""
    def __init__(self, robot_control):
        self.corner_points = []
        self.g_code = ""
        self.robot_control = robot_control

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
        """Returns the current X and Y coordinates of the machine."""
        response = self.robot_control.send_gcode("M114")
        # Parse the response to extract the X and Y coordinates
        # This assumes the response is in the format: X:0.00 Y:0.00 Z:0.00 E:0.00 Count X:0 Y:0 Z:0
        coordinates = response.split(' ')[0:2]
        x = float(coordinates[0].split(':')[1])
        y = float(coordinates[1].split(':')[1])
        return x, y

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

