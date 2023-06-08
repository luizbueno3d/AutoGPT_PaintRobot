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



    def map_manually_and_generate_gcode(self):  
        # Extract the coordinates from the labels
        x1, y1 = [float(coord[1:]) for coord in self.main_window.point1_label.text().split(', ')]
        x2, y2 = [float(coord[1:]) for coord in self.main_window.point2_label.text().split(', ')]

        # Calculate the width and height of the painting area
        width = abs(x2 - x1)
        height = abs(y2 - y1)

        # Define the spray jet width and overlap
        spray_jet_width = float(self.main_window.spray_jet_width_input.text() or '200')  # in mm
        spray_jet_overlap = float(self.main_window.spray_jet_overlap_input.text() or '10')  # in mm


        # Calculate the number of lines and the distance between each line
        num_lines = int(height / (spray_jet_width - spray_jet_overlap))
        line_spacing = height / num_lines

        # Generate the G-code
        g_code = []
        for i in range(num_lines):
            # Calculate the y-coordinate for this line
            y = min(y1, y2) + i * line_spacing

            # Move to the start of the line and activate the spray
            g_code.append(f"G0 X{min(x1, x2)} Y{y}")
            g_code.append("E50.00")

            # Move along the line
            g_code.append(f"G1 X{max(x1, x2)} Y{y}")

            # Deactivate the spray
            g_code.append("E0.00")

        # Update the G-code display
        self.main_window.gcode_display.setText("\n".join(g_code))

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
            time.sleep(2)  # Add a delay of 2 second
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



    def start_painting_area(self):
        for command in self.g_code:
            self.robot_control.send_gcode(command)
        self.execute_gcode(self.g_code)
        self.main_window.update_command_display()

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
        logging.info(f"Point picked at: {x}, {y}")
        self.robot_control.command_history[-1] += f": X{x}, Y{y}"
        if not self.corner_points or (len(self.corner_points) == 2 and self.main_window.point1_label.text() != '' and self.main_window.point2_label.text() != ''):
            self.corner_points.append((x, y))
        elif self.main_window.point1_label.text() == '':
            self.corner_points[0] = (x, y)
            self.main_window.point1_label.setText(f"X{x}, Y{y}")
        elif self.main_window.point2_label.text() == '':
            if len(self.corner_points) == 1:
                self.corner_points.append((x, y))
            else:
                self.corner_points[1] = (x, y)
            self.main_window.point2_label.setText(f"X{x}, Y{y}")
        self.main_window.update_command_display()



