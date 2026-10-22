# Intellipaat Module 6: First AI Application (Chatbot)

A complete, production-ready AI Chatbot project built for **Intellipaat Module 6**, demonstrating input validation, secure credential handling, OpenRouter API integration, timeout/network resilience, response sanitization, and dual CLI & FastAPI backend interfaces.

---

## 📁 Project Directory Structure

```
chatbot/
│
├── ANSWERS.md                     # Comprehensive answers to all 33 questions (Activities 1 - 8)
├── README.md                      # Complete documentation & test execution log
├── .gitignore                     # Git configuration safeguarding credentials & virtualenvs
│
├── backend/                       # Backend Application Folder
│   ├── .env.example               # Configuration template (safe to commit/submit)
│   ├── requirements.txt           # Python dependencies manifest
│   ├── config.py                  # Activity 3: Secure credential loader & startup validator
│   ├── response_cleaner.py        # Activity 7: AI response cleaning & markdown sanitization
│   ├── chatbot.py                 # Activities 4, 5, 6, 7: Core chatbot engine
│   ├── cli.py                     # Activities 4 & 8: Continuous interactive CLI chatbot loop
│   ├── server.py                  # Activity 2: FastAPI backend with CORS & health/chat routes
│   └── test_suite.py              # Activity 8: Verification suite testing all failure/success states
│
└── frontend/                      # Web UI (bonus demonstrating CORS support)
    ├── index.html                 # Glassmorphic chatbot UI
    ├── style.css                  # Modern dark-mode responsive styles
    └── app.js                     # REST client connecting to backend /api/chat
```

---

## 🚀 Quickstart & Setup Guide

### 1. Configure the Virtual Environment (Activity 2)
Open PowerShell or your preferred terminal inside the `chatbot/backend` directory:

```powershell
cd "d:\gen ai agent\chatbot\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Command Prompt:
.\venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Credentials (Activity 1 & 3)
Copy `.env.example` to create your private `.env` file:

```powershell
copy .env.example .env
```

Open `.env` and configure your API key:
```ini
OPENROUTER_API_KEY=your_openrouter_api_key_here
CHATBOT_MODEL=meta-llama/llama-3.2-3b-instruct:free
REQUEST_TIMEOUT=15
```
*(Note: As a convenience fallback, if you have a `GROQ_API_KEY` in your environment, the chatbot will automatically detect and support it as well!)*

---

## 🧪 Running Hands-On Activities & Tests

### Running the Interactive CLI Chatbot (Activities 4, 7, 8)
```powershell
.\venv\Scripts\python.exe cli.py
```
- Type any question and press Enter.
- Press Enter on empty inputs to observe input validation warnings.
- Type `exit` or `quit` to cleanly exit the session.

### Running the Automated Test Suite (Activity 8)
```powershell
.\venv\Scripts\python.exe test_suite.py
```
This script automatically executes and validates:
1. **Empty input rejection** (`validate_user_input` test)
2. **Exit command handling** (`exit`, `quit`, case insensitivity)
3. **Response cleaner** (Markdown and code-block sanitization)
4. **Missing & invalid API key handling** (HTTP 401 error capture)
5. **Network error & timeout handling** (Connection drops & timeout traps)
6. **Live valid question execution** (Receiving and formatting real AI reply)

### Running the Backend Web Server with CORS (Activity 2 & 8)
```powershell
.\venv\Scripts\python.exe server.py
```
- API Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`
- Chat Route: `POST http://127.0.0.1:8000/api/chat`

To test the frontend, open `chatbot/frontend/index.html` in your web browser while `server.py` is running.

---

## 📋 Activity-by-Activity Feature Checklist

| Activity | Requirement | Implementation File | Verification Status |
| :--- | :--- | :--- | :--- |
| **Activity 1** | Project organization (`chatbot/` & `backend/`) | Folder structure | Completed & Verified |
| **Activity 2** | Virtual environment & dependencies | `backend/venv`, `requirements.txt` | Completed & Verified |
| **Activity 3** | Secure API key load & validation | `backend/config.py` | Completed & Verified |
| **Activity 4** | Continuous loop, whitespace trim, exit | `backend/chatbot.py`, `backend/cli.py` | Completed & Verified |
| **Activity 5** | API error handling & structure validation | `backend/chatbot.py` | Completed & Verified |
| **Activity 6** | Network & timeout error handling | `backend/chatbot.py` | Completed & Verified |
| **Activity 7** | Clean & display AI response | `backend/response_cleaner.py` | Completed & Verified |
| **Activity 8** | Run & test all edge cases | `backend/test_suite.py`, `backend/cli.py` | Completed & Verified |

---

## 🔒 Security Notice for Submission
As specified in the curriculum guidelines:
> *Important: Do not include your actual API key in the submission.*

The project includes `.gitignore` and `.env.example` templates ensuring no live secret keys are packaged.
