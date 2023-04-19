import tkinter as tk

root = tk.Tk()
root.title('PaintRobot-AGPT03')
root.geometry('800x600')

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack(side='left', padx=10, pady=10)

label = tk.Label(root, text='Waiting for camera feed...')
label.pack(side='right', padx=10, pady=10)

root.mainloop()