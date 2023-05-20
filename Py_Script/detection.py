#detection.py

import os
import cv2
import logging
import numpy as np
import json
from mmdet.apis import init_detector, inference_detector

# Define the maximum distance from the main wall to still be considered as wall
MAX_WALL_DISTANCE = 20  # in cm


class ObstacleDetection:
    def __init__(self, config_file, checkpoint_file, device='cuda:0'):
        self.model = init_detector(config_file, checkpoint_file, device=device)
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

    def map_area(self):
        # This method should implement the mapping functionality
        # For example, it might use the detected obstacles to divide the area into sections to be painted
        # This is a placeholder and needs to be implemented based on your specific requirements
        # For now, let's assume that the area is a 2D numpy array where 1 represents wall and 0 represents obstacle
        self.wall_map = np.ones((100, 100))  # replace this with your actual wall map
        for obstacle in self.obstacles:
            # Mark the obstacle area in the wall map
            # You'll need to convert the obstacle coordinates to indices in the wall map
            # This is a placeholder and needs to be replaced with your actual code
            self.wall_map[obstacle['bbox'][1]:obstacle['bbox'][3], obstacle['bbox'][0]:obstacle['bbox'][2]] = 0

        # Save the wall map as an image
        cv2.imwrite('wall_map.png', self.wall_map * 255)

        # Save the wall map as a json file
        with open('wall_map.json', 'w') as f:
            json.dump(self.wall_map.tolist(), f)

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
    obs_detect.map_area()
