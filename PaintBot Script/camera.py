import cv2

class Camera:
    def __init__(self):
        self.cap = None

    def configure(self):
        self.cap = cv2.VideoCapture(0)
        return self.cap.isOpened()

    def capture_image(self):
        ret, frame = self.cap.read()
        return frame
