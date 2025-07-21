from unicodedata import name
from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
                                 QHBoxLayout, QLineEdit, QFrame, QListWidget, QListWidgetItem)
from PySide6.QtGui import QFont, QColor, QPalette
from PySide6.QtCore import Qt
import sys
import re # For regex operations

# GUI of the main window
def create_main_window(emails, label_counts):
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
    sidebar_widget.setStyleSheet("background-color: #f6f9ff;")
    sidebar_widget.setFixedWidth(260)

    # Gmail Logo
    gmail_logo = QLabel("📧 Gmail")
    gmail_logo.setFont(QFont("Helvetica", 18, QFont.Bold))
    gmail_logo.setContentsMargins(12, 0, 0, 0)  # left margin
    sidebar_layout.addWidget(gmail_logo)
    sidebar_layout.addSpacing(10)

    # Compose Button
    compose_btn = QPushButton("🖊️  Compose")
    compose_btn.setFont(QFont("Helvetica", 12, QFont.Bold))
    compose_btn.setStyleSheet("""
        QPushButton {
            background-color: #c2e7ff;
            padding: 10px;
            border-radius: 16px;
            font-weight: bold;
            margin-left: 12px;
            margin-right: 12px;
        }
    """)
    sidebar_layout.addWidget(compose_btn)
    sidebar_layout.addSpacing(10)

    # Folder Items (Inbox, Starred, etc.)
    folder_items = [
    ("📥", "Inbox", str(label_counts.get("INBOX", "")), True),
    ("⭐", "Starred", str(label_counts.get("STARRED", "")), False),
    ("⏰", "Snoozed", str(label_counts.get("SNOOZED", "")), False),
    ("📤", "Sent", str(label_counts.get("SENT", "")), False),
    ("📝", "Drafts", str(label_counts.get("DRAFT", "")), False),
    ("▾", "More", "", False),
    ]

    for icon, name, count, is_active in folder_items:
        row = QHBoxLayout()
        row.setContentsMargins(12, 6, 12, 6)  # Left margin
        row.setSpacing(2)

        combined_label = QLabel(f"{icon}&nbsp;&nbsp;&nbsp;&nbsp;<b>{name}</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {count if count else ''}")
        combined_label.setFont(QFont("Helvetica", 12))
        combined_label.setTextFormat(Qt.RichText)

        # Highlight background if active
        bg_widget = QWidget()
        bg_layout = QHBoxLayout(bg_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.addLayout(row)

        if is_active:
            bg_widget.setStyleSheet("""
                background-color: #d2e3fc;
                border-radius: 20px;
            """)
        else:
            bg_widget.setStyleSheet("")

        row.addWidget(combined_label)
        sidebar_layout.addWidget(bg_widget)

    # Labels Section
    sidebar_layout.addSpacing(20)
    label_header = QLabel("Labels")
    label_header.setFont(QFont("Helvetica", 12, QFont.Bold))
    label_header.setContentsMargins(12, 0, 0, 0)
    sidebar_layout.addWidget(label_header)

    important_label = QLabel("🏷️ Important")
    important_label.setFont(QFont("Helvetica", 12))
    important_label.setContentsMargins(20, 0, 0, 0)
    sidebar_layout.addWidget(important_label)

    add_label = QLabel("➕ Add Label")
    add_label.setFont(QFont("Helvetica", 12))
    add_label.setContentsMargins(20, 0, 0, 0)
    sidebar_layout.addWidget(add_label)

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

    for sender, subject, snippet in emails:
        # Limit snippet length
        preview = snippet[:50] + "..." if len(snippet) > 50 else snippet

        # Clean up subject for displaying
        clean_subject = re.sub(r'<.*?>', '', subject).strip()

        row = QHBoxLayout()
        row.setContentsMargins(8, 2, 8, 2)
        row.setSpacing(6)

        # Checkbox and star
        checkbox = QLabel("☐")
        checkbox.setFixedWidth(20)
        star = QLabel("☆")
        star.setFixedWidth(20)
        row.addWidget(checkbox)
        row.addWidget(star)

        # Subject (bold) / From who it is
        subject_label = QLabel(clean_subject)
        subject_label.setFont(BOLD)
        subject_label.setStyleSheet("color: #202124")
        subject_label.setFixedWidth(250)  # Adjust as needed
        row.addWidget(subject_label)

        # Sender (bold) / About what it is
        sender_label = QLabel(sender)
        sender_label.setFont(BOLD)
        sender_label.setFixedWidth(180)
        row.addWidget(sender_label)



        # Snippet (gray)
        snippet_label = QLabel(preview)
        snippet_label.setFont(FONT)
        snippet_label.setStyleSheet("color: gray")
        snippet_label.setWordWrap(False)
        row.addWidget(snippet_label, 1)  # Stretch remaining space

        # Optional time placeholder
        time_label = QLabel("")
        time_label.setFont(SMALL)
        time_label.setStyleSheet("color: gray")
        time_label.setFixedWidth(60)
        row.addWidget(time_label)

        # Wrap in a QWidget
        row_widget = QWidget()
        row_widget.setLayout(row)
        row_widget.setFixedHeight(30)
        row_widget.setMaximumWidth(int(window.width() * 0.9))  # 90% width of main window
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


# "Only run this block if this file is being run directly, not when it’s being imported from another file." (Its now for me, so thats why there is this comment)
if __name__ == '__main__':

    emails = [
        ("Alice", "Meeting Reminder", "Don't forget our meeting at 10am tomorrow."),
        ("Bob", "Lunch?", "Are you free for lunch this week?"),
        ("Carol", "Project Update", "Here's the latest update on the project. Please review."),
    ]

    dummy_label_counts = {
        "INBOX": 3,
        "STARRED": 1,
        "SNOOZED": 0,
        "SENT": 5,
        "DRAFT": 2
    }

    create_main_window(emails, dummy_label_counts)
