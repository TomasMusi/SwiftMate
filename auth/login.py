# Imports 
import tkinter as tk
import webbrowser # Importing tkinter for GUI
from PIL import Image, ImageTk

import os
import mysql.connector  # Importing MySQL connector for database operations
# Google API imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from datetime import datetime

# Google permissions (scopes)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Function to list messages from Gmail
def list_messages(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute() # Fetching message details
        headers = msg_detail.get('payload', {}).get('headers', []) # Extracting headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)") # Extracting subject
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)") # Extracting sender
        snippet = msg_detail.get('snippet', '') # Extracting snippet
        emails.append((subject, sender, snippet)) # Appending to emails list
    
    return emails


def get_db_connection():
    """Establish a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"), 
            user=os.getenv("DB_USER"), 
            port=int(os.getenv("DB_PORT", 3306)), # Default to 3306 if not set
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def save_user_token(email, credentials):
    conn = get_db_connection()
    
    # Check if the connection was successful
    if conn is None:
        print("❌ Could not connect to database.")
        return
    
    cursor = conn.cursor()

    # Prepare the credentials for storage
    query = """
        INSERT INTO Users (email, access_token, refresh_token, token_expiry, scopes)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            access_token = VALUES(access_token),
            refresh_token = VALUES(refresh_token),
            token_expiry = VALUES(token_expiry),
            scopes = VALUES(scopes)
    """
    # Convert credentials to a format suitable for storage (preventing issues with SQL injection)
    values = (
        email,
        credentials.token,
        credentials.refresh_token,
        credentials.expiry.strftime("%Y-%m-%d %H:%M:%S") if credentials.expiry else None,
        " ".join(credentials.scopes)
    )

    cursor.execute(query, values)
    conn.commit() # Commit the transaction
    conn.close() # Close the database connection

# Login via Google and store user token
def login_with_google():
    try:
        # Load the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file("auth/credentials.json", SCOPES)

        # This will open the browser and wait for login (best for desktop apps)
        creds = flow.run_local_server(port=0)

        # Use credentials to access Gmail
        service = build("gmail", "v1", credentials=creds)
        profile = service.users().getProfile(userId="me").execute()
        email = profile["emailAddress"]

        # Save token to database
        save_user_token(email, creds)

        # fetch messages from Gmail
        messages = list_messages(service)


        # GUI: Show messages
        menu_root = tk.Tk()
        menu_root.title("SwiftMate - Inbox")
        menu_root.geometry("700x500")
        menu_root.configure(bg="white")

        title_label = tk.Label(menu_root, text=f"Inbox for {email}", font=("Helvetica", 16, "bold"), bg="white", fg="#333")
        title_label.pack(pady=(20, 10))

        # Frame for text + scrollbar
        frame = tk.Frame(menu_root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        text_area = tk.Text(frame, yscrollcommand=scrollbar.set, wrap=tk.WORD, font=("Helvetica", 12))
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        for i, (subject, sender, snippet) in enumerate(messages, start=1):
            text_area.insert(tk.END, f"{i}. 📩 Subject: {subject}\n")
            text_area.insert(tk.END, f"   👤 From: {sender}\n")
            text_area.insert(tk.END, f"   ✏️ Snippet: {snippet}\n\n")

        text_area.config(state=tk.DISABLED)  # Make read-only

        menu_root.mainloop()

    except Exception as e:
        print(f"❌ Error during Google login: {e}")
        return

