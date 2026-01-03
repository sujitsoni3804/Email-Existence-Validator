# 📧 Email Existence Validator

A web-based tool for validating email addresses using SMTP verification. It checks email format, verifies domain MX records, and confirms mailbox existence through SMTP handshake.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20App-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| ✅ **Single Email Validation** | Validate individual email addresses instantly |
| 📂 **Bulk Validation** | Upload CSV/Excel files to validate multiple emails |
| 🔍 **SMTP Verification** | Confirms mailbox existence via SMTP handshake |
| 📊 **Real-time Progress** | Track validation progress for bulk operations |
| 💾 **Export Results** | Download validation results as CSV file |

---

## 🔄 Validation Process

| Step | Action |
|------|--------|
| 1 | **Format Check** - Validates email syntax using regex |
| 2 | **MX Lookup** - Resolves domain's mail exchange records |
| 3 | **SMTP Handshake** - Connects to mail server to verify mailbox |

---

## 🛠️ Tech Stack

- **Backend:** Flask, Python
- **Frontend:** HTML, CSS, JavaScript
- **Validation:** dnspython, smtplib
- **Data Processing:** Pandas, OpenPyXL

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher

### Step 1: Clone the Repository

```bash
git clone https://github.com/sujitsoni3804/Email-Existence-Validator.git
cd Email-Existence-Validator
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python app.py
```

The application will be available at:
- **Local:** http://127.0.0.1:5001

---

## 🎮 Usage

1. **Single Email:** Enter an email address and click validate
2. **Bulk Validation:** Upload a CSV/Excel file with emails in the first column
3. **Wait for Processing:** Monitor real-time progress
4. **Download Results:** Get the CSV file with validation status

---

## 📁 Project Structure

```
Email-Existence-Validator/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Web interface
└── Results/               # Validated email outputs
```

---

## 📊 Validation Results

| Status | Meaning |
|--------|---------|
| Valid | Email address exists and is deliverable |
| Invalid | Mailbox does not exist |
| Unknown | Could not verify (server blocked or timeout) |
| Invalid Email Format | Email syntax is incorrect |

---

## 🔧 Creating Executable (EXE)

Convert this application to a standalone Windows executable using PyInstaller:

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Generate EXE

```bash
pyinstaller --onefile --add-data "templates;templates" app.py
```

### Step 3: Locate Executable

The executable will be created in the `dist/` folder:
```
dist/
└── app.exe
```

> **Note:** Run the EXE from command prompt or ensure the `Results` folder exists in the same directory as the executable.

---

<p align="center">
  Made with ❤️ for Email Validation
</p>
