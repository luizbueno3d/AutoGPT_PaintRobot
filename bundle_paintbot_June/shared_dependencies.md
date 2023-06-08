Shared dependencies between paint.py and map.py:

1. Exported Variables:
   - corner_points: A list of tuples containing the coordinates of the corner points of the painting area.

2. Data Schemas:
   - None

3. DOM Element IDs:
   - point1_label: A label displaying the coordinates of the first corner point.
   - point2_label: A label displaying the coordinates of the second corner point.
   - spray_jet_width_input: An input field for the spray jet width.
   - spray_jet_overlap_input: An input field for the spray jet overlap.
   - gcode_display: A text display for the generated G-code.

4. Message Names:
   - mapping_ready_message: A message indicating that the painting area is ready.

5. Function Names:
   - find_serial_port: A function to find the serial port that the BTT SKR V1.3 board is connected to.
   - RobotControl: A class responsible for controlling the robot.
   - MainWindow: A class representing the main window of the application.
   - WallMapping: A class for mapping the wall and generating G-code for painting.
   - map_manually: A method to map the wall manually (without camera).
   - map_manually_and_generate_gcode: A method to generate G-code for manual mapping.
   - set_corner: A method to set the corner point based on the current position.
   - get_current_coordinates: A method to get the current coordinates of the robot.
   - start_painting_area: A method to start painting the mapped area.
   - confirm_mapping: A method to confirm the mapping process.
   - store_gcode: A method to store the generated G-code.
   - get_stored_gcode: A method to retrieve the stored G-code.
   - execute_gcode: A method to execute the G-code and start the painting process.
   - pick_point: A method to pick a point on the wall and update the corner points.