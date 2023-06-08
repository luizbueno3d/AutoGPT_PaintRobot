import torch
import os
from pathlib import Path
from utils import load_yaml, save_yaml
from detect import detect
from IPython.display import Image

def train_yolov5():
    # Set up the training environment
    os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    torch.backends.cudnn.benchmark = True

    # Load the YOLOv5 configuration file
    config_file = "yolov5_training/yolov5s.yaml"
    config = load_yaml(config_file)

    # Set the number of classes
    config['nc'] = 3  # Number of classes: wall, window, edge

    # Save the updated configuration file
    save_yaml(config_file, config)

    # Set the data configuration file
    data_config_file = "yolov5_training/data.yaml"

    # Train the YOLOv5 model
    !python yolov5/train.py --img 640 --batch 16 --epochs 100 --data {data_config_file} --cfg {config_file} --weights yolov5s.pt --nosave --cache

    # Detect objects in the validation dataset
    detect(weights="runs/train/exp/weights/best.pt", source="yolov5_training/dataset/val/images", output="yolov5_training/detection_results", conf_thres=0.25)

    # Display a sample detection result
    result_image = Path("yolov5_training/detection_results") / os.listdir("yolov5_training/detection_results")[0]
    return Image(filename=result_image, width=600)

if __name__ == "__main__":
    train_yolov5()