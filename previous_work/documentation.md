# Documentation

This documentation explains how to execute the files and operate the machine to a 12 year old.

## Executing the Files

1. Clone the repository to your local machine using the command `clone_repository`.
2. Install the required libraries and modules using the commands `install_libraries` and `install_modules`.
3. Connect the Raspberry Pi 4 to the BIGTREETECH SKR V1.3 control board using the serial connection.
4. Run the GUI application using the command `paint_robot_gui.py`.

## Operating the Machine

1. Load the facade_painting_tasks.txt file into the GUI application.
2. Hang the robot on two 9mm static nylon cables hooked on encoded DC motor-controlled.
3. Turn on the OpenCV AI camera and position it to analyze paint coverage and map the facade.
4. Turn on the Paint Sprayer Wagner High Efficiency Airless Pro 250 M and position it to spray the paint on the facade.
5. Use the GUI application to control the robot and optimize the painting process to minimize paint consumption and maximize speed.
6. Use the collision switches and PID Servo Controller to ensure that the robot does not collide with the facade or other obstacles.

## Troubleshooting

If you encounter any issues while executing the files or operating the machine, refer to the file_logger.txt file for error messages and consult the OpenCV_integration_link.txt and opencv_links.txt files for OpenCV integration information.

