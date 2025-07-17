# Imports
import tkinter as tk
from PIL import Image, ImageTk
def open_menu():
    menu_root = tk.Tk()
    menu_root.title("SwiftMate - Authentication Menu")
    menu_root.geometry("600x400")
    menu_root.configure(bg="white")

    label = tk.Label(menu_root, text="Welcome to SwiftMate Authentication Menu!", font=("Arial", 18), bg="white")
    label.pack(pady=50)

    menu_root.mainloop()
