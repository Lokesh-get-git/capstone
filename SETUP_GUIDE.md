# ⚙️ Hackathon Setup & Verification Guide

This quick setup sheet will guide you through spinning up and validating the **Intelligent Interview Prep System** in under 2 minutes.

---

## 🛠️ Step-by-Step Installation

### Step 1: Initialize Virtual Environment & Dependencies
Open your PowerShell, Command Prompt, or terminal in the project directory:
```bash
# 1. Create Python Virtual Environment
python -m venv venv

# 2. Activate Virtual Environment
# On Windows (PowerShell):
.\venv\Scripts\Activate
# On Windows (Cmd):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# 3. Install Required Libraries
pip install -r requirements.txt
```

### Step 2: Establish Credentials
Create a file named `.env` in the project root and add your Groq API credentials:
```ini
GROQ_API_KEY=gsk_...
```
*(Get a free instant key at [console.groq.com](https://console.groq.com) if you do not have one).*

### Step 3: Run the Unified Service
Start the FastAPI server (which hosts both the APIs and the React Dashboard concurrently):
```bash
uvicorn api.main:app
```
*(You will see a log indicating `Uvicorn running on http://127.0.0.1:8000`).*

---

## 🔍 Validation Checklist

1. **Access Web Portal**:
   Open **[http://localhost:8000](http://localhost:8000)** in your web browser. You should see a cyber-dark, glassmorphic welcome page titled **"AI Interview Preparation System"** showing the active agent state diagram.

2. **Upload Test Resume**:
   - In the left sidebar, click the **"Upload Resume"** drag-and-drop box.
   - Choose the provided file: **`sample_resume.txt`** located in the project's root folder.
   - Set Years of Experience to `5` and Target Role to `Software Engineer`.
   - Click **🚀 Analyze Resume**.

3. **Verify Orchestration Steps**:
   You will see an animated checklist sequence through all seven agent nodes (Analyst, Strategist, Planner, Generator, Validator, and Coach).

4. **Explore Dashboard Tabs**:
   Once finished, verify that the following components render:
   - **📊 Resume Analysis**: Review extracted claims and their associated ML risk labels (Red/Amber/Green).
   - **🎤 Practice Interview**: Click the tailored questions to expand the collapse panels and view answer checklists.
   - **💡 AI Coach**: Toggle open the **"AI Grading Breakdown"** to view features and weights, and review specific advice cards.

---

## 📂 Hackathon Package Checklist
- **`sample_resume.txt`**: The pre-packaged candidate resume provided for quick testing.
- **`synthetic_resume_training.csv`**: Used to train the ML ensemble risk classifiers.
- **`frontend/dist/`**: The pre-built, production-optimized React SPA static client folder.
