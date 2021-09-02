import tkinter as tk
import os

def get_value(event):
    global input_value, entry_box, root
    input_value = entry_box.get()
    root.destroy()

def center_window(width=300, height=200):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/4) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def run():
    global input_value, entry_box, root

    root = tk.Tk()
    root.title("Microsoft To Do: Quick Task")
    root.iconbitmap(f"{os.path.dirname(os.path.abspath(__file__))}\\Microsoft-To-Do.ico")
    root.focus_force()

    input_value = None

    entry_box = tk.Entry(root, font = "SegoeUI 25", fg = "white", width = 50, borderwidth=5)
    entry_box.configure({"background": "#292929"})
    entry_box.pack()
    entry_box.focus()

    root.bind("<Return>", get_value)
    root.bind("<Escape>", lambda x: root.destroy())

    center_window(600, 50)
    root.mainloop()
    return input_value

if __name__ == "__main__":
    print(run())