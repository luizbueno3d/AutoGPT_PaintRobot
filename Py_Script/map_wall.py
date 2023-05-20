#map_wall.py

import numpy as np
import logging
import depthai as dai
import tensorflow as tf
from time import sleep
# import other necessary libraries here

class WallMapping:
    """Class for mapping the wall and generating G-code for painting."""
    def __init__(self, robot_control):
        self.corner_points = []
        self.g_code = ""
        self.robot_control = robot_control
        # Add initialization for your hardware setup here

    def map_with_camera(self):
        """Starts the camera and performs mapping with it."""
        # Code to start the camera and perform mapping with it
        # Note that you'll need to replace this with actual commands for your hardware
        logging.info("Mapping with camera...")
        self.g_code = self.map_with_camera_and_generate_gcode(self.corner_points)
        
        # Initialize the OpenAI Oak-D Lite camera
        # Capture images from the camera while moving the machine between the two corner points
        # Process the images using OpenCV to detect wall, windows, and empty spaces
        # Generate a map of the wall based on the processed images
        # Call the map2gcode algorithm to convert the wall map into G-code

    def map_manually(self):
        """Maps manually (without camera)."""
        # Code to map manually (without camera)
        # Assuming that the entire rectangular area is a wall and generate G-code accordingly
        # Generate a map of the wall assuming the entire rectangular area is a wall
        # Call the map2gcode algorithm to convert the wall map into G-code
        logging.info("Mapping manually...")
        self.g_code = self.map_manually_and_generate_gcode(self.corner_points) #or (self.wall_map)


    def map2gcode(self, wall_map):
        # Initialize an empty G-code string
        g_code = ""

        # Create an instance of the PaintOptimization class
        paint_optimization = PaintOptimization()

        # Iterate through the wall_map
        for wall_area in wall_map:
            # Update the paint coverage
            paint_optimization.update_coverage(self.calculate_coverage(wall_area))

            # Optimize the painting speed
            speed = paint_optimization.optimize_speed()

            # Generate G-code commands to move the machine to the starting point of the wall area
            g_code += f"G0 X{wall_area.start_x} Y{wall_area.start_y}\n"

            # Generate G-code commands to set the painting speed
            g_code += f"G1 F{speed}\n"

            # Generate G-code commands to activate the paint sprayer
            g_code += "M106 S255\n"  # M106 S255 turns on the paint sprayer

            # Generate G-code commands to move the machine along the wall area while painting
            g_code += f"G1 X{wall_area.end_x} Y{wall_area.end_y}\n"

            # Generate G-code commands to deactivate the paint sprayer after painting the wall area
            g_code += "M107\n"  # M107 turns off the paint sprayer

        return g_code




    def set_corner(self):
        """Sets the corner point based on the current position."""
        # Code to set the corner point based on the current position
        x, y = self.get_current_coordinates()
        self.corner_points.append((x, y))
        logging.info(f"Corner point set at: {x}, {y}")

    def get_current_coordinates(self):
        """Returns the current coordinates of the machine."""
        # Replace this with the code to get the current coordinates of the machine
        # For now, we'll just return a placeholder value
        return np.random.randint(0, 100), np.random.randint(0, 100)

    def confirm_mapping(self):
        """Confirms mapping."""
        # Code to confirm mapping 
        # For now, we'll assume the user always confirms
        logging.info(f"Start mapping area from point {self.corner_points[0]} to point {self.corner_points[1]}?")
        return True

    def map_with_camera_and_generate_gcode(self, points):
        """Performs mapping with camera and generates G-code."""
        # Add your code to perform mapping with camera and generate G-code
        g_code = "G-code from camera"
        return g_code

    def map_manually_and_generate_gcode(self, points):
        """Generates G-code for the entire rectangular area."""
        # Add your code to generate G-code for the entire rectangular area
        g_code = "G-code from manual"
        return g_code

    def store_gcode(self, g_code):
        """Stores the generated G-code."""
        # Add your code to store the generated G-code
        self.g_code = g_code

    def mapping_ready_message(self):
        """Returns the message for when the painting area is ready."""
        # Add your code here
        return "Painting Area READY: Click Start Painting Area"

    def start_painting_area(self):
        """Starts the painting process."""
        # Add your code here
        self.execute_gcode(self.g_code)

    def get_stored_gcode(self):
        """Retrieves the stored G-code."""
        # Add your code to retrieve the stored G-code
        return self.g_code

    def execute_gcode(self, g_code):
        """Executes the G-code and starts the painting process."""
        # Add your code to execute the G-code and start the painting process
            # Split the G-code string into individual commands
        g_code_commands = g_code.split('\n')

        # Iterate through the G-code commands
        for command in g_code_commands:
            # Send the command to the BIGTREETECH SKR V1.3 board using the RobotControl class
            self.robot_control.send_gcode(command)

    def detect_obstacles(self):
        # Create pipeline
        pipeline = dai.Pipeline()

        # Define sources and outputs
        camRgb = pipeline.createColorCamera()
        spatialDetectionNetwork = pipeline.createMobileNetSpatialDetectionNetwork()
        xoutRgb = pipeline.createXLinkOut()

        xoutRgb.setStreamName("rgb")
        camRgb.preview.link(xoutRgb.input)

        # Properties
        camRgb.setPreviewSize(300, 300)
        camRgb.setInterleaved(False)
        camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        spatialDetectionNetwork.setBlobPath("mobilenet-ssd.blob.sh14cmx14NCE1")
        spatialDetectionNetwork.setConfidenceThreshold(0.5)
        spatialDetectionNetwork.input.setBlocking(False)

        # Linking
        camRgb.preview.link(spatialDetectionNetwork.input)

        # Connect to device and start pipeline
        with dai.Device(pipeline) as device:
            # Output queues will be used to get the rgb frames and nn data from the outputs defined above
            qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

            while True:
                inRgb = qRgb.get()  # Blocking call, will wait until a new data has arrived
                # Data is originally represented as a flat 1D array, it needs to be converted into HxWxC form
                frame = inRgb.getData().reshape((3, inRgb.getHeight(), inRgb.getWidth())).transpose(1, 2, 0).astype(np.uint8)
                frame = np.ascontiguousarray(frame)

                # Detect obstacles in the frame
                # Here you can use any object detection model trained with a machine learning library like TensorFlow or PyTorch
                # For now, we'll just use a placeholder function
                obstacles = self.detect_obstacles_in_frame(frame)

                # Update the wall map with the detected obstacles
                self.update_wall_map_with_obstacles(obstacles)

    def detect_obstacles_in_frame(self, frame):
        # Placeholder function for detecting obstacles in a frame
        # Replace this with your actual obstacle detection code
        return []

    def update_wall_map_with_obstacles(self, obstacles):
        # Placeholder function for updating the wall map with the detected obstacles
        # Replace this with your actual code for updating the wall map
        pass


class PaintOptimization:
    def __init__(self):
        self.current_coverage = 0  # Current paint coverage in percentage

    def update_coverage(self, coverage):
        """Updates the current paint coverage."""
        self.current_coverage = coverage

    def optimize_speed(self):
        """Optimizes the painting speed based on the current paint coverage."""
        if self.current_coverage < 50:
            # If the paint coverage is less than 50%, use a higher speed
            return 100  # Speed in percentage
        elif 50 <= self.current_coverage < 80:
            # If the paint coverage is between 50% and 80%, use a medium speed
            return 75  # Speed in percentage
        else:
            # If the paint coverage is greater than 80%, use a lower speed
            return 50  # Speed in percentage


class PaintOptimization:
    def __init__(self):
        self.current_coverage = 0  # Current paint coverage in percentage
        self.model = self.load_model()  # Load the trained model

    def load_model(self):
        """Loads the trained machine learning model."""
        # Replace 'model.h5' with the path to your trained model
        return tf.keras.models.load_model('model.h5')

    def update_coverage(self, coverage):
        """Updates the current paint coverage."""
        self.current_coverage = coverage

    def optimize_speed(self):
        """Optimizes the painting speed based on the current paint coverage."""
        # Use the model to predict the optimal painting speed
        speed = self.model.predict([[self.current_coverage]])
        return speed[0][0]  # Return the predicted speed



        logging.info("Executing G-code...")