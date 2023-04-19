# Import necessary modules
import tkinter as tk
from PIL import ImageTk, Image


class GUI_Control:
    def __init__(self):
        # Create main window and size
        self.window = tk.Tk()
        self.window.title('Facade Painting Robot Controller')
        self.width, self.height = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.window.geometry(f'800x500+{int(self.width/3)}+0')

        # Create Heading Label
        self.heading_label = tk.Label(self.window, text="Facade Painting Robot Controller")
        self.heading_label.config(font=("Courier", 20))
        self.heading_label.grid(row=0, column=0, sticky='EW', pady=20, padx=10)

         # Create AI Feed Window
        self.camera_canvas = tk.Canvas(self.window, width=640, height=480)
        self.camera_canvas.grid(row=1, column=0, rowspan=3, sticky ='WENS', padx=10, pady=10)

        #Create Facademap Canvas
        self.facade_canvas = tk.Canvas(self.window, width=640, height=480)
        self.facade_canvas.grid(row=1, column=1, rowspan=3, sticky ='WENS', padx=10, pady=10)

        def start_painting(event):
            pass

        def reset_motion(event):
            pass

        def up_motion(event):
            pass

        def down_motion(event):
            pass

        def left_motion(event):
            pass

        def right_motion(event):
            pass

        def paint_done(event):
            pass

        # Respond to button events
        self.window.bind('<Control-s>', start_painting)
        self.window.bind('<Control-r>', reset_motion)
        self.window.bind('<Up>', up_motion)
        self.window.bind('<Down>', down_motion)
        self.window.bind('<Left>', left_motion)
        self.window.bind('<Right>', right_motion)
        self.window.bind('<Control-p>', paint_done)

if __name__ == "__main__":
    pass