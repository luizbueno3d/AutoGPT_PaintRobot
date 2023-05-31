import sys
import time
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QSlider, QLineEdit, QMessageBox, QSizePolicy, QComboBox
from PyQt6.QtCore import Qt
from map import WallMapping


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
        self.wall_mapping = WallMapping(self.robot_control, self)

        self.setWindowTitle('Polarbot Painter')
        self.resize(1000, 600)
        self.command_display = QLabel()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.grid_layout = QGridLayout(central_widget)

        # Create the command display, scroll area, and widget
        self.command_display = QLabel("Command history:")
        self.command_scroll_area = QScrollArea()
        self.command_widget = QWidget()
        self.port_selector = QComboBox()

        # Set the widget for the scroll area and create a layout for the widget
        self.command_scroll_area.setWidget(self.command_widget)
        self.command_scroll_area.setWidgetResizable(True)  # Make the widget resizable
        self.command_layout = QVBoxLayout(self.command_widget)
        self.command_layout.addWidget(self.command_display)

        self.update_port_list()
        #self.update_port_list.setFixedWidth(300)
        self.port_selector.currentIndexChanged.connect(self.initialize_robot_control)
        self.grid_layout.addWidget(self.port_selector, 0, 0)

        self.connected_port_label = QLabel() #Label that shows which port is connected.
        self.connected_port_label.setFixedWidth(300)
        self.grid_layout.addWidget(self.connected_port_label, 0, 3)

        self.connect_button = QPushButton('Connect') # Connect button
        self.connect_button.setFixedWidth(160)
        self.connect_button.clicked.connect(self.initialize_robot_control)
        self.grid_layout.addWidget(self.connect_button, 0, 1)

        self.disconnect_button = QPushButton('Disconnect') # Disconnect button
        self.disconnect_button.setFixedWidth(160)
        self.disconnect_button.clicked.connect(self.disconnect)
        self.grid_layout.addWidget(self.disconnect_button, 0, 2)

        self.distance_input = QLineEdit() # Input distance field
        self.distance_input.setFixedWidth(160)
        self.distance_input.setPlaceholderText('Distance (in cm)') #distance in cm as Ghost text:
        self.grid_layout.addWidget(self.distance_input, 3, 0)

        self.feedrate_input = QLineEdit() #feedrate in cm as Ghost text:
        self.feedrate_input.setFixedWidth(160)
        self.feedrate_input.setPlaceholderText('Feedrate')
        self.grid_layout.addWidget(self.feedrate_input, 4, 0)

        self.xp_button = QPushButton('X+')
        self.xp_button.setFixedWidth(50)
        #self.xp_button.clicked.connect(lambda: self.move_axis('X', float(self.distance_input.text()), self.feedrate_input.text()))
        self.xp_button.clicked.connect(lambda: self.move_axis('X', self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.xp_button, 5, 3)

        self.xm_button = QPushButton('X-')
        self.xm_button.setFixedWidth(50)
        #self.xm_button.clicked.connect(lambda: self.move_axis('X', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.xm_button.clicked.connect(lambda: self.move_axis('X', '-' + self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.xm_button, 5, 1)

        self.yp_button = QPushButton('Y+')
        self.yp_button.setFixedWidth(50)
        #self.yp_button.clicked.connect(lambda: self.move_axis('Y', float(self.distance_input.text()), self.feedrate_input.text()))
        self.yp_button.clicked.connect(lambda: self.move_axis('Y', self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.yp_button, 4, 2)

        self.ym_button = QPushButton('Y-')
        self.ym_button.setFixedWidth(50)
        #self.ym_button.clicked.connect(lambda: self.move_axis('Y', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.ym_button.clicked.connect(lambda: self.move_axis('Y', '-' + self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.ym_button, 6, 2)

        self.zp_button = QPushButton('Z+')
        self.zp_button.setFixedWidth(50)
        #self.zp_button.clicked.connect(lambda: self.move_axis('Z', float(self.distance_input.text()), self.feedrate_input.text()))
        self.zp_button.clicked.connect(lambda: self.move_axis('Z', self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.zp_button, 1, 3)

        self.zm_button = QPushButton('Z-')
        self.zm_button.setFixedWidth(50)
        #self.zm_button.clicked.connect(lambda: self.move_axis('Z', -float(self.distance_input.text()), self.feedrate_input.text()))
        self.zm_button.clicked.connect(lambda: self.move_axis('Z', '-' + self.distance_input.text(), self.feedrate_input.text()))
        self.grid_layout.addWidget(self.zm_button, 2, 3)

        # Set a fixed height for the scroll area
        self.command_scroll_area.setFixedHeight(200)
        self.grid_layout.addWidget(self.command_scroll_area, 7, 0, 1, 3)

        self.pick_point_button = QPushButton('Pick Point')
        self.pick_point_button.clicked.connect(self.wall_mapping.pick_point)
        self.grid_layout.addWidget(self.pick_point_button, 8, 0)

        self.gcode_input = QLineEdit()
        self.grid_layout.addWidget(self.gcode_input, 8, 3)

        self.send_gcode_button = QPushButton('Send G-code')
        self.send_gcode_button.setFixedWidth(100)
        self.send_gcode_button.clicked.connect(self.send_gcode)
        self.grid_layout.addWidget(self.send_gcode_button, 8, 6)


        self.start_painting_button = QPushButton('Start Painting')
        self.start_painting_button.clicked.connect(self.wall_mapping.start_painting_area)
        self.grid_layout.addWidget(self.start_painting_button, 9, 0)


    def send_gcode(self):
        gcode = self.gcode_input.text()
        self.robot_control.send_gcode(gcode)
        self.update_command_display()

    def disconnect(self):
        self.robot_control.disconnect()
        self.connected_port_label.setText("Disconnected")

    def move_axis(self, axis, distance, feedrate):
        if not distance or not feedrate:
            QMessageBox.critical(self, "Error", "Please enter both distance and feedrate.")
            return
        try:
            self.robot_control.move_axis(axis, float(distance), float(feedrate))
            self.update_command_display()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def initialize_robot_control(self):
        try:
            self.robot_control.disconnect()
            self.robot_control = RobotControl(port=self.port_selector.currentText(), baudrate=115200)
            self.connected_port_label.setText(f"Connected to: {self.port_selector.currentText()}")
            self.update_command_display()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_command_display(self):
        self.command_display.setText("\n".join(self.robot_control.command_history))
        self.command_scroll_area.verticalScrollBar().setValue(self.command_scroll_area.verticalScrollBar().maximum())


    def update_port_list(self):
        self.port_selector.clear()
        self.port_selector.addItems([port.device for port in serial.tools.list_ports.comports()])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    robot_control = RobotControl()
    main_window = MainWindow(robot_control)
    main_window.show()
    sys.exit(app.exec())