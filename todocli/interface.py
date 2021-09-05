import tkinter as tk
import os

def get_value(event):
    global input_value, entry_box, window
    input_value = entry_box.get()
    window.destroy()

def center_window(width=300, height=200):
    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/4) - (height/2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y))

def run():
    global input_value, entry_box, window

    window = tk.Tk()
    window.title("Microsoft To Do: Quick Task")
    window.iconbitmap(f"{os.path.dirname(os.path.abspath(__file__))}\\Microsoft-To-Do.ico")
    window.attributes("-topmost", True)
    window.lift()

    input_value = None

    entry_box = tk.Entry(window, font = "SegoeUI 25", fg = "white", width = 50, borderwidth=5)
    entry_box.configure({"background": "#292929"})
    entry_box.pack()
    entry_box.focus()

    window.bind("<Return>", get_value)
    window.bind("<Escape>", lambda x: window.destroy())

    window.after(1000, entry_box.focus)
    center_window(600, 50)
    window.mainloop()
    return input_value

if __name__ == "__main__":
    print(run())