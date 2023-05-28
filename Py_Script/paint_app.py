#paint_app.py
import sys
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QSlider, QLineEdit, QMessageBox, QSizePolicy, QComboBox
from PyQt6.QtCore import Qt
import serial.tools.list_ports
#import RPi.GPIO as GPIO
from map_wall import WallMapping
from detection import ObstacleDetection
import serial

# This is only for the Mac. Remove for RPi.
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    class GPIO:
        BCM = IN = None

        @staticmethod
        def setmode(mode):
            pass

        @staticmethod
        def setup(channel, state):
            pass

GPIO.setmode(GPIO.BCM)
PAINT_LEVEL_PIN = 21
GPIO.setup(PAINT_LEVEL_PIN, GPIO.IN)

def find_serial_port():
    # VID and PID for BTT SKR V1.3 board
    VID_PID = [("1D50", "6029")]

    ports = serial.tools.list_ports.comports()
    for port in ports:
        for vid, pid in VID_PID:
            if vid in port.hwid and pid in port.hwid:
                return port.device
    return None


CONFIG_FILE = './yolov3_mobilenetv2_mstrain-416_300e_coco.py'
CHECKPOINT_FILE = './yolov3_mobilenetv2_mstrain-416_300e_coco_20210718_010823-f68a07b3.pth'



class RobotControl:
    def __init__(self, baudrate=115200, port=None):
        print("Creating RobotControl object...")
        self.serial_connection = None  # Initialize serial_connection as None
        if port is not None:
            try:
                self.serial_connection = serial.Serial()
                self.serial_connection.port = port
                self.serial_connection.baudrate = baudrate
                self.serial_connection.bytesize = serial.EIGHTBITS
                self.serial_connection.parity = serial.PARITY_NONE
                self.serial_connection.stopbits = serial.STOPBITS_ONE
                self.serial_connection.open()
                print(f"Successfully connected to port {port}")
            except Exception as e:
                raise Exception(f"Error establishing serial connection: {e}")

        try:
            print("Creating ObstacleDetection object...")
            self.obstacle_detection = ObstacleDetection(CONFIG_FILE, CHECKPOINT_FILE)
            print("Successfully created ObstacleDetection object.")
        except Exception as e:
            print(f"Error initializing obstacle detection: {e}")
            raise Exception(f"Error initializing obstacle detection: {e}")

        self.command_history = []



    def send_gcode(self, command):
        if self.serial_connection is not None and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                time.sleep(1)  # Wait for 1 second
                response = self.serial_connection.readline().decode().strip()
                print(f"Sent: {command}, Received: {response}")
            except Exception as e:
                print(f"An error occurred while sending G-code command: {e}")
                response = "Error"
        else:
            print("Serial connection is not open.")
            response = "Error"

        # Update the command history and the QLabel widget
        self.command_history.append(command)
        if len(self.command_history) > 6:
            self.command_history.pop(0)
        self.command_display.setText('\n'.join(self.command_history))

        return response



    def move_x_positive(self, distance):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 X{distance}")
        self.send_gcode(f"G90")

    def move_x_negative(self, distance):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 X{-distance}")
        self.send_gcode(f"G90")

    def move_y_positive(self, distance):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 Y{distance}")
        self.send_gcode(f"G90")

    def move_y_negative(self, distance):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 Y{-distance}")
        self.send_gcode(f"G90")

    def paint_vertical_line(self, length):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 Y{length}")
        self.send_gcode(f"G0 Y{-length}")
        self.send_gcode(f"G90")

    def paint_horizontal_line(self, length):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 X{length}")
        self.send_gcode(f"G0 X{-length}")
        self.send_gcode(f"G90")

    def read_paint_level(self):
        return GPIO.input(PAINT_LEVEL_PIN)

    def disconnect(self):
        if self.serial_connection.is_open:
            self.serial_connection.close()




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Polarbot Painter')
        self.resize(1000, 600)
        self.command_history = []
        self.command_display = QLabel()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)
        self.command_display = QLabel("Command history:")

        # Initialize the robot control object
        port = find_serial_port()
        if port is not None:
            self.robot_control = RobotControl(port=port)
        else:
            print("No suitable port found. Please connect the BTT SKR V1.3 board.")
            self.robot_control = None

        self.port_selector = QComboBox()
        self.update_port_list()
        # Connect the port selector's currentIndexChanged signal to the initialize_robot_control method
        self.port_selector.currentIndexChanged.connect(self.initialize_robot_control)
        self.grid_layout.addWidget(self.port_selector, 0, 1)

        self.paint_level_label = QLabel()
        self.grid_layout.addWidget(self.paint_level_label, 0, 2)

        self.paint_area = QPushButton('Select Painting Areas')
        self.paint_area.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.paint_area, 0, 0)

        self.speed_label = QLabel("Speed (%)", self)
        self.grid_layout.addWidget(self.speed_label, 1, 0)


        self.paint_speed = QSlider(Qt.Orientation.Horizontal)
        self.paint_speed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.paint_speed.setMinimum(0)
        self.paint_speed.setMaximum(20)
        self.paint_speed.setValue(10)
        self.paint_speed.setTickInterval(1)
        self.paint_speed.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.grid_layout.addWidget(self.paint_speed, 2, 0)

        self.feed_rate_input = QLineEdit()
        self.feed_rate_input.setPlaceholderText("Feed rate")
        self.grid_layout.addWidget(self.feed_rate_input, 3, 0)

        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Distance (cm)")
        self.grid_layout.addWidget(self.distance_input, 4, 0)

        #here was the Home Button, was the 5, 0 position. Now it is free.

        self.xp_button = QPushButton('Move X+')
        self.xp_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.xp_button, 6, 0)
        self.xp_button.clicked.connect(lambda: self.robot_control.move_x_positive(self.get_valid_distance()))

        self.xm_button = QPushButton('Move X-')
        self.xm_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.xm_button, 7, 0)
        self.xm_button.clicked.connect(lambda: self.robot_control.move_x_negative(self.get_valid_distance()))

        self.yp_button = QPushButton('Move Y+')
        self.yp_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.yp_button, 8, 0)
        self.yp_button.clicked.connect(lambda: self.robot_control.move_y_positive(self.get_valid_distance()))
        
        self.ym_button = QPushButton('Move Y-')
        self.ym_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.ym_button, 9, 0)
        self.ym_button.clicked.connect(lambda: self.robot_control.move_y_negative(self.get_valid_distance()))

        self.run_button = QPushButton('Run Paint Line')
        self.run_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.run_button, 10, 0)

        self.set_corner_button = QPushButton('Set Corner')
        self.set_corner_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.set_corner_button, 12, 0)

        self.map_wall_rect_button = QPushButton('Map Wall Rectangle')
        self.map_wall_rect_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.map_wall_rect_button, 11, 0)

        self.start_paint_area_button = QPushButton('Start Painting Area')
        self.start_paint_area_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.start_paint_area_button, 13, 0)

        self.stop_paint_area_button = QPushButton('Stop Painting Area')
        self.stop_paint_area_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.stop_paint_area_button, 14, 0)
        self.stop_paint_area_button.clicked.connect(self.stop_paint_area)

        self.paint_vertical_button = QPushButton('Paint Vertical Line')
        self.paint_vertical_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.paint_vertical_button, 15, 0)
        self.paint_vertical_button.clicked.connect(lambda: self.robot_control.paint_vertical_line(self.get_valid_distance()))

        self.paint_horizontal_button = QPushButton('Paint Horizontal Line')
        self.paint_horizontal_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.paint_horizontal_button, 16, 0)
        self.paint_horizontal_button.clicked.connect(lambda: self.robot_control.paint_horizontal_line(self.get_valid_distance()))

        self.detect_obstacles_button = QPushButton('Detect Obstacles')
        self.detect_obstacles_button.clicked.connect(self.robot_control.obstacle_detection.detect_obstacles)
        self.grid_layout.addWidget(self.detect_obstacles_button, 0, 3)

        self.optimize_paint_button = QPushButton('Optimize Paint')
        self.optimize_paint_button.clicked.connect(self.robot_control.obstacle_detection.map_area)
        self.grid_layout.addWidget(self.optimize_paint_button, 1, 3)

        self.camera_feed = QLabel()
        self.camera_feed.setFixedSize(320, 240)
        self.grid_layout.addWidget(self.camera_feed, 0, 2, 2, 1)

        self.start_button = QPushButton('Start')
        self.start_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.start_button, 2, 2)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.stop_button, 3, 2)

        self.pause_button = QPushButton('Pause')
        self.pause_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.pause_button, 4, 2)

        self.restart_button = QPushButton('Restart')
        self.restart_button.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.restart_button, 5, 2)

        self.status_label = QLabel('Status:')
        self.status_label.setStyleSheet("font-size: 20px;")
        self.grid_layout.addWidget(self.status_label, 6, 2)

        #Console display command history
        self.grid_layout.addWidget(self.command_display, 7, 2)  # Adjust the position as needed


        empty_widget = QWidget()
        empty_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_layout.addWidget(empty_widget, 0, 3, 17, 1)

        self.map_wall_rect_button.clicked.connect(self.map_wall_rectangle)
        self.set_corner_button.clicked.connect(self.set_corner)
        self.start_paint_area_button.clicked.connect(self.start_painting_area)

        self.wall_mapping = WallMapping(self.robot_control)

        self.corner_points = []

    def initialize_robot_control(self):
        try:
            self.robot_control.disconnect()
            self.robot_control = RobotControl(port=self.port_selector.currentText(), baudrate=115200)
            self.command_display.setText(f"Connected to port {self.port_selector.currentText()}")

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return


    def update_port_list(self):
        ports = serial.tools.list_ports.comports()
        self.port_selector.clear()
        for port in ports:
            self.port_selector.addItem(port.device)

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    def update_camera_feed(self, frame):
        qimage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.camera_feed.setPixmap(pixmap)

    def map_wall_rectangle(self):
        self.wall_mapping.map_wall_rectangle()
        self.map_wall_rect_button.hide()
        self.set_corner_button.show()

    # gets points for rectangle to create mapping strategy and points for bed size:
    def set_corner(self):
        corner_point = self.wall_mapping.set_corner()
        self.corner_points.append(corner_point) # Bed wall size -> Gcode
        if len(self.wall_mapping.corner_points) == 2:
            confirmed = self.wall_mapping.confirm_mapping()
            if confirmed:
                self.wall_mapping.store_gcode(self.wall_mapping.get_stored_gcode())
                QMessageBox.information(self, "Info", self.wall_mapping.mapping_ready_message())
                self.start_paint_area_button.show()
                # Update the bed size
                self.update_bed_size()   

            # Reset the corner points for the next mapping
            self.corner_points = []


    # gets points for bed size:
    def calculate_bed_size(self, corner_points):
        x_bed_size = abs(corner_points[1][0] - corner_points[0][0])
        y_bed_size = abs(corner_points[1][1] - corner_points[0][1])
        return x_bed_size, y_bed_size


    def start_painting_area(self):
        self.wall_mapping.start_painting_area()

    def get_valid_distance(self):
        try:
            distance = float(self.distance_input.text())
            if distance <= 0:
                raise ValueError
            return distance
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid distance (positive number).")
            return 0

    def stop_paint_area(self):
        msg = QMessageBox()
        msg.setWindowTitle("Warning")
        msg.setText("Are you sure you want to lose the mapping?")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            print("Stop painting area and lose mapping")

    def update_paint_level(self):
        while True:
            paint_level = self.robot_control.read_paint_level()
            self.paint_level_label.setText(f"Paint Level: {paint_level}")
            time.sleep(1)

        threading.Thread(target=self.update_paint_level, daemon=True).start()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
