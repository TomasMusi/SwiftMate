# Imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,)
from PySide6.QtGui import QFont, QPixmap, QGuiApplication
from PySide6.QtCore import QThread
from PySide6.QtCore import Qt, QObject, Slot, QThread
import auth.login    # Importing the login module
from dotenv import load_dotenv
import os
import sys  # Importing sys for system-specific parameters and functions
import menu.menu as menu_module  # Importing the menu module (Using alias for clarity)
import menu.loading as loading_module  # Importing the loading module

load_dotenv()  # Load environment variables from .env file

# Global variables for preventing garbage collection
_login_thread = None
_login_worker = None
_result_handler = None

# Worker class for threading

""" 
Analogy for understanding Signal, Emit, Slot

Signal = your raised hand ✋
(You’re saying something happened)

emit() = the moment you shout the message
(You send the signal)

Slot = the teacher who hears you 👂
(And reacts by saying: “Great job!” or checking your homework)

"""

class LoginWorker(QObject): # QObject becomes QT compatible object, you can use signals and slots and move it to threads.

    finished = Signal(list, dict, object)  # Signal to indicate the worker has finished (This has no data, it just says: ,,im finished,,) [its]

    
    @Slot() # “Hey, the function below is a slot — it can be triggered by a signal or safely run in a thread.”
    def run(self): # defnies function run that will be executed in the background when the thread starts. 
        print("🧵 LoginWorker running in thread:", QThread.currentThread())
        print("LoginWorker started")
        
        try:
            emails, label_counts, service = auth.login.login_with_google()
        
        except Exception as e:
            print("Login failed:", e)
            emails, label_counts, service = [], {}, None
        print("✅ Emitting finished signal...")
        # What is emit? (Imagine you are in school and raise your hand and tell your teacher you are done, thats exactly what emit is for.)
        self.finished.emit(emails or [], label_counts or {}, service or {})  # emit done signal (always, success or fail) (Also we have to make sure that we handle the errors also, if the login fails send empty data.)

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

class ResultHandler(QObject):
    @Slot(list, dict, object)
    def on_finished(self, emails, label_counts, service):

                # Clean up the thread and worker 
                _login_thread.quit()  # Stop the thread Politely tells the thread: "Please stop running" 

                # These tell Qt to delete these objects later, when it's safe ( prevents memory leaks)
                _login_worker.deleteLater()  
                _login_thread.deleteLater() 

                # Close the loading screen
                loading_module.close_loading_screen()  # Close the loading dialog

                # Open menu window
                menu_module._gmail_service = service
                menu_module.create_main_window(emails=emails, label_counts=label_counts).show()

                # Clean up worker and thread after event loop completes
                _login_worker.deleteLater()
                _login_thread.quit()
                _login_thread.wait()  # this is now safe
                _login_thread.deleteLater()

                print("Login process completed.")

# Login Button action, when you click this happends.
def login_action(window):
    global _login_thread, _login_worker, _result_handler
    window.close()

    loading_module.show_loading_screen()  # Show loading screen (Runs in main thread)

    # Step 1: Create the worker and thread
    _login_worker = LoginWorker()  # Create an instance of the worker (holds the .run() method which runs the login process)
    _login_thread = QThread()  # Create a thread for the worker, (this thread is not running yet- it is just created)

    _login_worker.moveToThread(_login_thread)  # Move the worker to the thread (Super important step From now on, any slots (like .run()) on this worker will run inside that thread.) if we wouldnt do that, it would run inside of the main thread, which we dont want  to.

    # step 2: What happends when the login is finished
    _result_handler = ResultHandler()
    
    # Step 3: Connect signals
    _login_thread.started.connect(_login_worker.run)  # Connect the thread's started signal ( when the thread starts, it will call the worker's run() method)
    _login_worker.finished.connect(_result_handler.on_finished, Qt.QueuedConnection)  # Connect the worker's finished signal (This function runs in the main thread, so it’s safe to close windows and update GUI)

    # step 4: Start the thread
    _login_thread.start()  # Start the thread, this will call the run() method 


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