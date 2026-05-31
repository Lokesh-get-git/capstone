# 🧠 Intelligent Interview Prep System

A sophisticated, multi-agent AI framework designed to prepare candidates for high-level technical interviews. The system orchestrates a team of specialized AI nodes using **LangGraph**, combining **Hybrid Resume Parsing**, **Machine Learning Classifier Models**, and **Generative AI** to deliver a bespoke, high-fidelity interview dashboard.

This Capstone & Hackathon edition consolidates both the **FastAPI backend** and a gorgeous, custom-styled **React + Vite + Vanilla CSS** dashboard into a unified project. The entire application runs concurrently with **a single terminal command**.

---

## 🚀 Key Highlights & Flagship Features

1. **Cyclical Multi-Agent State Orchestration (LangGraph)**:
   - Orchestrates six specialized nodes (`Analyst` ➔ `Strategist` ➔ `Planner` ➔ `Generator` ➔ `Validator` ➔ `Coach`) working in a state-dependent feedback loop.
   - Enforces a quality control loop: if questions fail quality metrics, the `Validator` routes them back to the `Generator` for context-aware refinement.

2. **Machine Learning Risk Detection & Calibrated Scoring**:
   - Uses an ensemble classifier (Logistic Regression vs. Random Forest) calibrated using `CalibratedClassifierCV` to detect weak or unsubstantiated claims on a resume.
   - Computes a dynamic **Readiness Score (0-100)** mapping candidates to levels (Beginner, Intermediate, Expert) while penalizing vague and risky assertions.

3. **Sleek Cyber-Dark Developer Dashboard**:
   - A fully responsive React Single Page Application (SPA) designed using glassmorphism.
   - Features real-time, pulsing progress bars tracking agent steps, an interactive claim assessment table with glows, and tailored practice accordions with checklist points.

4. **Zero CORS / Unified Deployment**:
   - The compiled React client is hosted directly by the FastAPI web server. Running the backend immediately launches the frontend on the same port with zero cross-origin configuration required.

---

## 🏗️ Technical Architecture & Directory Layout

```
├── agents/             # Core LangGraph agent nodes & cyclical state graph
│   ├── resume_analyst.py
│   ├── question_strategist.py
│   ├── difficulty_planner.py
│   ├── question_generator.py
│   ├── validator.py
│   └── coach.py
├── ml/                 # Machine Learning modules (Risk Classifiers & Scorer models)
│   ├── risk_classifier.py
│   └── readiness_scorer.py
├── api/                # FastAPI endpoint controllers & static React web server
│   └── main.py
├── frontend/           # High-fidelity React + Vite + Vanilla CSS client application
│   ├── src/            # App.jsx states, index.css cyberpunk styles, assets
│   ├── index.html      # SEO metadata & Google Fonts imports
│   └── dist/           # Compiled, production-ready static assets
├── parsers/            # PDF and text parsers utilizing pdfplumber & regex
├── services/           # Utility integrations (Token tracking & cost counters)
└── utils/              # Config systems and logger helpers
```

---

## 🏃‍♂️ Quick Start (Single-Command Execution)

### 📋 Prerequisites
- **Python 3.10+**
- **Node.js 20+** (only if rebuilding frontend files)
- **Groq API Key** (Get a free key at [console.groq.com](https://console.groq.com))

### 🛠️ Setup Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Lokesh-get-git/capstone.git
   cd capstone
   ```

2. **Install Python Dependencies**:
   ```bash
   python -m venv venv
   # Activate virtual env:
   # Windows: .\venv\Scripts\activate
   # macOS/Linux: source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Configure Environment variables**:
   Create a `.env` file in the root directory and append your API key:
   ```ini
   GROQ_API_KEY=gsk_your_actual_groq_api_key
   # Optional: Tavily key for web searches during coaching
   TAVILY_API_KEY=tvly-your_key
   ```

4. **Start the Application**:
   ```bash
   uvicorn api.main:app --reload
   ```
   
That's it! Navigate to **[http://localhost:8000](http://localhost:8000)** in your browser to experience the dashboard.

---

## 🛠️ Developer Mode (Frontend Customizations)

If you wish to make live modifications to the React code and experience Hot Module Replacement (HMR):

1. **Navigate to the frontend folder**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *Your dev server will run on [http://localhost:5173](http://localhost:5173) and proxy backend requests automatically to port 8000.*

2. **Rebuilding production static files**:
   ```bash
   npm run build
   ```
   *This recompiles assets into `frontend/dist`, updating the unified FastAPI root immediately.*
