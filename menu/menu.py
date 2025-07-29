from unicodedata import name
from PySide6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                                 QHBoxLayout, QLineEdit, QFrame)
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtCore import Qt
import re
import base64
from datetime import datetime
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QTextEdit, QPushButton, QScrollArea
from PySide6.QtWebEngineWidgets import QWebEngineView
import html
import re
import html
import re
from auth.login import get_sent_messages, get_starred_messages # For regex operations


# Global variables
_menu_window = None # Keep a reference to prevent garbage collection
_main_layout = None
_emails_container = None
_folder_widgets = {}  # Store folder widgets for easy access
_active_folder = "Inbox"  # Default active folder


# Global lists to store emails by category
_all_emails = []
_gmail_service = None  # To store the Gmail API service


# Regex function to convert plain text links to HTML hyperlinks
def plain_text_to_html_with_links(text):
    # 1. Escape HTML special characters (&, <, >)
    text = html.escape(text) 

    # 2. Replace labeled links: Label (https://...)
    def replace_labeled(match):
        label = match.group(1).strip()
        url = match.group(2)
        return f'<a href="{url}">{label}</a>'

    text = re.sub(r'([^\n()]{2,100}?)\s*\((https?://[^\s()]+)\)', replace_labeled, text)

    # 3. Replace raw links like (https://...)
    def replace_raw(match):
        url = match.group(1)
        return f'<a href="{url}">{url}</a>'

    text = re.sub(r'\((https?://[^\s()]+)\)', replace_raw, text)

    # 4. Convert newlines to <br> for HTML formatting
    text = text.replace('\n', '<br>')

    return text


# Function that shows full message (when message_id is parsed.)
def show_full_email(message_id):
    global _emails_container  # We're using this layout to display the email

    # 1. Step Clear the email view layout
    # Clear previous email list view
    while _emails_container.count(): # This counts till there are no items in the container
        item = _emails_container.takeAt(0) # remove the item from the container
        # If the item has a widget, delete it
        if item.widget():
            item.widget().deleteLater()

    try:

        # 2. Fetch full message details from Gmail API
        msg_detail = _gmail_service.users().messages().get(userId='me', id=message_id, format='full').execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
        date_raw = int(msg_detail.get('internalDate', 0)) // 1000
        date_str = datetime.fromtimestamp(date_raw).strftime("%b %d, %Y %H:%M")

        # 3. Extract HTML content (fallback to plain text if missing)
        def extract_body(payload):
            if payload.get("mimeType") == "text/html" and "data" in payload.get("body", {}):
                data = payload["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8")

            if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
                data = payload["body"]["data"]
                return base64.urlsafe_b64decode(data).decode("utf-8")

            if "parts" in payload:
                for part in payload["parts"]:
                    result = extract_body(part)
                    if result:
                        return result

            return None         

        # Function to extract attachments
        # This function recursively checks for attachments in nested parts
        def extract_attachments(payload):
            attachments = []
            if "parts" in payload:
                for part in payload["parts"]:
                    filename = part.get("filename")
                    body = part.get("body", {})
                    attachment_id = body.get("attachmentId")
                    if filename and attachment_id:
                        attachments.append({
                            "filename": filename,
                            "attachment_id": attachment_id,
                            "mimeType": part.get("mimeType"),
                            "part": part,
                        })
                    # Recursively check nested parts
                    attachments.extend(extract_attachments(part))
            return attachments
 
        
        # Extract body from the payload
        body = extract_body(msg_detail.get("payload", {})) or "<i>(No content found)</i>"

        # Convert plain text to HTML if needed
        if "<html" not in body.lower():
            body = plain_text_to_html_with_links(body)


        # 4. Create UI elements
        subject_label = QLabel(subject)
        subject_label.setFont(QFont("Helvetica", 16, QFont.Bold))

        sender_label = QLabel(f"From: {sender}")
        sender_label.setFont(QFont("Helvetica", 12))
        sender_label.setStyleSheet("color: gray")

        date_label = QLabel(date_str)
        date_label.setFont(QFont("Helvetica", 10))
        date_label.setStyleSheet("color: gray")

        body_view = QWebEngineView()
        print("📤 FINAL BODY HTML (partial preview):\n", body[:500], "...\n")
        body_view.setHtml(body)
        body_view.setMinimumHeight(400)

        back_btn = QPushButton("← Back to Emails")
        back_btn.setFixedWidth(200)
        back_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        back_btn.clicked.connect(return_to_email_list)  # go back to inbox

        # 5. Put Everything into Layout
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(back_btn)
        layout.addWidget(subject_label)
        layout.addWidget(sender_label)
        layout.addWidget(date_label)
        layout.addWidget(body_view)

        # Extract attachments
        attachments = extract_attachments(msg_detail["payload"])
        if attachments:
            for attach in attachments:
                download_btn = QPushButton(f"📎 {attach['filename']} (Click to Download)")
                download_btn.setStyleSheet("padding: 6px;")
                
                # Needed to "capture" attach inside loop
                def download_file(attach_data):
                    try:
                        attach_data = _gmail_service.users().messages().attachments().get(
                            userId="me",
                            messageId=message_id,
                            id=attach_data["attachment_id"]
                        ).execute()

                        file_data = base64.urlsafe_b64decode(attach_data["data"])

                        # Ask user where to save the file
                        save_path, _ = QFileDialog.getSaveFileName(
                            None,
                            "Save Attachment",
                            attach["filename"]
                        )

                        if save_path:
                            with open(save_path, "wb") as f:
                                f.write(file_data)
                            print(f"✅ Saved to: {save_path}")
                        else:
                            print("⚠️ Save canceled by user.")

                    except Exception as e:
                        print(f"❌ Failed to download {attach['filename']}: {e}")

                download_btn.clicked.connect(lambda checked=False, a=attach: download_file(a))
                layout.addWidget(download_btn)

        container = QWidget()
        container.setLayout(layout)
        _emails_container.addWidget(container)

    except Exception as e:
        print("❌ Error showing full email:", e)


def return_to_email_list():
    render_emails(_all_emails)

def render_emails(email_list):
    global _emails_container

    # Clear old email widgets
    while _emails_container.count():
        item = _emails_container.takeAt(0)
        if item.widget():
            item.widget().deleteLater()

    FONT = QFont("Helvetica", 12)
    BOLD = QFont("Helvetica", 12, QFont.Bold)
    SMALL = QFont("Helvetica", 10)

    for msg_id, sender, subject, snippet, date_str in email_list:
        preview = snippet[:50] + "..." if len(snippet) > 50 else snippet
        clean_subject = re.sub(r'<.*?>', '', subject).strip()

        row = QHBoxLayout()
        row.setContentsMargins(8, 0, 8, 0)
        row.setSpacing(6)

        checkbox = QLabel("☐")
        checkbox.setFixedWidth(20)
        star = QLabel("☆")
        star.setFixedWidth(20)
        row.addWidget(checkbox)
        row.addWidget(star)

        subject_label = QLabel(clean_subject)
        subject_label.setFont(BOLD)
        subject_label.setStyleSheet("color: #202124")
        subject_label.setFixedWidth(250)
        row.addWidget(subject_label)

        sender_label = QLabel(sender)
        sender_label.setFont(BOLD)
        sender_label.setFixedWidth(180)
        row.addWidget(sender_label)

        snippet_label = QLabel(preview)
        snippet_label.setFont(FONT)
        snippet_label.setStyleSheet("color: gray")
        snippet_label.setWordWrap(False)
        row.addWidget(snippet_label, 1)

        # Date label aligned right
        time_label = QLabel(date_str)
        time_label.setFont(SMALL)
        time_label.setStyleSheet("color: gray")
        time_label.setFixedWidth(60)
        time_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        row.addWidget(time_label)

        row_widget = QWidget()
        row_widget.setLayout(row)
        row_widget.setFixedHeight(30)


        # Connect a click to open full view
        row_widget.mousePressEvent = lambda event, mid=msg_id: show_full_email(mid)

        row_widget.setMaximumWidth(int(_menu_window.width() * 0.9))
        row_widget.setStyleSheet("""
            QWidget {
                margin: 0px;
                padding: 0px;
            }
            QWidget:hover {
                background-color: #f5f5f5;
            }
        """)

        _emails_container.addWidget(row_widget)

# Function to handle folder clicks and update active folder
def handle_folder_click(folder_name, handler_func):
    global _active_folder

    # Reset old active background
    if _active_folder in _folder_widgets:
        _folder_widgets[_active_folder].setStyleSheet("")

    # Set new active background
    if folder_name in _folder_widgets:
        _folder_widgets[folder_name].setStyleSheet("background-color: #d2e3fc; border-radius: 20px;")

    _active_folder = folder_name
    handler_func()  # Call the original click handler like handle_starred_click()

# Functions for sidemenu folder_items   

def handle_inbox_click():
    print("Clicked on Inbox")
    render_emails(_all_emails)

def handle_starred_click():
    print("Clicked on Starred")
    if _gmail_service is not None:
        starred_emails = get_starred_messages(_gmail_service)
        render_emails(starred_emails)

def handle_snoozed_click():
    print("Clicked on Snoozed")

def handle_sent_click():
    print("Clicked on Sent")
    if _gmail_service is not None:
        sent_messages = get_sent_messages(_gmail_service)
        render_emails(sent_messages)

def handle_drafts_click():
    print("Clicked on Drafts")

def handle_more_click():
    print("Clicked on More")




# GUI of the main window
def create_main_window(emails, label_counts):    
    # Make sure we keep reference to prevent GC
    global _menu_window, _main_layout, _emails_container
    global _all_emails


    # Save emails globally
    _all_emails = emails


    # Big Error, cannot create this, because we have this already in main.py -> app = QApplication(sys.argv)
    _menu_window = QWidget()
    _menu_window.setWindowTitle("SwiftMate - Gmail Client by Tom Musil")
    _menu_window.resize(1200, 700)

    # Fonts
    FONT = QFont("Helvetica", 12)
    BOLD = QFont("Helvetica", 12, QFont.Bold)
    SMALL = QFont("Helvetica", 10)

    # --- Sidebar ---
    sidebar_layout = QVBoxLayout()
    sidebar_widget = QWidget()
    sidebar_widget.setStyleSheet("background-color: #f6f9ff;")
    sidebar_widget.setFixedWidth(260)

    # SwiftMate Logo with Image + Text
    logo_layout = QHBoxLayout()
    logo_layout.setContentsMargins(12, 0, 0, 0)  # Add some left margin
    logo_layout.setSpacing(0)

    # Load logo image
    logo_path = "imgs/SwiftMateLogo.png" 
    logo_pixmap = QPixmap(logo_path).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    logo_img = QLabel()
    logo_img.setPixmap(logo_pixmap)
    logo_img.setFixedSize(48, 48)               # Shrink the QLabel box
    logo_img.setScaledContents(True)            # Force the pixmap to fill the label

    # Text label
    logo_text = QLabel("SwiftMate")
    logo_text.setFont(QFont("Helvetica", 18, QFont.Bold))
    logo_text.setStyleSheet("color: #1a73e8;")  # Optional: color to match branding

    # Add image and text to layout
    logo_layout.addWidget(logo_img)
    logo_layout.addWidget(logo_text)

    # Wrap in a widget
    logo_widget = QWidget()
    logo_widget.setLayout(logo_layout)
    sidebar_layout.addWidget(logo_widget)
    sidebar_layout.addSpacing(0)
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
    sidebar_layout.addSpacing(0)

    # Folder Items (Inbox, Starred, etc.)
    folder_items = [
    ("📥", "Inbox", str(label_counts.get("INBOX", "")), True, handle_inbox_click),
    ("⭐", "Starred", str(label_counts.get("STARRED", "")), False, handle_starred_click),
    ("⏰", "Snoozed", str(label_counts.get("SNOOZED", "")), False, handle_snoozed_click),
    ("📤", "Sent", str(label_counts.get("SENT", "")), False, handle_sent_click),
    ("📝", "Drafts", str(label_counts.get("DRAFT", "")), False, handle_drafts_click),
    ("▾", "More", "", False, handle_more_click),
    ]

    for icon, name, count, is_active, click_handler in folder_items:
        row = QHBoxLayout()
        row.setContentsMargins(12, 6, 12, 6)
        row.setSpacing(2)

        folder_btn = QPushButton(f"{icon}  {name}")
        folder_btn.setFont(QFont("Helvetica", 12))
        folder_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 6px;
                border: none;
                background-color: transparent;
            }
        """)

        count_label = QLabel(count if count else "")
        count_label.setFont(QFont("Helvetica", 11))
        count_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        count_label.setContentsMargins(0, 0, 8, 0)
        count_label.setFixedWidth(24)

        row.addWidget(folder_btn)
        row.addStretch()
        row.addWidget(count_label)

        bg_widget = QWidget()
        bg_layout = QHBoxLayout(bg_widget)
        bg_layout.setContentsMargins(0, 0, 0, 0)
        bg_layout.addLayout(row)

        if is_active:
            bg_widget.setStyleSheet("background-color: #d2e3fc; border-radius: 20px;")
        else:
            bg_widget.setStyleSheet("")

        sidebar_layout.addWidget(bg_widget)

        # Store reference to the widget so we can toggle later
        _folder_widgets[name] = bg_widget

        # Connect button and pass its name
        folder_btn.clicked.connect(lambda checked, n=name, h=click_handler: handle_folder_click(n, h))

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
    _main_layout = QVBoxLayout()  # This contains search, tabs, and email rows
    _main_layout.setSpacing(0)

    # Search bar
    search_box = QWidget()
    search_box.setStyleSheet("background-color: #e5f1ff; border-radius: 16px; padding: 0px;")
    search_box.setFixedHeight(32)  # <-- This controls the *visible height*
    search_box.setFixedWidth(int(_menu_window.width() * 0.5)) # <-- This controls the *visible width* 70%
    search_box.setStyleSheet("""
        background-color: #e5f1ff;
        border-radius: 16px;
        padding: 0px;
    """)

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
    _main_layout.addWidget(search_box)

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
    _main_layout.addWidget(tabs_container)
    _emails_container = QVBoxLayout()
    _main_layout.addLayout(_emails_container)

    # Render emails in the main area
    render_emails(_all_emails)

    # --- Combine Sidebar and Main Area ---
    container = QHBoxLayout()
    container.addWidget(sidebar_widget)

    main_area_widget = QWidget()
    main_area_widget.setLayout(_main_layout)
    container.addWidget(main_area_widget)

    _menu_window.setLayout(container)
    _menu_window.show()
    # Cannot also use this, because it is not the main.py! Same Error as the same above. -> sys.exit(app.exec())