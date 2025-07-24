# Imports
from curses import window
from PIL import Image, ImageTk
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                                 QHBoxLayout, QLineEdit, QFrame, QListWidget, QListWidgetItem)
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap, QGuiApplication
from PySide6.QtCore import Qt
import auth.login    # Importing the login module
from dotenv import load_dotenv
import os
import sys  # Importing sys for system-specific parameters and functions
import menu.menu  # Importing the menu module

load_dotenv()  # Load environment variables from .env file

# Function to get half the screen size
def get_half_screen_size():
    screen = QGuiApplication.primaryScreen().geometry()
    return screen.width() // 2, screen.height() // 2

# Function to center the window
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    window.geometry(f"{width}x{height}+{x}+{y}")


# Login Button action, when you click this happends.
def login_action(window):
    print("Login button clicked!")
    window.close()

    # Call the login function from auth.login module
    emails, primary_emails, social_emails, promotion_emails, label_counts, starred_emails = auth.login.login_with_google()
    
    # If login is successful, create the main window with emails and label counts
    if emails is not None:
        if emails is not None:
            menu.menu.create_main_window(
                emails=emails,
                label_counts=label_counts,
                primary_emails=primary_emails,
                social_emails=social_emails,
                promotion_emails=promotion_emails,
                starred_emails=starred_emails
            )
    else:
        print("Login failed.")
        # If login fails, you can handle it here (e.g., show an error message)

# Main window


def MainWindow():
    """Create the main window for the application."""
    # Initialize the main window
    app = QApplication(sys.argv)  # Create a QApplication instance

    window = QWidget()
    window.setWindowTitle("SwiftMate - Gmail Client")
    window.resize(*get_half_screen_size())

    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignCenter)

    #Logo

    logo_path = "imgs/logo.png"  # Path to the logo image
    if os.path.exists(logo_path):
        logo_label = QLabel()
        pixmap = QPixmap(logo_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
    else:
        logo_label = QLabel("Logo not found")
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

    # Title
    title_label = QLabel("SwiftMate")
    title_label.setFont(QFont("Helvetica", 20, QFont.Bold))
    title_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(title_label)

    # Subtitle
    subtitle_label = QLabel("Gmail Client")
    subtitle_label.setFont(QFont("Helvetica", 14))
    subtitle_label.setStyleSheet("color: #333;")  # Set color for subtitle
    subtitle_label.setAlignment(Qt.AlignCenter)
    layout.addWidget(subtitle_label)

    layout.addSpacing(20)  # Add some space before buttons

    # Login Button
    login_button = QPushButton("Login")
    login_button.setFont(QFont("Helvetica", 14))
    login_button.setStyleSheet("""
        QPushButton {
            background-color: #1a73e8;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }
        QPushButton:hover {
            background-color: #4285f4;
        }
        QPushButton:pressed {
            background-color: #1669c1;
        }
    """)
    login_button.clicked.connect(lambda: login_action(window))  # Connect the button to the login action

    layout.addWidget(login_button)

    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    MainWindow()  # Run the main window function
