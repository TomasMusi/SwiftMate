from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                                 QHBoxLayout, QLineEdit, QFrame, QListWidget, QListWidgetItem)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt
import sys

def create_main_window():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("SwiftMate - Gmail Clone")
    window.resize(1200, 700)

    # Fonts
    FONT = QFont("Helvetica", 12)
    BOLD = QFont("Helvetica", 12, QFont.Bold)
    SMALL = QFont("Helvetica", 10)

    # --- Sidebar ---
    sidebar_layout = QVBoxLayout()
    sidebar_widget = QWidget()
    sidebar_widget.setStyleSheet("background-color: #f6f9ff")
    sidebar_widget.setFixedWidth(260)

    gmail_logo = QLabel("\U0001F4E7 Gmail")
    gmail_logo.setFont(QFont("Helvetica", 16, QFont.Bold))
    sidebar_layout.addWidget(gmail_logo)

    compose_btn = QPushButton("\u270D\ufe0f Compose")
    compose_btn.setFont(BOLD)
    compose_btn.setStyleSheet("background-color: #bae6fd; padding: 10px; border-radius: 10px;")
    sidebar_layout.addWidget(compose_btn)

    folder_items = [
        ("\U0001F4E5", "Inbox", "4,256"),
        ("\u2B50", "Starred", ""),
        ("\U0001F552", "Snoozed", ""),
        ("\U0001F4E4", "Sent", ""),
        ("\u270F", "Draft", "42"),
        ("\u25BE", "More", "")
    ]

    for icon, name, count in folder_items:
        label = QLabel(f"{icon} {name} {f'({count})' if count else ''}")
        label.setFont(FONT)
        sidebar_layout.addWidget(label)

    sidebar_layout.addSpacing(20)
    label_header = QLabel("Labels")
    label_header.setFont(BOLD)
    sidebar_layout.addWidget(label_header)
    sidebar_layout.addWidget(QLabel("\U0001F3F7️ Important"))
    sidebar_layout.addWidget(QLabel("➕ Add Label"))

    sidebar_widget.setLayout(sidebar_layout)

    # --- Main Area ---
    main_layout = QVBoxLayout()
    main_layout.setSpacing(0)

    # Search bar
    search_box = QWidget()
    search_box.setStyleSheet("background-color: #e5f1ff; border-radius: 16px; padding: 0px;")
    search_box.setFixedHeight(32)  # <-- This controls the *visible height*
    search_box.setFixedWidth(int(window.width() * 0.5)) # <-- This controls the *visible width* 70%

    search_icon = QLabel("🔍")
    search_icon.setStyleSheet("padding: 2px; font-size: 15px; color: #5f6368;")

    search_input = QLineEdit()
    search_input.setPlaceholderText("Search mail")
    search_input.setStyleSheet("background-color: transparent; border: none; font-size: 15px;")

    search_row = QHBoxLayout()
    search_row.setContentsMargins(4, 0, 4, 0)  # Optional: reduce layout spacing
    search_row.setSpacing(4)

    search_row.addWidget(search_icon)
    search_row.addWidget(search_input, 1)

    search_box.setLayout(search_row)
    main_layout.addWidget(search_box)

    # Tabs section
    tabs = QHBoxLayout()
    def create_tab(name, icon, active=False, badge_text=None, badge_color="#1a73e8"):
        # Create a tab with an icon, name, and optional badge
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)   # Remove margin
        tab_layout.setSpacing(0)  

        # Create the row with icon and name
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(8, 2, 8, 2)   # Small padding
        row_layout.setSpacing(4)        
        
        label = QLabel(f"{icon} {name}")
        label.setFont(BOLD if active else FONT)
        label.setStyleSheet("color: #1a73e8;" if active else "color: #202124;")
        row_layout.addWidget(label)

        # if statement to show which tab is active 
        if active:
            label.setStyleSheet("color: #1a73e8;")
        row_layout.addWidget(label)

        # if badge_text is provided, create a badge 
        if badge_text:
            badge = QLabel(badge_text)
            badge.setFont(SMALL)
            badge.setStyleSheet(f"background-color: #1a73e8; color: white; border-radius: 8px; padding: 1px 6px;")
            row_layout.addWidget(badge)

        # Center the row layout
        row_layout.setAlignment(Qt.AlignCenter)
        tab_layout.addLayout(row_layout)

        # If the tab is active, add an underline
        if active:
            underline = QFrame()
            underline.setFrameShape(QFrame.HLine)
            underline.setStyleSheet("background-color: #1a73e8; height: 2px")
            underline.setFixedHeight(2)
            tab_layout.addWidget(underline)

        # Add the tab layout to the main tabs layout
        tab_widget = QWidget()
        tab_widget.setLayout(tab_layout)
        tabs.addWidget(tab_widget)
        tabs.setSpacing(0)  # No spacing between tabs

    create_tab("Primary", "\U0001F4C2", active=True)
    create_tab("Promotions", "\U0001F4DC", badge_text="5 new")
    create_tab("Social", "\U0001F465", badge_text="3 new")
    tabs_container = QWidget()
    tabs_container.setLayout(tabs)
    tabs_container.setFixedHeight(40) # <-- Height of the tabs (Primary, Promotions, Social)
    main_layout.addWidget(tabs_container)

    # Emails List
    emails = [
        ("PW Skills", "Join Our Live Class on JavaScript Fundamentals📊", "07:00"),
        ("Cuvette", "Job Guarantee course Program", "05:12"),
        ("Geeks", "This Is Exactly What You're Looking For!", "03:31"),
        ("LinkedIn", "See Monindra's and other people's connections", "5 Nov")
    ]

    for sender, subject, time in emails:
        row = QHBoxLayout()
        row.setContentsMargins(8, 4, 8, 4)
        row.setSpacing(0)


        # Checkbox and star placeholder (can add icons later)
        checkbox = QLabel("☐")  # Or use a QCheckBox
        checkbox.setFixedWidth(20)
        star = QLabel("☆")
        star.setFixedWidth(20)
        row.addWidget(checkbox)
        row.addWidget(star)

        # Sender
        sender_label = QLabel(sender)
        sender_label.setFont(BOLD)
        sender_label.setFixedWidth(120)
        row.addWidget(sender_label)

        # Subject + preview text
        subject_label = QLabel(subject + " - Lorem ipsum dolor sit amet, consectetur adipiscing...")
        subject_label.setFont(FONT)
        subject_label.setStyleSheet("color: #202124")
        row.addWidget(subject_label, 1)

        # Time
        time_label = QLabel(time)
        time_label.setFont(SMALL)
        time_label.setStyleSheet("color: gray")
        time_label.setFixedWidth(60)
        row.addWidget(time_label)

        row_widget = QWidget()
        row_widget.setLayout(row)
        row_widget.setFixedHeight(30)
        row_widget.setStyleSheet("""
    QWidget {
        margin: 0px;
        padding: 0px;
    }
    QWidget:hover {
        background-color: #f5f5f5;
    }
""")
        
        main_layout.addWidget(row_widget)

    # --- Combine Sidebar and Main Area ---
    container = QHBoxLayout()
    container.addWidget(sidebar_widget)

    main_area_widget = QWidget()
    main_area_widget.setLayout(main_layout)
    container.addWidget(main_area_widget)

    window.setLayout(container)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    create_main_window()
