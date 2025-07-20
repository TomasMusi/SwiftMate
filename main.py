# Imports
import tkinter as tk
from PIL import Image, ImageTk
import auth.login    # Importing the login module
from dotenv import load_dotenv
import menu.menu  # Importing the menu module

load_dotenv()  # Load environment variables from .env file

# Function to get half the screen size
def get_half_screen_size(window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    return int(screen_width / 2), int(screen_height / 2)

# Function to center the window
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")

# Main window
root = tk.Tk()
root.title("SwiftMate - Gmail Client")

# Window size and centering it
window_width, window_height = get_half_screen_size(root)
center_window(root, window_width, window_height)

root.configure(bg="white")

# Load and place logo
logo_path = "imgs/logo.png"  
try:
    img = Image.open(logo_path)
    img = img.resize((100, 100))  # Sizing of the image.
    logo = ImageTk.PhotoImage(img)
    logo_label = tk.Label(root, image=logo, bg="white")
    logo_label.image = logo  # Keep a reference to avoid garbage collection
    logo_label.pack(pady=(40, 10))
except Exception as e:
    print(f"Error loading logo: {e}")
    logo_label = tk.Label(root, text="Logo not found", bg="white", fg="red")
    logo_label.pack(pady=(40, 10))

# App Title
title_label = tk.Label(root, text="SwiftMate", font=("Helvetica", 20, "bold"), bg="white", fg="#333")
title_label.pack()

# Subtitle
subtitle_label = tk.Label(root, text="Gmail Client", font=("Helvetica", 14), bg="white", fg="#666")
subtitle_label.pack(pady=(0, 40))

# Login Button action, when you click this happends.
def login_action():
    print("Login button clicked!")
    root.destroy()  # Close the main window
    auth.login.login_with_google()  # Call the open_menu function from the login module

def testing_button_action():
    print("Testing button clicked!")
    root.destroy()  # Close the main window
    menu.menu.create_main_window()  # Call the open_menu function from the menu module


# Login Button
login_button = tk.Button(
    root,
    text="Login",
    font=("Helvetica", 14),
    bg="#2a5dab",
    fg="white",
    activebackground="#31a1d4",
    padx=20,
    pady=10,
    command=login_action,
)
login_button.pack()

# Testing Button
testing_button = tk.Button(
    root,
    text="Testing",
    font=("Helvetica", 14),
    bg="#2a5dab",
    fg="white",
    activebackground="#31a1d4",
    padx=20,
    pady=10,
    command=testing_button_action,
)
testing_button.pack()

# Start GUI
root.mainloop()
