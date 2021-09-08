import tkinter as tk
import os

def get_values(event):
    global window, title_value, title_entry, details_value, details_entry
    title_value = title_entry.get()
    details_value = details_entry.get()
    window.destroy()

def toggle_details(event):
    global window, title_entry, details_entry
    if details_entry.winfo_viewable():
        details_entry.grid_remove()
        title_entry.focus()

    else:
        details_entry.grid(row=1, sticky=tk.E+tk.W)
        details_entry.selection_range(0, tk.END)
        details_entry.focus()


def run():
    global title_value, details_value
    window.mainloop()
    return title_value, details_value

window = tk.Tk()
window.title("Microsoft To Do: Quick Task")
window.iconbitmap(f"{os.path.dirname(os.path.abspath(__file__))}\\Microsoft-To-Do.ico")
window.attributes("-topmost", True)
window.lift()

title_value = ""
details_value = ""

title_entry = tk.Entry(window, font = "SegoeUI 26",bg="#292929", fg = "white", width = 60, borderwidth=5)
title_entry.grid(row=0, sticky=tk.N+tk.S)
title_entry.focus()

details_entry = tk.Entry(window, font = "SegoeUI 16",bg="#292929", fg = "white", borderwidth=5)

window.after(100, window.focus_force)
window.after(200, title_entry.focus_force)

window.bind("<Return>", get_values)
window.bind("<Tab>", toggle_details)
window.bind("<Escape>", lambda x: window.destroy())

if __name__ == "__main__":
    print(run())