# Imports 
import os
import mysql.connector  # Importing MySQL connector for database operations
# Google API imports
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

# Google permissions (scopes)
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Function to list messages from Gmail
def list_messages(service, max_results=10):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        label_ids = msg_detail.get('labelIds', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
        snippet = msg_detail.get('snippet', '')

         # Get the timestamp and format it
        timestamp = int(msg_detail.get('internalDate', 0)) // 1000
        date_str = datetime.fromtimestamp(timestamp).strftime("%b %d")  # e.g., "Jul 22"

        email_data = (sender, subject, snippet, date_str)
        emails.append(email_data)

    return emails

# Function to get label counts (e.g., Inbox, Starred)
def get_label_counts(service):
    label_stats = {} # empty array for label stats
    labels = service.users().labels().list(userId='me').execute().get('labels', [])

    for label in labels:
        if label['name'] in ['INBOX', 'STARRED', 'SNOOZED', 'SENT', 'DRAFT']:
            label_id = label['id']
            messages = service.users().messages().list(userId='me', labelIds=[label_id], maxResults=500).execute()
            count = len(messages.get('messages', []))
            label_stats[label['name']] = count

    return label_stats

# Function to get starred messages
def get_starred_messages(service, max_results=50):
    """Fetch emails that are labeled as STARRED."""
    results = service.users().messages().list(userId='me', labelIds=['STARRED'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    starred_emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
        snippet = msg_detail.get('snippet', '')
        timestamp = int(msg_detail.get('internalDate', 0)) // 1000
        date_str = datetime.fromtimestamp(timestamp).strftime("%b %d")

        starred_emails.append((sender, subject, snippet, date_str))

    return starred_emails

# Function to get sent messages
def get_sent_messages(service, max_results=50):
    """Fetch emails that are labeled as SENT."""
    results = service.users().messages().list(userId='me', labelIds=['SENT'], maxResults=max_results).execute()
    messages = results.get('messages', [])

    sent_emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(No Sender)")
        snippet = msg_detail.get('snippet', '')
        timestamp = int(msg_detail.get('internalDate', 0)) // 1000
        date_str = datetime.fromtimestamp(timestamp).strftime("%b %d")

        sent_emails.append((sender, subject, snippet, date_str))

    return sent_emails

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

        # Returning emails and label counts to main.py
        emails = list_messages(service)
        label_counts = get_label_counts(service)

        # Return all the necessary data (service, for fetching more emails later)
        return emails, label_counts, service 

    # If login fails, handle the exception
    except Exception as e:
        print(f"❌ Error during Google login: {e}")
        return None, None, None

