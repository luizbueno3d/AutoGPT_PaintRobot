import numpy as np
import logging
import time
import cv2
from yolov5_training.detect import detect_walls_and_windows
from pathlib import Path

class WallMapping:
    def __init__(self, robot_control, main_window):
        self.corner_points = []
        self.g_code = ""
        self.robot_control = robot_control
        self.main_window = main_window
        self.yolov5_weights = "yolov5_training/best.pt"

    def map_with_camera(self):
        logging.info("Mapping with camera...")
        x1, y1 = [float(coord[1:]) for coord in self.main_window.point1_label.text().split(', ')]
        x2, y2 = [float(coord[1:]) for coord in self.main_window.point2_label.text().split(', ')]

        width = abs(x2 - x1)
        height = abs(y2 - y1)

        spray_jet_width = float(self.main_window.spray_jet_width_input.text() or '200')
        spray_jet_overlap = float(self.main_window.spray_jet_overlap_input.text() or '10')

        num_lines = int(height / (spray_jet_width - spray_jet_overlap))
        line_spacing = height / num_lines

        g_code = []
        wall_image = np.zeros((int(height), int(width)), dtype=np.uint8)

        for i in range(num_lines):
            y = min(y1, y2) + i * line_spacing

            g_code.append(f"G0 X{min(x1, x2)} Y{y}")

            img_path = self.capture_image()
            wall_mask, window_mask = detect_walls_and_windows(img_path, self.yolov5_weights)

            wall_image = cv2.bitwise_or(wall_image, wall_mask)

            for j in range(wall_mask.shape[1]):
                if wall_mask[0, j] == 255:
                    g_code.append("E50.00")
                else:
                    g_code.append("E0.00")

                g_code.append(f"G1 X{min(x1, x2) + j} Y{y}")

            g_code.append("E0.00")

        self.main_window.gcode_display.setText("\n".join(g_code))
        self.g_code = g_code
        cv2.imwrite("wall_image.png", wall_image)

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        img_path = Path("captured_image.jpg")
        cv2.imwrite(str(img_path), frame)
        cap.release()
        return img_path
