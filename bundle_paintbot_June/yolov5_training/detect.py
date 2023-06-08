import cv2
import torch
from pathlib import Path
from utils import load_model, process_image, draw_boxes

def detect_objects(image_path, model, device):
    img = cv2.imread(image_path)
    img_processed, img_meta = process_image(img)
    img_processed = img_processed.to(device)

    with torch.no_grad():
        pred = model(img_processed)[0]

    pred = pred[pred[:, 4] > 0.5]
    boxes = pred[:, :4].cpu().numpy()
    boxes = boxes * img_meta["scale_factor"]
    boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, img_meta["original_width"])
    boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, img_meta["original_height"])

    return boxes

def main(image_path, model_path, output_path):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(model_path, device)

    boxes = detect_objects(image_path, model, device)
    img = cv2.imread(image_path)
    img_with_boxes = draw_boxes(img, boxes)

    cv2.imwrite(output_path, img_with_boxes)

if __name__ == "__main__":
    image_path = "yolov5_training/dataset/val/images/sample.jpg"
    model_path = "yolov5_training/best.pt"
    output_path = "yolov5_training/detection_results/sample_result.png"

    main(image_path, model_path, output_path)