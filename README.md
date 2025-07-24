# 💌 SwiftMate — Gmail Desktop Client (Python / PySide6 / AI)

**A modern Gmail-powered email client** built natively using **Python and Qt (PySide6)**. SwiftMate brings a clean, fast, and AI-augmented desktop experience to managing your email — complete with calendar integration and smart features.

> 🎯 Designed for productivity-focused users who want Gmail on their desktop, enhanced with AI reply generation, clean layouts, and native OS integration.

---

(IMG)

## 🧩 About the Project
SwiftMate is built using **PySide6 (Qt for Python)**, offering a smooth, polished, and responsive desktop GUI. It securely connects to your Gmail and Calendar through the **Google API**, allowing you to send, receive, and manage emails without needing your browser.

> 🤖 Bonus: integrated AI features bring smart email suggestions, automatic categorization, and intelligent inbox management.


## ✨ Features


| Feature                     | Description                                                                 |
|---------------------------- |-----------------------------------------------------------------------------|
| 🖥️  **Modern Qt UI**        | Clean interface with custom themes, layouts, and responsive components     |
| 📅 **Calendar**             | Schedule emails or Your Plans     |
| 🤖 **AI**                   | Uses AI to generate smart replies and auto-sort emails by intent           |
| 📥 **Smart Inbox Sorting**     | AI organizes your inbox by intent and priority                                |
| 🌗 **Dark Mode**     | 	Full support for dark/light themes with Qt palettes   |


---

## 🛠 Tech Stack

- **Language**: Python 3.11
- **GUI**: PySide6 (Qt for Python)
- **Email/Calendar Integration**: Gmail & Calendar 
- **AI Tools**: AI for smart replies, sorting and summarizing emails.
- **Auth**: OAuth 2.0 (via google-auth)
- **Image & UI Assets**: QPixmap, QPalette, and Qt stylesheets
- **Env Managment**: `python-dotenv` 

---

## 🖼️ Screenshots

<img width="1286" height="735" alt="Screenshot from 2025-07-24 17-19-34" src="https://github.com/user-attachments/assets/305d6cbd-bbbf-4d41-a944-783ceeebc980" />

---

## 🧠 What I Learned

Building SwiftMate taught me:

- How to use PySide6 for creating fluid, responsive desktop apps
- Working with the Gmail API
- Implementing OAuth2 authentication flows
- Integrating AI features in a GUI app 
- Designing modular, scalable Python apps with clean UI/UX

---


## 📌 Roadmap

- [X] Login with Google using OAuth2
- [X] View and compose Gmail messages
- [] Calendar event viewer
- [] AI smart reply suggestions
- [] Inbox categorization via AI
- [] PySide6 dark/light theme support
- [] Sidebar navigation for mail, calendar, and settings
- [] Desktop notifications


## 📁 Directory Structure

```
Swiftmate/
├── auth/
│ ├── login.py # Handles Google OAuth2 login
│ ├── credentials.json # Gmail API credentials (keep secure!)
│ └── pycache/ # Auto-generated Python bytecode
│
├── database/
│ └── schema.sql # (Optional) Database schema for local storage
│
├── menu/
│ ├── menu.py # App menu layout and navigation logic
│ └── pycache/ # Auto-generated Python bytecode
│
├── imgs/
│ ├── logo.png # App logo
│ └── SwiftMateLogo.png # High-res or alternate logo
│
├── venv/ # Python virtual environment (excluded from Git)
│ ├── bin/ # Scripts and executables
│ ├── include/ # Header files
│ ├── lib/ # Installed libraries
│ ├── lib64/ # (symlink) for 64-bit platforms
│ └── pyvenv.cfg # Virtual environment configuration
│
├── main.py # Main entry point for launching the app
├── requirements.txt # Project dependencies
├── licence.md # License information
├── README.md # Project documentation
```

## 🚀 Building Locally
```bash
# Clone the repo
git clone https://github.com/TomasMusi/SwiftMate.git
cd SwiftMate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Fill in DB Info

# Run the app
python app.py
```