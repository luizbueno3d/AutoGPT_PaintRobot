# YOLOv5 Training and Integration with Paint and Map Scripts

This readme will guide you through the process of training a YOLOv5 model to recognize windows, walls, and edges of a building for a painting machine. It will also explain how to integrate the trained model with the existing paint.py and map.py scripts.

## Directory Structure

Make sure you have the following directory structure:

```
yolov5_training/
    dataset/
        train/
            images/
            labels/
        val/
            images/
            labels/
    yolov5s.yaml
    data.yaml
    train.py
    detect.py
    utils.py
modified_map.py
modified_paint.py
```

## Training the YOLOv5 Model

1. Clone the YOLOv5 repository: `git clone https://github.com/ultralytics/yolov5.git`
2. Install the required dependencies: `pip install -r yolov5/requirements.txt`
3. Prepare your dataset by placing the images and corresponding label files in the `yolov5_training/dataset/train/images`, `yolov5_training/dataset/train/labels`, `yolov5_training/dataset/val/images`, and `yolov5_training/dataset/val/labels` directories.
4. Update the `yolov5_training/data.yaml` file with the correct number of classes and the paths to your train and validation datasets.
5. Train the model by running the following command:

```
python yolov5_training/train.py --img 640 --batch 16 --epochs 100 --data yolov5_training/data.yaml --cfg yolov5_training/yolov5s.yaml --weights yolov5s.pt --name my_model
```

This will train the model and save the best weights in the `yolov5_training/runs/train/my_model/weights/best.pt` file.

## Integrating the Trained Model with Paint and Map Scripts

1. Copy the `yolov5_training/detect.py` and `yolov5_training/utils.py` files into the same directory as the `modified_map.py` and `modified_paint.py` files.
2. In the `modified_map.py` file, import the necessary functions:

```python
from detect import detect
from utils import load_model, process_detections
```

3. Load the trained model in the `WallMapping` class:

```python
def __init__(self, robot_control, main_window):
    ...
    self.model = load_model('yolov5_training/runs/train/my_model/weights/best.pt')
```

4. Add a new method to the `WallMapping` class to map the wall using the camera:

```python
def map_with_camera(self):
    detections = detect(self.model, self.main_window.point1_label, self.main_window.point2_label)
    processed_detections = process_detections(detections)
    self.g_code = self.generate_gcode_from_detections(processed_detections)
    self.main_window.gcode_display.setText("\n".join(self.g_code))
```

5. Add a new button to the `MainWindow` class to map the wall using the camera:

```python
self.map_wall_camera_button = QtWidgets.QPushButton("Map Wall Camera", self)
self.map_wall_camera_button.clicked.connect(self.wall_mapping.map_with_camera)
```

6. Add the new button to the layout in the `MainWindow` class:

```python
layout.addWidget(self.map_wall_camera_button)
```

Now you can use the "Map Wall Camera" button to map the wall using the trained YOLOv5 model. The G-code will be generated based on the detected windows, walls, and edges, and the painting machine will paint only the walls while avoiding the windows.