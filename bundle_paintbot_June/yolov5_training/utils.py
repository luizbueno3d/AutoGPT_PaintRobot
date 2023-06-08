import cv2
import numpy as np
from pathlib import Path
from typing import Tuple

def load_yolov5_model(weights_path: str, device: str = "cpu"):
    from yolov5.models.experimental import attempt_load

    model = attempt_load(weights_path, map_location=device)
    return model

def preprocess_image(image: np.ndarray, img_size: Tuple[int, int] = (640, 640)):
    from yolov5.utils.datasets import letterbox

    img = letterbox(image, img_size, stride=32)[0]
    img = img[:, :, ::-1].transpose(2, 0, 1)
    img = np.ascontiguousarray(img)
    img = img / 255.0
    return img

def detect_objects(model, image: np.ndarray, conf_thres: float = 0.25, iou_thres: float = 0.45):
    from yolov5.utils.general import non_max_suppression

    img = preprocess_image(image)
    img = np.expand_dims(img, axis=0)
    pred = model(img)[0]
    pred = non_max_suppression(pred, conf_thres, iou_thres, agnostic=True)
    return pred

def draw_detections(image: np.ndarray, detections, names):
    from yolov5.utils.plots import plot_one_box

    for det in detections:
        if det is not None and len(det):
            for *xyxy, conf, cls in det:
                label = f"{names[int(cls)]} {conf:.2f}"
                plot_one_box(xyxy, image, label=label, color=(0, 255, 0), line_thickness=2)
    return image

def save_detections_to_png(image: np.ndarray, output_path: str):
    cv2.imwrite(output_path, image)

def get_wall_mask(image: np.ndarray, detections, img_size: Tuple[int, int] = (640, 640)):
    wall_mask = np.zeros(img_size, dtype=np.uint8)
    for det in detections:
        if det is not None and len(det):
            for *xyxy, conf, cls in det:
                if cls == 0:  # Wall class
                    x1, y1, x2, y2 = map(int, xyxy)
                    wall_mask[y1:y2, x1:x2] = 255
    return wall_mask

def save_wall_mask_to_png(wall_mask: np.ndarray, output_path: str):
    cv2.imwrite(output_path, wall_mask)