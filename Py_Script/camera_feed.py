import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap

class CameraFeed(QThread):

    obstacle_signal = pyqtSignal(list)

    frame_signal = pyqtSignal(QPixmap)

    def __init__(self):
        super().__init__()
        self.capture = cv2.VideoCapture(0)


    def run(self):
        while True:
            ret, frame = self.capture.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                self.frame_signal.emit(pixmap)
                
                # Detect obstacles in the current frame
                detected_obstacles = self.application.obstacle_detection.detect_obstacles(frame)

                # Emit the obstacle_signal with the detected obstacles
                self.obstacle_signal.emit(detected_obstacles)
                
            else:
                break   

            time.sleep(0.03)

    def stop(self):
        self.capture.release()
        self.quit()
        self.wait() 
