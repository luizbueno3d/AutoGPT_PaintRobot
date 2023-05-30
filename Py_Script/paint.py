import sys
import time
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QSlider, QLineEdit, QMessageBox, QSizePolicy, QComboBox
from PyQt6.QtCore import Qt

def find_serial_port():
    # VID and PID for BTT SKR V1.3 board
    VID_PID = [("1D50", "6029")]

    ports = serial.tools.list_ports.comports()
    for port in ports:
        for vid, pid in VID_PID:
            if vid in port.hwid and pid in port.hwid:
                return port.device
    return None

class RobotControl:
    def __init__(self, baudrate=115200, port=None):
        print("Creating RobotControl object...")
        self.serial_connection = None  # Initialize serial_connection as None
        if port is None:
            port = find_serial_port()
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
        else:
            print("No suitable port found. Please connect the BTT SKR V1.3 board.")
        self.command_history = []

    def send_gcode(self, command):
        if self.serial_connection is not None and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\n".encode())
                #time.sleep(1)  # Wait for 1 second
                response = self.serial_connection.readline().decode().strip()
                print(f"Sent: {command}, Received: {response}")
            except Exception as e:
                print(f"An error occurred while sending G-code command: {e}")
                response = "Error"
        else:
            print("Serial connection is not open.")
            response = "Error"
        self.command_history.append(command)
        return response

    def move_axis(self, axis, distance, feedrate):
        self.send_gcode(f"G91")
        self.send_gcode(f"G0 {axis}{distance} F{feedrate}")
        self.send_gcode(f"G90")

    def disconnect(self):
        if self.serial_connection.is_open:
            self.serial_connection.close()
            print("Serial connection closed.")

class MainWindow(QMainWindow):
    def __init__(self, robot_control):
        super().__init__()
        self.robot_control = robot_control
        self.setWindowTitle('Polarbot Painter')
        self.resize(1000, 600)
        self.command_display = QLabel()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)
        self.command_display = QLabel("Command history:")
        self.port_selector = QComboBox()
        self.update_port_list()
        self.port_selector.currentIndexChanged.connect(self.initialize_robot_control)
        self.grid_layout.addWidget(self.port_selector, 0, 0)
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.initialize_robot_control)
        self.grid_layout.addWidget(self.connect_button, 1, 0)
        self.disconnect_button = QPushButton('Disconnect')
        self.disconnect_button.clicked.connect(self.robot_control.disconnect)
        self.grid_layout.addWidget(self.disconnect_button, 2, 0)
        #distance in cm as Ghost text:
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText('Distance (in cm)')
        self.grid_layout.addWidget(self.distance_input, 3, 0)
        #feedrate in cm as Ghost text:
        self.feedrate_input = QLineEdit()
        self.feedrate_input.setPlaceholderText('Feedrate')
        self.grid_layout.addWidget(self.feedrate_input, 4, 0)

        self.xp_button = QPushButton('X+')
        self.xp_button.clicked.connect(lambda: self.move_axis('X', float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.xp_button, 5, 3)
        self.xm_button = QPushButton('X-')
        self.xm_button.clicked.connect(lambda: self.move_axis('X', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.xm_button, 5, 1)
        self.yp_button = QPushButton('Y+')
        self.yp_button.clicked.connect(lambda: self.move_axis('Y', float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.yp_button, 4, 2)
        self.ym_button = QPushButton('Y-')
        self.ym_button.clicked.connect(lambda: self.move_axis('Y', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.ym_button, 6, 2)
        self.zp_button = QPushButton('Z+')
        self.zp_button.clicked.connect(lambda: self.move_axis('Z', float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.zp_button, 1, 3)
        self.zm_button = QPushButton('Z-')
        self.zm_button.clicked.connect(lambda: self.move_axis('Z', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.zm_button, 2, 3)
        self.command_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.grid_layout.addWidget(self.command_display, 7, 0, 1, 3)

    def move_axis(self, axis, distance, feedrate):
        try:
            self.robot_control.move_axis(axis, float(distance), float(feedrate))
            self.update_command_display()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def initialize_robot_control(self):
        try:
            self.robot_control.disconnect()
            self.robot_control = RobotControl(port=self.port_selector.currentText(), baudrate=115200)
            self.update_command_display()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_command_display(self):
        self.command_display.setText("\n".join(self.robot_control.command_history))

    def update_port_list(self):
        self.port_selector.clear()
        self.port_selector.addItems([port.device for port in serial.tools.list_ports.comports()])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    robot_control = RobotControl()
    main_window = MainWindow(robot_control)
    main_window.show()
    sys.exit(app.exec())