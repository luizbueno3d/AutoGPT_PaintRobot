#detection.py

import os
import cv2
import logging
import numpy as np
import json
from mmdet.apis import init_detector, inference_detector

# Define the maximum distance from the main wall to still be considered as wall
MAX_WALL_DISTANCE = 20  # in cm
PAINT_STRIPE_WIDTH = 12  # in cm

# Camera specifications
CAMERA_RESOLUTION = (1280, 800)
FIELD_OF_VIEW = 81

class ObstacleDetection:
    def __init__(self, config_file, checkpoint_file, device='cuda:0'):
        self.model = init_detector(config_file, checkpoint_file, device='cpu') #device=device, when was look 4 GPU
        self.obstacles = []
        self.wall_map = None

    def detect_obstacles(self, image_path):
        # Check if the image file exists
        if not os.path.exists(image_path):
            logging.error(f"Image file {image_path} does not exist.")
            return

        # Run inference on the image
        result = inference_detector(self.model, image_path)

        # Update the list of obstacles
        self.obstacles = result

    def map_area(self, corner_points):
        # Initialize wall map
        self.wall_map = np.ones((corner_points[1][1] - corner_points[0][1], corner_points[1][0] - corner_points[0][0]))

        # Mark obstacles in wall map
        for obstacle in self.obstacles:
            self.mark_obstacle(obstacle)

        # Save wall map as image and json file
        cv2.imwrite('wall_map.png', self.wall_map * 255)
        with open('wall_map.json', 'w') as f:
            json.dump(self.wall_map.tolist(), f)

    def mark_obstacle(self, obstacle):
        # Convert obstacle coordinates to indices in wall map
        # Mark the corresponding elements in wall map as 0
        self.wall_map[int(obstacle[1]):int(obstacle[3]), int(obstacle[0]):int(obstacle[2])] = 0

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Replace these with the path to your actual config file and checkpoint file
    config_file = 'path_to_your_config_file.py'
    checkpoint_file = 'path_to_your_checkpoint_file.pth'

    # Initialize the ObstacleDetection class
    obs_detect = ObstacleDetection(config_file, checkpoint_file)

    # Replace this with the path to your actual image
    image_path = 'path_to_your_image.jpg'

    # Detect obstacles
    obs_detect.detect_obstacles(image_path)

    # Map the area
    corner_points = [(0, 0), (100, 100)]  # replace this with your actual corner points
    obs_detect.map_area(corner_points)
