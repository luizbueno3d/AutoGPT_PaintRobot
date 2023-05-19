#paint_app.py

import sys
import RPi.GPIO as GPIO
import threading
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QSlider, QLineEdit, QMessageBox, QSizePolicy, QComboBox
from PyQt6.QtCore import Qt
import serial.tools.list_ports
from map_wall import WallMapping

GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
PAINT_LEVEL_PIN = 21  # Change this to the GPIO pin number connected to your paint level sensor
GPIO.setup(PAINT_LEVEL_PIN, GPIO.IN)

def find_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]



class RobotControl:

    def __init__(self, baudrate=115200, port=None):
        if port is None:
            port = find_serial_port()
            if port is None:
                raise Exception("No suitable serial port found.")

            #error handling
            try:
                self.serial_connection = serial.Serial(port, baudrate)
        except Exception as e:
            raise Exception(f"Error establishing serial connection: {e}")


    def send_gcode(self, command):
        self.serial_connection.write(f"{command}\n".encode())
        response = self.serial_connection.readline().decode().strip()
        print(f"Sent: {command}, Received: {response}")
        return response

    def home_machine(self):
        self.send_gcode("G28")  # Home all axes

    def move_x_positive(self, distance):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 X{distance}")  # Move X+ by distance
        self.send_gcode(f"G90")  # Set back to absolute positioning

    def move_x_negative(self, distance):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 X{-distance}")  # Move X- by distance
        self.send_gcode(f"G90")  # Set back to absolute positioning

    def move_y_positive(self, distance):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 Y{distance}")  # Move Y+ by distance
        self.send_gcode(f"G90")  # Set back to absolute positioning

    def move_y_negative(self, distance):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 Y{-distance}")  # Move Y- by distance
        self.send_gcode(f"G90")  # Set back to absolute positioning

    def paint_vertical_line(self, length):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 Y{length}")  # Move Y+ by length
        self.send_gcode(f"G0 Y{-length}")  # Move Y- by length
        self.send_gcode(f"G90")  # Set back to absolute positioning

    def paint_horizontal_line(self, length):
        self.send_gcode(f"G91")  # Set to relative positioning
        self.send_gcode(f"G0 X{length}")  # Move X+ by length
        self.send_gcode(f"G0 X{-length}")  # Move X- by length
        self.send_gcode(f"G90")  # Set back to absolute positioning

        def read_paint_level(self):
            return GPIO.input(PAINT_LEVEL_PIN)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Polarbot Painter')
        self.resize(1000, 600)

        # Central Widget - This starts the GRID. Must come before these (self.xx, 0, 1)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)

        self.port_selector = QComboBox()
        self.update_port_list()
        grid_layout.addWidget(self.port_selector, 0, 1)  # Adjust the position as needed


        try:
            # Create instance of RobotControl class
            self.robot_control = RobotControl(port=self.port_selector.currentText(), baudrate=115200)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        #Level of paint Label
        self.paint_level_label = QLabel()
        grid_layout.addWidget(self.paint_level_label, 0, 2)  # Adjust the position as needed

        # Painting Area Selector
        self.paint_area = QPushButton('Select Painting Areas')
        self.paint_area.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.paint_area, 0, 0)
        # Painting Speed Slider
        self.speed_label = QLabel("Speed (%)", self)
        grid_layout.addWidget(self.speed_label, 1, 0)
        self.paint_speed = QSlider(Qt.Orientation.Horizontal)
        self.paint_speed.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.paint_speed.setMinimum(0)
        self.paint_speed.setMaximum(20)
        self.paint_speed.setValue(10)
        self.paint_speed.setTickInterval(1)
        self.paint_speed.setTickPosition(QSlider.TickPosition.TicksBelow)
        grid_layout.addWidget(self.paint_speed, 2, 0)
        # Feed rate input field
        self.feed_rate_input = QLineEdit()
        self.feed_rate_input.setPlaceholderText("Feed rate")
        grid_layout.addWidget(self.feed_rate_input, 3, 0)
        # Distance input field
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Distance (cm)")
        grid_layout.addWidget(self.distance_input, 4, 0)
        # Home Button
        self.home_button = QPushButton('Home Machine')
        self.home_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.home_button, 5, 0)
        self.home_button.clicked.connect(self.robot_control.home_machine)
        # X+ Button
        self.xp_button = QPushButton('Move X+')
        self.xp_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.xp_button, 6, 0)
        # Added: Connect X+ button to move_x_positive function
        self.xp_button.clicked.connect(lambda: self.robot_control.move_x_positive(self.get_valid_distance()))
        # X- Button
        self.xm_button = QPushButton('Move X-')
        self.xm_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.xm_button, 7, 0)
        # Added: Connect X- button to move_x_negative function
        self.xm_button.clicked.connect(lambda: self.robot_control.move_x_negative(self.get_valid_distance()))
        # Y+ Button
        self.yp_button = QPushButton('Move Y+')
        self.yp_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.yp_button, 8, 0)
        # Added: Connect Y+ button to move_y_positive function
        self.yp_button.clicked.connect(lambda: self.robot_control.move_y_positive(self.get_valid_distance()))
        # Y- Button
        self.ym_button = QPushButton('Move Y-')
        self.ym_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.ym_button, 9, 0)
        # Added: Connect Y- button to move_y_negative function
        self.ym_button.clicked.connect(lambda: self.robot_control.move_y_negative(self.get_valid_distance()))
        # Run Paint Line Button
        self.run_button = QPushButton('Run Paint Line')
        self.run_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.run_button, 10, 0)
        # Mapping wall sequence of Buttons:
        # Set Corner Button
        self.set_corner_button = QPushButton('Set Corner')
        self.set_corner_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.set_corner_button, 12, 0)
        # Map Wall Rectangle Button
        self.map_wall_rect_button = QPushButton('Map Wall Rectangle')
        self.map_wall_rect_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.map_wall_rect_button, 11, 0)
        # Start Painting Area Button
        self.start_paint_area_button = QPushButton('Start Painting Area')
        self.start_paint_area_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.start_paint_area_button, 13, 0)
        # Stop Painting Area Button
        self.stop_paint_area_button = QPushButton('Stop Painting Area')
        self.stop_paint_area_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.stop_paint_area_button, 14, 0)
        self.stop_paint_area_button.clicked.connect(self.stop_paint_area)

        # Paint Vertical Line Button
        self.paint_vertical_button = QPushButton('Paint Vertical Line')
        self.paint_vertical_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.paint_vertical_button, 15, 0)
        self.paint_vertical_button.clicked.connect(lambda: self.robot_control.paint_vertical_line(self.get_valid_distance()))

        # Paint Horizontal Line Button
        self.paint_horizontal_button = QPushButton('Paint Horizontal Line')
        self.paint_horizontal_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.paint_horizontal_button, 16, 0)
        self.paint_horizontal_button.clicked.connect(lambda: self.robot_control.paint_horizontal_line(self.get_valid_distance()))


        # Camera Feed
        self.camera_feed = QLabel()
        self.camera_feed.setFixedSize(320, 240)  # Set size of camera feed
        grid_layout.addWidget(self.camera_feed, 0, 2, 2, 1)

        # Start Button
        self.start_button = QPushButton('Start')
        self.start_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.start_button, 2, 2)

        # Stop Button
        self.stop_button = QPushButton('Stop')
        self.stop_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.stop_button, 3, 2)

        # Pause Button
        self.pause_button = QPushButton('Pause')
        self.pause_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.pause_button, 4, 2)

        # Restart Button
        self.restart_button = QPushButton('Restart')
        self.restart_button.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.restart_button, 5, 2)

        # Status Label
        self.status_label = QLabel('Status:')
        self.status_label.setStyleSheet("font-size: 20px;")
        grid_layout.addWidget(self.status_label, 6, 2)


        # Add empty QWidget with stretch factor to occupy remaining 70% width
        empty_widget = QWidget()
        empty_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        grid_layout.addWidget(empty_widget, 0, 3, 17, 1)  # Spanning 17 rows


        # Mapping wall sequence of Buttons:
        self.map_wall_rect_button.clicked.connect(self.map_wall_rectangle)
        self.set_corner_button.clicked.connect(self.set_corner)
        self.start_paint_area_button.clicked.connect(self.start_painting_area)
        
        # Create an instance of the WallMapping class
        self.wall_mapping = WallMapping(self.robot_control)

        threading.Thread(target=self.update_paint_level, daemon=True).start()

    def update_port_list(self):
        ports = serial.tools.list_ports.comports()
        self.port_selector.clear()
        for port in ports:
            self.port_selector.addItem(port.device)


    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    def update_camera_feed(self, frame):
        # Convert the frame to a QImage and set it as the pixmap for the camera_feed QLabel
        qimage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.camera_feed.setPixmap(pixmap)

    def map_wall_rectangle(self):
        self.wall_mapping.map_wall_rectangle()
        self.map_wall_rect_button.hide()  # Hide Map Wall Rectangle Button
        self.set_corner_button.show()  # Show Set Corner Button

    def set_corner(self):
        self.wall_mapping.set_corner()
        if len(self.wall_mapping.corner_points) == 2:
            confirmed = self.wall_mapping.confirm_mapping()
            if confirmed:
                self.wall_mapping.store_gcode(self.wall_mapping.get_stored_gcode())
                QMessageBox.information(self, "Info", self.wall_mapping.mapping_ready_message())
                self.start_paint_area_button.show()  # Show Start Painting Area Button

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
            # Add your code to stop the painting area and lose mapping here

    def update_paint_level(self):
        while True:
            paint_level = self.robot_control.read_paint_level()
            self.paint_level_label.setText(f"Paint Level: {paint_level}")
            time.sleep(1)  # Update every second


    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
