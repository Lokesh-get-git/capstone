# 🚀 Intelligent Interview Prep System - Setup Guide

This guide will walk you through setting up the project from scratch on your local machine.

## 📋 Prerequisites

Ensure you have the following installed:
1.  **Git**: [Download Git](https://git-scm.com/downloads)
2.  **Python 3.10+**: [Download Python](https://www.python.org/downloads/)
    *   *Note: Ensure "Add Python to PATH" is checked during installation.*
3.  **VS Code** (Optional but recommended): [Download VS Code](https://code.visualstudio.com/)

---

## 🛠️ Installation Steps

### 1. Clone the Repository
Open your terminal (Command Prompt, PowerShell, or Git Bash) and run:
```bash
git clone https://github.com/Lokesh-get-git/capstone
cd capstone
```

### 2. Create a Virtual Environment
It's best practice to isolate dependencies.
```bash
# Windows
python -m venv venv

# Mac/Linux
python3 -m venv venv
```

### 3. Activate the Virtual Environment
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```


### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

```bash
pip install langchain langchain-groq langgraph fastapi uvicorn streamlit python-dotenv pdfplumber scikit-learn pandas sentence-transformers
```

---

## ⚙️ Configuration

1.  **Create a [.env] file** in the root directory (`capstone/`).
2.  Add your API keys. You will need a **Groq API Key** for the LLM.

**[.env] content:**
```ini
GROQ_API_KEY=gsk_...  <-- Replace with your actual key
```
*Get a free key at [console.groq.com](https://console.groq.com)*

3.  (Optional) If using Tavily for search:
```ini
TAVILY_API_KEY=tvly-...
```

---

## 🏃‍♂️ Running the Application

The system consists of a **FastAPI Backend** and a **Streamlit UI**. You need to run both.

### Option A: Run Both (Recommended for Dev)
Open **two separate terminal windows**. Ensure [(venv)] is active in both.

**Terminal 1 (Backend API):**
```bash
uvicorn api.main:app --reload
```
*You should see: `Uvicorn running on http://127.0.0.1:8000`*

**Terminal 2 (Frontend UI):**
```bash
streamlit run ui/app.py
```
*This will automatically open your browser to `http://localhost:8501`*

---
---

## 📂 Project Structure
- `agents/`: Core logic for AI agents (Strategist, Generator, etc.).
- [ml/]: Machine Learning models for risk and readiness.
- `api/`: FastAPI backend endpoints.
- [ui/]: Streamlit frontend code.
- `services/`: Utility services like CostTracking.
- `parsers/`: PDF and text parsing logic.

---

## ❓ Troubleshooting

**Issue: "Module not found"**
*   Fix: Ensure your virtual environment is active ([(venv)]) and you ran `pip install -r requirements.txt`.

**Issue: "Groq API Key not found"**
*   Fix: Check that your [.env] file exists and has the correct variable name `GROQ_API_KEY`.

**Issue: "File not found: sample_resume.txt"**
*   Fix: Ensure a text file named [sample_resume.txt] exists in the root folder for testing.

## NOTE
a log file and cost log file will be generated in your root upon using.
