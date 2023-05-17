import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils

class AICamera:
    def __init__(self, model_path):
        self.model_path = model_path
        self.category_index = label_map_util.create_category_index_from_labelmap('path/to/labelmap.pbtxt', use_display_name=True)
        self.load_model()

    def load_model(self):
        self.model = tf.saved_model.load(self.model_path)

    def detect_objects(self, frame):
        input_tensor = tf.convert_to_tensor(np.expand_dims(frame, 0), dtype=tf.float32)
        detections = self.model(input_tensor)

        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections

        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        label_id_offset = 1
        image_np_with_detections = frame.copy()

        viz_utils.visualize_boxes_and_labels_on_image_array(
            image_np_with_detections,
            detections['detection_boxes'],
            detections['detection_classes'] + label_id_offset,
            detections['detection_scores'],
            self.category_index,
            use_normalized_coordinates=True,
            max_boxes_to_draw=200,
            min_score_thresh=.30,
            agnostic_mode=False)

        detected_obstacles = self.extract_bounding_boxes(detections)
        return detected_obstacles

    def extract_bounding_boxes(self, detections):
        boxes = detections['detection_boxes']
        scores = detections['detection_scores']
        classes = detections['detection_classes']
        height, width, _ = frame.shape

        detected_obstacles = []

        for i in range(len(scores)):
            if scores[i] > 0.3:  # You can change the threshold value
                box = boxes[i]
                ymin, xmin, ymax, xmax = box
                x, y, w, h = int(xmin * width), int(ymin * height), int((xmax - xmin) * width), int((ymax - ymin) * height)
                detected_obstacles.append((x, y, w, h))

        return detected_obstacles
