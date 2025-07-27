# loading.py

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer


_loading_dialog = None # Global variable to hold the loading dialog (if we didnt use global variable, python garbage collector might delete it)

def show_loading_screen():
    global _loading_dialog # Here we declare it again so we can modify it.

    # Preventing showing multiple loading dialogs
    if _loading_dialog:
        return  # already showing

    _loading_dialog = QDialog() # We are using QDialog for the loading screen (because it is used for temporary windows)
    _loading_dialog.setWindowTitle("Loading SwiftMate...") # Set the title of the loading dialog
    _loading_dialog.setModal(True)  # means you can’t interact with other windows until you close this one. It blocks user input.
    _loading_dialog.resize(500, 300) # Set the size of the loading dialog

    # Layout for the loading dialog
    layout = QVBoxLayout() #  Create a vertical layout for the loading dialog
    layout.setAlignment(Qt.AlignCenter) # Center the content in the dialog

    # Text label for loading message
    label = QLabel("🔄 Loading SwiftMate...\nPlease wait while we connect to Gmail.") # This shows the message, \n adds a break line.
    label.setStyleSheet("font-size: 20px; color: #1a73e8;") # Set the style of the label (font size and color)
    label.setAlignment(Qt.AlignCenter) # Center the label in the dialog

    # Add the label to the layout
    layout.addWidget(label)

    # Tells the dialog to use the layout we just created — otherwise nothing will appear
    _loading_dialog.setLayout(layout)

    # Show the loading dialog
    _loading_dialog.show()
    QApplication.processEvents()  # Ensure it paints immediately (it tells: "Hey, stop what you're doing and immediately draw the loading screen.")

def close_loading_screen():
    # Must write global otherwise it would think it is a local variable
    global _loading_dialog # Acces the global variable

    # Checks if the loading screen is currently showing (if loading_dialog is None, it means it is not showing or it was already closed)
    if _loading_dialog is not None:
        dialog = _loading_dialog  # Store the dialog in a local variable
        _loading_dialog = None  # Reset the global variable to None (so we can show it again later)
        QTimer.singleShot(0, dialog.accept)  # Tells QT to schedule a function to run after a delay ( Run it as soon as possible, “Please close the dialog, but do it safely in the main thread, at the next safe moment.”)
        

# Qt requires that all UI updates happen on the main thread !!!